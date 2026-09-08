# Workshop manual - Offer option - 2 courses

Plan: `4470e837809e9781fb6151995899ab6276423f648f2192abcb9fedfcb25a59de`  |  Status: DRAFT_MARK_OUT_ONLY  |  As of: 2026-09-06

## Read this first

- [2x] Use two people for heavy lifts and long members.
- [CHECK] Verify level, square and labels at every stage.
- [STOP] Any blocker in `BUILD.md` means stop and resolve before building.

## Prepare before assembly

1. Clear enough floor area to lay out full-length members.
2. Confirm stock IDs, part labels and datum A orientation before cuts.
3. Keep all fixings and driver bits grouped by screw ID.
4. Open the process and drawing sheets before drilling or driving.

## Pack map (use in order)

1. `drawings/parts-fixings-board.svg`
2. `drawings/process-overview.svg`
3. `drawings/stock-arrival-labelling.svg`
4. `drawings/cuts-*.svg` + `cuts.csv`
5. `drawings/*-C*-plan.svg`
6. `drawings/*-fixings.svg` + `fixings.csv`
7. `drawings/fastener-*.svg` + `shopping.csv`

## Step flow

1. Label incoming stock and mark datum A ends.
2. Perform trims and crosscuts in listed sequence only.
3. Mark each finished part ID and orientation (A/TOP/OUTER).
4. Assemble course 1 square and level, then fix.
5. Repeat by course using each course plan and fixing sheet.
6. Fit reviewed support/drainage details before filling.

## Drill and pilot rule

- `pilot_mode=pilot`: use the scripted drill-bit diameter/depth exactly.
- `pilot_mode=none`: no pilot, per recorded evidence.
- `pilot_mode=unconfirmed`: STOP. Do not drill until diameter/depth evidence is recorded.

## Draft workshop advisory (while unconfirmed)

- These are trial planning notes only, not release evidence for `pilot_mode`.
- For 7 mm timber-drive screws, trial softwood pilot around `4.5-5.0 mm`; in denser timber trial larger pilots around `5.5-6.0 mm`.
- For long screws (for example `250 mm`), trial deeper pilots to reduce torque and wandering.
- Near edges/ends: clamp, slow drive speed, and favour piloting to reduce split risk.
- Sleeper planter basics: level drained base, maintain open-bottom drainage, treat cut ends, and use corrosion-resistant fixings.

All coordinates and counts are script-generated from the same geometry model that drives cuts, fixings and drawings.
