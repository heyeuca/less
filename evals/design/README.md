# Design checker

Checks D cases in `../evals.json` (spec-v0.3 §5) at 1280×800 and 320×640.
Gates (all must pass): G1 roles kept, G2 selectors/CSS text kept, G3 no new axe
violations (wcag2a/2aa/21aa/22aa), G4 interactive nodes kept unless
`must_remove_hint` names them, G5 focus indicator and ≥24px target no worse,
G6 reflow at 320px holds if it held before. Element and CSS declaration counts
print as info only.

    npm ci && npx playwright install chromium
    node check.mjs self        # before, after, bad_after vs before
    node check.mjs OUT [ID]    # OUT/<id>.with.out.md (from ../run.py) vs before

A `must_keep_selectors` entry is a CSS selector (counted, hidden elements
included) unless it isn't a valid selector or uses a state pseudo-class such as
`:hover`; then it is CSS text, matched as a substring after whitespace is
normalized.

Selectors with pseudo-classes (`:hover`, `:focus-visible`, etc.) are always
compared as normalized CSS text, never matched in the DOM.

G5 accepts the browser's default focus ring (WCAG 2.4.7 needs visible focus
only); `outline:none` with no replacement fails. `npm test` runs fixtures in
`test/` proving both. `LESS_CASES=file.json` points the checker at other cases.
