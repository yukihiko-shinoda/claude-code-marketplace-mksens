---
name: explain
description: >-
  Outputs an actual prose explanation, not a list of bullet points, about a topic for a stated
  audience, sized to a length budget given as seconds/minutes to read or a direct character count.
  Delegates language resolution to a dedicated subagent and budget conversion to a bundled Python
  script (falling back to a dedicated subagent when uv is unavailable), calls
  explain-for-stated-audience for the content plan, then routes to one of three case-skills --
  explain-deliver-chat-strict, explain-deliver-chat, or explain-deliver-file -- to draft and
  deliver the prose, and renders its own trailing debug section.
argument-hint: '"<topic>" "<audience>" "<how-long>" [-o <path>] [-l <language>] [--debug]'
arguments: [topic, audience, how-long]
allowed-tools:
  - Agent
  - Bash(uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_how_long.py *)
  - Skill(explain-for-stated-audience)
  - Skill(explain-deliver-chat-strict)
  - Skill(explain-deliver-chat)
  - Skill(explain-deliver-file)
  - AskUserQuestion
when_to_use: >-
  The audience is always stated directly by the caller — this skill never infers it from a draft
  or transcript.
---

# Explain

## Using Arguments

Invoke as `/explain "<topic>" "<audience>" "<how-long>" [-o <path>] [-l <language>] [--debug]` --
always double-quote all of the following, since Claude Code splits the raw invocation into named
arguments by quoted segment, not by whitespace alone:

- `$topic`
- `$audience`
- `$how-long`

The three trailing flags are documented only in `argument-hint`, not in `arguments` -- they arrive
as raw text appended after the third positional.

1. Take the raw text bound to `$how-long` as given by the invocation (it may carry trailing flag
   tokens appended after the actual budget value). Repeat the following extraction until no more
   matches remain anywhere in that text -- these flags may appear in any order relative to each
   other:
   - `--debug` (a standalone token) -- strip it, enable this skill's own debug mode.
   - `-l` followed by whitespace and the next token -- strip both, keep the token as
     `$language-flag`.
   - `-o` followed by whitespace and either a double-quoted string or the next whitespace-delimited
     token -- strip both, keep the value as `$output-path`.
2. Trim whatever remains -- that is the literal how-long budget string (e.g. `5m`).
3. If a `-`-prefixed token remains after step 1 that matched none of the three flags, ask the user
   to clarify it rather than silently ignoring it.
4. If `$topic`, `$audience`, or the how-long string left after step 2 is empty, ask the user for
   the missing piece(s) instead of guessing -- never assume a default topic, audience, or budget.

## Steps

### 1. Resolve the output language

Before calling the subagent, check whether this conversation's own system prompt already states a
language to respond in (e.g. a section such as "# Language" naming one) -- if so, keep that
language as `$ambient-language`; otherwise use an empty string. Call `Agent` with
`subagent_type: "explain-language-resolver"`, passing all of the following:

- `$topic`
- `$audience`
- `$language-flag` (empty string if `-l` wasn't given)
- `$ambient-language`

If the response matches the error shape:

```json
{
  "error": "<message>"
}
```

use `AskUserQuestion` to ask for a valid `-l` value instead of guessing. Otherwise keep
`$resolved-language` and `$language-source` from the response.

### 2. Convert the how-long budget and get the content plan

These two sub-steps share no dependency -- budget conversion needs only `$resolved-language` from
Step 1, and the content plan needs only `$topic`/`$audience` from "Using Arguments"; neither one's
output feeds the other. Call both in the same turn, in parallel, not one after the other.

#### Convert the how-long budget

Run the bundled script with `Bash`, passing the trimmed how-long string from "Using Arguments"
step 2 and `$resolved-language` from Step 1:

```bash
uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_how_long.py "<how-long>" "$resolved-language"
```

Use its stdout only when it is a single JSON object -- either the success shape or the error
shape below. If instead the command fails for any of the following reasons, fall back to the
subagent:

- `uv` is not installed (e.g. `command not found`)
- `uv` itself errors before running the script (e.g. it cannot write its temporary files)
- The stdout is not a single JSON object

To fall back, call `Agent` with `subagent_type: "explain-how-long-converter"`, passing the same two
values. The script and the subagent share one output contract, so everything below applies to
whichever one produced the response. If the response matches the error shape:

```json
{
  "error": "<message>"
}
```

use `AskUserQuestion` to ask for a valid budget, showing examples (`30s`, `5m`, `500c`). Otherwise
keep all of the following from the response:

- `$target`
- `$metric`
- `$typology`
- `$strict`

#### Get the content plan

Call `/explain-for-stated-audience "$topic" "$audience"` (append `--debug` to that invocation if
this skill's own debug mode is on). Take its `what_to_explain` array as the points to cover, and,
if debug mode is on, also keep the following from its response, for this skill's own Step 4 debug
output:

- `terms`
- `excluded_prerequisites`
- `stage`
- `evidence`

### 3. Select the case, then delegate drafting and delivery

Route to exactly one of the 3 sibling case-skills below, using this deterministic table -- never
guess or reason about which case fits; the table is exhaustive and mutually exclusive, checked in
this fixed order:

- **`$output-path` is present, regardless of `$strict`** -- call `explain-deliver-file`.
- **`$output-path` is absent AND `$strict` is `true`** -- call `explain-deliver-chat-strict`.
- **`$output-path` is absent AND `$strict` is `false`** -- call `explain-deliver-chat`.

Call the `Skill` tool with the matching `skill` name, passing its `args` as labeled `key=value`
pairs, one per line:

- **`explain-deliver-file`** (output-path branch):

      topic=$topic
      output-path=$output-path
      language=$resolved-language
      points=<the what_to_explain JSON array from Step 2's "Get the content plan" sub-step>
      target=$target
      metric=$metric
      strict=$strict

- **`explain-deliver-chat-strict`** (no output-path, strict branch):

      language=$resolved-language
      points=<the what_to_explain JSON array from Step 2's "Get the content plan" sub-step>
      target=$target
      metric=$metric

- **`explain-deliver-chat`** (no output-path, non-strict branch):

      language=$resolved-language
      points=<the what_to_explain JSON array from Step 2's "Get the content plan" sub-step>
      target=$target
      metric=$metric

None of the 3 case-skills receives any of the following:

- `debug`
- `language-source`
- `typology`
- `terms`
- `excluded_prerequisites`
- `stage`
- `evidence`

Step 4 below renders this skill's own debug output directly, using values this skill already
holds, so nothing debug-related needs to cross into any case-skill's own `args` at all.

The chosen case-skill drafts the prose and delivers it (to chat, or to `$output-path` with
overwrite confirmation). This skill's own job continues only into Step 4 below; there is nothing
else to render for the delivery itself once the call returns.

### 4. Render debug output

Only when this skill's own debug mode is on (Using Arguments step 1). Append a trailing
`## Debug` section to the chat response (after whatever Step 3's case-skill already rendered --
the drafted prose, or a file-write report) containing:

- `$resolved-language` and `$language-source` (Step 1).
- From Step 2's "Convert the how-long budget" sub-step, all of the following:
  - `$target`
  - `$metric`
  - `$typology`
  - `$strict`

  Plus a note if Step 3 called `explain-deliver-chat-strict`, or called `explain-deliver-file` with
  `strict=true`, and that call's own Step 1 drafting reasoning hit its 3-attempt ceiling without
  landing under budget -- this skill already observed that directly, in this same conversation,
  from the case-skill's own reasoning, since the `Skill` tool loads a skill's instructions into the
  same context rather than an isolated one; no passthrough key carries it back. Omit this note
  entirely when Step 3 called `explain-deliver-chat`, or called `explain-deliver-file` with
  `strict=false` -- neither ever runs a counting/retry loop.
- Kept from Step 2's "Get the content plan" sub-step debug response, passed through unchanged:
  - `$terms`
  - `$excluded_prerequisites`
  - `$stage`
  - `$evidence`

## Guardrails

- Never guess a missing value among the following -- always ask:
  - `$topic`
  - `$audience`
  - How-long budget
- Never do any of the following in this skill's own reasoning -- each is delegated whole to its
  own script, subagent, or skill (Steps 1-3); this skill's own job is only to resolve arguments,
  run those delegations -- Step 2's two in parallel, the rest in order -- and forward each one's
  results as the next one's inputs:
  - Judge the audience's awareness stage
  - Expand `what_to_explain`'s points
  - Resolve the output language
  - Convert the how-long budget
  - Draft/deliver the explanation itself

  The one narrow exception is Step 1's own `$ambient-language` check -- noticing whether this
  conversation's own system prompt already states a language is not the same judgment as resolving
  the final output language, which still always goes through `explain-language-resolver`.
- Never guess which of the 3 case-skills to route to in Step 3 -- always use the deterministic
  table (output-path presence first, then `$strict`); the 3 cases are exhaustive and mutually
  exclusive, so exactly one always applies.
- Render the trailing `## Debug` section (Step 4) itself, in this skill's own reasoning, using
  values already held from Steps 1-2 (plus whatever a strict-drafting case-skill's own Step 1
  reasoning already made observable in this same conversation) -- never delegate that rendering
  into any of the 3 case-skills, and never pass a `debug` key (or any debug-only value) into any
  of their `args`, since none of them accepts one anymore.
