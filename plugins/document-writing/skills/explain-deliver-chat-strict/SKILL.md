---
name: explain-deliver-chat-strict
description: >-
  Drafts real connected prose covering an already-decided content plan under an already-computed
  length budget treated as a hard ceiling, then delivers it to chat as plaintext only -- zero
  Markdown syntax. Invoked via the Skill tool, not typed directly: its caller (currently only
  explain) has already resolved the output language, converted the how-long budget, confirmed the
  budget is strict (target <= 280) with no -o path given, and obtained the content plan before
  calling here.
allowed-tools:
  - Read(${CLAUDE_PLUGIN_ROOT}/references/explain-manual-counting.md)
  - Bash(uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_count_length.py *)
when_to_use: >-
  Not for file delivery (explain-deliver-file, regardless of strict), and not for chat delivery
  under a non-strict, rough-anchor budget (explain-deliver-chat) — each of the 3 sibling
  case-skills owns exactly one combination, chosen by explain's own routing.
---

# Explain Deliver Chat Strict

## Using Arguments

This skill is invoked via the `Skill` tool -- there is no slash-command CLI form a human is
expected to type directly. The caller writes the `Skill` tool's `args` text as labeled
`key=value` pairs, one per line, the same convention `explain-deliver-file` and
`explain-deliver-chat` also use, since several of this skill's values are JSON arrays that a
quoted-positional split cannot represent safely.

Required keys (always present, all already resolved upstream by `explain`):

- `language=<ISO 639-1 code>` -- the language to draft in.
- `points=<JSON array of strings>` -- the content plan to cover
  (`explain-for-stated-audience`'s `what_to_explain` array), passed through unchanged.
- `target=<number>` -- the numeric length target. Here it is always a hard ceiling on `$metric`:
  `explain` only ever calls this skill when its own Step 1 already found `$strict=true`.
- `metric=characters|words`

No `topic` key -- chat delivery renders no heading, so nothing needs it. No `output-path` key --
this skill only ever delivers to chat. No `strict` key -- it is always `true` here, implied by
which skill `explain` chose to call. None of the following keys are ever passed:

- `debug`
- `language-source`
- `typology`
- `terms`
- `excluded_prerequisites`
- `stage`
- `evidence`

`explain` renders its own trailing `## Debug` section itself, in the same conversation this
skill's own reasoning already ran in (the `Skill` tool loads this skill's instructions into that
same context, not an isolated one), using values it already held before calling here plus whatever
this skill's own Step 1 reasoning already made observable (e.g. a 3-attempt shortfall) -- nothing
needs to be reported back through a return value or passthrough key.

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

Write real, connected prose in `$language` that covers the points in `$points` -- never a bulleted
list or outline standing in for prose.

- `$points` may hold more than `$target` can fit, since it is planned without knowing the budget.
  Choose what to keep by how much the rest of the explanation depends on a point, then drop or
  merge the least essential points rather than compressing every point until a sentence no longer
  makes sense on its own to a reader without the plan's background. This decides only what stays,
  not the order it appears in.

- Order the explanation abstract-first then concrete, and conclusion-first then reason: state the
  overall point before the supporting detail, both at the level of the whole explanation and
  within each point it covers.
- Treat `$target` as a hard ceiling on `$metric`. After drafting, count the draft as described in
  "Counting the draft" below and act on what it reports.
- The drafted prose must also be plain text only: no Markdown syntax of any kind -- no headers, no
  bold/italic emphasis, no backtick code spans, no links -- plain sentences only. The strict
  budget this skill is only ever called for signals an SNS-style destination that won't render
  Markdown, so any markup syntax is both wasted budget and a literal stray character in the
  delivered text.

#### Counting the draft

Count each draft with the bundled script, piping the draft in through a quoted heredoc:

<!-- markdownlint-disable MD013 -->
```bash
uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_count_length.py "<metric>" "<target>" plaintext "<revisions>" <<'EOF'
<draft>
EOF
```
<!-- markdownlint-enable MD013 -->

`<revisions>` is how many revisions the draft has had so far, starting at `0`. The stdout is a JSON
object. Act on its `next`, never on your own reading of the other fields:

| `next` | Action |
| --- | --- |
| `deliver` | Continue to Step 2 |
| `remove_markdown` | Remove the constructs `markdown_syntax` lists, then recount with `<revisions>` plus one |
| `shorten` | Drop or merge the next-least-essential point, then recount with `<revisions>` plus one |

`next` is `deliver` with `gave_up` set to `true` once the revision ceiling is reached with a defect
remaining. That fact stays visible in this conversation's own transcript, which is enough for
`explain`'s own trailing Debug step to reference later if its debug mode is on.

Follow `${CLAUDE_PLUGIN_ROOT}/references/explain-manual-counting.md` instead, as a skill delivering
plaintext, if the command fails for any of the following reasons:

- `uv` is not installed (e.g. `command not found`)
- `uv` itself errors before running the script (e.g. it cannot write its temporary files)
- The stdout is not a single JSON object

### 2. Deliver the explanation

Render the drafted prose directly as this skill's chat response. No forced heading -- just the
prose.

## Guardrails

- Counting is required, not optional -- never deliver the first draft without counting it first.
- The delivered prose must contain zero Markdown syntax -- rely on `next`, or check by eye when the
  count fell back to a tally, to confirm that none of the following crept in:
  - Headers
  - Emphasis markers
  - Backtick code spans
  - Links
- Never deliver the explanation itself as a bulleted list or outline -- `$points` is only the
  content plan; turning it into real connected prose, in the stated order, is this skill's own
  job.
- Treat a missing or malformed required key as an integration bug in the caller -- state which key
  is the problem and stop, rather than guessing a default or asking the human via
  `AskUserQuestion`. The required keys are:
  - `language`
  - `points`
  - `target`
  - `metric`
