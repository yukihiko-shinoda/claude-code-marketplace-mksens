# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Copyright (c) 2026 Yukihiko Shinoda
"""Convert the explain skill's how-long budget into a drafting target.

Deterministic counterpart of the explain-how-long-converter agent: same input, same JSON output contract.

Usage: explain_how_long.py <how-long> <language>
"""

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
from typing import ClassVar

EXPECTED_ARGC = 3
# Logographic scripts only; every other language is treated as phonetic.
IDEOGRAPHIC_LANGUAGES = frozenset({"ja", "zh"})


class InvalidHowLongError(ValueError):
    """Raised when a how-long string doesn't match the expected format."""

    def __init__(self, how_long: str) -> None:
        """Build the message the error shape reports."""
        super().__init__(f"invalid how-long: {how_long}")


class Metric(StrEnum):
    """The unit a budget's target counts."""

    CHARACTERS = "characters"
    WORDS = "words"


class WritingSystem(Enum):
    """Pair each writing-system typology with its metric and reading speed."""

    PHONETIC = ("phonetic", Metric.WORDS, 200)
    IDEOGRAPHIC = ("ideographic", Metric.CHARACTERS, 400)

    def __init__(self, typology: str, metric: Metric, units_per_minute: int) -> None:
        """Unpack a member's tuple into named attributes."""
        self.typology = typology
        self.metric = metric
        self.units_per_minute = units_per_minute

    @classmethod
    def of(cls, language: str) -> WritingSystem:
        """Return the writing system of an ISO 639-1 language code."""
        return cls.IDEOGRAPHIC if language.strip().lower() in IDEOGRAPHIC_LANGUAGES else cls.PHONETIC


@dataclass(frozen=True)
class Budget:
    """A drafting target the explain skill's case-skills draft against."""

    STRICT_CEILING: ClassVar[int] = 280

    target: float
    metric: Metric
    # None for a direct character count, where no language-based conversion applies.
    writing_system: WritingSystem | None = None

    @property
    def strict(self) -> bool:
        """Return whether the target is short enough to be a hard ceiling."""
        return self.target <= self.STRICT_CEILING

    def to_dict(self) -> dict[str, object]:
        """Return the success shape of the output contract."""
        typology = self.writing_system.typology if self.writing_system else None
        return {"target": self.target, "metric": self.metric, "typology": typology, "strict": self.strict}


@dataclass(frozen=True)
class HowLong:
    """A parsed how-long string: a number plus its unit (s, m, or c)."""

    PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"([0-9]+(?:\.[0-9]+)?)([smc])")

    value: float
    unit: str

    @classmethod
    def parse(cls, text: str) -> HowLong:
        """Parse a how-long string, raising InvalidHowLongError if it doesn't match."""
        how_long = text.strip()
        match = cls.PATTERN.fullmatch(how_long)
        if match is None:
            raise InvalidHowLongError(how_long)
        return cls(float(match.group(1)), match.group(2))

    def to_budget(self, language: str) -> Budget:
        """Convert into a budget, using the language's reading speed for time units."""
        if self.unit == "c":
            return Budget(int(self.value) if self.value.is_integer() else self.value, Metric.CHARACTERS)
        minutes = self.value / 60 if self.unit == "s" else self.value
        system = WritingSystem.of(language)
        return Budget(math.floor(minutes * system.units_per_minute + 0.5), system.metric, system)


def emit(result: dict[str, object]) -> None:
    """Write one JSON object to stdout as the script's whole output."""
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")


def main() -> int:
    """Convert the budget given on the command line and emit it as JSON."""
    if len(sys.argv) != EXPECTED_ARGC:
        emit({"error": "usage: explain_how_long.py <how-long> <language>"})
        return 2
    try:
        budget = HowLong.parse(sys.argv[1]).to_budget(sys.argv[2])
    except InvalidHowLongError as error:
        emit({"error": str(error)})
        return 1
    emit(budget.to_dict())
    return 0


if __name__ == "__main__":
    sys.exit(main())
