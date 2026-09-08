"""Transactional output into a NEW directory; never delete a user's existing directory."""
from __future__ import annotations
import csv
import json
import shutil
import tempfile
from pathlib import Path
from .costing import pounds
from .drawing import (iso_scene, layer_scene, piece_scene, cutting_scene, scad_model,
                      process_scene, stock_scene, fastener_scene, parts_scene)
from .model import PlanError
from .operations import operations_document


def write_json(path: Path, value: object):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def csv_rows(path: Path, rows: list[dict], columns: list[str]):
    # UTF-8 BOM lets Windows Excel show text correctly. Treat spreadsheet-formula strings as text.
    def safe(v):
        if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')):
            return "'"+v
        return v
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore')
        writer.writeheader()
        for r in rows:
            writer.writerow({k:safe(v) for k,v in r.items()})


def build_notes(plan: dict) -> str:
    b=plan['cut_plan'];cost=plan['costs'];t=plan['profile']['thickness_mm'];h=plan['profile']['height_mm']
    patterns={bed['corner_pattern'] for bed in plan['beds']}
    if patterns == {'alternating'}:
        corner_instruction = "Follow the per-course drawing; alternating corners change which sides run full length."
    elif len(patterns) == 1:
        corner_instruction = "Follow the per-course drawing; the corner pattern stays the same on every course."
    else:
        corner_instruction = "Follow the per-course drawing; corner pattern can differ by bed design in this batch."
    lines=[f"# {plan['name']}",f"\n**{plan['status']}** | {plan['as_of']} | plan `{plan['input_sha256']}` | physical design `{plan['physical_design_hash']}`",
           "\n## Before work starts", "This pack checks nominal geometry, stock allocation and straight screw paths. "
           "It does not calculate structural capacity, soil pressure, foundation adequacy or long-term timber movement. "
           "Do not build from an unreviewed draft. Site-specific supports/bracing are not part of the generated timber model.",
           "\n"+"\n".join(f"- **{'BLOCKER' if i['blocking'] else 'Note'} / {i['code']}**: {i['message']}" for i in plan['issues']),
           "\n## Read the dimensions correctly",f"All plan dimensions are millimetres. Timber wall thickness is **{t} mm**; each course adds **{h} mm**. "
           "Outside dimensions include the walls. Interior dimensions subtract two wall thicknesses. "
           "The drawing's S/W labels define a reference frame; they need not point south or west on site.",
           "Piece A is the lower-global-X end for S/N members, or lower-global-Y end for W/E members. "
           "U runs from A along the piece. V runs from the lower-coordinate cross-section edge (not always the outside face). "
           "W runs upwards from the piece bottom. Top fixings enter at W=course height; outer-face entries have V=0 for S/W and V=wall thickness for N/E. "
           "Use labelled piece sheets instead of guessing the orientation.",
           "\n## Assembly sequence",
           "1. Survey the footprint and access. Identify buried services before any ground work. Confirm a level, open-bottom site and adequate drainage. "
           "Record the separate support/foundation plan. Check the purchase list and collection/handling arrangements.",
           "2. Inspect and measure the timber: actual usable lengths, section, straightness and end condition. Measure actual saw kerf with a test cut. "
           "Set end trims explicitly, update the catalogue/job and regenerate. A nominal 2400 mm sleeper is not guaranteed to yield a square 2400 mm part.",
           "3. Lay out the proposed frame full-size. Check external dimensions and equal outside diagonals. Confirm access to plant the centre. "
           "Label every stock item with its B-number and original end A before cutting.",
           "4. Make the listed end trims, then the sequential crosscuts. In cuts.csv, each kerf_start..kerf_end band is WASTE. "
           "Do not centre the blade on the finished-length boundary. Coordinates stay relative to the ORIGINAL stock datum A, even after squaring it. "
           "A saw cut means one complete crosscut through the section; it does not specify a particular saw or number of machine passes. "
           "Use a suitable saw, stable supports/clamps and appropriate dust/eye/hearing protection following the tool instructions.",
           "5. Mark the resulting piece IDs on the timber and preserve the A end / TOP / OUTER orientation. Check finished lengths. "
           "Treat exposed cut ends with the compatible product and method specified for the timber.",
           "6. Assemble course 1 on the prepared base. Clamp and verify square and level before fixing. Corner screws enter the OUTER side face of the full-through member "
           "and pass into the end of its adjoining member. They do not enter through the cut end of that full-through member.",
            f"7. {corner_instruction} Position and clamp the next course, then use its own fixing sheet. "
            "Stack screws enter vertically through the TOP and into the previous course. The schedule offsets them to avoid modelled existing screws. "
            "Re-check that real timber, hardware heads and installation tolerances match the model before drilling or driving. "
            "Screw HEADS and bearing seats are NOT modelled: before stacking any course, confirm the head-seat detail for the actual hardware "
            "(a protruding head can stop the next sleeper sitting flat, and recessing a seat deepens the hole and moves the tip).",
            "8. For every fixing use the confirmed pilot instruction for the actual screw and timber. UNCONFIRMED is a STOP, not permission to choose a bit. "
            "Hole coordinates are entry centres; pilot depth is measured from that entry face along the stated direction. Nominal screw penetration includes its point, "
            "so it is not the same as effective threaded embedment.",
            "9. Install and inspect the separately reviewed supports, protection/liner and drainage details. Do not turn an open-bottom bed into an undrained tank. "
            "Then fill to the specified freeboard. Fill quantity is cavity geometry only, without compaction, settlement, existing soil or displaced supports.",
            "10. Record actual purchases, labour, corrections and useful offcuts. Only AFTER completing the cut plan, merge the inventory proposal into the next job. "
            "Measure retained offcuts again; running a plan does not consume physical stock.",
            "\n## Draft workshop advisory (not confirmed pilot evidence)",
            "Use this only as trial planning context while pilot mode remains unconfirmed. It is not manufacturer approval and must not be copied into release evidence without a recorded source or physical trial for the exact screw/timber pair.",
            "- Pilot-hole trial start points for 7 mm timber-drive screws: treated softwood receiving piece around 4.5-5.0 mm; denser/harder timber often larger (around 5.5-6.0 mm).",
            "- For long screws (for example 250 mm), test deeper pilot depths to reduce drive torque and wandering, and stop if splitting, lift or burning appears.",
            "- Near edges/ends: clamp, reduce drive speed, and favour piloting to reduce splitting risk.",
            "- Sleeper planter practice: keep base level and drained, preserve open-bottom drainage path, treat cut ends, and use corrosion-resistant fixings suitable for treated timber.",
            "\n## Bed schedule", "| Bed | Outside L x W x H | Courses | Clear opening | Fill litres | Outside diagonal |", "|---|---|---:|---|---:|---:|"]
    for bed in plan['beds']:
        lines.append(f"| {bed['id']} | {bed['length_mm']} x {bed['width_mm']} x {bed['height_mm']} | {bed['courses']} | "
                     f"{bed['inside_length_mm']} x {bed['inside_width_mm']} | {bed['fill_litres']} | {bed['diagonal_mm']} |")
    lines += ["\n## Purchase / cutting summary", f"{b['purchased_sleepers']} purchased sleepers; {b['inventory_pieces_used']} existing stock pieces used; "
              f"{b['saw_cuts']} full crosscuts. Optimiser: **{b['algorithm']}**. {b['reason']}",
              f"Finished timber: {b['finished_length_mm']} mm. Input stock: {b['input_length_mm']} mm. "
              f"Remaining offcuts: {b['offcut_length_mm']} mm. Kerf + trim loss: {b['kerf_and_trim_loss_mm']} mm.",
              "Offcuts are not all waste. No speculative offcut resale credit is used to reduce today's purchase cost.",
              f"Timber and screw purchases: **{pounds(cost['timber_and_screw_purchase_pence'])}**. "
              f"Known subtotal: **{pounds(cost['known_subtotal_pence'])}**.",
              "Complete job cost: "+pounds(cost['complete_cost_pence'])+". Unpriced: "+(', '.join(cost['unpriced_items']) or 'none')+".",
              "Internal margin-based target: "+pounds(cost['internal_target_price_pence'])+". "+cost['pricing_note'],
              "\n## Files", "`plan.json` contains the full model and normalised inputs. `parts.csv` ties each member to its stock board. "
              "`cuts.csv` gives actual saw bands, including trim cuts. `stock.csv` lists every used stock item. `fixings.csv` gives local/global coordinates, receiver, "
              "direction, screw and pilot information. `shopping.csv` rounds purchases to whole screw packs. `model.scad` is an offline OpenSCAD model with optional exploded view. "
              "`drawings/` contains assembled, per-course, cutting and individual piece sheets. CSV money columns are integer pence.",
              "\nThe supplier and price snapshot are embedded in plan.json. Read docs/SOURCES.md and docs/ENGINEERING.md in the repository for evidence and model limits."]
    return '\n\n'.join(lines)+'\n'


def manual_notes(plan: dict) -> str:
    lines=[
        f"# Workshop manual - {plan['name']}",
        "",
        f"Plan: `{plan['input_sha256']}`  |  Status: {plan['status']}  |  As of: {plan['as_of']}",
        "",
        "## Read this first",
        "",
        "- [2x] Use two people for heavy lifts and long members.",
        "- [CHECK] Verify level, square and labels at every stage.",
        "- [STOP] Any blocker in `BUILD.md` means stop and resolve before building.",
        "",
        "## Prepare before assembly",
        "",
        "1. Clear enough floor area to lay out full-length members.",
        "2. Confirm stock IDs, part labels and datum A orientation before cuts.",
        "3. Keep all fixings and driver bits grouped by screw ID.",
        "4. Open the process and drawing sheets before drilling or driving.",
        "",
        "## Pack map (use in order)",
        "",
        "1. `drawings/parts-fixings-board.svg`",
        "2. `drawings/process-overview.svg`",
        "3. `drawings/stock-arrival-labelling.svg`",
        "4. `drawings/cuts-*.svg` + `cuts.csv`",
        "5. `drawings/*-C*-plan.svg`",
        "6. `drawings/*-fixings.svg` + `fixings.csv`",
        "7. `drawings/fastener-*.svg` + `shopping.csv`",
        "",
        "## Step flow",
        "",
        "1. Label incoming stock and mark datum A ends.",
        "2. Perform trims and crosscuts in listed sequence only.",
        "3. Mark each finished part ID and orientation (A/TOP/OUTER).",
        "4. Assemble course 1 square and level, then fix.",
        "5. Repeat by course using each course plan and fixing sheet.",
        "6. Fit reviewed support/drainage details before filling.",
        "",
        "## Drill and pilot rule",
        "",
        "- `pilot_mode=pilot`: use the scripted drill-bit diameter/depth exactly.",
        "- `pilot_mode=none`: no pilot, per recorded evidence.",
        "- `pilot_mode=unconfirmed`: STOP. Do not drill until diameter/depth evidence is recorded.",
        "",
        "## Draft workshop advisory (while unconfirmed)",
        "",
        "- These are trial planning notes only, not release evidence for `pilot_mode`.",
        "- For 7 mm timber-drive screws, trial softwood pilot around `4.5-5.0 mm`; in denser timber trial larger pilots around `5.5-6.0 mm`.",
        "- For long screws (for example `250 mm`), trial deeper pilots to reduce torque and wandering.",
        "- Near edges/ends: clamp, slow drive speed, and favour piloting to reduce split risk.",
        "- Sleeper planter basics: level drained base, maintain open-bottom drainage, treat cut ends, and use corrosion-resistant fixings.",
        "",
        "All coordinates and counts are script-generated from the same geometry model that drives cuts, fixings and drawings.",
    ]
    return "\n".join(lines)+"\n"


def _viewer_defaults(plan: dict) -> dict:
    min_x = min(p['x_mm'] for p in plan['pieces'])
    min_y = min(p['y_mm'] for p in plan['pieces'])
    min_z = min(p['z_mm'] for p in plan['pieces'])
    max_x = max(p['x_mm'] + (p['length_mm'] if p['axis'] == 'X' else p['thickness_mm']) for p in plan['pieces'])
    max_y = max(p['y_mm'] + (p['thickness_mm'] if p['axis'] == 'X' else p['length_mm']) for p in plan['pieces'])
    max_z = max(p['z_mm'] + p['height_mm'] for p in plan['pieces'])

    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    max_size = max(size_x, size_y, size_z)
    centre_x = (min_x + max_x) / 2
    centre_y = (min_y + max_y) / 2
    centre_z = (min_z + max_z) / 2
    distance = max_size * 1.8 if max_size else 1000

    return {
        "units": "mm",
        "bounds_mm": {
            "min": [min_x, min_y, min_z],
            "max": [max_x, max_y, max_z],
            "size": [size_x, size_y, size_z],
        },
        "camera": {
            "target_mm": [round(centre_x, 3), round(centre_y, 3), round(centre_z, 3)],
            "position_mm": [
                round(centre_x + distance, 3),
                round(centre_y + distance * 0.8, 3),
                round(centre_z + distance * 0.65, 3),
            ],
            "fov_degrees": 45,
            "min_distance_mm": max(100.0, round(max_size * 0.2, 3)),
            "max_distance_mm": max(1000.0, round(max_size * 6.0, 3)),
        },
        "controls": {
            "orbit": True,
            "zoom": True,
            "pan": True,
        },
    }


def _web_manifest(plan: dict, *, pdf: bool) -> dict:
    drawings = []
    for b in plan['beds']:
        drawings.append({"kind": "assembled", "path": f"drawings/{b['id']}-assembled.svg", "bed_id": b['id']})
        for layer in range(1, b['courses'] + 1):
            drawings.append({"kind": "course_plan", "path": f"drawings/{b['id']}-C{layer}-plan.svg", "bed_id": b['id'], "course": layer})
    for p in plan['pieces']:
        drawings.append({"kind": "piece_fixings", "path": f"drawings/{p['id']}-fixings.svg", "piece_id": p['id']})
    boards = plan['cut_plan']['boards']
    for i in range(0, len(boards), 5):
        drawings.append({"kind": "cut_sheet", "path": f"drawings/cuts-{i//5+1:02d}.svg"})
    drawings.append({"kind": "parts_board", "path": "drawings/parts-fixings-board.svg"})
    drawings.append({"kind": "process_overview", "path": "drawings/process-overview.svg"})
    drawings.append({"kind": "stock_arrival", "path": "drawings/stock-arrival-labelling.svg"})
    for screw_id in sorted({f['screw_id'] for f in plan['fixings']}):
        drawings.append({"kind": "fastener", "path": f"drawings/fastener-{screw_id}.svg", "screw_id": screw_id})

    artifacts = {
        "plan": "plan.json",
        "operations": "operations.json",
        "build_notes": "BUILD.md",
        "workshop_manual": "WORKSHOP_MANUAL.md",
        "model_scad": "model.scad",
        "parts_csv": "parts.csv",
        "cuts_csv": "cuts.csv",
        "stock_csv": "stock.csv",
        "fixings_csv": "fixings.csv",
        "shopping_csv": "shopping.csv",
        "inventory_proposal": "inventory-proposal.json",
        "quality_report": "quality-report.json",
    }
    if pdf:
        artifacts["workshop_pdf"] = "workshop.pdf"

    return {
        "schema": "sleeperplan.web_manifest.v1",
        "name": plan['name'],
        "status": plan['status'],
        "as_of": plan['as_of'],
        "plan_sha256": plan['input_sha256'],
        "generator_version": plan['generator_version'],
        "artifacts": artifacts,
        "drawings": drawings,
        "viewer": _viewer_defaults(plan),
    }


def _quality_report(plan: dict, manual_text: str, manifest: dict) -> dict:
    manual_sections = [
        "Read this first",
        "Prepare before assembly",
        "Pack map (use in order)",
        "Step flow",
        "Drill and pilot rule",
        "Draft workshop advisory (while unconfirmed)",
    ]
    section_presence = {title: (f"## {title}" in manual_text) for title in manual_sections}

    kind_counts: dict[str, int] = {}
    for drawing in manifest['drawings']:
        kind = drawing['kind']
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    focus_kinds = {"corner": 0, "stack": 1}
    pieces_with_callouts = 0
    pieces_with_fixings = 0
    callouts_by_kind = {"corner": 0, "stack": 0, "other": 0}
    for piece in plan['pieces']:
        fixings = [f for f in plan['fixings'] if f['piece_id'] == piece['id']]
        focus = sorted(fixings, key=lambda f: focus_kinds.get(f['kind'], 2))[:3]
        if fixings:
            pieces_with_fixings += 1
        if focus:
            pieces_with_callouts += 1
        for fixing in focus:
            key = fixing['kind'] if fixing['kind'] in callouts_by_kind else "other"
            callouts_by_kind[key] += 1

    expected = {
        "assembled": len(plan['beds']),
        "course_plan": sum(b['courses'] for b in plan['beds']),
        "piece_fixings": len(plan['pieces']),
        "cut_sheet": (len(plan['cut_plan']['boards']) + 4) // 5,
        "parts_board": 1,
        "process_overview": 1,
        "stock_arrival": 1,
        "fastener": len({f['screw_id'] for f in plan['fixings']}),
    }

    checks = {
        "manual_sections_complete": all(section_presence.values()),
        "drawings_match_expected": all(kind_counts.get(k, 0) == v for k, v in expected.items()),
        "piece_callouts_cover_all_fixing_pieces": pieces_with_callouts == pieces_with_fixings,
    }

    return {
        "schema": "sleeperplan.quality_report.v1",
        "plan_sha256": plan['input_sha256'],
        "manual_sections": section_presence,
        "drawings_expected": expected,
        "drawings_actual": kind_counts,
        "callout_summary": {
            "pieces_with_callouts": pieces_with_callouts,
            "pieces_with_fixings": pieces_with_fixings,
            "total_pieces": len(plan['pieces']),
            "callouts_by_kind": callouts_by_kind,
        },
        "pilot_mode_summary": {
            "pilot": sum(1 for f in plan['fixings'] if f['pilot_mode'] == 'pilot'),
            "none": sum(1 for f in plan['fixings'] if f['pilot_mode'] == 'none'),
            "unconfirmed": sum(1 for f in plan['fixings'] if f['pilot_mode'] == 'unconfirmed'),
        },
        "checks": checks,
    }


def _populate(plan: dict, directory: Path, pdf: bool):
    directory.mkdir(parents=True,exist_ok=True)
    manual_text = manual_notes(plan)
    build_text = build_notes(plan)
    manifest = _web_manifest(plan, pdf=pdf)
    write_json(directory/'plan.json',plan)
    write_json(directory/'inventory-proposal.json',plan['inventory_proposal'])
    write_json(directory/'operations.json',operations_document(plan))
    write_json(directory/'web-manifest.json',manifest)
    write_json(directory/'quality-report.json',_quality_report(plan,manual_text,manifest))
    (directory/'BUILD.md').write_text(build_text,encoding='utf-8')
    (directory/'WORKSHOP_MANUAL.md').write_text(manual_text,encoding='utf-8')
    (directory/'model.scad').write_text(scad_model(plan),encoding='utf-8')
    allocation={part['piece_id']:board['id'] for board in plan['cut_plan']['boards'] for part in board['parts']}
    parts=[dict(p,stock_board=allocation[p['id']]) for p in plan['pieces']]
    csv_rows(directory/'parts.csv',parts,['id','stock_board','bed_id','course','side','axis','length_mm','thickness_mm','height_mm','x_mm','y_mm','z_mm','through_at_corners'])
    cut_rows=[dict(c,board_id=b['id'],stock_id=b['stock_id']) for b in plan['cut_plan']['boards'] for c in b['cuts']]
    csv_rows(directory/'cuts.csv',cut_rows,['board_id','stock_id','sequence','operation','piece_id','kerf_start_mm','kerf_end_mm','blade_centre_mm'])
    csv_rows(directory/'stock.csv',plan['cut_plan']['boards'],['id','stock_id','inventory','gross_length_mm','trim_start_mm','trim_end_mm','price_pence','offcut_start_mm','offcut_mm','keep_offcut','kerf_and_trim_loss_mm','source_url'])
    fixing_rows=[]
    for f in plan['fixings']:
        d=dict(f)
        d.update(zip(['u_from_A_mm','v_mm','w_up_mm'],f['local_mm']))
        d.update(zip(['entry_x_mm','entry_y_mm','entry_z_mm'],f['entry_mm']))
        d.update(zip(['direction_x','direction_y','direction_z'],f['direction']))
        fixing_rows.append(d)
    csv_rows(directory/'fixings.csv',fixing_rows,['id','bed_id','course','piece_id','receiver_id','kind','entry_face','u_from_A_mm','v_mm','w_up_mm',
        'entry_x_mm','entry_y_mm','entry_z_mm','direction_x','direction_y','direction_z','screw_id','screw_length_mm','diameter_mm','through_mm','penetration_mm',
        'pilot_mode','pilot_diameter_mm','pilot_depth_mm'])
    csv_rows(directory/'shopping.csv',plan['costs']['rows'],['id','category','description','needed','buy_quantity','unit','spares','unit_price_pence','line_pence','source_url','price_checked_on','note'])
    drawings=directory/'drawings';drawings.mkdir()
    for b in plan['beds']:
        (drawings/f"{b['id']}-assembled.svg").write_text(iso_scene(plan,b).svg(),encoding='utf-8')
        for layer in range(1,b['courses']+1):
            (drawings/f"{b['id']}-C{layer}-plan.svg").write_text(layer_scene(plan,b,layer).svg(),encoding='utf-8')
    for p in plan['pieces']:
        (drawings/f"{p['id']}-fixings.svg").write_text(piece_scene(plan,p).svg(),encoding='utf-8')
    boards=plan['cut_plan']['boards']
    for i in range(0,len(boards),5):
        (drawings/f"cuts-{i//5+1:02d}.svg").write_text(cutting_scene(plan,boards[i:i+5]).svg(),encoding='utf-8')
    (drawings/'parts-fixings-board.svg').write_text(parts_scene(plan).svg(),encoding='utf-8')
    (drawings/'process-overview.svg').write_text(process_scene(plan).svg(),encoding='utf-8')
    (drawings/'stock-arrival-labelling.svg').write_text(stock_scene(plan).svg(),encoding='utf-8')
    for screw_id in sorted({f['screw_id'] for f in plan['fixings']}):
        (drawings/f"fastener-{screw_id}.svg").write_text(fastener_scene(plan,screw_id).svg(),encoding='utf-8')
    if pdf:
        from .pdf import write_workshop_pdf
        write_workshop_pdf(plan,directory/'workshop.pdf')


def export_plan(plan: dict, destination: str | Path, *, pdf: bool = False):
    destination=Path(destination)
    if destination.exists() or destination.is_symlink():
        raise PlanError(f"Output already exists: {destination}. Use a new folder; existing work is never overwritten.")
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.sleeperplan-',dir=destination.parent))
    try:
        _populate(plan,temp,pdf)
        # rename refuses a non-empty destination on supported systems; existence checked above.
        if destination.exists():
            raise PlanError(f"Output appeared while building: {destination}")
        temp.rename(destination)
    except Exception:
        shutil.rmtree(temp,ignore_errors=True)
        raise
