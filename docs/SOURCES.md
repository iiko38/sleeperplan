# Source register

Checked on **6 September 2026**. These are manual public-page snapshots, not scraped/live integrations. Prices are as displayed and exclude delivery. Recheck prices, product suitability and branch stock before buying. The repository does not copy product imagery or manufacturers' documents.

## Timber catalogue

**Wickes SKU 276785** — UC4 incised light green garden sleeper, nominal 100 x 200 x 2400 mm. Displayed promotional price GBP 28 (previous price shown GBP 33). Product page lists 38.40 kg, approximate sizes, ground-contact treatment and treatment of cut ends. The orientation in Sleeperplan is an explicit job setting; it is not inferred from Wickes' “height/thickness” field names.

https://www.wickes.co.uk/Wickes-UC4-Incised-Light-Green-Garden-Sleeper---100-x-200-x-2400mm/p/276785

**Wickes SKU 256948** — matching nominal 100 x 200 x 1800 mm sleeper. Displayed promotional price GBP 24 (previous price shown GBP 29). No weight is populated in our snapshot, so the software will not invent a complete collection weight for an order containing it.

https://www.wickes.co.uk/Wickes-UC4-Incised-Light-Green-Garden-Sleeper---100-x-200-x-1800mm/p/256948

## Candidate fasteners

**Wickes SKU 287686** — Timber Drive washer-head screw, 7 x 150 mm, pack of 25, GBP 9. The page describes Torx drive, exterior use and a weather-resistant coating for treated timber.

https://www.wickes.co.uk/Wickes-Timber-Drive-Washer-Head-Screws---7-x-150mm---Pack-of-25/p/287686

**Wickes SKU 287688** — matching 7 x 250 mm screws, pack of 25, GBP 12.30.

https://www.wickes.co.uk/Wickes-Timber-Drive-Washer-Head-Screws---7-x-250mm---Pack-of-25/p/287688

**Wickes search API cross-check (same product family):** `/search/suggestProductsSecure` returns the four 7 mm Timber Drive washer-head sizes as one range (`287685`, `287686`, `287687`, `287688`) with product-page links and image IDs `GPID_5000106026`..`GPID_5000106029`. Product pages expose manufacturer model numbers `NEW_45`..`NEW_48` for these four sizes.

https://www.wickes.co.uk/search/suggestProductsSecure?term=timber%20drive%20washer%20head%20screws

**Limitation:** these pages establish the listed products and prices, not the structural adequacy of this proposed bed connection, an exact pilot-hole specification or effective embedment. The catalogue leaves pilot mode unconfirmed. None of the numerical placement/clearance defaults is claimed to be a Wickes-approved engineering schedule.

## General construction context

**Wickes — How to build a raised sleeper bed.** General sequence and fixing guidance; describes two screws at a butt joint and support options. This does not certify our generated design.

https://www.wickes.co.uk/ideas-advice/raised-sleeper-bed

**Wickes — How to build and lay garden sleepers.** General cutting/joining guidance, including pilot holes and different fixing considerations for softwood/hardwood. It does not supply a verified bit diameter for the selected screw SKU.

https://www.wickes.co.uk/ideas-advice/sleeper-techniques

Additional extracted points from the same Wickes guidance snapshot:

- Softwood sleepers: piloting is described as "not always necessary" and dependent on tooling.
- Hardwood sleepers: pilot each fixing hole and use stainless screws (to reduce tannin-corrosion risk).
- Fixing length rule-of-thumb: screw length about one-third longer than timber depth.
- One Wickes sentence says to use a pilot bit matching screw diameter and length; this is recorded as source text only, not accepted as a validated sleeper-joint specification for this repo.

**Royal Horticultural Society — How to make a raised bed.** General raised-bed material, drainage and planting considerations. Hard-surface beds need different drainage detail; v1 keeps that outside its reviewed construction scope.

https://www.rhs.org.uk/garden-features/how-to-make-a-raised-bed

**Wickes — How to build a raised sleeper bed.** Reinforces overlap-and-screw approach and repeats hardwood-specific pilot-hole requirement in narrative guidance, but again provides no product-specific pilot diameter/depth values for Wickes screw SKUs.

https://www.wickes.co.uk/ideas-advice/raised-sleeper-bed

**FastenMaster TimberLOK product page (US).** States "No Pre-Drilling Required" for that structural screw line. This is useful as comparative context only; it is not a Wickes 287686/287688 instruction and should not be copied directly into UK sleeper plans.

https://www.fastenmaster.com/products/timberlok

**DIYdata wood screw pilot table (general carpentry reference).** Gives generic clearance/pilot tables by gauge and timber hardness (for example, larger pilot in hardwood than softwood). Useful for broad sanity checking only; not a manufacturer instruction for the selected Wickes timber-drive products.

https://www.diydata.com/carpentry/screw-holes/wood-screw-holes.php

## Manual structure references

**IKEA UK assembly-guides support page.** Used as a structure cue for manual flow (clear "find docs", ordered steps, and visual-first guidance style), not as technical authority for sleeper construction.

https://www.ikea.com/gb/en/customer-service/product-support/assembly-guides/

**IKEA product page document layout example (PAX frame).** Used as a formatting cue for grouping "Assembly and documents", "Good to know", and "Safety and compliance" sections.

https://www.ikea.com/gb/en/p/pax-wardrobe-frame-white-20214571/

## Branch clarification

The user's supplier description was Wickes in Clapham, West Sussex. The exact intended branch was not established. The official Wickes Worthing page lists **114 Dominion Road, Worthing, West Sussex, BN14 8JP**. That is a verified store listing, not confirmation that it is the branch intended, the nearest branch to the job or that any product is locally available.

https://www.wickes.co.uk/store/8221

## Evidence versus assumptions

Source-backed values: dated product dimensions, identifiers and displayed prices; the noted product weight; general supplier/RHS guidance.

Source-backed guidance now also includes: softwood-vs-hardwood pilot treatment from Wickes article guidance, and comparative manufacturer/reference context showing that predrill policy is product-family specific.

Software-derived values: lengths, ring geometry, saw coordinates, board allocation, part IDs, fixing path intersections, volumes and arithmetic totals.

Human/shop assumptions requiring review: actual measurements, kerf, end condition, fixing layout and suitability, exact pilot diameter/depth for Wickes 287686/287688 in this build, support/foundation design, drainage, stock availability, transport, labour and extra materials.

## Pilot-hole status for this repo

Current external research is still insufficient to claim a manufacturer-verified pilot diameter/depth for the specific Wickes screw SKUs used in this project (`287686`, `287688`) in 100 x 200 mm treated sleeper joints. Therefore, default catalogues remain `pilot_mode: "unconfirmed"` unless a documented physical trial or primary manufacturer instruction is recorded for the exact use case.

Additional negative evidence checks were run against likely Wickes media-document patterns for the Timber Drive range (`GPID_5000106026`..`GPID_5000106029`, `NEW_45`..`NEW_48`, and variants such as `_TECH_0`, `_INST_0`), and returned not found responses in this snapshot. This strengthens the decision to keep pilot mode unconfirmed by default.

Direct product API probes that might expose structured technical attachments (`/rest/v2/wickes/products/<sku>?fields=FULL`) returned access denied responses for these SKUs in this environment, so they did not provide usable pilot-hole data.
