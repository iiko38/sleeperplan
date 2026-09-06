# Implementation Status

## Current Snapshot
- **Version:** 0.1.0
- **Status:** Complete & Validated (Ready for Physical Field Trial)
- **Host Platform:** Windows 11 Native (Verified on `DESKTOP`)
- **Python Version:** CPython 3.12.10 (64-bit)
- **Test Results:** 83 passed, 59 subtests passed (100% passing in 3.4s)
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

## Developer Harness & Automation
- `health.cmd` / `health.ps1`: One-command comprehensive environment, dependency, test suite, and CLI smoke test verification.
- `sleeperplan.cmd`: Root CLI runner directly delegating to `.venv`.
- Directory junction `projects/sleeperplan` linked to `projects/sleepers`.
- Git repository tracking on branch `main` with clean working tree.

## Next Operational Step
Execute physical shop measurement trial on Wickes sleepers and record pilot hole torque/split evidence to promote draft job files to reviewed release packs.
