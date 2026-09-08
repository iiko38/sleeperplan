# Changelog

## 2026-09-08 (v0.4.0) — IKEA-style assembly manual + animation upgrade

### Added
- **`assembly-manual.pdf`** (`sleeperplan/manual.py` + `pdf.py`): a numbered, one-action-per-page step guide compiled from the same operations as the web player:
  - 3D keyframe per panel: active part highlighted, installed parts solid, pending parts ghost outlines, orange marker on the active fixing's entry point.
  - Scaled joint cross-sections (`joint_closeup_scene`): entry face, mating plane, receiver continuation, penetration/depth datum; mark-ONLY, drill and seated-drive variants.
  - Equivalent fixings grouped with explicit repeat counts and mark-out sheet references (3-course guide: 43 panels).
  - Deterministic output (byte-identical regeneration, regression-tested).
- **Animation upgrades** (`site/app.js`): ghosted timber on close-up operations, drill-bit model at the entry axis during drill steps, persistent drilled holes that remain visible once made, deterministic per-step tooling state.
- **F10 fixes:** piece-sheet callouts now select one representative per operation type (corner + stack); vertical drilling directions draw the into-page symbol instead of a zero-length line.
- Hardware-agnostic wording throughout the manual ("the actual hardware"); Wickes remains a dated price snapshot only.

### Changed
- "OUTER outer face" wording fix in operation details; manual merges prepare+drive per fixing group.
- Version 0.4.0; 100 tests passing. Published/demo bundles regenerated (v04).

## 2026-09-08 (v0.3.0) — review-of-review hardening (REVIEW_37db13b)

### Added
- **Operations model** (`sleeperplan/operations.py`): every export now compiles a deterministic, ordered workshop operation schedule (`operations.json`, schema `sleeperplan.operations.v1`) — receive/label/cut/treat per board, place/clamp per course, then mark (STOP) or drill + drive per fixing, then supports/final checks. Dependencies are explicit; unknown pilot specs surface as STOP operations, never invented instructions.
- **Assembly player** on the customer site: play/pause/step/scrub through the compiled operations; pieces appear when placed, screws animate insertion with `head(u) = E - d*(L+g)*(1-u)` so the final frame equals the approved model exactly; per-step camera hints; active pieces highlighted.
- **Status & blockers panel** on the site showing the loaded plan's real status, hashes and unresolved blockers (F14).
- Evidence-kind field (`pilot_evidence_kind`: `fixture` | `manufacturer_instruction` | `recorded_trial`, required for pilot/none modes). **Fixture evidence can never issue a workshop plan**, even with a matching approval hash (F04).
- Publication gate tests: the public tree (`published/`, `site/demo`) must contain no `REVIEWED_WORKSHOP_PLAN`, every published manifest must match its plan hash, and published bundles must ship the operations schedule (F01).

### Changed
- **Screw selection is now price-independent** (`length, diameter, id`): repricing can no longer swap installed hardware under an unchanged approval (F02). Regression test with competing same-length screws.
- **Physical-design hash tightened:** excludes commercial rules (spares %, price-age days), includes generator version (F02b).
- **Single readiness calculation:** a missing approval hash now blocks draft/check (`release_ready=false`) the same as release — no more "draft looks clear, release fails" divergence (F05).
- **Public tree quarantine:** stale `build/*` packs removed from the repo and `build/` re-ignored; only the current v0.3.0 options pack is tracked under `published/` with identity checks. `tools/viewer.py` defaults to the published pack and now HTML-escapes plan values (F01/F14).
- **Viewer fixes:** DPR-correct resize tracking (no more per-frame resize at high DPI, F11); per-bed display groups so batch jobs render side by side without altering manufacturing coordinates (F12); recursive geometry disposal on offer switch (F14).
- **Print sizing:** parts board paginates with table-only continuation pages (readable ~11pt rows); stock-arrival board paginated at 8 boards/page (~9.6pt); options PDF now includes stock pages.

### Notes
- F03 (modelled head seats/joint recipes) and the full keyed drilling-recipe work remain gated on the physical trial; the operations model already carries the STOP semantics until then.
- Version 0.3.0: physical-design hashes changed (generator version now included); demo fixture approval hash re-embedded. 99 tests passing.

## 2026-09-08 (v0.2.0) — engineering review fixes

### Added
- **Physical-design approval binding (release gate):** plans now carry `physical_design_hash` (SHA-256 over profile/beds/orientation/stock lengths+trims/screw specs/geometric rules; excludes prices, packs, availability, provenance text, review block and as-of date). `--release` requires `review.approved_physical_design_hash` to match: mismatch blocks (`stale_approval`), missing hash blocks (`approval_hash_required`). Price-only revisions keep a physical approval; dimension/hardware/machining changes invalidate it.
- **Head-seat honesty:** explicit non-blocking `head_seat_unmodeled` issue on every multi-course bed (screw heads, bearing seats, recesses and driver access are not modelled), plus BUILD.md step 7 text and an ENGINEERING.md section.
- CLI summary and BUILD.md header now print the physical design hash for copy-into-job workflow.
- Regression tests: approval binding (missing/stale/machining-change/price-only), hash format validation, head-seat presence, demo-fixture markers. Suite: 91 tests.

### Changed
- `examples/reviewed-example.json` and `catalogues/wickes-reviewed-2026-09-06.json` are now explicitly marked **DEMONSTRATION ONLY** (reviewer "DEMO FIXTURE", placeholder pilot-evidence strings). Their previous text could be mistaken for real workshop evidence; no real timber was ever cut or drilled for this repo.
- Version bump to 0.2.0 (results-affecting change per AGENTS.md invariant 12).

### Fixed (drawing/PDF)
- Piece-sheet zoom callouts no longer overlap the member views (views narrowed to reserved callout column).
- Parts/fixings board paginates in PDFs (18 rows/page) instead of shrinking to fit one page; applies to workshop.pdf and options-and-build.pdf.

## 2026-09-08

### Added
- Combined height-options PDF: `compare --pdf` now also writes `options-and-build.pdf`, one document covering every requested height (1/2/3 courses) with:
  - Options overview table (courses, outside size, pieces, fixings, sleepers, saw cuts, timber + screws cost).
  - Same-scale comparison drawing page.
  - Per-option section: build sequence, corner-pattern instruction, assembled view, one plan page per course, cutting diagrams, process and parts boards.
  - Pointer to each option's full `workshop.pdf` / `cuts.csv` / `fixings.csv`.
- Regression test for deterministic options-PDF generation (`test_options_pdf_covers_each_height`).
- Generated pack `build/first-model-2400x1400-options-1-2-3/` for the 2400 x 1400 example across 1, 2 and 3 courses.

### Fixed
- "1 courses" pluralisation on height-comparison drawings.

## 2026-09-07

### Added
- Static customer visualiser under `site/` for 1/2/3 course offer presentation.
- Interactive browser 3D controls (orbit/pan/zoom) with Z-up orientation.
- Clear per-piece black edge lines in the viewer to make course splits visible.
- Exported `web-manifest.json` for static-web artifact discovery and viewer camera defaults.
- Exported `quality-report.json` for deterministic export integrity checks.
- Client-facing panel content: option summary, process flow, and links to assembled/process/manual/PDF artifacts.

### Changed
- Reworked the site UI into a modern visual layout focused on client presentation rather than internal pack details.
- Updated repository docs to reflect static web scope and deployment status.

### Fixed
- Browser import resolution failure (`Failed to resolve module specifier "three"`) by switching to local vendor module imports.
- Viewer axis alignment to model coordinates (forced Z-up camera/object orientation).

### Deployment
- Vercel production alias verified: `https://site-rho-six-fdck1jw7c6.vercel.app`

### Notes
- Engineering/release safety gates are unchanged: draft plans remain draft until physical review and confirmed pilot evidence are recorded.
