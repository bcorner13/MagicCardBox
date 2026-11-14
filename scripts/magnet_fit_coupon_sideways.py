#!/usr/bin/env python3
"""
magnet_fit_coupon_sideways.py - MagicCardBox SIDEWAYS (lid-face) magnet pocket coupon, v2.

Why: on coupon v1 (CR-Silk) every round sideways pocket was loose - even Ø3.95 - and all
printed slightly OVAL, wider than tall. A horizontal-axis round bore loses its grip at the
sides. So this coupon is sideways-only, two faces of one wall:

  FRONT face  DOUBLE-D pockets: a Ø DD_HEIGHT circle cut by two VERTICAL flats W apart.
              The flats are straight walls laid by the XY path (accurate), so they grip;
              top and bottom keep clearance where the ceiling droops.
              Label = W, the flat-to-flat width: 3.85 .. 4.25
  BACK face   ROUND pockets, smaller than v1: Ø3.55 .. 3.95

All pockets: depth MAGNET_POCKET_DEPTH, 45 deg lead-in MAGNET_LEAD_IN (built as a hull, so
the flats get the lead-in too). Labels (last two digits) engraved on the slab in front of
each face. The engraved triangle marks the small end on the front side.

Requires: pip install manifold3d trimesh
"""
import sys
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, set_circular_segments

MAGNET_POCKET_DEPTH = 1.505
MAGNET_LEAD_IN      = 0.3
DD_HEIGHT           = 4.40                     # circle the flats are cut from (clears top/bottom)
DD_WIDTHS  = [3.85, 3.90, 3.95, 4.00, 4.05, 4.10, 4.15, 4.20, 4.25]
ROUND_DIAS = [3.55, 3.60, 3.65, 3.70, 3.75, 3.80, 3.85, 3.90, 3.95]

PITCH, MARGIN = 7.0, 4.0
SLAB_T, SLAB_D = 4.0, 26.0
WALL_Y0, WALL_T, WALL_TOP = 10.5, 5.0, 18.0    # 5 mm wall: ~2 mm web between opposing pockets
SIDE_Z = 10.0
LABEL_FRONT_Y, LABEL_BACK_Y = 5.0, 18.0
DIGIT_H, DIGIT_W, STROKE, ENGRAVE = 3.0, 1.8, 0.55, 0.4
SEG = 128
EPS = 0.01
set_circular_segments(SEG)


def box(x0, y0, z0, x1, y1, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def dd_section(height, width):
    """Double-D: circle Ø height intersected with |x| <= width/2 (convex)."""
    circ = CrossSection.circle(height / 2, SEG)
    band = CrossSection.square([width, height + 2], center=True)
    return circ ^ band


def round_section(d):
    return CrossSection.circle(d / 2, SEG)


def sideways_pocket(section_at_mouth, section_nominal, x, y_face, z, direction):
    """Blind pocket built along +Z (mouth at 0), lead-in as a hull of two thin slices,
    then rotated so +Z points INTO the wall. direction=+1 -> into +Y, -1 -> into -Y."""
    t = 0.001
    mouth = section_at_mouth.extrude(t).translate([0, 0, -EPS])
    neck = section_nominal.extrude(t).translate([0, 0, MAGNET_LEAD_IN])
    lead = Manifold.batch_hull([mouth, neck])
    bore = section_nominal.extrude(MAGNET_POCKET_DEPTH + EPS).translate([0, 0, -EPS])
    p = lead + bore
    # sketch-X stays world X, sketch-Y becomes world Z (vertical), extrusion goes into the wall
    # rotate about X: -90 sends +Z -> +Y, +90 sends +Z -> -Y; sketch-Y ends up vertical either way
    p = p.rotate([-90, 0, 0]) if direction > 0 else p.rotate([90, 0, 0])
    return p.translate([x, y_face, z])


SEGS = {'0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', '4': 'bcfg',
        '5': 'acdfg', '6': 'acdefg', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}


def digit(ch, x0, y0, z_top, flip=False):
    w, h, s = DIGIT_W, DIGIT_H, STROKE
    hm = h / 2
    rects = {'a': (0, h - s, w, h), 'd': (0, 0, w, s), 'g': (0, hm - s / 2, w, hm + s / 2),
             'f': (0, hm, s, h), 'e': (0, 0, s, hm), 'b': (w - s, hm, w, h), 'c': (w - s, 0, w, hm)}
    out = Manifold()
    for sg in SEGS[ch]:
        a, b, c, d = rects[sg]
        if flip:   # readable from the back side (rotated 180 deg)
            a, b, c, d = w - c, h - d, w - a, h - b
        out += box(x0 + a, y0 + b, z_top - ENGRAVE, x0 + c, y0 + d, z_top + EPS)
    return out


def label(value, x, y, flip=False):
    lab = f"{int(round(value * 100)) % 100:02d}"
    gap = 0.5
    x0 = x - (2 * DIGIT_W + gap) / 2
    if flip:
        return digit(lab[1], x0, y, SLAB_T, True) + digit(lab[0], x0 + DIGIT_W + gap, y, SLAB_T, True)
    return digit(lab[0], x0, y, SLAB_T) + digit(lab[1], x0 + DIGIT_W + gap, y, SLAB_T)


def build():
    n = len(DD_WIDTHS)
    length = 2 * MARGIN + (n - 1) * PITCH
    xs = [MARGIN + i * PITCH for i in range(n)]
    body = box(0, 0, 0, length, SLAB_D, SLAB_T) + \
        box(0, WALL_Y0, SLAB_T - EPS, length, WALL_Y0 + WALL_T, WALL_TOP)
    cuts = Manifold()
    L = MAGNET_LEAD_IN
    for x, w in zip(xs, DD_WIDTHS):        # front face, pockets go +Y
        cuts += sideways_pocket(dd_section(DD_HEIGHT + 2 * L, w + 2 * L), dd_section(DD_HEIGHT, w),
                                x, WALL_Y0, SIDE_Z, +1)
        cuts += label(w, x, LABEL_FRONT_Y)
    for x, d in zip(xs, ROUND_DIAS):       # back face, pockets go -Y; same small->large order in X
        cuts += sideways_pocket(round_section(d + 2 * L), round_section(d),
                                x, WALL_Y0 + WALL_T, SIDE_Z, -1)
        cuts += label(d, x, LABEL_BACK_Y, flip=True)
    cuts += Manifold.cylinder(ENGRAVE + EPS, 1.5, 1.5, 3).translate([1.8, 1.8, SLAB_T - ENGRAVE])
    part = body - cuts
    return part.translate([-length / 2, -SLAB_D / 2, 0])


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "MagnetFitCoupon-sideways-v2"
    tm = to_trimesh(build())
    assert tm.is_watertight, "mesh not watertight"
    assert len(tm.split(only_watertight=False)) == 1, "more than one body"
    tm.export(out + ".stl")
    tm.export(out + ".3mf")
    print(f"extents {np.round(tm.extents, 2)}  volume {tm.volume:.1f} mm3  tris {len(tm.faces)}")
