# claude-code-marketplace-mksens

The Claude Code marketplace of mksens.

## Advantage

This marketplace distributes ready-made Claude Code plugins, so that a project does not need to
hand-craft its own output style from scratch:

- `document-writing` plugin — adds output styles that keep every Claude Code response in a
  consistent, structured shape, plus skills for drafting explanations to a stated audience and length
  budget and for reviewing an existing document's audience coverage:
  - `NestedList` — organizes each response into headers, one per main point, with the supporting
    detail rendered as a nested bullet list under each header
  - `FreeToGo` — orders each response along the OATH formula (Oblivious, Apathetic, Thinking,
    Hurting), stating shared context before conclusions, and conclusions before their reasons
  - `explain` — drafts a topic into a real explanation for a stated audience, sized to a length
    budget given as seconds/minutes to read or a direct character count, delivered to chat or an
    output file
  - `review-audience-coverage` — reviews an existing document against the audience its own framing
    implies, checking whether owed content-value terms are covered and whether domain-specific
    jargon is adequately explained

## Quickstart

Installing the marketplace and a plugin from it takes two commands.

Adding this repository as a marketplace:

```console
claude plugin marketplace add https://github.com/yukihiko-shinoda/claude-code-marketplace-mksens
```

Installing the `document-writing` plugin from it:

```console
claude plugin install document-writing@mksens
```

Restarting Claude Code makes the installed output styles selectable from the `/config` command's
**Output style** menu.

<!-- markdownlint-disable-next-line MD026 -->
## How do I...

### How do I list the plugins available in this marketplace?

```console
claude plugin marketplace list
```

### How do I switch between the installed output styles?

Running the `/config` command inside a Claude Code session and selecting **Output style** opens a
picker where either `NestedList` or `FreeToGo` can be selected.

### How do I use the `explain` skill?

Invoke it directly inside a Claude Code session:

```console
/document-writing:explain "<topic>" "<audience>" "<how-long>"
```

### How do I use the `review-audience-coverage` skill?

Invoke it directly inside a Claude Code session:

```console
/document-writing:review-audience-coverage <path-or-text> [--debug]
```

### How do I remove this marketplace?

```console
claude plugin marketplace remove mksens
```
