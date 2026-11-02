# CLAUDE.md

This file provides guidance to Claude Code when working with the `document-writing` plugin's own
content, in addition to the marketplace-level guidance in the repository root `CLAUDE.md`.

## The `explain` skill family

`explain` drafts a topic into real connected prose for a stated audience, sized to a length budget
given as seconds/minutes to read or a direct character count, then delivers it to chat or an output
file. It does not run alone — it delegates to two subagents for language/budget resolution, to a
sibling skill for deciding what to cover, and to one of three sibling skills for drafting and
delivery. The full dependency tree, spanning `skills/`, `agents/`, and `references/`:

```text
skills/explain
├── Agent: explain-language-resolver          agents/explain-language-resolver.md
├── Script: explain_how_long.py                scripts/explain_how_long.py
│     └── (fallback) Agent: explain-how-long-converter  agents/explain-how-long-converter.md
├── Skill: explain-for-stated-audience         skills/explain-for-stated-audience/SKILL.md
│     ├── references/content-value-vocabulary.md
│     └── Agent: topic-audience-stage-classifier  agents/oath-formula/topic-audience-stage-classifier.md
│           ├── agents/oath-formula/references/awareness-stage.md
│           └── agents/oath-formula/references/owed-terms-output-contract.md
├── Skill: explain-deliver-chat-strict         skills/explain-deliver-chat-strict/SKILL.md
│     └── Script: explain_count_length.py      scripts/explain_count_length.py
├── Skill: explain-deliver-chat                skills/explain-deliver-chat/SKILL.md
│     └── references/structured-prose-formatting.md
└── Skill: explain-deliver-file                skills/explain-deliver-file/SKILL.md
      ├── references/structured-prose-formatting.md
      └── Script: explain_count_length.py      scripts/explain_count_length.py
```

## Bundled Python scripts

`scripts/` holds stdlib-only Python scripts that replace a deterministic step a prompt would
otherwise perform. Each one carries a PEP 723 inline-metadata header and is run as
`uv run --no-cache --script ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`. `--no-cache` keeps the call
independent of environment settings: a stdlib-only script gains nothing from uv's cache, while a
sandbox can leave that cache read-only, which makes uv fail before the script starts. Since uv is
not guaranteed in every environment, each calling skill keeps the original prompt-based procedure
as its fallback, used whenever the command fails or prints something other than one JSON object:

| Script | Replaces | Fallback |
| --- | --- | --- |
| `explain_how_long.py` | The `explain-how-long-converter` agent | That same agent |
| `explain_count_length.py` | The strict-mode "explicit tally" of a draft's length | Tallying by the skill itself |

`explain_how_long.py` must keep the same JSON output contract as `explain-how-long-converter`,
since `skills/explain` reads either one's response the same way. The one intentional difference is
the writing-system classification: the script uses a fixed set of ideographic languages
(`IDEOGRAPHIC_LANGUAGES`, currently `ja` and `zh`) and treats every other language as phonetic,
where the agent classifies from its own linguistic knowledge.

`explain` itself picks exactly one of `explain-deliver-chat-strict`, `explain-deliver-chat`, or
`explain-deliver-file` per invocation (based on whether an output path was given and whether the
length budget is a hard ceiling or a rough anchor) — the tree above shows all three because any of
them can be the one actually called.

## The `review-audience-coverage` skill

`review-audience-coverage` audits an EXISTING document against the audience its own framing implies,
reporting whether the document's actual content already covers what that reader still needs
explained. Unlike `explain`, it never drafts new content — it only reads and reports. Its full
dependency tree:

```text
skills/review-audience-coverage
├── Agent: audience-stage-classifier            agents/oath-formula/audience-stage-classifier.md
│     ├── references/content-value-vocabulary.md
│     ├── agents/oath-formula/references/awareness-stage.md
│     └── agents/oath-formula/references/owed-terms-output-contract.md
├── Agent: review-audience-coverage-reviewer     agents/review-audience-coverage/reviewer.md
│     └── references/content-value-vocabulary.md
└── Agent: review-audience-coverage-jargon-checker  agents/review-audience-coverage/jargon-checker.md
```

## Shared reference file

`references/content-value-vocabulary.md` is shared between the two skill families above — it is not
duplicated per family, since both `explain-for-stated-audience` and `review-audience-coverage-reviewer`
read the same top-level copy.

## Path conventions

Every file below resolves references to another bundled file via `${CLAUDE_PLUGIN_ROOT}` (e.g.
`${CLAUDE_PLUGIN_ROOT}/references/structured-prose-formatting.md`), never a hardcoded absolute path —
that env var resolves to this plugin's own installed root regardless of which machine or path it was
installed to.

`explain-language-resolver.md` and `explain-how-long-converter.md` are kept flat directly under
`agents/` (not nested) because a plugin agent's invocation name incorporates its subdirectory path
per Claude Code's own docs on plugin agents (`agents/review/security.md` in plugin `my-plugin`
registers as `my-plugin:review:security` — unlike user-level or project-level agents, where nesting
is cosmetic). Nesting either of these two would break the literal `subagent_type: "..."` strings
`skills/explain/SKILL.md` calls them by.

`topic-audience-stage-classifier.md` is one of several agents deliberately nested under a
subdirectory — `agents/oath-formula/` here, to sit alongside its own sealed reference files (below);
likewise `audience-stage-classifier.md` under the same directory, and `reviewer.md`/`jargon-checker.md`
under `agents/review-audience-coverage/`. `skills/explain-for-stated-audience/SKILL.md` and
`skills/review-audience-coverage/SKILL.md` still call these by their bare `subagent_type` values (e.g.
`"topic-audience-stage-classifier"`, `"audience-stage-classifier"`), with no plugin or subdirectory
prefix. Claude Code's own docs on plugin agents state that nesting under a plugin's `agents/`
directory folds the subdirectory into the agent's registered name (e.g. `agents/review/security.md`
in plugin `my-plugin` registers as `my-plugin:review:security`), which would suggest a prefix is
required here too — but in practice these bare calls resolve correctly, so the bare names are kept
on the strength of that observed behavior rather than the documented plugin-nesting rule.

`references/` files (plain `Read` targets, never invoked by name) are unaffected by the nesting rule
above. `awareness-stage.md` and `owed-terms-output-contract.md` live under
`agents/oath-formula/references/` rather than the top-level `references/`, unlike
`content-value-vocabulary.md` and `structured-prose-formatting.md`. Those two files hold the O/A/T/H
stage table and its output contract, meant to stay readable only by `audience-stage-classifier` and
`topic-audience-stage-classifier` and never by a skill. Nesting them inside `agents/oath-formula/`
rather than the shared `references/` makes that boundary structural — no `skills/` file has a reason
to look there — instead of relying on a comment to enforce it.
