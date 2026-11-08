"""Bedste bud på temperaturen i Vordingborg de næste 12 måneder.

Model (statistisk, ikke en vejrudsigt):
  temperatur(dag) = sæsonkurve(dag) + trend + anomali
  * Sæsonkurve: 3 harmoniske (sinus/cosinus) tilpasset døgndata 2016-01-01 – seneste dag.
  * Trend: lineær opvarmning. 10 års data er for kort til at estimere den sikkert, så den
    er sat til DMI's observerede danske opvarmning siden 1990'erne, ~0,3 °C pr. årti.
  * Anomali: dagens afvigelse fra sæsonkurven klinger af som AR(1) (fittet på data),
    så de første 1-2 uger påvirkes af det aktuelle vejr; derefter er buddet klimatologien.
  * Usikkerhed: 80 %-interval for den enkelte dag, ud fra spredningen i anomalierne
    pr. kalendermåned (vinter er mere variabel end sommer).
"""
import json, io, contextlib, importlib.util
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("analyze", HERE / "analyze.py")
a = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(a)

D = pd.DataFrame(a.daily).loc["2016-01-01":].dropna()
D.index = pd.DatetimeIndex(D.index)
last = D.index.max()
TREND_PER_YEAR = 0.03
T0 = pd.Timestamp("2021-01-01")          # midt i datagrundlaget
Z80 = 1.2816

def design(idx):
    t = 2 * np.pi * idx.dayofyear.values / 365.25
    cols = [np.ones(len(idx))]
    for k in (1, 2, 3):
        cols += [np.cos(k * t), np.sin(k * t)]
    return np.column_stack(cols)

def trend(idx):
    return TREND_PER_YEAR * (idx - T0).days.values / 365.25

future = pd.date_range(last + pd.Timedelta(days=1), last + pd.DateOffset(years=1), freq="D")
out = {"last_obs": str(last.date()), "params": {}}
fc = pd.DataFrame(index=future)
for col, key in [("Middel", "mean"), ("Døgnmax", "max"), ("Døgnmin", "min")]:
    y = D[col].values - trend(D.index)
    beta, *_ = np.linalg.lstsq(design(D.index), y, rcond=None)
    clim_hist = design(D.index) @ beta + trend(D.index)
    anom = pd.Series(D[col].values - clim_hist, index=D.index)
    phi = float(np.corrcoef(anom.values[:-1], anom.values[1:])[0, 1])
    # spredning som glat funktion af årets dag (2 harmoniske tilpasset de kvadrerede anomalier)
    g, *_ = np.linalg.lstsq(design(D.index)[:, :5], anom.values ** 2, rcond=None)
    h = np.arange(1, len(future) + 1)
    a0 = anom.iloc[-1]
    clim = design(future) @ beta + trend(future)
    pred = clim + a0 * phi ** h
    sd = np.sqrt(np.clip(design(future)[:, :5] @ g, 0.1, None)) * np.sqrt(1 - phi ** (2 * h))
    if key == "min":   # forventede frostdage: empirisk fordeling af anomalier i samme kalendermåned
        sh = np.sqrt(1 - phi ** (2 * h))
        frost = [(pred[i] + sh[i] * anom[anom.index.month == future[i].month].values < 0).mean()
                 for i in range(len(future))]
        fc["pfrost"] = frost
    fc[key] = pred
    fc[key + "_clim"] = clim
    fc[key + "_lo"] = pred - Z80 * sd
    fc[key + "_hi"] = pred + Z80 * sd
    out["params"][key] = {"phi": round(phi, 3), "last_anomaly": round(float(a0), 2),
                          "half_life_days": round(float(np.log(0.5) / np.log(phi)), 1)}

# historik (fra 1. januar 2026) og 10-års snit pr. dag til sammenligning
hist = D.loc["2026-01-01":]
out["hist"] = [[str(i.date()), r["Middel"], r["Døgnmax"], r["Døgnmin"]] for i, r in hist.iterrows()]
out["fc"] = [[str(i.date())] + [round(float(r[c]), 2) for c in
             ["mean", "mean_lo", "mean_hi", "max", "min", "mean_clim"]] for i, r in fc.iterrows()]

# månedsoversigt for prognosen (kun hele/forudsagte dage)
# måned med målte dage (indeværende måned) blandes med buddet; sidste ufuldstændige måned droppes
obs = D.loc[f"{future[0]:%Y-%m}-01":].rename(columns={"Middel": "mean", "Døgnmax": "max", "Døgnmin": "min"})
comb = pd.concat([obs.assign(obs=1), fc[["mean", "max", "min"]].assign(obs=0)])
mon = comb.groupby(comb.index.to_period("M")).agg(
    mean=("mean", "mean"), max=("max", "mean"), min=("min", "mean"), n=("mean", "size"), nobs=("obs", "sum"))
mon = mon[mon["n"] >= 28]
ten = a.M10.groupby(a.M10.index.month).mean()
out["months"] = [{"m": str(p), "mean": round(r["mean"], 1), "max": round(r["max"], 1),
                  "min": round(r["min"], 1), "avg10": round(float(ten.loc[p.month, "Middel"]), 1),
                  "n": int(r["n"]), "nobs": int(r["nobs"])} for p, r in mon.iterrows()]
out["frost_by_month"] = {str(k): round(float(v), 1) for k, v in fc["pfrost"].groupby(fc.index.to_period("M")).sum().items()}
(HERE / "data" / "forecast.json").write_text(json.dumps(out, ensure_ascii=False))
print(json.dumps({k: out[k] for k in ["last_obs", "params", "months", "frost_by_month"]}, ensure_ascii=False, indent=1))

# byg den interaktive graf
tpl = (HERE / "prognose_template.html").read_text()
(HERE / "prognose.html").write_text(tpl.replace("/*DATA*/null", json.dumps(out, ensure_ascii=False)))
