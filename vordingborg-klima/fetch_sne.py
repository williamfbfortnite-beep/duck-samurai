"""Henter snedata for Vordingborg: kommuneværdi (0390), snestation 31185 Køng og 31259 Borre/Neble på Møn."""
import csv, json, urllib.parse, urllib.request
from pathlib import Path
API = "https://opendataapi.dmi.dk/v2/climateData/collections"
OUT = Path(__file__).parent / "data"
SRC = {"kommune": ("municipalityValue", {"municipalityId": "0390"}),
       "koeng": ("stationValue", {"stationId": "31185"}),
       # Møn: 31259 Borre (østlige Møn) til nov. 2019, derefter Neble (vestlige Møn)
       "borre_neble": ("stationValue", {"stationId": "31259"})}
for name, (coll, key) in SRC.items():
    for p in ["snow_depth", "snow_cover"]:
        q = {**key, "parameterId": p, "timeResolution": "day",
             "datetime": "2009-07-01T00:00:00Z/2026-11-09T00:00:00Z", "limit": 300000}
        try:
            with urllib.request.urlopen(f"{API}/{coll}/items?" + urllib.parse.urlencode(q), timeout=120) as r:
                feats = json.load(r).get("features", [])
        except Exception as e:
            print(name, p, "fejl:", e); continue
        rows = sorted(({"date": f["properties"]["from"][:10], "value": f["properties"]["value"]} for f in feats),
                      key=lambda x: x["date"])
        if not rows: print(name, p, "ingen data"); continue
        with open(OUT / f"sne_{name}_{p}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["date", "value"]); w.writeheader(); w.writerows(rows)
        print(name, p, len(rows), rows[0]["date"], rows[-1]["date"])
