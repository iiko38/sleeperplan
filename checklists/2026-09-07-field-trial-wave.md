# Checklist - 2026-09-07: Field Trial Wave

## Context

This wave starts after MVP software validation and OpenSCAD workstation bedding-in.
The repo remains an offline planning tool and default outputs remain draft until physical evidence is captured.

## Non-Negotiables

- Preserve AGENTS.md invariants, especially geometry/cut/fixing single-model truth.
- Keep units strict (integer mm, integer pence) and avoid inferred pilot rules.
- Do not claim field validation without recorded evidence paths.
- Do not change release status for draft examples without fresh measured review data.

## Phase 1 - Harness And Tooling Baseline

- [x] Confirm OpenSCAD installation on workstation.
- [x] Confirm OpenSCAD compile smoke in health script (`demo/batch/model.scad` -> CSG).
- [x] Confirm repo harness core docs are present (`AGENTS.md`, `state.yaml`, `backlog.md`, `implementationstatus.md`).
- [x] Evidence: OpenSCAD version 2021.01 detected; `health.ps1` run passed with 83 tests and OpenSCAD smoke compile.

## Phase 2 - Physical Stock And Fastener Evidence

- [ ] Measure 3-5 real sleepers (actual section, length, squaring trim).
- [ ] Measure actual workshop kerf on target saw setup.
- [ ] Pilot tests for Wickes 7x150 and 7x250 screws (direct drive vs pilot diameters).
- [ ] Record evidence and source metadata in `docs/SOURCES.md`.
- [ ] Evidence:

## Phase 3 - Controlled Prototype Build

- [ ] Build one 2-course prototype from generated plan outputs.
- [ ] Validate cut list and fixing coordinates against physical assembly outcomes.
- [ ] Record any geometry or workflow deltas as reproducible tests before code changes.
- [ ] Evidence:

## Stop Conditions

- Any measured mismatch that breaks material conservation or fixing clearance assumptions.
- Any screw/pilot finding that invalidates current default fastener assumptions.
- Any release-gate bypass attempt without evidence updates.

## Current Next Step

Collect first stock and kerf measurements and add dated evidence to `docs/SOURCES.md`.
