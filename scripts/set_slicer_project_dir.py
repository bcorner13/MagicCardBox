#!/usr/bin/env python3
"""Point Creality Print's sticky save/open folders away from the tracked 3mf/ directory.

WHY
---
Creality Print remembers the last folder you saved a project into and defaults there next
time. On 2026-09-13/14 that folder was this repo's `3mf/`, and THREE times a Creality PROJECT
file (plate thumbnails, no geometry) was written over `3mf/MagicCardBox-fluted.3mf` — the
tracked export. A project file has 0 triangles, so the export silently became unusable;
macro 16's gate now catches it, but only after the fact.

The keys are sticky "last used" values, not a preference, so the app rewrites them whenever
you save somewhere else. Re-run this whenever they drift back.

REFUSES TO RUN WHILE CREALITY PRINT IS OPEN — it rewrites Creality.conf on exit and would
discard the change.

Usage:  python3 scripts/set_slicer_project_dir.py [target_dir]
        (default target: <project>/gcode, which is gitignored)
"""
import json
import os
import subprocess
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.expanduser(
    "~/Library/Application Support/Creality/Creality Print/7.0/Creality.conf")
BAD = os.path.join(PROJ, "3mf")
KEYS = ("last_export_path", "last_opened_folder", "settings_folder")


def running():
    try:
        out = subprocess.run(["pgrep", "-f", "Creality Print"],
                             capture_output=True, text=True).stdout.split()
        return len(out)
    except FileNotFoundError:
        return 0


def walk(node, new, hits):
    """Repoint any of KEYS that currently sits inside the tracked 3mf/ directory."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in KEYS and isinstance(v, str) and os.path.normpath(v) == os.path.normpath(BAD):
                node[k] = new
                hits.append(k)
            else:
                walk(v, new, hits)
    elif isinstance(node, list):
        for v in node:
            walk(v, new, hits)


def main():
    target = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(PROJ, "gcode")
    n = running()
    if n:
        sys.exit("Creality Print is running (%d processes). Quit it first — it rewrites\n"
                 "Creality.conf on exit and would discard this change." % n)
    if not os.path.isfile(CONF):
        sys.exit("not found: %s\n(version folder may have changed from 7.0)" % CONF)
    os.makedirs(target, exist_ok=True)

    with open(CONF) as f:
        raw = f.read()
    cfg = json.loads(raw)                      # fail loudly rather than corrupt the file
    hits = []
    walk(cfg, target, hits)
    if not hits:
        print("nothing to change — no sticky folder currently points at %s" % BAD)
        return
    with open(CONF + ".bak", "w") as f:
        f.write(raw)
    with open(CONF, "w") as f:
        json.dump(cfg, f, indent=4)
    print("repointed %s -> %s" % (", ".join(sorted(set(hits))), target))
    print("backup written to %s.bak" % CONF)


if __name__ == "__main__":
    main()
