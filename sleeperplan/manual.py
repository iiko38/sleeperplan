"""IKEA-style assembly manual compiled from the deterministic operation schedule.

One dominant action per panel: a 3D keyframe (installed solid, active
highlighted, pending ghosted), the instruction text, and — for fixing
operations — a scaled joint cross-section. Panels are grouped so repeated,
equivalent fixings carry an explicit repeat count and the piece mark-out
sheet reference, instead of one page per screw.
"""
from __future__ import annotations
from dataclasses import dataclass

from .drawing import keyframe_scene, joint_closeup_scene
from .operations import build_operations


@dataclass(frozen=True)
class Panel:
    number: int
    title: str
    action: str
    lines: tuple[str, ...]
    scene: object            # keyframe Scene
    closeup: object | None   # joint cross-section Scene or None
    closeup_caption: str


def _wrap(text: str, width: int = 88) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 > width:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        lines.append(current)
    return lines


def _first_fixing(plan: dict, fixing_id: str | None) -> dict | None:
    if not fixing_id:
        return None
    return next((f for f in plan["fixings"] if f["id"] == fixing_id), None)


def build_manual_panels(plan: dict) -> list[Panel]:
    ops = build_operations(plan)
    panels: list[Panel] = []
    number = 0

    def emit(title: str, action: str, lines: list[str], installed: set, active: set,
             closeup=None, closeup_caption: str = "", fixing: str | None = None) -> None:
        nonlocal number
        number += 1
        panels.append(Panel(number, title, action, tuple(_wrap(" ".join(lines))),
                            keyframe_scene(plan, installed, active, fixing=fixing, width=540, height=400),
                            closeup, closeup_caption))

    installed: set = set()
    emitted_groups: set = set()
    seating_shown: set = set()

    # ---- stock preparation panels (one per board) ----
    for op in ops:
        if op.action == "receive":
            board_id = op.title.split()[-1]
            lines = [op.detail]
            for follow in ops:
                if follow.id <= op.id:
                    continue
                if follow.action in ("label", "treat") and follow.piece_ids == op.piece_ids:
                    lines.append(follow.detail)
            emit(f"Prepare board {board_id}", "receive", lines, installed, set(op.piece_ids))
        elif op.action == "cut":
            emit(op.title, "cut", [op.detail], installed, set(op.piece_ids))
            installed |= set(op.piece_ids)
        elif op.action == "place":
            emit(op.title, "place", [op.detail], installed, set(op.piece_ids))
        elif op.action == "clamp":
            emit(op.title, "clamp", [op.detail], installed, set(op.piece_ids))
            installed |= set(op.piece_ids)
        elif op.action in ("mark", "drill"):
            fixing = _first_fixing(plan, op.fixing_id)
            if fixing is None:
                continue
            key = (fixing["piece_id"], fixing["kind"], fixing["entry_face"])
            if key in emitted_groups:
                continue
            emitted_groups.add(key)
            group = [f for f in plan["fixings"]
                     if f["piece_id"] == fixing["piece_id"] and f["kind"] == fixing["kind"]
                     and f["entry_face"] == fixing["entry_face"]]
            mode = "drill" if op.action == "drill" else "mark"
            closeup = joint_closeup_scene(plan, fixing, mode)
            caption = ("Scaled section along the screw axis. "
                       f"All positions for this member: mark-out sheet {fixing['piece_id']}-fixings.svg.")
            lines = [op.detail]
            drive = next((o for o in ops if o.action == "drive" and o.fixing_id in
                          {f["id"] for f in group}), None)
            if drive:
                lines.append(drive.detail)
            if len(group) > 1:
                lines.append(f"Repeat identically at all {len(group)} {fixing['kind']} positions on this "
                             f"member (coordinates differ; preparation is identical).")
            emit(f"Fit {fixing['kind']} screws - {fixing['piece_id']}", op.action,
                 lines, installed, {fixing["piece_id"]}, closeup, caption, fixing=fixing["id"])
        elif op.action == "drive":
            # groups are rendered with their preparation step above; show the
            # seated/head detail once per fixing kind across the plan.
            fixing = _first_fixing(plan, op.fixing_id)
            if fixing is None:
                continue
            if fixing["kind"] not in seating_shown:
                seating_shown.add(fixing["kind"])
                closeup = joint_closeup_scene(plan, fixing, "drive")
                emit(f"Seated view - {fixing['kind']} screws", "drive",
                     ["This is how a correctly seated screw looks in section: head bearing on the entry face, "
                      "point inside the receiver. The head-seat detail must be confirmed with the actual "
                      "hardware before any course is stacked over driven screws."],
                     installed, {fixing["piece_id"]}, closeup,
                     "Seated view along the screw axis.", fixing=fixing["id"])
        elif op.action == "supports":
            installed_all = {p["id"] for p in plan["pieces"]}
            emit(op.title, "supports", [op.detail], installed_all, set())
        elif op.action == "final":
            installed_all = {p["id"] for p in plan["pieces"]}
            emit(op.title, "final", [op.detail], installed_all, set())

    return panels


def manual_document(plan: dict) -> dict:
    panels = build_manual_panels(plan)
    return {"schema": "sleeperplan.manual.v1",
            "plan_sha256": plan["input_sha256"],
            "physical_design_hash": plan["physical_design_hash"],
            "status": plan["status"],
            "panel_count": len(panels),
            "note": ("Compiled from the same operations schedule as the web player. "
                     "Pilot/head-seat entries marked CONFIRM/STOP need the actual hardware before drilling."),
            "panels": [{"number": p.number, "title": p.title, "action": p.action,
                        "lines": list(p.lines), "closeup_caption": p.closeup_caption} for p in panels]}
