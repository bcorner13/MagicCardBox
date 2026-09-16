#!/usr/bin/env python
"""Rasterize a sliced gcode layer by layer and look for islands.

An ISLAND is a connected region of extrusion in layer N that shares no
footprint at all with layer N-1: it starts in mid-air with nothing under it.
That is the failure the slicer's "floating cantilever" warning gestures at,
and round 9 established the warning is NOT reporting one.  This script is the
re-runnable version of that check.

It also reports, per layer:
  * NEW area   -- solid here, empty below.  What the slicer has to bridge or
                  cantilever out over.  A big number is not automatically bad
                  (print 5: curved overhangs print, flat ones droop) but it is
                  where to look.
  * the worst-supported component, so a near-island reads differently from a
    well-anchored wall.  A component resting on 1 px is technically "supported"
    and physically is not.

PARSER ASSUMPTIONS, all verified against the file before trusting a result:
  * M83 relative extrusion (asserted -- aborts if absent)
  * G2/G3 arcs flattened to a 0.02 mm sagitta, NOT chorded.  This model is
    full of arcs (flutes, ramp, knuckles); treating them as lines loses real
    geometry.
  * per-segment ;WIDTH: used as the stamp width, not one nominal value.
  * EXCLUDE_OBJECT_START/END gating, so prime lines are not counted as part
    of the object.

INTERPRETER: needs numpy + scipy.  The system python3 has neither; FreeCAD's
bundled interpreter has both and is the one to use:
    /Applications/FreeCAD.app/Contents/Resources/bin/python
That is a plain interpreter -- it opens no CAD document and reads only gcode,
so it is not a back door around the MCP-only rule for model files.

Usage:
    <py> scripts/gcode_island_check.py gcode/FILE.gcode [--res 0.15] [--json out.json]
"""
import argparse, json, math, re, sys
import numpy as np
from scipy import ndimage

NUM = r"([-+]?[0-9]*\.?[0-9]+)"


def parse(path):
    """-> (layers, meta).  layers[i] = dict(z, segs=[(x0,y0,x1,y1,width,type)])."""
    rx = {k: re.compile(k + NUM) for k in "XYZEIJ"}
    with open(path, "r", errors="ignore") as fh:
        has_exclude = "EXCLUDE_OBJECT_START" in fh.read(400000)

    x = y = z = 0.0
    width, ftype = 0.42, "?"
    in_obj = not has_exclude
    relative_e = False
    layers, cur = [], None
    arc_tol = 0.02          # mm sagitta -> arc flattening step

    def new_layer():
        nonlocal cur
        cur = {"z": None, "segs": []}
        layers.append(cur)

    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s[0] == ";":
                if s.startswith(";LAYER_CHANGE"):
                    new_layer()
                elif s.startswith(";WIDTH:"):
                    try:
                        width = float(s[7:])
                    except ValueError:
                        pass
                elif s.startswith(";TYPE:"):
                    ftype = s[6:].strip()
                continue
            if s.startswith("EXCLUDE_OBJECT_START"):
                in_obj = True
                continue
            if s.startswith("EXCLUDE_OBJECT_END"):
                in_obj = False
                continue
            if s.startswith("M83"):
                relative_e = True
                continue
            if s.startswith("M82"):
                relative_e = False
                continue

            code = s.split(" ", 1)[0].split(";")[0]
            if code not in ("G0", "G1", "G2", "G3"):
                continue
            body = s.split(";")[0]

            def g(k):
                m = rx[k].search(body)
                return float(m.group(1)) if m else None

            nx, ny, nz, e = g("X"), g("Y"), g("Z"), g("E")
            if nz is not None:
                z = nz
            tx = x if nx is None else nx
            ty = y if ny is None else ny
            # relative E: any positive E is deposition.  Absolute E would need
            # a delta against the previous value -- we assert M83 below.
            extruding = e is not None and e > 0.0

            if extruding and in_obj and cur is not None:
                if cur["z"] is None:
                    cur["z"] = z
                if code in ("G2", "G3"):
                    i, j = g("I") or 0.0, g("J") or 0.0
                    cx, cy = x + i, y + j
                    r = math.hypot(x - cx, y - cy)
                    a0 = math.atan2(y - cy, x - cx)
                    a1 = math.atan2(ty - cy, tx - cx)
                    if code == "G2":                       # clockwise
                        while a1 >= a0:
                            a1 -= 2 * math.pi
                    else:                                  # counter-clockwise
                        while a1 <= a0:
                            a1 += 2 * math.pi
                    sweep = abs(a1 - a0)
                    if r > 1e-9:
                        step = 2 * math.acos(max(-1.0, min(1.0, 1 - arc_tol / r)))
                        n = max(2, int(math.ceil(sweep / max(step, 1e-3))))
                    else:
                        n = 2
                    px, py = x, y
                    for k in range(1, n + 1):
                        ang = a0 + (a1 - a0) * k / n
                        qx, qy = cx + r * math.cos(ang), cy + r * math.sin(ang)
                        cur["segs"].append((px, py, qx, qy, width, ftype))
                        px, py = qx, qy
                else:
                    cur["segs"].append((x, y, tx, ty, width, ftype))
            x, y = tx, ty

    if not relative_e:
        sys.exit("ABORT: no M83 seen -- extrusion is absolute and this parser "
                 "assumes relative.  Fix before trusting any result.")
    layers = [L for L in layers if L["segs"]]
    return layers, {"has_exclude": has_exclude}


def rasterize(segs, res, ox, oy, w, h):
    """Stamp segments as capsules of their own extrusion width."""
    mask = np.zeros((h, w), dtype=bool)
    by_width = {}
    for (x0, y0, x1, y1, wd, _t) in segs:
        by_width.setdefault(round(wd, 2), []).append((x0, y0, x1, y1))
    for wd, group in by_width.items():
        a = np.asarray(group, dtype=float)
        p0, p1 = a[:, :2], a[:, 2:]
        d = p1 - p0
        L = np.hypot(d[:, 0], d[:, 1])
        n = np.ceil(L / (res * 0.5)).astype(int) + 1
        tot = int(n.sum())
        if tot == 0:
            continue
        ends = np.cumsum(n)
        idx = np.arange(tot) - np.repeat(ends - n, n)
        t = idx / np.repeat(np.maximum(n - 1, 1), n)
        pts = np.repeat(p0, n, axis=0) + t[:, None] * np.repeat(d, n, axis=0)
        cc = ((pts[:, 0] - ox) / res).astype(int)
        rr = ((pts[:, 1] - oy) / res).astype(int)
        ok = (cc >= 0) & (cc < w) & (rr >= 0) & (rr < h)
        line = np.zeros((h, w), dtype=bool)
        line[rr[ok], cc[ok]] = True
        # capsule: dilate the centreline by half the extrusion width
        rad = max(1, int(round((wd / 2) / res)))
        yy, xx = np.ogrid[-rad:rad + 1, -rad:rad + 1]
        disc = (xx * xx + yy * yy) <= rad * rad
        mask |= ndimage.binary_dilation(line, structure=disc)
    return mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gcode")
    ap.add_argument("--res", type=float, default=0.15, help="mm per pixel")
    ap.add_argument("--json", default=None)
    ap.add_argument("--min-area", type=float, default=0.10,
                    help="ignore components smaller than this (mm2) -- raster dust")
    a = ap.parse_args()

    layers, meta = parse(a.gcode)
    allseg = np.asarray([s[:4] for L in layers for s in L["segs"]], dtype=float)
    xmin = min(allseg[:, 0].min(), allseg[:, 2].min())
    xmax = max(allseg[:, 0].max(), allseg[:, 2].max())
    ymin = min(allseg[:, 1].min(), allseg[:, 3].min())
    ymax = max(allseg[:, 1].max(), allseg[:, 3].max())
    pad = 1.0
    ox, oy = xmin - pad, ymin - pad
    w = int(math.ceil((xmax - xmin + 2 * pad) / a.res))
    h = int(math.ceil((ymax - ymin + 2 * pad) / a.res))
    cell = a.res * a.res
    st8 = np.ones((3, 3), dtype=bool)

    print(f"file      {a.gcode}")
    print(f"layers    {len(layers)}   grid {w}x{h} @ {a.res} mm/px")
    print(f"footprint {xmax - xmin:.2f} x {ymax - ymin:.2f} mm")
    print(f"exclude-object gating: {meta['has_exclude']}")
    print()

    prev = None
    islands, rows = [], []
    for i, L in enumerate(layers):
        mask = rasterize(L["segs"], a.res, ox, oy, w, h)
        lab, n = ndimage.label(mask, structure=st8)
        area_tot = float(mask.sum() * cell)
        worst = None
        if prev is None:
            new_area = area_tot
        else:
            new_area = float((mask & ~prev).sum() * cell)
            sizes = ndimage.sum(np.ones_like(lab, dtype=float), lab, range(1, n + 1))
            sup = ndimage.sum(prev.astype(float), lab, range(1, n + 1))
            worst = 1.0
            for k in range(1, n + 1):
                ar = float(sizes[k - 1] * cell)
                if ar < a.min_area:
                    continue
                frac = float(sup[k - 1] / sizes[k - 1])
                worst = min(worst, frac)
                if sup[k - 1] == 0:
                    cy, cx = ndimage.center_of_mass(lab == k)
                    islands.append({"layer": i, "z": L["z"], "area_mm2": round(ar, 3),
                                    "x": round(ox + cx * a.res, 2),
                                    "y": round(oy + cy * a.res, 2)})
        rows.append({"layer": i, "z": L["z"], "n_comp": int(n),
                     "area_mm2": round(area_tot, 2),
                     "new_mm2": round(new_area, 2),
                     "worst_support": None if worst is None else round(worst, 4),
                     "types": sorted({s[5] for s in L["segs"]})})
        prev = mask

    print("=" * 66)
    if islands:
        print(f"!! {len(islands)} ISLAND(S) FOUND")
        for isl in islands[:40]:
            print(f"   layer {isl['layer']:>3}  z={isl['z']:.2f}  "
                  f"{isl['area_mm2']:>8.3f} mm2  at ({isl['x']}, {isl['y']})")
    else:
        print(f"NO ISLANDS in {len(layers)} layers. Every region rests on the one below.")
    print("=" * 66)
    print(f"\nbed layer: {rows[0]['n_comp']} component(s), {rows[0]['area_mm2']} mm2\n")

    print("10 layers with the most NEW (unsupported) area:")
    print(f"  {'lyr':>4} {'z':>7} {'new mm2':>9} {'total':>9} {'wsup':>6}  slicer tags")
    for r in sorted(rows[1:], key=lambda r: -r["new_mm2"])[:10]:
        t = ",".join(x for x in r["types"] if x in
                     ("Overhang wall", "Bridge", "Internal Bridge", "Bottom surface"))
        print(f"  {r['layer']:>4} {r['z']:>7.2f} {r['new_mm2']:>9.2f} "
              f"{r['area_mm2']:>9.2f} {r['worst_support']:>6.3f}  {t}")

    print("\n10 layers whose worst-supported component is worst:")
    print(f"  {'lyr':>4} {'z':>7} {'wsup':>7} {'new mm2':>9} {'ncomp':>6}")
    for r in sorted(rows[1:], key=lambda r: r["worst_support"])[:10]:
        print(f"  {r['layer']:>4} {r['z']:>7.2f} {r['worst_support']:>7.4f} "
              f"{r['new_mm2']:>9.2f} {r['n_comp']:>6}")

    ov = [r for r in rows if any(t in r["types"] for t in
                                 ("Overhang wall", "Bridge", "Internal Bridge"))]
    print(f"\nlayers tagged Overhang/Bridge by the slicer: {len(ov)}")
    if ov:
        print("  z: " + ", ".join(f"{r['z']:.2f}" for r in ov[:24]) +
              (" ..." if len(ov) > 24 else ""))

    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"file": a.gcode, "res": a.res, "islands": islands,
                       "layers": rows}, fh, indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
