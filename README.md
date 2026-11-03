# less

**Less, but better.**

An agent skill to keep only what has a reason to exist.

## Install

Any agent that supports skills:

```sh
npx skills add heyeuca/less
```

Claude Code plugin:

```sh
claude plugin marketplace add heyeuca/less
claude plugin install less@heyeuca
```

Manual: copy `skills/less` into your agent's skills folder, for example `~/.claude/skills/less` or `~/.agents/skills/less`.

less runs when you ask for it (`/less`, or "cut", "trim", "simplify", "tighten", "shorten", "too long", "clean up AI-written output"). To keep it always on, add this line to your `AGENTS.md`:

```md
Apply the less skill to everything you write: keep only what has a reason to exist.
```

## License

[MIT](LICENSE)
