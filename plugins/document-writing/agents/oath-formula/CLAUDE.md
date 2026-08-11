# CLAUDE.md

This directory holds the `topic-audience-stage-classifier` agent — and its private reference files —
that implement the O/A/T/H (Oblivious/Apathetic/Thinking/Hurting) audience-awareness-stage formula
for this plugin. Its purpose is to seal the formula's complexity, meaning the stage table and the
owed-terms derivation rule, inside an isolated agent context, so that no skill in this plugin and no
main conversation ever has to load that scaffolding itself.

## Files

- `topic-audience-stage-classifier.md` — judges the O/A/T/H stage from a short, already-stated
  `topic` and `audience` description, rather than inferring it from evidence. It exists so that
  multiple calling skills share one judgment instead of each re-deriving it. It also recognizes when
  `audience` already states an owed-terms list directly, and uses that list without reasoning about a
  stage at all.
- `audience-stage-classifier.md` — infers the O/A/T/H stage from existing evidence: an article draft,
  a chat transcript, or pasted text, rather than a stated topic/audience. Used by this plugin's own
  `review-audience-coverage` skill.
- `references/awareness-stage.md` — the sealed O/A/T/H table and the owed-terms derivation rule, read
  only by the two agents above.
- `references/owed-terms-output-contract.md` — the sealed output contract: the debug-mode signal
  phrase and the default/debug JSON shapes.

## Why `references/` is split out

`references/awareness-stage.md` and `references/owed-terms-output-contract.md` live in their own
files, separate from the agent that reads them, so that each piece of scaffolding exists in exactly
one place instead of drifting out of sync if duplicated inline. Both files are sealed to
`audience-stage-classifier` and `topic-audience-stage-classifier` only — no skill, and no other
plugin-root-visible file, may read them directly, since that would put the very scaffolding these
agents exist to hide back into the calling process's context.

Both `audience-stage-classifier` and `topic-audience-stage-classifier` are used within this plugin.

For why the agent itself is shaped the way it is — what it returns by default, what only surfaces in
debug mode — see the rationale the agent file states about itself; that reasoning is load-bearing for
the agent's own judgment calls, not just background for maintainers, so it stays next to the agent
rather than living here.
