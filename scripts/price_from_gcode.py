#!/usr/bin/env python3
"""
price_from_gcode.py - price every exported variant through Maker-Ops from REAL G-code.

Slices each stl/MagicCardBox-*.stl with slice_price_matrix.py's exact profile (Core One L
HF0.4, 0.20mm BALANCED, Prusament PETG, 15 %), keeps the G-code in gcode/sliced/, and
POSTs it to Maker-Ops  POST /products/calculate/from-gcode  (127.0.0.1:8000).

Cost inputs are Bradley's, 2026-11-21 (CornerCAD content/square-descriptions-card-boxes.md):
    machine 92        Prusa CORE One L (HF0.4)
    material          Prusament PETG $0.02999/g, waste x1.05
    labor             2 min at $30/h            (plate off, free hinge, fit 4 magnets)
    hardware          4 magnets x $0.20 = $0.80
One G-code = one whole box (box + lid), so labor and magnets are counted exactly once -
unlike macro 60, which priced box and lid as two calls.

Read-only on the model (never opens FreeCAD). Never saves a Maker-Ops profile.

Usage:  python3 scripts/price_from_gcode.py [--match REGEX]
Output: gcode/maker_ops_gcode_prices.json
"""
import argparse, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slice_price_matrix as spm

API = "http://127.0.0.1:8000/products/calculate/from-gcode"
OUT_DIR = os.path.join(spm.PROJ, "gcode", "sliced")
REPORT = os.path.join(spm.PROJ, "gcode", "maker_ops_gcode_prices.json")
FORM = {"machine_id": "92", "material_cost_per_gram": "0.02999", "waste_factor": "1.05",
        "labor_minutes": "2", "target_hourly_rate": "30", "hardware_cost": "0.80",
        "save_profile": "false"}


def post(gcode):
    cmd = ["curl", "-sS", "--fail-with-body", "-X", "POST", API, "-F", "file=@%s" % gcode]
    for k, v in FORM.items():
        cmd += ["--form-string", "%s=%s" % (k, v)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("POST failed: %s %s" % (r.stdout[-300:], r.stderr[-300:]))
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--match", default="")
    args = ap.parse_args()
    rx = re.compile(args.match)
    os.makedirs(OUT_DIR, exist_ok=True)
    stls = sorted(f for f in os.listdir(spm.STL_DIR)
                  if f.startswith("MagicCardBox-") and f.endswith(".stl")
                  and "dryrun" not in f and rx.search(f[len("MagicCardBox-"):-4]))
    results = []
    for f in stls:
        tag = f[len("MagicCardBox-"):-4]
        row = {"tag": tag, "label": spm.label(tag)}
        try:
            row["slice"] = spm.slice_one(os.path.join(spm.STL_DIR, f), OUT_DIR, spm.PRINT)
            row["gcode"] = os.path.join("gcode", "sliced", f[:-4] + ".gcode")
            row["maker_ops"] = post(os.path.join(spm.PROJ, row["gcode"]))
        except Exception as e:
            row["error"] = str(e)
        results.append(row)
        print(tag, row.get("error") or "ok")
    json.dump({"inputs": FORM, "printer": spm.PRINTER, "print": spm.PRINT,
               "filament": spm.FILAMENT, "fill_density": spm.FILL, "results": results},
              open(REPORT, "w"), indent=1)
    print("wrote", REPORT)
    sys.exit(1 if any("error" in r for r in results) else 0)


if __name__ == "__main__":
    main()
