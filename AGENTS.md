# Instructions for coding agents working on Sleeperplan

Mission: make a small, deterministic, offline workshop tool reliable enough to support a repeatable sleeper flower-bed service. No web/customer-facing work unless Jake explicitly changes scope.

## Invariants

1. One geometry model drives BOM, fixings, cut assignment, CAD and every drawing. Never “fix” a drawing by changing dimensions only in the renderer.
2. Integer millimetres for timber and stock; integer pence for money. Hole centres can be fractional. Reject booleans/floats masquerading as timber units.
3. Same timber section/profile throughout a job. No hidden mixed cap sizes. No automatic mid-side splices. Prefer uninterrupted sides.
4. A finished piece consumes its length, plus all actual kerf/trim losses. Do not use the universal n-1 kerf shortcut when a trailing offcut must be separated.
5. Exact optimisation may be claimed only after completing the exact search. A bounded fallback must say heuristic. Do not use a failed heuristic as proof of infeasibility.
6. Label every physical stock item, component and fixing. Keep original-stock datum A distinct from the resulting component's local A datum.
7. Validate actual receiving timber, screw endpoints and modelled collision clearance. Never derive drill-bit diameter from screw diameter alone.
8. A mark-out coordinate is not structural engineering or proof of screw capacity. Default examples must remain drafts. Do not populate fictitious review/pilot evidence to make release pass.
9. Missing costs remain unknown, never zero. Whole packs/spares are rounded across the batch. Margin and markup are different.
10. Plans are side-effect free until export. Never silently modify an input/catalogue/inventory, place orders, scrape live prices, overwrite output folders or add telemetry.
11. Comparisons are independent alternatives and reset reviews. Inventory proposals apply only after physical job completion.
12. Preserve source URLs/dates and normalised inputs. Changes affecting results require a version bump and regression tests; meaningful job edits require renewed physical review.

## Test first

```sh
python -m unittest discover -v
python -m sleeperplan plan examples/neighbour.json --as-of 2026-09-06 --out /tmp/sleeperplan-new-run
```

The main example is deliberately not a completed neighbour survey. Baseline: outside 2400 x 1200 mm, 100 x 200 mm section on edge, alternating corners, three courses; 12 parts; 52 fixing entries; 9 purchased 2400 mm sleepers; 8 crosscuts with 3 mm kerf; 1210 litres geometric fill; timber/screws GBP 294.60 at the supplied dated prices and 10% screw allowance. Two-course independent alternative: 6 sleepers; timber/screws GBP 189.30. Those are not complete installed job costs.

Read docs/ENGINEERING.md before changing any joinery, kerf, support, screw or release logic. Read docs/VALIDATION.md before claiming tested platforms or physical correctness. Add a reproducer for every physical/math failure before changing code.
