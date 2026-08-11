# CLAUDE.md

This directory holds the two subagents the `review-audience-coverage` skill delegates to for
judging an existing document: whether its owed content-value terms are covered, and whether its
jargon is adequately explained. Its purpose is to seal each judgment's own scaffolding inside an
isolated agent context, so the calling skill and the main conversation never load the document body
or the judgment criteria directly.

## Files

- `reviewer.md` (`review-audience-coverage-reviewer`) — given a document (or pasted text) and an
  already-resolved `owed_terms` list, judges per term whether the document's body covers it,
  partially covers it, or is missing it.
- `jargon-checker.md` (`review-audience-coverage-jargon-checker`) — given a document (or pasted
  text), flags domain-specific/technical terms used without an inline gloss, link, or upfront
  prerequisite pointer. Self-contained; reads no other bundled reference file.

Both agents are called by `skills/review-audience-coverage/SKILL.md`, alongside the
`audience-stage-classifier` agent in `../oath-formula/`, which resolves the `owed_terms` list
`reviewer.md` needs before either agent here is called. See the plugin root's `CLAUDE.md` for the
full dependency tree.
