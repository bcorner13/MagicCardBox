#!/usr/bin/env python3
"""Inject PrusaSlicer height-range modifiers into an exported MagicCardBox 3MF.

Writes Metadata/Prusa_Slicer_layer_config_ranges.xml (the ONLY name PrusaSlicer 2.9.7
reads - `Metadata/layer_config_ranges.xml` is silently ignored, measured 2026-11-24).
Replaces an existing ranges file, so it is safe to re-run. Geometry is untouched.

Bands, in PRINT z (box upright, lid open), proven on the tarot78 print 2026-11-24:
    0 .. 3        0.20   so the ramp band starts exactly at 3.08
    3 .. 7        0.08   the ~20 deg rear ramp (PETG delaminated at 0.16)
    7 .. 16       0.20   hinge clearance zone
    top-11..top-4 0.15   lid magnet pockets (print z = Depth - 4, i.e. top - 8)
Everything else takes the print profile's layer height (0.25 SPEED was used).
The pocket band follows the PART's height, so it is computed per file from the mesh.

Usage:  python3 scripts/inject_layer_ranges.py 3mf/*.3mf
"""
import re
import shutil
import sys
import tempfile
import zipfile

RANGES_NAME = "Metadata/Prusa_Slicer_layer_config_ranges.xml"
FIXED = [(0.0, 3.0, 0.20), (3.0, 7.0, 0.08), (7.0, 16.0, 0.20)]
POCKET_FROM_TOP = (11.0, 4.0)     # band = (top - 11, top - 4)
POCKET_LH = 0.15


def mesh_height(model_xml):
    zs = [float(z) for z in re.findall(r'<vertex [^>]*z="([-0-9.eE+]+)"', model_xml)]
    return max(zs) - min(zs)


def object_ids(model_xml):
    return re.findall(r'<object id="(\d+)"', model_xml)


def ranges_xml(obj_id, height):
    bands = FIXED + [(round(height - POCKET_FROM_TOP[0], 2),
                      round(height - POCKET_FROM_TOP[1], 2), POCKET_LH)]
    out = ['<?xml version="1.0" encoding="utf-8"?>', "<objects>",
           '  <object id="%s">' % obj_id]
    for lo, hi, lh in bands:
        out += ['    <range min_z="%g" max_z="%g">' % (lo, hi),
                '      <option opt_key="layer_height">%g</option>' % lh,
                "    </range>"]
    out += ["  </object>", "</objects>", ""]
    return "\n".join(out), bands


def inject(path):
    with zipfile.ZipFile(path) as z:
        model = z.read("3D/3dmodel.model").decode("utf-8")
        entries = [(i, z.read(i.filename)) for i in z.infolist()
                   if i.filename != RANGES_NAME]
    ids = object_ids(model)
    if len(ids) != 1:
        raise ValueError("%s: expected one object, found %s" % (path, ids))
    h = mesh_height(model)
    xml, bands = ranges_xml(ids[0], h)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".3mf")
    tmp.close()
    with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in entries:
            z.writestr(info, data)
        z.writestr(RANGES_NAME, xml)
    shutil.move(tmp.name, path)
    return h, bands


if __name__ == "__main__":
    for p in sys.argv[1:]:
        h, bands = inject(p)
        print("%s  height %.2f  %s" % (p, h, "  ".join("%g-%g@%g" % b for b in bands)))
