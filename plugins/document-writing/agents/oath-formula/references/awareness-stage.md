# Awareness Stage (O/A/T/H)

Sealed reference for the `audience-stage-classifier` and `topic-audience-stage-classifier` agents
only. Never referenced from `skills/` or any other root-context-visible file
for why this table lives in its own file. By default only `owed_terms` (see "Owed-terms derivation"
below) is meant to surface upstream; the stage letter and evidence surface only when a caller
explicitly signals debug mode.

| Stage | Audience's state | Already aware of | Needs explained next |
| --- | --- | --- | --- |
| O (Oblivious) | Doesn't know the topic/problem exists | — | `Issue` |
| A (Apathetic) | Aware but unmotivated | `Issue` | `Stakes` |
| T (Thinking) | Actively evaluating | `Issue`, `Stakes` | `Solution` |
| H (Hurting) | Needs this specific problem solved now | `Issue`, `Stakes`, `Solution` | `Conviction` |

## Owed-terms derivation

A stage's owed terms are the slice of the fixed order `Issue`, `Stakes`, `Solution`, `Conviction`
starting at that stage's `Needs explained next` value through the end of the list (e.g. O's `Needs
explained next` is `Issue`, so O owes all four; H's is `Conviction`, so H owes only `Conviction`).
Because the fixed order has exactly four terms, its four possible suffixes correspond bijectively to
the four stages, so this also works in reverse: a stated owed-terms list that is an exact contiguous
suffix of the fixed order identifies exactly one stage.
