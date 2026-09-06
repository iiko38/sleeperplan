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

---

## Next Milestone: Physical Shop & Field Validation

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
