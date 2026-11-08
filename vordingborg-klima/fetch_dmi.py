"""Henter temperaturdata for Vordingborg Kommune (0390) fra DMI Climate Data API."""
import csv, json, sys, urllib.parse, urllib.request
from pathlib import Path

API = "https://opendataapi.dmi.dk/v2/climateData/collections"
# Reservestation: 06147 Vindebæk Kyst (Møn, ligger i Vordingborg Kommune).
# Bruges hvor kommunedata mangler (max/min findes ikke for kommunen 2014-11 – 2017-12).
STATION = "06147"
MUNI = "0390"
PARAMS = ["mean_temp", "mean_daily_max_temp", "mean_daily_min_temp"]
RES = ["day", "month"]
START, END = "2015-12-31T00:00:00Z", "2026-11-09T00:00:00Z"
OUT = Path(__file__).parent / "data"

def fetch(source, param, res):
    if source == "kommune":
        coll, key = "municipalityValue", {"municipalityId": MUNI}
    else:
        coll, key = "stationValue", {"stationId": STATION}
    # Stationer har ikke mean_daily_max/min på dagsniveau; der svarer døgnets max/min hertil.
    api_param = {"mean_daily_max_temp": "max_temp_w_date",
                 "mean_daily_min_temp": "min_temp"}.get(param, param) if (source, res) == ("station", "day") else param
    q = {**key, "parameterId": api_param, "timeResolution": res,
         "datetime": f"{START}/{END}", "limit": 300000}
    url = f"{API}/{coll}/items?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=120) as r:
        feats = json.load(r)["features"]
    rows = [{"from": f["properties"]["from"][:10], "to": f["properties"]["to"][:10],
             "value": f["properties"]["value"], "qcStatus": f["properties"]["qcStatus"]}
            for f in feats]
    return sorted(rows, key=lambda x: x["from"])

OUT.mkdir(exist_ok=True)
for src in ["kommune", "station"]:
  for p in PARAMS:
    for r in RES:
        rows = fetch(src, p, r)
        path = OUT / f"{src}_{p}_{r}.csv"
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["from", "to", "value", "qcStatus"])
            w.writeheader(); w.writerows(rows)
        print(f"{path.name}: {len(rows)} rækker ({rows[0]['from']} – {rows[-1]['from']})")
