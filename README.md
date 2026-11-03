# less

**Less, but better.**

An agent skill to keep only what has a reason to exist.

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

Manual: from a clone of this repo, copy `skills/less` into your agent's skills folder (`~/.claude/skills` here, or `~/.agents/skills`):

```sh
mkdir -p ~/.claude/skills && cp -r skills/less ~/.claude/skills/
```

less runs when you ask for it (`/less`, or "cut", "trim", "remove", "strip", "simplify", "tighten", "shorten", "declutter", "too long", "too busy", "looks cluttered", "clean up AI-written output"), on writing, code, and UI code. To keep it always on, add this line to your `AGENTS.md`:

```md
Apply the less skill to everything you write: keep only what has a reason to exist.
```

## License

[MIT](LICENSE)
