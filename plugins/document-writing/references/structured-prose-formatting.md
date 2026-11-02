# Structured Prose Formatting

Shared drafting/formatting procedure used by both `explain-deliver-chat` and `explain-deliver-file`
-- the two `explain` case-skills that render a Markdown-capable explanation (to chat, or to a
`.md` file). `explain-deliver-chat-strict` deliberately does not use this file: its own
plaintext-only, zero-Markdown restriction makes every rule below inapplicable, so it keeps its own
inline ordering rule instead of pointing here.

## Ordering

Order the explanation abstract-first then concrete, and conclusion-first then reason: state the
overall point before the supporting detail, both at the level of the whole explanation and within
each point it covers.

## Conclusion and reason rendering

Write each point's conclusion as one plain sentence. When a point needs supporting reasoning or
detail beyond that sentence, put that support in a nested bullet list directly beneath it, never
folded back into flowing prose -- even a single supporting reason still becomes a one-item bullet
under its conclusion, not a sentence beside it. If a reason itself needs its own further
justification, nest that justification one level deeper still, beneath the reason it supports.

## Headings

Below a rough length anchor, the drafted explanation renders with no headings at all -- just the
conclusion-and-nested-reason shape described above. As a rough anchor, judged by eye and never by a
tool call: about 280 half-width characters (Latin letters, digits, ASCII punctuation) alone, or
about 140 full-width/multibyte characters (Japanese, CJK, etc.) alone, or any mix that feels like
it's in that range. Once the drafted content runs long enough to cross that anchor, split it into
sections and give each one its own heading, nested by whatever depth the content's own structure
needs.

Start section headings one level below whatever title heading, if any, already wraps the whole
response -- for a caller with no such wrapper this starts at `##`; for a caller that wraps the
whole response under its own top-level heading, section headings start one level below that
wrapper. Both of this file's current callers converge on `##` as the starting level either way.

Word each heading as a neutral label naming that section's own content (e.g. "Dockerのレイヤーの仕組み").
Never use a heading that only names a structural role instead of content -- since that would
announce the response's own structure to the reader instead of what the section is about.
Forbidden examples include a local-language equivalent of any of the following:

- "conclusion"
- "reason"
- "summary"
- "overview"
- "abstract"
- "concrete"

Adding headings never changes the conclusion-then-nested-reason shape above -- it only wraps that
same shape in labeled sections once there's enough of it to need them.

## Mood

Phrase every sentence in a formal, polite, descriptive mood (e.g. Japanese `〜します`/`〜となります`)
rather than an imperative one (e.g. `〜してください`) -- describe what is true or what happens, never
instruct the reader to do something.

## Trailing-summary words

Never end any of the following on a word that merely paraphrases or wraps up what was just said
(e.g. a local-language equivalent of "in other words," "in short," "to summarize," "therefore,"
"so," "as a result"):

- A paragraph
- A bullet item
- The response itself

Landing one of those at the end of a passage is a
sign that the conclusion-first ordering above didn't actually happen there -- move the point it's
restating to the front of that passage instead, and delete the trailing word once it no longer
restates anything.
