#!/usr/bin/env python
"""Measure true down-facing overhang area on an exported mesh, by angle band.

Answers "where does this part actually droop", on the geometry that was sliced
rather than on the CAD solid, so no print-pose transform has to be
reconstructed -- a 3MF's object mesh is already in print orientation.

ANGLE CONVENTION matches the project's: measured FROM HORIZONTAL, so
    0 deg  = a flat down-facing ledge, the worst case
   90 deg  = a vertical wall, not an overhang at all
This is the same sense as the round 10 bands ("< 20 deg eliminated").

TWO TRAPS THIS HANDLES, both of which produced wrong numbers first time:

  * A 3MF object mesh is centred on the origin, NOT bed-referenced.  Filtering
    by "z 0..16" without offsetting measures the MIDDLE of the part.  z is
    re-referenced to the mesh minimum here.

  * The BED-CONTACT FACE is down-facing and perfectly flat, so it lands in the
    0-10 deg band and swamps everything.  It is layer 1, not an overhang.  It
    is excluded by --bed-tol and reported separately; on MagicCardBox it is
    ~12 915 mm2 against ~3 137 mm2 of genuine overhang.

  * --detail additionally separates a REAL planar ledge from the tessellated
    tangent of a cylinder.  A cylinder's lowest generatrix reads 0 deg too, but
    spreads its normals over a finite band; a true plane shows a single exact
    normal and ZERO z spread.  Round 5 warns specifically against chasing the
    former with a bigger radius.

INTERPRETER: needs numpy + scipy; the system python3 has neither.  Use
    /Applications/FreeCAD.app/Contents/Resources/bin/python
It reads only mesh files and opens no CAD document.

Usage:
    <py> scripts/mesh_overhang_audit.py FILE.3mf [--band LO HI] [--detail]
"""
import argparse, sys, struct, zipfile, collections
import xml.etree.ElementTree as ET
import numpy as np

NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
BANDS = [(0, 10), (10, 20), (20, 30), (30, 45), (45, 60), (60, 90)]


def load(path):
    """-> (V, T) for a 3MF (largest object mesh) or a binary STL."""
    if path.lower().endswith('.3mf'):
        z = zipfile.ZipFile(path)
        cands = [n for n in z.namelist()
                 if n.startswith('3D/Objects/') and n.endswith('.model')] \
                or ['3D/3dmodel.model']
        best = max(cands, key=lambda n: z.getinfo(n).file_size)
        root = ET.fromstring(z.read(best))
        V, T = [], []
        for mesh in root.iter(NS + 'mesh'):
            for v in mesh.find(NS + 'vertices'):
                V.append((float(v.get('x')), float(v.get('y')), float(v.get('z'))))
            for t in mesh.find(NS + 'triangles'):
                T.append((int(t.get('v1')), int(t.get('v2')), int(t.get('v3'))))
        return np.asarray(V), np.asarray(T), best
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[80:84])[0]
    dt = np.dtype([('n', '<f4', (3,)), ('v', '<f4', (3, 3)), ('a', '<u2')])
    tri = np.frombuffer(d[84:84 + n * 50], dtype=dt)['v'].astype(float)
    V = tri.reshape(-1, 3)
    T = np.arange(len(V)).reshape(-1, 3)
    return V, T, 'stl'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mesh')
    ap.add_argument('--band', nargs=2, type=float, metavar=('LO', 'HI'),
                    help='also report this print-z slice on its own')
    ap.add_argument('--bed-tol', type=float, default=0.25,
                    help='facets flatter than 5 deg below this z are layer 1, not overhang')
    ap.add_argument('--detail', action='store_true',
                    help='separate true planar ledges from cylinder tangents')
    a = ap.parse_args()

    V, T, src = load(a.mesh)
    p0, p1, p2 = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    nn = np.cross(p1 - p0, p2 - p0)
    L = np.linalg.norm(nn, axis=1)
    ok = L > 1e-12
    nn = nn[ok] / L[ok, None]
    area = L[ok] / 2.0
    ctr = ((p0 + p1 + p2) / 3.0)[ok]
    PZ = ctr[:, 2] - V[:, 2].min()          # bed at 0
    PX, PY = ctr[:, 0], ctr[:, 1]

    down = nn[:, 2] < -1e-6
    ang = np.degrees(np.arccos(np.clip(-nn[:, 2], -1, 1)))
    bed = down & (ang < 5) & (PZ < a.bed_tol)

    ext = V.max(axis=0) - V.min(axis=0)
    print(f"{a.mesh}  [{src}]")
    print(f"  {len(V)} verts, {len(T)} tris, print pose {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f}")
    print(f"  bed-contact face (layer 1, EXCLUDED): {area[bed].sum():.1f} mm2\n")

    def table(sel, label):
        print(f"--- {label} ---")
        tot = 0.0
        for lo, hi in BANDS:
            m = sel & down & ~bed & (ang >= lo) & (ang < hi)
            A = area[m].sum(); tot += A
            print(f"   {lo:>3}-{hi:<3} deg {A:>9.1f} mm2")
        print(f"   {'TOTAL':>11} {tot:>9.1f} mm2\n")
        return tot

    table(np.ones(len(area), bool), "WHOLE PART, true overhangs (0 deg = flat)")
    if a.band:
        lo, hi = a.band
        sel = (PZ >= max(lo, a.bed_tol)) & (PZ <= hi)
        table(sel, f"BAND, print z {lo}..{hi}")
        w = sel & down & ~bed & (ang < 30)
        print(f"worst in band (<30 deg): {area[w].sum():.2f} mm2")
        step = (hi - lo) / 5.0
        z = lo
        while z < hi:
            m = w & (PZ >= z) & (PZ < z + step)
            if area[m].sum() > 0.01:
                print(f"   z {z:>6.2f}-{z + step:<6.2f} {area[m].sum():>8.2f} mm2   "
                      f"x {PX[m].min():7.1f}..{PX[m].max():7.1f}   min angle {ang[m].min():5.1f}")
            z += step

    if a.detail:
        print("\n--- PLANAR LEDGE vs CYLINDER TANGENT (facets under 1 deg) ---")
        f = down & ~bed & (ang < 1.0)
        if not f.any():
            print("   none")
            return
        zs = np.round(PZ[f], 3)
        for zval in sorted(set(zs)):
            m = f & (np.abs(PZ - zval) < 1e-3)
            uniq = collections.Counter(map(tuple, np.round(nn[m], 4)))
            spread = PZ[m].max() - PZ[m].min()
            kind = "TRUE PLANE" if (len(uniq) <= 3 and spread < 1e-3) else "cylinder tangent"
            print(f"   z {zval:>8.3f}  {area[m].sum():>7.2f} mm2  {int(m.sum()):>3} facets  "
                  f"x {PX[m].min():7.2f}..{PX[m].max():7.2f}  "
                  f"normals {len(uniq)}  zspread {spread:.4f}  -> {kind}")


if __name__ == '__main__':
    main()
