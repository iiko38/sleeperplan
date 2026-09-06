"""Single pipeline: input -> solids -> fixing paths -> cut allocation -> cost -> artefacts."""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from datetime import date
from . import __version__
from .cutting import solve
from .costing import cost_job
from .geometry import compile_geometry
from .model import Job, PlanError


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def plan(job: Job, as_of: date | None = None, *, release: bool = False) -> dict:
    as_of = as_of or date.today()
    beds, pieces, fixings = compile_geometry(job)
    cuts = solve(pieces, job.stocks, job.rules)
    costs = cost_job(job, cuts, fixings)
    issues = []

    def issue(code: str, message: str, blocking: bool = False) -> None:
        issues.append({"code": code, "blocking": blocking, "message": message})

    for flag, msg in {
        "timber_and_kerf_measured": "Measure actual stock length/section, usable ends and saw kerf; update inputs before cutting.",
        "site_and_supports_reviewed": "Review foundations, drainage, soil loads, support/bracing and any buried services on site.",
        "fixing_schedule_reviewed": "Review screw suitability, end-grain connections, penetration and spacing with a competent builder / supplier.",
    }.items():
        if not job.review.get(flag, False):
            issue(flag, msg, True)
    if not job.review.get("reviewer") or not job.review.get("reviewed_on") or not job.review.get("notes"):
        issue("review_record", "Record reviewer, reviewed_on and review notes before releasing a workshop pack.", True)
    elif date.fromisoformat(job.review["reviewed_on"]) > as_of:
        issue("future_review", "Review date is after the plan's as-of date.", True)
    used_screws = {f.screw_id for f in fixings}
    for s in job.screws:
        if s.id in used_screws and s.pilot_mode == "unconfirmed":
            issue("pilot_unconfirmed", f"{s.id}: fixing centres are mark-out only. Confirm pilot diameter/depth "
                  "or a manufacturer-supported no-pilot instruction; none is inferred.", True)
    for b in beds:
        if b["site_type"] != "level_open_ground":
            issue("unsupported_site", f"{b['id']}: {b['site_type']} is outside v1's level, open-bottom flower-bed scope.", True)
        if b["height_mm"] > 600:
            issue("height_scope", f"{b['id']}: above the 600 mm v1 scope limit (not a claimed safe-height threshold).", True)
        if b["corner_pattern"] != "alternating" and b["courses"] > 1:
            issue("aligned_corners", f"{b['id']}: same corner arrangement on every course. Deliberately not interlocked; review the connection.")
        reach = b["width_mm"]/b["access_sides"]
        if reach > 650:
            issue("reach", f"{b['id']}: centre reach is approximately {reach:g} mm from {b['access_sides']} accessible side(s); confirm with the user. "
                  "650 mm is a planning prompt, not an accessibility standard.")
    used_stock = {b["stock_id"] for b in cuts["boards"]}
    for product in (*job.stocks, *job.screws):
        if product.id not in used_stock | used_screws or not product.checked_on:
            continue
        age = (as_of-date.fromisoformat(product.checked_on)).days
        if age < 0:
            issue("future_price", f"{product.id}: catalogue price date is after this plan's as-of date.")
        elif age > job.rules.price_max_age_days:
            issue("stale_price", f"{product.id}: price snapshot is {age} days old; recheck it before purchasing.")
    if any(s.trim_start_mm == 0 or s.trim_end_mm == 0 for s in job.stocks if s.id in used_stock):
        issue("factory_ends", "Zero end trim assumes square, sound, usable factory/cut ends. Nominal 2400 mm is not a measurement.")
    if not cuts["optimality_proven"]:
        issue("heuristic_cutting", cuts["reason"])
    if not costs["is_complete"]:
        issue("incomplete_cost", "Known subtotal only; unpriced: " + ", ".join(costs["unpriced_items"]))
    issue("supply", "Catalogue prices are dated snapshots. The configured store and collection stock are NOT confirmed.")
    issue("not_structural", "Geometry and straight screw-path clearance are checked; timber strength, screw capacity, long-term movement and soil pressure are NOT calculated. "
          "Supports/bracing, liner detailing and foundations are site-specific and not drawn by v1.")
    blockers = [i for i in issues if i["blocking"]]
    if release and blockers:
        raise PlanError("Workshop release blocked:\n" + "\n".join("- "+i["message"] for i in blockers))
    input_record = {"job": asdict(job), "as_of": as_of.isoformat(), "generator_version": __version__}
    fingerprint = hashlib.sha256(canonical(input_record)).hexdigest()
    stock_counts = Counter(b["stock_id"] for b in cuts["boards"] if b["inventory"])
    next_inventory = []
    for s in job.stocks:
        if s.inventory and s.quantity is not None and s.quantity-stock_counts[s.id] > 0:
            d = asdict(s)
            d.pop("inventory")
            d["quantity"] = s.quantity-stock_counts[s.id]
            next_inventory.append(d)
    for b in cuts["boards"]:
        if b["keep_offcut"]:
            next_inventory.append({"id": f"off-{fingerprint[:8]}-{b['id']}", "length_mm": b["offcut_mm"],
                                   "price_pence": 0, "quantity": 1, "trim_start_mm": 0, "trim_end_mm": 0})
    known_weight = sum((s.weight_grams or 0)*sum(b["stock_id"] == s.id for b in cuts["boards"])
                       for s in job.stocks if not s.inventory)
    weight_complete = all(s.weight_grams is not None for s in job.stocks if s.id in used_stock and not s.inventory)
    return {"schema_version": 1, "generator_version": __version__, "input_sha256": fingerprint,
            "as_of": as_of.isoformat(), "name": job.name,
            "status": "REVIEWED_WORKSHOP_PLAN" if release else "DRAFT_MARK_OUT_ONLY",
            "review_gate_clear": not blockers, "issues": issues, "input": input_record,
            "profile": asdict(job.profile), "beds": beds, "pieces": [asdict(p) for p in pieces],
            "fixings": [asdict(f) for f in fixings], "cut_plan": cuts, "costs": costs,
            "total_fill_litres": round(sum(b["fill_litres"] for b in beds), 3),
            "catalogue_timber_collection_weight_kg": known_weight/1000 if weight_complete else None,
            "inventory_proposal": {"apply_only_after_job_completed": True,
                "profile_key": job.profile.key, "section_mm": sorted([job.profile.thickness_mm, job.profile.height_mm]),
                "source_plan_sha256": fingerprint, "consumed": dict(stock_counts), "inventory": next_inventory}}
