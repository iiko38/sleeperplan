# Workshop manual - First rectangular bed draft - 2400 x 1400

Plan: `50c064c82d0d06387b49013ee177332ee455f2679ac6b4c581b456ecfcb4cf3e`  |  Status: DRAFT_MARK_OUT_ONLY  |  As of: 2026-09-06

## Use these files in order

1. `drawings/process-overview.svg`
2. `drawings/stock-arrival-labelling.svg`
3. `drawings/cuts-*.svg` + `cuts.csv`
4. `drawings/*-C*-plan.svg`
5. `drawings/*-fixings.svg` + `fixings.csv`
6. `drawings/fastener-*.svg` + `shopping.csv`

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
