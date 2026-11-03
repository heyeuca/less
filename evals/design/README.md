# Design checker

Checks D cases in `../evals.json` (spec-v0.3 §5) at 1280×800 and 320×640.
Gates (all must pass): G1 roles kept, G2 selectors/CSS text kept, G3 no new axe
violations (wcag2a/2aa/21aa/22aa), G4 interactive nodes kept unless
`must_remove_hint` names them, G5 focus indicator and ≥24px target no worse,
G6 reflow at 320px holds if it held before, G7 every fixed/sticky element with
text on the returned page that content scrolls under has an opaque fill or a
`backdrop-filter` (computed style, not pixels; one already see-through before,
same tag and about the same place, prints a pre-existing note instead), G8
required removals hold. Element and CSS declaration counts print as info only.

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

Full run: `python3 evals/run.py prompts OUT` (D-case with-skill prompts also
include `references/design.md`), save replies as `OUT/<id>.with.out.md` and
`OUT/<id>.without.out.md`, then `node check.mjs OUT` and
`node check.mjs OUT --suffix without`. Each writes `OUT/design-<suffix>.json`;
`python3 evals/run.py sheet OUT` puts those gate results in the pass columns.

`format: jsx` cases (D11, D12) are static JSX: the checker renders the returned
tree to HTML (`className`→`class`, `htmlFor`→`for`, `{…}` props dropped) with
`fixtures/tailwind.css`, which was precompiled once with `@tailwindcss/cli`
(no Tailwind at check time). CSS-text entries match the JSX source.

G8 checks explicit `must_remove_selectors` (absent from the rendered DOM) and
`must_remove_text` (absent from whitespace-normalized source). Unlike the
preservation gates, it rejects unchanged output on reduction cases. These are
fixture-specific assertions, not a general visual quality score. In `self`
mode, `before` checks preservation only; `after` must pass all gates and
`bad_after` must fail at least one gate, otherwise the command exits nonzero.

Use `must_remove_rendered_text` for visible content (body innerText, with HTML
entities decoded by the browser, matched case-insensitively). Keep `must_remove_text` for source-only
assertions. Content checks avoid requiring a particular tag or wrapper layout.
`must_have_styles` asserts canonical computed CSS values on every matching
element and requires at least one match. A `hover: true` assertion checks each
matching element while hovered. D12 protects the focus ring separately while
requiring no decorative shadow, transition, or scale at rest and on hover.
`must_remove_computed_background` rejects computed linear gradients (including
pseudo-elements), regardless of function case or CSS escapes. D07 requires the form's four border
widths to be zero and its box-shadow to be none, independent of declaration
spelling. D11 uses `must_remove_nested_surfaces` to reject styled div, section, article, aside, or main containers nested
inside another such container; unstyled layout wrappers and
useful spans remain allowed. These are fixture-specific checks, not a general
classifier for visual clutter. `npm test` covers entity-encoded emoji, retagged
copy, equivalent CSS, retained decoration, and legitimate layout changes.
