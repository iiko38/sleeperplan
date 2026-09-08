# Offer option - 1 course


**DRAFT_MARK_OUT_ONLY** | 2026-09-06 | plan `fe0c049d92f327fcf251a889490e81ddd6ee0db1f3f343bc8b58b973c6dcc0ea` | physical design `8c2746063b90b4419470b5e209df7589551b1a14d9489f3dc862551574fd2fa5`


## Before work starts

This pack checks nominal geometry, stock allocation and straight screw paths. It does not calculate structural capacity, soil pressure, foundation adequacy or long-term timber movement. Do not build from an unreviewed draft. Site-specific supports/bracing are not part of the generated timber model.


- **BLOCKER / timber_and_kerf_measured**: Measure actual stock length/section, usable ends and saw kerf; update inputs before cutting.
- **BLOCKER / site_and_supports_reviewed**: Review foundations, drainage, soil loads, support/bracing and any buried services on site.
- **BLOCKER / fixing_schedule_reviewed**: Review screw suitability, end-grain connections, penetration and spacing with a competent builder / supplier.
- **BLOCKER / review_record**: Record reviewer, reviewed_on and review notes before releasing a workshop pack.
- **BLOCKER / approval_hash_required**: Release readiness requires review.approved_physical_design_hash to equal the current physical design hash, so an edited job cannot inherit an old review. Run a draft plan, then copy the printed physical design hash into the job's review block after a genuine physical review.
- **BLOCKER / pilot_unconfirmed**: wickes-287686: fixing centres are mark-out only. Confirm pilot diameter/depth or a manufacturer-supported no-pilot instruction; none is inferred.
- **Note / reach**: offer-bed-01: centre reach is approximately 700 mm from 2 accessible side(s); confirm with the user. 650 mm is a planning prompt, not an accessibility standard.
- **Note / factory_ends**: Zero end trim assumes square, sound, usable factory/cut ends. Nominal 2400 mm is not a measurement.
- **Note / incomplete_cost**: Known subtotal only; unpriced: consumables, fill, liner, preservative, site_preparation, supports, transport, labour
- **Note / supply**: Catalogue prices are dated snapshots. The configured store and collection stock are NOT confirmed.
- **Note / not_structural**: Geometry and straight screw-path clearance are checked; timber strength, screw capacity, long-term movement and soil pressure are NOT calculated. Supports/bracing, liner detailing and foundations are site-specific and not drawn by v1.


## Read the dimensions correctly

All plan dimensions are millimetres. Timber wall thickness is **100 mm**; each course adds **200 mm**. Outside dimensions include the walls. Interior dimensions subtract two wall thicknesses. The drawing's S/W labels define a reference frame; they need not point south or west on site.

Piece A is the lower-global-X end for S/N members, or lower-global-Y end for W/E members. U runs from A along the piece. V runs from the lower-coordinate cross-section edge (not always the outside face). W runs upwards from the piece bottom. Top fixings enter at W=course height; outer-face entries have V=0 for S/W and V=wall thickness for N/E. Use labelled piece sheets instead of guessing the orientation.


## Assembly sequence

1. Survey the footprint and access. Identify buried services before any ground work. Confirm a level, open-bottom site and adequate drainage. Record the separate support/foundation plan. Check the purchase list and collection/handling arrangements.

2. Inspect and measure the timber: actual usable lengths, section, straightness and end condition. Measure actual saw kerf with a test cut. Set end trims explicitly, update the catalogue/job and regenerate. A nominal 2400 mm sleeper is not guaranteed to yield a square 2400 mm part.

3. Lay out the proposed frame full-size. Check external dimensions and equal outside diagonals. Confirm access to plant the centre. Label every stock item with its B-number and original end A before cutting.

4. Make the listed end trims, then the sequential crosscuts. In cuts.csv, each kerf_start..kerf_end band is WASTE. Do not centre the blade on the finished-length boundary. Coordinates stay relative to the ORIGINAL stock datum A, even after squaring it. A saw cut means one complete crosscut through the section; it does not specify a particular saw or number of machine passes. Use a suitable saw, stable supports/clamps and appropriate dust/eye/hearing protection following the tool instructions.

5. Mark the resulting piece IDs on the timber and preserve the A end / TOP / OUTER orientation. Check finished lengths. Treat exposed cut ends with the compatible product and method specified for the timber.

6. Assemble course 1 on the prepared base. Clamp and verify square and level before fixing. Corner screws enter the OUTER side face of the full-through member and pass into the end of its adjoining member. They do not enter through the cut end of that full-through member.

7. Follow the per-course drawing; the corner pattern stays the same on every course. Position and clamp the next course, then use its own fixing sheet. Stack screws enter vertically through the TOP and into the previous course. The schedule offsets them to avoid modelled existing screws. Re-check that real timber, hardware heads and installation tolerances match the model before drilling or driving. Screw HEADS and bearing seats are NOT modelled: before stacking any course, confirm the head-seat detail for the actual hardware (a protruding head can stop the next sleeper sitting flat, and recessing a seat deepens the hole and moves the tip).

8. For every fixing use the confirmed pilot instruction for the actual screw and timber. UNCONFIRMED is a STOP, not permission to choose a bit. Hole coordinates are entry centres; pilot depth is measured from that entry face along the stated direction. Nominal screw penetration includes its point, so it is not the same as effective threaded embedment.

9. Install and inspect the separately reviewed supports, protection/liner and drainage details. Do not turn an open-bottom bed into an undrained tank. Then fill to the specified freeboard. Fill quantity is cavity geometry only, without compaction, settlement, existing soil or displaced supports.

10. Record actual purchases, labour, corrections and useful offcuts. Only AFTER completing the cut plan, merge the inventory proposal into the next job. Measure retained offcuts again; running a plan does not consume physical stock.


## Draft workshop advisory (not confirmed pilot evidence)

Use this only as trial planning context while pilot mode remains unconfirmed. It is not manufacturer approval and must not be copied into release evidence without a recorded source or physical trial for the exact screw/timber pair.

- Pilot-hole trial start points for 7 mm timber-drive screws: treated softwood receiving piece around 4.5-5.0 mm; denser/harder timber often larger (around 5.5-6.0 mm).

- For long screws (for example 250 mm), test deeper pilot depths to reduce drive torque and wandering, and stop if splitting, lift or burning appears.

- Near edges/ends: clamp, reduce drive speed, and favour piloting to reduce splitting risk.

- Sleeper planter practice: keep base level and drained, preserve open-bottom drainage path, treat cut ends, and use corrosion-resistant fixings suitable for treated timber.


## Bed schedule

| Bed | Outside L x W x H | Courses | Clear opening | Fill litres | Outside diagonal |

|---|---|---:|---|---:|---:|

| offer-bed-01 | 2400 x 1400 x 200 | 1 | 2200 x 1200 | 396.0 | 2778.5 |


## Purchase / cutting summary

4 purchased sleepers; 0 existing stock pieces used; 2 full crosscuts. Optimiser: **exact**. All explored cutting patterns and inventory states solved.

Finished timber: 7200 mm. Input stock: 8400 mm. Remaining offcuts: 1194 mm. Kerf + trim loss: 6 mm.

Offcuts are not all waste. No speculative offcut resale credit is used to reduce today's purchase cost.

Timber and screw purchases: **GBP 113.00**. Known subtotal: **GBP 113.00**.

Complete job cost: UNPRICED. Unpriced: consumables, fill, liner, preservative, site_preparation, supports, transport, labour.

Internal margin-based target: UNPRICED. Margin target is suppressed until all required costs are supplied. Zero is an explicit decision that an item is not needed/already allowed, not a missing price.


## Files

`plan.json` contains the full model and normalised inputs. `parts.csv` ties each member to its stock board. `cuts.csv` gives actual saw bands, including trim cuts. `stock.csv` lists every used stock item. `fixings.csv` gives local/global coordinates, receiver, direction, screw and pilot information. `shopping.csv` rounds purchases to whole screw packs. `model.scad` is an offline OpenSCAD model with optional exploded view. `drawings/` contains assembled, per-course, cutting and individual piece sheets. CSV money columns are integer pence.


The supplier and price snapshot are embedded in plan.json. Read docs/SOURCES.md and docs/ENGINEERING.md in the repository for evidence and model limits.
