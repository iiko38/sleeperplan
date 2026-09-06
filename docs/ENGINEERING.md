# Geometry contract, workshop conventions and limits

## One coordinate model

Each bed has its own local XYZ origin at its outside S/W bottom corner. S/N are labels, not compass directions. X follows the nominal long side; Y follows the other side; Z is height. S/N members are placed in +X; W/E members in +Y. All actual geometry uses positioned rectangular solids.

For outside length L, outside width W and wall thickness t:

- Odd alternating courses: S/N lengths L, W/E lengths W - 2t.
- Even alternating courses: S/N lengths L - 2t, W/E lengths W.
- Clear opening: (L - 2t) x (W - 2t).
- Top height: course count x course height.
- Fill volume: clear length x clear width x (height - freeboard), divided by 1,000,000 for litres.

The nominal profile is uniform across every piece. Edge/flat changes the section orientation, not its material. The photograph is inspiration only: no dimensions or buildable corner arrangement have been reverse-engineered from its perspective.

The compiler checks the expected ring area, absence of timber overlap and bed envelope for every course. Drawings never calculate a different length independently. Piece IDs include design, instance, course and side.

## Saw geometry

Every cutting stock item has gross length G, total start/end removals a/b, and kerf k. Usable length U = G - a - b. Trims include their kerf and are either zero or at least k. All cut coordinates are relative to the original stock datum A, before trimming.

A pattern containing n finished pieces with total finished length S is feasible precisely when:

```
S + k*(n-1) == U       # final piece reaches usable stock end: n-1 cuts
or
S + k*n <= U           # a final cut is made: n cuts
```

This is intentionally conservative about edge shaving. It does not assume that a terminal sliver narrower than k can be removed safely with a partially overhanging blade. A sound full-stock piece needs zero crosscuts. A full crosscut through a sleeper may need multiple tool passes; tool capacity and technique are not selected by this code.

Every board must conserve material:

```
gross length = finished parts + retained/discarded tail + complete trims + kerf from part-separating cuts
```

Actual dimensions, timber movement, knots, splits and blade wander can invalidate a nominal plan. Measure and regenerate; do not quietly shorten a component. To allow squaring of a nominal 2,400 mm sleeper, set the actual end removals and choose a feasible footprint. Full-length sides at 2,400 mm assume genuinely usable ends and adequate measured stock length.

The optimiser is exact for its encoded linear-stock/crosscut problem when `optimality_proven` is true. It is not optimising manufacturing time, tool changes, defects, grain, moisture, delivery charges, bulk-price tiers or a speculative resale value of offcuts. Fixed delivery/collection and other costs belong in explicit extras. Store availability is unconfirmed unless quantities are entered after checking.

The search bound counts work deterministically. A completed dynamic programme proves the lowest lexicographic objective over the enumerated stock model. A budget-limited best-fit-decreasing fallback is marked heuristic and may cost more. Independent tests compare exact results against a separate subset-partition solver.

## Fixing geometry is not connection engineering

Corner screws enter the OUTER broad face of the full-through member at t/2 from each end, at one-quarter and three-quarters of the course height. They traverse t before entering end grain of the perpendicular member. These positions form a proposed regular marking pattern, not a Eurocode/manufacturer-certified joint detail.

Stack screws enter the TOP face, on the cross-section centreline, and traverse one course height into the course below. The routine identifies the actual receiver and checks the path. It moves upper-course entries to avoid lower screws and the corner screws. Where a shift enlarges a gap beyond the configured maximum, an intermediate entry is added rather than accepting the gap.

The starting rules are **editable shop-layout assumptions**:

| Rule | Starting value | Meaning / limitation |
|---|---:|---|
| Nominal minimum penetration | 50 mm | Includes screw point; does not establish effective thread engagement or holding capacity. |
| Far-face clearance | 20 mm | Keeps a nominal straight tip away from the opposite timber face. |
| Stack end clearance | 80 mm | Geometric distance from receiving/through member ends for stack fixings only. |
| Side clearance | 20 mm | Geometric cross-section clearance for stack paths. |
| Stack target end inset | 200 mm | Increased when necessary for the section/end-clearance rule. |
| Stack maximum spacing | 600 mm | Layout rule, not proof of resistance to soil pressure. |
| Additional shaft separation | 12 mm | Added to both shaft radii for idealised path collision checks; not a full swept-tool or hardware-head model. |

For two perpendicular or parallel axis-aligned screw segments, minimum segment separation is computed from their interval separations on X/Y/Z. This is exact for these straight, axis-aligned paths. It does not model angled driving, large/irregular heads, countersinks, clamps, drill body access, dimensional tolerances or timber displacement. The installer must check these before execution.

The actual fastener selection must be suitable for treated timber, exterior exposure, end-grain withdrawal, loading and the full site. Manufacturer guidance and competent review take precedence over these geometric defaults. Brackets/posts/through-bolts or other supports may be required; this version does not design or draw them. Their materials and labour must be priced explicitly and their installation detail recorded separately.

**Pilot diameter and depth are not inferred.** The selected Wickes product pages did not establish those values. Confirm them against the actual product/timber and record the evidence. A recorded no-pilot instruction is distinct from an unknown pilot instruction. The release gate enforces that distinction, but cannot verify the truth of a human's evidence.

## Site and material limits

The executable v1 design envelope is a rectangular open-bottom flower bed on level ground, no mid-side splices and a reviewed-output height not above 600 mm. The software can draft higher alternatives to demonstrate why review is blocked. The envelope is a scope choice, not proof that every bed inside it is safe.

No structural design is supplied for retaining slopes, roofs/decks, hard surfaces, foundations, lateral loads, soil pressure, posts/bracing, accessibility, buried services or a load-bearing use. No guarantee of timber warranty after cutting is made. The cited Wickes timber instructions say to preserve cut ends, so follow the compatible treatment supplier's method. Follow tool and PPE instructions and assess safe lifting/transport; the stock can be heavy and wet timber weight varies.

Drainage is site-specific. A liner/protection layer must not create an undrained basin. RHS guidance distinguishes construction on hard surfaces; v1 refuses to release that site type because it has not implemented those drainage details. Fill calculations deliberately stop at cavity geometry and do not invent soil recipes, density-based bulk-bag conversions, settlement percentages or planting choices.

The “centre reach over 650 mm” warning is a user-fit prompt only; it is not an accessibility standard. A decorative bed with planting access around it differs from a productive bed worked from one side. Confirm the actual use and reach.

## Release and physical validation

All included examples are drafts. The three review flags plus reviewer/date/notes record that measurements, site/supports and fixings have been checked. `--release` requires them and confirmed pilot specifications, and refuses unsupported sites/heights. This is a workflow gate, not professional certification. Editing a reviewed job does not make its old review applicable to the new design; renew the review after every meaningful change. Height comparison resets reviews automatically.

For the first real bed, use a controlled trial: measure stock/kerf; verify a full-size course; check the saw sequence against one physical board; confirm the exact pilot/driver setup and connection with a competent builder or supplier; then compare the installed course to the drawing. Verify supports and drainage before filling. Record changes and make regression tests before standardising a sellable kit.

Future development should follow failures found in that process. Likely useful extensions are a properly specified support/bracing module, surveyed site constraints, actual-vs-estimated labour, material valuation, price import and manufacturing jigs. A storefront is not needed to validate any of those fundamentals.
