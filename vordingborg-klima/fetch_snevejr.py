"""Henter DMI's vejrkoder (present weather) fra station 06147 Vindebæk Kyst (Møn), oktober–april
i vintrene 2011/12–2025/26 samt indeværende vinter, og gemmer dage med sne eller slud.
Kode = 100 + WMO-tabel 4680 (automatisk station). Sne/slud-koder:
  124 sne seneste time · 167/168 slud (regn og sne) · 170–178 sne, kornsne, iskorn · 185–187 snebyger"""
import csv, json, urllib.parse, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items?"
OUT = Path(__file__).parent / "data"
SNOW = {124, 167, 168, *range(170, 179), 185, 186, 187}
SLEET = {167, 168}
MONTHS = [(y if m >= 10 else y + 1, m) for y in range(2011, 2027) for m in (10, 11, 12, 1, 2, 3, 4)]
NOW = datetime.now(timezone.utc)
MONTHS = [(y, m) for y, m in MONTHS if datetime(y, m, 1, tzinfo=timezone.utc) < NOW]

def month(ym):
    y, m = ym
    end = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=timezone.utc)
    q = {"stationId": "06147", "parameterId": "weather", "limit": 300000,
         "datetime": f"{y}-{m:02d}-01T00:00:00Z/{end:%Y-%m-%dT%H:%M:%SZ}"}
    for _ in range(4):
        try:
            with urllib.request.urlopen(API + urllib.parse.urlencode(q), timeout=300) as r:
                return [(f["properties"]["observed"], int(f["properties"]["value"])) for f in json.load(r)["features"]]
        except Exception as e:
            err = e
    raise err

days = defaultdict(lambda: [0, 0, 0])   # dato -> [antal obs, sne/slud-obs, slud-obs]
with ThreadPoolExecutor(4) as ex:
    for rows in ex.map(month, MONTHS):
        for t, code in rows:
            local = datetime.fromisoformat(t.replace("Z", "+00:00")) + timedelta(hours=1)   # dansk normaltid
            d = days[local.date().isoformat()]
            d[0] += 1; d[1] += code in SNOW; d[2] += code in SLEET
with open(OUT / "snevejr_moen.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["dato", "obs", "sne_slud_obs", "slud_obs"])
    for k in sorted(days): w.writerow([k, *days[k]])
print(len(days), "dage gemt")
