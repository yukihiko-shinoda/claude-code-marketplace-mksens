# Explain Manual Preparation

Prompt-based counterpart of `explain_prepare.py`, used by the `explain` skill only when that script
is unavailable or can't resolve the language. It sets the variables `explain` needs for the rest of
its steps. `<plugin-root>` below stands for the plugin root `explain` names when pointing here.

## 1. Extract the flags

Take the raw how-long text, the same text piped to the script, and repeat the following extraction
until no more matches remain anywhere in that text -- these flags may appear in any order relative
to each other:

- `--debug` (a standalone token) -- strip it, enable `explain`'s own debug mode.
- `-l` followed by whitespace and the next token -- strip both, keep the token as `$language-flag`.
- `-o` followed by whitespace and either a double-quoted string or the next whitespace-delimited
  token -- strip both, keep the value as `$output-path`.

Then trim whatever remains, along with any double quotes around it -- that is the literal how-long
budget string (e.g. `5m`). If a
`-`-prefixed token remains that matched none of the three flags, ask the user to clarify it rather
than silently ignoring it. If the budget string is empty, ask the user for it instead of guessing.

## 2. Resolve the output language

Call `Agent` with `subagent_type: "explain-language-resolver"`, passing all of the following:

- The topic
- The audience
- `$language-flag` (empty string if `-l` wasn't given)
- `$ambient-language`

If the response has `error`, use `AskUserQuestion` to ask for a valid `-l` value instead of
guessing. Otherwise keep `language` as `$resolved-language` and `source` as `$language-source`.

## 3. Convert the how-long budget

Run the bundled script with `Bash`, passing the budget string from section 1 and
`$resolved-language`:

```bash
uv run --no-cache --script <plugin-root>/scripts/explain_how_long.py "<how-long>" "<resolved-language>"
```

Use its stdout only when it is a single JSON object. If the command fails, or prints anything else,
call `Agent` with `subagent_type: "explain-how-long-converter"`, passing the same two values
instead. Both share one output contract: if the response has `error`, use `AskUserQuestion` to ask
for a valid budget, showing examples (`30s`, `5m`, `500c`). Otherwise keep all of the following as
the same-named variables:

- `target`
- `metric`
- `typology`
- `strict`

## 4. Select the case

Set `$case` from this deterministic table -- never guess or reason about which case fits; the table
is exhaustive and mutually exclusive, checked in this fixed order:

- **`$output-path` is present, regardless of `$strict`** -- `explain-deliver-file`.
- **`$output-path` is absent AND `$strict` is `true`** -- `explain-deliver-chat-strict`.
- **`$output-path` is absent AND `$strict` is `false`** -- `explain-deliver-chat`.

Leave `$output-action` unset: `explain-deliver-file` then checks `$output-path` itself.
