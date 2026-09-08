# Reference: construction pack exemplar (commit 37db13b)

These files are an externally produced visual-construction pack for the
2400 x 1400 x 600 mm long-through model at repo commit `37db13b`. They set the
design standard for Sleeperplan's generated assembly manuals.

## Contents

- `Sleeperplan_Construction_Manual_37db13b_DRAFT.pdf` — 20-page visual step-by-step manual (landscape A4, course-coloured isometrics, stage-per-page narrative, do/don't callouts, per-course stack cards, drill/drive storyboard frames).
- `Sleeperplan_Workshop_Markout_37db13b_DRAFT.pdf` — 6-page workshop cut/mark-out reference cards.
- `Sleeperplan_Construction_PDF_Pack_37db13b_DRAFT.zip` — original distribution bundle.
- `pack/` — extracted bundle: `mark_out_2400x1400_three_courses.csv` (56-fixing register),
  `independent_checks.json`, `pack_manifest.json`, and the generator source
  (`pack/source/make_construction_pack.py`, `pack/source/review_model.py`).

## Provenance

- `pack_manifest.json`: source commit `37db13b`, model `examples/first-model-2400x1400.json`,
  model hash `94ab5b0d...`, status `DRAFT_VISUAL_CONSTRUCTION_PACK`.
- The geometry is an independent transcription (`review_model.py`) cross-checked against
  the committed r08 build artifacts; the pack's own manifest lists the unresolved items
  (pilot diameter/depth, head seat/recess, connection capacity, supports/drainage/site).
- **This is a DRAFT visual pack, not issued drilling instructions.** The manual itself
  says centres are known but drill settings are not; treat it exactly like our own
  DRAFT_MARK_OUT_ONLY outputs.

## How we use it

Adopted as the design target for `assembly-manual.pdf` (v0.5+): the "Book" page
system (kicker / declarative headline / callout boxes / course-colour coding /
stage aggregation instead of one page per fixing), ported to be **generated from
`operations.json` + `plan.json`** so it covers every height and footprint
automatically instead of being a hand-transcribed three-course exemplar.
