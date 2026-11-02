---
name: explain
description: >-
  Outputs an actual prose explanation, not a list of bullet points, about a topic for a stated
  audience, sized to a length budget given as seconds/minutes to read or a direct character count.
  Delegates argument parsing, language normalization, budget conversion, and routing to a bundled
  Python script (falling back to a prompt-based procedure when uv is unavailable or the language
  needs detecting), calls explain-for-stated-audience for the content plan, then routes to one of
  three case-skills -- explain-deliver-chat-strict, explain-deliver-chat, or explain-deliver-file
  -- to draft and deliver the prose, and renders its own trailing debug section.
argument-hint: '"<topic>" "<audience>" "<how-long>" [-o <path>] [-l <language>] [--debug]'
arguments: [topic, audience]
allowed-tools:
  - Agent
  - Bash(uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_prepare.py *)
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

- The topic
- The audience
- The how-long budget

Only the topic and the audience are named in `arguments`. The how-long budget and the three
trailing flags are read from the full invocation, exactly as typed:

```text
$ARGUMENTS
```

If the first or second positional is missing or empty (`""`) in that invocation, ask the user for
the missing piece(s) instead of guessing -- never assume a default topic or audience. This check names them by
position because their named placeholders expand to the empty value itself.

## Steps

### 1. Prepare the run

Check whether this conversation's own system prompt already states a language to respond in (e.g.
a section such as "# Language" naming one) -- if so, keep that language as `$ambient-language`;
otherwise use an empty string. Then run the bundled script, piping everything in the full invocation
after the second positional, flags included, through a quoted heredoc:

```bash
uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/explain_prepare.py "$ambient-language" <<'EOF'
<raw how-long text>
EOF
```

Branch on its stdout:

| Stdout | Next |
| --- | --- |
| Has `ask` | Ask the user that question with `AskUserQuestion`, then re-run with the corrected text |
| Has `case` | Keep each field as the same-named variable (e.g. `target` as `$target`) |
| Anything else, or the command fails (e.g. `uv` is missing) | Follow the manual procedure below |

The manual procedure is in `${CLAUDE_PLUGIN_ROOT}/references/explain-manual-preparation.md` -- read
it there, taking its `<plugin-root>` to mean `${CLAUDE_PLUGIN_ROOT}`. It sets the same variables.

`debug` being `true` enables this skill's own debug mode, and a `null` `output-path` means
`$output-path` is absent. If `output-exists` is `true`, use `AskUserQuestion` to ask whether to edit
that file in place or choose a different path, never overwriting silently. For a different path,
re-run with the `-o` value replaced. Whenever the script found `$output-path`, keep `$output-action`
as `edit` if the user chose editing in place, otherwise `write`.

### 2. Get the content plan

Call `/explain-for-stated-audience "$topic" "$audience"` (append `--debug` to that invocation if
this skill's own debug mode is on). Take its `what_to_explain` array as the points to cover, and,
if debug mode is on, also keep the following from its response, for this skill's own Step 4 debug
output:

- `terms`
- `excluded_prerequisites`
- `stage`
- `evidence`

### 3. Delegate drafting and delivery

Call the `Skill` tool with `$case` as the `skill` name -- never guess or reason about a different
case -- passing its `args` as labeled `key=value` pairs, one per line:

- **`explain-deliver-file`**, adding `output-action=$output-action` only when that variable is set:

      topic=$topic
      output-path=$output-path
      language=$resolved-language
      points=<the what_to_explain JSON array from Step 2>
      target=$target
      metric=$metric
      strict=$strict

- **`explain-deliver-chat-strict`** or **`explain-deliver-chat`**:

      language=$resolved-language
      points=<the what_to_explain JSON array from Step 2>
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

Only when this skill's own debug mode is on (Step 1). Append a trailing `## Debug` section to the
chat response (after whatever Step 3's case-skill already rendered -- the drafted prose, or a
file-write report) containing:

- From Step 1, all of the following:
  - `$resolved-language`
  - `$language-source`
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
- Kept from Step 2's debug response, passed through unchanged:
  - `$terms`
  - `$excluded_prerequisites`
  - `$stage`
  - `$evidence`

## Guardrails

- Never guess a missing value among the following -- always ask:
  - The topic
  - The audience
  - The how-long budget
- Never do any of the following in this skill's own reasoning -- each is delegated whole to its
  own script, subagent, or skill (Steps 1-3); this skill's own job is only to resolve arguments,
  run those delegations in order, and forward each one's results as the next one's inputs:
  - Judge the audience's awareness stage
  - Expand `what_to_explain`'s points
  - Resolve the output language
  - Convert the how-long budget
  - Draft/deliver the explanation itself

  The one narrow exception is the `$ambient-language` check -- noticing whether this conversation's
  own system prompt already states a language is not the same judgment as resolving the final
  output language.
- Render the trailing `## Debug` section (Step 4) itself, in this skill's own reasoning, using
  values already held from Steps 1-2 (plus whatever a strict-drafting case-skill's own Step 1
  reasoning already made observable in this same conversation) -- never delegate that rendering
  into any of the 3 case-skills, and never pass a `debug` key (or any debug-only value) into any
  of their `args`, since none of them accepts one anymore.
