"""Bounded exact cutting-stock solver with finite offcuts and a labelled fallback.

The model makes full-width crosscuts. A terminal sliver smaller than the blade's
kerf is NOT quietly accepted as an edge-shaving operation. A final piece ending
exactly at a sound stock end needs no extra cut. End trims include their kerf.
"""
from __future__ import annotations
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from .model import Piece, PlanError, Rules, Stock


class SearchLimit(Exception):
    pass


@dataclass
class Budget:
    limit: int
    used: int = 0

    def tick(self) -> None:
        self.used += 1
        if self.used > self.limit:
            raise SearchLimit


def pattern_fits(lengths: list[int] | tuple[int, ...], stock: Stock, kerf: int) -> bool:
    if not lengths:
        return False
    n, total = len(lengths), sum(lengths)
    return total + kerf*(n-1) == stock.usable_mm or total + kerf*n <= stock.usable_mm


def enumerate_patterns(lengths: tuple[int, ...], demand: tuple[int, ...], stock: Stock,
                       kerf: int, budget: Budget) -> list[tuple[int, ...]]:
    out = []

    def walk(i: int, counts: tuple[int, ...], total: int, n: int) -> None:
        budget.tick()
        if i == len(lengths):
            if n and (total + kerf*(n-1) == stock.usable_mm or total + kerf*n <= stock.usable_mm):
                out.append(counts)
            return
        max_count = min(demand[i], (stock.usable_mm+kerf-total-kerf*n)//(lengths[i]+kerf))
        for count in range(max_count, -1, -1):
            walk(i+1, counts+(count,), total+count*lengths[i], n+count)

    walk(0, (), 0, 0)
    return sorted(out, key=lambda p: (-sum(a*b for a, b in zip(p, lengths)), p))


def score_selection(selection: list[tuple[int, tuple[int, ...]]], stocks: list[Stock]) -> tuple[int, int, int]:
    return (sum(stocks[i].price_pence for i, _ in selection),
            sum(not stocks[i].inventory for i, _ in selection),
            sum(stocks[i].length_mm for i, _ in selection))


def greedy(lengths: tuple[int, ...], demand: tuple[int, ...], stocks: list[Stock], kerf: int) -> list[tuple[int, tuple[int, ...]]]:
    """A valid best-fit-decreasing fallback; no optimality or infeasibility claim."""
    remaining = [s.quantity for s in stocks]
    bins: list[tuple[int, list[int]]] = []
    for li, count in enumerate(demand):
        for _ in range(count):
            candidates = []
            for bi, (si, content) in enumerate(bins):
                ls = [lengths[j] for j in content+[li]]
                if pattern_fits(ls, stocks[si], kerf):
                    candidates.append((stocks[si].usable_mm-sum(ls), bi))
            if candidates:
                _, bi = min(candidates)
                bins[bi][1].append(li)
                continue
            choices = [i for i, s in enumerate(stocks)
                       if remaining[i] != 0 and pattern_fits([lengths[li]], s, kerf)]
            if not choices:
                raise PlanError("Search budget exhausted and the greedy fallback could not find a feasible "
                                "plan. Increase max_search_steps or review available stock; infeasibility is NOT proven.")
            si = min(choices, key=lambda i: (stocks[i].price_pence, stocks[i].length_mm, stocks[i].id))
            bins.append((si, [li]))
            if remaining[si] is not None:
                remaining[si] -= 1
    result = []
    for si, content in bins:
        counts = Counter(content)
        result.append((si, tuple(counts[i] for i in range(len(lengths)))))
    return result


def solve(pieces: list[Piece], stocks: list[Stock] | tuple[Stock, ...], rules: Rules) -> dict:
    if not pieces:
        raise PlanError("No pieces to cut")
    stocks = sorted((s for s in stocks if s.quantity != 0), key=lambda s: (not s.inventory, s.price_pence, s.id))
    counts = Counter(p.length_mm for p in pieces)
    lengths = tuple(sorted(counts, reverse=True))
    demand = tuple(counts[L] for L in lengths)
    if not stocks:
        raise PlanError("No available stock")
    for L in lengths:
        if not any(pattern_fits([L], s, rules.kerf_mm) for s in stocks):
            raise PlanError(f"Cannot produce an uninterrupted {L} mm piece from the configured stock "
                            "after end trims/kerf. Change dimensions or add longer suitable stock; "
                            "v1 never invents a mid-side splice.")
    budget = Budget(rules.max_search_steps)
    algorithm, reason = "exact", "All explored cutting patterns and inventory states solved."
    try:
        patterns = [enumerate_patterns(lengths, demand, s, rules.kerf_mm, budget) for s in stocks]
        initial_available = tuple(-1 if s.quantity is None else s.quantity for s in stocks)
        choices: dict[tuple, tuple[int, tuple[int, ...]]] = {}

        @lru_cache(maxsize=None)
        def dp(need: tuple[int, ...], available: tuple[int, ...]) -> tuple[int, int, int] | None:
            budget.tick()
            if not any(need):
                return (0, 0, 0)
            anchor = next(i for i, n in enumerate(need) if n)
            best = None
            for si, options in enumerate(patterns):
                if available[si] == 0:
                    continue
                for pattern in options:
                    budget.tick()
                    if not pattern[anchor] or any(p > n for p, n in zip(pattern, need)):
                        continue
                    next_need = tuple(n-p for n, p in zip(need, pattern))
                    av = list(available)
                    if av[si] > 0:
                        av[si] -= 1
                    child = dp(next_need, tuple(av))
                    if child is None:
                        continue
                    s = stocks[si]
                    cost = (child[0]+s.price_pence, child[1]+int(not s.inventory), child[2]+s.length_mm)
                    if best is None or cost < best:
                        best = cost
                        choices[(need, available)] = (si, pattern)
            return best

        optimum = dp(demand, initial_available)
        if optimum is None:
            raise PlanError("No feasible cutting plan with the configured finite stock quantities")
        selection = []
        need, available = demand, initial_available
        while any(need):
            si, pattern = choices[(need, available)]
            selection.append((si, pattern))
            need = tuple(n-p for n, p in zip(need, pattern))
            av = list(available)
            if av[si] > 0:
                av[si] -= 1
            available = tuple(av)
    except SearchLimit:
        algorithm = "heuristic"
        reason = "Deterministic search budget reached. Valid greedy fallback; lowest cost is NOT proven."
        selection = greedy(lengths, demand, stocks, rules.kerf_mm)
    pools: dict[int, deque] = defaultdict(deque)
    for p in sorted(pieces, key=lambda p: p.id):
        pools[p.length_mm].append(p)
    boards = []
    for board_number, (si, pattern) in enumerate(selection, 1):
        allocated = [pools[L].popleft() for L, n in zip(lengths, pattern) for _ in range(n)]
        boards.append(layout_board(stocks[si], allocated, rules, f"B{board_number:03d}"))
    if any(pools.values()):
        raise PlanError("Internal error: cut plan omitted a part")
    allocation = [part["piece_id"] for b in boards for part in b["parts"]]
    if sorted(allocation) != sorted(p.id for p in pieces):
        raise PlanError("Internal error: cut allocation is not one-to-one")
    return {"algorithm": algorithm, "optimality_proven": algorithm == "exact", "reason": reason,
            "search_steps": budget.used, "objective": "purchase pence, then purchased sleeper count, then total input length",
            "boards": boards, "timber_purchase_pence": sum(b["price_pence"] for b in boards),
            "purchased_sleepers": sum(not b["inventory"] for b in boards),
            "inventory_pieces_used": sum(b["inventory"] for b in boards),
            "saw_cuts": sum(len(b["cuts"]) for b in boards),
            "finished_length_mm": sum(p.length_mm for p in pieces),
            "input_length_mm": sum(b["gross_length_mm"] for b in boards),
            "offcut_length_mm": sum(b["offcut_mm"] for b in boards),
            "kerf_and_trim_loss_mm": sum(b["kerf_and_trim_loss_mm"] for b in boards)}


def layout_board(stock: Stock, pieces: list[Piece], rules: Rules, board_id: str) -> dict:
    if not pattern_fits([p.length_mm for p in pieces], stock, rules.kerf_mm):
        raise PlanError("Internal error: invalid cutting pattern")
    k, start, end = rules.kerf_mm, stock.trim_start_mm, stock.length_mm-stock.trim_end_mm
    parts, cuts = [], []

    def cut(lo: int, hi: int, operation: str, piece_id: str = "") -> None:
        cuts.append({"sequence": len(cuts)+1, "operation": operation, "piece_id": piece_id,
                     "kerf_start_mm": lo, "kerf_end_mm": hi, "blade_centre_mm": (lo+hi)/2})

    if stock.trim_start_mm:
        cut(start-k, start, "square datum end A")
    if stock.trim_end_mm:
        cut(end, end+k, "square far end")
    cursor = start
    for p in pieces:
        stop = cursor+p.length_mm
        parts.append({"piece_id": p.id, "length_mm": p.length_mm,
                      "start_mm": cursor, "end_mm": stop, "cut_required": stop != end})
        if stop == end:
            cursor = end
        else:
            cut(stop, stop+k, "crosscut; keep piece on datum side", p.id)
            cursor = stop+k
    offcut = end-cursor
    loss = stock.trim_start_mm+stock.trim_end_mm + sum(c["kerf_end_mm"]-c["kerf_start_mm"]
                                                         for c in cuts if c["piece_id"])
    if sum(p.length_mm for p in pieces) + offcut + loss != stock.length_mm or offcut < 0:
        raise PlanError("Internal error: board material conservation failed")
    return {"id": board_id, "stock_id": stock.id, "inventory": stock.inventory,
            "gross_length_mm": stock.length_mm, "trim_start_mm": stock.trim_start_mm,
            "trim_end_mm": stock.trim_end_mm, "price_pence": stock.price_pence,
            "source_url": stock.source_url, "parts": parts, "cuts": cuts,
            "offcut_start_mm": cursor, "offcut_mm": offcut,
            "keep_offcut": offcut >= rules.reusable_offcut_min_mm,
            "kerf_and_trim_loss_mm": loss}
