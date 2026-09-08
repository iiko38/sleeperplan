# Sleeperplan — code review and assembly-instructions plan

**Repository:** `iiko38/sleeperplan`  
**Reviewed commit:** `37db13b378fc868f2d4e6b73f8ba19f6e5f4b526`  
**Review date:** 8 September 2026  
**Goal:** exact cuts, explicit drilling operations, visible screw insertion, and an IKEA-like colour manual generated from the same build model.

## Verdict

Keep the deterministic planner. It is a useful geometry, cutting and costing foundation. Do not treat the current outputs as a complete, drill-ready kit specification or an assembly animation.

The essential missing layer is an **ordered, validated list of workshop operations**. The repo knows where the timber and screws end up; it does not yet describe every action that gets them there. That list should drive both the PDF and the player. Adding a prettier picture or another separately written instruction template will not close the gap.

## Scope and verification

Read the handwritten planning/configuration, geometry/cutting/costing interfaces, CLI, export and PDF code, relevant drawing functions, both viewer implementations, all four test modules, catalogue/example changes, and selected generated packs at the pinned commit. Unchanged core modules were also cross-checked by their Git blob identities against the previously inspected source. This was not an audit of every line of vendored Three.js or every duplicated generated file.

GitHub Actions run `34240224252` is successful. Its four core jobs cover Windows and Ubuntu on Python 3.11 and 3.13; the separate PDF job also passed. The PDF-job log reports **91 tests, OK**, followed by a successful PDF smoke export. These are GitHub's executions, not a locally rerun full suite.

A local checkout could not be obtained because outbound GitHub access from the execution environment failed. Repository reads succeeded through the GitHub connection. The supplied `probes/review_probes.py` was executed locally: it copies the relevant selection/hash functions into small synthetic fixtures and reproduces renderer arithmetic. It does **not** execute the full application or a live browser. Fresh PDFs from this commit were not visually rendered in this review; print-size findings below are calculated from the renderer source, not claimed screenshot observations. No physical construction or connection testing took place. No repository files were changed.

## Improvements since the earlier review

- `planner.py` now exposes a physical-design hash and refuses an explicitly mismatched approval. `config.py` validates the hash format; CLI/build notes surface the hash.
- The source reviewed catalogue and example now identify their evidence as demonstrations instead of claiming a real workshop trial.
- `piece_scene` reserves a separate right-hand area for callout circles rather than laying those circles directly over the timber view.
- PDF parts boards can be split into 18-row pages. This is a useful start, although physical printed font sizes remain too small.
- CI for this commit is green. Do not carry forward the old failed-CI finding.

---

# Findings

Priorities here mean: **P1 — fix before issuing workshop/customer kit instructions; P2 — correctness or usability work required for the stated product; P3 — secondary hardening.** A missing product capability is identified as such, rather than presented as a newly introduced regression.

## F01 / P1 — old public output still claims reviewed status

**Locations:** `build/reviewed/BUILD.md`; new tracked `build/` outputs; `tools/viewer.py` default target.

The source catalogue now calls its pilot values demonstration placeholders, but `build/reviewed/BUILD.md` still opens with `REVIEWED_WORKSHOP_PLAN`, has no physical-design hash, and presents complete job costs. It is an older output that did not acquire the new warnings and approval logic. The legacy viewer defaults to `build/reviewed`, which increases the chance of opening it.

**Why it matters:** editing input evidence does not revoke already exported instructions. Making old outputs public can distribute the very unsupported approval that the new code attempts to correct.

**Change:** remove or clearly quarantine obsolete packs from the publishable tree; keep a small, explicit set of current draft examples. Restore a default ignore for working build directories and publish allowlisted, generated artefacts separately. Give published bundles a manifest containing source commit, generator version, resolved build hash, status and file checksums. A publication check must reject demonstration evidence paired with a reviewed/customer-issued status.

**Acceptance:** scanning the public example/export tree finds no demo-based `REVIEWED_WORKSHOP_PLAN`; published instructions can be traced to their exact source and evidence.

## F02 / P1 — price changes can change hardware without changing approval

**Locations:** `planner.py::physical_design`, `physical_design_hash`; `geometry.py::select_screw`; `tests/test_config_costs.py::test_price_only_change_keeps_physical_approval`.

`physical_design` hashes the candidate screw catalogue without pack prices or pack sizes. `select_screw` chooses the shortest fitting screw, then uses **price per screw** to break ties. Two same-length products with different diameters or pilot requirements can therefore switch places after repricing while the approved hash stays unchanged.

**Executed focused reproduction:** synthetic product A is 150 mm long, 7 mm diameter and initially cheaper than product B, which is 150 mm long and 9 mm diameter. Increasing only A's pack price changes selection to B. The physical-design hashes remain identical. This is a catalogue-extension defect; it does not claim the shipped two-length catalogue already makes that substitution.

The existing price-only test increases timber prices but does not exercise competing screw products.

**Change:** pin a screw/recipe selection in the approved build, or hash the resolved physical output, including selected fastener IDs, dimensions, machining recipes and relevant generator/recipe revision. Keep quote prices outside that record. If repricing really changes hardware or manufacturing instructions, it is not a price-only revision and must require renewed approval.

**Acceptance:** repricing cannot change any installed screw, machining operation or approved connection while leaving approval valid.

**Related lower-priority issue:** the hash includes all `Rules`, including spare percentage and price-age settings. A spare-percentage-only change invalidates the hash even though selected hardware is unchanged; the probe reproduces this too. Conversely, the hash does not include the physical generator version or resolved geometry, so changes in physical algorithms need an explicit version/hash policy.

## F03 / P1 — head-seat handling is warned about, not specified or enforced

**Locations:** `model.py::Screw`, `Fixing`; `geometry.py::make_fixing`; `planner.py::plan` (`head_seat_unmodeled`); viewer screw construction.

The hardware model still lacks head type, head dimensions, bearing-seat location, recess geometry, driver envelope and effective threaded engagement. The new head-seat message is explicitly non-blocking. A release can therefore succeed without a modelled or linked issued detail for an interface where the next course must sit over screw heads.

A note is an improvement in disclosure, not a physical solution. The exact default screw's seating behaviour must be confirmed rather than assumed to protrude or assumed to bury cleanly. Where a recess changes the bearing seat, the resulting shaft, tip and available timber geometry must be recalculated.

**Change:** add an approved joint/machining recipe and require it for affected interfaces. Either model the seating detail or make an explicitly reviewed, versioned supplementary detail a required part of the issued pack. The animation must show that same detail; it must not hide a protruding head merely to make the next course appear flush.

**Acceptance:** no issued sequence can place the next member over unresolved head geometry. Changes to the seat update penetration, collisions, machining depths and the approved build hash.

## F04 / P1 — demonstration evidence is text, not an enforced evidence type

**Locations:** `config.py::parse_screw`; `catalogues/wickes-reviewed-2026-09-06.json`; `planner.py::plan`; demo test in `tests/test_config_costs.py`.

For `pilot` or `none`, `parse_screw` requires a non-empty evidence string. The explicit text `DEMONSTRATION PLACEHOLDER - NOT REAL EVIDENCE` meets that requirement. The release checks do not distinguish a fixture from a manufacturer instruction or a recorded trial. The new test verifies the presence of warning words, not that demonstration data cannot produce an issued status once a matching approval hash is supplied.

**Change:** model evidence kind and provenance separately, for example `fixture`, `manufacturer_instruction`, `recorded_trial`, with the applicable hardware/joint/material, record ID and reviewer where relevant. Normal release must refuse fixtures. Fixture-only testing should not generate a real-looking issued status or publishable customer pack. This does not mean software can independently certify the truth of a human's trial; it means it can reject known test data.

**Acceptance:** the distributed demonstration catalogue cannot issue a real workshop plan, even with a correct copied hash.

## F05 / P2 — check and release disagree about missing approval

**Locations:** `planner.py::plan` (`elif approval is None and release`); `cli.py::main`.

A missing approval hash becomes a blocker only when `release=True`. With the other fields populated, a normal draft/check run can report `review_gate_clear=True` and exit 0, while release of the same job fails for the missing hash.

**Change:** calculate one full release-readiness result in all modes. Drafting may still export a valid draft, but it must report the same outstanding blockers. Release should decide whether those blockers prevent output, not whether they exist.

**Acceptance:** absent approval produces `release_ready=False` in a draft, a non-clear check result, and release refusal. Preserve a separate geometry-valid status for useful draft work.

## F06 / P1 product gap — neither viewer implements the requested assembly process

**Locations:** `site/app.js::buildSceneFromPlan`, `renderFrame`; `tools/viewer.py::generate_viewer_html`; `model.py`.

The main site places every timber solid and screw cylinder in its final position. Its animation frame loop updates camera controls and redraws the scene; it does not advance a construction timeline. Cylinders have no screw heads or drill features. Since their shafts are inside opaque timber, much of the fixing information is hidden.

The legacy viewer offers a useful course-explode slider and screw lines. That is a different, partly duplicated viewer, not a drill/cut/drive sequence. It drops receiver, pilot and detailed hardware information when converting CSV rows into its embedded scene data.

Missing capabilities include raw-stock cut stages, preconditions, drill approach and withdrawal, persistent holes, screw approach/insertion, clamping, tool changes, step selection, scrubbing and deliberate close-up cameras.

**Change:** keep the Three.js viewer and introduce a deterministic operation model. Drive the player and PDF steps from it. Use transparent or sectioned receiving timber for a drilling close-up and restore ordinary timber for the assembled view. Preserve IDs on scene objects so the active step can select the actual part and fixing.

**Acceptance:** one real modelled fixing can be followed from labelled stock to prepared joint, verified drilling operation, insertion and seated screw; then the same mechanism handles every fixing in every configured height.

## F07 / P2 — instruction order is duplicated and already inconsistent

**Locations:** `drawing.py::process_scene`; `export.py::build_notes`, `manual_notes`; `pdf.py::write_options_pdf`; `site/index.html`.

The process drawing says “Drill and drive” at step 5, then “Assemble course-by-course” at step 6. Other instructions say to assemble/clamp a course before fixing. Pre-drilling individual parts can be valid; driving into an absent receiver is not. The current prose does not encode that distinction.

Multiple templates separately write their own process. They will drift further when head preparation, supports or product-specific drilling is added. Some generic 7 mm pilot advisory text is emitted for all jobs, even though the catalogue accepts other diameters. It is labelled trial context, but should not appear as a generic fallback near an exact drilling schedule.

**Change:** generate descriptions and step numbering from typed operations and dependencies. Treat through-member preparation, receiver drilling and joint driving as distinct operations where the approved recipe requires them. Remove uncited, product-agnostic pilot-number suggestions from issued instructions.

**Acceptance:** every drive operation depends on the required members being placed and clamped and on all required preparation being complete. All output formats show the same ordering and requirements.

## F08 / P2 — one pilot setting per SKU cannot describe every joint

**Locations:** `model.py::Screw`; `geometry.py::make_fixing`; `drawing.py::fastener_scene`.

A catalogue screw has only a single pilot diameter and depth, copied to every fixing. This cannot express a different through-member bore, receiver pilot, approved head recess or operation-specific depth reference. The same screw could be used in multiple connection geometries.

`fastener_scene` groups solely by screw ID and takes its first fixing's through thickness and penetration as the representative section. That is only valid when all uses of the SKU share those properties. For a supported catalogue/profile extension where the same length serves different joint geometries, the diagram can describe one use as if it represents all uses.

**Change:** separate product properties from `JointRecipe` and per-fixing `MachiningOperation`. Group explanatory cards by recipe/geometry, not only screw SKU. Dimensions should identify whether depth is measured from the untouched outer face, approved seat or receiver face. Do not infer pilot diameter from nominal screw diameter.

**Acceptance:** one SKU used in two different valid recipes produces two correct preparation descriptions and sections, rather than inheriting the first one's values.

## F09 / P2 — parts pagination still produces tiny printed labels

**Locations:** `drawing.py::parts_scene`, `stock_scene`; `pdf.py::SceneFlow` in both PDF writers; `export.py::_populate`.

The renderer scales the whole vector scene to at most 770 × 525 points. With two fastener types (one row of fastener cards), a 12-part board has scene height 960 and its nominal 12-unit labels print at about **6.56 pt**. An 18-part page is 1140 units high and those labels print at about **5.53 pt**. These values were reproduced from the source arithmetic.

The stock-arrival board remains unpaginated. At 20 boards its 14-unit labels print at about **4.45 pt**. The separate SVG parts export still calls the unpaginated variant. Text widths are not measured before insertion into fixed columns.

**Change:** design in final page units, impose a minimum physical text size, and paginate by available page area. Separate the tool/hardware overview from repeated part tables so every continuation page does not carry a large header. Apply equivalent pagination rules to all intended printable formats.

**Acceptance:** workshop-critical text remains at an agreed minimum print size (recommend 9–10 pt minimum, larger for action instructions); no table/label overlap for maximum-length IDs and representative maximum-size batches. Do not pass the test simply by shrinking a complete scene.

## F10 / P2 — fixing callouts do not explain vertical drilling

**Locations:** `drawing.py::piece_scene`, `fastener_scene`.

Zoom callouts still select only the first three fixings, prioritising corners. A mixed corner/stack piece can therefore use all three bubbles on corners, leaving no stack example. In a stack-only example, the direction graphic reads `dx, dy, _`; a vertical direction `(0, 0, -1)` becomes a zero-length line in that calculation. The circular mark remains, but there is no explanatory view of the drilling direction/depth.

The current fastener section draws receiving material only for the nominal penetration distance. It should distinguish penetration depth from total receiving-member size so the illustration does not imply that the tip is at a real free edge.

**Change:** choose representative callouts per operation/recipe and draw a genuine local section or an explicit into-page symbol as appropriate. Show the bit, head seat, mating plane, receiver continuation and depth datum. Use a separate magnified instructional view rather than treating a larger dot as a drilled-hole explanation.

**Acceptance:** every distinct preparation/drive operation used in the plan has a readable detail, with a non-ambiguous direction and depth reference.

## F11 / P2 — high-DPI resize condition does not converge

**Location:** `site/app.js::renderFrame`.

After `setPixelRatio`, `canvas.width` and `canvas.height` are backing-buffer pixels, while `clientWidth` and `clientHeight` are CSS pixels. The frame loop compares these directly, so at DPR 2 it can call `setSize` and update the projection every frame despite no layout change. The supplied arithmetic probe reproduces 60 resize requests over 60 static frames. This is not a measured FPS or battery benchmark.

**Change:** track CSS dimensions and DPR separately, or use a resize observer and update only when either changes. Guard zero dimensions. Once a step player exists, stop continuous rendering while idle unless camera damping or an active animation requires it.

**Acceptance:** a static DPR-2 view does not repeatedly resize its drawing buffer; resizing/orientation changes still update the projection correctly.

## F12 / P2 — batch beds overlap in the main viewer

**Locations:** `site/app.js::buildSceneFromPlan`, `populateClientPanel`; `geometry.py::compile_geometry`; contrast `drawing.py::scad_model`.

The engine deliberately uses a separate local origin per bed. The main viewer adds every piece at its local coordinates in one scene without a per-bed display transform. Batch beds therefore overlap. Its metrics show `beds[0]` dimensions but a job-level cost. The supplied offer views contain one bed, so this is a supported-input extension problem, not a claim that the present offer demo contains overlapping beds.

OpenSCAD already applies per-bed display offsets, illustrating the missing adaptation in the web viewer.

**Change:** add explicit per-bed display groups/transforms, or restrict the viewer to one selected bed and clearly identify job totals separately. Display transforms must not alter manufacturing coordinates.

**Acceptance:** a three-bed fixture shows distinct beds and correctly scoped dimensions, counts and costs.

## F13 / P2 — the quality report is an inventory check, not visual validation

**Locations:** `export.py::_quality_report`; `tests/test_cli_exports.py`.

The report checks heading presence, expected drawing counts and callouts inferred from the fixing data. It does not inspect the rendered output. The PDF tests check a PDF header and repeatable bytes; the test named `test_options_pdf_covers_each_height` does not actually inspect per-height content.

**Change:** keep deterministic-output tests, but name them accurately and add semantic/visual checks: required operation coverage, correct labels and counts, minimum printed font size, no clipping, no overlaps, expected per-height sections and consistent build identities. Add browser tests for viewer controls and final animation transforms.

**Acceptance:** removing a drilling step, making a label unreadably small or mixing a manifest with the wrong plan causes a test failure.

## F14 / P3 — secondary viewer and export hardening

**Locations:** `site/app.js::clearGroup`, `loadManifestFromUrl`; `tools/viewer.py::generate_viewer_html`; comparison PDF overview.

- `clearGroup` disposes only immediate geometries. Timber meshes contain nested `EdgesGeometry` objects that are not explicitly disposed when offers are switched. Remove objects using the scene API and recursively dispose owned geometries; keep shared materials alive until application teardown.
- The main viewer does not validate the manifest schema or compare its plan hash to the loaded plan. A generic draft footnote exists in the HTML, but the panel does not expose the plan's actual unresolved blockers. Keep that footnote, add explicit status/blockers, and reject mismatched bundles.
- The legacy HTML generator interpolates the configurable plan title without HTML escaping. Treat incoming job/CSV values as untrusted in a public workflow; escape HTML and make embedded JSON safe for script contexts. This is a conditional injection exposure, not a finding that the current title contains malicious content.
- The combined options PDF mixes first-bed dimensions with whole-job counts/costs for multi-bed inputs. Make batch versus per-bed scope explicit.
- Two independent viewers and several prose-generating functions multiply maintenance work. Consolidate around one plan adapter and operation model rather than expanding both implementations.

---

# Recommended implementation

## 1. Keep the physical planner, add operations

Use a small typed model, not a new general-purpose framework. Suggested ownership:

| Module | Responsibility |
|---|---|
| `model.py` | Product, piece, joint, evidence and operation records |
| `machining.py` | Approved preparation/seat/receiver operations per joint |
| `assembly.py` | Ordered operations, dependencies and step grouping |
| `validation.py` or a small extension of `planner.py` | One readiness result and resolved build identity |
| `drawing.py` | Technical diagrams and instructional keyframes |
| `pdf.py` | Fixed-size page layout over the shared operations |
| `site/assembly-player.js` | Deterministic play/pause/step/scrub state |
| `site/scene-adapter.js` | Piece/fixing/tool objects and display-only transforms |

Do not split tiny concerns into dozens of services. These can begin as a few dataclasses and pure functions.

A useful operation has: unique ID; action type; stock, part and fixing IDs; dependency IDs; entry face and coordinate reference; axis; confirmed diameter/depth/seat parameters where applicable; tool/recipe/evidence IDs; before/after state; close-up camera hint; and a short instruction key. Unknown physical values remain unknown and block issued machining instructions.

Core actions include receive/inspect, label, cut, treat cut end, place, clamp, square/level check, drill, prepare seat, drive, inspect seat, add reviewed supports, and final check. Not every recipe requires every drilling operation.

## 2. First working sequence

Build one source-driven sequence for the current 2400 × 1400 long-through draft:

1. Select the one-, two- or three-course variant and show its scope/status.
2. Show each original stock board, labelled datum and required finished piece.
3. Show each cutting band's actual start/end, with keep/waste sides clearly identified.
4. Label the finished member and treat the cut end under the applicable instruction.
5. Place and clamp the first corner's two actual members.
6. Mark the exact centre, then display the recipe's preparation operations in order.
7. Show the screw outside the timber, aligned with the approved axis, then inserting and seating.
8. Repeat through all other required fixings, with a per-step count and the active fixing ID.
9. Add further courses only after the preceding interfaces are ready, using their own staggered coordinates.
10. Show the approved restraint/drainage detail before an issued pack depicts final filling.

The current first-model file is a draft, not a surveyed neighbour design. Its long-through variant and the older alternating-corner neighbour example must have separate expected counts and layouts; do not conflate their 56- and 52-fixing three-course patterns.

## 3. Deterministic animation

Each displayed state should be a pure function of **plan + operation ID + progress**. Seeking backwards or taking a PDF keyframe must produce the same geometry without depending on how many animation frames have previously run.

For a screw with known under-bearing length `L`, insertion direction `d`, final approved bearing point `E` and approach gap `g`, a simple insertion phase can place the head at:

`head(u) = E - d * (L + g) * (1 - u)`, for `0 <= u <= 1`.

The tip is `head(u) + d * L`; the shaft centre is `head(u) + d * L/2`. At the final frame this must agree with the approved geometric model. If `E` is a recessed bearing point, it must be derived from the actual approved preparation, not substituted to hide a seating problem. Product length conventions need to be explicit.

Pilot progress uses its approved drill depth, not the screw length. Provide local section/ghost timber when necessary to show what is happening. Thread rotation is illustrative unless genuine pitch/turn data is available; do not present an arbitrary spin as a validated installation setting.

No generative imagery is needed for dimensioned construction geometry. Use rendered or vector keyframes from the model. A PDF can use clean vector diagrams while the browser uses 3D meshes, provided both consume the same operation data and assertions.

## 4. Manual layout

Split the customer-friendly assembly guide from the dense workshop schedule, but bind both to the same revision. The visual guide should show one action per panel: active part/tool in colour, already-installed parts subdued, clear arrows, a small orientation thumbnail and a short sentence. Show where to clamp, the correct entry face, the depth datum, waste side and completion check.

Use a dedicated joint close-up rather than a whole-bed image to explain drilling. A magnified section should show the mating plane, preparation bore(s), head seat and tip within the full receiver. A repeated-operation count is useful only when the actual locations and details are equivalent; provide a location map for the other instances. Keep IDs and labels consistent with the physical kit.

Critical measurements belong on the relevant panel, not only in a distant CSV. Do not print a pseudo-1:1 jig without a verified physical scale and calibration marks. Do not silently round away a distinction needed by the approved machining tolerance.

## 5. Acceptance tests before calling it ready

- Repricing cannot silently select new hardware under an old approval.
- Fixtures and missing head/recipe details cannot produce an issued status.
- Draft/check/release share one complete readiness calculation.
- Every fixing has exactly one drive operation; required drill/seat tasks precede it.
- No drive occurs before the named through and receiving members are positioned and clamped.
- Final player positions agree with the plan's approved shaft/head/tip coordinates.
- Drilling uses its own diameter, depth and datum, including changes between recipes.
- All cuts conserve stock, kerf, trim and offcuts; visual blade bands use the same coordinates as the cutting list.
- One-, two- and three-course long-through and alternating variants are tested separately.
- Manifest, plan, CSVs, PDFs and animation share a validated resolved build identity.
- Printable pages pass minimum-font, clipping, overlap and required-content checks.
- High-DPI resizing converges; switching offers disposes old owned geometry.
- Batch views separate bed-local frames without altering manufacturing coordinates.
- Every issued support/head detail is included or explicitly linked and revision-controlled; unresolved detail is not replaced by a reassuring picture.

## Suggested order

**First:** quarantine stale approved outputs and repair evidence/hash/readiness handling.  
**Second:** specify one complete joint recipe with the actual hardware and timber; model head seating and tool preparation.  
**Third:** compile and animate one truthful corner sequence, including drilling and screw insertion.  
**Fourth:** extend to the whole bed and all heights; drive manual pages from the same operations.  
**Fifth:** add browser and print-layout acceptance tests, then publish a controlled draft/customer bundle.

The next milestone is not a nicer full-bed render. It is **one correct corner, explained completely**, whose data can scale to every corner, stack fixing, cut and manual page.

---

# Sources

All paths below are pinned to the reviewed commit; repository source is the primary evidence.

- Repository: https://github.com/iiko38/sleeperplan/tree/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526
- CI run: https://github.com/iiko38/sleeperplan/actions/runs/34240224252
- PDF CI job: https://github.com/iiko38/sleeperplan/actions/runs/34240224252/job/102108179881
- Planner/hash/gates: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/planner.py
- Configuration/evidence: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/config.py
- Domain records: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/model.py
- Geometry/selection: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/geometry.py
- Cutting: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/cutting.py
- Export/quality: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/export.py
- Drawing: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/drawing.py
- PDF: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/pdf.py
- CLI: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/sleeperplan/cli.py
- Main viewer: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/site/app.js
- Main page: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/site/index.html
- Legacy viewer: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/tools/viewer.py
- Source demonstration catalogue: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/catalogues/wickes-reviewed-2026-09-06.json
- Stale reviewed output: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/build/reviewed/BUILD.md
- Current offer example: https://github.com/iiko38/sleeperplan/blob/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/examples/first-model-2400x1400.json
- Tests: https://github.com/iiko38/sleeperplan/tree/37db13b378fc868f2d4e6b73f8ba19f6e5f4b526/tests

All implementation proposals and acceptance thresholds in this review are recommendations, not claims that the current code already implements them or that a physical kit is certified.
