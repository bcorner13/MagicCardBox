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
0.3 mm sliver below is under one layer height).

**Correction (2026-09-15):** this section first claimed the chamfer widened the unsupported
shelf at z=0 from 4.6 to 6.0 mm, reasoning that the cut starts at `Depth/2 − C` = 32.4. That
is wrong — the chord only governs between the crossovers, so below z=0.297 the fillet arc is
still the outer surface and the bottom face reaches y=31 as before. Measured `ymax(x=30,
z=0) = 31.0`. **The shelf is unchanged at 4.6 mm; the chamfer costs nothing there.**

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

## SEVENTH ROUND — 2026-09-15 — the floating cantilever, halved (macros 42-44)

Creality Print warns `object Object_1 has floating cantilever` on every slice. Bradley fixed
it with **two changes of his own**, and the work here was mostly clearing what blocked them.

### The measured result

```
flat down-facing area at z=0     458.4  ->  176.9 mm2     (-61%)
footer reach at z=-0.1            26.4  ->   28.381
panel swing                      0.4000 flat, zero interference (unchanged)
```

### What actually fixed it — and the order matters

1. **`PanelBottomFillet`** (Lid/Fillet001) rounds the rear panel's bottom inner edge. It is
   NOT cosmetic: it shrinks the lid's **swept envelope**, freeing space the box can then
   occupy. Measured, space free below z=0 after adding it:

   ```
   z = -0.5    26.5 -> 29.00    (+2.50 mm)
   z = -1.0    26.0 -> 27.25
   z = -2.0    25.5 -> 26.25
   ```

   Bound: `Radius = LidBackThickness - HingeSwingClearance - HingeTabClearance` = 3.1. The
   panel is 3.5 thick there, so it rounds to within one `HingeTabClearance` of its outer face.

2. **`FooterReliefRadius` 3.74** turns the footer relief from a step into an arc (Sketch006 →
   Pocket004), using the space the fillet freed. A **free design input, not derived** —
   nothing in the Params lands on 3.74, and inventing a derivation that merely evaluates
   correctly today is the `LidTopThickness` mistake all over again.

   **It is AT the swept-envelope limit.** The relief reaches y = 29.24 at z = 0 against a
   sampled free limit of 29.00 (0.25 mm grid, so inside the error band). The swing gate reads
   a flat 0.4000, so it is not colliding — but **raising this Param eats hinge clearance
   directly. Re-measure the swing after any increase.**

### The lesson: a cosmetic feature was hiding a real design change

`Fillet004` — a 0.7 mm ease on an internal socket edge, which macro 26 explicitly called
"NOT clearance-critical" — had gone Invalid and was holding a **stale shape**: 506 edges
against its own base `Pocket009`'s 515. Everything downstream built on that stale geometry,
so **the footer arc was not reaching the part at all**. The viewport was not showing the box
that had been designed.

Deleted, and the footer `Chamfer` behind it re-pointed. Note its target had **moved**, not
just re-indexed: the arc relief put the relief's front edge at (0, 25.5, −FooterHeight)
instead of (0, 25.5, 0), so it was re-found **by position**.

### A NAMED-EDGE REFERENCE THAT RE-RESOLVES TO THE WRONG EDGE IS WORSE THAN ONE THAT DIES

`PanelBottomChamfer` was superseded by the new fillet, but it had also **silently drifted**.
Both named `Edge27` on their own base, and inserting the fillet ahead of the chamfer changed
that base:

```
PanelBottomFillet    Edge27 on PocketKnuckleRelief  ->  (0, 36.5, 0)     panel BOTTOM
PanelBottomChamfer   Edge27 on Fillet001            ->  (0, 36, 65.25)   panel TOP
```

It had moved to the panel's **top** inner edge, inside the overlap with the lid plate, while
still labelled `PanelBottomChamfer`. It was never Invalid, so nothing complained. `Fillet004`
at least announced itself.

**After inserting any feature mid-chain, re-check every named-edge reference DOWNSTREAM of it
BY POSITION — not just the ones that error.**

### Retired Params

`SocketFlatFillet` and `BorderWidth`, both dead. Each checked against the live expression
engine of **both** documents *and* the VarSet's own internal expressions before removal —
never on the assumption that they were unused. `RimFilletRadius` was checked and **kept**: it
still drives `MagicCardBox/Fillet002`.

### What the slicer warning is actually worth

Unchanged by any of this, and worth keeping in proportion:

```
Overhang wall    6s     0.00 m       Internal Bridge   6m38s   1.45 m
```

Six seconds of overhang wall in the whole print. **The slicer bridges that ledge rather than
treating it as unsupported perimeter**, at 0.2 mm layers and at 0.12 alike. The warning is a
geometry flag, not a defect report — five prints bear that out. h3liØ's reference box has the
same joint with the same 0.38 mm gap over its own lid; what it lacks is one big flat face.

---

## EIGHTH ROUND — 2026-09-15 — the cantilever reaches ZERO, and one Param was two things

Bradley replaced both chamfers with a hand-drawn B-spline ramp, and asked for a taller
60-card box and a magnet pocket the magnets actually fit. Macros 45-49.

```
flat down-facing area at z=0     176.9  ->  0.0 mm2      (458.4 where round 7 began)
minimum rear wall                0.983  ->  1.982 mm     it got THICKER, not thinner
panel swing                      0.4000 flat, zero interference, unchanged throughout
```

### THE BIG ONE — `CardPitch` WAS TWO DIFFERENT MEASUREMENTS IN ONE KNOB

The 60-card box came up 5 mm short. The obvious fix — raise `CardPitch` — was applied
(macro 45) and its own gate reported both card counts clean. It was still wrong, and the
macro's docstring contains the tell: it lays out two capacity measurements that contradict
each other and calls the contradiction "an accepted trade".

```
printed 100 box   101 cards with ~2 mm still free  ->  0.6040 mm/card
Ryan's 60 box     60 cards need 5 mm more          ->  0.6867 mm/card
```

**It was not a trade. It was two different sleeves.** Bradley identified it: the sleeves
Ryan used are thicker. Neither number was ever wrong — they measure different objects.

```
thin sleeve   true 0.6040   CardPitch 0.6200   slack 0.0160 mm/card
Ryan's        true 0.6867   CardPitch 0.7033   slack 0.0163 mm/card
```

The SAME per-card slack, applied to two sleeves. And the loose single-card caliper reading
of **0.69**, which this file wrote off as a 19 % overread from an uncompressed sleeve,
lands almost exactly on Ryan's 0.6867 — **it was very likely measuring the thick sleeve
all along, and was never an error.**

`CardPitch` now lives **per-variant in macro 41's MATRIX**, beside `CardCount`:

```python
THIN_SLEEVE = 0.62      # 100-card products
THICK_SLEEVE = 0.7033   # 60-card products - Ryan's sleeves
```

So the 100 box keeps its proven `Height` 65 and the 60 gets 45.2. Forcing one global pitch
would have made the 100 box hold ~114 cards. **Macro 45 is marked SUPERSEDED — DO NOT RUN.**

> **THE RULE: when two careful measurements of "the same" quantity disagree, the default
> explanation is that they are NOT the same quantity.** Averaging them, or picking one and
> calling the difference a trade-off, buries a real distinction inside a single knob. This
> is the coincidence trap in its third form — the print-3 defects gave one EXPRESSION to two
> surfaces that had to differ; this gave one PARAM to two things that had to differ.

### THE RAMP — three constraints that over-determine each other

Bradley's `Sketch013` -> `Pocket010` is a cubic B-spline, vertical where it meets the rear
face and landing nearly flat, swept `UpToFace`. It replaced `PocketHingeChamfer` (macro 37)
and the footer `Chamfer`, and it is **better than both**: 176.9 -> 15.7 mm² of flat ledge
before the rear wall change, 0.0 after.

**A 45 deg exit angle is GEOMETRICALLY IMPOSSIBLE here, and that is not a tuning problem.**
The curve must pass outboard of `(cavity face + RampMinWall)` at the cavity floor to keep
the wall, and land inside the footer's reach at z = 0 or the ledge returns:

```
minWall  landing Yb   best exit angle   unsupported ledge
0.8      29.0         19.0 deg          none
0.8      31.0         27.8 deg          1.60 mm
1.0      33.0         45.0 deg          3.60 mm
```

**You may have any two of {thick rear wall, steep exit, no ledge}. Never all three.** Every
candidate Bézier forced to 45 deg reached y ≈ 31.5 at z = 2 — a *negative* wall, i.e. it
deletes the rear wall rather than thinning it. Measured before building, not after.

And it does not matter as much as it looks: print 5 established that **curved overhangs
print and flat ones droop**. A shallow CURVED exit is fine; it was the flat ledge that sagged.

### PARAMETRIZING A SPLINE — name the frame, not the control points

Naming six control points would be wrong: they would drift independently and the curve
would stop being smooth, which is its entire purpose. What works is that each interior pole
is held by two `Distance` constraints to the frame lines, so it is an **offset from the
frame** and the whole curve translates and keeps its shape when `Depth` moves.

```
RampBottomY 29  RampTopZ 8  RampOvershoot 2  RampUndercut 2     the frame
RampPole1In/Up  RampPole2In/Up  RampPole3In/Up                  hand-tuned, MOVE TOGETHER
RampMinWall 0.8                                                 a GUARD, not a driver
```

Binding the frame alone made the curve parametric — asserted with a phase-A no-op check
(0.0000 mm³ drift). The six pole offsets are recorded as **free design inputs**, not dressed
in a derivation that merely evaluates correctly today.

### `RearWallThickness` 3.0 — and it FIXED the ramp rather than costing anything

Bradley asked for a 3 mm rear wall. `WallThickness` could not carry it: it also drives the
front wall, the hinge neck, and `Depth` itself.

```
Depth = CardWidth + 2*CardClearance + WallThickness + RearWallThickness = 73   (was 72)
```

The box gets **1 mm deeper** — interior must stay 68.000 for the cards, so a thicker rear
wall pushes the rear face OUT rather than eating card space. Asserted: interior 68.000,
front wall 2.000, rear wall 3.000.

The payoff was larger than predicted. Moving the cavity face 34 -> 33.5 gave the ramp room:

```
ramp minimum wall    0.983 -> 1.982 mm     DOUBLED, and 2.5x the 0.8 guard
flat area at z=0      15.7 -> 0.0 mm2      the ledge stopped existing
```

**Print height rises 1 mm**: print Z is `Depth + FooterHeight`, so 76 -> 77.

### Magnets — a chamfer alone would NOT have fixed it

```
MagnetDia 4.00, MagnetFit 0.05 per side  ->  bore Ø4.100, measured at rim AND floor
```

0.05 mm per side is a CAD fit, not an FDM fit. Printed holes come out **undersize** —
typically 0.1–0.3 mm on diameter, worst on small bores — so a nominal Ø4.100 prints near
Ø3.9–4.0 and the magnet binds along the WHOLE DEPTH. A lead-in helps it START and then it
still jams. Both were needed, and the fit is the load-bearing half:

```
MagnetFit    0.05 -> 0.15 per side      bore Ø4.100 -> Ø4.300
MagnetLeadIn 0.3                        45 deg lead-in at each mouth
```

Walls 1.95 -> 1.85 mm each side; skin under the outer flute unchanged at 1.00 mm (it is
`MagnetSkin - FluteDepth`, so widening the bore extends that region but cannot thin it).

**Built as a TAPERED POCKET, not `PartDesign::Chamfer`** — a chamfer needs four named edge
references, and this project has been bitten twice (Fillet004 died; PanelBottomChamfer
silently re-resolved onto the WRONG edge). A tapered pocket references a sketch and a Param.
The taper SIGN is determined by measurement, with an automatic flip if the cone came out
widening.

### Retired Params, and the cascade

`HingeChamferSize` and `FooterReliefChamfer` died with the features Bradley deleted.
Removing `HingeChamferSize` then orphaned **`ChamferWallKeep`**, which was kept alive only
by `HingeChamferSize`'s own expression — it read as "in use" right up until it wasn't.
Macro 49 re-scans after every removal until the dead set stops growing. 75 -> 72 Params.

### Export

All six variants re-exported clean, `all_ok: True`. Facet counts rose ~5x (5 636 -> 29 076
on the fluted) because the ramp is a genuine curved surface. Volume deltas ≤ 0.007 %.

| | 100-card | 60-card |
|---|---|---|
| Height | 65.0 | 45.2 |
| bbox (print pose) | 116.81 × 134.26 × 77.0 | 116.81 × 114.46 × 77.0 |
| facets smooth/fluted/label | 12 976 / 29 076 / 32 236 | 12 908 / 29 008 / 32 168 |

---

## NINTH ROUND — 2026-09-15 — print 6, and the check that had been lying all along

Print 6 came off with the hinge free and the lid flush. Two defects, both fixed
(macros 50, 51) — and the investigation turned up something worse than either.

### ⚠️ `o.State` IS NOT `Shape.isValid()`. NINE FEATURES WERE BROKEN BEHIND "Up-to-date".

```
MagicCardBox/Body    9 of 23 features:  Shape.isValid() == False
                                        "Unorientable shape"
                     three of them also  isClosed() == False
every one of them:   State == ['Up-to-date']
```

**Every macro in rounds 8 and 9 gated on `"Invalid" in o.State`, and every one
reported "all checks pass".** So did `scripts/audit_parametric.py`, which does
not look at shapes at all. So did all six export gates — because they check the
TIP, and the tip is genuinely valid, closed, one solid, watertight, manifold and
free of self-intersections. Six prints confirm it.

```python
o.State                  # recompute bookkeeping. NOT shape health.
o.Shape.isValid()        # the actual question
o.Shape.check(True)      # tells you WHAT is wrong ("Unorientable shape")
```

**The debt is PRE-EXISTING** — present in the saved file before this session, so
neither Bradley's GUI edits nor macros 45-51 caused it. Macro 50 took it 9 -> 8.
Macros 50 and 51 now carry `chain_validity()`, used as a REGRESSION gate: fail
if the count GROWS. Copy that helper into anything that touches the box body.

### DO NOT NAME A ROOT CAUSE FROM ONE READING

"Root cause found: Pocket008" was stated here on a single measurement. It was
wrong. Under a suppress/restore experiment the first-invalid **migrated to
Pocket007** and stayed there across three repeat recomputes with the flags
restored — an upstream feature cannot be caused by a downstream toggle, so the
"first invalid" is not a causal signal at all. Repeat a diagnostic before
building a story on it, especially one that moves under perturbation.

### A VIEWPORT ARTIFACT MAY BE AN INTERMEDIATE FEATURE, NOT THE PART

Bradley saw a spike near the socket after selecting `BackHengeFilet`. It is not
in the printed geometry:

```
Fillet001 (BackHengeFilet)  valid=False  closed=FALSE   <- what was on screen
Body tip                     valid=True   closed=True, 1 solid
tip mesh: solid ✓  non-manifold ✗  self-intersecting ✗  1 component
largest sliver in the tip: 0.00055 mm2  (0.02 mm across)
```

Selecting a mid-chain feature makes FreeCAD draw THAT feature's shape. **Before
chasing a visual defect, check whether you are looking at the Tip.**

### `NeckClip001` REMOVES NOTHING — AND CANNOT BE DELETED

Bradley called it worthless. Measured at the TIP (the only valid place to
measure), he was exactly right:

```
tip with NeckClip     137195.863
tip without           137195.863      removes 0.000 mm3, no lumps
tip valid without     FALSE           <- the catch
```

`PocketNeckClip` + `MirroredNeckClip` contribute **zero** material and are the
features where shape validity RECOVERS. They are geometrically worthless and
structurally load-bearing by accident. Removing them requires fixing the
upstream invalidity first. `Pocket008` and `Mirrored002` are similarly
near-redundant (-0.001 mm3) — `Pocket008` re-cuts `Pocket`'s exact profile with
the same Length expression in the same direction, which is the coincident-surface
trap in its fourth form.

### `FooterLidClearance` 0.62 — the lid and footer nearly fused at the bed

Measured in the print pose, across the bed plane:

```
z = bed+0.02 .. +0.20   box reaches 26.000 | lid starts 26.500 | gap 0.5000 FLAT
```

A flat 0.5 mm slot, both walls printing simultaneously, ~2 mm tall, in PETG.
That is what welded. The gap WAS `HingeSwingClearance` exactly, by construction
— but that Param drives **eight** things, seven of them inside the hinge Bradley
reports as good, and raising it shrinks `PanelBottomFillet`, pushing the footer
back the other way. So only `Sketch006.Constraints[7]` was rebound to a new knob.
The z=0 footer reach did not move at all (that is `FooterReliefRadius`'s tangent
point), so the ledge margin was unaffected.

### `NeckArcFilletRadius` 0.6 — the knuckle blip, and a fillet that ADDS material

```
angle   -37     -36     -35     -34      <- the disc holds r=5.000 to -36.87 deg
radius  5.000   5.114   5.230   5.346       then 0.116 mm/DEGREE. Tangent = 5.0008.
```

`HingeNeckDrop` 3.0 puts the neck's flat bottom at `z = axis - 3`, which chords
the R5 disc at `atan2(-3, 4) = -36.87 deg`. A 53 deg crease, on both knuckles.

**The corner is CONCAVE, so the fillet FILLS it and EATS clearance** — claimed
here as convex and "can only improve clearance", which the first measurement
disproved. Sized by sweep, not argument:

```
R 0.2/0.4  gap at 90 deg 0.4000, limiting contact = socket flat chord
R 0.6      gap 0.4000, limiting contact MOVES elsewhere   <- chosen
R 0.8      gap 0.3987   fails the nozzle-width export gate
```

After: the departure from the circle begins at -40 deg and ramps 0.003 ->
0.013 -> 0.035 mm/deg. Tangent-continuous; the crease is gone.

### Also learned

- **`is_modified` and a clean audit both passed while the disk held none of this work.**
  Bradley's ramp and three deletions existed ONLY in memory for the whole session. Diff
  memory against disk with `zipfile` inside FreeCAD before trusting any status signal.
- **The slicer's "floating cantilever" is not an island.** Rasterizing every layer of the
  sliced gcode found **0 islands** in 348 layers, and layer 1 already spans the full
  footprint. h3liØ's box has *more* unsupported area (255.6 mm²) and no warning.
- **Creality's gcode lands in temp whether or not the export succeeds** — recover it from
  `.../crealityprint_model/<Day>/<HH_MM_SS>#<pid>#<n>/Metadata/.<pid>.N.gcode`.

---

## TENTH ROUND — 2026-09-16 — the ramp reshape (macro 52)

The frame was never the limit; the CURVE was. Same frame, same wall guard, same
landing, same `RampMinWall`, **no dimensional change whatsoever** — only the
three interior spline poles moved:

```
old poles   (36.42, 5.39)  (36.01, 1.96)  (34.09, -0.03)
new poles   (36.50, 6.08)  (35.82, 2.09)  (34.31,  1.98)

min ramp angle, MEASURED ON THE SOLID   5.38 deg -> 19.88 deg
geometric ceiling                                   20.67 deg
rear wall minimum                       1.982 -> 0.853 mm  (guard 0.80)
```

The old third pole sat at `z = -0.03`, level with the `(29, 0)` endpoint, so the
curve ran into its landing horizontally. The new one carries the descent outward
and arrives at ~21 deg.

### THE PAYOFF IS A REDISTRIBUTION, NOT A REDUCTION — say so

```
overhang band    before    after
< 20 deg          410.7      0.0     <- eliminated
20-30               0.0   1191.8
30-45             240.2      0.0
45-60             698.9    698.9
> 60              128.7    128.7
TOTAL            1515.3   2019.4     <- went UP
```

Everything under 20 deg is gone, and total unsupported area **rose 33 %** because
a surface descending steadily at 20 deg is longer than one that collapses to
flat. That is the right trade given print 5's finding that curved, steeper
overhangs print while flat ones droop — but the total going up is a real cost
and belongs in the record, not buried under the headline.

### MEASURE THE SOLID. THE CURVE FLATTERS.

The spline's own minimum angle is **0.34 deg**; the solid's is **5.38 deg**. The
difference is that the curve's last stretch is buried inside the footer and is
not box surface at all. Optimising or reporting against the curve overstates
both the problem and the fix.

### A CURVE-LEVEL CONSTRAINT IS NOT A SOLID-LEVEL ONE

The first search asked only that the CURVE stay outboard of
`cavity + RampMinWall`. Its winning poles built a solid measuring **0.759 mm** of
rear wall against the 0.80 guard — 0.041 mm inside, caught by macro 52's guard.
Finite sampling and the pocket being `UpToFace` both contribute. The search now
adds **0.10 mm of margin**, costing 0.7 deg of angle and buying a solid that
actually clears.

### AN UNCONSTRAINED SEARCH WILL TRADE AWAY WHAT YOU LIKE

Left free, the optimiser scored marginally BETTER (20.05 deg) by leaving the rear
face at **65.8 deg instead of 90** — putting a crease exactly where Bradley had
said the result was good, to buy half a degree lower down. Pole 1 is now locked
to `x = Depth/2`.

**`RampPole1In` is BOUND to `RampOvershoot`.** Since
`pole1.y = (Depth/2 + RampOvershoot) - RampPole1In`, the equality
`RampPole1In == RampOvershoot` **is** the vertical-top-tangent condition. Leaving
it as a free 2.0 that happens to match would be the `LidTopThickness` mistake a
fourth time.

### A RELATIVE GATE IS NOT IDEMPOTENT

Macro 52 first gated on "steeper than before" and then **failed itself** —
`ramp did not get steeper: 20.57 -> 19.88` — where 19.88 was the intended result
and 20.57 was a rejected candidate that had breached the wall guard on the prior
run. Re-running compares against whatever the model currently holds, not the
original. Gate on an ABSOLUTE floor (`RAMP_MIN_ANGLE` 15.0) and log the delta.

---

## ELEVENTH ROUND — 2026-09-16 — print 7 sliced, and the first SLICE-level check

Every verification before this round measured the CAD solid. This one measures the
**toolpaths** — what the printer will actually do. The two can disagree: a clearance
that survives the model can still be closed up by the slicer, and nothing in this
file had ever looked.

`scripts/gcode_island_check.py` is the re-runnable version of the ad-hoc check round 9
ran once and threw away.

### The slice

| | |
|---|---|
| variant | **60-card, fluted, with name plate** |
| file | `gcode/Object_1_PLA-CF_2h39m.gcode`, 341 layers, 77.01 mm |
| **material** | **Hyper PLA-CF** (slot 1 / T0), 220 °C / 50 °C bed |
| profile | stock `0.16mm Standard @Creality K2 Plus 0.4 nozzle` — **NOT** the `- CardBox` profile |
| walls / shells | 2 walls, 5 top / 4 bottom; infill **15 %** (was 10) |
| supports / brim | disabled / auto — none generated, no `;TYPE:Brim` in the file |
| estimate | **2 h 39 m, 97.01 g** |

**Prints 1–4 PLA, 5–6 PETG, 7 PLA-CF.** The three hinge clearances still hold PLA
values and have now been asked to work in three materials. They survived PETG, which
bonds across a gap far more readily than PLA-CF will, so PLA-CF is the easier case for
fusion — but CF-filled PLA is **more brittle** than plain PLA, and print 1 snapped this
hinge. It is also abrasive: confirm the nozzle is hardened before a 97 g run.

### RESULT — no islands, no fusion

```
islands, 341 layers                       0
fusion events (a region spanning bodies)  0
bed layer                                 2 components (box 5325, lid 7587 mm2)
closest box<->lid approach                0.3391 mm @ layer 105, z 14.03, X 224.9
tightest SAME-body approach               35.35 mm
```

### A GREEN CHECK FROM A CHECK YOU JUST WROTE IS NOT EVIDENCE

The island detector was validated against a synthetic gcode carrying a deliberate
floating square **before** its zero was believed. It found it at (54.98, 54.98) — the
centre of a square floated at 50…60 — and sized it 18 mm², right for a 40 mm perimeter
at 0.42 width. Only then does "0 islands" mean anything.

Keep the control. **A detector that has never gone red has not gone green.** This is
the same family as the `o.State` lesson in round 9, one step earlier: there the check
was looking at the wrong property, here the risk is a check that cannot fire at all.

### PARSING GCODE — FOUR THINGS THAT SILENTLY WRECK A NAIVE PARSER

All four are present in this file and each was verified before any result was trusted:

- **`M83` — extrusion is RELATIVE.** Read as absolute, nearly every move classifies as
  a retraction and the part comes out empty. The script aborts if it sees no `M83`.
- **31 463 `G2`/`G3` arc moves.** The flutes, the ramp and the knuckles are arcs.
  Chording them straight loses real geometry; they are flattened to a 0.02 mm sagitta.
- **`;WIDTH:` varies per segment.** One nominal width misjudges coverage.
- **`EXCLUDE_OBJECT_START/END`** gating, or prime lines count as part of the object.

### THE 82 SUB-NOZZLE LAYERS ARE THE DESIGNED HINGE CLEARANCE, NOT A DEFECT

82 layers hold two regions closer than one nozzle width. The *distribution* is what
identifies them:

```
65 layers   exactly 0.4000 mm    <- HingeTabClearance, dead flat
 8 layers   0.4001 - 0.4008
 3 layers   0.3391 / 0.3850 / 0.3859
```

**A dead-flat number across 65 layers is a designed clearance surviving into the
toolpaths.** That is the third-print lesson read in reverse: there, a gap *collapsing*
toward zero was the jam; here, a gap *refusing to move* is the proof the slicer is not
closing the hinge up.

The body split settles it — the tightest **same-body** approach anywhere in the print is
**35.35 mm**, so all 82 are genuinely box-to-lid at the hinge and none is one wall
nearing another wall of the same part.

Bed interface measures **0.604–0.635 mm** across layers 1–9 against `FooterLidClearance`
0.62. Round 9's fix is present in the gcode, not just in the model.

**The one spot to know about: 0.3391 mm at z 14.03, X 224.9** (closed-frame x ≈ +49.9,
the knuckle). That is 0.06 under the 0.4 design value and under this project's own
0.42 nozzle-width gate. Method error is about ±0.05 mm from 0.1 mm centreline sampling.
Not acted on — prints 5 and 6 came off free in PETG at these same clearances.

### A FIXED SPLIT PLANE CANNOT SEPARATE TWO BODIES THAT INTERLEAVE

The first attempt classified box vs lid with a print-Y plane taken from the bed layer.
From layer 10 up it reported a **negative** gap of exactly **−0.42 mm** — one extrusion
width, which is the signature of a plane slicing through a single continuous wall and
calling its two halves "box" and "lid". Above the bed the bodies interleave at the
knuckle and no fixed plane separates them.

The sound method is to **propagate body identity upward from the bed** through connected
components: label the two bed regions, then give each component the identity of whatever
it overlaps in the layer below. A component overlapping BOTH is a fusion — which is the
check actually wanted, and it is the only way to ask the question without assuming the
answer. Zero occurred.

### THE PRO AI MODULE EARNED ITS 0.16 — LOOK AT WHERE IT SPENT THE LAYERS

Creality's new Pro AI module suggested this profile. "0.16 mm" badly understates what it
did: the print averages **0.226 mm/layer** (341 layers over 77.01 mm) because adaptive
height is carrying the profile. From the project file's
`Metadata/layer_heights_profile.txt` (343 control points, 0.080–0.320):

```
z  0-15    mean 0.116-0.149, pinned to the 0.080 FLOOR 9 times   <- hinge clearance zone
z 20-45    0.320 solid, the CEILING, 144 control points          <- featureless walls
z 65-75    floor again at 66.85, 66.93, 71.04, 71.12             <- front-wall overhangs
```

Measured independently from the gcode, the hinge zone z 4.01 → 14.03 runs **0.124
mm/layer** across 81 layers. The four floor points at z 66.85–71.12 land exactly on the
layers the slicer tags Overhang/Bridge (67.12, 71.19, 71.32).

**It put the finest layers precisely where the clearance and the overhangs are, and
spent 0.32 through the long featureless middle** — 2 h 39 m against the 4 h 12 m fixed /
3 h 43 m variable measured in round 4. Round 5 was hand-trying 0.12 globally; this is
better targeted and faster. Re-run it per variant rather than freezing this profile.

### "NEW AREA" IS CONTAMINATED BY SOLID-OVER-SPARSE — SPLIT IT BY EXTRUSION TYPE

The two largest new-area layers look alarming and are not:

| layer | z | total new | of which Internal Bridge | exterior wall |
|---|---|---|---|---|
| 35 | 5.24 | 5023.6 | 4968.8 | **31.8** |
| 13 | 2.84 | 3378.0 | 3301.1 | **16.9** |
| 227 | 48.33 | 407.7 | 394.5 | **0.1** |

Solid infill over 15 % sparse reads as ~85 % "unsupported" to a raster, and the
"28.6 % supported" figure is just the sparse grid's coverage fraction. **The number that
actually droops is the exterior wall**: peak **49.4 mm²** in any single layer, **1419.5
mm²** over the whole print.

**Do not compare that to round 10's 2019.4 mm².** That was CAD face area on the
100-card; this is projected toolpath area on the 60-card. Different quantities on
different variants — equating them is the `CardPitch` mistake in a new costume.

### Environment — the island check needs FreeCAD's interpreter

The system `python3` has no numpy. FreeCAD's bundled one has numpy 1.26.4 and scipy
1.16.3:

```bash
/Applications/FreeCAD.app/Contents/Resources/bin/python \
    scripts/gcode_island_check.py gcode/FILE.gcode --res 0.15
```

It opens no CAD document and reads only gcode, so it is not a back door around the
MCP-only rule for model files.

**The model-file guard hook matches on the command TEXT, not the target.** A heredoc
writing a script whose *docstring* merely named the model extension was blocked although
it touched no model file. Write such files with the Write tool, or keep the extension
out of shell command text.

### A 3MF IN `gcode/` AND A 3MF IN `3mf/` ARE DIFFERENT KINDS OF FILE

Saving from Creality Print writes a **project**, not a model export:

| | `3mf/<name>.3mf` (tracked) | `gcode/<name>.3mf` (slicer save) |
|---|---|---|
| entries | 4 | 17 |
| content | plain 3MF model, macro 41 `export_3mf` | plate thumbnails, `project_settings.config`, `layer_heights_profile.txt`, slice info |

They can carry the **same filename in two directories** while being different artifacts,
and only one of them is what macro 41's gate checks. `gcode/` already holds
`MagicCardBox-fluted.creality-project.3mf` — follow that convention and suffix slicer
saves `.creality-project.3mf` so the name itself says which it is.

Tracked deliverables were **not** touched this round: all six files in `3mf/` verified
byte-identical to HEAD. Only the gitignored copy in `gcode/` was overwritten.


---

## TWELFTH ROUND — 2026-09-16 — print 8 in PLA-CF, and where the droop actually is

Print 8 came off with the hinge free, the lid flush, both magnet bores open, and the
flutes and name plate clean. **PLA-CF works** — a third material on clearances still
holding PLA values. Bradley's one complaint: "still some slight overhang issues in the
underside of the hinge."

`scripts/mesh_overhang_audit.py` answers that by measuring the SLICED MESH rather than
the CAD solid, which sidesteps reconstructing the print-pose transform entirely — a 3MF
object mesh is already in print orientation.

### THE 60-CARD HEIGHT IS CONFIRMED WITH REAL CARDS

Bradley, with a sleeved deck loaded: **"the 60 card height is perfect."** The stack fills
to the rim with a card lying level on top.

That is the round-8 `CardPitch` resolution validated by the object rather than by
arithmetic. `CardCount` 60 x `THICK_SLEEVE` 0.7033 -> `CardStackHeight` 42.2,
`Height` 45.2 — derived from a per-variant sleeve pitch, on the finding that the thin and
thick sleeves are **different quantities** and were never one number measured three ways.
Both sleeve pitches have now produced a correct box: 101 cards in the 100 at 0.62, and a
correct 60 at 0.7033.

**This closes the longest-running open question in the file.** Card dimensions had been
wrong every single time they were inferred rather than measured; they are now derived from
a measured per-sleeve pitch and both variants check out against real decks.

### WHERE THE OVERHANG IS — and it is not spread out

```
whole part, true overhangs     3136.6 mm2
of which in the hinge band     2669.0 mm2      85%
```

Inside the hinge band the worst-lying material:

```
z  3.2-6.4    775.77 mm2   the RAMP
z  9.6-12.8    21.35 mm2
z 12.8-16.0    44.70 mm2
```

**Only 1.92 mm2 of the entire hinge is genuinely flat** — two ~1 mm2 shelves at
z 6.001 and z 12.399, |x| ~52 (the knuckles). Against the 458.4 mm2 this started at in
round 7, the flat ledge problem is finished.

Those two are almost certainly `HingeSocketFlatZ`'s chord and `HingeNeckDrop`'s flat
neck bottom — **deliberate** flats that each fixed a measured interference (macro 23
cleared 2.25 mm3 at 90 deg with that chord). Chasing 1.92 mm2 risks reopening a solved
problem. Leave them.

### THE REMAINING DROOP IS THE RAMP, AND THE LEVER IS LAYER HEIGHT

The 776 mm2 at z 3.2-6.4 bottoms out at **19.9 deg** — round 10 targeted 19.88 and the
geometric ceiling is 20.67. The geometry is out of room: round 8 established you may
have any two of {thick rear wall, steep exit, no ledge}, never all three.

What is NOT out of room is layer height. Per-layer outward step is `h / tan(19.9 deg)`
= `h x 2.762`, against a 0.42 mm extrusion:

```
h        step      unsupported
0.16     0.442     105%     <- each layer entirely in air
0.12     0.331      79%
0.112    0.309      74%     <- what print 7/8 actually gave the ramp
0.08     0.221      53%
```

Painting **0.08 across print z 4-8** costs about 14 extra layers. A flat 0.12 over the
whole part costs ~300. The fix is local because the defect is local.

Speed is NOT the missing lever: `enable_overhang_speed` is 1 with the 4/4 bucket at
10 mm/s, so the ramp already crawls.

### A BED-CONTACT FACE IS NOT AN OVERHANG

The first run reported **12 980 mm2** in the 0-10 deg band and made the part look
catastrophic. That is layer 1 — down-facing, perfectly flat, and resting on the plate.
Excluded, the real total is 3136.6 mm2.

Two independent methods then agreed on it: **12 915.5 mm2** from the mesh against
**12 911.72 mm2** from macro-free island rasterisation of the gcode — 0.03%. Worth
keeping as a cross-check whenever either number is in doubt.

Same class of error one step earlier: the 3MF object mesh is **centred on the origin,
not bed-referenced**. Filtering "z 0..16" without offsetting measures the MIDDLE of the
part and reports 0.3 mm2 of nothing. The script re-references z; do not hand-roll it.

### A TRUE PLANE AND A CYLINDER TANGENT BOTH READ 0 DEG. THEY ARE NOT THE SAME.

Round 5 warned against chasing the bore apex with a bigger radius. The discriminator is
cheap and belongs in every overhang audit:

```
true plane        one exact normal, z spread 0.0000
cylinder tangent  normals fan out over a finite band
```

**Do not classify on normal COUNT alone.** The 41.6 mm2 patch below was called a
cylinder tangent because it carried 4 distinct normals — which turned out to be 4 stray
facets out of 602, the other 598 being exactly (0,0,-1). Weight by area, or check the
z spread.

### OPEN — a 41.61 mm2 flat at print z 67, the LARGEST on the part, outside the hinge

Surfaced only because the audit was re-run without a band filter:

```
z 67.000   41.61 mm2   602 facets   598 of them normal exactly (0,0,-1)
           x -40.28..40.23   y 56.40..57.20   (a 0.80 mm step)
           7 patches, gaps spaced 4.3 mm = THE FLUTE PITCH
```

So it is a narrow ledge ~80 mm wide that the flutes cut through over `|x| < 12`. It is
**20x the total flat area in the hinge**, and every round since the seventh has been
optimising the hinge while this sat unmeasured. The slicer already knows about it — it
tags Overhang/Bridge at z 67.12 and the adaptive profile pins 0.080 at z 66.85/66.93.

**NOT IDENTIFIED.** Naming the feature needs mapping print z 67 back to the closed
frame; that was not done, and guessing it would be the round-9 "root cause from one
reading" mistake. Next round: identify it before touching anything else.

### h3liØ's RECIPE — verified from the MakerWorld originals

He publishes **per-printer variants**, which is why any single file is a bad sample:

| file | printer | profile | layer | infill | adaptive |
|---|---|---|---|---|---|
| `card_deck_box.3mf` | Bambu X1C | 0.16mm Optimal @BBL X1C | 0.16 | gyroid 10% | none |
| `card_deck_box_25mm_orig.3mf` | Bambu H2D | 0.16mm Balanced Quality | 0.16 | gyroid 10% | none |
| `card_deck_box_20mm.3mf` | Creality K2 Plus | 0.12mm Standard | 0.12 | gyroid 10% | none |

His published notes agree: PLA-CF and matte PLA, 0.4 nozzle, 0.16 layer, 10% gyroid.
Three independent sources. The invariants are **gyroid at 10%** and **no adaptive layer
height anywhere**; the 0.12 appears only in the Creality variant.

**Print 7/8 was ALSO nominally 0.16 — but adaptive pushed the actual average to 0.226
with 144 control points pinned at the 0.32 ceiling.** So the difference is not that he
prints finer, it is that he prints CONSISTENTLY.

**Copying his flat 0.16 would make our ramp worse** (105% unsupported vs the 74% adaptive
already gives it). His recipe suits a part whose overhangs are small, curved and
distributed. **Copy the gyroid 10%; do not copy the layer height.**

Also noted: `outer_wall_speed` 60 on the H2D variant against 200 on the others and on
print 8 — 3.3x, on the surface you actually look at.

### THE PROVENANCE TRAP — a downloaded reference folder held OUR OWN slices

This produced two wrong statements in one session and is the round's cheapest lesson.

`h3liØ/Home Decor/Card Deck Box/` contained `deck_box_25mm_PLA_3h4m.gcode` and
`card_deck_box_25mm.3mf`, both of which look like the author's work. Both were
**Bradley's**: they carry `print_settings_id = ClockFace`, his own profile. Settings read
off them were attributed to h3liØ and were not his.

Then, sampling `card_deck_box_25mm.3mf` alone gave "grid everywhere, no gyroid" — stated
as a conclusion about the whole folder. The **20mm** file had gyroid all along.

```
check FIRST:  print_settings_id / printer_settings_id   <- whose profile is this?
              an STL carries NO settings at all
              a multi-file reference needs ALL files read before any generalisation
```

Same shape as round 9's "do not name a root cause from one reading", applied to
provenance rather than causation. CLAUDE.md rule 5 covers reference geometry being
disposable; it did not cover checking who made the file you are reading.

### MAGNETS — his depth is a DEFECT for us, and it confirms `MagnetProud`

Measured on his original meshes (byte-identical geometry to his STLs — 10 048 and 9 970
triangles match exactly):

```
h3liØ rear/front   Ø4.19-4.20 x 2.160 deep, straight cylinder
h3liØ side walls   Ø4.44 mouth, DOMED bottom, r 2.09 -> 0 over 1.95 mm
ours               Ø4.300 x 1.505 deep, flat bottom, magnet 0.075 PROUD
```

**Bradley, from the part in hand: at his depth the magnets seat BELOW the rim and never
touch.** That is exactly the failure `MagnetProud` was introduced to prevent in the
fourth round — the magnet faces must meet directly, not through two layers of plastic.
**His depth is wrong for us. Do not copy it.** Our depth decision is confirmed, not
challenged.

**And his bore is TIGHTER than ours** (Ø4.20 vs Ø4.30), so "copy his clearance" is
backwards as well. There is nothing to take from his magnet design except possibly the
domed pocket bottom, which removes the flat unsupported ceiling a blind bore otherwise
has.

**The open question is the DIAMETER, and copying cannot settle it.** Printed bores come
out undersize and the amount is a property of this printer, profile and material — not
of anyone's model. It needs a calibration coupon stepping bore diameter against the
actual magnet, which would also serve every future project. Measure the printed bore
before touching `MagnetFit`; if it reads near the modelled Ø4.30 the problem is not the
fit and widening it would be wrong.

(Measurement note: a naive cluster scan reports his pocket as "0.53-0.72 deep". That is
an artifact — the two rim rings sit 2.16 mm apart, further than the 2.0 mm cluster
radius, so they split into separate clusters. The axial profile trace is the reliable
read.)

### `overhang_optimization` — a real key, and UNVERIFIED

```
overhang_optimization            0     <- in print 7/8; the checkbox in Variable Layer Height
slowdown_for_curled_perimeters   0     <- a genuine anti-droop feature, also off
make_overhang_printable          0     <- LEAVE OFF: it reshapes geometry to force <55 deg
```

`overhang_optimization` appears in the project settings but **not** in the stock process
profile, so it is per-project, same family as `layer_heights_profile.txt`. Given it lives
in the Variable Layer Height dialog it probably biases adaptive layers thinner at
overhangs — the automatic version of the band paint. **That is inference, not verified.**
Settle it by toggling it, re-slicing, and diffing the generated
`Metadata/layer_heights_profile.txt` against print 8's.

### Environment

`scripts/mesh_overhang_audit.py` needs numpy + scipy, so it runs on FreeCAD's
interpreter like the island check:

```bash
/Applications/FreeCAD.app/Contents/Resources/bin/python \
    scripts/mesh_overhang_audit.py MagicCardBox.3mf --band 0 16 --detail
```

---

## THIRTEENTH ROUND — 2026-09-23 — a fillet that was being DELETED, not clipped

Bradley added `Lid/Fillet002` in the GUI "after Pocket for additional strength and to
follow the curve of the box", and reported that PanelRelief cuts into it.

It does not cut into it. **It erases it.**

```
gusset added by Fillet002     17.1681 mm3   bbox x 50.5..55.5, y 32.5..36.5, z 10..14
surviving in the final part    0.000000 mm3
percent surviving              0.0000 %
```

Fillet002 sits at position 5 of 11 in the chain, and `PocketPanelRelief` is a **full-width
ThroughAll** cut of `y in [26.5, 37], z in [10, 48.553]`. The fillet's material lies wholly
inside that box, so all of it goes.

### THE COINCIDENCE TRAP, FIFTH FORM — a fillet taken on a face that a later feature MOVES

The previous four were two surfaces sharing one expression, two surfaces that had to stay
coplanar not sharing one, one Param meaning two measurements, and `Pocket008` re-cutting
`Pocket`'s own profile. This one is new:

```
Fillet002 taken on the panel face at   y = Depth/2                      = 36.5
PocketPanelRelief then MOVES it to     y = Depth/2 + HingeSwingClearance = 37.0
```

The fillet was correct where it was built. The relief relocated the very face it was
blending and took the blend with it. **A dress-up feature is only safe upstream of a cut if
that cut does not touch either of its two faces — check the cut's REGION against the
fillet's material, not just its chain position.**

And the reason it went unnoticed: nothing complains. Fillet002 is valid, `Up-to-date`,
expression-bound (`HingeTabRadius - RimRelief`), and the audit passes. It simply
contributes nothing.

> **The measurement that settles it in one line:**
> `feat.Shape.cut(feat.BaseFeature.Shape).common(body.Tip.Shape).Volume`
> — how much of what a feature ADDS actually survives to the tip. Run it on any dress-up
> feature that sits upstream of a cut.

### THE FIX — `PanelNeckGusset`, appended at the TIP

Built on the corner the relief actually leaves behind: `KnuckleArcFillet` Edge26/Edge32,
each 5.0 mm, at `(+/-50.5..55.5, 37, 10)`. At the tip it disturbs no existing named-edge
reference (macro 24's flutes, macro 37's chamfer — same reasoning) and suppressing it
restores the previous shape exactly.

**Bradley's X placement was already right, and the box says why.** Measured box rear-wall
reach over z 10..14:

```
x  45  47  48  49  50   ->  y = 36.500   SOLID REAR WALL
x  51  53               ->  y = 29.5 .. 35.4   socket breakout
```

A gusset anywhere inboard of the socket floor (x = 50.1) drives straight into the box when
closed. That is *why* `PocketPanelRelief` is full width — it is not lazy, it is the
constraint.

### `GussetTangentKeep` — THE DEGENERATE BOUNDARY, MEASURED, NOT ARGUED

The neck top runs from the journal's tangent point to the relieved panel face:

```
from  y = Depth/2 - HingeAxisFromRear   = 31.5     journal R5 top, (31.5, 10)
to    y = Depth/2 + HingeSwingClearance = 37.0     relieved panel face
width =     HingeAxisFromRear + HingeSwingClearance = 5.5      <- Depth cancels
```

A fillet of radius R has its tangent point at `y = 37 - R`, so `R = 5.5` lands it exactly on
the journal's top. That equality **is** the tangency condition (same species as
`RampPole1In == RampOvershoot`). It is also unbuildable:

```
R       4.50  5.00  5.30  5.40  5.45  5.49  5.499  5.4999  5.5
builds   ok    ok    ok    ok    ok    ok    ok     ok     FAIL
```

It consumes the neck-top face exactly and OCC refuses, failing at 5.5 and nowhere below.

```
GussetTangentKeep  0.05   FREE DESIGN INPUT - a GUARD, not a clearance
PanelGussetRadius  5.45   DERIVED = HingeAxisFromRear + HingeSwingClearance
                                    - GussetTangentKeep
```

0.05 because printed roughness here is +/-0.05-0.1 mm, so the residual is below what the
part can express. Third member of the family after `ChamferWallKeep` and `RampMinWall`:
**a knob whose only job is to hold a degenerate case away from zero.**

> **DO NOT REUSE `HingeWrapRadius`.** It is also 5.5, and also
> `HingeTabRadius + HingeSwingClearance` (since `HingeAxisFromRear == HingeTabRadius`). It
> is DEAD and it means something else — a radius about the HINGE AXIS. The gusset arc is
> centred at (31.55, 15.45). Same number, different concept; this project's single most
> repeated failure mode.

### THE 0.05 RESIDUAL DOES NOT BREAK TANGENCY — and the proof is cheap

Measured section at x = 53:

```
Circle R=5.4500 C=(31.5500,15.4500)   (37,15.45)->(31.55,10)   gusset arc
Line   (31.5000,10.0000)->(31.5500,10.0000)  L=0.0500          link
Circle R=5.0000 C=(31.5000, 5.0000)   top at (31.5,10)         journal
```

A circle's tangent is perpendicular to the centre->point ray, so **an arc is horizontal at a
point iff its centre is directly above or below it.** The journal's centre is directly below
its top; the link is horizontal; the gusset's centre is directly above its lower end. One
shared tangent direction — G1 continuous. The 0.05 mm is a vanishingly short horizontal
segment, not a corner.

That is the same construction the box uses on the other side of the joint:

```
box   socket bore R5.4  ->  BackHengeFilet  ->  rear face
lid   journal    R5.0   ->  gusset R5.45    ->  panel face
```

**Assert G1 from the arc CENTRES, not by eye or by a zero-length-flat test.** Macro 55's
first gate demanded `residual_flat == 0`, which is both unbuildable and the wrong question.

### Result

```
volume added  +63.7421 mm3   (analytic 2*(1-pi/4)*R^2*HingeTabThickness = 63.7421, delta -0.0000)
swing 0..75   gusset gap 0.4000   LidBack gap 0.4000   interference 0.000000
swing 90      gusset gap 0.4874   LidBack gap 0.4000   interference 0.000000
mesh @0.02    4382 facets, solid, manifold, no self-intersections
```

The LidBack-vs-box gap stays **flat at 0.4000 across the whole swing** — unchanged. The
gusset's own closest approach is also 0.4000, because its lower end sits essentially on the
journal circle, so it costs no hinge clearance at all.

### ⚠️ A JOINT REFERENCE THAT RE-RESOLVES ONTO THE WRONG FACE — D4's SILENT HALF

This is the round's most dangerous finding. Appending one feature took `Body001` from 21 to
23 faces, and the assembly joint's stored `Body001.Face20` **silently re-resolved**:

```
before   Plane,    area 36.3168 = pi*3.4^2, centre ( 53.5, 31.5,  5.0)   pin-hole end disc
after    Cylinder, R=0.600,               centre (-50.5, 35.79, 1.4)   KnuckleArcFillet,
                                                                        OPPOSITE SIDE
```

No `?`. Nothing Invalid. Joint State `['Up-to-date']`. `Placement1` still read
(53.5, 31.5, 5) because FreeCAD had not re-derived it yet — **so every available check said
fine.** The moment the assembly was recomputed, Placement1 was re-derived from the wrong
face and the lid link jumped to X 73..184.

**And it cannot be fixed by restoring the placement.** Captured P1/P2, restored them,
recomputed — and it re-derived from the bad reference again. As long as the Reference is
wrong, every recompute re-breaks it. The REFERENCE must be repaired.

**Macro 05 would NOT have caught this.** Its gate was `is_dead(ref)`, testing for the `?`
FreeCAD writes on an unresolvable subelement. Ours resolved fine — to the wrong face — so
the macro would have printed "nothing was dead" on a broken joint. Upgraded 2026-09-23 to
`needs_repair()`, which repairs on **dead OR mismatched-against-geometry**. Its `find_disc()`
geometry lookup was already correct and located `Face22` (lid, disc r 3.4) and `Face170`
(box, disc r 3.0) without help.

> This is the seventh round's `PanelBottomChamfer` lesson — *a named reference that
> re-resolves to the wrong thing is worse than one that dies, because nothing complains* —
> now proven to apply to **assembly joint faces**, not just fillet edges. After appending
> ANY feature to a body the assembly references, re-check the joint's faces BY GEOMETRY.

### `is_modified` LIED THREE MORE TIMES IN ONE SESSION

1. `Fillet002` existed **only in memory**; `Lid.FCStd` on disk had never seen it, while
   `isTouched()` was False and nothing was Touched. Hours of GUI work, one crash from gone.
   (Macro 54 was written as the replay BEFORE anything was recomputed, per round 4.)
2. After macro 41, `Params` in memory held `CardCount 100 / CardPitch 0.62` while disk held
   `60 / 0.7033` — **all four documents reported nothing Touched.**
3. The only reliable test remains: read `Document.xml` out of the saved file with `zipfile`
   inside FreeCAD and diff it against memory. It found all of the above in one call.

### Macro 41's `finally` restores a CANONICAL variant — NOT "what you had"

`CANONICAL = 100-fluted-label`. The saved state was **60**-fluted-label. So a plain export
run silently leaves memory on a different card count from disk, with nothing Touched to say
so. Set the variant back deliberately after running it, or save.

### Three mistakes of mine worth not repeating

- **A point-sampling scan locked FreeCAD for ~4 minutes.** `isInside` over ~750k points
  starved the bridge until it finished; even `1+1` timed out. It must not be killed — the
  unsaved `Fillet002` was still in memory. Use `slice()` + edge geometry, which answered the
  same question in 0.2 s and gave exact curve types and radii instead of sampled points.
- **A macro whose baseline is `body.Tip` is not idempotent.** On the second run the tip IS
  the new feature, so the volume gate measured 0.0000 for a gusset that was present and
  correct. Take the baseline from `feat.BaseFeature`, which is right on both passes.
- **A hard-coded gate floor rejected the design value.** `GAP_FLOOR = 0.42 - 0.02` failed a
  measured 0.4000 — which IS `HingeTabClearance`, the documented healthy value. Gate against
  the Param, not a remembered constant.

### Left deliberately undone

`Fillet002` now contributes 0.000 mm3 and is dead weight, but it was NOT removed. Deleting
it changes the shape that `Mirrored`, `Fillet001` (Edge47) and `KnuckleArcFillet`
(Edge16/Edge31) are computed on, and this project has twice had named-edge references
silently re-resolve. Retiring it is its own pass, with a by-position re-check of those three
references afterwards.

### Exports

All six variants rebuilt, `all_ok: True`, every file's hash changed.

```
tag                 gap  bbox                     facets  3mf_tris  comp  on_z   vol_cm3   vd%
100-smooth          0.4  116.81 x 134.26 x 77.0    15188     15188     2   0.0     194.40  0.006
100-fluted          0.4  116.81 x 134.26 x 77.0    31288     31288     2   0.0     186.57  0.005
100-fluted-label    0.4  116.81 x 134.26 x 77.0    34448     34448     2   0.0     183.94  0.005
60-smooth           0.4  116.81 x 114.46 x 77.0    15132     15132     2   0.0     155.97  0.003
60-fluted           0.4  116.81 x 114.46 x 77.0    31232     31232     2   0.0     149.92  0.001
60-fluted-label     0.4  116.81 x 114.46 x 77.0    34392     34392     2   0.0     147.29  0.001
```

Bounding boxes are **unchanged** from the eighth round — the gusset fills an internal corner,
so it costs nothing in envelope or bed space. Facets rose ~2220 per variant.

**The gusset is genuinely in the files, and the volume gate is too loose to prove it.**
Measured mesh-vs-solid delta is 0.001 % on 60-fluted; a MISSING gusset would read
`63.7421 / 149920 = 0.042 %` — forty times larger, but still well inside the 1 % tolerance.
Same weakness the sixth round found when a stale file missing the whole name plate passed at
+0.95 %. Read the delta, do not just check that it passed.

### Footer — asked and answered, 2026-09-23

"Is there a protrusion off the bottom of the footer?" **No. `ZMin` is exactly -4.0000 =
-`FooterHeight`.** The footprint flares monotonically and linearly going down:

```
z  0.000  ->  X +/-55.5000,  Y -36.5000 .. 29.000
z -3.999  ->  X +/-58.4054,  Y -39.4054 .. 25.880
```

2.9062 mm per side over 4 mm, which is exactly
`FooterHeight * tan(FooterTaperAngle) = 4.0 * tan(36 deg)`. That is the designed flared foot
(design direction item 3), not a spur. The rear edge moves the other way (29.000 -> 25.880):
that is the footer relief clearing the folded-open lid. A blue rectangle running past the
part in a screenshot is FreeCAD's **selection bounding box**, not geometry.

---

| Defect | Status |
|---|---|
| D1 / D1b — projected external geometry in the box sketches | ✅ fixed (macro 02) |
| D2 — `Width`, panel grew off-centre | ✅ fixed (side effect of the D7 rebuild) |
| D3 — `Height`, panel grew downward | ✅ fixed (same) |
| D4 — assembly joint dies on face renumbering | ⚠️ recurs by design; re-run macro 05. **It also has a SILENT half** — the stored name can land on a different VALID face, with no `?`, nothing Invalid and State `Up-to-date`, and only break on the next recompute. Macro 05 was upgraded 2026-09-23 to catch that; see the thirteenth round |
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

5. **Reference geometry is DISPOSABLE, and you check it before you build on it.**

   **Naming — `TMP_` or `REF_` prefix means throwaway.** Any body, sketch or object whose
   label starts with either is a mockup: read dimensions off it, never bind to it, delete it
   when the real feature lands. No lifecycle question needs asking. Anything *without* the
   prefix is load-bearing until proven otherwise.

   **Before building on ANY reference object, enumerate what depends on it — and on anything
   it binds through.** Not just the object itself:

   ```python
   [o.Name for o in ref.InList]                    # who points at the mockup
   [o.Name for o in ref.getObject("Binder").InList]  # and at its helpers
   ```

   GUI-built reference geometry creates helper objects nobody asked for. On 2026-09-15 a
   mockup NamePlate body owned a `SubShapeBinder`, and **`Sketch001` — the lid's rear panel,
   hinge-critical — held four external-geometry references to that binder**. They appeared in
   `Binder.InList` as `Sketch001` four times, visible from the moment the mockup was first
   read. Nobody looked until the audit failed, by which point the model carried two DAG
   cycles (see the sixth-round section) and deleting the "disposable" body would have yanked
   the binder out from under the rear panel.

   Reading a reference object's dependents costs one query. It is the `~/.claude/CLAUDE.md`
   verify-before-asserting rule applied to **dependencies** rather than to claims.

   **And keep mockup-specific code out of permanent macros.** Macro 38 shipped with a
   `Body002.Visibility = False` block — logic about a throwaway object embedded in the macro
   that builds the real feature. It became dead code the moment the mockup was deleted.
   Mockup handling belongs in its own one-shot macro (macro 40), never in the feature's.

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
- **Gusset** (`PanelNeckGusset`, macro 55, the body's TIP): an R `PanelGussetRadius` fillet
  on the two knuckle corner edges where the neck's top face meets the relieved panel face,
  at `(±50.5…55.5, 37, 10)`. It exists **only** across the knuckles, because the box's rear
  wall is solid at y = 36.5 out to x = 50 and only falls away inside the socket breakout at
  x ≥ 51 — a gusset any further inboard hits the box when closed. It adds 63.74 mm³ and
  costs **no** hinge clearance: its lower end sits on the journal circle, so the swing stays
  flat at 0.4000.


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
| `Params.FCStd` | VarSet — all parametric variables (**77** today) | — | ✅ |
| `MagicCardBox.FCStd` | The box tub; hinge sockets in the side walls; 4-deep fillet chain | `Params.FCStd` | ✅ clean, tip `Fillet003`. **8 features carry `Shape.isValid() == False`** — pre-existing round-9 debt, unchanged; the tip is clean |
| `Lid.FCStd` | Lid top plate + stepped rear panel + hinge knuckles | `Params.FCStd` | ✅ clean; tip `PanelNeckGusset`, 12 features, **0 shape-invalid**; 2 feature-attached datums remain |
| `MagicCardAssembly.FCStd` | Assembly doc; `App::Link` to both parts, `Revolute` joint | `MagicCardBox.FCStd`, `Lid.FCStd` | ✅ audit clean; joint faces `Body001.Face22` / `Body.Face170` — **re-check BY GEOMETRY after any feature is appended to either body** |

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
Width  = CardLength      + 2*CardClearance + 2*SideWallThickness           = 111.0
Depth  = CardWidth       + 2*CardClearance + WallThickness + RearWallThickness = 73.0
Height = CardStackHeight +   CardClearance +   FloorThickness              =  65.0
```

`Depth` gained `RearWallThickness` (3.0) in the eighth round — front and rear walls are no
longer the same knob. Interior stays **68.000**, asserted; the rear face moved OUT.

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
  CardPitch = 0.62           (mm per sleeved card - A PROPERTY OF THE SLEEVE, see below)
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

  **RESOLVED 2026-09-15 — THE CALIPER READINGS WERE NEVER IN CONFLICT.** Everything above
  tries to reconcile 0.58, 0.62 and 0.69 as one number measured three ways. They are not
  one number: **`CardPitch` is a property of the SLEEVE.** The 0.69 dismissed here as a
  19 % overread lands almost exactly on the 0.6867 that Ryan's thicker sleeves actually
  need — it was measuring a different sleeve, and it was right. `CardPitch` now lives
  per-variant in macro 41's MATRIX (`THIN_SLEEVE` 0.62 / `THICK_SLEEVE` 0.7033). See the
  eighth-round section; the reasoning there supersedes the reconciliation attempts below.

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
  `RearWallThickness` **3.0** (new, macro 48 — the box REAR wall gets its own knob because
  `WallThickness` also drives the front wall, the hinge neck and `Depth` itself. Raising it
  pushes the rear face OUT, never into card space, and it is what let the ramp's minimum
  wall double to 1.982 mm while the flat ledge went to zero),
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
  `MagnetFit` — **RETIRED by macro 53. It was ONE knob for TWO ORIENTATIONS.** Split into:
  `MagnetFitHorizontal` **0.35** (the BOX pockets, whose axis prints HORIZONTAL; bore
  Ø4.700) and `MagnetFitVertical` **0.15** (the LID pockets, axis prints VERTICAL; bore
  Ø4.300, unchanged). Measured on print 8 at a shared Ø4.300: box printed **3.75–3.80**,
  i.e. *smaller than the Ø4.00 magnet* and impossible to insert, while the lid printed
  4.05–4.25. A horizontal bore has an unsupported top arc and loses 0.50–0.55; a vertical
  bore tracks nominal and loses 0.05–0.25. **Do not tighten the lid** — its problem is
  SPREAD (0.20 mm range), not mean, and tightening pushes the low end under Ø4.00.
  (History: 0.05 was a CAD fit that printed solid; macro 46 took it to 0.15, Ø4.100 ->
  Ø4.300, which fixed the lid and left the box still unusable.),
  `MagnetLeadIn` **0.3** (new, macro 46 — depth of the 45 deg lead-in at each pocket mouth,
  cut as a TAPERED POCKET so there is no named edge to go stale. An ASSEMBLY aid, not a
  fit: the bore is what decides whether the magnet goes in)

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
- **Footer:** `FooterReliefRadius` **3.74** (macro 44 — the relief arc; a free design input,
  AT the lid's swept-envelope limit, so re-measure the swing if raised),
  `FooterHeight` **4.0 (DERIVED = `LidBackThickness`, macro 34 — they must stay
  equal or the part will not sit flat in the print pose)**, `FooterTaperAngle` 36 deg
- **Name plate** (macro 38): `NamePlateInset` 10.0, `BorderRadius` 5.0,
  `NamePlateSink` **0.2** (holds the blank's floor below the flute bottoms; at 0 the floor
  is tangent to flute 2 along the whole X edge and the exported STL self-intersects)
- **Rear-bottom ramp** (Bradley's B-spline, bound by macro 48). The FRAME is parametric and
  the curve is offsets from it, which is why the whole thing tracks `Depth`:
  `RampBottomY` 29.0 (where it lands — must stay inside the footer's reach at z=0 or the
  ledge returns), `RampTopZ` 8.0, `RampOvershoot` 2.0, `RampUndercut` 2.0,
  `RampPole1In` **BOUND to `RampOvershoot`** (that equality IS the vertical-top-tangent
  condition — see the tenth round; do not free it), `RampPole1Up` 8.0812,
  `RampPole2In/Up` 2.6794/4.0859, `RampPole3In/Up` 4.1874/3.9787 — **optimised by macro
  52, not hand-tuned; MOVE THEM TOGETHER or the curve kinks**,
  `RampMinWall` **0.8 — a GUARD, not a driver**: no expression references it; macro 48
  measures the built solid's rear wall against it and refuses if breached. Do not "clean it
  up" as a dead Param.
- **RETIRED in the eighth round** (macro 49, with the cascade): `HingeChamferSize`,
  `FooterReliefChamfer`, and `ChamferWallKeep` — the last of which was kept alive ONLY by
  `HingeChamferSize`'s own expression and read as in-use until the moment it wasn't.
  `HingeWrapRadius` 5.5 and `FluteCountSide` 15 are ALSO dead but predate that round; they
  were reported rather than removed.
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
- **LidBack gusset** (macro 55, 2026-09-23 — blends the hinge neck's top face into the
  relieved rear-panel face, on the two knuckle corner edges at `(±50.5…55.5, 37, 10)`, so the
  lid's profile rolls off the journal the way the box's rolls off its bore):
  `PanelGussetRadius` **5.45 (DERIVED = `HingeAxisFromRear + HingeSwingClearance -
  GussetTangentKeep`** — the first two terms ARE the neck-top width, and that equality IS the
  tangency condition; do not free it),
  `GussetTangentKeep` **0.05 — a GUARD, not a clearance.** At 0 the fillet consumes the
  neck-top face exactly and **OCC refuses to build it** (measured: builds at 5.4999, fails at
  5.5). Same family as `ChamferWallKeep` and `RampMinWall`.
  **NOT `HingeWrapRadius`** — that is also 5.5 and also `HingeTabRadius +
  HingeSwingClearance`, but it is DEAD and means a radius about the HINGE AXIS; the gusset
  arc is centred at (31.55, 15.45).
- **Flutes:** `FluteCountFront` 24, `FluteCountSide` 15, `FluteRadius` 2.5, `FluteDepth` 0.7,
  `FluteMargin` 6.0, `FluteStartZ` 12.0
- **Finger slot:** `FingerSlotWidth` 30.0, `FingerSlotDepth` 61.0 (runs to the floor as of
  2026-09-13 so the whole stack can be gripped)
- **Clearances (one per interface, never merged):** `HingePinClearance` 0.4,
  `HingeTabClearance` 0.4, `HingeSwingClearance` 0.5, `CardClearance` 1.0,
  `FooterLidClearance` **0.62** (new, macro 50 — box footer vs the folded-open lid WHERE
  THEY MEET THE BED. Its own knob because HingeSwingClearance also drives seven
  hinge-internal features, and raising that shrinks PanelBottomFillet and pushes the
  footer back the other way. Bounded above by RampBottomY),
  `NeckArcFilletRadius` **0.6** (new, macro 51 — blends the 53° crease where the neck's
  flat bottom chords the knuckle disc at −36.87°. The corner is CONCAVE so this ADDS
  material and EATS full-open clearance: 0.8 drops the 90° gap to 0.3987 and fails the
  nozzle-width gate)

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

This script flags **exactly five things** — read from the source 2026-09-15, not from
memory:
- Sketches with 0 constraints (`UNCONSTRAINED`)
- Sketches with constraints but `FullyConstrained=false` (`UNDERCONSTRAINED`)
- Sketch dimensional constraints with no expression binding (`UNBOUND DIMENSION`)
- Sketches attached to feature faces (`DAG RISK`)
- Feature numeric properties with no expression binding (`UNBOUND FEATURE DIM`)

**IT DOES NOT CHECK FOR DEAD PARAMS.** This file claimed it did — "Params variables
used nowhere (dead Params)" — and that was simply false; there is no such check in the
228-line script, and `grep -i "dead\|unused\|varset"` returns nothing. On 2026-09-15 the
audit passed clean while the VarSet carried **five** unreferenced Params. Dead Params are
a MANUAL job; macros 42 and 49 are the prior art.

**And "referenced by no expression" is not the same as "dead".** `RampMinWall` is read by
macro 48's rear-wall guard, never by an expression. A naive sweep would delete it and
silently remove a safety check. Check whether a MACRO consumes it before removing
anything.

The script is authoritative for what it checks. If it reports violations, fix them via a
`macros/*.FCMacro` change before saving or committing — never by direct coordinate edits
or FCStd XML surgery.

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

### THE CHECKS THAT PASS WHILE THE MODEL IS WRONG — 0: SHAPE HEALTH

**0. `o.State` says nothing about shape health. Use `Shape.isValid()`.**

Added 2026-09-15, and it is the one that hid the longest. Nine features in
`MagicCardBox/Body` carry `Shape.isValid() == False` ("Unorientable shape",
three also not closed) while every one of them reports `State ['Up-to-date']`.
Every macro in rounds 8-9 gated on `"Invalid" in o.State` and reported "all
checks pass"; the audit script never looks at shapes at all; the export gates
check only the Tip, which really is clean.

```python
[o.Name for o in body.Group
 if hasattr(o, "BaseFeature") and not o.Shape.isValid()]   # run this
o.Shape.check(True)                                        # says WHAT is wrong
```

The debt is pre-existing and the Tip is valid, so gate on it as a REGRESSION
(fail if the count grows) rather than pass/fail — `chain_validity()` in macros
50 and 51 does exactly that. And note the corollary: **a mid-chain feature can
look broken in the viewport while the part is fine.** Selecting a feature draws
THAT feature's shape, not the body's.

### THE CHECKS THAT PASS WHILE THE MODEL IS WRONG — 1-4: CLEARANCE, STRUCTURE, REACH

Learned the expensive way, 1 and 2 on 2026-09-13, 3 and 4 on 2026-09-23. They all share one
shape: **the obvious test returns green because it is looking somewhere the defect is not.**
Run them BY HAND after any change to a moving interface or a feature tree — no script here
catches any of them.

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

**3. A feature can be valid, bound, Up-to-date AND CONTRIBUTE NOTHING. Ask what survives to
the tip.**

Added 2026-09-23. `Lid/Fillet002` was valid, expression-bound, `Up-to-date`, audit-clean —
and 100 % of the 17.1681 mm³ it added was removed by a later full-width cut. Nothing in this
project's toolchain asks the question, so ask it directly:

```python
added    = feat.Shape.cut(feat.BaseFeature.Shape)        # what this feature ADDS
survives = added.common(body.Tip.Shape).Volume            # how much reaches the part
```

Run it on any dress-up feature (fillet/chamfer) that sits UPSTREAM of a cut. And note the
trap is not merely chain order: the cut had **moved the very face the fillet was blending**
(`y = Depth/2` → `y = Depth/2 + HingeSwingClearance`). Compare the cut's REGION against the
feature's material, not just their positions in the tree.

**4. After appending ANY feature, re-check the assembly joint's faces BY GEOMETRY.**

Face counts shift, and a stored joint reference can re-resolve onto a different VALID face —
no `?`, nothing Invalid, State `Up-to-date`, and the placement still reads correctly until
the next recompute re-derives it and throws the assembly across the screen. Restoring the
placement does NOT fix it; the reference must be repaired. `macros/05-repair_hinge_joint`
does this and was upgraded 2026-09-23 to catch the silent case. See the thirteenth round.

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
- `macros/` holds 01-55. Every change from here forward goes in as a `.FCMacro`, symlinked
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

> **SUPERSEDED for print 7 — see the ELEVENTH ROUND section.** The profile below is
> print 5's: PETG, 0.20 mm, the custom `- CardBox` profile, 10 % infill. Print 7 is
> **PLA-CF on the stock 0.16 profile at 15 % infill**, chosen by Creality's Pro AI
> module, and its adaptive layer heights are materially different (0.080 at the hinge,
> 0.320 through the middle). Keep this section as the PETG record; do not read it as
> current.

### MEASURED PROFILE — read off print 5's gcode, 2026-09-15

No longer a placeholder. Pulled from the sliced gcode, not from memory:

| | |
|---|---|
| profile | `0.20mm Standard @Creality K2 Plus 0.4 nozzle - CardBox` |
| printer | Creality K2 Plus, 0.4 nozzle, High Temp Plate |
| layer height | 0.2, first layer 0.2 — **356 layers for 75.98 mm, avg 0.213, so variable layer height is ON** (limits 0.08 / 0.32) |
| walls | 2, arachne. Line width 0.42, inner wall 0.45 |
| shells | 5 top / 3 bottom |
| infill | 10 % grid |
| speeds | outer 200, inner 300, infill 270, first layer 60 mm/s |
| supports | **disabled** — see the cantilever warning below |
| brim | auto |
| estimate | 2 h 40 m 15 s, 84.44 g |

### PRINT 5 IS PETG, AND EVERY CLEARANCE IN THIS MODEL WAS SIZED FOR PLA

Ryan asked for black; the black loaded is `CR-PETG` (tool **T3**, 240 °C / 70 °C bed —
confirmed three ways: active tool, `filament_settings_id` slot 4, and all 84.44 g drawn from
slot 4). **It printed, and the hinge moves freely — see the print 5 result below.**

**The numbers below were chosen against PLA's ~0.2 % shrink and PLA layer bonding:**

```
HingeTabClearance    0.4      knuckle in socket
HingePinClearance    0.4      pin in bore
HingeSwingClearance  0.5      panel vs footer - AND the gap under the cantilever
NamePlateSink        0.2      sized against ~0.1 mm mesh deviation, not material
```

PLA print-in-place wants 0.3–0.4 per side; PETG usually wants 0.5–0.6, bonds far more
readily between layers, and strings more. **If a PETG build ever fuses, open
`HingeTabClearance` and `HingeSwingClearance` first** — both are single Params and the
cascade is already parametric.

The riskiest spot is the 4.5 mm cantilever sitting **0.5 mm above the lid panel**: PETG
droops further at the same overhang and welds to what it lands on. It prints in roughly the
first 80 layers (the compound is shifted so the box underside is print z = 0), so a build
that gets past ~z 20 mm has cleared it — though whether the hinge is actually FREE is only
knowable off the plate.

### PRINT 5 RESULT (PETG, black) — the hinge survived, and the droop is NOT a material problem

**The hinge came off the plate FREE.** PETG, in clearances sized for PLA — `HingeTabClearance`
0.4, `HingeSwingClearance` 0.5, and the 0.5 mm gap under the cantilever — did not fuse. That
was the one failure that cannot be rescued after the fact, and it did not happen. Record it as
a fact about the joint; **it does not mean PETG fixed anything.**

**The lid now sits FLUSH at rest and closes better.** That is `LidSeatClearance` 0.15 doing its
job — the 1.1 mm front lift from print 4 is gone. The seat moved off a knife-edge 1.3 mm from
the pivot (38:1) onto the front rim at 66 mm (1:1).

**Curved overhangs print; flat ones droop.** The two knuckle undersides are cylindrical,
101.7 mm² each, and are *hard to see* on the part. The flat ledge between them — 176.9 mm²,
`X ±50.1`, the span between the knuckles — is the visible defect. Same part, same material,
same layers: the difference is flat vs curved. This is exactly what separates this box from
h3liØ's reference, whose overhangs are small, curved and distributed.

**THE DROOP IS MATERIAL-INDEPENDENT — it did the same thing in PLA.** So it is purely a
function of unsupported span and layer height. Do not chase it with temperatures, materials or
clearances.

  * span: 4.5 mm on print 5 → **1.9 mm** now (macros 43/44, sliced after print 5 went out)
  * layers: ~0.16 effective on print 5 → 0.12, and 0.08 being tried

The stringing visible alongside it is a separate problem — the nozzle traverses an open hinge
gap every layer through that region. Retraction, travel speed and nozzle temperature are the
levers there; model changes will not touch it.

### THE SLICER WILL WARN ABOUT A FLOATING CANTILEVER. THIS IS EXPECTED.

```
It seems object Object_1 has floating cantilever.
Please re-orient the object or enable support generation.
```

**Click OK. Do NOT enable supports, and do not re-orient.** Both of the slicer's suggestions
are wrong for this part:

- **Supports** — measured, the only thing under that cantilever is the lid, 0.5 mm below
  (`HingeSwingClearance`). Support material there prints onto the hinge and welds box to lid.
- **Re-orient** — the lid only opens to 90°; there is no flatter pose. That limit is designed
  in, not a slicer setting.

The cantilever is the down-facing face at closed-frame z = 0, **458.4 mm², x ±55.5 (full
width), y 26.5…31** — 4.5 mm deep, supported only along its inboard edge. Both ends are
pinned: `Depth/2 − HingeTabRadius` = 31 outboard (the hinge fillet tangent), and the lid's
edge at 90° plus `HingeSwingClearance` = 26.5 inboard. It cannot be narrowed without a
smaller knuckle, and `HingeTabRadius` is already capped at 5 by the side wall.

It is a **warning**, not a block — the message says "warnings AFTER slicing models". The
slice has already succeeded when you see it.

### WHEN THE SLICER WON'T SAVE THE GCODE

Two traps, both hit on 2026-09-15:

1. **The sliced gcode already exists in Creality's temp session**, whether or not the export
   succeeded:

   ```
   /var/folders/.../T/crealityprint_model/<Day>/<HH_MM_SS>#<pid>#<n>/Metadata/.<pid>.N.gcode
   ```

   15 MB, full settings block in `; key = value` comments. Read the profile from there rather
   than waiting for a working export.

2. **`app.last_export_path` drifts back to the tracked `3mf/` directory.** In
   `~/Library/Application Support/Creality/Creality Print/7.0/Creality.conf`. These are sticky
   last-used values, so the app rewrites them whenever you save somewhere else — it is not a
   preference you can set once. `scripts/set_slicer_project_dir.py` repoints them at `gcode/`
   (gitignored) and **refuses to run while Creality Print is open**, because the app rewrites
   the conf on exit and would discard the change.


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

Target hardware per `CAD_STANDARDS.md`: Creality K2 Plus (FDM) / ELEGOO Saturn 4.
**Layer height, wall count and material are no longer a TODO — see MEASURED PROFILE at the
top of this section**, read off print 5's gcode rather than assumed.

The hinge clearances (`HingePinClearance`, `HingeTabClearance`, `HingeSwingClearance`) are
material-dependent and get tuned from a real print, not defaults. They currently hold **PLA**
values. Prints 1–4 were PLA; **print 5 is PETG** because black was requested and the black
loaded is CR-PETG. Production in ASA was the original intent and would need its own pass —
ASA shrinks ~0.5–0.7 % against PLA's ~0.2 %, so those three Params cannot simply carry over.
