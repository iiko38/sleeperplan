"""Deterministic workshop operation schedule compiled from the same plan.

One ordered list of typed operations drives the web player and any printed
step pages, so prose can never drift from the geometry. Unknown physical
values (pilot spec, head seat) stay unknown: they appear as mark-out-only
or STOP operations, never as invented machining instructions.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass


ACTIONS = ("receive", "label", "cut", "treat", "place", "clamp", "mark", "drill", "drive", "supports", "final")


@dataclass(frozen=True)
class Operation:
    id: str
    action: str
    title: str
    detail: str
    bed_id: str | None
    course: int | None
    piece_ids: tuple[str, ...]
    fixing_id: str | None
    dependencies: tuple[str, ...]
    camera_hint: str  # overview | active-piece | joint-closeup


def _entry_face_text(entry_face: str, direction) -> str:
    if direction[2] != 0:
        return "vertically through the TOP face"
    return f"horizontally into the {entry_face.upper()} outer face"


def build_operations(plan: dict) -> list[Operation]:
    ops: list[Operation] = []

    def add(action: str, title: str, detail: str, *, bed_id=None, course=None,
            piece_ids=(), fixing_id=None, dependencies=(), camera="overview") -> str:
        op = Operation(f"op-{len(ops)+1:03d}", action, title, detail, bed_id, course,
                       tuple(piece_ids), fixing_id, tuple(dependencies), camera)
        ops.append(op)
        return op.id

    # 1. Receive, label and cut each stock board in allocation order.
    for b in plan["cut_plan"]["boards"]:
        piece_ids = tuple(part["piece_id"] for part in b["parts"])
        receive = add("receive", f"Receive and inspect {b['id']}",
                      f"{b['stock_id']} | gross {b['gross_length_mm']} mm | reject twisted, split or unsound stock. "
                      f"Trims: start {b['trim_start_mm']} mm, end {b['trim_end_mm']} mm.", piece_ids=piece_ids)
        label = add("label", f"Label {b['id']} and mark datum A",
                    f"Write board ID {b['id']} on the timber and mark datum A. All cut coordinates run from this "
                    f"original A datum, even after squaring.", piece_ids=piece_ids, dependencies=(receive,))
        prior = label
        for c in b["cuts"]:
            band = f"{c['kerf_start_mm']}..{c['kerf_end_mm']} mm"
            detail = (f"{c['operation']} at blade centre {c['blade_centre_mm']} mm from A. Kerf band {band} is WASTE - "
                      "do not centre the blade on a finished-length boundary. One complete crosscut through the section.")
            prior = add("cut", f"{c['operation'].capitalize()} {b['id']} @ {c['blade_centre_mm']} mm",
                        detail, piece_ids=(c["piece_id"],) if c["piece_id"] else (), dependencies=(prior,))
        add("treat", f"Treat cut ends of {b['id']}",
            "Apply the compatible cut-end preservative per the timber supplier's method before assembly.",
            piece_ids=piece_ids, dependencies=(prior,))

    # 2. Assemble course by course; every fixing gets its own mark/drill + drive.
    pieces_by_course: dict[tuple[str, int], list[dict]] = {}
    for p in plan["pieces"]:
        pieces_by_course.setdefault((p["bed_id"], p["course"]), []).append(p)
    fixings_by_course: dict[tuple[str, int], list[dict]] = {}
    for f in plan["fixings"]:
        fixings_by_course.setdefault((f["bed_id"], f["course"]), []).append(f)

    beds = {b["id"]: b for b in plan["beds"]}
    for (bed_id, course) in sorted(pieces_by_course, key=lambda k: (list(beds).index(k[0]), k[1])):
        course_pieces = sorted(pieces_by_course[(bed_id, course)], key=lambda p: p["id"])
        piece_ids = tuple(p["id"] for p in course_pieces)
        bed = beds[bed_id]
        place = add("place", f"Place {bed_id} course {course}",
                    f"Lay the course-{course} members for {bed_id} in the drawn positions "
                    f"(outside {bed['length_mm']} x {bed['width_mm']} mm).", bed_id=bed_id, course=course,
                    piece_ids=piece_ids)
        clamp = add("clamp", f"Clamp and check {bed_id} course {course}",
                    "Clamp the course, check square (equal outside diagonals) and level. Do not release the clamps "
                    "until this course's fixings are driven.", bed_id=bed_id, course=course,
                    piece_ids=piece_ids, dependencies=(place,), camera="active-piece")
        prior_drive = clamp
        for f in sorted(fixings_by_course.get((bed_id, course), []), key=lambda x: x["id"]):
            where = (f"{_entry_face_text(f['entry_face'], f['direction'])} at "
                     f"U {f['local_mm'][0]:g} / V {f['local_mm'][1]:g} / W {f['local_mm'][2]:g} mm from piece datum A "
                     f"({f['entry_mm'][0]:g}, {f['entry_mm'][1]:g}, {f['entry_mm'][2]:g} global).")
            if f["pilot_mode"] == "pilot":
                prepare = add("drill", f"Drill for {f['id']}",
                              f"{f['pilot_diameter_mm']:g} mm bit, {f['pilot_depth_mm']} mm deep from the entry face, "
                              f"along the fixed screw axis. " + where,
                              bed_id=bed_id, course=course, piece_ids=(f["piece_id"],), fixing_id=f["id"],
                              dependencies=(clamp,), camera="joint-closeup")
            else:
                prepare = add("mark", f"Mark out {f['id']} - STOP before drilling",
                              f"Pilot spec UNCONFIRMED: mark the centre only. Do NOT drill or drive until a recorded "
                              "trial or manufacturer instruction confirms diameter and depth. " + where,
                              bed_id=bed_id, course=course, piece_ids=(f["piece_id"],), fixing_id=f["id"],
                              dependencies=(clamp,), camera="joint-closeup")
            prior_drive = add("drive", f"Drive {f['id']} ({f['diameter_mm']} x {f['screw_length_mm']} mm)",
                              f"Drive {f['screw_id']} square to the entry face into receiver {f['receiver_id']}. "
                              f"Nominal penetration {f['penetration_mm']} mm (includes the point; not rated embedment). "
                              "Head seat: confirm against the actual hardware - heads and recesses are NOT modelled.",
                              bed_id=bed_id, course=course, piece_ids=(f["piece_id"],), fixing_id=f["id"],
                              dependencies=(prepare,), camera="joint-closeup")
        _ = prior_drive

    # 3. Supports, drainage and final checks.
    last = ops[-1].id if ops else None
    add("supports", "Install reviewed supports, liner and drainage",
        "Fit the separately reviewed restraint/bracing and protection details. Keep the base open-bottomed and "
        "drained; never turn the bed into an undrained tank.", dependencies=(last,) if last else ())
    add("final", "Final check and fill to freeboard",
        "Re-check level, square and all fixing seats. Fill to the specified freeboard. Record actual purchases, "
        "labour, corrections and useful offcuts; merge the inventory proposal only after the job is completed.",
        dependencies=(ops[-1].id,) if ops else ())
    return ops


def operations_document(plan: dict) -> dict:
    ops = build_operations(plan)
    return {"schema": "sleeperplan.operations.v1",
            "plan_sha256": plan["input_sha256"],
            "physical_design_hash": plan["physical_design_hash"],
            "status": plan["status"],
            "note": ("Compiled from the same geometry model as cuts.csv and fixings.csv. Pilot entries marked "
                     "STOP are mark-out only. Screw head seats are not modelled and require hardware confirmation."),
            "operations": [asdict(o) for o in ops]}
