# Owed-terms Output Contract

Sealed reference for the `audience-stage-classifier` and `topic-audience-stage-classifier` agents
only. Never referenced from `skills/` or any other root-context-visible file
for why this contract lives in its own file. Both agents resolve to an `owed_terms` list (see
`awareness-stage.md`'s "Owed-terms derivation") and this file defines how each reports it.

## Debug-mode signal

If the invocation's prompt explicitly contains the exact text `(debug mode: also report stage and
evidence)`, include `stage` and `evidence` in the output as described below. If that text is absent,
omit them — never include them speculatively. The caller (never the agent itself) decides whether to
append this text.

## Single-result JSON shape

Output exactly one JSON object and nothing else — no prose before or after, no code fence:

- Default: `{"owed_terms": ["<term>", ...]}`
- Debug mode: `{"owed_terms": ["<term>", ...], "stage": "<O|A|T|H>", "evidence": "<text>"}`

The raw stage letter and evidence text must never appear anywhere in the output unless debug mode was
explicitly signaled per the rule above — this is the whole point of sealing `awareness-stage.md`.

An agent with an additional result shape (e.g. a directory-input, multi-file case) defines that shape
in its own Output contract section, applying this same default/debug split to each entry.
