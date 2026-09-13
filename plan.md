# Plan — MagicCardBox

**Status:** geometry was built manually before this project was bootstrapped. This plan
documents the as-built model and the remaining work to bring it into compliance with
`PROJECT_BOOTSTRAP.md` / `CAD_STANDARDS.md`.

Last verified against the live model via the FreeCAD MCP bridge: **2026-09-13**
(FreeCAD 1.1.3, all four documents open and unmodified).

---

## PARAMETERS

Current `Params.FCStd` → `VarSet` contents (verified live, 5 variables):

| Name | Type | Default | Drives |
|---|---|---|---|
| `Width` | `App::PropertyLength` | 97.0 mm | Box X extent; lid X extent; hinge sketch offset (`Width / 2`) |
| `Depth` | `App::PropertyLength` | 69.0 mm | Box Y extent; lid Y extent (`Depth + WallThickness`) |
| `Height` | `App::PropertyLength` | 67.0 mm | `Pad.Length` (box body); `LidPlane` datum Z offset |
| `WallThickness` | `App::PropertyLength` | 2.0 mm | Lid `Pad.Length`, `RearWall` `Pad001.Length`, front/back wall pocket offset |
| `SideWallThickness` | `App::PropertyLength` | 6.0 mm | `Pocket002.Length` (`Width − SideWallThickness * 2`) |

### Parameters that MUST be added (currently literals in the model)

These are the 19 audit violations. Each literal below needs a VarSet variable and an
expression binding — one knob, one concern (global rule #5), and clearances decoupled per
mating interface (global rule #4).

| Proposed Param | Type | Value today | Replaces |
|---|---|---|---|
| `HingeTabRadius` | Length | 10.0 mm | `MagicCardBox/Sketch001.Constraints[0]` (Radius), `Lid/Sketch002.Constraints[1]` (Radius) |
| `HingePinDia` | Length | 6.0 mm | `MagicCardBox/Sketch001.Constraints[12]`, `MagicCardBox/Sketch002.Constraints[3]` (Diameter) |
| `HingePinClearance` | Length | **absent** | new — per-side clearance between lid pin hole and box boss. Today all three Ø6 features are the *same* literal, i.e. a zero-clearance interference fit. `Lid/Sketch003.Constraints[0]` becomes `HingePinDia + HingePinClearance * 2`. |
| `HingeAxisInset` | Length | 5.0 mm | `MagicCardBox/Sketch001.Constraints[1]` and `[15]`, `MagicCardBox/Sketch002.Constraints[0]` and `[1]`, `Lid/Sketch002.Constraints[9]`/`[10]`, `Lid/Sketch003.Constraints[3]`/`[7]` — the hinge-axis offset from the rear/bottom edges |
| `HingeTabThickness` | Length | 5.0 mm | `Lid/Pad002.Length` (HingeTab) |
| `HingeSocketDepth` | Length | 5.0 mm | `MagicCardBox/Pocket.Length` |
| `HingeTabClearance` | Length | **absent** | new — per-side clearance between the lid hinge tab and its socket in the box side wall. `Pocket.Length` becomes `HingeTabThickness + HingeTabClearance`. |
| `EdgeFilletRadius` | Length | 1.0 mm | `Lid/Fillet.Radius` |
| *(reuse `WallThickness`)* | — | 2.0 mm | `MagicCardBox/Sketch003.Constraints[9]` and `[10]`, `MagicCardBox/Pocket001.Length` — **only if** these genuinely express wall thickness. Verify before binding; if they express something else, give them their own Param. |

> `HingeAxisInset` is listed as a single knob because every site currently holds the same
> 5.0 mm value **and** they describe the same physical thing (where the pivot sits relative
> to the rear/bottom corner). Confirm that reading against the geometry before binding —
> "variables that just happen to have the same current value are still different concepts."

---

## FEATURE TREE (as built)

### `Params.FCStd`
- `VarSet` (`App::VarSet`) — 5 variables above. No other objects.

### `MagicCardBox.FCStd` — the box body (27 objects)
1. `Part` (`Box001`, App::Part) — container
2. `Body` (`Box`, PartDesign::Body)
3. `Sketch` on `XY_Plane` — outer footprint rectangle. Bound: `Constraints[9] → Width`, `Constraints[10] → Depth`. Fully constrained.
4. `Pad` — `Length → Height`
5. `Sketch001` (`HingProfile`) on `YZ_Plane`, `AttachmentOffset.Base.z → Width / 2` — hinge socket profile on the side wall. **4 unbound literals.**
6. `Pocket` — hinge socket cut. **`Length = 5.0` unbound.**
7. `Sketch002` on `YZ_Plane`, `AttachmentOffset.Base.z → Width / 2` — hinge pin/boss circle. **3 unbound literals.**
8. `Pocket001` — **`Length = 2.0` unbound.**
9. `Mirrored` — mirrors the hinge features to the opposite side wall
10. `Sketch003` on `YZ_Plane` — interior cavity profile. `Constraints[8] → WallThickness`; **`[9]` and `[10]` unbound.**
11. `Pocket002` — `Length → Width − SideWallThickness * 2` (hollows the interior)

### `Lid.FCStd` — the lid + integral rear wall (42 objects)
1. `Part` (`Lid`, App::Part) — container holding both bodies
2. `Body` (`Lid001`) — the top plate
   - `DatumPlane` (`LidPlane`) on `XY_Plane001`, `AttachmentOffset.Base.z → Height`
   - `Sketch` (`LidSketch`) — `Constraints[8] → Width`, `[9] → Depth + WallThickness`, `[10] → Depth / 2`. Fully constrained.
   - `Pad` — `Length → WallThickness`
3. `Body001` (`LidBack`) — the rear wall that swings with the lid
   - `Sketch001`, `AttachmentOffset.Base.z → -Depth`; `Constraints[8] → Width`, `[9] → Height`
   - `Pad001` (`RearWall`) — `Length → WallThickness`
   - `Fillet` — **`Radius = 1.0` unbound**
   - `DatumPlane001` — ⚠️ attached to `Fillet.Face6` (**feature face — DAG risk, global rule #3**)
   - `Sketch002` on `DatumPlane001` — hinge tab profile. **3 unbound literals.**
   - `Binder001`, `Binder002` (SubShapeBinder)
   - `Pad002` (`HingeTab`) — **`Length = 5.0` unbound**
   - `DatumPlane002` — ⚠️ attached to `Pad` object, MapMode `ObjectYZ` (feature reference)
   - `Sketch003` on `DatumPlane002`, `AttachmentOffset.Base.z → Width / 2 − WallThickness` — hinge pin hole. **3 unbound literals.**
   - `Pocket`, `Mirrored` — pin hole, mirrored to the other side

### `MagicCardAssembly.FCStd` — fit check (14 objects)
- `Assembly` (`Assembly::AssemblyObject`)
- `Box001` (`App::Link` → `MagicCardBox#Part`) — grounded
- `Lid` (`App::Link` → `Lid#Part`)
- `GroundedJoint` on the box; `Joint` (`Revolute`) between `LidBack.Face13` and `Box.Face21`, axis along X at (46.5, 29.5, 5) in link-local coordinates
- Audit: **clean** (no unbound dims — assembly carries no design dimensions of its own)

---

## CONSTRAINT STRATEGY

- All sketches are already **fully constrained** (verified: `FullyConstrained == True`, DoF 0
  on all 9 sketches across both part documents). The debt is *binding*, not *constraining*.
- Fixes go in as `macros/*.FCMacro` files that: (a) `addProperty` the missing VarSet
  variables if absent, then (b) `setExpression` on the named constraint indices. Idempotent —
  skip properties that already exist, overwrite expressions rather than append.
- Never touch `LineSegment StartX/EndY` or `Circle CenterX/CenterY` to move geometry.
- Retarget `DatumPlane001` off `Fillet.Face6` onto a `PartDesign::Plane` offset from a
  principal plane, then reattach `Sketch002` to it. Same for `DatumPlane002`. This is the
  one change that may shift geometry — do it before the parametric binding pass, verify the
  recompute is clean, and re-check the assembly joint still solves.

---

## VALIDATION

1. `python3 scripts/audit_parametric.py` → must report `0 issues`.
2. Sweep test: set `Width` 97 → 110, `Depth` 69 → 80, `Height` 67 → 75 in `Params.FCStd`,
   recompute all three dependent docs, confirm no errors and no touched objects. Restore.
3. `validate_document` on each doc → all objects healthy.
4. Assembly interference check: `Shape.common()` between lid hinge tab and box socket must
   be > 0 only by the intended clearance, and the closed lid must not intersect the box.
5. Export STL → check manifold, then slice for the K2 Plus and record cost.

---

## REMAINING WORK (ordered)

1. ~~Retarget `DatumPlane001` / `DatumPlane002` off feature references onto datum planes.~~ **Still open** — see "Parameter sweep" below; the scope is now wider than these two datums.
2. ~~Add the missing Params (table above), including the two **absent** clearance knobs.~~ **Done 2026-09-13** — 10 variables added via `macros/01-bind_params.FCMacro`.
3. ~~Bind all 19 unbound dimensions via macro.~~ **Done 2026-09-13** — 19/19 bound, geometry verified bit-identical.
4. ~~Re-run the audit until clean~~ **Done — 0 issues.** Parameter sweep test **FAILED** — see below.
5. Fix the sweep defects (D1–D5 below).
6. Set `HingePinClearance` / `HingeTabClearance` to real values before printing.
7. Export `stl/` + `3mf/`, slice, confirm the $36–$45 target.
8. Test print in PLA; fill in the print profile table in `CLAUDE.md`.

---

## Parameter sweep — result: FAILED (2026-09-13)

Validation step 2 was run after the binding pass. The bindings themselves are correct —
every literal now tracks its Param — but the model **does not survive a parameter change**.
These are pre-existing modeling defects, independent of the 19 bindings, uncovered *because*
the model became parametric enough to sweep. Measured one parameter at a time from a freshly
reloaded document:

| # | Change | Symptom | Root cause |
|---|---|---|---|
| **D1** | `Depth` 69 → 80 | `MagicCardBox/Sketch003` goes **Invalid**, so `Pocket002` cannot rebuild and the box body silently keeps its old shape (vol stays 87462, Y stays ±34.5) | **External-geometry index shift** — measured, not inferred. `Sketch003` is correctly *attached* to `YZ_Plane`, but it dimensions against projected edges of `Mirrored` Face3. At `Depth` 80 that face gains two bounding edges (the hinge cut-out stops coinciding with the rear face and becomes an interior notch), so every external GeoId shifts by two: the top edge moves `-7`→`-9`, the left edge `-8`→`-10`, while the constraints still reference `-7`/`-8`. **Not** a cross-document problem and **not** an attachment problem — a third mechanism that datum/binder discipline does not cover. |
| **D2** | `Width` 97 → 110 | `Lid/Body001` (LidBack) spans X −48.5…61.5 instead of ±55 — grows off-centre, breaking the "centered at (0,0,0)" rule in `CAD_STANDARDS.md` | `Lid/Sketch001` pins one corner with a Coincident to element −5 instead of a Symmetric constraint about the vertical axis. |
| **D3** | `Height` 67 → 75 | `Lid/Body001` spans Z −8…67 instead of 0…75 — the rear wall hangs below the floor and stops short of the lid | `Lid/Sketch001` is anchored at its **top** edge, so added height grows downward. Its Z anchor is not tied to the box floor. |
| **D4** | any of the three | `MagicCardAssembly/Joint` (Revolute) goes **Invalid** | The joint references named faces `Body001.Face13` / `Body.Face21`. Already flagged as a risk in `CLAUDE.md`; now confirmed. |
| **D5** | after D1 fires | Restoring 97/69/67 does **not** restore the geometry — `MagicCardBox/Body` comes back 87571.81 mm³ vs the correct 87461.94 (+109.87). Reproducible. | A failed recompute leaves a stale tip. **Recovery: close all four documents without saving and reopen from disk.** Do not try to fix this forward. |

**Consequence for the next session:** `Width`, `Depth` and `Height` are *not* yet safe to
change. Fixing D1–D3 means removing the feature-face external-geometry reference in
`MagicCardBox/Sketch003` and re-anchoring `Lid/Sketch001` symmetrically — both are geometry
changes and need their own approved plan. D1 is the one that actually breaks the solid.
