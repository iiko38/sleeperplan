# Sleeperplan Backlog & Roadmap

A deterministic, offline workshop tool for repeatable timber sleeper flower beds.

## Current Milestone: MVP Complete & Hardened (v0.1.0)
- [x] Deterministic 3D solids coordinate model with alternating corner joinery.
- [x] Exact DP cutting stock solver with bounded heuristic fallback.
- [x] Axis-aligned screw path clearance and 3D collision avoidance.
- [x] Global screw pack rounding with spares allowance.
- [x] Complete transactional exports: CSV BOMs, cut list, SVG technical drawings, OpenSCAD 3D model, vector PDF workshop pack.
- [x] Independent multi-option height comparison tool (`compare`).
- [x] Release review gating (`--release`) blocking unreviewed drafts or unconfirmed pilot specs.
- [x] 83-test comprehensive test suite with property and oracle checks.
- [x] Windows native execution verified (`health.cmd`, `health.ps1`, `sleeperplan.cmd`).
- [x] OpenSCAD workstation integration verified (`view-cad.cmd`, OpenSCAD 2021.01, health smoke compile).
- [x] Deterministic static web manifest + quality report export (`web-manifest.json`, `quality-report.json`).
- [x] Customer-facing static offer visualiser (`site/`) for 1/2/3 course options with interactive 3D and process walkthrough.
- [x] Vercel static deployment pipeline verified for `site/`.

## v0.2.0 / v0.3.0 Hardening (review-driven) — complete
- [x] Physical-design approval binding (`approved_physical_design_hash`); price-only revisions keep approval; machining changes invalidate it (v0.2.0).
- [x] Screw heads/seats declared unmodelled with explicit `head_seat_unmodeled` issue and docs (v0.2.0).
- [x] DEMONSTRATION fixture marking on reviewed example/catalogue with regression test (v0.2.0).
- [x] Combined `options-and-build.pdf` covering 1/2/3 course options + build guides (v0.2.0).
- [x] Deterministic operations model (`operations.json`) + web assembly player with deterministic screw-insertion animation (v0.3.0).
- [x] Price-independent screw selection; commercial rules excluded from physical hash; generator version included (v0.3.0).
- [x] Evidence-kind gate (`fixture` can never issue) (v0.3.0).
- [x] Unified draft/check/release readiness (`release_ready`) (v0.3.0).
- [x] Publication quarantine: stale packs removed, `published/` allowlist with identity checks; legacy viewer defaults to published pack and escapes HTML (v0.3.0).
- [x] Viewer hardening: DPR resize, per-bed display groups, recursive disposal, manifest/plan hash check, blockers panel (v0.3.0).
- [x] Print sizing: paginated parts/stock pages with readable continuation tables (v0.3.0).

---

## Next Milestone: Physical Shop & Field Validation

- [ ] **HIGH PRIORITY — 3-tier 9-sleeper optimisation:**
  - Replace the current 12-sleeper 2400 x 1400 example with a near-identical-width design that uses **9 x 2400 mm sleepers total**.
  - Six 2400 mm sleepers remain full length for the long sides; the remaining three 2400 mm sleepers each produce two short sides.
  - Do **not** preserve an exact 1400 mm outside width if that forces three extra sleepers. Accept a few millimetres of width change to fit real kerf efficiently.
  - Current integer-mm planner target: **1197 mm short sides / 1397 mm outside width**, which fits two identical shorts in a 2400 mm board under the existing conservative 3 mm kerf model (`1197 + 3 + 1197 + 3 = 2400`).
  - Re-run BOM, cuts, costs, operations, animation and PDF packs after the geometry change; regression-test that the 3-course option purchases exactly 9 sleepers.
  - Reconfirm against the measured real sleeper lengths and actual saw kerf before finalising the physical prototype.

- [x] **Session Harness Refresh (2026-09-07):**
  - Verified repo core harness files against `P:\homelab\patterns\repo-harness` (`AGENTS.md`, `state.yaml`, `backlog.md`, `implementationstatus.md`).
  - Added a dated active checklist under `checklists/` for the current field-validation wave.

- [ ] **Stock Dimension & Kerf Calibration:**
  - Measure 3-5 real 100 x 200 x 2400 mm sleepers from Wickes Worthing / regional store.
  - Measure actual saw kerf on 100x200 crosscuts with the target workshop circular/mitre saw.
  - Check end squareness and measure minimum squaring trim required on factory ends.
- [ ] **Fastener & Pilot Testing:**
  - Test drive Wickes 7x150 mm and 7x250 mm washer-head screws into scrap treated softwood sleepers.
  - Compare direct driving vs 4 mm / 5 mm pilot hole: measure split risk near edges/end-grain and torque resistance.
  - Document confirmed pilot diameter, depth, and driving technique in `docs/SOURCES.md`.
- [ ] **First Prototype Assembly (Controlled Trial):**
  - Cut and assemble a 2-course prototype according to generated `cuts.csv` and `BUILD.md`.
  - Validate physical alignment, hole mark-outs, and corner interlocks against SVG drawings.
  - Inspect vertical screw staggering in real timber.

---

## Future Feature Backlog (Post-Field Validation)

### Joinery & Structural Support
- [ ] **Support & Bracing Module:**
  - Automated corner post / internal stake sizing and screw calculation for beds on soft ground or heights > 400 mm.
  - Ground anchor and staking schedules.
- [ ] **Liner & Drainage Detailer:**
  - Per-bed liner cutting layout and membrane overlap calculation.
  - Freeboard and base gravel drainage calculator.

### Catalogue & Stock Expansion
- [ ] **Multi-Supplier Catalogues:**
  - Snapshots for Travis Perkins, B&Q, Jewson, and local timber merchants.
  - Support for alternate sleeper sections (e.g. 125 x 250 mm oak, 100 x 150 mm softwood).
- [ ] **Reusable Offcut Management:**
  - Automated ingestion of `inventory-proposal.json` from completed jobs into a workshop stock registry.

### Workshop Productivity
- [ ] **Mark-Out & Jig Templates:**
  - 1:1 printable drill hole drilling templates for corner and stack fixings.
  - Cut stop / stop-block setup sheet for batch cutting.

### Client Experience (Static Site)
- [ ] **Operations-driven PDF keyframes:**
  - Render step keyframes from `operations.json` into the printable packs so PDF and player share one schedule.
- [ ] **Joint Recipe & Machining Operations (blocked on physical trial):**
  - Per-joint recipe records (head seat, bore preparation, depth datum, evidence) consumed by operations, drawings and CSVs.
  - Per-recipe fastener cards instead of one card per SKU (F08).
- [ ] **Sales Narrative Pass:**
  - Add clearer option positioning text (best-fit use cases) without overstating engineering claims.
  - Add optional branded hero imagery/background assets while keeping page load fast.
- [ ] **Visual Comparison Enhancements:**
  - Add side-by-side mini thumbnails for 1/2/3 course profiles.
  - Add optional animated transition between course options.
