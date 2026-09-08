# Changelog

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
