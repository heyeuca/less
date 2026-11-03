# Design

For UI code (HTML/CSS, JSX/TSX, Tailwind) the agent wrote or the user points at,
and design spec or review docs (those also follow the writing and document rules).

The test comes first: does this element have a clear reason to exist for this
user's request? A signal below only nominates a candidate. Check every
candidate against "Never remove" before removing it.

Removal only: no new aesthetic, fonts, or palette. Change markup and styles
only; keep handlers, form `name`/`type`, `href`, test ids, and component APIs.

Figma files, screenshots, and other visual inputs: return them unchanged plus
one line: "less edits code or text it can return."

## Removal order

1. **R1 Decoration:** gradient washes, glows, blobs (C1); the same border,
   shadow, and radius stacked on every surface (C2).
2. **R2 Nesting:** cards in cards, wrappers with no layout job (C3).
3. **R3 Chrome:** eyebrow labels, badge pills, all-caps tracked labels (C4);
   fake 01/02/03 markers on non-sequential content (C5); icons and emoji that
   carry no meaning (C6); duplicate labels (C10); appended arrows and
   middle-dot meta strings (C11). Fixed badges or labels not tied to data or
   state (e.g. a hardcoded "New") may go; hidden state elements may not (K8).
4. **R4 Unrequested content:** sections and buttons nobody asked for (logo
   strips, testimonials, a second CTA) (C7); filler and slogan copy (C8).
   Only content the agent added; what the user wrote is theirs.
5. **R5 Motion:** entrance and hover animation that answers no user action;
   `transition: all` (C9).
6. **R6 Cleanup:** utility classes or selectors that cancel or repeat each
   other (C12).

## Signals

| ID | Signal | Looks like |
|---|---|---|
| C1 | Decorative gradient washes, blobs, glow | `bg-gradient-*`, `linear-gradient` on non-brand surfaces, `blur-3xl` orbs |
| C2 | Identical shadow and border on every surface | `shadow-*` + `border` + `rounded-*` on each card; `rgba(0,0,0,.1)` |
| C3 | Cards in cards | a card-classed element nested inside another |
| C4 | Eyebrow labels, badge pills above headings | `uppercase tracking-*` span before `h1`–`h3` |
| C5 | Fake sequence markers (01/02/03) | numbered spans in non-`ol` lists |
| C6 | Decorative icons and emoji | icon above every card title, emoji in headings |
| C7 | Unrequested sections and buttons | logo strips, testimonials, a second CTA |
| C8 | Filler copy, triads, slogans | "Empower your team…" with no specific claim |
| C9 | Scattered entrance and hover animation | per-section fade/slide-up, `transition: all`, hover on non-interactive cards |
| C10 | Duplicate labels | eyebrow repeating the heading; tooltip repeating visible text |
| C11 | Arrows and middle-dot meta as chrome | `→` on every link or button; `A · B · C` |
| C12 | Classes that cancel or repeat each other | conflicting padding/margin selectors |

## Never remove

- **K1 Accessible names:** `<label>`, `aria-label`, `alt` on meaningful
  images, visible label text (WCAG 3.3.2, 4.1.2, 2.5.3, 1.1.1).
- **K2 Semantics:** headings, landmarks, lists, tables; don't flatten them
  into `div`s (1.3.1).
- **K3 Text contrast:** 4.5:1, or 3:1 for large text, after removing any
  background or overlay (1.4.3).
- **K4 Boundaries:** a border or shadow that is a control's only ≥3:1
  indicator (1.4.11).
- **K5 Focus and target:** focus styles; no `outline: none` without a
  replacement (2.4.7). Targets stay ≥24×24 CSS px or adequately spaced (2.5.8).
- **K6 Motion opt-out:** `prefers-reduced-motion` handling. Removing the
  animation is fine; removing the opt-out isn't (2.3.3).
- **K7 Signifiers:** cues that show what is clickable; color is never the
  only cue (1.4.1).
- **K8 States:** error, empty, and loading branches, even if they look unused
  (3.3.1, 4.1.3).
- **K9 Responsive behavior:** breakpoints and media queries; reflow at 320 CSS
  px (1.4.10).
- **K10 Brand:** logo, brand tokens, required legal text.
- **K11 The user's ask:** anything requested, including sections, fields, and
  buttons.

K1–K11 protect the named items only, not everything near them. When unsure
whether a removal breaks one, keep it.
