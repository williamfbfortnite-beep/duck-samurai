"""Laver data/dk_byer.json ud fra GeoNames' DK.txt (https://download.geonames.org/export/dump/DK.zip, CC BY 4.0).
Brug: python3 build_places.py /sti/til/DK.txt"""
import csv, json, sys
from pathlib import Path
HERE = Path(__file__).parent
csv.field_size_limit(10**9)
kommuner = json.loads((HERE / "data/dk_kommune_id.json").read_text())
keep = {"PPL", "PPLA", "PPLA2", "PPLC", "PPLS", "PPLF", "PPLL"}
seen, out = set(), []
for r in csv.reader(open(sys.argv[1], encoding="utf-8"), delimiter="\t"):
    if r[6] != "P" or r[7] not in keep:
        continue
    name, lat, lon, pop = r[1], float(r[4]), float(r[5]), int(r[14] or 0)
    kom = kommuner.get(r[11].zfill(4), "")
    key = (name, kom, round(lat, 2), round(lon, 2))
    if key in seen:
        continue
    seen.add(key)
    out.append([name, round(lon, 4), round(lat, 4), pop, kom])
out.sort(key=lambda x: -x[3])
(HERE / "data/dk_byer.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print(len(out), "steder")
