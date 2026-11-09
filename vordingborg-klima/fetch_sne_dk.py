"""Henter daglig snedybde for hele Danmark (DMI 10 km-grid) for vintrene 2011/12–2025/26
og gemmer et kompakt resumé pr. celle og vinter (snedage ≥1 cm, største snedybde)."""
import csv, json, urllib.parse, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API = "https://opendataapi.dmi.dk/v2/climateData/collections"
OUT = Path(__file__).parent / "data"
MONTHS = [(y if m >= 11 else y + 1, m) for y in range(2011, 2026) for m in (11, 12, 1, 2, 3, 4)]

def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                return json.load(r)
        except Exception as e:
            err = e
    raise err

def month(ym):
    y, m = ym
    end = f"{y + (m == 12)}-{m % 12 + 1:02d}-01T00:00:00Z"
    q = {"parameterId": "snow_depth", "timeResolution": "day",
         "datetime": f"{y}-{m:02d}-01T00:00:00Z/{end}", "limit": 300000}
    d = get(f"{API}/10kmGridValue/items?" + urllib.parse.urlencode(q))
    rows, geom = [], {}
    for f in d["features"]:
        p = f["properties"]
        rows.append((p["cellId"], p["from"][:10], p["value"]))
        geom.setdefault(p["cellId"], f["geometry"]["coordinates"][0])
    print(f"{y}-{m:02d}: {len(rows)}", flush=True)
    return rows, geom

agg = defaultdict(lambda: [0, 0, 0.0, 0.0])   # ndata, snedage, max, sum
cells = {}
with ThreadPoolExecutor(4) as ex:
    for rows, geom in ex.map(month, MONTHS):
        cells.update(geom)
        for cell, date, v in rows:
            y, m = int(date[:4]), int(date[5:7])
            season = f"{y - 1}/{str(y)[2:]}" if m < 7 else f"{y}/{str(y + 1)[2:]}"
            a = agg[(cell, season)]
            a[0] += 1; a[1] += v >= 1; a[2] = max(a[2], v); a[3] += v

with open(OUT / "sne_dk_grid.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["cellId", "vinter", "dage_data", "snedage", "max_cm", "sum_cm"])
    for (cell, s), (n, sd, mx, sm) in sorted(agg.items()):
        w.writerow([cell, s, n, sd, mx, round(sm, 1)])
(OUT / "dk_grid_cells.json").write_text(json.dumps(cells))

# kommunenavne og -positioner (til at navngive celler)
d = get(f"{API}/municipalityValue/items?parameterId=snow_depth&timeResolution=month"
        "&datetime=2026-01-01T00:00:00Z/2026-01-02T00:00:00Z&limit=1000")
munis = {f["properties"]["municipalityName"]: f["geometry"]["coordinates"] for f in d["features"]}
(OUT / "dk_kommuner.json").write_text(json.dumps(munis, ensure_ascii=False))
print("celler:", len(cells), "kommuner:", len(munis))
