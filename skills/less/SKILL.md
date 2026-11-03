---
name: less
description: Removes elements without a clear reason to exist from writing and code, keeping correctness, needed context, safety, and everything the user asked for. Use when the user asks to cut, trim, simplify, tighten, or shorten something, says it is "too long", or asks to clean up AI-written output.
license: MIT
---

# Less

Less, but better. Keep only what has a reason to exist.

## The test

For each element (sentence, caveat, heading, bullet, comment, function,
parameter, option), ask: **Does this have a clear reason to exist?**
If not, remove it. Clarity beats brevity. When unsure, keep it.

## Don't apply

Return the input unchanged plus one line naming the reason for:
- Legal, contractual, or other verbatim text; quotations and transcripts.
- Existing code, config, or commands the user didn't ask to change.

A user-set length or format is not an exclusion: work inside it.

## Removal order

Check every candidate against "Never remove" first.

Writing:
1. Preamble and restated question.
2. Closing recap and offers ("Let me know if...").
3. Hedges and filler that change nothing.
4. Duplicate points (keep the clearest).
5. Unrequested caveats and alternatives that don't change what the reader does.
6. Decoration on short answers: headers, bold, bullets.
7. Merge and shorten the rest, keeping complete sentences.

Code:
1. Comments that restate the code.
2. Unrequested abstractions: single-use helpers, wrappers, interfaces, factories.
3. Unrequested options, flags, config.
4. Defensive code for cases that can't happen.

## Never remove

- Correctness: numbers, units, dates, conditions, exceptions, negations.
- Needed context: what the reader needs to act (prerequisites, steps, versions).
- Safety: data-loss, security, money, legal, irreversible-action warnings.
- The user's ask: requested content, format, length, constraints.
- Attribution and citations.
- The user's voice when editing their text. Don't rewrite style.
- Code: behavior (output, side effects, errors); error handling at real
  boundaries (I/O, network, user input); "why" comments, constraints, safety
  notes; public API and signatures unless asked.
- Anything whose purpose you can't determine.

## Stop

Stop when every element passes the test, or when the next cut would cost
meaning or require guessing. Never cut to hit a length.

## Output

The reduced text or code only, in the same format and language. Don't comment
on what was cut unless the user asks; then list it. If nothing should change,
return it unchanged.
