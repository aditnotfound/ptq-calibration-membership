"""Download a dated arXiv abstract corpus for post-cutoff calibration experiments."""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ATOM = {"atom": "http://www.w3.org/2005/Atom"}


def _clean(value: str | None) -> str:
    return " ".join((value or "").split())


def _fetch(query: str, start: int, limit: int) -> bytes:
    parameters = urllib.parse.urlencode(
        {
            "search_query": query,
            "start": start,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "ascending",
        }
    )
    request = urllib.request.Request(
        f"https://export.arxiv.org/api/query?{parameters}",
        headers={"User-Agent": "CalibTrace/0.1 (research corpus; contact via paper authors)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="cat:cs.LG AND submittedDate:[202401010000 TO 202412312359]",
    )
    parser.add_argument("--max-results", type=int, default=4000)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--delay-seconds", type=float, default=3.0)
    parser.add_argument("--output", type=Path, default=Path("data/arxiv_cs_lg_2024.jsonl"))
    args = parser.parse_args()
    if args.max_results <= 0 or args.batch_size <= 0:
        raise ValueError("Result counts must be positive")

    records: dict[str, dict[str, str]] = {}
    for start in range(0, args.max_results, args.batch_size):
        payload = _fetch(args.query, start, min(args.batch_size, args.max_results - start))
        root = ET.fromstring(payload)
        entries = root.findall("atom:entry", ATOM)
        if not entries:
            break
        for entry in entries:
            identifier = _clean(entry.findtext("atom:id", namespaces=ATOM))
            title = _clean(entry.findtext("atom:title", namespaces=ATOM))
            abstract = _clean(entry.findtext("atom:summary", namespaces=ATOM))
            published = _clean(entry.findtext("atom:published", namespaces=ATOM))
            if not identifier or not abstract or not published.startswith("2024-"):
                continue
            records[identifier] = {
                "id": identifier,
                "published": published,
                "title": title,
                "abstract": abstract,
                "text": f"{title}. {abstract}",
                "source": "arXiv API",
                "query": args.query,
            }
        if len(entries) < min(args.batch_size, args.max_results - start):
            break
        if start + args.batch_size < args.max_results:
            time.sleep(args.delay_seconds)

    if not records:
        raise RuntimeError("The arXiv query returned no usable 2024 abstracts")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        for identifier in sorted(records):
            handle.write(json.dumps(records[identifier], ensure_ascii=False, sort_keys=True))
            handle.write("\n")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "records": len(records)}, sort_keys=True))


if __name__ == "__main__":
    main()
