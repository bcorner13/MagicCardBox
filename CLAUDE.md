# Project rules — MagicCardBox

This model was built **manually, before the project was bootstrapped**, so it carries real
parametric debt: **19 unbound dimensional literals** across `MagicCardBox.FCStd` and
`Lid.FCStd`, and **two datum planes attached to feature geometry** in `Lid.FCStd`. The
highest-risk item is the hinge: the box boss, the box pocket and the lid pin hole are all
the *same* Ø6.0 literal, so there is **no clearance parameter anywhere in this project** —
a printed lid will bind. Do not "fix" any of this by nudging coordinates. Read the rules
below before touching geometry.

---

## Hard rules (this project)

These restate the global rules in `~/.claude/CLAUDE.md` with project-specific context.

1. **Everything parametric.** The worst offenders are the hinge sketches:
   `MagicCardBox/Sketch001` (HingProfile, 4 literals), `MagicCardBox/Sketch002` (3),
   `Lid/Sketch002` (3), `Lid/Sketch003` (3), plus 4 unbound feature dims
   (`MagicCardBox/Pocket.Length`, `Pocket001.Length`, `Lid/Pad002.Length`,
   `Lid/Fillet.Radius`). The box footprint, pad height and interior pocket **are** bound
   correctly — do not re-do those. See `plan.md` for the proposed Param names per literal.

2. **No fixing geometry by editing raw sketch coordinates.** No prior coordinate-edit
   incident in this project; rule applies preventively. All 9 sketches are already fully
   constrained (DoF 0, `FullyConstrained == True`, verified 2026-09-13), so any urge to
   move a vertex means a missing *Param*, not a missing coordinate edit.

3. **Attach sketches to datum planes, not feature faces.** This project **has** the
   condition the rule exists to prevent, in `Lid.FCStd`:
   - `DatumPlane001` → attached to `Fillet.Face6` (a PartDesign::Fillet face). `Sketch002`
     (the hinge tab profile) sits on it, so the tab inherits topological-naming fragility.
   - `DatumPlane002` → attached to the `Pad` object with MapMode `ObjectYZ`. `Sketch003`
     (the hinge pin hole) sits on it.

   No DAG-cycle error has fired yet, but both are feature references and both must be
   retargeted to `PartDesign::Plane` datums offset from principal planes. **Note the audit
   script does not catch these** — it only checks *sketch* attachment, not datum-plane
   attachment. Check datum planes by hand via `execute_python`.

4. **Clearance concepts stay decoupled.** This project currently uses **zero** clearance
   Params — that is the debt, not the design. Two are required and neither exists yet:
   - `HingePinClearance` — lid pin hole ↔ box hinge boss (per side). Today both are the
     same Ø6.0 literal: an interference fit.
   - `HingeTabClearance` — lid hinge tab ↔ its socket pocket in the box side wall. Today
     `Pad002.Length` and `Pocket.Length` are both the same 5.0 literal.

   Never collapse these two into one knob, and never reuse `WallThickness` for either.
   PLA needs ~0.1 mm less per side than ASA; size the defaults for the test material and
   re-tune after the first print.

---

## Assembly architecture

Two printed parts, no fasteners, no separate hinge component.

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

`Params.FCStd` → `VarSet` currently holds **5** variables, all `App::PropertyLength`,
all in one group — there is no clearance group yet:

- **Geometry:** `Width` (97 mm), `Depth` (69 mm), `Height` (67 mm),
  `WallThickness` (2 mm), `SideWallThickness` (6 mm)
- **Hinge:** *none yet* — `HingeTabRadius`, `HingePinDia`, `HingeAxisInset`,
  `HingeTabThickness`, `HingeSocketDepth`, `EdgeFilletRadius` all need adding
- **Clearances:** *none yet* — `HingePinClearance`, `HingeTabClearance` need adding

The full literal→Param mapping is tabled in `plan.md`. Add missing variables to the VarSet
**first**, then bind — never the other way around.

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
