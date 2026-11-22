---
name: commit
description: >-
  Commits the current staging area with a commit message consisting of a title line only — no body,
  no trailers. Never stages, unstages, or otherwise modifies files; it commits exactly what is already
  staged.
when_to_use: >-
  Use whenever the user explicitly asks to commit, whether by invoking /git:commit or by asking in
  plain words (e.g. "commit this"), instead of the default commit procedure. Never invoke it on your
  own initiative, e.g. right after finishing a task, without the user asking to commit.
allowed-tools:
  - Bash(git status*)
  - Bash(git diff --cached*)
  - Bash(git log*)
  - Bash(git commit -m *)
---

# Commit

## Why the message is a title only

A commit message is a poor place to describe anything: it lives apart from the code it explains, and
readers of the code rarely look it up. Nevertheless, AI agents do read commit messages (e.g. through
`git log` or `git blame`) and are affected by them. Since the user rarely reads commit messages, a
description in one easily contains something the user doesn't know about (e.g. a body an agent
drafted that nobody reviewed), and such a description can steer a later agent in ways the user can
neither anticipate nor trace, producing unexpected results. When something is worth
noting, the developer describes it directly around the target code (e.g. as a comment) instead. The
commit message therefore only needs a title that identifies the change.

## Steps

1. Run `git diff --cached --stat` and `git diff --cached` to read what is staged.
   - If nothing is staged, stop and tell the user so. Never run `git add` or any other command that
     changes the staging area on the user's behalf.
2. Run `git log --oneline -10` to match the repository's existing title style (language, casing,
   prefixes such as Conventional Commits if the history uses them).
3. Write one title line for the staged change:
   - Imperative mood, e.g. `Add retry to webhook delivery`, not `Added ...` or `Adds ...`
   - 50 characters at most
   - No trailing period
   - Describes what the change does as a whole, not a list of touched files
   - If the change cannot be identified within 50 characters, do not abbreviate or cram it in. The
     staging area most likely mixes multiple changes, so stop without committing and suggest to the
     user how to split it into separately staged commits.
4. Commit with exactly that one line:

   ```bash
   git commit -m "<title>"
   ```

   - Pass only a single `-m`. Never add a second `-m`, a body, or trailers such as `Co-Authored-By`.
   - Never pass `--amend`, `--no-verify`, or `-a`/`--all`.
5. If a pre-commit hook fails, report the hook's output to the user and stop. Never retry with
   `--no-verify`.
6. Report the resulting commit (`git log --oneline -1`) to the user.

## When the change seems to need an explanation

If the staged diff contains something a future reader would need explained (a non-obvious workaround,
a reason behind a choice), do not put that explanation into the commit. Instead, tell the user after
committing which spot looks like it deserves a comment in the code itself, and leave the decision to
them.
