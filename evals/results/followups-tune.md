# Follow-up rule experiment

Two candidate changes (not adopted) were tested in separate case groups with the same candidate skill:
unlinked headings that merely repeat their parent may be removed; a motion
opt-out may be removed only when no animation or transition remains for it.
No other skill wording was changed to address #53: its three failure shapes
are encoded as P17–P22 tune cases with protection/removal counterparts.

Both local CLI families ran P15/P16/D21/D22 three times. Raw replies, reported
model identities, prompts, scripts, and checker summaries are in
`followups-tune/`. P15 removes the redundant heading 6/6, and P16 preserves
all headings/links with presentation-equivalent no-ops 6/6. D21 and D22 pass
all browser gates 6/6 each. The previous published experiment kept the
redundant heading and orphaned opt-out 6/6 each.

The first checker pass incorrectly rejected valid motion outputs that also
removed the unused `.hero` class. The fixture now checks computed animation
on `section`, which remains present, rather than requiring that class. The
same raw replies were rechecked; none were regenerated for this correction.

These are tune experiments, not a new held-out claim. Their small script
recorded model identities but not complete execution receipts, so the browser
results remain explicitly unverified. Do not retrofit them with a new-style
freeze record. The full protocol-v2 measurement uses separately authored
V01–V10, raw exact equality plus presentation equality, and per-call receipts.
Any failed absolute gate in that measurement remains a failure.
