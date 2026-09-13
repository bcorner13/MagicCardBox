# MagicCardBox

A parametric hinged-lid storage box for Magic: The Gathering cards, modeled in FreeCAD 1.1.

Two printed parts, no fasteners. The lid is a single piece that carries the rear wall and
pivots on hinge tabs engaging sockets in the box side walls, so the whole back of the box
folds open.

| | |
|---|---|
| Outer envelope | 97 × 69 × 67 mm (`Width` × `Depth` × `Height`) |
| Wall | 2.0 mm nominal, 6.0 mm at the hinged side walls |
| Parts | Box tub + lid (with integral rear wall) |
| Target | Creality K2 Plus — PLA for test, ASA for production |

## Layout

```
MagicCardBox.FCStd        box tub, hinge sockets
Lid.FCStd                 lid top plate + rear wall + hinge tabs (2 bodies, 1 Part)
MagicCardAssembly.FCStd   assembly with a solved Revolute joint
Params.FCStd              VarSet — every parametric variable lives here
3mf/  stl/                tracked print deliverables
gcode/                    slicer output (gitignored, regenerable)
images/                   renders and screenshots
macros/                   project .FCMacro files — all model changes go in as macros
scripts/                  audit_parametric.py
```

## Working on this model

Read `CLAUDE.md` first — it documents the assembly architecture and this project's
parametric debt. `plan.md` has the literal-to-Param mapping for the outstanding work.

Inspect and edit the `.FCStd` files through the FreeCAD MCP bridge only; a PreToolUse hook
in `.claude/settings.json` blocks shell access to them.

Before committing any model change:

```bash
python3 scripts/audit_parametric.py
```

Baseline at bootstrap (2026-09-13) is **19 issues** — all unbound dimensional literals in
the hinge geometry. Target is zero.

## Status

Geometry is ~95% complete and recomputes clean; every body is a single valid solid. Not yet
printed. Remaining work is parametric cleanup (see `plan.md`), then a PLA test print to tune
the hinge clearances.
