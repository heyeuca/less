# Demos

Each demo is a page an agent built from a short request, then the same page
after one `/less` pass by the same model. Neither file was edited by hand.
Each folder has the prompts, numbers, what was cut, what was missed, and
every attempt.

## Four small-business pages

Same setup for all four: gpt-5.6-sol through `codex exec`, a five-line
request with a name, a location, hours, a phone number, and five prices, then
`/less` with the skill at `414fc8b` and the original request. All four
requests ask for the same things, so the differences come from what the
model added.

| | Words | Elements | Height at 1280px | axe violations |
|---|---:|---:|---:|---:|
| [Dental](dental/) | 347 → 71 (−80%) | 256 → 81 (−68%) | 4753 → 1999px (−58%) | 18 → 2 |
| [Yoga](yoga/) | 405 → 95 (−77%) | 227 → 107 (−53%) | 4745 → 3250px (−32%) | 2 → 0 |
| [Bakery](bakery/) | 222 → 71 (−68%) | 114 → 65 (−43%) | 3467 → 2587px (−25%) | 14 → 2 |
| [Plumbing](plumbing/) | 325 → 166 (−49%) | 161 → 83 (−48%) | 3343 → 2111px (−37%) | 2 → 1 |

Every after page keeps all of the facts its request gave.

The main README shows dental because it lost the most. The topics were not
chosen at random, and each was run once per step, so read the spread between
them as run-to-run variation as much as a difference between topics. The
bakery was the first; its folder lists the four models and eleven runs that
led to it. Plumbing came next, then dental and yoga in parallel.

What the before pages added differs. The bakery invented the most checkable
facts (baked before sunrise, folded by hand, best selection before 11am).
Dental and yoga added promises and repeats: a cost estimator that lists the
five prices again, a booking form that sends nothing. Plumbing mostly
restated the request, so less had less to cut.

## Earlier

[Landing](landing/) is the first demo: a landing page for a made-up iPhone
habit tracker, built and cut by grok-4.7, with screen recordings.
