# Intent — MagicCardBox

## Goal

A parametric hinged-lid storage box for Magic: The Gathering cards. The box holds sleeved
decks; the lid is a single piece that carries the rear wall and pivots on side-wall hinge
bosses so it swings open and back without a separate hinge part or hardware.

## Constraints

- Must follow `CAD_STANDARDS.md` (mm, watertight/manifold, centered at origin, 2.0–3.0 mm
  nominal wall).
- Must follow the parametric rules in `CLAUDE.md` and `~/.claude/CLAUDE.md` — every
  dimension bound to `<<Params>>#VarSet.*`, no literal numbers in constraints.
- Printable on the Creality K2 Plus without supports where possible; the hinge must print
  in place or assemble without hardware.
- Interior sized to hold sleeved MTG decks (current interior envelope ≈ 97 × 69 × 67 mm
  outer, driven by `Width` / `Depth` / `Height`).
- Target price point $36–$45 per the commercial guardrails in `CAD_STANDARDS.md`.
- Two printed parts: box body and lid. No fasteners.

## Success criteria

- `python3 scripts/audit_parametric.py` reports zero issues.
- Changing `Width`, `Depth`, or `Height` in `Params.FCStd` rescales the whole assembly
  — body, lid, rear wall, and hinge — without breaking a recompute.
- The lid opens and closes on the printed hinge with no binding and no post-print fitting.
