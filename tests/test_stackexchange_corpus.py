from __future__ import annotations

from scripts.fetch_stackexchange_questions import html_to_prose


def test_stackexchange_html_cleaner_keeps_prose_and_removes_code() -> None:
    source = (
        "<p>A calibration question with <strong>important prose</strong>.</p>"
        "<pre><code>private_training_example = 1</code></pre>"
        "<blockquote>Additional context.</blockquote>"
    )
    cleaned = html_to_prose(source)
    assert "calibration question" in cleaned
    assert "important prose" in cleaned
    assert "Additional context" in cleaned
    assert "private_training_example" not in cleaned
