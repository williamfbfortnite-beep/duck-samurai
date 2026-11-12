"""Forudsigelse af snevejrsdage (sne ELLER slud) på Møn for resten af vinteren.

Snevejrsdag: mindst 2 målinger med sne/slud-kode fra station 06147 Vindebæk Kyst den dag
og døgnets laveste temperatur højst 3 °C (frasorterer sensorfejl på milde dage).
  * Klimatologi: andel af de 15 vintre 2011/12–2025/26 med snevejr på hver kalenderdag,
    udglattet over ±7 dage.
  * De første dage: DMI's HARMONIE-ensemble (sandsynlighed for fast nedbør og frost).
"""
import json, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
d = pd.read_csv(HERE / "data/snevejr_moen.csv", parse_dates=["dato"]).set_index("dato")
tmin = pd.read_csv(HERE / "data/station_06147_min_temp_day.csv", parse_dates=["dato"]).set_index("dato").min_temp
d = d.join(tmin)
d["sv"] = (d.sne_slud_obs >= 2) & (d.min_temp <= 3)
season = lambda x: x.year - 1 if x.month < 7 else x.year
d["s"] = [season(x) for x in d.index]
hist = d[(d.s >= 2011) & (d.s <= 2025)]
ref = lambda x: (x - pd.Timestamp(season(x), 7, 1)).days            # dag i sæsonen (1. juli = 0)
hist = hist.assign(doy=[ref(x) for x in hist.index])

# klimatologisk sandsynlighed pr. sæsondag: snevejrsdage / dage med data, ±7 dage
k = hist.groupby("doy").agg(n=("sv", "size"), y=("sv", "sum")).reindex(range(366), fill_value=0)
roll = lambda s: s.rolling(15, center=True, min_periods=1).sum()
p_clim = (roll(k.y) / roll(k.n).replace(0, np.nan)).fillna(0)

today = pd.Timestamp.now(tz="Europe/Copenhagen").normalize().tz_localize(None)
end = pd.Timestamp(season(today) + 1, 4, 30)
dates = pd.date_range(today, end)
prob = pd.Series([p_clim[ref(x)] for x in dates], index=dates)
src = pd.Series("klima", index=dates)

# de første dage: ensemble
eps_days = {}
try:
    url = ("https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_eps_probabilities/position?"
           "coords=POINT(12.29%2054.99)&parameter-name=time-integral-of-total-solid-precipitation-flux-above-1mm-in-6hours-probability,"
           "temperature-2m-below-273k-probability&crs=crs84&f=CoverageJSON")
    e = json.load(urllib.request.urlopen(url, timeout=60))
    t = pd.to_datetime(e["domain"]["axes"]["t"]["values"]).tz_convert("Europe/Copenhagen").tz_localize(None)
    r = e["ranges"]
    sol = pd.Series(r["time-integral-of-total-solid-precipitation-flux-above-1mm-in-6hours-probability"]["values"], index=t, dtype=float)
    frost = pd.Series(r["temperature-2m-below-273k-probability"]["values"], index=t, dtype=float)
    last_full = (t.max() - pd.Timedelta(hours=18)).normalize()
    for day in pd.date_range(today, last_full):
        s = sol[sol.index.normalize() == day].max(); f = frost[frost.index.normalize() == day].max()
        # sne/slud kan falde uden 1 mm fast nedbør: brug en lille bund knyttet til frostrisikoen
        eps_days[day] = float(np.nanmax([s if pd.notna(s) else 0, 0.5 * (f if pd.notna(f) else 0), 0.01]))
    for day, v in eps_days.items():
        if day in prob.index:
            prob[day] = v; src[day] = "model"
except Exception as ex:
    print("ensemble ikke tilgængelig:", ex)

# empirisk første snevejrsdag: blandt vintre uden snevejr indtil i dag
cut = ref(today)
firsts = []
for s, g in hist.groupby("s"):
    g = g[(g.doy >= cut) & g.sv]
    firsts.append(g.doy.min() if len(g) else np.nan)
firsts = pd.Series(firsts).dropna()
to_date = lambda doy: (pd.Timestamp(season(today), 7, 1) + pd.Timedelta(days=int(doy))).date()
monthly = prob.groupby(prob.index.to_period("M")).sum()
out = {
    "today": str(today.date()),
    "days": [[str(x.date()), round(float(prob[x]), 3), src[x]] for x in dates],
    "monthly": {str(m): round(float(v), 1) for m, v in monthly.items()},
    "expected_total": round(float(prob.sum()), 1),
    "hist_per_season": {f"{s}/{str(s+1)[2:]}": int(g.sv.sum()) for s, g in hist.groupby("s")},
    "first_after_today_median": str(to_date(firsts.median())),
    "first_after_today_q25": str(to_date(firsts.quantile(.25))),
    "first_after_today_q75": str(to_date(firsts.quantile(.75))),
    # empirisk: andel af de 15 vintre med mindst én snevejrsdag fra i dag til datoen
    "p_before": {lbl: round(float((firsts <= ref(pd.Timestamp(dt))).sum() / hist.s.nunique()), 2)
                 for lbl, dt in [("30-11", f"{today.year}-11-30"), ("15-12", f"{today.year}-12-15"), ("31-12", f"{today.year}-12-31")]},
}
(HERE / "data/snevejr_prognose.json").write_text(json.dumps(out, ensure_ascii=False))
print(json.dumps({k: v for k, v in out.items() if k != "days"}, ensure_ascii=False, indent=1))
print("næste 10 dage:", [(x[0][5:], x[1], x[2]) for x in out["days"][:10]])
