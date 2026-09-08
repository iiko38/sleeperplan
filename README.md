# Sleeperplan

**A local workshop tool for repeatable timber sleeper flower beds.**

A job file goes in. Labelled parts, exact stock allocations, saw bands, fixing coordinates, purchases, costs and technical drawings come out. The same positioned timber model drives the cut list, the fixing schedule, the SVG drawings, the optional PDF and the OpenSCAD model.

No LLM calls. Core planner runtime: Python 3.11+ and its standard library. Optional PDF dependency: ReportLab.

The planning engine remains deterministic and local/offline. A static client visualiser is now included under `site/` for showing 1/2/3 course options in-browser. It uses generated JSON artifacts and does not require a database.

## Start here on Windows

Extract the ZIP and open PowerShell **inside the `sleeperplan` folder**, alongside this README.

```powershell
py -m sleeperplan plan examples\neighbour.json --out build\neighbour
```

Open `build\neighbour\BUILD.md` and the files in `build\neighbour\drawings`. SVGs open locally in a browser or suitable image/vector viewer.

If OpenSCAD is installed, open the generated 3D model directly:

```cmd
view-cad.cmd build\neighbour\model.scad
```

Compare two and three courses:

```powershell
py -m sleeperplan compare examples\neighbour.json --courses 2 3 --out build\heights
```

To generate printable PDFs too:

```powershell
py -m pip install -e ".[pdf]"
py -m sleeperplan compare examples\neighbour.json --courses 2 3 --out build\heights-pdf --pdf
```

`height-comparison.pdf` is the same-scale comparison. `options-and-build.pdf` is a single combined document covering every requested height: an options table, the same-scale comparison drawing, then a per-option build section (build sequence, assembled view, one plan page per course, cutting diagrams, process and parts boards). Each height's directory also contains a full `workshop.pdf` with the parts and drilling/mark-out sheets.

For Linux, replace `py` with `python3` and use `/` in paths. Installing the package is unnecessary for the core commands when run from this folder. An optional `pip install -e .` also installs the `sleeperplan` command.

**Output directories must be new.** The tool refuses to overwrite an existing folder. Use a revision name such as `build\neighbour-r02`.

## What to edit for a real job

Copy `examples/neighbour.json` to a new file **in the examples folder** to preserve the relative catalogue path. Change the name, bed dimensions, number of courses and quantity. Measurements are **outside dimensions in whole millimetres**. Prices are **integer pence**.

The example is a **2,400 x 1,200 mm outside footprint**, not the neighbour's surveyed dimensions. It uses the same 100 x 200 mm timber section throughout, on edge: 100 mm wall thickness and 200 mm per course. Two courses are 400 mm; three are 600 mm. `orientation: "flat"` swaps these dimensions and selects different screw lengths.

```json
{
  "id": "front",
  "length_mm": 2400,
  "width_mm": 1200,
  "courses": 3,
  "quantity": 2,
  "corner_pattern": "alternating",
  "freeboard_mm": 50,
  "access_sides": 2,
  "site_type": "level_open_ground"
}
```

Put several designs in `beds` and the tool cuts them as **one batch**, sharing stock capacity and rounding screw packs once across the whole job. `examples/batch.json` demonstrates this. `examples/with-offcut.json` adds one measured piece of existing stock.

The catalogue is ordinary editable JSON in `catalogues/`. It contains a dated Wickes price snapshot, not a live stock integration. Duplicate the catalogue for a new date or a different uniform timber profile. Every stock length in one catalogue must have the stated section, treatment/material and finish. Do not mix mismatched timber under one profile.

The supplier description says Wickes in the Clapham / West Sussex area, as requested. **The exact branch is unconfirmed.** The official Worthing store is documented in `docs/SOURCES.md`; no branch availability has been asserted.

## The outputs

| File | Purpose |
|---|---|
| `plan.json` | Full model, normalised inputs, source URLs, date, review gates and input hash. |
| `parts.csv` | Unique piece IDs, lengths, course, orientation, assembly coordinates and allocated stock board. |
| `stock.csv` | Every purchased/existing sleeper used, trims, cost and remaining offcut. |
| `cuts.csv` | Sequential saw operations; exact kerf start, end and blade centre from the original stock datum A. |
| `fixings.csv` | Each screw's entry face, local/global coordinates, direction, receiving piece, nominal penetration and pilot status. |
| `shopping.csv` | Sleeper quantities, whole screw packs, spares and explicit extras/labour. All monetary columns are pence. |
| `web-manifest.json` | Static-web manifest for viewer/links/camera defaults. |
| `quality-report.json` | Deterministic export checks (sections, drawing inventory, callout coverage). |
| `BUILD.md` | Job-specific dimensions, review gates, workflow and assembly instructions. |
| `inventory-proposal.json` | Unused existing inventory and useful new offcuts; merge only after the physical job is completed. |
| `drawings/` | Assembled views, each course, cutting diagrams and an individual fixing sheet for every part. |
| `model.scad` | OpenSCAD geometry; set `explode_mm` to inspect courses and `show_fixing_paths` to show screw paths. |
| `workshop.pdf` | Optional vector workshop pack, generated from the same drawing scene graph. |

The comparison command creates complete **independent alternatives**. It does not consume inventory between options or add their purchases together. It resets review records because changing a design needs a new review.

## What is checked, not guessed

**Joinery.** With alternating corners, courses 1/3 use two full-length long members and shorter cross-members; course 2 reverses which sides pass through the corners. There are no mid-side splices. A length that cannot be cut as one piece is rejected, rather than quietly joined.

**Saw allowance.** Two exact 1,200 mm parts do not fit a 2,400 mm sleeper with a non-zero saw kerf. A final piece that exactly reaches a sound stock end does not get charged an imaginary final cut. End trims are explicit and include their own kerf. Tiny terminal slivers that require edge-shaving are rejected by this full-crosscut model.

**Stock optimisation.** A bounded exact dynamic programme enumerates feasible cutting patterns across stock lengths and finite inventory. Its objective is purchase price, then purchased sleeper count, then total input length. If its deterministic work budget is exhausted, it emits a valid greedy fallback labelled **heuristic**, never “optimal”. If that fallback fails it does not claim infeasibility was proven.

**Screw paths.** Corner and vertical fixing paths are checked against the actual positioned timber. Receivers must exist; tips must stay in the receiving member; modelled shafts must not collide. Upper-course screws are staggered to avoid previously installed screws. Extra intermediate entries are added when collision avoidance would otherwise exceed the configured maximum spacing. These are geometric checks, not strength calculations.

**Purchases and costs.** Screw packs round upwards after the configured spares allowance. Existing stock does not incur a second cash purchase, but its value is left as an explicit cost to resolve. Transport, fill, supports, liner, preparation, treatment, consumables and labour cannot vanish silently: missing values remain `null`/`UNPRICED`, and a complete-cost figure and margin target are withheld.

## Important: the supplied plans are drafts

The code is tested. **The construction detail has not been field-validated.** Do not use an unreviewed pack as a completed engineering design.

The starting Wickes catalogue confirms the screw products, sizes and prices, **not a specific pilot-hole diameter/depth**. All fixing centres are calculated, but `pilot_mode` deliberately starts as `unconfirmed`. After obtaining the actual product/timber instruction or recording an appropriate supervised trial, enter either:

* `pilot_mode: "pilot"`, with the confirmed `pilot_diameter_mm`, `pilot_depth_mm` and `pilot_evidence`; or
* `pilot_mode: "none"`, with evidence supporting no pilot for that exact use.

There is no automatic “screw diameter minus 2 mm” rule.

Before releasing a pack, measure timber/kerf and review the site, supports and fixing design. Populate the three review checks, reviewer, date and notes in the job file. Then run:

```powershell
py -m sleeperplan plan examples\your-job.json --out build\your-job-reviewed --release --pdf
```

`--release` refuses missing checks, unconfirmed pilots and out-of-scope sites/heights. A released status means the review was recorded, **not** that the software certified a structure. Any changed dimensions, hardware, stock or site require renewed review.

V1 covers **rectangular, open-bottom flower beds on level ground**, with nominal heights up to 600 mm for reviewed output. That height is a software scope boundary, not a universally safe height. Retaining walls, slopes, roofs/decks, hard-surface drainage details, structural calculations, bespoke support/bracing layouts and mid-side splice designs are not implemented. The app will not supply missing engineering by inventing it. See `docs/ENGINEERING.md`.

## Cost entry

Example **syntax**, not recommended prices:

```json
"costs": {
  "labour_minutes": 240,
  "labour_rate_pence_per_hour": 3000,
  "target_margin_bps": 2500,
  "extras": [
    {
      "id": "transport",
      "description": "Collection travel",
      "quantity": 1,
      "unit": "job",
      "unit_price_pence": 1500
    }
  ]
}
```

Here `2500` basis points means 25% gross margin, calculated as cost / (1 - margin), **not** a 25% markup. The target remains blank until every required cost line is supplied. Set a line explicitly to zero only when genuinely not required or already allowed elsewhere. This is an internal cost tool, not an invoice or VAT accounting system.

Fill litres come from the clear opening and specified freeboard. They do not include settlement/compaction allowances, existing soil, displaced supports or a planting recipe. Liner area is a net internal-wall measure, not a roll cutting/nesting plan. Price the actual required materials separately.

## Reproducibility and testing

```powershell
py -m unittest discover -v
py -m sleeperplan plan examples\neighbour.json --as-of 2026-09-06 --out build\reproduction
py -m sleeperplan check examples\neighbour.json --as-of 2026-09-06
```

`check` exits 3 for a geometrically valid but unreviewed draft, 2 for invalid/infeasible input, 0 for a clear review gate. Normal draft `plan` output exits 0 so design iterations are usable. `--release` turns missing review into an error.

The tests include an independent exhaustive subset solver for small cutting cases, seeded geometry/material-conservation cases, stock limits, screw-path collisions, golden worked examples, monetary rounding, review gates, deterministic exports, CLI behaviour and optional PDF generation. `docs/VALIDATION.md` records what was actually run and what remains to be tested on site / native Windows.

## Code map

```
sleeperplan/
  model.py       typed job, stock, timber and fixing records
  config.py      strict JSON/unit/money validation
  geometry.py    positioned pieces, connections and path checks
  cutting.py     exact cutting stock solver, fallback and saw bands
  costing.py     purchases, pack rounding, extras and labour
  planner.py     pipeline, provenance hash and review gates
  drawing.py     shared vector scenes and OpenSCAD export
  export.py      transactional CSV/JSON/drawing/build-note output
  pdf.py         optional print rendering
  cli.py         plan / check / compare
```

`AGENTS.md` gives coding agents the invariants to preserve. Start improvements by reproducing a physical or mathematical failure in a test. Scope now also includes the static customer visualiser in `site/`.

## Customer visualiser

`site/` is a static client-facing page for presenting offer options:

- 1, 2 and 3 course variants loaded from generated `web-manifest.json` bundles.
- Interactive 3D rotate/pan/zoom with Z-up orientation and visible course edges.
- Client-friendly metrics and process flow with links to assembled/process/manual/PDF artifacts.

Run locally:

```powershell
py -m http.server 4173
```

Then open:

```text
http://localhost:4173/site/
```

Optional direct offer links:

```text
http://localhost:4173/site/?offer=c1
http://localhost:4173/site/?offer=c2
http://localhost:4173/site/?offer=c3
```

## Repo harness

This repository follows the NAS repo-harness pattern with current-state files at repo root:

- `AGENTS.md`
- `state.yaml`
- `backlog.md`
- `implementationstatus.md`
- `checklists/2026-09-07-field-trial-wave.md`
