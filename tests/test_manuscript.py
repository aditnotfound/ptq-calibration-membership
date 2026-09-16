from __future__ import annotations

import re
from pathlib import Path


def test_abstract_respects_style_contract() -> None:
    text = (Path(__file__).parents[1] / "paper" / "sections" / "abstract.tex").read_text(
        encoding="utf-8"
    )
    assert len(text.split()) <= 250
    assert "\N{EM DASH}" not in text
    assert re.search(r"\brather than\b", text, flags=re.IGNORECASE) is None
    assert re.search(r"\bnot\b.{0,80}\bbut\b", text, flags=re.IGNORECASE) is None
    assert re.search(r"\bit(?:'|’)s not\b", text, flags=re.IGNORECASE) is None
