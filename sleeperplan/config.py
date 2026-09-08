"""Strict input loading: typos, unknown units and unknown money must not pass silently."""
from __future__ import annotations
import json
import re
from dataclasses import fields
from datetime import date
from pathlib import Path
from typing import Any
from .model import Bed, Job, PlanError, Profile, Rules, Screw, Stock


def obj(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise PlanError(f"{label}: expected a JSON object")
    return value


def keys(data: dict, allowed: set[str], required: set[str], label: str) -> None:
    unknown, missing = set(data) - allowed, required - set(data)
    if unknown:
        raise PlanError(f"{label}: unknown fields {sorted(unknown)} (check spelling/units)")
    if missing:
        raise PlanError(f"{label}: missing fields {sorted(missing)}")


def integer(value: Any, label: str, minimum: int = 0, maximum: int = 10**9) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise PlanError(f"{label}: expected an integer between {minimum} and {maximum}")
    return value


def text(value: Any, label: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise PlanError(f"{label}: expected {'a' if allow_empty else 'a non-empty'} string")
    return value


def identifier(value: Any, label: str) -> str:
    s = text(value, label)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,39}", s):
        raise PlanError(f"{label}: use 1-40 letters, digits, underscores or hyphens")
    return s


def iso_date(value: Any, label: str) -> str:
    value = text(value, label)
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise PlanError(f"{label}: use YYYY-MM-DD") from exc
    return value


def read_json(path: Path) -> dict:
    try:
        return obj(json.loads(path.read_text(encoding="utf-8-sig")), str(path))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"Cannot read JSON {path}: {exc}") from exc


def list_of(value: Any, label: str, *, nonempty: bool = True) -> list:
    if not isinstance(value, list) or (nonempty and not value):
        raise PlanError(f"{label}: expected {'a non-empty' if nonempty else 'a'} list")
    return value


def unique(items: list, label: str) -> None:
    ids = [i.id for i in items]
    if len(ids) != len(set(ids)):
        raise PlanError(f"{label}: duplicate IDs")


def parse_stock(raw: dict, *, inventory: bool, rules: Rules) -> Stock:
    raw = obj(raw, "stock")
    allowed = {f.name for f in fields(Stock)} - {"inventory"}
    required = {"id", "length_mm"} | (set() if inventory else {"price_pence", "source_url", "checked_on"})
    keys(raw, allowed, required, "stock")
    d = dict(raw)
    d["id"] = identifier(d["id"], "stock.id")
    integer(d["length_mm"], "stock.length_mm", 1, 20000)
    d.setdefault("price_pence", 0)
    integer(d["price_pence"], "stock.price_pence", 0 if inventory else 1)
    if inventory and d["price_pence"] != 0:
        raise PlanError("Inventory is sunk purchase cost: set price_pence to 0")
    if inventory:
        d.setdefault("quantity", 1)
    if d.get("quantity") is not None:
        integer(d["quantity"], "stock.quantity", 0, 1000)
    if inventory and d.get("quantity") is None:
        raise PlanError("Inventory must have a finite quantity")
    for k in ("trim_start_mm", "trim_end_mm"):
        v = integer(d.get(k, 0), k, 0, d["length_mm"])
        if 0 < v < rules.kerf_mm:
            raise PlanError(f"{k} includes kerf; must be 0 or at least kerf_mm")
    if d.get("weight_grams") is not None:
        integer(d["weight_grams"], "stock.weight_grams", 1)
    if not inventory:
        iso_date(d["checked_on"], "stock.checked_on")
        text(d["source_url"], "stock.source_url")
    s = Stock(**d, inventory=inventory)
    if s.usable_mm <= 0:
        raise PlanError(f"Stock {s.id}: trims consume the entire sleeper")
    return s


def parse_screw(raw: dict) -> Screw:
    d = dict(obj(raw, "screw"))
    allowed = {f.name for f in fields(Screw)}
    required = {"id", "length_mm", "diameter_mm", "pack_size", "pack_price_pence", "source_url", "checked_on"}
    keys(d, allowed, required, "screw")
    identifier(d["id"], "screw.id")
    for k in ("length_mm", "diameter_mm", "pack_size", "pack_price_pence"):
        integer(d[k], f"screw.{k}", 1)
    if d["diameter_mm"] >= d["length_mm"]:
        raise PlanError("Screw diameter must be smaller than its length")
    iso_date(d["checked_on"], "screw.checked_on")
    text(d["source_url"], "screw.source_url")
    mode = d.get("pilot_mode", "unconfirmed")
    if mode not in ("unconfirmed", "pilot", "none"):
        raise PlanError("pilot_mode must be unconfirmed, pilot or none")
    evidence_kinds = ("fixture", "manufacturer_instruction", "recorded_trial")
    if mode in ("pilot", "none"):
        text(d.get("pilot_evidence"), "pilot_evidence: manufacturer instruction / recorded trial")
        kind = d.get("pilot_evidence_kind")
        if kind not in evidence_kinds:
            raise PlanError("pilot_evidence_kind must be one of: " + ", ".join(evidence_kinds)
                            + " (a fixture can never issue a workshop plan)")
    if mode == "pilot":
        diameter = d.get("pilot_diameter_mm")
        if isinstance(diameter, bool) or not isinstance(diameter, (int, float)) or not 0 < diameter < d["diameter_mm"]:
            raise PlanError("pilot_diameter_mm must be positive and smaller than screw diameter")
        integer(d.get("pilot_depth_mm"), "pilot_depth_mm", 1, d["length_mm"])
    elif d.get("pilot_diameter_mm") is not None or d.get("pilot_depth_mm") is not None:
        raise PlanError("Only pilot_mode='pilot' can specify a pilot diameter/depth")
    return Screw(**d)


def load_job(path: str | Path, catalogue_override: str | Path | None = None) -> Job:
    path = Path(path)
    raw = read_json(path)
    if catalogue_override is None:
        catalogue_path = path.parent / text(raw.get("catalogue"), "catalogue")
    else:
        catalogue_path = Path(catalogue_override)
    return parse_job(raw, read_json(catalogue_path))


def parse_job(raw: dict, cat: dict) -> Job:
    keys(raw, {"schema_version", "name", "catalogue", "orientation", "measured_section_mm", "beds", "rules", "inventory", "costs", "review", "notes"},
         {"schema_version", "name", "beds"}, "job")
    if raw["schema_version"] != 1 or type(raw["schema_version"]) is not int:
        raise PlanError("Unsupported job schema_version (expected 1)")
    keys(cat, {"schema_version", "profile", "stocks", "screws", "supplier_note"},
         {"schema_version", "profile", "stocks", "screws"}, "catalogue")
    if type(cat["schema_version"]) is not int or cat["schema_version"] != 1:
        raise PlanError("Unsupported catalogue schema_version")
    rd = obj(raw.get("rules", {}), "rules")
    keys(rd, {f.name for f in fields(Rules)}, set(), "rules")
    for k, v in rd.items():
        integer(v, k, 0 if k in {"screw_spares_percent", "metal_clearance_mm"} else 1,
                100 if k == "screw_spares_percent" else 10**7)
    rules = Rules(**rd)
    p = obj(cat["profile"], "profile")
    keys(p, {"key", "section_mm", "description"}, {"key", "section_mm", "description"}, "profile")
    section = raw.get("measured_section_mm", p["section_mm"])
    if not isinstance(section, list) or len(section) != 2:
        raise PlanError("section_mm / measured_section_mm must be [smaller_side, larger_side]")
    a, b = (integer(v, "section_mm", 40, 400) for v in section)
    if a > b:
        raise PlanError("section_mm must list smaller side first")
    orientation = raw.get("orientation", "edge")
    if orientation not in ("edge", "flat"):
        raise PlanError("orientation must be edge or flat")
    t, h = (a, b) if orientation == "edge" else (b, a)
    profile = Profile(identifier(p["key"], "profile.key"), t, h, text(p["description"], "profile.description"))
    if 2 * rules.side_clearance_mm >= min(t, h):
        raise PlanError("Section too small for the configured side clearances")
    beds = []
    for br in list_of(raw["beds"], "beds"):
        br = obj(br, "bed")
        keys(br, {f.name for f in fields(Bed)}, {"id", "length_mm", "width_mm", "courses"}, "bed")
        b = Bed(**br)
        identifier(b.id, "bed.id")
        for k in ("length_mm", "width_mm"):
            integer(getattr(b, k), k, 2 * t + 2 * rules.end_clearance_mm + 1, 20000)
        integer(b.courses, "courses", 1, 6)
        integer(b.quantity, "quantity", 1, 50)
        integer(b.freeboard_mm, "freeboard_mm", 0, b.courses * h - 1)
        if b.corner_pattern not in ("alternating", "long_through"):
            raise PlanError("corner_pattern must be alternating or long_through")
        if type(b.access_sides) is not int or b.access_sides not in (1, 2):
            raise PlanError("access_sides must be 1 or 2")
        if b.site_type not in ("level_open_ground", "hard_surface", "slope", "retaining", "roof_or_deck"):
            raise PlanError("Unknown site_type")
        beds.append(b)
    if sum(b.quantity * b.courses * 4 for b in beds) > 240:
        raise PlanError("v1 limits a batch to 240 pieces; split the batch")
    unique(beds, "beds")
    stocks = [parse_stock(s, inventory=False, rules=rules) for s in list_of(cat["stocks"], "stocks")]
    for inv in list_of(raw.get("inventory", []), "inventory", nonempty=False):
        stocks.append(parse_stock(inv, inventory=True, rules=rules))
    unique(stocks, "stocks/inventory")
    screws = [parse_screw(s) for s in list_of(cat["screws"], "screws")]
    unique(screws, "screws")
    costs = obj(raw.get("costs", {}), "costs")
    keys(costs, {"extras", "labour_minutes", "labour_rate_pence_per_hour", "target_margin_bps"}, set(), "costs")
    # Missing costs remain null. No invented free delivery or zero labour.
    for k in ("labour_minutes", "labour_rate_pence_per_hour"):
        if costs.get(k) is not None:
            integer(costs[k], k)
    if (costs.get("labour_minutes") is None) != (costs.get("labour_rate_pence_per_hour") is None):
        raise PlanError("Supply both labour_minutes and labour_rate_pence_per_hour, or neither")
    if costs.get("target_margin_bps") is not None:
        integer(costs["target_margin_bps"], "target_margin_bps", 0, 9900)
    seen = set()
    for extra in list_of(costs.get("extras", []), "extras", nonempty=False):
        obj(extra, "extra")
        keys(extra, {"id", "description", "quantity", "unit", "unit_price_pence", "note"},
             {"id", "description", "quantity", "unit", "unit_price_pence"}, "extra")
        eid = identifier(extra["id"], "extra.id")
        if eid in seen or eid in {"labour", "timber", "screws"}:
            raise PlanError(f"Duplicate or reserved extra ID: {eid}")
        seen.add(eid)
        text(extra["description"], "extra.description")
        text(extra["unit"], "extra.unit")
        integer(extra["quantity"], "extra.quantity", 1)
        if extra["unit_price_pence"] is not None:
            integer(extra["unit_price_pence"], "extra.unit_price_pence")
    review = obj(raw.get("review", {}), "review")
    flags = {"timber_and_kerf_measured", "site_and_supports_reviewed", "fixing_schedule_reviewed"}
    keys(review, flags | {"reviewer", "reviewed_on", "notes", "approved_physical_design_hash"}, set(), "review")
    for k in flags:
        if k in review and type(review[k]) is not bool:
            raise PlanError(f"review.{k} must be true or false")
    if "approved_physical_design_hash" in review:
        approved = review["approved_physical_design_hash"]
        if not (isinstance(approved, str) and len(approved) == 64
                and all(c in "0123456789abcdef" for c in approved)):
            raise PlanError("review.approved_physical_design_hash must be the 64-character lowercase hex SHA-256 "
                            "of the physical design, copied from a draft plan output")
    if review.get("reviewed_on"):
        iso_date(review["reviewed_on"], "reviewed_on")
    for k in ("reviewer", "notes"):
        if k in review:
            text(review[k], k, allow_empty=True)
    return Job(text(raw["name"], "name"), profile, tuple(beds), tuple(stocks), tuple(screws), rules,
               costs, review, {"supplier_note": cat.get("supplier_note", ""),
                               "orientation": orientation, "notes": raw.get("notes", "")})
