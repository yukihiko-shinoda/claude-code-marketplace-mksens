---
name: review-audience-coverage
description: >-
  Review an EXISTING document (README, docs page, article) against the audience its own framing
  implies, and report whether the document's actual content covers what that reader still needs
  explained. Infers the O/A/T/H stage from the document's own framing (delegating unchanged to
  audience-stage-classifier) to get owed_terms, then delegates to a second agent that judges, per
  owed term, whether the document body covers it, partially covers it, or is missing it. Also
  delegates to a third agent that flags domain-specific/technical terms used without adequate
  explanation — no inline gloss, link, or upfront prerequisite pointer — a separate, provisional
  axis of judgment from owed-term coverage. Renders a gap report combining both. Distinct from
  every other skill in this family, which all draft NEW content for a stated or inferred audience;
  this is the only skill that audits an existing document's actual coverage.
argument-hint: "<path-or-text> [--debug]"
arguments: [path-or-text]
allowed-tools:
  - Agent
  - AskUserQuestion
when_to_use: >-
  Invoke directly, e.g. /review-audience-coverage README.md, when the user wants to know whether an
  existing README/docs/article already covers what its own implied reader still needs, or has gaps.
  Not for drafting new content — that's explain-for-stated-audience or the audience-awareness rule.
---

# Review Audience Coverage

## Using Arguments

Invoke as `/review-audience-coverage <path-or-text> [--debug]`.

1. If `$path-or-text`, trimmed, ends with the literal token `--debug` (preceded by whitespace or
   standing alone), strip that token and enable debug mode. Use the remaining text for the rest of
   this section.
2. If what remains is empty, use `AskUserQuestion` to ask which document, directory, or pasted text
   to review instead of guessing.

## Steps

### 1. Infer the implied stage and owed terms

Call the `Agent` tool with
`subagent_type: "document-writing:oath-formula:audience-stage-classifier"`, passing `$path-or-text`
unchanged. If this skill's own debug mode is on (Using Arguments step 1), append this exact text to
the end of the prompt: `(debug mode: also report stage and evidence)`.

Parse the subagent's JSON response:

- **Single-result shape without a `path` field** — returned when `$path-or-text` was a file path or
  pasted text:

  Default:

  ```json
  {
    "owed_terms": [
      "<term>",
      ...
    ],
    "input_kind": "path" | "text"
  }
  ```

  Debug mode:

  ```json
  {
    "owed_terms": [
      "<term>",
      ...
    ],
    "stage": "<letter>",
    "evidence": "<text>",
    "input_kind": "path" | "text"
  }
  ```

  Treat this as one entry, labeled with `$path-or-text` itself when the response's `input_kind` is
  `"path"`, or labeled `"pasted text"` when `input_kind` is `"text"` — never re-derive this from
  `$path-or-text`'s own shape; use the subagent's own determination.

- **Single-result shape with a `path` field** — returned when `$path-or-text` was a directory that
  resolved to exactly one candidate file:

  Default:

  ```json
  {
    "owed_terms": [
      "<term>",
      ...
    ],
    "path": "<path>"
  }
  ```

  Debug mode:

  ```json
  {
    "owed_terms": [
      "<term>",
      ...
    ],
    "stage": "<letter>",
    "evidence": "<text>",
    "path": "<path>"
  }
  ```

  Treat this as one entry, labeled with the response's own `path` field — never assume the label
  from `$path-or-text` itself in this case, since `$path-or-text` names the directory, not the
  resolved file.

- **Multi-file shape** — returned when `$path-or-text` was a directory with more than one candidate
  file:

  Default:

  ```json
  {
    "files": [
      {
        "path": "<path>",
        "owed_terms": [
          "<term>",
          ...
        ]
      },
      ...
    ]
  }
  ```

  Debug mode: each file entry additionally carries `"stage"` and `"evidence"`.

  Treat each array entry as its own entry, labeled with its own `path`.

Each entry now holds `(label, owed_terms, stage?, evidence?)`.

### 2. Evaluate coverage per entry

For each entry from Step 1, call the `Agent` tool with
`subagent_type: "document-writing:review-audience-coverage:review-audience-coverage-reviewer"`,
passing that entry's own target (its file path, or the pasted text) and its `owed_terms` list. If
this skill's own debug mode is on, append this exact text to the end of the prompt:
`(debug mode: also report evidence per term)`.

Parse the subagent's JSON response, shaped as follows (each entry additionally carrying `"evidence"`
in debug mode), and attach it to that entry:

```json
{
  "coverage": [
    {
      "term": "<Term>",
      "status": "covered|partial|missing",
      "reason": "<short reason>"
    },
    ...
  ]
}
```

### 3. Scan for unexplained jargon

For each entry from Step 1, call the `Agent` tool with
`subagent_type: "document-writing:review-audience-coverage:review-audience-coverage-jargon-checker"`,
passing that entry's own target (its file path, or the pasted text) — no `owed_terms` needed; this
subagent finds its own candidates. If this skill's own debug mode is on, append this exact text to
the end of the prompt: `(debug mode: also report the surrounding excerpt per flagged term)`.

Parse the subagent's JSON response, shaped as follows (each entry additionally carrying `"excerpt"`
in debug mode), and attach it to that entry:

```json
{
  "unexplained_terms": [
    {
      "term": "<term>",
      "reason": "<short reason>"
    },
    ...
  ]
}
```

### 4. Render the report

Render Markdown to chat — never raw JSON. For each entry from Steps 1–3, render one section titled
`## Audience coverage review: <label>`:

- A one-line summary tally: "N of M owed points covered, P partial, Q missing."
- A table with columns `Owed term`, `Status`, `Why` (one row per `owed_terms` entry, in the order
  given) — capitalize `Status` as `Covered`/`Partial`/`Missing` for display.
- If any term is `partial` or `missing`, a closing **Suggested next step** line naming the
  highest-priority gap to address: prefer any `missing` term over any `partial` term regardless of
  which term each is, and among terms of equal status (both `missing`, or both `partial`) prefer the
  earlier term in the fixed `Issue`/`Stakes`/`Solution`/`Conviction` order. Omit this line entirely if
  every term is `covered`.
- If that entry's `unexplained_terms` is non-empty, a small closing subsection titled `### Possibly
  unexplained jargon` with one bullet per flagged term, in the order returned: `- **<term>** —
  <reason>`. Omit this subsection entirely when `unexplained_terms` is empty. Never fold these rows
  into the owed-terms table above — jargon-explanation adequacy is a separate axis of judgment from
  owed-term content-value coverage, and the two must stay visually and structurally distinct.

Only when this skill's own debug mode is on: prepend, above the summary line, "**Inferred reader
stage:** `<letter>` — evidence: `<text>`" and "**Owed terms:** `<comma-joined list>`" using Step 1's
`stage`/`evidence` for that entry; add an `Evidence` column to the table,
populated from Step 2's per-term `evidence` (or `"no matching passage found"` for `missing` rows);
and append each jargon bullet with its Step 3 `excerpt`, e.g. `- **<term>** — <reason> (excerpt:
"<text>")`.

For a multi-entry result (directory input with multiple candidate files), render each entry's whole
section one after another, in the order Step 1 returned them — never merge them into one combined
verdict.

## Guardrails

- Never classify the audience's stage, never judge term coverage, and never judge
  jargon-explanation adequacy, in this skill's own reasoning -- all three are delegated whole to
  their own subagent (Steps 1–3 respectively).
- Never modify the reviewed document -- this skill and all three subagents only read and report;
  surface gaps as prose for the user to act on, never as an automatic edit.
- Never `Read` the document directly in this skill's own context -- Step 1 passes `$path-or-text`
  through to `audience-stage-classifier` unchanged; Steps 2 and 3 each pass that entry's own resolved
  target (a specific file path, or pasted text, as determined in Step 1), never the raw
  `$path-or-text` and never re-derived by Reading the document directly in this skill's own context,
  keeping the bulk document text out of the main conversation.
- Keep Step 1 (stage/owed-terms), Step 2 (coverage), and Step 3 (jargon) as three separate `Agent`
  calls -- never fold any of them into another, and never skip one by guessing its result yourself.
- The jargon-explanation heuristic (Step 3's subagent) is provisional and admittedly abstract by
  design -- never tighten, loosen, or second-guess its verdicts in this skill's own reasoning; if
  the heuristic itself needs revision, that happens by editing the subagent file, not here.
- Never guess a missing `$path-or-text` -- always ask via `AskUserQuestion`.
