# Workshop manual - First rectangular bed draft - 2400 x 1400

Plan: `3fe43733ec915f6d9bd9c9a43ad7f0d8b17cfb92f0a1b0db1c6f1b1acf8aee6e`  |  Status: DRAFT_MARK_OUT_ONLY  |  As of: 2026-09-06

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

All coordinates and counts are script-generated from the same geometry model that drives cuts, fixings and drawings.
