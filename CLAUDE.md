# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository is a Claude Code plugin marketplace (`mksens`) — a `.claude-plugin/marketplace.json`
manifest plus a `plugins/` directory, with no build system, package manager, or test suite. Every
plugin's content is plain Markdown/JSON consumed directly by Claude Code, so "development" here means
authoring or editing those manifest and content files, not compiling or running code.

## Commands

There are no build, lint, or test commands. Iterate on changes by installing this repository as a
local marketplace and exercising the plugin's effect inside a Claude Code session:

```bash
# Register this checkout as a marketplace (repeatable after edits)
claude plugin marketplace add /workspace/claude-code-marketplace-mksens

# Install a plugin from it
claude plugin install document-writing@mksens

# List plugins the marketplace currently declares
claude plugin marketplace list

# Unregister the marketplace
claude plugin marketplace remove mksens
```

After installing, an output style becomes selectable from inside a Claude Code session via the
`/config` command's **Output style** menu — that picker is the only way to verify a style's behavior
actually matches what its Markdown file describes.

## Architecture

### Marketplace → plugin → content hierarchy

`.claude-plugin/marketplace.json` is the entry point Claude Code reads first: it declares the
marketplace's `name` (the `@mksens` suffix used in installs) and a `plugins` array, where each entry
maps a plugin `name` to a `source` directory. Adding a new plugin means creating that source directory
with its own `.claude-plugin/plugin.json` manifest and adding a corresponding entry here — the
marketplace manifest is never the place plugin behavior itself is defined, only where a plugin is
registered.

Each plugin directory owns its own `.claude-plugin/plugin.json` (name, version, description, author,
license, keywords) and its actual content in subdirectories keyed by content type — currently only
`output-styles/`, one Markdown file per style.

### Output style files

Each file under `plugins/document-writing/output-styles/` is a self-contained output style: YAML
frontmatter (`description`, `keep-coding-instructions`) followed by a Markdown body that is injected
as behavioral instructions whenever that style is active. The two existing styles encode different,
mutually exclusive response-shaping rules:

- `NestedList.md` — forces every response into headers (one per main point) with all supporting detail
  as nested bullet lists beneath them; no bare prose outside list items.
- `FreeToGo.md` — orders every response by the OATH customer-awareness formula (Oblivious, Apathetic,
  Thinking, Hurting), stating shared context before conclusions and conclusions before their reasons.

Adding a new output style means creating a new Markdown file here with the same frontmatter shape; no
registration elsewhere is needed since Claude Code discovers styles by scanning the plugin's
`output-styles/` directory directly.
