"""Build a dated, attributed corpus from post-cutoff Stack Exchange questions."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


API = "https://api.stackexchange.com/2.3/questions"
USER_AGENT = "CalibTrace/0.1 (academic calibration privacy study)"


class _ProseParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"code", "pre", "script", "style"}:
            self.skip_depth += 1
        elif tag in {"p", "br", "li", "blockquote", "h1", "h2", "h3"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"code", "pre", "script", "style"} and self.skip_depth:
            self.skip_depth -= 1
        elif tag in {"p", "li", "blockquote"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def html_to_prose(value: str) -> str:
    parser = _ProseParser()
    parser.feed(value)
    return " ".join(html.unescape("".join(parser.parts)).split())


def _timestamp(value: str) -> int:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return int(parsed.timestamp())


def _iso_timestamp(value: int) -> str:
    return dt.datetime.fromtimestamp(value, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _request(parameters: dict[str, Any], retries: int = 5) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{API}?{urllib.parse.urlencode(parameters)}", headers={"User-Agent": USER_AGENT}
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in {429, 502, 503} or attempt == retries:
                details = error.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Stack Exchange API returned HTTP {error.code}: {details}") from error
            retry_after = error.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt)
            time.sleep(delay)
    raise RuntimeError("unreachable retry state")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2025-01-01T00:00:00Z")
    parser.add_argument("--end", default="2025-12-31T23:59:59Z")
    parser.add_argument(
        "--sites", default="stats,ai,datascience,stackoverflow", help="comma-separated API sites"
    )
    parser.add_argument("--pages-per-site", type=int, default=30)
    parser.add_argument("--min-characters", type=int, default=400)
    parser.add_argument("--target-characters", type=int, default=6_000_000)
    parser.add_argument(
        "--output", type=Path, default=Path("data/stackexchange_questions_2025.jsonl")
    )
    args = parser.parse_args()
    if args.start >= args.end:
        raise ValueError("start must precede end")
    sites = [value.strip() for value in args.sites.split(",") if value.strip()]
    if not sites or args.pages_per_site <= 0 or args.target_characters <= 0:
        raise ValueError("sites, page count, and character target must be positive")

    start_epoch = _timestamp(args.start)
    end_epoch = _timestamp(args.end)
    records: dict[str, dict[str, Any]] = {}
    total_characters = 0
    requests = 0
    quota_remaining: int | None = None
    for site in sites:
        for page in range(1, args.pages_per_site + 1):
            payload = _request(
                {
                    "site": site,
                    "page": page,
                    "pagesize": 100,
                    "fromdate": start_epoch,
                    "todate": end_epoch,
                    "sort": "creation",
                    "order": "asc",
                    "filter": "withbody",
                }
            )
            requests += 1
            quota_remaining = payload.get("quota_remaining", quota_remaining)
            for question in payload.get("items", []):
                body = html_to_prose(str(question.get("body", "")))
                title = html.unescape(str(question.get("title", ""))).strip()
                text = f"{title}. {body}".strip()
                if len(text) < args.min_characters:
                    continue
                link = str(question["link"])
                owner = question.get("owner") or {}
                record = {
                    "id": link,
                    "published": _iso_timestamp(int(question["creation_date"])),
                    "title": title,
                    "text": text,
                    "source": f"Stack Exchange API ({site})",
                    "query": f"questions created from {args.start} through {args.end}",
                    "question_id": int(question["question_id"]),
                    "author": html.unescape(str(owner.get("display_name", "unknown"))),
                    "license": "CC BY-SA 4.0",
                }
                if link not in records:
                    records[link] = record
                    total_characters += len(text)
            backoff = float(payload.get("backoff", 0))
            if backoff:
                time.sleep(backoff)
            if total_characters >= args.target_characters or not payload.get("has_more", False):
                break
        if total_characters >= args.target_characters:
            break

    if total_characters < args.target_characters:
        raise RuntimeError(
            f"Corpus contains only {total_characters:,} characters, below the requested "
            f"{args.target_characters:,}"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        for identifier in sorted(records):
            handle.write(json.dumps(records[identifier], ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    temporary.replace(args.output)
    print(
        json.dumps(
            {
                "characters": total_characters,
                "output": str(args.output),
                "quota_remaining": quota_remaining,
                "records": len(records),
                "requests": requests,
                "sites": sites,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
