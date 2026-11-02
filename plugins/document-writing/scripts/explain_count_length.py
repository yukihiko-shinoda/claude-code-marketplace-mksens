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
import sys
from enum import StrEnum

EXPECTED_ARGC = 3


class Metric(StrEnum):
    """The unit a budget's target counts, as explain_how_long.py reports it."""

    CHARACTERS = "characters"
    WORDS = "words"


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
        """Return the measured length and whether it fits within the target."""
        return {
            "length": self.length,
            "metric": self.metric,
            "target": target,
            "within": self.length <= target,
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
