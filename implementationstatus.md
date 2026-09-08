# Implementation Status

## Current Snapshot
- **Version:** 0.3.0
- **Status:** Planner + operations model + assembly player live; approval/evidence/publication gates enforced; physical joint-recipe trial still required
- **Host Platform:** Windows 11 Native (Verified on `DESKTOP`)
- **Python Version:** CPython 3.12.10 (64-bit)
- **Test Results:** 99 tests passed (unittest, 100% passing)
- **Core Dependencies:** Standard Library only (`reportlab 4.5.1` for PDF export, `pytest 9.1.1` for test execution)

## Verified Functionality
1. **Core Geometry Engine:**
   - Uniform timber profiles on edge (e.g. 100x200 mm) or flat.
   - Alternating corner joints across courses (odd/even course interlocking).
   - Exact piece coordinates, clear opening, and cavity volume calculations.
2. **Cutting Stock Optimizer:**
   - Linear stock cutting optimizer using bounded exact dynamic programming.
   - Heuristic best-fit fallback when budget is exceeded (never claims false infeasibility).
   - Strict material conservation accounting for kerf and squaring trims.
3. **Fixing & Fastener Geometry:**
   - 3D axis-aligned clearance checking preventing screw collisions.
   - Vertical stack screw staggering between adjacent courses.
   - Full-penetration checks into target receiving timber.
4. **Costing & Procurement:**
   - Exact sleeper purchases from inventory and store catalogues.
   - Global screw pack rounding with spares allowance across whole batches.
   - Strict unknown-cost withholding (never silently assumes £0 for missing materials/labour).
5. **Multi-Format Export Pipeline:**
   - Technical mark-out and assembly drawings in SVG.
   - 3D OpenSCAD model generation (`model.scad`).
   - Vector PDF workshop packs and comparative height sheets (`workshop.pdf`, `height-comparison.pdf`).
   - CSV outputs: `cuts.csv`, `parts.csv`, `fixings.csv`, `stock.csv`, `shopping.csv`.
6. **Safety & Scope Enforcing Gates:**
   - Strict review gating (`--release`) rejecting drafts without recorded human measurement, site check, fixing check, and confirmed pilot hole evidence.
   - Hard boundary at 600 mm max height and open-bottom level-ground beds for v1 release.
7. **Static Web Export + Client Visualiser:**
   - Export now includes `web-manifest.json` (artifact/drawing pointers + viewer camera defaults) and `quality-report.json` (deterministic export checks).
   - Customer-facing static site in `site/` presents 1/2/3 course offer options with interactive 3D orbit/zoom/pan.
   - Course separation is visually explicit via per-piece black edge outlines; viewer uses Z-up axis to match generated geometry.
   - Client view includes at-a-glance metrics and process walkthrough, with direct links to assembled drawing, process sheet, manual, and printable PDF.
   - Vercel deployment verified and aliased to: `https://site-rho-six-fdck1jw7c6.vercel.app`.
8. **Combined Height-Options PDF:**
   - `compare --pdf` additionally renders `options-and-build.pdf`: options table, same-scale comparison, then per-option build sequence + course plans + cutting/process/parts/stock pages.
9. **Deterministic Operations Model + Assembly Player:**
   - `sleeperplan/operations.py` compiles an ordered, typed workshop schedule (`operations.json`, schema `sleeperplan.operations.v1`) from the same geometry: receive/label/cut/treat per board, place/clamp per course, mark-STOP or drill + drive per fixing, supports/final checks, with explicit dependencies.
   - The customer site plays that schedule: play/pause/step/scrub, pieces appear when placed, screws animate insertion via `head(u) = E - d*(L+g)*(1-u)` (final frame equals the approved model exactly), per-step camera framing, active-piece highlighting, per-bed display groups for batch jobs.
10. **Approval, Evidence and Publication Gates:**
    - `--release` binds `review.approved_physical_design_hash` to the current physical design hash (price-only revisions keep approval; dimension/hardware/machining changes invalidate it). Screw selection is price-independent, so repricing can never swap hardware under an approval.
    - `pilot_evidence_kind` (`fixture` | `manufacturer_instruction` | `recorded_trial`) is required for confirmed pilot modes; fixture evidence can never issue a workshop plan.
    - One readiness calculation shared by draft/check/release (`release_ready` field); publication tests keep the public tree (`published/`, `site/demo`) free of issued plans and verify manifest/plan identity.

## Developer Harness & Automation
- `health.cmd` / `health.ps1`: One-command comprehensive environment, dependency, OpenSCAD compile smoke, test suite, and CLI smoke test verification.
- `sleeperplan.cmd`: Root CLI runner directly delegating to `.venv`.
- `view-cad.cmd`: One-command OpenSCAD launcher for generated `model.scad` outputs.
- Directory junction `projects/sleeperplan` linked to `projects/sleepers`.
- Repo harness core files aligned with NAS pattern (`AGENTS.md`, `state.yaml`, `backlog.md`, `implementationstatus.md`) and active checklist tracking in `checklists/`.

## Next Operational Step
Execute physical shop measurement trial on Wickes sleepers and record pilot hole torque/split evidence to promote draft job files to reviewed release packs.
