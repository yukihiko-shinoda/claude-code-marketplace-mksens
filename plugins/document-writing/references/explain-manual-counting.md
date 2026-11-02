# Explain Manual Counting

Prompt-based counterpart of `explain_count_length.py`, used by the strict delivery skills only when
that script is unavailable. Start with no revisions made, then repeat the following checks in order
after each revision:

1. **Markdown check** -- only when the calling skill delivers plaintext. Check by eye for all of the
   following:

   - Headers
   - Emphasis markers
   - Backtick code spans
   - Links

   If any is present, remove it, count that as one revision, and start the checks again.
2. **Length check** -- tally the draft explicitly in `$metric`, without surrounding whitespace:
   every character for `characters`, every whitespace-separated token for `words`. If the tally
   exceeds `$target`, drop or merge the next-least-essential point, count that as one revision, and
   start the checks again.
3. **Deliver** -- once both checks pass, continue to the calling skill's delivery step.

After 3 revisions, deliver the draft as it stands if a check still fails, rather than looping
indefinitely. This fact stays visible in this conversation's own transcript, which is enough for
`explain`'s own trailing Debug step to reference later if its debug mode is on.
