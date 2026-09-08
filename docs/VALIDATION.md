# Validation record

## Executed in the build environment

Date: 6 September 2026. Environment: Linux, CPython 3.13.5. The optional ReportLab renderer was available.

`python -m unittest discover -v`: **83 tests passed**. Within those tests are:

- 200 seeded rectangular-ring geometry cases.
- 40 seeded fixing-layout cases, checking all modelled pairs of screw shafts.
- 100 seeded cutting/material-conservation cases.
- 70 small cutting-stock instances checked against an independent exhaustive subset-partition oracle.
- The same plan exported twice and compared byte-for-byte, including optional PDFs.
- CLI checks, explicit release failures, independent height alternatives, bad inputs, finite inventory, saw kerf/end trims, screw pack rounding and incomplete-cost handling.

The example three-course plan, the two/three-course comparison, and a multi-bed batch were also generated with the real CLI. SVGs and rendered PDF pages were inspected for geometry, coordinate labels and legibility. The tests do not prove all possible combinations correct; the supported model and explicit rejects are documented in ENGINEERING.md.

## Included but not executed here

A GitHub Actions matrix is provided for **native Windows and Ubuntu, Python 3.11 and 3.13**, plus optional PDF output on Ubuntu. CI currently verifies generation of OpenSCAD source only; external OpenSCAD compilation is verified on native Windows via the health script.

## Executed on Native Windows host

Date: 6 September 2026. Environment: Windows 11, CPython 3.12.10 (64-bit), PowerShell / CMD.

- Virtual environment `.venv` created and package installed in editable mode (`pip install -e ".[pdf]" pytest ruff`).
- Full test suite execution: `python -m unittest discover -v` and `pytest -v` — **83 passed, 60 subtests passed** in 3.0s.
- Native PowerShell and CMD runners verified (`health.cmd`, `health.ps1`, `sleeperplan.cmd`).
- OpenSCAD 2021.01 installation detected and compile smoke test run (`demo/batch/model.scad` to CSG) through `health.ps1`.
- Batch planning, multi-option comparison (`compare`), and vector PDF generation verified with ReportLab 4.5.1 (`height-comparison.pdf`, `workshop.pdf`).
- Release review pipeline tested end-to-end with confirmed pilot specifications and full job costing (`examples/reviewed-example.json`), successfully generating `REVIEWED_WORKSHOP_PLAN`.

## Not physically validated

No real timber was cut or drilled for this delivery. No site was surveyed. The neighbour's measurements, branch stock, timber condition, real saw kerf, exact screw pilot specification, connection strength, bracing/supports, soil pressure, foundation or drainage detail have been verified on site. The shipped examples therefore remain **DRAFT_MARK_OUT_ONLY**, and `--release` rejects them.

This is a working software foundation and a field-trial workflow, not a certified kit design. Field corrections should become regression tests before standardising the installation service or offering kits for sale.

## Static customer visualiser checks

Date: 7 September 2026. Environment: Windows 11 + Vercel production deployment.

- Confirmed `site/` deploys as static assets via Vercel and serves the production alias.
- Verified offer manifests resolve for all three options: `demo/offer-c1`, `demo/offer-c2`, `demo/offer-c3`.
- Verified module loading is self-contained (`site/vendor/three.module.js`, `site/vendor/OrbitControls.module.js`) to avoid browser import-specifier failures.
- Verified viewer camera uses Z-up orientation and renders course boundaries with explicit per-piece edge lines.
- Verified client links surface assembled/process/manual/PDF artifacts from manifest paths.

These checks validate web presentation and integration, not structural correctness. Release gating and pilot evidence requirements are unchanged.
