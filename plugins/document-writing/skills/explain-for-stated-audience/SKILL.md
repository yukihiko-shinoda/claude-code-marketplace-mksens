---
name: explain-for-stated-audience
description: >-
  Given a short topic phrase and a short audience description, decide what still needs explaining --
  crossing the audience's awareness of the topic's problem (which of Issue/Stakes/Solution/Conviction
  still apply) with the audience's stated prerequisite background (which of the normal sub-points
  those terms require are already covered by what the audience already knows). Returns a
  `what_to_explain` JSON array of concrete, topic-specific points, filtered so already-known
  prerequisites are excluded. Called directly by section-drafting skills, or auto-loaded rules,
  that already know their target reader segment.
argument-hint: '"<topic>" "<audience>" [--debug]'
arguments: [topic, audience]
allowed-tools:
  - Agent
when_to_use: >-
  Called directly by section-drafting skills or auto-loaded rules that already know (or just
  asked the user for) their target reader segment — e.g. update-readme's Advantage section,
  zenn-introduce-solution's Hook section, or the audience-awareness rule for README/docs/articles.
---

# Explain For Stated Audience

## Two axes this skill crosses

1. **Awareness-of-problem stage** -- how far the audience already is on the path from not knowing
   this topic's problem exists, through knowing but not caring, to actively evaluating, to needing
   it solved right now. Governs WHICH of the four abstract terms (see "Content-value Vocabulary"
   below) are still owed.
2. **Prerequisite background** -- what the audience already knows in general, independent of
   whether they're aware of THIS topic's problem. Governs HOW MUCH of each owed term's usual
   content can be skipped as already-known scaffolding (e.g. an LPIC-certified reader already knows
   shell scripting, so explaining a Dockerfile's `Solution` doesn't need to re-teach shell syntax,
   only what this Dockerfile specifically does with it).

These axes are orthogonal -- an audience can be fully aware of a problem yet have no relevant
prerequisite background, or be unaware of the problem yet a domain expert needing only the briefest
framing once told it exists. Keep them as two distinct passes below -- stage first, prerequisite
filtering second -- rather than inferring one from the other.

## Content-value Vocabulary

The `Conclusion`/`Concerns`/`Issue`/`Cause`/`Solution`/`Stakes`/`Conviction` vocabulary is defined
in `${CLAUDE_PLUGIN_ROOT}/references/content-value-vocabulary.md` — read it there. It's kept in a
location common to both skills and agents rather than owned by this skill.

## Using Arguments

Invoke as `/explain-for-stated-audience "<topic>" "<audience>" [--debug]` — always double-quote
`$topic`
and `$audience` in the invocation, since both are typically multi-word phrases and Claude Code
splits the raw invocation into the two named arguments by quoted segment, not by whitespace alone
(an unquoted multi-word phrase gets truncated to its first word).

1. `$topic` and `$audience` arrive already split out by the invocation. If a trailing `--debug`
   token follows, enable debug mode.
2. If either `$topic` or `$audience` is empty, ask the caller for the missing one instead of
   guessing.
3. `$audience` may state a stage signal (a letter or stage name), a prerequisite-background signal
   (certifications, role, stated familiarity), both, or neither.

## Steps

### 1. Determine the owed abstract terms (stage pass)

Call the `Agent` tool with `subagent_type: "topic-audience-stage-classifier"`, stating both `$topic`
and `$audience` directly in the prompt (e.g. `Classify the audience awareness stage. Topic: $topic
Audience: $audience`). If this skill's own `--debug` was passed, append this exact text to the end
of that prompt: `(debug mode: also report stage and evidence)`.

Parse the subagent's JSON response and take `owed_terms` directly -- do not look the stage up in any
local table; the subagent now computes and returns the owed terms itself from the sealed table in
its own isolated context.

- Default response shape:

  ```json
  {
    "owed_terms": [
      "<term>",
      ...
    ]
  }
  ```

- With the debug note appended:

  ```json
  {
    "owed_terms": [
      "<term>",
      ...
    ],
    "stage": "<letter>",
    "evidence": "<text>"
  }
  ```

  Keep `stage` and `evidence` for Step 4's debug output; never surface them outside `--debug`.

### 2. Expand each owed term into topic-specific concrete points

For each term from Step 1, name the concrete sub-points `$topic` would normally require to cover
that term, grounded in what `$topic` actually is -- not a generic, topic-agnostic template.

Example: topic `Dockerfile summary`, term `Solution` -> sub-points might include "what each
instruction (`FROM`, `RUN`, `COPY`) in this Dockerfile does", "why this Dockerfile uses a
multi-stage build", "what the `RUN` step's shell script here is actually doing".

### 3. Filter out sub-points the audience's stated background already covers

Re-read `$audience` for any prerequisite-background signal. Drop a Step-2 sub-point only if the
stated background plainly covers that specific sub-point's prerequisite -- e.g. LPIC covers general
shell-scripting literacy, so drop a sub-point that only re-teaches shell syntax, but keep sub-points
specific to `$topic` itself (what a particular line in *this* Dockerfile does is topic content, not
a shell-syntax prerequisite, even to an LPIC holder). Never drop a whole term wholesale here.

### 4. Emit the result

- Default:

  ```json
  {
    "what_to_explain": [
      "<sub-point>",
      ...
    ]
  }
  ```

  Each entry is one surviving concrete sub-point string.
- With `--debug`: also `"terms"` (Step 1's `owed_terms` list), `"excluded_prerequisites"` (dropped
  sub-points, each with a short reason), `"stage"`, and `"evidence"` (the latter two sourced from
  Step 1's debug response).
- Output exactly one JSON object and nothing else -- no prose before or after, no code fence.

## Why Steps 2 and 3 use no subagent

Steps 2 (topic-specific expansion) and 3 (prerequisite filtering) reason directly in the calling
context. Unlike the evidence a full draft/transcript classification would need to keep out of the
caller's context, `$topic` and `$audience` are always short phrases, so there's no bulk text to
shield there, and an `Agent` hop would only add latency for those two steps. Step 1's stage judgment
is the exception -- it delegates to `topic-audience-stage-classifier` anyway, not to hide bulk
evidence, but so this skill and any other caller share the same judgment instead of each
re-deriving it, and so that judgment stays isolated the same way `audience-stage-classifier`'s
already is.

## Guardrails

- Never judge the audience's stage in this skill's own reasoning -- that's
  `topic-audience-stage-classifier`'s job (Step 1).
- Never classify an audience's stage from a source document (a draft or transcript) here -- this
  skill only expands an already-known or already-stated audience state; if the audience isn't
  already stated, the caller must ask for it (e.g. via `AskUserQuestion`) before calling this
  skill.
- Keep Step 1 (stage) and Step 3 (prerequisite) as separate passes -- a stated prerequisite must not
  change which terms are owed, and the stage must not change which prerequisites are considered
  known.
