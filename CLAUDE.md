# Project rules — MagicCardBox

This model was built **manually, before the project was bootstrapped**, and has since been
rebuilt into a parametric knuckle hinge. As of 2026-09-13 the audit is clean and **all three
main dimensions sweep safely**, verified by measurement across W 80-130, D 50-100, H 50-95
(9 cases): every dimension tracks, lid-vs-box swing interference is **0.0000 mm3** over
0-90 deg, and every solid is valid, closed and single.

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
- **`PanelBottomZ` is BOUND, not free.** The lid's rear panel cannot reach the bottom; it
  must start at or above `HingeAxisFromBottom + HingeAxisFromRear` or it digs into the box
  rear wall, and the failure is silent. It is bound to the socket circle's top.
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
  rectangular solid, `Width` × `Depth` × `Height` (97 × 69 × 67 mm today), hollowed from
  the top by `Pocket002` to leave `SideWallThickness` (6 mm) on the ±X side walls. It is
  centered on the origin in X/Y and sits on Z = 0 (bbox −48.5…48.5, −34.5…34.5, 0…67).

- **Lid** (`Lid.FCStd` → `Part` "Lid") is **one part containing two bodies** and is
  L-shaped in section:
  - `Body` ("Lid001") — the flat top plate, `WallThickness` (2 mm) thick, sitting on the
    `LidPlane` datum at Z = `Height`. It overhangs the box in +Y by `WallThickness`
    (`Depth + WallThickness` = 71 mm) so it caps the rear wall.
  - `Body001` ("LidBack") — the **rear wall**, a full-height panel (Z 0…67) at the +Y end
    that swings *with* the lid rather than being part of the tub. This is why the box tub
    has no rear wall of its own.

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

---

## Design direction (stated by Bradley 2026-09-13 — not yet modelled)

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

2. **Finger slots front and back** to lift the cards out. Needs its own Params
   (slot width, depth, corner radius) — do not borrow `WallThickness` or any hinge knob.

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
| `Params.FCStd` | VarSet — all parametric variables (5 today) | — | ✅ |
| `MagicCardBox.FCStd` | The box tub; hinge sockets in the side walls | `Params.FCStd` | ⚠️ 11 unbound literals |
| `Lid.FCStd` | Lid top plate + integral rear wall + hinge tabs | `Params.FCStd` | ⚠️ 8 unbound literals + 2 feature-attached datums |
| `MagicCardAssembly.FCStd` | Assembly doc; `App::Link` to both parts, `Revolute` joint | `MagicCardBox.FCStd`, `Lid.FCStd` | ✅ audit clean |

**Known debt (read before poking at these):**

- `MagicCardBox.FCStd` — the four hinge-related literals in `Sketch001` (R10, 5, Ø6, 5),
  three in `Sketch002` (5, 5, Ø6), two in `Sketch003` (2, 2), and `Pocket.Length = 5.0` /
  `Pocket001.Length = 2.0`. The footprint sketch, `Pad.Length` and `Pocket002.Length` are
  already bound correctly.
- `Lid.FCStd` — `Sketch002` (R10, 5, 5), `Sketch003` (Ø6, 5, 5), `Pad002.Length = 5.0`,
  `Fillet.Radius = 1.0`, plus the two feature-attached datum planes described in rule #3.
  Retarget the datums **before** the binding pass; that change can move geometry and needs
  a clean recompute plus a re-solve of the assembly joint afterward.
- Nothing is broken — all three shape-bearing docs recompute clean and every body is a
  single valid solid. This is debt, not breakage.

---

## Params variables (summary)

**The box size is DERIVED from the card spec** (macro 14) — `Width` / `Depth` / `Height` are
still Params and still drive everything downstream, but they are no longer free numbers:

```
Width  = CardLength      + 2*CardClearance + 2*SideWallThickness   = 105.0
Depth  = CardWidth       + 2*CardClearance + 2*WallThickness       =  72.0
Height = CardStackHeight +   CardClearance +   FloorThickness      =  63.0
```

Interior is therefore **93.0 x 68.0 x 61.0 mm**, verified from the solid, holding a
91 x 66 x 60 stack of 60 sleeved cards with 1 mm all round and 1 mm headroom.
To go back to free knobs, clear those three expressions.

- **Cards (the input):** `CardLength` 91.0, `CardWidth` 66.0, `CardStackHeight` 60.0.
  Only `CardStackHeight` was measured by caliper; the two card dimensions **assume** a
  standard 88 x 63 card plus a sleeve. Measure and correct them — everything follows.
- **Geometry:** `Width`, `Depth`, `Height` (derived), `WallThickness` 2.0,
  `SideWallThickness` 6.0, `FloorThickness` 2.0, `EdgeFilletRadius` 1.0
- **Footer:** `FooterHeight` 2.0, `FooterTaperAngle` 36 deg
- **Hinge:** `HingeTabRadius` 5.0 (capped by the side wall — see the header),
  `HingePinDia` 6.0, `HingePinLength` 3.0, `HingeAxisFromRear` 5.0,
  `HingeAxisFromBottom` 5.0, `HingeTabThickness` 5.0, `PanelBottomZ` (derived), `RimRelief` 1.0
- **Finger slot:** `FingerSlotWidth` 40.0, `FingerSlotDepth` 25.0
- **Clearances (one per interface, never merged):** `HingePinClearance` 0.4,
  `HingeTabClearance` 0.4, `HingeSwingClearance` 0.5, `CardClearance` 1.0

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
change made things worse.

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
- `macros/` is empty — the model predates the bootstrap. Every change from here forward
  goes in as a `.FCMacro`.

---

## Print profile

**No successful test print yet — profile TBD.**

Target hardware per `CAD_STANDARDS.md`: Creality K2 Plus (FDM) / ELEGOO Saturn 4. Test in
PLA, production in ASA. Fill this section in from the actual first print, not slicer
defaults — the hinge clearances (`HingePinClearance`, `HingeTabClearance`) will be tuned
from that print and are material-dependent.
