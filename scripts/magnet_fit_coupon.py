#!/usr/bin/env python3
"""
magnet_fit_coupon.py - MagicCardBox magnet-pocket calibration coupon.

Two rows of pockets at the SAME diameters, one per print orientation:
  FLAT row      axis vertical   - pockets open on the slab top  (like the box rim)
  SIDEWAYS row  axis horizontal - pockets open on the wall face (like the lid face)

Every pocket copies the real one: depth MAGNET_POCKET_DEPTH, 45 deg lead-in
MAGNET_LEAD_IN at the mouth, 128-segment circles. Labels between the rows are
the last two digits of the diameter (95 = 3.95, 00 = 4.00, 05 = 4.05 ...),
engraved in the slab top, and serve both rows (same X = same diameter).

Print as-is (slab down). Press a magnet into each pocket; the smallest one it
goes into by hand, firmly, is the fit for that orientation.

Requires: pip install manifold3d trimesh
"""
import sys
import numpy as np
import trimesh
from manifold3d import Manifold, set_circular_segments

# ---- values copied from Params (CLAUDE.md, 2026-09-23) -----------------
MAGNET_POCKET_DEPTH = 1.505   # MagnetThickness 1.58 - MagnetProud 0.075
MAGNET_LEAD_IN      = 0.3     # 45 deg, radial = axial
DIAMETERS = [3.95, 4.00, 4.05, 4.10, 4.15, 4.20, 4.25, 4.30, 4.35]

# ---- coupon layout (mm) -------------------------------------------------
PITCH      = 7.0     # pocket centre spacing in X
MARGIN     = 4.0     # X margin beyond first/last pocket centre
SLAB_T     = 4.0     # slab thickness (flat pocket floor = 2.495)
SLAB_D     = 22.0    # slab depth in Y
FLAT_Y     = 6.0     # flat-row pocket centres
WALL_Y0    = 18.0    # wall front face (sideways pocket mouths)
WALL_T     = 4.0     # wall thickness (2.495 behind each sideways pocket)
WALL_TOP   = 18.0    # wall top Z
SIDE_Z     = 10.0    # sideways-row pocket centre Z
LABEL_Y    = 11.0    # label baseline (bottom of digits)
DIGIT_H    = 3.0
DIGIT_W    = 1.8
STROKE     = 0.55
ENGRAVE    = 0.4
SEG        = 128
# crush-rib variant: loose bore, three ribs set the grip (inscribed dia = DIAMETERS)
RIB_BORE   = 4.60    # clears an oval print; the ribs, not the bore, hold the magnet
RIB_R      = 0.40    # rib is a half-round of this radius, full pocket depth

set_circular_segments(SEG)
EPS = 0.01


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def pocket_flat(x, y, z_top, d):
    """Blind bore opening UP at z_top, with a 45 deg lead-in."""
    r = d / 2
    bore = Manifold.cylinder(MAGNET_POCKET_DEPTH + EPS, r, r, SEG) \
        .translate([x, y, z_top - MAGNET_POCKET_DEPTH])
    lead = Manifold.cylinder(MAGNET_LEAD_IN + EPS, r, r + MAGNET_LEAD_IN + EPS, SEG) \
        .translate([x, y, z_top - MAGNET_LEAD_IN])
    return bore + lead


def pocket_side(x, y_face, z, d):
    """Blind bore opening toward -Y at y_face, axis +Y, with lead-in."""
    # build along +Z then rotate so +Z -> +Y
    r = d / 2
    bore = Manifold.cylinder(MAGNET_POCKET_DEPTH + EPS, r, r, SEG).translate([0, 0, -EPS])
    lead = Manifold.cylinder(MAGNET_LEAD_IN + EPS, r + MAGNET_LEAD_IN + EPS, r, SEG).translate([0, 0, -EPS])
    p = (bore + lead).rotate([-90, 0, 0])   # +Z -> +Y
    return p.translate([x, y_face, z])


def ribs(inscribed, angles_deg):
    """Three half-round ribs whose inner tips sit on the inscribed circle, built
    along +Z from 0 to the lead-in bottom (the lead-in stays clear to start the magnet)."""
    out = Manifold()
    rc = inscribed / 2 + RIB_R
    h = MAGNET_POCKET_DEPTH - MAGNET_LEAD_IN
    for a in angles_deg:
        t = np.radians(a)
        out += Manifold.cylinder(h, RIB_R, RIB_R, 32).translate(
            [rc * np.cos(t), rc * np.sin(t), 0])
    return out


def pocket_flat_ribbed(x, y, z_top, d):
    cut = pocket_flat(0, 0, 0, RIB_BORE) - ribs(d, [90, 210, 330]).translate(
        [0, 0, -MAGNET_POCKET_DEPTH])
    return cut.translate([x, y, z_top])


def pocket_side_ribbed(x, y_face, z, d):
    # built in the flat frame (axis +Z, mouth at 0) then rotated so +Z -> +Y.
    # Rib angles chosen so after rotation one rib is at the BOTTOM and none at
    # the top, where the bore ceiling droops.
    r = RIB_BORE / 2
    bore = Manifold.cylinder(MAGNET_POCKET_DEPTH + EPS, r, r, SEG).translate([0, 0, -EPS])
    lead = Manifold.cylinder(MAGNET_LEAD_IN + EPS, r + MAGNET_LEAD_IN + EPS, r, SEG).translate([0, 0, -EPS])
    rb = ribs(d, [90, 210, 330]).translate([0, 0, MAGNET_LEAD_IN])
    p = (bore + lead - rb).rotate([-90, 0, 0])
    return p.translate([x, y_face, z])


# 7-segment digits: segments a..g
SEGS = {
    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
    '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg',
}


def digit(ch, x0, y0, z_top):
    w, h, s = DIGIT_W, DIGIT_H, STROKE
    hm = h / 2
    rects = {
        'a': (x0, y0 + h - s, x0 + w, y0 + h),
        'd': (x0, y0, x0 + w, y0 + s),
        'g': (x0, y0 + hm - s / 2, x0 + w, y0 + hm + s / 2),
        'f': (x0, y0 + hm, x0 + s, y0 + h),
        'e': (x0, y0, x0 + s, y0 + hm),
        'b': (x0 + w - s, y0 + hm, x0 + w, y0 + h),
        'c': (x0 + w - s, y0, x0 + w, y0 + hm),
    }
    out = Manifold()
    for sgm in SEGS[ch]:
        a, b, c, d = rects[sgm]
        out += box(a, b, z_top - ENGRAVE, c, d, z_top + EPS)
    return out


def build(ribbed=False):
    n = len(DIAMETERS)
    length = 2 * MARGIN + (n - 1) * PITCH
    xs = [MARGIN + i * PITCH for i in range(n)]

    body = box(0, 0, 0, length, SLAB_D, SLAB_T)
    body += box(0, WALL_Y0, SLAB_T - EPS, length, WALL_Y0 + WALL_T, WALL_TOP)

    cuts = Manifold()
    for x, d in zip(xs, DIAMETERS):
        if ribbed:
            cuts += pocket_flat_ribbed(x, FLAT_Y, SLAB_T, d)
            cuts += pocket_side_ribbed(x, WALL_Y0, SIDE_Z, d)
        else:
            cuts += pocket_flat(x, FLAT_Y, SLAB_T, d)
            cuts += pocket_side(x, WALL_Y0, SIDE_Z, d)
        lab = f"{int(round(d * 100)) % 100:02d}"
        gap = 0.5
        x0 = x - (2 * DIGIT_W + gap) / 2
        cuts += digit(lab[0], x0, LABEL_Y, SLAB_T)
        cuts += digit(lab[1], x0 + DIGIT_W + gap, LABEL_Y, SLAB_T)
    # orientation marker: small triangle notch at the 3.95 end, slab top front
    tri = Manifold.cylinder(ENGRAVE + EPS, 1.5, 1.5, 3).translate([1.8, 2.0, SLAB_T - ENGRAVE])
    cuts += tri
    if ribbed:   # ID mark: engraved bar beside the triangle = RIBBED coupon
        cuts += box(4.0, 1.4, SLAB_T - ENGRAVE, 12.0, 2.6, SLAB_T + EPS)

    part = body - cuts
    # centre on origin in X/Y (CAD_STANDARDS), bed at Z=0
    part = part.translate([-length / 2, -(WALL_Y0 + WALL_T) / 2, 0])
    return part, xs


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3],
                           np.asarray(mesh.tri_verts), process=True)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "MagnetFitCoupon"
    parts = {}
    for tag, rib in (("plain", False), ("ribbed", True)):
        part, _ = build(rib)
        tm = to_trimesh(part)
        assert tm.is_watertight, f"{tag}: mesh not watertight"
        assert len(tm.split(only_watertight=False)) == 1, f"{tag}: more than one body"
        tm.export(f"{out}-{tag}.stl")
        parts[tag] = tm
        print(f"{tag:7s} extents {np.round(tm.extents, 2)}  volume {tm.volume:.1f} mm3  "
              f"tris {len(tm.faces)}")
    # one plate: plain in front, ribbed behind, 8 mm apart, centred on origin
    a = parts["plain"].copy(); b = parts["ribbed"].copy()
    dy = (a.extents[1] + 8.0) / 2
    a.apply_translation([0, -dy, 0]); b.apply_translation([0, dy, 0])
    scene = trimesh.Scene()
    scene.add_geometry(a, node_name="MagnetFit-plain", geom_name="MagnetFit-plain")
    scene.add_geometry(b, node_name="MagnetFit-ribbed", geom_name="MagnetFit-ribbed")
    scene.export(out + ".3mf")
    print("wrote", out + ".3mf", "(2 objects)")
