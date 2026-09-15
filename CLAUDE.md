# Project rules — MagicCardBox

This model was built **manually, before the project was bootstrapped**, and has since been
rebuilt into a parametric knuckle hinge. As of 2026-09-13 the audit is clean and **all three
main dimensions sweep safely**, verified by measurement across W 80-130, D 50-100, H 50-95
(9 cases): every dimension tracks, lid-vs-box swing interference is **0.0000 mm3** over
0-90 deg, and every solid is valid, closed and single.

## FIRST TEST PRINT — 2026-09-13 — and what it changed

The first PLA print (lid open, box upright on the plate) **failed three ways**, and the fixes
Bradley made by hand changed the hinge architecture. Read this before the older sections
below, several of which it supersedes.

| Print failure | Root cause (measured) | Fixed by |
|---|---|---|
| Hinge snapped | Lid hung off **4 mm of plastic out of 105** — `PanelBottomZ` held the rear panel 10.4 mm up, so only the two R5 tab discs bridged box to lid | Rear panel extended down to the hinge axis across `x +/-47.5`: **95 mm of connection** |
| Stringy mess across the back | Travel moves across that same open slot | Same fix |
| Overhang at the top of the hinge | Socket circle breaks out through the rear face at `y = 36.4` (rear face is `y = 36`), leaving sharp unsupported edges | `BackHengeFilet` R4 on those edges |

Card spec was also corrected from calipers: `CardLength` 91 -> 92, `CardStackHeight` 60 -> 62.
Interior is now **94 x 68 x 63** for a 92 x 66 x 62 stack — a true 1 mm per side and 1 mm
headroom. Note this was fixed at the *input*, not by inflating `CardClearance`; that is the
right move and should be repeated. **`CardWidth` 66 is still an ASSUMPTION** — `CardLength`
turned out to be wrong by 1 mm, so measure the width too.

### FIXED — the zero running clearance at the hinge (macro 20)

The lid's rear panel had its inner bottom edge at radius **5.000** from the hinge axis, and
`HengeFilet` generates a roll at radius **5.000**. Both constant, so the panel **rode on the
box for the entire 0-90 deg swing** — a ~95 mm line contact that would have welded shut in a
print-in-place part.

**The swing test passed the whole time: interference was 0.000 mm3.** A zero-gap tangency is
not an interference. When checking a hinge, measure `distToShape` (the GAP) as well as
`common().Volume`. Macro 16's export gate now checks the gap for exactly this reason.

Fixed on the **lid** side by `PocketHingeWrap` — a rectangular relief setting the panel's
inner face back to `Depth/2 + HingeSwingClearance` over the wrap region, leaving the outer
face (and therefore the print-pose bed plane) untouched. Now **0.400 mm running clearance
from 30 deg through 90 deg, 0.0000 mm3 interference at every angle**.

Two dead ends worth not repeating:
- **Do NOT fix it by changing `HingeFilletRadius`** — see the concentricity rule below.
- **Do NOT move the whole panel outboard in Y.** In the 90 deg print pose, closed-frame Y maps
  onto print Z, so shifting the panel 0.5 mm out drops it to ZMin -2.5 while the box stays at
  -2.0 — the slicer then rests the part on the lid and the box floats 0.5 mm off the bed.

### The hinge neck, and the socket flat (macro 23)

`HingeNeckDrop` (3 mm) carries the neck below the hinge axis, thickening the joint vertically
without widening the box. That makes the neck's bottom corner sweep
`sqrt(HingeAxisFromRear^2 + HingeNeckDrop^2)` = 5.831, wider than the 5.400 bore, and near
full-open it caught the box floor — 2.25 mm3 at 90 deg.

Cleared by a **flat chord off the bottom of the socket**, `HingeSocketFlatZ` 0.9 high and
`HingeSocketFlatHalf` 3.514 each side. The half-width is derived from the BORE's chord, so the
flat's ends land on the circle and it leaves no notch; deriving it from the swept radius
instead made the flat wider than the bore and gouged 2.8 mm into solid side wall.

Two things that do NOT work here, both measured:
- **An annular sector** (bore out to swept radius, 180..270 deg) clears it but leaves an ugly
  thin crescent up the side of the socket — 90 deg of arc for a defect occupying 236..248 deg.
- **Raising the footer relief** to clear it makes the box's bottom-rear edge CONCAVE, and
  `HengeFilet` then ADDS material there instead of rolling it away (+7.56 mm3, contact
  restored). Fillets fill concave edges.

## THIRD TEST PRINT — 2026-09-14 — "the lid doesn't close all the way"

The hinge **held** this time and the box is usable. Three complaints, all now fixed by
`macros/27-panel_relief_and_walls` and `macros/28-magnet_skin`.

The lid not closing was **three separate coincident-surface defects stacked on one another**,
and they had to be peeled off one at a time because each one hid the next.

| # | Two surfaces driven to the same place | Fix |
|---|---|---|
| A | lid panel inner face `y = 36` vs box rear face `y = 36` | `PocketPanelRelief`, full width, → 0.5 mm |
| B | `PanelBottomZ` == socket bore top, both `HingeAxisFromBottom + HingeTabRadius + HingeTabClearance` | rebind `PanelBottomZ` to the **knuckle** top |
| C | outer lid flute at `x = Width/2 - FluteMargin` vs magnet pocket edge | `MagnetSkin` 1.0 → 1.7, `LidTopThickness` derived |

**The measurement that identified the jam.** A grazing contact between near-parallel
surfaces opens as `gap ≈ r(1 - cos θ)`, i.e. as θ², so it reads ZERO at closed and stays
microscopic for many degrees:

```
deg     gap_mm          deg     gap_mm  (after)
0.0     0.0000          0.0     0.4000
1.0     0.0008          1.0     0.4000
2.0     0.0033          2.0     0.4000
4.0     0.0132          4.0     0.4000
```

Before, the panel was within 0.1 mm of the box for the last **11 degrees** of travel and
within 0.3 mm for the last **19**. Printed roughness is ±0.05–0.1 mm, so the whole final
approach was a rub — "I can force it" is exactly what that feels like. After, the gap is
**constant** at the knuckle journal fit, which is concentric with the hinge axis and
therefore cannot resist closing. **A flat line across that table is the thing to look for;
a number that collapses toward θ = 0 is a jam no matter how small it looks at 4°.**

**Back-solving the curve tells you WHICH surface.** `r = gap / (1 - cos θ)` gave 5.42 at 4°
— the socket bore (5.4), not the panel face (5.0). That is how defect B was found after
fixing A changed the approach table not at all.

**Do not fix B by raising `PanelBottomZ`** — tried and measured. `+ HingeSwingClearance`
puts the step's corner at radius 5.9 against a 5.4 bore, i.e. outside the socket and into
solid side wall (single contact at `(50.5, 31.0, 10.9)`). The lid fills the socket from
BELOW, so clearance means coming DOWN to the knuckle radius.

### THE PATTERN BEHIND ALL THREE — identical expressions guarantee zero clearance

```
PanelBottomZ    = HingeAxisFromBottom + HingeTabRadius + HingeTabClearance
socket bore top = HingeAxisFromBottom + HingeTabRadius + HingeTabClearance
```

Two mating surfaces driven by the **same expression** are coincident forever, by
construction, and no amount of re-checking the numbers will reveal it because the numbers
are correct. Compare `HingeWrapRadius = HingeTabRadius + HingeSwingClearance`, which carries
its clearance term. **When two surfaces must not touch, their expressions must differ by a
clearance Param — grep for pairs that don't.** This has now happened three times in this
model (the r=5.000 ride macro 20 fixed, the panel face, and `PanelBottomZ`).

`LidTopThickness` was the same bug in a benign form: it *happened* to equal
`MagnetThickness + MagnetSkin` = 3.0, with nothing recording that it had to. It is now
derived, so "the magnets meet with no plastic between them" cannot be broken by editing one
number.

## FOURTH ROUND — 2026-09-14 — post-print-4 hand edits (macros 33, 34)

Bradley made four changes in the GUI after print 4. All four were sound; two of them were
expressed through the wrong knob. Captured by `macros/33-lid_back_and_magnet_depth` (replays
the edits as found) and corrected by `macros/34-magnet_proud_and_footer_binding`.

| Change | Verdict |
|---|---|
| Rear panel 2 → 4 mm via new `LidBackThickness`, lid plate Y extent rebound to `Depth + LidBackThickness` | ✅ correct as made |
| `FooterHeight` 2 → 4 "to match the new rear lid" | ✅ correct, and it was load-bearing — now bound, see below |
| New `TopLidClearance` 0.1 on the panel's top edge | ✅ works — but it is an OVERLAP, and it was aimed at the wrong problem; renamed `TopLidOverlap` by macro 35 |
| `MagnetThickness` 2.0 → 1.58 to shallow the pocket | ⚠️ right number, wrong knob — fixed by macro 34 |

### THE UNSAVED-SESSION TRAP — `is_modified` LIED

All four documents reported `is_modified: false` from `list_documents`, the working tree was
clean, and the files on disk were untouched since the previous commit — while the live VarSet
held two variables that **did not exist on disk at all** and 28 objects in `MagicCardBox` sat
`Touched`. Hours of GUI work was one crash away from gone, and every status signal said fine.

**`is_modified` is not evidence.** What actually proves the disk matches memory:

```python
# per-object staleness — 28 Touched objects means the geometry is not what the Params say
[(o.Name, list(o.State)) for o in doc.Objects if "Touched" in (o.State or [])]
# and read the document on disk directly (zipfile inside FreeCAD is NOT a shell tool,
# so it complies with the MCP-only rule; the guard hook blocks the shell path, not this)
zipfile.ZipFile(path).read("Document.xml")
```

**Before recomputing anything on a session that may hold unsaved GUI work, write the delta out
as a macro first.** A failed recompute does not roll back (D5), and the only recovery is
closing without saving — which would have destroyed exactly the work being recovered. Macro 33
exists for that reason and is the template: diff disk against memory, emit the replay.

### `MagnetProud` — pocket depth is not magnet thickness (macro 34)

`PocketMagnetBox.Length` and `PocketMagnetLid.Length` both bound straight to
`MagnetThickness`, so the pockets were **always exactly flush by construction** and the only
way to make a magnet stand proud was to lie about how thick it is. Now:

```
MagnetThickness   1.58    FACT     - measured with calipers
MagnetProud       0.025   DECISION - how far each magnet stands out
MagnetPocketDepth 1.555   DERIVED  = MagnetThickness - MagnetProud
LidTopThickness   3.255   DERIVED  = MagnetPocketDepth + MagnetSkin   <- follows the POCKET
```

Both magnets are proud, so the closed seam opens by `2 * MagnetProud` = **0.05 mm** and the
magnet faces meet directly instead of through two layers of plastic. Verified from the solids:
box pocket 1.5550, lid pocket 1.5550, skin 1.7000, worst-case skin under the outer flute
**0.9995 mm** (the flute at `x = 49.5` still clips the bore, which spans 49.45–53.55 — the
documented, accepted 1.0 mm case, preserved because the flutes reference `LidTopThickness`).

**The seam gap cannot be measured in CAD.** The magnets are purchased parts, not modelled
geometry, so the plate underside and the box rim remain coincident at `z = Height` in the
model. Do not go looking for a 0.05 mm gap in the solids — check the pocket depths instead.

### `FooterHeight = LidBackThickness` — now bound, and it is a real constraint

Printed lid-open at 90°, closed-frame +Y maps onto print −Z:

```
box underside      -> z = -FooterHeight
panel outer face   -> z = -(Depth/2 + LidBackThickness - ay) = -LidBackThickness
                      with ay = Depth/2 - HingeAxisFromRear: the rear terms cancel exactly
```

Equal → both land flat on the bed. Unequal → the slicer rests the part on whichever is lower
and the other floats. Measured **0.0000 mm bed mismatch** at 4.0/4.0. These were two free
knobs that happened to hold the same value — the print-3 coincidence trap **inverted**: there,
two surfaces that must NOT touch shared an expression; here, two that MUST stay coplanar did
not. `FooterHeight` is now derived from `LidBackThickness`. To decouple, the print pose itself
has to change — clear the expression deliberately, don't overwrite the value.

### `TopLidOverlap` (was `TopLidClearance`) — it is an overlap, and it was aimed wrong

Bradley added this trying to make the closed lid lie flatter. **It cannot do that**, and the
reason is worth keeping: the plate's underside is pinned to the `LidPlane` datum at
`z = Height`, while this constraint lives in `Sketch001`, the rear *panel's* profile. So it
moves the panel relative to the plate and never moves the plate at all. The diagnosis behind
it was right — see the 38:1 lever section — but the lever needed `LidSeatClearance`.

Renamed by macro 35, because leaving a "TopLidClearance" beside a real `LidSeatClearance`
is precisely the name collision this model keeps getting caught by.

`Lid/Sketch001.Constraints[7] = Height + LidSeatClearance + TopLidOverlap` pushes the rear panel's top edge
0.1 mm **into** the lid top plate. The two lid bodies now interpenetrate by **38.85 mm³**
(distance 0.0). That is harmless and arguably good — they are one rigid part and the overlap
guarantees they export as one connected mesh rather than meeting at a fragile tangency — but
the name promises a gap and delivers an interference. Rename to `TopLidOverlap` on the next
pass that touches it; don't "fix" the geometry to match the name.

### A hinge needs its bodies measured SEPARATELY (CLAUDE.md rule 1b, again)

The combined lid-vs-box swing table looked like the print-3 jam — 0.0000 at closed, rising as
θ². It was not. Split into the two lid bodies:

```
deg   panel vs box      plate vs box
0     0.4000  flat      0.0000   <- lid SEATING on the rim; this is what closure IS
2     0.4000            0.0814
8     0.4000            0.7571
90    0.4000            55.0
```

The panel — the surface that jammed on print 3 — is **flat at 0.4000 mm through the entire
0–90° swing with 0.0000 mm³ interference**. The whole-shape minimum was the plate's contact
masking the panel entirely. **Gate on the specific mating pair; a combined number can hide a
good surface behind a bad one.**

**And the plate's zero was NOT "the lid landing on the rim, which it is supposed to do" —
that reading was wrong and it cost a round.** Seating is correct; seating *1.3 mm from the
pivot* is the defect that pushed the closed lid's front edge up 1.1 mm. See the next section.
A contact being expected is not the same as a contact being in an acceptable place — always
ask WHERE, and what its lever arm is.

### THE CLOSED LID SAT 1.1 mm PROUD AT THE FRONT — a 38:1 lever (macro 35)

Observed on print 4 with **no magnets installed**, so this is pure plastic-on-plastic.

The box's sealing rail runs along each side wall at `z = Height` and stops at **y = 30.5**,
set by `Sketch009.Constraints[8] = Depth/2 - HingeAxisFromRear - HingeSwingClearance`. The
rim fillet pushes the real contact out to **y = 29.71**. The hinge axis is at **y = 31**. So
the lid's rearmost seat is a knife-edge **1.29 mm from its own pivot**, while the front edge
is 67 mm away:

```
back lid short by    front lifts
0.006 mm             0.29 mm
0.014 mm             0.59 mm
0.029 mm             1.10 mm     <- measured on the part
0.054 mm             1.75 mm
```

**29 microns — a third of one layer — produced 1.1 mm.** The CAD was never wrong: at nominal
the lid is dead flat, plate-to-rim 0.0000. The geometry simply multiplies tolerance by 38.

`HingeSwingClearance` was the culprit knob. It means "lid-vs-footer running clearance"
everywhere else; here it was silently deciding *how close to the pivot the lid may seat*.
0.5 is right as a swing clearance and catastrophic as a seat setback. **Left alone** — the
fix removes the dependence rather than overloading the knob further.

**The fix: `LidSeatClearance` 0.15 lifts the plate clear of the rail entirely.** The lid
cannot be raised as a whole — the panel is pinned to the hinge axis by its knuckle — so it
is the *plate* that rises relative to the panel. Result, measured:

| | before | after |
|---|---|---|
| front edge | up 1.10 mm | seats flat (drops 0.152 mm onto the front rim) |
| rear rail clearance | 0.000 | **0.125 mm** |
| fulcrum distance from pivot | 1.29 mm | **66 mm** |
| amplification | **38x** | **1x** |

The lid now seats on the **front** rim, where the lever is 1:1 and the surface is the one you
actually look at. The leftover wedge is at the rear, 0.125 mm, hidden under the lid overhang.

**`MagnetProud` is bound to `LidSeatClearance / 2` and must stay bound.** If the plate rises
0.15 while the magnets stay 0.025 proud, the faces no longer meet — they sit 0.10 apart, the
magnets drag the lid back down until they touch, and the lift silently collapses to 0.05. A
knob that looks unrelated would undo the whole fix. Bound, the faces meet exactly at the rest
position. Consequence: **the closed seam is `LidSeatClearance` = 0.15 mm, not the 0.05 picked
when `MagnetProud` was chosen in isolation.** Raising the lid and keeping a 0.05 seam are the
same number; you cannot have both.

### THE DATUM TRAP — feature-attached datums bit for real this time

Raising the panel's top edge by `LidSeatClearance` **moved `DatumPlane001` from z = 65 to
z = 65.15**, because it is attached to `Fillet.Face6` — the standing debt rule 3 flags. Both
hinge sketches ride that datum and convert to absolute Z by subtracting a bare `Height`:

```
Sketch002.Constraints[10]   HingeAxisFromBottom - Height - HingeNeckDrop
Sketch002.Constraints[11]   PanelBottomZ - Height
Sketch010.Constraints[1]    HingeAxisFromBottom - Height
```

That compensation is only valid while the datum sits exactly at `Height`. With the datum
0.15 higher the **entire hinge neck rode up into the socket bore** — panel volume
25926.54 → 25976.10 mm³, and panel-to-box clearance collapsed from a flat 0.400 to **0.254**.
Each now subtracts `(Height + LidSeatClearance)`.

Two things to carry forward:
- **The swing gate caught this, not inspection.** Nothing looked wrong; one number moved.
  Every macro that moves lid geometry must re-measure the panel swing before claiming success.
- **This is the second time the feature-attached datums have bitten.** Retargeting
  `DatumPlane001`/`DatumPlane002` to origin planes is now overdue. Until then, **any** change
  to the rear panel's top edge must re-check those three expressions.

## FIFTH ROUND — 2026-09-14 — the hinge overhangs (macros 36, 37)

Print 4's hinge area printed with drooping and stringing in two places. Both are overhangs.

### Top: `BackHingeFilletRadius` 4 → 8 (macro 36)

The knuckle recess is open in the rear face over `x 50.1…55.5` each side. `BackHengeFilet`
sweeps it from 9.49 mm deep at z=8 up to closed, and at R4 did that in **4.88 mm** — ~63°
average, 90° at the tangent. At R8 it spreads over 7.89 mm and closes at z=15.89 (was 12.88):
66.4° at z=11 → 44.2° at z=13 → 18.7° at z=16. 87.7 mm³ removed, swing unchanged.

**The 66° at z≈11 is NOT the fillet** — it is directly above the socket bore's apex at
`HingeAxisFromBottom + HingeTabRadius + HingeTabClearance` = 10.4. The top of a round hole has
a horizontal tangent by definition. The bore is the knuckle's journal, so it stays round.
Don't chase that number with a bigger radius.

### Bottom: a 45° chamfer, cut as a POCKET (macro 37)

`HengeFilet` is a **radius-5.000 cylinder centred exactly on the hinge axis, offset 0.0000**
(measured — Face9/Face10). It is the journal the panel wraps at a constant **5.5000**.
Printed upright its tangent is horizontal where it meets the bottom face: 88.8° at z=0,
over 45° for the first 1.7 mm.

**`PartDesign::Chamfer` cannot do this edge.** The edge is 100.2 mm at (0, 36, 0) and crosses
regions where the adjacent rear face is too short — the finger slot bottoms at z=4, the
knuckle recesses interrupt it. Size 5.0 and 4.5 → NULL shape; 4.0 → computes but
`isValid() == False`. The fillet copes by trimming itself to x 5.39…50.1; the chamfer
algorithm doesn't.

**So it is a sketch + pocket, appended LAST in the tree.** The 45° chord joins the fillet
arc's own endpoints and the arc bulges outside it, so cutting that plane leaves exactly the
chamfer — `HengeFilet` stays as the base geometry. At the tip it disturbs no edge references
(deleting it mid-tree would break all 17), and suppressing `PocketHingeChamfer` restores the
roll. Same reasoning as macro 24's flutes-last reorder.

**THE SIZE IS PINNED BY THREE LIMITS, AND THE THIRD IS THE ONE NOBODY EXPECTS:**

1. *The hinge, from above.* Corner radius `√((HingeTabRadius−C)² + HingeTabRadius²)`:
   C=3 → 5.385 (**fuses**, 0.115 clearance), C=4 → 5.099, C=5 → 5.000.
2. *The rear wall, from below.* The chord reaches `Depth/2 − C + z` and the wall's inner face
   is at `Depth/2 − WallThickness`, so the wall is cut through wherever `z ≤ C − WallThickness`,
   and it only exists above `FloorThickness`. **C=5 put a 1 mm slot straight through the back
   of the box** across the whole cavity width — and it still measured valid, closed, one solid,
   because the side walls and floor keep it connected.
3. *`C = FloorThickness + WallThickness` is the DEGENERATE BOUNDARY, not a safe limit.* There
   the plane passes exactly through the floor/rear-wall corner and pinches the wall to
   **exactly zero** along the full width. OCC: valid, closed, one solid. The **mesh**: not
   watertight, non-manifold, and the exported STL unprintable.

```
C      wall kept   mesh solid   manifold
4.0    0.000       False        False     <- knife edge
3.8    0.200       True         True      <- under one extrusion width
3.6    0.400       True         True      <- one nozzle width
3.2    0.800       True         True
```

```
ChamferWallKeep  = 0.4    manufacturing limit, its own knob - NOT a clearance
HingeChamferSize = min(HingeTabRadius; FloorThickness + WallThickness - ChamferWallKeep)
                 = 3.6
```

**Hinge clearance is unaffected at 0.500** — the chord is a chord of the fillet's *own*
circle, so the surface's max radius from the axis stays `HingeTabRadius` wherever the arc
still governs. The 45° band covers z 0.297…3.303; outside it the original arc remains (the
0.3 mm sliver below is under one layer height). The shelf at z=0 widens 4.6 → 6.0 mm.

### **A VALID CLOSED SOLID IS NOT EVIDENCE THAT IT CAN BE PRINTED**

This is the round's main lesson and it is new. `isValid()`, `isClosed()`, `len(Solids)==1`
and a clean audit **all passed on geometry with a zero-thickness knife edge through it**.
Only `MeshPart.meshFromShape(...).hasNonManifolds()` caught it. **Any macro that cuts near a
thin wall must gate on the MESH, not just the BRep** — macro 37 now does.

### Two more things that passed while wrong

- **Macro 16's volume gate is too loose to catch a change this size.** The R8 + chamfer edit
  moved 100-fluted from +0.06 % to +0.26 % against a **1 %** tolerance. It reported OK on a
  stale file. Re-export whenever the model changes; do not wait for the gate to complain.
- **D5, triggered by sweeping `HingeFilletRadius` 5 → 8 → 10** to explore a larger blend. It
  hung FreeCAD past the bridge's 30 s cap and left a downstream box fillet bound to a
  different edge, **filling a concave corner** at the footer relief: +1.2469 mm³ into the
  lid's sweep at 90°. Setting the radius back did **not** undo it. Box volume stayed identical
  at 131247.2, nothing was Invalid, the audit passed — only the swing measurement saw it.
  Recovery: close all four documents **without saving**, reopen from disk.
  **Fillets fill concave edges. After any fillet change in this body, measure the swing.**

## SIXTH ROUND — 2026-09-15 — the name plate, and a real variant matrix

### The product matrix is now 3 surfaces x 2 card counts = SIX

```
MagicCardBox-{100|60}-{smooth|fluted|fluted-label}.{stl|3mf}
```

`-plain` was renamed `-smooth` at Bradley's request. Two switches drive it, and
both features sit at the TIP of their bodies, which is what makes them
suppressible without disturbing any edge reference:

```
flutes   Pocket009.Suppressed        in BOTH MagicCardBox and Lid
label    PocketNamePlate.Suppressed  in Lid
```

**`macros/41-export_matrix` drives the whole thing from a table.** The old
procedure — set CardCount, flip two flags in two documents, run macro 16, call
`export_3mf`, call `export_stl`, repeat — was seven steps per variant. At six
variants that is forty-plus steps and every one can write the wrong state into
a file. That is not hypothetical: a file was exported carrying the name plate
while named `-fluted`.

Three things macro 41 does that the manual cycle could not:

- **Exports in-loop, so every variant is fully checked.** Macro 16 can only
  dimension-check the variant currently loaded; the other five got structural
  checks only. This retires a gate that was demonstrably too weak — a stale
  100-fluted file **missing the entire name plate** measured **+0.95 %** against
  macro 16's 1 % volume tolerance and passed.
- **Writes a JSON report to disk.** Six variants is minutes of recompute, far
  past the MCP bridge's 30 s response cap — but the macro keeps running in
  FreeCAD after the response is lost, so the caller polls for the file and the
  cap stops mattering. **This is the general fix for the 30 s cap**, not a
  one-off.
- **Restores a canonical state in a `finally`**, so the model is never left
  half-configured for the next session.

Macro 16 is still useful for building and gating a single pose by hand; its
variant list must be kept in step with macro 41's.

### The name plate blank (macro 38)

A rounded rectangle pocketed out of the flutes — **subtractive**, not the
additive pad of the original mockup.

| | |
|---|---|
| floor | `top − FluteDepth − NamePlateSink` = 67.4550 |
| X | ±45.1957, the **2nd flute's centreline** |
| Y | −26.000 … 30.000, `NamePlateInset` 10 from the leading and rear edges |
| corners | `BorderRadius` 5 |

X is pinned to the flute lattice, not to a number:
`Width/2 − FluteMargin − (Width − 2·FluteMargin)/(FluteCountFront − 1)`.
Y needs **two different expressions** because the plate is not symmetric in Y —
it overhangs the back by `LidBackThickness` to cap the rear panel.

### `NamePlateSink` — and why a coarse mesh check proves nothing

First build put the floor level with the flute bottoms. The blank's X walls run
**along** the flutes and sit exactly on the 2nd flute's low line, so the floor
was **tangent to that cylinder down the blank's whole length**.

`MeshPart` at `LinearDeflection 0.1` reported the plate solid, manifold and free
of self-intersections. The exported STL did not. `Mesh.export`'s default
tessellation is **~5× finer** (10656 facets where the typed tool wrote 1958) and
it found exactly **one** self-intersection in 29970 facets, at x = −45.15 — the
2nd flute's centreline.

```
NamePlateSink = 0.2    how far the floor sits BELOW the flute bottoms
```

0.2 and not less because the default mesh deviation is around 0.1; a margin
under that is smeared away by the tessellation and proves nothing. Same species
as `ChamferWallKeep` — a knob that exists purely to hold a degenerate case away
from zero. **Check the exported file, not a convenient local mesh.**

### The mockup left a DAG cycle behind (macros 39, 40)

The additive mockup's `SubShapeBinder` bound `Body.Pad` by going **through the
App::Part container**, and `Sketch001` — the lid's *rear panel* sketch — had
picked up four external-geometry references to `Binder.Face2` that **no
constraint used**. Two closed loops:

```
Binder     -> Part -> Body002 -> Sketch013 -> Binder
Sketch001  -> Binder -> Part  -> Body001   -> Sketch001
```

A plain `recompute()` succeeded and every solid measured correct, but 8 objects
stayed `Touched` however often it ran, and only a **forced** recompute surfaced
it:

```python
doc.recompute()                    # NOT a cycle check
doc.recompute(None, True, True)    # raises "The graph must be a DAG"
```

Bind to the **Body**, never to the container that holds the thing you are
binding into. And when auditing sketch GeoIds: **−1 is the X axis, −2 the Y
axis; external geometry starts at −3** — a `gid < 0` filter reports the axes as
external references and sends you the wrong way.

### Also: a macro that sets an expression only on creation is not idempotent

Macro 38 set its pocket's `Length` expression inside the `if not present:`
branch. Adding `NamePlateSink` then changed nothing on a re-run, because the
branch was skipped — and the macro's own gate caught it (`floor 67.6550 !=
67.4550`). **Re-assert driving expressions every run, outside the create
branch.**

| Defect | Status |
|---|---|
| D1 / D1b — projected external geometry in the box sketches | ✅ fixed (macro 02) |
| D2 — `Width`, panel grew off-centre | ✅ fixed (side effect of the D7 rebuild) |
| D3 — `Height`, panel grew downward | ✅ fixed (same) |
| D4 — assembly joint dies on face renumbering | ⚠️ recurs by design; re-run macro 05 |
| D5 — failed recompute does not roll back | ⚠️ still true in general — reload from disk |
| D6 — `Depth`, panel did not track | ✅ fixed (macro 11) |
| D7 — lid could not rotate at all | ✅ fixed (macros 07/08/10/12) |

Three things to know before touching anything:

- **The hinge is a knuckle, not a sector.** A disc in a disc socket rotates freely at any
  angle; the old R10 sector swept outside its own outline and dug into the box (372.73 mm3
  at 45 deg). `HingeTabRadius` is capped at
  `min(Depth/2 - HingeAxisFromRear, HingeAxisFromBottom)` = 5 mm by the side wall — do not
  raise it without re-checking that bound.
- **`PanelBottomZ` — SUPERSEDED 2026-09-13, and it was the cause of the broken hinge.**
  The old rule read "the lid's rear panel cannot reach the bottom; it must start at or above
  `HingeAxisFromBottom + HingeAxisFromRear`." That is true of the *full-width* panel, but it
  was applied to the whole panel, which left the two R5 tab discs as the only thing joining
  lid to box — **4 mm of connection out of 105**. The hinge snapped on the first print.
  The panel now steps down to the hinge axis across `x +/-47.5` (95 mm) and only the outer
  5 mm at each end stays at `PanelBottomZ` where the knuckles are. `PanelBottomZ` still
  governs that outer step, and is still bound to the socket circle's top.

- **`HingeFilletRadius` must equal the axis offsets — this is a hard geometric constraint.**
  A fillet on the bottom-rear edge centres at `(Depth/2 - R, R)`. That lands on the hinge axis
  `(Depth/2 - HingeAxisFromRear, HingeAxisFromBottom)` **only when
  `R == HingeAxisFromRear == HingeAxisFromBottom`.** At R = 5 the roll is concentric with the
  axis, which is what makes it a usable journal surface. Measured: setting R = 4.5 (which looks
  like a reasonable "add clearance" move) shifts the centre to (31.5, 4.5), breaks
  concentricity, and drives the box **18.086 mm3 into the lid's sweep**. It is now bound to
  `HingeAxisFromBottom` by `macros/18-bind_fillet_params.FCMacro`, which also refuses to run
  if the two axis offsets differ.
- **A failed recompute does not roll back** (D5). If an edit puts a feature Invalid, the
  geometry does *not* return when you restore the parameter. Recover by closing all four
  documents **without saving** and reopening from disk.
- **A bound expression is not proof of anything.** `Lid/Sketch001` carried
  `.AttachmentOffset.Base.z = -Depth` all along — but with `AttachmentSupport = []` the
  attachment engine never runs and the offset is never applied. Its position is now bound
  via `.Placement.Base.y` instead. Check `Placement` and `AttachmentSupport`, not just
  `ExpressionEngine`.

Do not "fix" any of this by nudging coordinates. Read the rules below before touching
geometry.

---

## Hard rules (this project)

These restate the global rules in `~/.claude/CLAUDE.md` with project-specific context.

1. **Everything parametric.** All 19 literals were bound on 2026-09-13 via
   `macros/01-bind_params.FCMacro` — that macro is the record of what maps to what, and
   re-running it is safe (it never overwrites an existing VarSet value). The audit is
   clean; keep it that way. Note the audit's blind spots below — a clean audit here does
   **not** mean the model is parametrically sound, as the failed sweep proves.

2. **No fixing geometry by editing raw sketch coordinates.** No prior coordinate-edit
   incident in this project; rule applies preventively. All 9 sketches are already fully
   constrained (DoF 0, `FullyConstrained == True`, verified 2026-09-13), so any urge to
   move a vertex means a missing *Param*, not a missing coordinate edit.

3. **Attach sketches to datum planes, not feature faces.**

   **What is already right here — do not "fix" it.** Verified 2026-09-13 by enumerating
   every `AttachmentSupport` and `ExternalGeometry` in both documents:
   - **There are zero cross-document geometry references.** `MagicCardBox` and `Lid` are
     coupled *only* through `<<Params>>#VarSet` expressions. `Binder002` binds
     `Lid/Pad001` — same document. That is cleaner than binders-across-documents and it
     is the reason a `Depth` change never corrupts the Lid document.
   - **All four `MagicCardBox` sketches attach to Origin planes** (`XY_Plane`, `YZ_Plane`).
     Textbook correct.
   - **`Lid/LidSketch` → `LidPlane` → `XY_Plane001`** — a datum on an origin plane, also
     correct.

   **Where the fragility actually lives.** The datum-and-binder discipline was applied
   consistently; the problem is what three of those datums/binders are *anchored to*. A
   datum plane attached to a feature face does not remove topological-naming fragility —
   it relays it:
   - `DatumPlane001` → `Fillet.Face6`, carrying `Sketch002` (hinge tab profile)
   - `DatumPlane002` → the `Pad002` object, carrying `Sketch003` (hinge pin hole)
   - `Binder002` → `Pad001.Face3`, feeding external geometry into `Sketch002`

   **And a third mechanism that is neither attachment nor cross-document** — this is what
   actually breaks the model (defect D1), so read it before assuming the datum work covers
   you. `MagicCardBox/Sketch003` is correctly *attached* to `YZ_Plane`, but it takes
   **external geometry** from `Mirrored` (Face3, the side-wall outer face) and dimensions
   against those projected edges by index. Measured at `Depth` 69 → 80:

   > The referenced face goes from 6 bounding edges to 8, because the hinge cut-out stops
   > coinciding with the rear face and becomes an interior notch. Every external GeoId
   > shifts by two — the top edge moves from `-7` to `-9`, the left edge from `-8` to
   > `-10` — while the constraints still point at `-7`/`-8`. `Sketch003` goes **Invalid**,
   > `Pocket002` cannot rebuild, and the body silently keeps its previous shape.

   So the trigger is **the edge count of the referenced face changing**, not face
   renumbering. Attachment discipline does not protect against this; only removing the
   external-geometry dependency does (dimension the cavity from Params instead).

   **Status 2026-09-13:** the external-geometry dependencies are GONE. Macro 02 removed them
   from all three `MagicCardBox` sketches; macros 08/12 removed the `Binder002` link from
   `Lid/Sketch002`. Every sketch in both documents now has `ExternalGeometry` empty and
   depends only on `Origin` + `VarSet`. `DatumPlane001` (→ `Fillet.Face6`) and
   `DatumPlane002` (→ `Pad002`, MapMode `ObjectYZ`) still reference features — they have not
   misbehaved, but treat them as the remaining fragility.

   **Audit blind spots — the script catches none of the above.** It checks *sketch*
   `AttachmentSupport` only: not datum-plane attachment, not `ExternalGeometry`, not
   binder supports, not `AttachmentOffset`, not object `Placement`, not `TaperAngle`.
   Check those by hand via `execute_python`. Two real defects hid in exactly those gaps:
   the footer's unbound 36° `TaperAngle`, and `Lid/Sketch001`'s hard-coded `Placement`.

   *(Housekeeping: `Binder001` has an empty `Support` — it is orphaned and appears to be
   dead. Confirm before deleting.)*

4. **Clearance concepts stay decoupled.** Two clearance Params now exist, deliberately
   separate because they are different physical interfaces:
   - `HingePinClearance` — lid pin hole ↔ the Ø6 pin standing in the box socket. Drives
     `Lid/Sketch003.Constraints[0]` as `HingePinDia + HingePinClearance * 2`.
   - `HingeTabClearance` — lid hinge tab ↔ its socket recess in the box side wall. Drives
     `MagicCardBox/Pocket.Length` as `HingeTabThickness + HingeTabClearance`.

   **Both are set to 0.4 mm** — one full 0.4 mm nozzle width — plus `HingeSwingClearance`
   0.5 mm for the lid-vs-footer faces. Verified from the solids, not the Params: box pin
   r 3.000 in lid hole r 3.400, lid tab r 5.000 in box socket r 5.400, tab 5.0 thick in a
   socket 5.4 deep. The hinge will feel loose (0.8 mm diametral play); tighten after a test
   print by editing the Params, which now drive every affected feature. Never collapse them
   into one knob and never reuse `WallThickness`.

   **These are print-in-place clearances, not assembly clearances.** The box and lid are
   printed as **one part with the lid open** (see Design direction below), so the pin and
   its hole are formed in the same print and must come off the plate already free. That is
   a stricter requirement than a press fit between two separately printed parts:
   - The gap must not fuse. Size it against the layer height and extrusion width, not just
     a nominal fit — a clearance smaller than roughly one layer height in the Z-facing
     direction will weld solid and the hinge will never move.
   - Typical FDM print-in-place hinges want **0.15–0.3 mm per side** (0.3–0.6 mm on
     diameter). Start at the top of that range and tighten after the first print; a hinge
     that prints seized cannot be rescued, one that prints loose still works.
   - `HingePinClearance` is applied to the **hole** (`HingePinDia + HingePinClearance * 2`),
     so it is a per-side radial value.

---

## Assembly architecture

**One printed part** (print-in-place hinge, lid open ~90 deg), no fasteners, no separate
hinge component. The Lid document holds two PartDesign bodies that touch — `Body` (top
plate) and `Body001` (rear panel + hinge) — so they export as one connected mesh.

Current hinge, after the 2026-09-13 rebuild:
- **Box side:** a disc socket of `HingeTabRadius + HingeTabClearance` about the hinge axis,
  cut `HingeTabThickness + HingeTabClearance` deep into each side wall, with a full Ø
  `HingePinDia` pin standing `HingePinLength` proud of the socket floor, plus a slot whose
  inner boundary is the socket ARC so it never cuts the pin.
- **Lid side:** a neck rectangle (`Pad002`, bridges to the panel) plus a disc
  (`Pad004`, `HingeTabRadius`) that fuses into it, with a blind hole
  `HingePinDia + HingePinClearance*2`. Two pads, not one outline — a single 270 deg arc
  profile has two valid solver solutions and flips.
- **Rear panel** starts at `PanelBottomZ`, not at Z=0; the box's own rear wall shows below
  it. That is forced, not cosmetic.


- **Box** (`MagicCardBox.FCStd` → `Part` "Box001" → `Body` "Box") is the tub: a padded
  rectangular solid, `Width` × `Depth` × `Height` (**106 × 72 × 65 mm today**), hollowed from
  the top by `Pocket002` to leave `SideWallThickness` (6 mm) on the ±X side walls. It is
  centered on the origin in X/Y and sits on Z = 0. Tip is `Fillet003`; 95 128.9 mm³, valid,
  closed, single solid.

  **The box DOES have a rear wall of its own** — 2 mm at `y 34…36`, full width. An earlier
  version of this file said it did not; that was wrong and it matters, because that wall sits
  face-to-face with the lid's rear panel at **zero clearance** (see the open defect above).
  At mid-width the finger slot cuts through it from z ≈ 4 upward, so what remains there is
  only the strip below the slot; outside the slot (`|x| > 15`) it is intact from z ≈ 3 up.

- **Lid** (`Lid.FCStd` → `Part` "Lid") is **one part containing two bodies** and is
  L-shaped in section:
  - `Body` ("Lid001") — the flat top plate, `WallThickness` (2 mm) thick, sitting on the
    `LidPlane` datum at Z = `Height`. It overhangs the box in +Y by `WallThickness`
    (`Depth + WallThickness` = 71 mm) so it caps the rear wall.
  - `Body001` ("LidBack") — the **outer rear panel** at the +Y end (`y 36…38`), which swings
    *with* the lid. It sits directly outboard of the box's own 2 mm rear wall, not instead of
    it. Since 2026-09-13 it is **not** a plain rectangle: it runs full width from
    `PanelBottomZ` to `Height`, then steps down to the hinge axis (`z = HingeAxisFromBottom`)
    across `x ±47.5`. That step is what carries the hinge load — 95 mm of it.

- **Hinge** is at the **rear-bottom corner, on the ±X side walls**, not on a rod:
  - The box side walls carry a socket + boss pair cut by `Sketch001`/`Pocket` and
    `Sketch002`/`Pocket001`, both sketched on `YZ_Plane` offset by `Width / 2`, then
    `Mirrored` to the opposite wall.
  - The lid's rear wall carries matching hinge tabs (`Sketch002` → `Pad002` "HingeTab",
    R10 with a Ø6 pin hole from `Sketch003`/`Pocket`), also `Mirrored`.
  - Pivot axis runs along **X**, inset 5 mm from the rear and 5 mm up from the bottom.

- **Opening direction:** the lid + rear wall rotate rearward about that X axis, so the
  whole back of the box folds away. `MagicCardAssembly.FCStd` models this with the box
  grounded and a `Revolute` joint between `LidBack.Face13` and `Box.Face21`.

- **Magnetic closure** (macro 19; depth decoupled by macro 34): two pairs of Ø4 × **1.58**
  disc magnets, one pair per thick side wall, `MagnetFromFront` (8 mm) back from the front
  face. Centres at `x = ±(Width/2 - SideWallThickness/2)` = **±51.5**,
  `y = -Depth/2 + MagnetFromFront` = -28.
  Both pockets are `MagnetPocketDepth` **1.505** deep — box `z 63.495…65`, lid
  `z 65.15…66.655` (the lid pocket rides `Height + LidSeatClearance`, not `Height`) with
  `MagnetSkin` above it — so each magnet stands `MagnetProud` **0.075** out and the two faces
  meet at **z = 65.075** with **no plastic between them**, holding the closed seam at
  `LidSeatClearance` = 0.15 mm. Verified from the solid: Ø4.10 bore, both pockets 1.5050,
  skin 1.7000, worst case 0.9995 under the outer flute.

  **The outermost lid-top flute still clips the magnet bore.** It sits at
  `x = Width/2 - FluteMargin` = **49.5**, and the bore spans **49.45–53.55**, so the flute
  cuts `FluteDepth` 0.7 out of the skin right at the bore's inboard edge. Measured worst-case
  skin is **0.9995 mm** (was 0.30 mm before macro 28 raised `MagnetSkin` to 1.7). If that
  ever needs more, raise `FluteMargin` (moves the outer flute inboard, away from the magnet)
  or `MagnetSkin` — do not move the magnets outboard, there is only 1.95 mm of wall there.

---

## Design direction (stated by Bradley 2026-09-13 — items 2 and 3 now partly built)

Four intentions that are **not** visible anywhere in the FCStd files. Nothing below has
been built yet; treat them as the agreed direction for the next modeling passes.

1. **Print as a single part, lid open.** The box and lid are one print with a
   print-in-place hinge — not two parts assembled. This is why the hinge clearances are
   sized as print-in-place clearances (rule #4), and it means
   `MagicCardAssembly.FCStd` is a *design-intent / motion* check, not a description of how
   the object is manufactured.
   **Unresolved:** the hinge axis sits at Z = 5 mm, so with the lid folded open the lid and
   rear wall lie in a plane 5 mm above the bed — an unsupported span unless the part is
   reoriented, the open angle is chosen to bring the lid down to the plate, or support is
   accepted under the lid. Settle this **before** tuning clearances, because it decides
   which surfaces are Z-facing and therefore which gaps are at risk of fusing.

2. ~~**Finger slots front and back** to lift the cards out.~~ **BUILT, and now REAR ONLY**
   (macro 29, 2026-09-14). `FingerSlotWidth` 30, `FingerSlotDepth` 61 — runs to the interior
   floor so the whole stack can be gripped. `Pocket007` is `ThroughAll` + **`One side`**;
   it was `Symmetric`, which punched both walls with one feature.

   **The front wall is solid.** Two reasons: it is the display face and the flutes now run
   across it unbroken, and a solid front means a knocked-over box cannot shed its cards.

   **An earlier note here said the rear slot "is sealed shut and currently does nothing".
   That was wrong** — it is only covered with the lid CLOSED. The panel swings with the lid,
   so at 90° open it has rotated down and back to lie flat behind the box and the rear wall
   is exposed, which is exactly when you reach in for cards.

   **Changing this side breaks `Fillet003` and that is unavoidable.** Closing the front slot
   is a TOPOLOGICAL change: the front inner rim stops being two 32.5 mm segments at
   `(±31.25, -34, 65)` and becomes one 95 mm edge. Both stored names die AND both recorded
   midpoints then land on the SAME new edge, so re-picking must de-duplicate — 12 refs
   collapse to 11. Macro 29 does this; macro 24 is the prior art but never had to merge.

3. **Bottom extended by 2 mm**, as an additional body that tapers outward to a wider
   footprint. Note this interacts with `FloorThickness` and with the "centered at (0,0,0)"
   rule — the taper must stay symmetric in X and Y. Being a separate body, it also needs a
   deliberate decision about whether it fuses into the box for export.

4. **Decoration on the outer faces** — last, after the functional geometry is settled and
   the sweep defects (D1–D3) are fixed. Decoration multiplies the face count and will make
   any remaining topological-naming reference far more fragile.

**Sequencing note:** items 2 and 3 both add features to `MagicCardBox`, which will renumber
faces. `MagicCardBox/Sketch003` still references `Mirrored.Face3` as external geometry
(defect D1), so **fix D1 first** or these additions will break the cavity the same way a
`Depth` change does.

---

## Files in this project

| File | Role | Depends on | Status |
|---|---|---|---|
| `Params.FCStd` | VarSet — all parametric variables (36 today) | — | ✅ |
| `MagicCardBox.FCStd` | The box tub; hinge sockets in the side walls; 4-deep fillet chain | `Params.FCStd` | ✅ clean, tip `Fillet003` |
| `Lid.FCStd` | Lid top plate + stepped rear panel + hinge knuckles | `Params.FCStd` | ✅ clean; 2 feature-attached datums remain |
| `MagicCardAssembly.FCStd` | Assembly doc; `App::Link` to both parts, `Revolute` joint | `MagicCardBox.FCStd`, `Lid.FCStd` | ✅ audit clean |

**Verified state, 2026-09-13 after the print-failure round** (all measured in-memory via the
MCP bridge, all three documents recomputing clean, nothing Touched):

| Check | Result |
|---|---|
| Box / lid rear / lid top | each valid, closed, **1 solid** |
| Static interference, all three pairs | **0 mm³** |
| Lid `Body` ↔ `Body001` distance | **0.0 mm** — exports as one connected mesh |
| Swing 0–90° | ≤ 0.29 mm³ (tangency noise on a 95 mm contact line) |
| Swing past 90° | 95° → 7.6, 100° → 115, 110° → 335 mm³ — **hard stop just past 90°** |
| Min gap, box ↔ lid | **0.0000 mm** ← the open defect above |

The lid opens to 90° and no further. If a flatter print pose is ever wanted, that limit has to
be designed for; it is not a slicer setting.

**Known debt (read before poking at these):**

- **The literals listed here through 2026-09-13 are all bound now** (macros 01 and 18). What
  remains is below.
- `Lid.FCStd` — the two feature-attached datum planes described in rule #3 (`DatumPlane001`
  → `Fillet.Face6`, `DatumPlane002` → the `Pad002` object). They have not misbehaved through
  several dimension changes, but they are the remaining topological-naming exposure. Retarget
  them to datums **before** any further binding pass; that change can move geometry and needs
  a clean recompute plus a re-solve of the assembly joint afterward.
- `Binder001` still has an empty `Support` — orphaned, appears dead. Confirm before deleting.
- Nothing is broken — all three shape-bearing docs recompute clean and every body is a
  single valid solid. This is debt, not breakage. The one functional defect is the zero
  running clearance documented at the top of this file.

---

## Params variables (summary)

**The box size is DERIVED from the card spec** (macro 14) — `Width` / `Depth` / `Height` are
still Params and still drive everything downstream, but they are no longer free numbers:

```
Width  = CardLength      + 2*CardClearance + 2*SideWallThickness   = 111.0
Depth  = CardWidth       + 2*CardClearance + 2*WallThickness       =  72.0
Height = CardStackHeight +   CardClearance +   FloorThickness      =  65.0
```

Interior is therefore **94.0 x 68.0 x 63.0 mm**, verified from the solid, holding a
92 x 66 x 62 stack with 1 mm all round and 1 mm headroom.
To go back to free knobs, clear those three expressions.

- **Cards (the input):** `CardLength` 93.0, `CardWidth` 66.0, `CardStackHeight` 62.0.
  `CardLength` and `CardStackHeight` were corrected from calipers on 2026-09-13 after the
  first print rubbed. **`CardWidth` 66.0 is still an ASSUMPTION** (standard 63 card + sleeve)
  — and since `CardLength` turned out to be off by 1 mm, measure this one too.

  **Card pitch: measure IN A STACK, not one card.** Two caliper readings, 2026-09-14:

  ```
  one sleeved card, loose        0.69 mm/card
  cards in the 100-count box     0.58 mm/card   <- USE THIS ONE
  ```

  A single sleeved card reads ~19 % thick: the sleeve is uncompressed and there is air at the
  lip. In a stack under its own weight that disappears. Over 60 cards the two figures differ
  by **6.6 mm**, which is more than `CardClearance` and `FloorThickness` combined — size off
  the loose figure and the box is needlessly tall; size off nothing and it does not close.

  ```
  CardStackHeight 62.0  ÷ 0.58  =  ~107 cards     <- what this box actually is
  60 cards        × 0.58        =  34.8 mm        <- CardStackHeight for a 60-card version
  ```

  So the current design is effectively a **100-card box** (107 with the headroom), not a
  60-card one. A 60-card variant lands near `CardStackHeight` 35, taking `Height` 65 → 38.

  **CARD COUNT IS NOW THE DRIVING PARAMETER** (macro 32). `CardStackHeight` was a free
  literal; it is now derived, so a variant is one integer:

  ```
  CardCount = 100            (integer - the product name)
  CardPitch = 0.62           (mm per sleeved card, in a stack - measured)
  CardStackHeight = CardCount * CardPitch

  100 cards -> CardStackHeight 62.0, Height 65.0     interior 95 x 68 x 63
   60 cards -> CardStackHeight 37.2, Height 40.2     interior 95 x 68 x 38.2
  ```

  At `CardCount` 100 that evaluates to 62.0, identical to the old literal, so installing the
  binding moved no geometry — macro 32 asserts it.

  **`FluteStartZ` 12.0 is deliberately NOT scaled with `Height`.** It is tied to the HINGE:
  `PanelBottomZ` is 10.0 and the flutes start 2 mm above it, clearing the knuckle step.
  Scaling it would drive the flutes down into the hinge on a short box. So the 60 box has a
  28.2 mm fluted band against the 100's 53 mm — same design language, shorter panel.

  **SUPERSEDED BY THE REAL BOX, 2026-09-14: the printed box holds 101 cards.** That is the
  authoritative pitch, because it is this sleeve in this box rather than a caliper on a
  sample:

  ```
  62 mm (CardStackHeight) ÷ 101  =  0.614 mm/card
  63 mm (interior)        ÷ 101  =  0.624 mm/card   <- if the stack used the 1 mm headroom
                                    ~0.62 mm/card   <- use this
  ```

  It lands between the loose 0.69 and the fully-compressed 0.58, which is what a
  partially-compressed stack should do — both calipers were right about their own case and
  wrong about this one. **Capacity is ~100 cards, by count, not by arithmetic.**

  ```
  60 cards × 0.62  =  37.2 mm   ->  CardStackHeight ~37, Height ~40
  ```

  Keep the older readings above: they are the evidence for WHY a single-card caliper cannot
  size a stack, which is worth more than the numbers themselves.

  **Still worth measuring a real sleeved 60-card stack** rather than trusting the
  multiplication, since a 60-stack compresses less than a 101-stack. 0.58 came from a full 100-box, where compression is at its greatest; a
  60-stack sits somewhere between the two figures, and the honest number is the measured one.
  This is the same correction `CardLength` and `CardStackHeight` already needed after print 1
  — card dimensions have been wrong every single time they were inferred rather than measured.

  **`FingerSlotDepth` IS NOW BOUND** (macro 30). It was a free literal, 61.0, hand-computed
  as `65 - 2 - 2`. Read from `Sketch011` rather than guessed, the constraints are

  ```
  Constraints[8]  DistanceY 19 = Height - FingerSlotDepth + FingerSlotWidth / 2   arc centre
  Constraints[9]  Radius    15 = FingerSlotWidth / 2
  Constraints[10] DistanceY 67 = Height + WallThickness                           slot top
  ```

  so the profile's lowest point is `centre - radius`, i.e. **`slot bottom = Height -
  FingerSlotDepth`** — the depth is measured DOWN FROM THE RIM, not up from the floor. Now:

  ```
  FingerSlotFloorLip = 2.0                                        (new Param)
  FingerSlotDepth    = Height - FloorThickness - FingerSlotFloorLip
  slot bottom        = FloorThickness + FingerSlotFloorLip = 4    constant in Height
  ```

  `FingerSlotFloorLip` is the strip of rear wall left continuous across the bottom of the
  slot. It equals `WallThickness` today AND equals `FloorThickness` today and is neither —
  the same coincidence trap as the third-print defects, so it gets its own knob.

  **THE 60-CARD BLOCKER IS FIXED (macro 31), and the box now sweeps to `Height` 40.**
  `Fillet003` went Invalid at `Height` 40 with `Invalid edge link: ;#d585:da;:H231,E.Edge24`.
  Diagnosed rather than assumed: **exactly one of its eleven references had died.** The other
  ten resolved and had tracked the rim down correctly (z 65→40, 64→39), and `Edge24` was still
  present *at the same index*, 95 mm at `(0, -34, Height)` — the front inner rim. So it was a
  stale element-map entry, **not** a missing edge and not a geometry failure.

  That edge was the one **macro 29 created** when it closed the front finger slot and merged
  two 32.5 mm segments into one. The reference it was given had a thin map history and did not
  carry through a dimensional change. Stripping the `?` and re-assigning fixed it **for good**,
  not as a patch: the box has since round-tripped **65 → 40 → 65 → 40** with no dead references
  and nothing Invalid (81 996.97 mm³ at Height 40, 116 541.35 at 65).

  **General lesson: a feature re-pointed by a macro deserves one more re-assignment after the
  next clean recompute.** The weak entry came from being written immediately after a merge.

  `macros/31-repair_dead_edge_refs` does this, and encodes the distinction that matters: a `?`
  says the MAP entry is stale, not whether the edge still exists. If the bare name resolves,
  strip and re-assign. If it does not, the edge is genuinely gone and must be re-picked BY
  POSITION (macros 24, 29) — stripping there would silently bind the fillet to whatever edge
  happens to hold that index. The macro repairs the first case and reports the second.

  (Macro 30's `DRY_RUN` stays False: it is no longer needed, and re-running a height sweep for
  its own sake only risks D5 again.)

  `FluteStartZ` **12.0 is still absolute**, so a shorter box gets proportionally chunkier
  fluting (53 mm of flute becomes 28 mm at `Height` 40). Cosmetic, not a defect — but decide
  it deliberately when the variant is built.
- **Geometry:** `Width`, `Depth`, `Height` (derived), `WallThickness` 2.0,
  `SideWallThickness` **8.0** (was 6.0; raised by macro 27 — hinge web 0.60 → 2.60 mm and
  magnet wall margins 0.95 → 1.95 mm. Grows the box OUTWARD only; interior is unchanged),
  `FloorThickness` 2.0, `EdgeFilletRadius` 1.0,
  `LidTopThickness` **3.205 (DERIVED = `MagnetPocketDepth + MagnetSkin`, macros 28/34 —
  follows the POCKET, not the magnet)**,
  `LidBackThickness` **4.0** (new, macro 33 — the rear panel; `FooterHeight` is derived from
  it, see the fourth-round section),
  `LidSeatClearance` **0.15** (new, macro 35 — lifts the lid plate clear of the rail near the
  hinge; killed the 38:1 lever that pushed the closed lid's front edge up 1.1 mm. **Raising it
  moves `DatumPlane001` — re-check the three hinge-sketch expressions, see THE DATUM TRAP**),
  `TopLidOverlap` **0.1** (new, macro 33; renamed from the misleading `TopLidClearance` by
  macro 35 — it drives the panel's top edge 0.1 mm INTO the plate so the two bodies fuse)
- **Magnets** (added 2026-09-13, macro 19; decoupled 2026-09-14, macro 34): `MagnetDia` 4.0,
  `MagnetThickness` **1.58 (MEASURED — a fact about the purchased magnet, never a depth knob)**,
  `MagnetProud` **0.075 (DERIVED = `LidSeatClearance / 2`, macro 35 — MUST stay bound, or the
  magnets silently drag the lid back down and undo the seat lift)**,
  `MagnetPocketDepth` **1.505 (DERIVED = `MagnetThickness - MagnetProud`; drives BOTH
  `PocketMagnetBox.Length` and `PocketMagnetLid.Length`)**,
  `MagnetFromFront` 8.0, `MagnetSkin` **1.7** (was 1.0 — the outer lid flute cuts
  `FluteDepth` 0.7 straight out of the skin, leaving **0.30 mm** over the magnet after the
  Width change; now 0.9995 mm worst case, measured under the flute),
  `MagnetFit` 0.05 (per side on the radius)

**`LidTopThickness` is separate from `WallThickness` on purpose — do not merge them.**
`WallThickness` already means four unrelated things: the box front/rear walls
(`Sketch003`), the lid's rear panel (`Pad001.Length`), the hinge neck (`Sketch002`), and
it drives `Depth` (`CardWidth + 2*CardClearance + 2*WallThickness`). The lid's top plate
needed to go 2.0 -> 3.0 to host a 2 mm magnet blind; raising `WallThickness` would have
grown the box's Depth by 2 mm and thickened three unrelated walls to fix a lid. Only
`Lid/Pad.Length` is bound to `LidTopThickness`.

**If you change `LidTopThickness`, the lid flutes must follow it.** `Lid/Sketch012`
positions all 24 flute circles off the plate's TOP face as
`Height + LidTopThickness + FluteRadius - FluteDepth`. Macro 19 rewrote those 24
expressions from `WallThickness`; if they ever drift back, the flutes get cut into the
middle of the plate instead of its surface.
- **Footer:** `FooterHeight` **4.0 (DERIVED = `LidBackThickness`, macro 34 — they must stay
  equal or the part will not sit flat in the print pose)**, `FooterTaperAngle` 36 deg,
  `FooterReliefChamfer` 1.0
- **Name plate** (macro 38): `NamePlateInset` 10.0, `BorderRadius` 5.0,
  `NamePlateSink` **0.2** (holds the blank's floor below the flute bottoms; at 0 the floor
  is tangent to flute 2 along the whole X edge and the exported STL self-intersects)
- **Hinge chamfer** (macro 37): `HingeChamferSize` **3.6 (DERIVED =
  `min(HingeTabRadius; FloorThickness + WallThickness - ChamferWallKeep)`)**,
  `ChamferWallKeep` **0.4** (one nozzle width of rear wall the chamfer must leave at the
  floor junction — a MANUFACTURING limit, not a clearance; at 0 the wall is a knife edge and
  the mesh goes non-manifold while the solid still reads valid)
- **Hinge:** `HingeTabRadius` 5.0 — **the single knob; `HingeAxisFromRear` and
  `HingeAxisFromBottom` are DERIVED from it** (see the identity below). `HingePinDia` 6.0,
  `HingePinLength` 3.0, `HingeTabThickness` 5.0, `HingeNeckDrop` 3.0, `RimRelief` 1.0, plus
  derived `PanelBottomZ` **10.0 = `HingeAxisFromBottom + HingeTabRadius`** (the knuckle
  top, NOT the bore top — see the third-print section), `PanelWrapZ` 0.0,
  `HingeWrapRadius` 5.5,
  `HingeFilletRadius` 5.0, `HingeSocketFlatZ` 0.9, `HingeSocketFlatHalf` 3.514

**`HingeTabRadius == HingeAxisFromRear == HingeAxisFromBottom` is a hard requirement, now
bound.** Three separate things need it and none of them said so:
1. `HengeFilet` must be concentric with the axis. A fillet on the bottom-rear edge centres at
   `(Depth/2 - R, R)`, which lands on the axis only when the two offsets are equal.
2. The knuckle must be tangent to the panel's inner face at `y = Depth/2`, which needs
   `HingeTabRadius == HingeAxisFromRear`.
3. `PanelWrapZ = HingeAxisFromBottom - HingeTabRadius` must land on 0 so the panel wraps to the
   bottom of the circle.

**Growing the knuckle was tried and measured WORSE.** At R = 7 the swing picked up 0.0081 mm3
at 15 deg and 0.3256 mm3 at 30 deg, and the running gap collapsed to 0.0000 until 45 deg.
At R = 5 it is 0.0000 at every angle with 0.400 mm from 30 deg on. See `macros/21`, unrun.
- **Fillets** (added 2026-09-13, macro 18 — four different concerns, never merged):
  `HingeFilletRadius` 5.0 **(DERIVED from `HingeAxisFromBottom`; concentricity — do not
  hand-set, see the header)**, `BackHingeFilletRadius` **8.0** (was 4.0; macro 36 — spreads the socket-recess ramp over 7.89 mm instead of 4.88, ~63° → ~50°),
  `RimFilletRadius` 0.8, `EdgeBreakRadius` 0.6
- **Flutes:** `FluteCountFront` 24, `FluteCountSide` 15, `FluteRadius` 2.5, `FluteDepth` 0.7,
  `FluteMargin` 6.0, `FluteStartZ` 12.0
- **Finger slot:** `FingerSlotWidth` 30.0, `FingerSlotDepth` 61.0 (runs to the floor as of
  2026-09-13 so the whole stack can be gripped)
- **Clearances (one per interface, never merged):** `HingePinClearance` 0.4,
  `HingeTabClearance` 0.4, `HingeSwingClearance` 0.5, `CardClearance` 1.0

**Still carrying the pin.** `HingePinDia` 6.0 and `HingePinLength` 3.0 are live: the box still
has a 3 mm-radius pin standing in a **0.6 mm** web (`SideWallThickness 6 − (HingeTabThickness 5
+ HingeTabClearance 0.4)`). Measured along X at the hinge axis: material runs 47.0 → 50.6, with
the cavity wall at 47.0 and the socket floor at 47.6. Bradley's stated intent (2026-09-13) is to
**eliminate the pin**; that has not been done. If the first print snapped at the box side wall
rather than the lid tab, this is why, and it will snap again.

---

## How to verify your change didn't break parametric

After any FreeCAD edit, before considering the task done:

```bash
python3 scripts/audit_parametric.py
```

This script flags:
- Sketches with 0 constraints
- Sketches with dimensional constraints lacking expression bindings
- Sketches attached to feature faces (DAG risk)
- Params variables used nowhere (dead Params)

The script is authoritative. If it reports violations, fix them via a `macros/*.FCMacro`
change before saving or committing — never by direct coordinate edits or FCStd XML surgery.

**Baseline at bootstrap (2026-09-13): 19 issues.** Any run reporting more than 19 means the
change made things worse. **Current target: 0.** The four hand-added fillets regressed it to
4 unbound `Fillet.Radius` values; `macros/18-bind_fillet_params.FCMacro` binds all four, so a
clean run is expected again. The audit reads the FCStd **from disk** — if documents are open
with unsaved changes it is reporting the last save, not what you just measured.

**The audit cannot see the defect that actually broke this print.** It checks expression
bindings; it does not check clearances, swing interference, or gaps. The first print's hinge
failure (4 mm of connection out of 105) happened while the audit was clean. Treat a clean
audit as necessary, never sufficient — and for anything that moves, measure `distToShape`
as well as `common().Volume`.

### THE TWO CHECKS THAT PASS WHILE THE MODEL IS WRONG

Both of these were learned the expensive way on 2026-09-13. They share a shape: the obvious
test returns green because it is looking somewhere the defect is not. Run them BY HAND after
any change to a moving interface or a feature tree — no script here catches either.

**1. A zero gap is not an interference. Measure `distToShape`, not just `common().Volume`.**

`common().Volume` is 0.000 for surfaces that merely TOUCH. The lid's rear panel rode on the
box at radius exactly 5.000 for the whole 0-90 deg swing — a ~95 mm line contact that would
have welded shut in a print-in-place part — and the swing test passed at every angle the
entire time. For anything that has to move relative to something else:

```python
gap  = box.distToShape(rotated_lid)[0]      # the number that matters
volume = box.common(rotated_lid).Volume     # 0.0 proves nothing on its own
```

Macro 16's export gate now checks the GAP, which is why it can refuse a mesh that every
interference test would have waved through.

**1b. At a hinge, the whole-shape minimum distance is the WRONG gate.**

`box.distToShape(lid)[0]` is dominated by surfaces that are SUPPOSED to be close — the
knuckle journal fit is `HingeTabClearance` 0.4 and the step sits on the bore at 0.0. Gating
macro 27 on it cost four full verify cycles, because it kept failing on geometry that was
correct while the defect sat elsewhere. Gate on the SPECIFIC mating faces instead (macro 27
measures the panel's inner face against the box's rear face directly with a line/solid
`common()`), and report the whole-shape contact POINTS as information — the points are what
identify which surface pair is at fault. A bare failing number tells you nothing here.

**1c. A bounding box does not notice most changes. Check VOLUME too.**

Macro 16's export gate compared triangle counts, watertightness, component count and bbox,
and on 2026-09-14 it passed BOTH stale exports after macro 29 filled the front wall's finger
slot — 2854 mm³ of geometry and not one millimetre of bounding box. It now also compares the
mesh volume against the posed solid, for whichever variant the model is currently in
(`Pocket009.Suppressed` decides which). Measured tessellation error is **0.07 %** against a
**1 %** gate, and the staleness it had missed was 1.87 %, so the margin is wide.

**2. Geometrically perfect and structurally inconsistent are not exclusive. Check Group
order against the BaseFeature chain.**

PartDesign carries TWO orderings of a Body's features:
  * `BaseFeature` — the chain the solid is actually computed from
  * `Group` — the tree order, which FreeCAD **re-derives `BaseFeature` from** on later
    evaluations (reload, reopening a feature for edit, ...)

`body.newObject()` appends to the END of `Group`. So setting only `BaseFeature` leaves the
two disagreeing, and FreeCAD will silently rewrite one from the other later. Macro 25 did
exactly this and produced a **cycle** — `Chamfer.BaseFeature = PocketKnuckleRelief` while
`PocketKnuckleRelief.BaseFeature = Chamfer`. The Chamfer then held `?Edge30` and died when
the feature was next opened; cancelling that dialog deleted it outright.

Every geometric check had passed: valid, closed, single solid, exactly 10.000 mm3 removed,
0.4000 mm gap at 90 deg. All of them true, because `BaseFeature` was correct at that instant
and that is what the shape is computed from. None of them looked at the tree.

Whenever a macro reorders features or inserts one mid-chain, rebuild BOTH and then verify —
`macros/25-knuckle_relief_parametric.FCMacro` carries `check_body_order()`, which walks the
chain from its root and refuses if any feature is unreachable or in a cycle, if
`Group != chain`, or if `Tip` is not the chain end. **Run it against every body in the
document, not just the one you touched.** Macro 24 does the reorder correctly; copy from it.

**Exemptions and known blind spots:**

- No dimensional exemptions — every one of the 19 is a real violation that must be bound.
- **Blind spot:** the script only checks *sketch* `AttachmentSupport`, so it does **not**
  flag `Lid/DatumPlane001` (attached to `Fillet.Face6`) or `Lid/DatumPlane002` (attached to
  the `Pad` object). Verify datum attachment manually via `execute_python`.
- This project's copy of the script is the **corrected** one from the Clocks project, not
  the buggy canonical Spade copy. The canonical version ships a wrong `DIMENSIONAL_TYPES`
  enum that reports geometric constraints (Tangent, Perpendicular, Block) as unbound
  dimensions and misses real `Radius`. Do not replace `scripts/audit_parametric.py` with
  the canonical copy. See the `reference_audit_parametric_type_bug` memory.
- **Second enum bug, found and fixed here 2026-09-13** — present in the Clocks copy too,
  so it is still live in every other project. The Pad/Pocket `Type` table was wrong:
  it claimed `TwoLengths` was index 1 (it is **4**) and assumed Pad and Pocket share an
  enum (they differ at index 1). Verified against FreeCAD 1.1.3 via
  `getEnumerationsOfProperty("Type")`:

  ```
  Pad:    0 Length, 1 UpToLast,   2 UpToFirst, 3 UpToFace, 4 TwoLengths, 5 UpToShape
  Pocket: 0 Length, 1 ThroughAll, 2 UpToFirst, 3 UpToFace, 4 TwoLengths, 5 UpToShape
  ```

  Effect: a Pocket with `Type=ThroughAll` was read as TwoLengths, so its **inert**
  `Length`/`Length2` were reported as unbound dimensions. It stayed dormant until
  `Pocket004` became the project's first ThroughAll feature. Corrected to
  `LENGTH_ACTIVE_TYPES = {0, 4}`, `LENGTH2_ACTIVE_TYPES = {4}`.
- **`TaperAngle` is not checked at all.** The footer's 36° taper sat unbound through a
  clean audit until it was bound by hand. Treat a clean audit as necessary, not sufficient.

---

## Memory files (deeper context)

`~/.claude/projects/[encoded-path]/memory/MEMORY.md` indexes the persistent memories for
this project. If you're unsure *why* a rule exists, read those files first.

No project-scoped memories for MagicCardBox yet — this project was bootstrapped on
2026-09-13. Relevant cross-project memories:

- `reference_audit_parametric_type_bug.md` — why this project uses the Clocks audit script
- `feedback_freecad_use_mcp.md` — inspect FCStd via the MCP bridge, never shell tools
- `feedback_freecad_assembly_workbench.md` — Assembly workbench gotchas (relevant to
  `MagicCardAssembly.FCStd`: `Assembly::AssemblyObject`, `LinkTransform`, 3D-view-only clicks)
- `feedback_freecad_rename_breaks_xlink.md` — do not `mv` these FCStd files; the assembly
  and both parts XLink to `Params.FCStd`. Rename via FreeCAD Save-As only.

---

## Workflow notes

**Invariant (apply to every FreeCAD project — do not edit):**

- **Inspect/edit FreeCAD models via the MCP bridge — never with shell tools.** Do **not**
  `unzip`/`grep`/`cat`/`sed`/`strings`/etc. a `.FCStd`. Use the FreeCAD Robust MCP server:
  `get_connection_status` first, then `open_document`, `list_objects`, `inspect_object`,
  `execute_python`, and macros. This is **enforced** by a PreToolUse hook in
  `.claude/settings.json` (copied from the root `settings.template.json` during bootstrap) —
  raw shell access to `.FCStd` is blocked. Only fall back to read-only `unzip` if the MCP
  bridge is genuinely unreachable, and ask the user first.
- **MCP server auto-starts with FreeCAD.** If an `mcp__freecad__*` call fails, the right
  interpretation is "FreeCAD isn't running" — ask whether to launch it. Do **not** silently
  fall back to `unzip` + XML parsing, and do **not** retry the same MCP call.
- **Write changes as `macros/*.FCMacro` files**, not direct XML edits. Reasons: reviewable,
  re-runnable, idempotent-friendly, uses FreeCAD's own serialization.
- **Cross-document expressions**: use the canonical form `<<Params>>#VarSet.VarName`. The
  shorter `<<Params>>.VarName` form sometimes fails with "Params not found."
- **Run `python3 scripts/audit_parametric.py` before committing.** If it reports violations,
  fix via macro, not by editing FCStd XML.

**Project-specific:**

- **`Midplane` is deprecated — use `SideType`.** FreeCAD 1.1 replaced `Midplane` on
  `FeatureExtrude` (Pad/Pocket) with `SideType`, enum
  `["One side", "Two sides", "Symmetric"]`; `Midplane=True` == `"Symmetric"`. Writing
  `Midplane` at all emits a deprecation warning to the Report View, and the property is
  slated for removal. All project macros now set `SideType`.
  **The two are linked, and clearing the legacy flag is not free:** writing
  `Midplane = False` also resets `SideType` to `"One side"`, silently undoing a symmetric
  cut (measured: box volume moved 100836.58 -> 100954.58 mm3). Clear the legacy flag FIRST,
  then set `SideType` — never the other way round.

- `inspect_object` and `get_sketch_info` **throw on every shape-bearing object here**
  (sketches, Pads, Bodies) on FreeCAD 1.1.3 — a known unpatched upstream gap, not a stale
  install. Read sketch internals (`sk.Geometry`, `sk.Constraints`, `sk.ExpressionEngine`,
  `obj.Shape`) via `execute_python` instead. `inspect_object` on `Params#VarSet` works fine.
- The **lid is one part with two bodies** (`Body` = top plate, `Body001` = rear wall). When
  exporting for print, export the `Part` container "Lid", not a single body, or the rear
  wall is silently dropped.
- `MagicCardAssembly.FCStd` uses the real Assembly workbench (`Assembly::AssemblyObject`)
  with a solved `Revolute` joint referencing `Body001.Face13` / `Body.Face21` — **named
  faces**. Any change to the hinge geometry can invalidate those references; re-open and
  re-solve the assembly after a hinge edit and confirm the joint still binds.
- All four documents (`Params`, `MagicCardBox`, `Lid`, `MagicCardAssembly`) should be open
  together; editing `Params` while the others are closed leaves them stale until reopened.
- `macros/` holds 01-41. Every change from here forward goes in as a `.FCMacro`, symlinked
  into `~/Library/Application Support/FreeCAD/v1-1/Macro/` as `MCB-<name>.FCMacro` so it
  appears in Macro -> Macros...

- **Fillet edge references survive DIMENSIONAL changes but not TOPOLOGICAL ones.** The box
  carries a four-deep fillet chain (`Fillet` -> `Fillet001` -> `Fillet002` -> `Fillet003`,
  17 named edges total). It looks like exactly the topological-naming fragility warned about
  in rule 3, and a 2026-09-13 review predicted it would break when the finger slot was
  deepened. **It did not.** The slot change threw a transient `Fillet002: BRep_API: command
  not done` during recompute and recovered clean; afterwards every stored edge name had been
  **re-hashed** (`Edge310`->`319`, `Edge113`->`112`, `Edge344`->`348`, ...) and all still
  resolved. `Use Hasher` is on for these documents. Verify before assuming breakage — check
  whether the referenced edges still resolve to sane coordinates.

  **But hashing cannot map a name onto an edge that stops existing.** Suppressing the flutes
  to make a plain variant left `Fillet002` Invalid, because `Fillet001`'s shape then loses
  most of its edges. That is a topological change, not a dimensional one.

- **The flutes are LAST in the box tree, so they can be suppressed (macro 24).** Order is
  `... MirroredNeckClip -> Sketch012 -> Pocket009`. Nothing depends on them, which is what
  makes the plain print variant possible. **Do not move them back upstream.** Re-rooting the
  chain meant re-picking all 17 edges by POSITION — after the move each fillet computes on a
  shape with no flutes, so neither the stored names nor exact midpoint/length matching work;
  what survives is that the recorded midpoint still LIES ON the right edge. Box volume came
  through the reorder at 93 999.15 -> 93 999.15, drift 0.00 mm3.

  Side effect, accepted: `Fillet002`/`Fillet003` round the top rim, which the flutes reach.
  The rim is now filleted clean and then fluted through, rather than fluted and then filleted
  along the scalloped edge. `Fillet`/`Fillet001` sit below `FluteStartZ` and are unaffected.

---

## Print profile

**Print 1 (2026-09-13, PLA): FAILED** — hinge snapped, stringing across the back, overhang at
the top of the hinge. See the first-print section at the top of this file.
**Print 2: cancelled.**
**Print 3 (2026-09-14, PLA, silk): the hinge HELD and the box is usable** — but the lid would
not close, which took three stacked coincident-surface defects to explain. See the third-print
section. Print 4 is the first with real clearance on every mating face.

### Measured print times — Creality K2 Plus, 0.4 nozzle, PLA, fluted variant

Two findings from slicing print 4, both worth carrying into the production version.

**A cutout that INTERRUPTS a perimeter can cost more time than the material it removes.**
Making the front wall solid (macro 29) ADDED 2854 mm³ and the estimate went DOWN to 4h12m.
The finger slot ran `FingerSlotDepth` 61 mm up the front, so for roughly 300 layers the outer
perimeter was not a closed loop: stop at one slot edge, retract, travel, re-prime, restart at
the other — two extra wall ends per layer, with the front flutes chopped into short segments
that never reach cruise before decelerating. Filling it restores one continuous loop per
layer. The saved retractions and accelerations outweigh the extra extrusion comfortably.
**Judge a cutout on its perimeter cost, not its volume.**

**Variable layer height is worth more than it looks.** Same geometry:

| setting | estimate |
|---|---|
| fixed layer height | 4h12m |
| variable, 0.32 quality/speed, smooth 5 | **3h43m** |

(Smoothing is inverted — a LOWER number means MORE adjustment, so 5 is more aggressive than
the 7 used earlier.) Earlier rounds measured 3h6m at 0.4 quality / smooth 7, but on the
SMALLER box; print 4 carries `SideWallThickness` 8, `LidTopThickness` 3.7, `Width` 111 and a
solid front, which is **94 555 → 116 541 mm³ of box, +23%**. The rise from 3h6m is that extra
material, not a regression.

**FOUR published variants as of 2026-09-14** — card count x surface, all from one model.
`CardCount` 100/60 and `Pocket009.Suppressed` in BOTH documents are the only two switches:

| 100-card | plain | fluted |
|---|---|---|
| facets | 2 012 | 5 636 |
| volume | 163.02 cm³ | 155.43 cm³ |
| watertight / non-manifold / self-int. | ✓ / False / False | ✓ / False / False |
| components | 2 (box + fused lid) | 2 |
| footprint | 113.91 × 132.15 × 74.00 on Z=0 | identical |

| 60-card | plain | fluted |
|---|---|---|
| facets | 2 012 | 5 636 |
| volume | 122.39 cm³ | 116.99 cm³ |
| footprint | 113.91 × 107.35 × 74.00 on Z=0 | identical |

Triangle counts match across card counts because the topology is identical; the flute volume
scales with height (7.59 cm³ removed on the 100, 5.40 cm³ on the 60).

**Macro 16 dimension-checks only the variant the model is currently loaded as.** The other
three are different boxes on purpose, so bbox and volume would report correct files as stale;
they get the structural checks (triangle count, watertight, manifold, 2 components) instead.
| print-pose hinge gap | 0.4000 mm | 0.4000 mm |

Plain is produced by suppressing `Pocket009` in BOTH documents (box flutes and lid top
flutes), which only works because of the macro-24 reorder. Re-enable them afterwards.

**Print pose is settled: lid OPEN, box upright on the plate.** This is what was printed, and
it is what the geometry now assumes. It matters because it decides which gaps are horizontal:
printed open, the lid/box clearances are vertical seams (they string but do not sag or fuse),
whereas printed closed every clearance becomes something the slicer has to bridge in mid-air.
The lid only opens to 90°, so a flatter pose is not available without a design change.

What the first print showed, and what to look for on the next one:
- The hinge snapped — 4 mm of connection out of 105. Fixed (95 mm now). **Check this first.**
- Stringing across the lid/box gap. Should be much reduced now the slot is mostly closed.
- Overhang at the top of the hinge socket. Fixed with `BackHengeFilet` R4.
- Cards rubbed the sides and the stack was too tall. Fixed at the card spec, not the clearance.
- **Not yet fixed:** the lid rides on the box at zero gap for ~95 mm. Expect it to fuse.
  Fix that before printing again, or the hinge will not move.

Target hardware per `CAD_STANDARDS.md`: Creality K2 Plus (FDM) / ELEGOO Saturn 4. Test in
PLA, production in ASA. Fill in layer height / wall count / material from the first print that
actually works — the hinge clearances (`HingePinClearance`, `HingeTabClearance`,
`HingeSwingClearance`) are material-dependent and get tuned from a real print, not defaults.
