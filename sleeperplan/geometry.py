"""Compile a rectangular frame into positioned solids and collision-checked fixing paths.

This is geometric validation, not a timber connection / soil-pressure calculation.
Every schedule requires site-specific human review before it is used for construction.
"""
from __future__ import annotations
from math import ceil, sqrt
from .model import Bed, Fixing, Job, Piece, PlanError, Screw


def bed_pieces(bed: Bed, bed_id: str, t: int, h: int) -> list[Piece]:
    pieces = []
    L, W = bed.length_mm, bed.width_mm
    for course in range(1, bed.courses + 1):
        long_through = bed.corner_pattern == "long_through" or course % 2 == 1
        z = (course - 1) * h
        if long_through:
            positions = [("S", "X", 0, 0, L, True), ("N", "X", 0, W-t, L, True),
                         ("W", "Y", 0, t, W-2*t, False), ("E", "Y", L-t, t, W-2*t, False)]
        else:
            positions = [("S", "X", t, 0, L-2*t, False), ("N", "X", t, W-t, L-2*t, False),
                         ("W", "Y", 0, 0, W, True), ("E", "Y", L-t, 0, W, True)]
        for side, axis, x, y, length, through in positions:
            pieces.append(Piece(f"{bed_id}-C{course}-{side}", bed_id, course, side,
                                axis, x, y, z, length, t, h, through))
    validate_frame(bed, pieces, t, h)
    return pieces


def validate_frame(bed: Bed, pieces: list[Piece], t: int, h: int) -> None:
    expected_area = bed.length_mm * bed.width_mm - (bed.length_mm-2*t)*(bed.width_mm-2*t)
    for course in range(1, bed.courses + 1):
        layer = [p for p in pieces if p.course == course]
        if len(layer) != 4 or sum(p.length_mm * t for p in layer) != expected_area:
            raise PlanError("Internal error: layer does not cover the rectangular ring exactly")
        for i, a in enumerate(layer):
            for b in layer[i+1:]:
                if all(min(aa[1], bb[1]) > max(aa[0], bb[0])
                       for aa, bb in zip(a.box, b.box)):
                    raise PlanError(f"Overlapping timber: {a.id} and {b.id}")
        for p in layer:
            for (lo, hi), limit in zip(p.box, (bed.length_mm, bed.width_mm, bed.courses*h)):
                if not 0 <= lo < hi <= limit:
                    raise PlanError(f"Piece outside bed envelope: {p.id}")


def contains(p: Piece, xyz: tuple[float, float, float], eps: float = 1e-6) -> bool:
    return all(lo-eps <= v <= hi+eps for v, (lo, hi) in zip(xyz, p.box))


def translated(xyz: tuple[float, float, float], direction: tuple[int, int, int],
               distance: float) -> tuple[float, float, float]:
    return tuple(v + distance*d for v, d in zip(xyz, direction))  # type: ignore[return-value]


def shaft_distance(a: Fixing, b: Fixing) -> float:
    """Exact segment distance for these axis-aligned segments (not arbitrary diagonals)."""
    distance2 = 0.0
    for a0, a1, b0, b1 in zip(a.entry_mm, a.tip_mm, b.entry_mm, b.tip_mm):
        alo, ahi = sorted((a0, a1))
        blo, bhi = sorted((b0, b1))
        gap = max(0.0, blo-ahi, alo-bhi)
        distance2 += gap * gap
    return sqrt(distance2)


def collide(a: Fixing, b: Fixing, clearance_mm: int) -> bool:
    return a.bed_id == b.bed_id and shaft_distance(a, b) < (a.diameter_mm+b.diameter_mm)/2 + clearance_mm - 1e-7


def select_screw(job: Job, through: int, receiver_depth: int) -> Screw:
    candidates = [s for s in job.screws
                  if through + job.rules.minimum_penetration_mm <= s.length_mm
                  <= through + receiver_depth - job.rules.far_face_clearance_mm]
    if not candidates:
        raise PlanError(f"No screw fits a {through} mm through-member and {receiver_depth} mm receiver: "
                        f"need at least {job.rules.minimum_penetration_mm} mm nominal penetration and "
                        f"{job.rules.far_face_clearance_mm} mm far-face clearance. Add suitable hardware.")
    # Hardware selection must be price-independent: repricing may never swap the
    # installed screw under an unchanged physical-design approval. Deterministic
    # spec order (length, then diameter, then ID) keeps the choice a function of
    # the approved physical catalogue only.
    return min(candidates, key=lambda s: (s.length_mm, s.diameter_mm, s.id))


def make_fixing(job: Job, p: Piece, pieces: list[Piece], point: tuple[float, float, float],
                direction: tuple[int, int, int], through: int, kind: str, number: int) -> Fixing:
    entry_to_receiver = translated(point, direction, through + 0.01)
    receivers = [q for q in pieces if q.id != p.id and contains(q, entry_to_receiver, 0)]
    if len(receivers) != 1:
        raise PlanError(f"{p.id}: fixing would enter a gap or an ambiguous joint")
    receiver = receivers[0]
    axis = next(i for i, d in enumerate(direction) if d)
    lo, hi = receiver.box[axis]
    receiver_depth = int(round(hi - lo))
    screw = select_screw(job, through, receiver_depth)
    tip = translated(point, direction, screw.length_mm)
    if not contains(p, translated(point, direction, 0.01), 0) or not contains(p, translated(point, direction, through-0.01), 0):
        raise PlanError(f"{p.id}: fixing leaves its through-member before reaching the joint")
    if not contains(receiver, tip, 0):
        raise PlanError(f"{p.id}: screw tip exits the intended receiving timber")
    # Every point of each axis-aligned segment is inside its convex member if both ends are.
    return Fixing(f"{p.id}-F{number:02d}", p.bed_id, p.course, p.id, receiver.id, kind,
                  "top" if kind == "stack" else "outer", point, direction, p.local(point),
                  screw.id, screw.length_mm, screw.diameter_mm, through, screw.length_mm-through,
                  screw.pilot_mode, screw.pilot_diameter_mm, screw.pilot_depth_mm)


def fixing_schedule(job: Job, pieces: list[Piece]) -> list[Fixing]:
    r = job.rules
    all_fixings: list[Fixing] = []
    sequence = {p.id: 0 for p in pieces}
    # Generate all corner paths FIRST, so vertical paths avoid both earlier and future corners.
    for p in pieces:
        if not p.through_at_corners:
            continue
        direction = {"S": (0, 1, 0), "N": (0, -1, 0), "W": (1, 0, 0), "E": (-1, 0, 0)}[p.side]
        outer_v = 0 if p.side in ("S", "W") else p.thickness_mm
        for u in (p.thickness_mm/2, p.length_mm-p.thickness_mm/2):
            for w in (p.height_mm/4, 3*p.height_mm/4):
                sequence[p.id] += 1
                f = make_fixing(job, p, pieces, p.world(u, outer_v, w), direction,
                                p.thickness_mm, "corner", sequence[p.id])
                if any(collide(f, old, r.metal_clearance_mm) for old in all_fixings):
                    raise PlanError(f"Corner screw collision at {f.id}; revise section/fixing design")
                all_fixings.append(f)
    for p in sorted(pieces, key=lambda q: (q.course, q.side)):
        if p.course == 1:
            continue
        inset = max(r.stack_end_inset_mm, p.thickness_mm+r.end_clearance_mm)
        # On a very short member a central stack fixing is the only geometric candidate.
        span = max(0, p.length_mm-2*inset)
        if span == 0:
            anchors = [p.length_mm/2]
        else:
            intervals = ceil(span/r.stack_max_spacing_mm)
            anchors = [inset + span*i/intervals for i in range(intervals+1)]
        accepted = []

        def place_stack(anchor: float) -> None:
            # Alternate first-choice offset to avoid driving into the screw in the layer below.
            shift = 40 if p.course % 2 == 1 else 0
            offsets = [shift, shift+20, shift-20, shift+40, shift-40, shift+60, shift-60, 0]
            found = None
            for off in dict.fromkeys(offsets):
                u = round(anchor + off, 3)
                if not r.end_clearance_mm <= u <= p.length_mm-r.end_clearance_mm:
                    continue
                try:
                    f = make_fixing(job, p, pieces, p.world(u, p.thickness_mm/2, p.height_mm),
                                    (0, 0, -1), p.height_mm, "stack", sequence[p.id]+1)
                except PlanError:
                    continue
                # Stay away from the receiving member's end, not merely the upper piece's end.
                receiver = next(q for q in pieces if q.id == f.receiver_id)
                ru, rv, _ = receiver.local(translated(f.entry_mm, f.direction, f.through_mm+1))
                if not (r.end_clearance_mm <= ru <= receiver.length_mm-r.end_clearance_mm
                        and r.side_clearance_mm <= rv <= receiver.thickness_mm-r.side_clearance_mm):
                    continue
                if not any(collide(f, old, r.metal_clearance_mm) for old in all_fixings):
                    found = f
                    break
            if found is None:
                raise PlanError(f"{p.id}: cannot place a clear stack fixing near u={anchor:.1f} mm; "
                                "revise hardware/layout, not the drawing alone")
            sequence[p.id] += 1
            all_fixings.append(found)
            accepted.append(found.local_mm[0])
        for anchor in anchors:
            place_stack(anchor)
        # Avoidance can enlarge a near-limit gap. Add an intermediate fixing instead
        # of claiming compliance or failing an otherwise ordinary rectangular bed.
        while True:
            accepted.sort()
            gap = next(((a, b) for a, b in zip(accepted, accepted[1:])
                        if b-a > r.stack_max_spacing_mm+1e-6), None)
            if gap is None:
                break
            if len(accepted) >= 200:
                raise PlanError(f"{p.id}: stack fixing pattern exceeded the v1 complexity limit")
            place_stack((gap[0]+gap[1])/2)
    return sorted(all_fixings, key=lambda f: (f.bed_id, f.course, f.piece_id, f.id))


def compile_geometry(job: Job) -> tuple[list[dict], list[Piece], list[Fixing]]:
    beds, pieces, fixings = [], [], []
    t, h = job.profile.thickness_mm, job.profile.height_mm
    for b in job.beds:
        for i in range(1, b.quantity+1):
            bed_id = f"{b.id}-{i:02d}"
            ps = bed_pieces(b, bed_id, t, h)
            fs = fixing_schedule(job, ps)
            inside_L, inside_W = b.length_mm-2*t, b.width_mm-2*t
            fill_mm3 = inside_L * inside_W * (b.courses*h-b.freeboard_mm)
            beds.append({"id": bed_id, "design_id": b.id, "length_mm": b.length_mm, "width_mm": b.width_mm,
                         "courses": b.courses, "height_mm": b.courses*h,
                         "inside_length_mm": inside_L, "inside_width_mm": inside_W,
                         "freeboard_mm": b.freeboard_mm, "fill_litres": round(fill_mm3/1_000_000, 3),
                         "inside_wall_area_m2": round(2*(inside_L+inside_W)*b.courses*h/1_000_000, 4),
                         "diagonal_mm": round(sqrt(b.length_mm**2+b.width_mm**2), 1),
                         "corner_pattern": b.corner_pattern, "site_type": b.site_type,
                         "access_sides": b.access_sides})
            pieces.extend(ps)
            fixings.extend(fs)
    return beds, pieces, fixings
