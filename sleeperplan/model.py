"""Typed domain objects. Rectangular solids, not a second set of drawing dimensions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


class PlanError(ValueError):
    """An invalid, infeasible or unsupported input. Safe to show to an operator."""


@dataclass(frozen=True)
class Profile:
    key: str
    thickness_mm: int
    height_mm: int
    description: str


@dataclass(frozen=True)
class Stock:
    id: str
    length_mm: int
    price_pence: int
    quantity: int | None = None  # None = purchasable; not a claim of store availability.
    inventory: bool = False
    trim_start_mm: int = 0  # TOTAL removed, including the trimming cut's kerf.
    trim_end_mm: int = 0
    source_url: str = ""
    checked_on: str = ""
    weight_grams: int | None = None

    @property
    def usable_mm(self) -> int:
        return self.length_mm - self.trim_start_mm - self.trim_end_mm


@dataclass(frozen=True)
class Screw:
    id: str
    length_mm: int
    diameter_mm: int
    pack_size: int
    pack_price_pence: int
    source_url: str
    checked_on: str
    # 'unconfirmed' is intentional. Never derive a drill diameter from screw diameter.
    pilot_mode: str = "unconfirmed"
    pilot_diameter_mm: float | None = None
    pilot_depth_mm: int | None = None
    pilot_evidence: str = ""


@dataclass(frozen=True)
class Rules:
    kerf_mm: int = 3
    reusable_offcut_min_mm: int = 300
    minimum_penetration_mm: int = 50  # Geometric penetration, NOT rated thread embedment.
    far_face_clearance_mm: int = 20
    end_clearance_mm: int = 80
    side_clearance_mm: int = 20
    stack_end_inset_mm: int = 200
    stack_max_spacing_mm: int = 600
    metal_clearance_mm: int = 12  # Extra clearance between idealised screw shafts.
    screw_spares_percent: int = 10
    max_search_steps: int = 300000
    price_max_age_days: int = 30


@dataclass(frozen=True)
class Bed:
    id: str
    length_mm: int
    width_mm: int
    courses: int
    quantity: int = 1
    corner_pattern: str = "alternating"
    freeboard_mm: int = 50
    access_sides: int = 2
    site_type: str = "level_open_ground"


@dataclass(frozen=True)
class Job:
    name: str
    profile: Profile
    beds: tuple[Bed, ...]
    stocks: tuple[Stock, ...]
    screws: tuple[Screw, ...]
    rules: Rules
    costs: dict[str, Any]
    review: dict[str, Any]
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Piece:
    id: str
    bed_id: str
    course: int
    side: str  # S/N run in +X; W/E run in +Y.
    axis: str
    x_mm: int
    y_mm: int
    z_mm: int
    length_mm: int
    thickness_mm: int
    height_mm: int
    through_at_corners: bool

    @property
    def box(self) -> tuple[tuple[float, float], ...]:
        dx, dy = ((self.length_mm, self.thickness_mm) if self.axis == "X"
                  else (self.thickness_mm, self.length_mm))
        return ((self.x_mm, self.x_mm + dx), (self.y_mm, self.y_mm + dy),
                (self.z_mm, self.z_mm + self.height_mm))

    def local(self, xyz: tuple[float, float, float]) -> tuple[float, float, float]:
        x, y, z = xyz
        if self.axis == "X":
            return x - self.x_mm, y - self.y_mm, z - self.z_mm
        return y - self.y_mm, x - self.x_mm, z - self.z_mm

    def world(self, u: float, v: float, w: float) -> tuple[float, float, float]:
        if self.axis == "X":
            return self.x_mm + u, self.y_mm + v, self.z_mm + w
        return self.x_mm + v, self.y_mm + u, self.z_mm + w


@dataclass(frozen=True)
class Fixing:
    id: str
    bed_id: str
    course: int
    piece_id: str
    receiver_id: str
    kind: str
    entry_face: str  # 'outer' or 'top'
    entry_mm: tuple[float, float, float]
    direction: tuple[int, int, int]
    local_mm: tuple[float, float, float]
    screw_id: str
    screw_length_mm: int
    diameter_mm: int
    through_mm: int
    penetration_mm: int
    pilot_mode: str
    pilot_diameter_mm: float | None
    pilot_depth_mm: int | None

    @property
    def tip_mm(self) -> tuple[float, float, float]:
        return tuple(a + self.screw_length_mm * d
                     for a, d in zip(self.entry_mm, self.direction))  # type: ignore[return-value]
