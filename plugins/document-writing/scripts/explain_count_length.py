# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Copyright (c) 2026 Yukihiko Shinoda
"""Count a drafted explanation's length against a strict budget.

Reads the draft from stdin.

Usage: explain_count_length.py <characters|words> <target>
"""

from __future__ import annotations

import json
import re
import sys
from enum import Enum
from enum import StrEnum

EXPECTED_ARGC = 3


class Metric(StrEnum):
    """The unit a budget's target counts, as explain_how_long.py reports it."""

    CHARACTERS = "characters"
    WORDS = "words"


class MarkdownSyntax(Enum):
    """Pair each construct plaintext delivery forbids with a pattern matching what Markdown renders as one."""

    HEADER = ("header", r"^#{1,6}\s")
    EMPHASIS = ("emphasis", r"(\*{1,3})\S(?:.*?\S)?\1|(?<!\w)(_{1,3})\S(?:.*?\S)?\2(?!\w)")
    CODE_SPAN = ("code_span", r"`[^`\n]+`")
    LINK = ("link", r"\[[^\]\n]*\]\([^)\n]*\)")

    def __init__(self, label: str, pattern: str) -> None:
        """Unpack a member's tuple into named attributes."""
        self.label = label
        self.pattern = re.compile(pattern, re.MULTILINE)

    @classmethod
    def found_in(cls, text: str) -> list[str]:
        """Return the label of each construct the text contains."""
        return [syntax.label for syntax in cls if syntax.pattern.search(text)]


class DraftLength:
    """Measure a draft by the metric explain-how-long-converter chose."""

    def __init__(self, text: str, metric: Metric) -> None:
        """Keep the trimmed draft and the metric to measure it by."""
        self.text = text.strip()
        self.metric = metric

    @property
    def length(self) -> int:
        """Return the draft's length in characters or whitespace-separated words."""
        if self.metric is Metric.CHARACTERS:
            return len(self.text)
        return len(self.text.split())

    def report(self, target: float) -> dict[str, object]:
        """Return the measured length, whether it fits the target, and any Markdown syntax found."""
        return {
            "length": self.length,
            "metric": self.metric,
            "target": target,
            "within": self.length <= target,
            "markdown_syntax": MarkdownSyntax.found_in(self.text),
        }


def emit(result: dict[str, object]) -> None:
    """Write one JSON object to stdout as the script's whole output."""
    sys.stdout.write(json.dumps(result) + "\n")


def main() -> int:
    """Measure the draft read from stdin and emit the report as JSON."""
    if len(sys.argv) != EXPECTED_ARGC or sys.argv[1] not in tuple(Metric):
        emit({"error": "usage: explain_count_length.py <characters|words> <target>"})
        return 2
    try:
        target = float(sys.argv[2])
    except ValueError:
        emit({"error": f"invalid target: {sys.argv[2]}"})
        return 2
    emit(DraftLength(sys.stdin.read(), Metric(sys.argv[1])).report(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
