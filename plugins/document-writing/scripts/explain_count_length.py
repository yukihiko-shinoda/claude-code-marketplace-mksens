# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Copyright (c) 2026 Yukihiko Shinoda
"""Count a drafted explanation's length against a strict budget and decide what the draft needs next.

Reads the draft from stdin.

Usage: explain_count_length.py <characters|words> <target> <plaintext|markdown> <revisions>
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from enum import StrEnum

EXPECTED_ARGC = 5
MAX_REVISIONS = 3
USAGE = "usage: explain_count_length.py <characters|words> <target> <plaintext|markdown> <revisions>"


class Metric(StrEnum):
    """The unit a budget's target counts, as explain_how_long.py reports it."""

    CHARACTERS = "characters"
    WORDS = "words"


class Delivery(StrEnum):
    """The form the draft is delivered in, which decides whether Markdown syntax is a defect."""

    PLAINTEXT = "plaintext"
    MARKDOWN = "markdown"


class NextStep(StrEnum):
    """What the calling skill does with the draft after this count."""

    DELIVER = "deliver"
    REMOVE_MARKDOWN = "remove_markdown"
    SHORTEN = "shorten"


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


@dataclass(frozen=True)
class DraftReview:
    """Decide the draft's next step, so every strict delivery shares one fix order and one revision ceiling."""

    draft: DraftLength
    target: float
    delivery: Delivery
    revisions: int

    @classmethod
    def parse(cls, argv: list[str], text: str) -> DraftReview:
        """Return the review the command line describes, raising ValueError for malformed arguments."""
        if len(argv) != EXPECTED_ARGC:
            message = f"expected {EXPECTED_ARGC - 1} arguments, got {len(argv) - 1}"
            raise ValueError(message)
        _, metric, target, delivery, revisions = argv
        return cls(DraftLength(text, Metric(metric)), float(target), Delivery(delivery), int(revisions))

    @property
    def needed(self) -> NextStep:
        """Return what would fix the draft, removing Markdown first since doing so also shortens it."""
        if self.delivery is Delivery.PLAINTEXT and MarkdownSyntax.found_in(self.draft.text):
            return NextStep.REMOVE_MARKDOWN
        if self.draft.length > self.target:
            return NextStep.SHORTEN
        return NextStep.DELIVER

    def report(self) -> dict[str, object]:
        """Return the draft's measurements plus its next step, giving up once the revision ceiling is reached."""
        needed = self.needed
        gave_up = needed is not NextStep.DELIVER and self.revisions >= MAX_REVISIONS
        return {
            **self.draft.report(self.target),
            "revisions": self.revisions,
            "next": NextStep.DELIVER if gave_up else needed,
            "gave_up": gave_up,
        }


def emit(result: dict[str, object]) -> None:
    """Write one JSON object to stdout as the script's whole output."""
    sys.stdout.write(json.dumps(result) + "\n")


def main() -> int:
    """Review the draft read from stdin and emit the report as JSON."""
    try:
        review = DraftReview.parse(sys.argv, sys.stdin.read())
    except ValueError as error:
        emit({"error": f"{USAGE}: {error}"})
        return 2
    emit(review.report())
    return 0


if __name__ == "__main__":
    sys.exit(main())
