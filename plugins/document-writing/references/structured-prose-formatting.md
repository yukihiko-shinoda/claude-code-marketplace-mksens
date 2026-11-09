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

## Diagrams

Draw at least one diagram in every explanation. Pick the relationship among `$points` that a
reader gains the most from seeing rather than reading, such as any of the following:

- A flow of events
- A hierarchy
- An order of steps
- How parts depend on each other

The diagram's form depends on where the explanation is delivered:

| Caller | Form | Why |
| --- | --- | --- |
| `explain-deliver-chat` | A `text` code block, in characters only | A chat client may show Mermaid as raw code |
| `explain-deliver-file` | A `mermaid` code block | GitHub and VS Code previews render it |

A `text` diagram may take whatever shape fits the relationship, such as any of the following:

- Boxes
- A flow with arrows
- Branches
- A cycle
- Side-by-side columns

The only limit concerns labels holding full-width/multibyte characters (Japanese, CJK, etc.): never
place anything to the right of such a label on the same line that must line up with another line,
such as a closing box border, an arrow continuing past the label, or a second column. A full-width
character takes two columns in most monospace fonts, and some symbols (e.g. `→`, `∩`, `①`) take one
or two depending on the font, so anything drawn to their right falls out of line. Either of the
following keeps such a diagram aligned:

- **Label at line end:** end each line with its full-width label, drawing arrows and branches to its
  left or on lines of their own, with ASCII connectors (`+`, `-`, `|`, `>`, `v`):

  ```text
  ユーザーの質問
      |
      v
  Mermaid対応?
      |
      +-- Yes --> 図として表示
      |
      +-- No ---> コードのまま表示
  ```

- **Half-width keys:** draw boxes or columns with half-width keys such as `[A]` inside them, then
  explain each key in the explanation's language right below the diagram (e.g. `A: ユーザーの質問`).

Place the diagram as the content of a bullet item in the reason list beneath the conclusion it
illustrates. It never replaces a conclusion sentence, and it never opens the explanation, since the
ordering rule above still puts the overall point first.

A diagram counts toward neither `$target` nor the heading anchor above -- judge both by the prose
alone. Since the diagram costs nothing against the budget, the prose alone must still cover every
point; the diagram only adds a view of it.

## Links

When a statement comes from a source whose URL already appears in this conversation -- in the
user's own message, a file already read, or an earlier tool result -- link that source inline at the
statement it supports. Never call `WebSearch` or `WebFetch` to find a link, and never write a URL
from memory, since a recalled URL may not exist. With no such URL, the statement simply goes
unlinked.

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
