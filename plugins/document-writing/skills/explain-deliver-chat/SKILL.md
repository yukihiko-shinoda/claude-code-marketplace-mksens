---
name: explain-deliver-chat
description: >-
  Drafts a real explanation covering an already-decided content plan under an already-computed
  length budget treated as a rough anchor, then delivers it directly to chat. Invoked via the
  Skill tool, not typed directly: its caller (currently only explain) has already resolved the
  output language, converted the how-long budget, confirmed the budget is not strict with no -o
  path given, and obtained the content plan before calling here.
when_to_use: >-
  Not for file delivery (explain-deliver-file, regardless of strict), and not for chat delivery
  under a strict, hard-ceiling budget with its plaintext-only restriction
  (explain-deliver-chat-strict) — each of the 3 sibling case-skills owns exactly one combination,
  chosen by explain's own routing.
---

# Explain Deliver Chat

## Using Arguments

This skill is invoked via the `Skill` tool -- there is no slash-command CLI form a human is
expected to type directly. The caller writes the `Skill` tool's `args` text as labeled
`key=value` pairs, one per line, the same convention `explain-deliver-file` and
`explain-deliver-chat-strict` also use.

Required keys (always present, all already resolved upstream by `explain`):

- `language=<ISO 639-1 code>` -- the language to draft in.
- `points=<JSON array of strings>` -- the content plan to cover, passed through unchanged.
- `target=<number>` -- the numeric length target. Here it is always a rough anchor: `explain`
  only ever calls this skill when its own Step 1 already found `$strict=false`.
- `metric=characters|words`

No `topic` key -- chat delivery never renders a top-level title heading naming the overall topic
(the shared formatting file's heading rule, applied in Step 1, may still add section headings once
the drafted content is long enough, but those name a section's own content, never the topic
itself). No `output-path` key -- this skill only ever delivers to chat. No `strict` key -- it is
always `false` here, implied by which skill `explain`
chose to call. No `debug` key, and none of the debug-only values -- `explain` renders its own
trailing `## Debug` section itself, using values it already held before calling here; nothing
debug-related needs to cross into this skill's own `args` at all.

If any of the following required keys is missing or malformed (e.g. `points` isn't a valid JSON
array):

- `language`
- `points`
- `target`
- `metric`

Treat it as an integration bug in the caller, not an ambiguous user input: state which key is
missing or malformed and stop -- do not guess a default and do not use `AskUserQuestion` for it,
since this skill's only caller is another skill's own reasoning, never a human typing free text
directly.

## Steps

### 1. Draft the explanation

Write a real explanation in `$language` that covers every point in `$points`. This drafting
must follow the rules defined in `${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md`
-- read it there, covering all of the following:

- Ordering
- Conclusion/reason rendering
- Heading
- Mood
- Trailing-summary-word

Treat `$target` as a rough anchor judged by eye. Draft once -- a result landing a little outside
`$target` either way is not a defect and does not need a rewrite.

### 2. Deliver the explanation

Render the drafted explanation directly as this skill's chat response.

## Guardrails

- Never invoke a tool call to count characters or words against `$target` or against the shared
  file's heading-length anchor, and never re-draft solely for landing a little outside either one
  -- both are approximate anchors, not an exact tally.
- Follow `${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md` for how a point's
  rendering must handle all of the following -- `$points` is only the content plan; turning it into
  a real explanation with that shape is this skill's own job:
  - Conclusion
  - Reason
  - Headings
  - Mood
  - Trailing words
- Treat a missing or malformed required key as an integration bug in the caller -- state which key
  is the problem and stop, rather than guessing a default or asking the human via
  `AskUserQuestion`. The required keys are:
  - `language`
  - `points`
  - `target`
  - `metric`
