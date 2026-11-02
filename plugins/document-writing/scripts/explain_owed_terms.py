# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Copyright (c) 2026 Yukihiko Shinoda
"""Read the owed-terms list an audience description states outright, without judging a stage.

Reads the audience description from stdin. Anything but an exact list makes it report needs_agent, since telling that a
free-form description carries no signal takes understanding its meaning.

Usage: explain_owed_terms.py
"""

from __future__ import annotations

import json
import re
import sys

FIXED_ORDER = ("Issue", "Stakes", "Solution", "Conviction")
STATED_LIST = re.compile(r"owed\s+terms\s+are:\s*([A-Za-z,\s]+)", re.IGNORECASE)


def stated_owed_terms(audience: str) -> list[str] | None:
    """Return the stated list in the fixed order, or None unless it is exactly a suffix of that order."""
    match = STATED_LIST.search(audience)
    if match is None:
        return None
    stated = {term.strip() for term in match.group(1).split(",")}
    for start in range(len(FIXED_ORDER)):
        if stated == set(FIXED_ORDER[start:]):
            return list(FIXED_ORDER[start:])
    return None


def main() -> int:
    """Emit the owed terms the audience read from stdin states, or ask for the agent, as JSON."""
    owed_terms = stated_owed_terms(sys.stdin.read())
    result = {"needs_agent": True} if owed_terms is None else {"owed_terms": owed_terms}
    sys.stdout.write(json.dumps(result) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
