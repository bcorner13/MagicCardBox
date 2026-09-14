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

- **Magnetic closure** (macro 19): two pairs of Ø4 x 2 disc magnets, one pair per thick
  side wall, `MagnetFromFront` (8 mm) back from the front face. Centres at
  `x = ±(Width/2 - SideWallThickness/2)` = ±50, `y = -Depth/2 + MagnetFromFront` = -28.
  The box pocket is `z 63…65` (magnet flush with the rim); the lid pocket is `z 65…67`
  with `MagnetSkin` above it, so the two magnet faces meet on the parting plane at
  `z = Height` with **no plastic between them**. Verified from the solid: Ø4.10 bore with
  0.95 mm of side wall each side, solid below, and the box loses 52.79 mm³ against 52.81
  predicted.

  **Skin thins to 0.5 mm at the inboard edge of the lid pocket.** The outermost lid-top
  flute sits at `x = 47` and grazes the hole, which starts at `x = 47.95`. Measured skin is
  1.0 mm across the whole pocket except the first ~0.8 mm, where it falls to 0.5 mm. If that
  ever matters, raise `FluteMargin` (moves the outer flute inboard, away from the magnet) or
  `MagnetSkin` — do not move the magnets outboard, there is only 0.95 mm of wall there.

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

  **BLOCKER FOR THE 60-CARD VARIANT, measured 2026-09-14: `Fillet003` goes Invalid at
  `Height` 40.** Macro 30's dry run drove `CardStackHeight` to 37 and the R 0.6 top-rim
  fillet died — its edges do not survive the rim moving 25 mm. **So the 60-card version is
  NOT a parameter change**; it needs the edge re-pick by position that macros 24 and 29 use.
  Worse, defect D5 applies: restoring `CardStackHeight` left `Fillet003` dead while every
  parameter read correct, and recovery meant closing all four documents without saving and
  reopening. Macro 30's `DRY_RUN` is therefore False by default.

  `FluteStartZ` **12.0 is still absolute**, so a shorter box gets proportionally chunkier
  fluting (53 mm of flute becomes 28 mm at `Height` 40). Cosmetic, not a defect — but decide
  it deliberately when the variant is built.
- **Geometry:** `Width`, `Depth`, `Height` (derived), `WallThickness` 2.0,
  `SideWallThickness` **8.0** (was 6.0; raised by macro 27 — hinge web 0.60 → 2.60 mm and
  magnet wall margins 0.95 → 1.95 mm. Grows the box OUTWARD only; interior is unchanged),
  `FloorThickness` 2.0, `EdgeFilletRadius` 1.0,
  `LidTopThickness` **3.7 (DERIVED = `MagnetThickness + MagnetSkin`, macro 28)**
- **Magnets** (added 2026-09-13, macro 19): `MagnetDia` 4.0, `MagnetThickness` 2.0,
  `MagnetFromFront` 8.0, `MagnetSkin` **1.7** (was 1.0 — the outer lid flute cuts
  `FluteDepth` 0.7 straight out of the skin, leaving **0.30 mm** over the magnet after the
  Width change; now 1.00 mm worst case, measured across the pocket),
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
- **Footer:** `FooterHeight` 2.0, `FooterTaperAngle` 36 deg
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
  hand-set, see the header)**, `BackHingeFilletRadius` 4.0 (socket-breakout overhang),
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
- `macros/` holds 01-18. Every change from here forward goes in as a `.FCMacro`, symlinked
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

**Exports current as of 2026-09-14, both variants, both from the same tree state:**

| | plain | fluted |
|---|---|---|
| facets | 2 012 | 5 636 |
| volume | 163.02 cm³ | 155.43 cm³ |
| watertight / non-manifold / self-int. | ✓ / False / False | ✓ / False / False |
| components | 2 (box + fused lid) | 2 |
| footprint | 113.91 × 132.15 × 74.00 on Z=0 | identical |
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
