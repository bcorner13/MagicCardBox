#!/usr/bin/env python
"""Put macro 41's print-pose geometry into a Creality project that has the settings.

THE PROBLEM THIS SOLVES
-----------------------
Two files each hold half of what a printable project needs:

  macro 41's 3mf/<variant>.3mf   correct PRINT POSE (lid swung open about the
                                 hinge axis, lid's two bodies fused into one
                                 solid, both bodies coplanar on the bed) --
                                 but a bare 4-entry model with NO settings.

  a Creality project .3mf        correct SETTINGS (profile, gyroid, filament)
                                 -- but whatever geometry happened to be on the
                                 plate when it was saved.

The FreeCAD 3D_Printer_3mf_Workflow macro merges the other way round, from the
documents as they sit -- and no document is ever in the print pose. The pose is
built in code by macro 41's posed_compound() and thrown away. Exporting the
assembly document gives the LID CLOSED, which is not printable: every hinge
clearance becomes something the slicer has to bridge in mid-air.

So this takes the geometry from the deliverable and everything else from the
project, which is the combination nothing else produces.

WHAT IT REWRITES
----------------
  3D/Objects/object_N.model   mesh replaced with the deliverable's
  3D/3dmodel.model            build transform recomputed so the new mesh sits
                              centred on the plate with ZMin on the bed
  everything else             copied through byte for byte, which is how the
                              profile survives

DO NOT trust `source_file` in model_settings.config to tell you what geometry a
project contains. Creality carries that field forward across saves, so it names
where an object once came from, not what is in the file now -- it claimed the
60-fluted-label deliverable while holding the closed assembly.

Usage:
    <py> scripts/merge_print_project.py BASE.3mf GEOMETRY.3mf OUT.3mf
e.g.
    <py> scripts/merge_print_project.py BasePrint.3mf \
         3mf/MagicCardBox-60-fluted-label.3mf PRINT-60-fluted-label.3mf
"""
import re
import shutil
import sys
import zipfile

PLATE_CENTRE = (120.0, 120.0)      # Creality K2 Plus bed centre used by the base


def mesh_block(xml):
    """-> the <mesh>...</mesh> substring of a 3MF model document."""
    a = xml.find("<mesh>")
    b = xml.find("</mesh>")
    if a < 0 or b < 0:
        raise SystemExit("no <mesh> found")
    return xml[a:b + len("</mesh>")]


def mesh_bounds(block):
    xs, ys, zs = [], [], []
    for m in re.finditer(r'<vertex x="([-\d.eE+]+)" y="([-\d.eE+]+)" z="([-\d.eE+]+)"', block):
        xs.append(float(m.group(1)))
        ys.append(float(m.group(2)))
        zs.append(float(m.group(3)))
    if not xs:
        raise SystemExit("no vertices parsed")
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    base_p, geom_p, out_p = sys.argv[1:4]

    zb = zipfile.ZipFile(base_p)
    zg = zipfile.ZipFile(geom_p)
    names = zb.namelist()

    objs = [n for n in names if n.startswith("3D/Objects/") and n.endswith(".model")]
    if len(objs) != 1:
        raise SystemExit("expected exactly one 3D/Objects/*.model in the base, got %r" % objs)
    obj_name = objs[0]

    new_mesh = mesh_block(zg.read("3D/3dmodel.model").decode("utf8"))
    (x0, x1), (y0, y1), (z0, z1) = mesh_bounds(new_mesh)
    print("new geometry: %.2f x %.2f x %.2f  (X %.2f..%.2f  Y %.2f..%.2f  Z %.2f..%.2f)"
          % (x1 - x0, y1 - y0, z1 - z0, x0, x1, y0, y1, z0, z1))

    # swap the mesh into the base's object file, keeping its namespaces + UUIDs
    obj_xml = zb.read(obj_name).decode("utf8")
    old = mesh_block(obj_xml)
    obj_xml = obj_xml.replace(old, new_mesh)

    # place it: centre on the plate in XY, sit ZMin on the bed
    tx = PLATE_CENTRE[0] - (x0 + x1) / 2.0
    ty = PLATE_CENTRE[1] - (y0 + y1) / 2.0
    tz = -z0
    root = zb.read("3D/3dmodel.model").decode("utf8")
    new_t = "1 0 0 0 1 0 0 0 1 %.6f %.6f %.6f" % (tx, ty, tz)
    root_new, n = re.subn(r'(<item\b[^>]*\btransform=")[^"]*(")',
                          lambda m: m.group(1) + new_t + m.group(2), root)
    if n != 1:
        raise SystemExit("expected exactly one build <item transform>, patched %d" % n)
    print("build transform -> %s" % new_t)

    with zipfile.ZipFile(out_p, "w", zipfile.ZIP_DEFLATED) as zo:
        for n_ in names:
            if n_ == obj_name:
                zo.writestr(n_, obj_xml)
            elif n_ == "3D/3dmodel.model":
                zo.writestr(n_, root_new)
            else:
                zo.writestr(n_, zb.read(n_))       # profile rides through untouched
    print("wrote %s" % out_p)


if __name__ == "__main__":
    main()
