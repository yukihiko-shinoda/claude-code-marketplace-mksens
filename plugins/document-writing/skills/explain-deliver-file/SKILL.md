---
name: explain-deliver-file
description: >-
  Drafts a real explanation covering an already-decided content plan under an already-computed
  length budget (a hard ceiling if strict, a rough anchor if not), then delivers it to a Markdown
  -o file path with overwrite confirmation. Invoked via the Skill tool, not typed directly: its
  caller (currently only explain) has already resolved the output language, converted the
  how-long budget, confirmed an -o path was given, and obtained the content plan before calling
  here.
allowed-tools:
  - Read(${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md)
  - Read(${CLAUDE_PLUGIN_ROOT}/references/explain-manual-counting.md)
  - Glob
  - Write
  - Edit
  - AskUserQuestion
  - Bash(uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_count_length.py *)
when_to_use: >-
  Not for chat delivery of any kind (explain-deliver-chat-strict or explain-deliver-chat, chosen
  by explain's routing). Unlike those two siblings, the plaintext-only restriction never
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

Optional key:

- `output-action=write|edit` -- present only when `explain_prepare.py` already validated
  `$output-path` and the user already confirmed any overwrite, so Step 2 skips asking again.

None of the following keys are ever passed:

- `debug`
- `language-source`
- `typology`
- `terms`
- `excluded_prerequisites`
- `stage`
- `evidence`

`explain` renders its own trailing `## Debug` section itself, using values it already held before
calling here plus whatever this skill's own Step 1 reasoning already made observable (e.g. a
3-attempt shortfall when `strict=true`); nothing debug-related needs to cross into this skill's own
`args` at all.

If any of the following required keys is missing or malformed (e.g. `points` isn't a valid JSON
array):

- `topic`
- `output-path`
- `language`
- `points`
- `target`
- `metric`
- `strict`

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

That file's heading rule starts section headings one level below whatever title heading
already wraps the whole response -- here that is Step 2's `# $topic` heading, so section headings
inside the file start at `##`.

- If `$strict` is `true`: treat `$target` as a hard ceiling on `$metric`, which overrides covering
  every point: `$points` may hold more than `$target` can fit, since it is planned without knowing
  the budget. Choose what to keep by how much the rest of the explanation depends on a point, then
  drop or merge the least essential points rather than compressing every point until a sentence no
  longer makes sense on its own to a reader without the plan's background. This decides only what
  stays, not the order it appears in. After drafting, count the draft as described in "Counting
  the draft" below and act on what it reports. The plaintext-only restriction from the
  chat-strict case never applies here -- Step 2's normal Markdown-file wrapping always governs.
- If `$strict` is `false`: treat `$target` as a rough anchor judged by eye. Draft once -- a result
  landing a little outside `$target` either way is not a defect and does not need a rewrite.

#### Counting the draft

Only when `$strict` is `true`. Count each draft's body text -- without the `# $topic` heading
Step 2 adds -- with the bundled script, piping the draft in through a quoted heredoc:

<!-- markdownlint-disable MD013 -->
```bash
uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_count_length.py "<metric>" "<target>" markdown "<revisions>" <<'EOF'
<draft>
EOF
```
<!-- markdownlint-enable MD013 -->

`<revisions>` is how many revisions the draft has had so far, starting at `0`. The stdout is a JSON
object. Act on its `next`, never on your own reading of the other fields:

| `next` | Action |
| --- | --- |
| `deliver` | Continue to Step 2 |
| `shorten` | Drop or merge the next-least-essential point, then recount with `<revisions>` plus one |

`next` is `deliver` with `gave_up` set to `true` once the revision ceiling is reached over budget.
That fact stays visible in this conversation's own transcript, which is enough for `explain`'s own
trailing Debug step to reference later if its debug mode is on.

Follow `${CLAUDE_PLUGIN_ROOT}/references/explain-manual-counting.md` instead, as a skill not
delivering plaintext, if the command fails for any of the following reasons:

- `uv` is not installed (e.g. `command not found`)
- `uv` itself errors before running the script (e.g. it cannot write its temporary files)
- The stdout is not a single JSON object

### 2. Deliver the explanation

1. Skip this step and step 2 if `$output-action` was passed. Validate the extension is `.md` or
   `.markdown` (case-insensitive). If not, use `AskUserQuestion` to get a corrected path -- never
   silently rename or add an extension.
2. `Glob` the literal `$output-path`. If it matches an existing file, use `AskUserQuestion` to ask
   whether to edit it in place or choose a different path -- never overwrite silently.
3. `Write` the explanation to `$output-path` (or `Edit` it, if `$output-action` is `edit` or the user
   chose to revise the existing file found in step 2), under a single top-level `# $topic`
   heading, with the body formatted per
   `${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md` as drafted in Step 1.
4. Report the path written. Any debug output is `explain`'s own concern, rendered in chat after
   this skill's call returns -- never inside the written file itself, and never by this skill.

## Guardrails

- Never silently overwrite an existing `$output-path` -- always confirm via `AskUserQuestion`
  first, unless `$output-action` shows `explain` already did.
- When `$strict` is `false`, never invoke a tool call to count characters or words against
  `$target`, and never re-draft solely for landing a little outside it -- the budget is an
  approximate anchor, not an exact tally. When `$strict` is `true`, counting is required, not
  optional.
- The plaintext-only, zero-Markdown restriction that applies to `explain-deliver-chat-strict`
  never applies here, regardless of `$strict` -- file delivery always wraps the explanation as Markdown
  under a `# $topic` heading.
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
  - `topic`
  - `output-path`
  - `language`
  - `points`
  - `target`
  - `metric`
  - `strict`
