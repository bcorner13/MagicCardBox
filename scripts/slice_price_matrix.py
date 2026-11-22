#!/usr/bin/env python3
"""
slice_price_matrix.py - real slicer weights/times for every exported variant.

Replaces the Maker-Ops volumetric estimator (macro 60) as the source of mass and print
time. Slices each stl/MagicCardBox-*.stl headlessly with PrusaSlicer and parses the
G-code footer:

    ; filament used [g] = 120.15
    ; estimated printing time (normal mode) = 5h 6m 28s

Profile (system presets from PrusaSlicer's PrusaResearch bundle):
    printer  Prusa CORE One L HF0.4 nozzle
    print    0.20mm BALANCED @COREONEL HF0.4   (fill_density overridden to 15%)
    filament Prusament PETG @COREONE HF0.4

Validated 2026-11-21: 100-fluted -> 120.15 g / 5h06m28s, against Bradley's GUI slice of
120.14 g / 5h07m.

Read-only on the model: it never opens FreeCAD and only reads the exported STLs, so it
is safe to run while FreeCAD is busy. G-code goes to a temp dir and is discarded.

Usage:
    python3 scripts/slice_price_matrix.py                  # all variants, BALANCED
    python3 scripts/slice_price_matrix.py --match '^(60|100)-' --speed
                                                           # MTG only, 0.20mm SPEED
Output: gcode/slice_prices.json (BALANCED) or gcode/slice_prices-speed.json (--speed).

Display names: the FreeCAD/STL tags keep their historical "alchemy" prefix (macro 41's
MATRIX); the product line sells them as "Oversized (Planechase / Archenemy)" - see LABELS.
"""
import argparse, json, os, re, subprocess, sys, tempfile, time

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL_DIR = os.path.join(PROJ, "stl")
REPORT = os.path.join(PROJ, "gcode", "slice_prices.json")
SLICER = "/Applications/Original Prusa Drivers/PrusaSlicer.app/Contents/MacOS/PrusaSlicer"

PRINTER = "Prusa CORE One L HF0.4 nozzle"
PRINT = "0.20mm BALANCED @COREONEL HF0.4"
PRINT_SPEED = "0.20mm SPEED @COREONEL HF0.4"
FILAMENT = "Prusament PETG @COREONE HF0.4"
FILL = "15%"
BED_CENTER = "150,150"   # CORE One L bed is 300 x 300; without --center the STL's own
                         # origin-centred coordinates land off the bed.

SIZE_LABELS = {"60": "MTG 60", "100": "MTG 100",
               "alchemy60": "Oversized 60 (Planechase / Archenemy)",
               "alchemy100": "Oversized 100 (Planechase / Archenemy)"}
FINISH_LABELS = {"smooth": "Smooth", "fluted": "Fluted", "fluted-label": "Fluted + Label"}


def label(tag):
    size, finish = tag.split("-", 1)
    return "%s · %s" % (SIZE_LABELS.get(size, size), FINISH_LABELS.get(finish, finish))


RE_G = re.compile(r"^; filament used \[g\] = ([\d.]+)", re.M)
RE_T = re.compile(r"^; estimated printing time \(normal mode\) = (.+)$", re.M)


def hours(s):
    """'1d 2h 5m 28s' -> float hours."""
    mult = {"d": 24.0, "h": 1.0, "m": 1 / 60.0, "s": 1 / 3600.0}
    return sum(float(n) * mult[u] for n, u in re.findall(r"(\d+)([dhms])", s))


def slice_one(stl, workdir, print_profile):
    out = os.path.join(workdir, os.path.basename(stl)[:-4] + ".gcode")
    cmd = [SLICER, "--export-gcode",
           "--printer-profile", PRINTER, "--print-profile", print_profile,
           "--material-profile", FILAMENT, "--fill-density", FILL,
           "--binary-gcode=0", "--center", BED_CENTER, "--output", out, stl]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
        raise RuntimeError("slice failed: " + " | ".join(tail))
    with open(out, "r", errors="replace") as f:
        f.seek(max(0, os.path.getsize(out) - 200_000))   # the footer is at the end
        foot = f.read()
    g, t = RE_G.search(foot), RE_T.search(foot)
    if not (g and t):
        raise RuntimeError("footer lines not found in G-code")
    return {"grams": float(g.group(1)), "time": t.group(1).strip(),
            "hours": round(hours(t.group(1)), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", default="", help="regex on the variant tag, e.g. '^(60|100)-'")
    ap.add_argument("--speed", action="store_true", help="use " + PRINT_SPEED)
    args = ap.parse_args()
    print_profile = PRINT_SPEED if args.speed else PRINT
    report_path = REPORT.replace(".json", "-speed.json") if args.speed else REPORT
    rx = re.compile(args.match)
    stls = sorted(f for f in os.listdir(STL_DIR)
                  if f.startswith("MagicCardBox-") and f.endswith(".stl")
                  and "dryrun" not in f and rx.search(f[len("MagicCardBox-"):-4]))
    if not stls:
        sys.exit("no STLs matched in " + STL_DIR)
    results = []
    with tempfile.TemporaryDirectory() as wd:
        for f in stls:
            tag = f[len("MagicCardBox-"):-4]
            t0 = time.time()
            try:
                res = slice_one(os.path.join(STL_DIR, f), wd, print_profile)
                res.update(tag=tag, label=label(tag), stl=f)
            except Exception as e:                       # report, keep going
                res = {"tag": tag, "label": label(tag), "stl": f, "error": str(e)}
            results.append(res)
            print("%-50s %s  (%.0fs)" % (label(tag), res.get("error") or
                  "%7.2f g  %s" % (res["grams"], res["time"]), time.time() - t0))
    report = {"printer": PRINTER, "print": print_profile, "filament": FILAMENT,
              "fill_density": FILL, "sliced_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "results": results}
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as fh:
        json.dump(report, fh, indent=1)
    print("wrote", report_path)
    sys.exit(1 if any("error" in r for r in results) else 0)


if __name__ == "__main__":
    main()
