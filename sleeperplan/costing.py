"""Integer-pence procurement costing. Unknown is null, never zero."""
from __future__ import annotations
from collections import Counter
from .model import Fixing, Job

REQUIRED_EXTRAS = {
    "site_preparation": "Ground preparation / bedding / disposal",
    "supports": "Site-specific stakes, bracing, brackets and their fixings",
    "preservative": "Compatible cut-end preservative",
    "liner": "Liner / protection and attachment (or explicitly not required)",
    "fill": "Soil / compost / mulch supply",
    "transport": "Collection / delivery / travel",
    "consumables": "Drill bits, blades, PPE and other consumables",
}


def pounds(pence: int | None) -> str:
    return "UNPRICED" if pence is None else f"GBP {pence//100:,}.{pence%100:02d}"


def cost_job(job: Job, cut_plan: dict, fixings: list[Fixing]) -> dict:
    rows = []
    stocks = {s.id: s for s in job.stocks}
    stock_counts = Counter(b["stock_id"] for b in cut_plan["boards"])
    for sid, n in sorted(stock_counts.items()):
        s = stocks[sid]
        rows.append({"id": sid, "category": "inventory" if s.inventory else "timber",
                     "description": f"{s.length_mm} mm sleeper / matching section",
                     "needed": n, "buy_quantity": 0 if s.inventory else n, "unit": "sleeper",
                     "spares": 0, "unit_price_pence": s.price_pence,
                     "line_pence": n*s.price_pence, "source_url": s.source_url,
                     "price_checked_on": s.checked_on})
    used = Counter(f.screw_id for f in fixings)
    screws = {s.id: s for s in job.screws}
    for sid, need in sorted(used.items()):
        s = screws[sid]
        with_spares = (need*(100+job.rules.screw_spares_percent)+99)//100
        packs = (with_spares+s.pack_size-1)//s.pack_size
        rows.append({"id": sid, "category": "screws",
                     "description": f"{s.diameter_mm} x {s.length_mm} mm screws; {s.pack_size}/pack",
                     "needed": need, "buy_quantity": packs, "unit": "pack",
                     "spares": packs*s.pack_size-need, "unit_price_pence": s.pack_price_pence,
                     "line_pence": packs*s.pack_price_pence,
                     "source_url": s.source_url, "price_checked_on": s.checked_on})
    extras = {e["id"]: e for e in job.costs.get("extras", [])}
    for eid, description in REQUIRED_EXTRAS.items():
        extras.setdefault(eid, {"id": eid, "description": description, "quantity": 1,
                                "unit": "job", "unit_price_pence": None})
    if cut_plan["inventory_pieces_used"]:
        extras.setdefault("inventory_value", {"id": "inventory_value",
            "description": "Value of existing timber consumed (cash purchase above is zero)",
            "quantity": 1, "unit": "job", "unit_price_pence": None})
    for eid, e in sorted(extras.items()):
        price = e["unit_price_pence"]
        rows.append({"id": eid, "category": "extra", "description": e["description"],
                     "needed": e["quantity"], "buy_quantity": e["quantity"], "unit": e["unit"],
                     "spares": 0, "unit_price_pence": price,
                     "line_pence": None if price is None else e["quantity"]*price,
                     "source_url": "", "price_checked_on": "", "note": e.get("note", "")})
    minutes, rate = job.costs.get("labour_minutes"), job.costs.get("labour_rate_pence_per_hour")
    labour = None if minutes is None or rate is None else (minutes*rate+30)//60
    rows.append({"id": "labour", "category": "labour", "description": "Labour (nearest penny, half-up)",
                 "needed": minutes, "buy_quantity": minutes, "unit": "minute",
                 "spares": 0, "unit_price_pence": None, "line_pence": labour,
                 "source_url": "", "price_checked_on": ""})
    missing = [r["id"] for r in rows if r["line_pence"] is None]
    known = sum(r["line_pence"] for r in rows if r["line_pence"] is not None)
    material = sum(r["line_pence"] for r in rows if r["category"] in ("timber", "screws"))
    margin = job.costs.get("target_margin_bps")
    target = None
    if not missing and margin is not None:
        denominator = 10000-margin
        target = (known*10000+denominator-1)//denominator
    return {"currency": "GBP", "basis": "Catalogue retail purchase prices as displayed; VAT is not recalculated. "
            "Explicit extras and labour are added on the same user-supplied basis. Not a tax invoice.",
            "rows": rows, "timber_and_screw_purchase_pence": material,
            "known_subtotal_pence": known, "complete_cost_pence": known if not missing else None,
            "unpriced_items": missing, "is_complete": not missing,
            "target_margin_bps": margin, "internal_target_price_pence": target,
            "pricing_note": "Margin target is suppressed until all required costs are supplied. "
            "Zero is an explicit decision that an item is not needed/already allowed, not a missing price."}
