# Content-value Vocabulary

Shared term glossary used by both skills (e.g. `explain-for-stated-audience`) and
agents (e.g. `topic-audience-stage-classifier`). This file holds only the vocabulary itself — never the
O/A/T/H awareness-stage table or classification procedure, which stay sealed under
`agents/oath-formula/references/` and are never published here.

| Term | Definition |
| --- | --- |
| `Conclusion` | The abstract, structural name for what's stated first |
| `Concerns` | "What the audience wants to know" -- the concrete substance a `Conclusion` states |

`Conclusion` and `Concerns` are two names for the same thing, so stating the `Conclusion` always
means stating the audience's `Concerns`. `Concerns` takes several concrete kinds:

| Kind of `Concerns` | Definition |
| --- | --- |
| `Issue` | The surface-level matter the audience brings to the topic, before investigation clarifies it |
| `Stakes` | The cost of leaving the `Issue` unresolved |
| `Cause` | The root reason the `Issue` exists, found through investigation |
| `Solution` | The technically correct answer, fix, or recommendation |
| `Conviction` | Confidence to commit to `Solution` now, built via evidence, precedent, transparency |

The following three terms form a chain, in order:

- `Issue`
- `Cause`
- `Solution`

`Stakes` sits outside that chain, naming the cost of leaving the `Issue` unresolved. `Conviction`
sits outside the chain too, at the opposite end, building confidence that acting on `Solution` now
is safe, via:

| Mechanism | Description |
| --- | --- |
| Verification evidence | Tests passing, reproduced behavior |
| Precedent | Established patterns already in use elsewhere |
| Transparency | Risk and reversibility made clear |
