---
name: explain-deliver-file
description: >-
  Drafts real connected prose covering an already-decided content plan under an already-computed
  length budget (a hard ceiling if strict, a rough anchor if not), then delivers it to a Markdown
  -o file path with overwrite confirmation. Invoked via the Skill tool, not typed directly: its
  caller (currently only explain) has already resolved the output language, converted the
  how-long budget, confirmed an -o path was given, and obtained the content plan before calling
  here.
allowed-tools:
  - Glob
  - Write
  - Edit
  - AskUserQuestion
when_to_use: >-
  Not for chat delivery of any kind (explain-deliver-chat-strict or explain-deliver-chat, chosen
  by explain's Step 4 table). Unlike those two siblings, the plaintext-only restriction never
  applies here — Markdown-file wrapping always governs file output, even when strict is true.
---

# Explain Deliver File

## Using Arguments

This skill is invoked via the `Skill` tool -- there is no slash-command CLI form a human is
expected to type directly. The caller writes the `Skill` tool's `args` text as labeled
`key=value` pairs, one per line, the same convention its two chat-delivery siblings also use.

Required keys (always present, all already resolved upstream by `explain`):

- `topic=<text>` -- the topic being explained; used only for the `# <Topic>` heading (Step 2).
- `output-path=<path>` -- where to deliver; `explain` only ever calls this skill when this was
  given.
- `language=<ISO 639-1 code>` -- the language to draft in.
- `points=<JSON array of strings>` -- the content plan to cover, passed through unchanged.
- `target=<number>` -- the numeric length target.
- `metric=characters|words`
- `strict=true|false` -- governs only Step 1's drafting sub-step (hard ceiling with retry vs.
  rough anchor); it never affects Step 2's delivery mechanics or the plaintext restriction, since
  that restriction never applies to file delivery at all.

No `debug` key, and none of `language-source`, `typology`, `terms`, `excluded-prerequisites`,
`stage`, `evidence` -- `explain` renders its own trailing `## Debug` section itself, using values
it already held before calling here plus whatever this skill's own Step 1 reasoning already made
observable (e.g. a 3-attempt shortfall when `strict=true`); nothing debug-related needs to cross
into this skill's own `args` at all.

If `topic`, `output-path`, `language`, `points`, `target`, `metric`, or `strict` is missing or
malformed (e.g. `points` isn't a valid JSON array), treat it as an integration bug in the caller,
not an ambiguous user input: state which key is missing or malformed and stop -- do not guess a
default and do not use `AskUserQuestion` for it, since this skill's only caller is another skill's
own reasoning, never a human typing free text directly.

## Steps

### 1. Draft the explanation

Write real, connected prose in `$language` that covers every point in `$points`. The ordering,
conclusion/reason rendering, heading, mood, and trailing-summary-word rules this drafting must
follow are defined in `${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md` -- read it
there. That file's heading rule starts section headings one level below whatever title heading
already wraps the whole response -- here that is Step 2's `# $topic` heading, so section headings
inside the file start at `##`.

- If `$strict` is `true`: treat `$target` as a hard ceiling on `$metric`. After drafting, count
  the actual length by explicit tally and, if it exceeds `$target`, shorten and recount. Repeat up
  to 3 times; if still over budget after 3 attempts, deliver it anyway rather than looping
  indefinitely -- this fact stays visible in this conversation's own transcript, which is enough
  for `explain`'s own trailing Debug step to reference later if its debug mode is on; no separate
  return value is needed. The plaintext-only restriction from the chat-strict case never applies
  here -- Step 2's normal Markdown-file wrapping always governs.
- If `$strict` is `false`: treat `$target` as a rough anchor judged by eye. Draft once -- a result
  landing a little outside `$target` either way is not a defect and does not need a rewrite.

### 2. Deliver the explanation

1. Validate the extension is `.md` or `.markdown` (case-insensitive). If not, use
   `AskUserQuestion` to get a corrected path -- never silently rename or add an extension.
2. `Glob` the literal `$output-path`. If it matches an existing file, use `AskUserQuestion` to ask
   whether to edit it in place or choose a different path -- never overwrite silently.
3. `Write` the prose to `$output-path` (or `Edit` it, if the user chose to revise the existing
   file found in step 2), under a single top-level `# $topic` heading, with the body formatted per
   `${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md` as drafted in Step 1.
4. Report the path written. Any debug output is `explain`'s own concern, rendered in chat after
   this skill's call returns -- never inside the written file itself, and never by this skill.

## Guardrails

- Never silently overwrite an existing `$output-path` -- always confirm via `AskUserQuestion`
  first.
- When `$strict` is `false`, never invoke a tool call to count characters or words against
  `$target`, and never re-draft solely for landing a little outside it -- the budget is an
  approximate anchor, not an exact tally. When `$strict` is `true`, counting and re-shortening
  (bounded to 3 attempts) is required, not optional.
- The plaintext-only, zero-Markdown restriction that applies to `explain-deliver-chat-strict`
  never applies here, regardless of `$strict` -- file delivery always wraps the prose as Markdown
  under a `# $topic` heading.
- Follow `${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md` for how a point's
  conclusion, reason, headings, mood, and trailing words must render -- `$points` is only the
  content plan; turning it into real connected prose with that shape is this skill's own job.
- Treat a missing or malformed required key (`topic`, `output-path`, `language`, `points`,
  `target`, `metric`, `strict`) as an integration bug in the caller -- state which key is the
  problem and stop, rather than guessing a default or asking the human via `AskUserQuestion`.
