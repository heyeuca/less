# less

**Less, but better.** — Dieter Rams

An agent skill to keep only what has a reason to exist.

less has your agent cut what has no clear reason to exist from writing, code, and UI code, and keep correctness, needed context, safety, accessibility, and what you asked for.

![A landing page without less and with less](demo/landing/side-by-side-top.png)

A landing page grok-4.7 built for a made-up app, then the same page after `/less`: 42% fewer elements and words, invented testimonials and stats gone, price and App Store button kept. Unedited, one run: [demo/landing](demo/landing/).

```text
Before: Great question! You're asking how to undo the last Git commit. To undo it while keeping your changes, run `git reset --soft HEAD~1`. I hope this helps! Let me know if you have other questions.
After:  To undo the last commit and keep your changes, run `git reset --soft HEAD~1`.
```

```html
<!-- Before -->
<span class="badge">New</span>
<h2>Orders</h2>
<ul id="list"><li>#1042 · Shipped</li></ul>
<p id="loading" role="status" hidden>Loading orders…</p>
<p id="empty" hidden>No orders yet.</p>
<p id="error" role="alert" hidden>Couldn't load orders. Try again.</p>

<!-- After: badge gone; hidden loading, empty and error states kept -->
<h2>Orders</h2>
<ul id="list"><li>#1042 · Shipped</li></ul>
<p id="loading" role="status" hidden>Loading orders…</p>
<p id="empty" hidden>No orders yet.</p>
<p id="error" role="alert" hidden>Couldn't load orders. Try again.</p>
```

## Install

Any agent that supports skills:

```sh
npx skills add heyeuca/less
```

Add `-y` to skip the prompts (CI, no TTY).

Claude Code plugin:

```sh
claude plugin marketplace add heyeuca/less
claude plugin install less@heyeuca
```

Cursor: `.cursor-plugin/plugin.json` mirrors the Claude Code manifest and
points at `skills/`. less is not listed in the Cursor Marketplace yet; until it
is, install it with `npx skills add heyeuca/less` above.

Manual: from a clone of this repo, copy `skills/less` into your agent's skills folder (`~/.claude/skills` here, or `~/.agents/skills`):

```sh
mkdir -p ~/.claude/skills && cp -r skills/less ~/.claude/skills/
```

less runs when you ask for it (`/less`, or "cut", "trim", "remove", "strip", "simplify", "tighten", "shorten", "declutter", "too long", "too busy", "looks cluttered", "clean up AI-written output"), on writing, code, and UI code. To keep it always on, add this line to your `AGENTS.md`:

```md
Apply the less skill to everything you write: keep only what has a reason to exist.
```

## Results

Measured with v0.3.3 on the 50 cases in [`evals/`](evals/), 2 runs with grok-4.7, against the same model without the skill.

- All cases: 50/50 in both runs (100%), with 0 must-keep misses in 100 outputs. Without the skill: 39/50 (78%), 10 misses in 50.
- Writing and code: 29–31% fewer words on 37 cases, with 0 must-keep misses and identical code behavior. Without the skill: 39% fewer, but must-keep content lost in 7 cases.
- UI: 17–18% fewer elements and 42% fewer CSS declarations on 13 cases, with 13/13 accessibility and semantics gates and 0 new axe violations in both runs. Without the skill: 10/13 on the gates and 9/13 by meaning.

A separate grading agent checks each case against its `must_keep` list; code is run and compared, and UI is checked with Playwright and axe. The runs were isolated from the repo. We tuned the skill on these evals, so read them as a regression test, not a benchmark, and only one model was tested.

These numbers predate the current evaluation protocol. The baseline arm was
asked to "Make this less verbose." while the skill arm got `/less`; the runner
now gives both arms the same task instruction, so only the skill context
differs. UI checks now also require fixture-specific removals (G8). The numbers
above have not been remeasured with these changes. Future reports should retain
model/version settings, raw outputs, grading decisions, and behavior-check
commands so results can be reproduced.

The current suite adds 14 paired preservation cases and 8 cases that cover
every remaining rule ID (72 total). See the
[evaluation guide](evals/README.md) for separate removal, preservation, damage,
and exact no-op checks. No updated model performance result is claimed.

## License

[MIT](LICENSE)
