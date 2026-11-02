# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Copyright (c) 2026 Yukihiko Shinoda
"""Prepare an explain run from its raw how-long text.

Deterministic counterpart of the explain skill's flag extraction, language normalization, budget conversion, output
path check, and case routing. Language detection needs judgment, so any language this can't resolve is reported as
needs_language_agent for the skill's prompt-based procedure to handle.

Reads the raw how-long text, trailing flags included, from stdin.

Usage: explain_prepare.py <ambient-language>
"""

from __future__ import annotations

import re
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from explain_how_long import HowLong
from explain_how_long import InvalidHowLongError
from explain_how_long import emit

EXPECTED_ARGC = 2
BUDGET_EXAMPLES = "e.g. 30s, 5m, 500c"
# Deliberately not a full ISO 639-1 list: it would dwarf this script and need its own upkeep, while every language
# missing here still resolves through explain-language-resolver, only more slowly.
# Extend only when a genuinely new case is encountered, as explain-language-resolver's own table does.
LANGUAGE_NAMES = {"japanese": "ja", "english": "en"}
MARKDOWN_SUFFIXES = frozenset({".md", ".markdown"})


class PreparationError(ValueError):
    """Raised with the question the skill must ask the user to correct its input."""


@dataclass(frozen=True)
class ResolvedLanguage:
    """An ISO 639-1 code plus which source it came from."""

    code: str
    source: str

    @staticmethod
    def normalize(value: str) -> str | None:
        """Return the code for a language code or known name, or None if it's neither."""
        language = value.strip().lower()
        return language if language in LANGUAGE_NAMES.values() else LANGUAGE_NAMES.get(language)

    @classmethod
    def resolve(cls, language_flag: str, ambient_language: str) -> ResolvedLanguage | None:
        """Return the language the flag or else the ambient value names, or None if that value isn't known."""
        value, source = (language_flag, "flag") if language_flag else (ambient_language, "settings")
        code = cls.normalize(value)
        return cls(code, source) if code else None


@dataclass
class Arguments:
    """The raw how-long text split into its budget and trailing flags."""

    TOKEN: ClassVar[re.Pattern[str]] = re.compile(r'"[^"]*"|\S+')

    how_long: str = ""
    debug: bool = False
    language_flag: str = ""
    output_path: str | None = None

    @classmethod
    def parse(cls, text: str) -> Arguments:
        """Extract the flags in any order, raising PreparationError if a dash-prefixed token matches none of them."""
        arguments = cls()
        words = deque(cls.TOKEN.findall(text))
        remaining = []
        while words:
            word = words.popleft()
            if not arguments.consume_flag(word, words):
                remaining.append(word.removeprefix('"').removesuffix('"'))
        unknown = [word for word in remaining if word.startswith("-")]
        if unknown:
            message = f"Unknown flag: {' '.join(unknown)}. What did you mean?"
            raise PreparationError(message)
        arguments.how_long = " ".join(remaining)
        return arguments

    def consume_flag(self, word: str, words: deque[str]) -> bool:
        """Apply a recognized flag and its value, returning whether the word was consumed."""
        if word == "--debug":
            self.debug = True
            return True
        if word not in {"-l", "-o"} or not words or words[0].startswith("-"):
            return False
        value = words.popleft().removeprefix('"').removesuffix('"')
        if word == "-l":
            self.language_flag = value
        else:
            self.output_path = value
        return True

    def parse_how_long(self) -> HowLong:
        """Return the validated budget, raising PreparationError if it's missing or malformed."""
        if not self.how_long:
            message = f"What is the length budget? ({BUDGET_EXAMPLES})"
            raise PreparationError(message)
        try:
            return HowLong.parse(self.how_long)
        except InvalidHowLongError as error:
            message = f"Invalid length budget: {self.how_long}. What should it be? ({BUDGET_EXAMPLES})"
            raise PreparationError(message) from error

    def output_exists(self) -> bool:
        """Return whether a file already sits at the output path, raising PreparationError for a non-Markdown one."""
        if self.output_path is None:
            return False
        path = Path(self.output_path).expanduser()
        if path.suffix.lower() not in MARKDOWN_SUFFIXES:
            message = f"Output path isn't Markdown: {self.output_path}. Which .md or .markdown path should it be?"
            raise PreparationError(message)
        return path.exists()


class Preparation:
    """Everything the explain skill needs before calling its content plan and case-skill."""

    def __init__(self, arguments: Arguments, ambient_language: str) -> None:
        self.arguments = arguments
        self.ambient_language = ambient_language

    def to_dict(self) -> dict[str, object]:
        """Return the success shape, or needs_language_agent when the language can't resolve here."""
        how_long = self.arguments.parse_how_long()
        output_exists = self.arguments.output_exists()
        language = ResolvedLanguage.resolve(self.arguments.language_flag, self.ambient_language)
        if language is None:
            return {"needs_language_agent": True}
        budget = how_long.to_budget(language.code)
        return {
            "debug": self.arguments.debug,
            "resolved-language": language.code,
            "language-source": language.source,
            **budget.to_dict(),
            "case": self.select_case(strict=budget.strict),
            "output-path": self.arguments.output_path,
            "output-exists": output_exists,
        }

    def select_case(self, *, strict: bool) -> str:
        """Return the case-skill that owns this combination of output path and strictness."""
        if self.arguments.output_path is not None:
            return "explain-deliver-file"
        return "explain-deliver-chat-strict" if strict else "explain-deliver-chat"


def main() -> int:
    """Prepare the run described on stdin and emit the result as JSON."""
    if len(sys.argv) != EXPECTED_ARGC:
        emit({"error": "usage: explain_prepare.py <ambient-language>"})
        return 2
    try:
        emit(Preparation(Arguments.parse(sys.stdin.read()), sys.argv[1]).to_dict())
    except PreparationError as error:
        emit({"ask": str(error)})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
