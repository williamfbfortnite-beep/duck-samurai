"""Bygger sne_kort.html: et heatmap over sne i Danmark (DMI 10 km-grid, vintrene 2011/12–2025/26)."""
import json
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).parent
g = pd.read_csv(HERE / "data/sne_dk_grid.csv")
cells = json.loads((HERE / "data/dk_grid_cells.json").read_text())
munis = json.loads((HERE / "data/dk_kommuner.json").read_text())
seasons = sorted(g.vinter.unique())
names = list(munis); P = np.array([munis[n] for n in names])
def near(poly):
    x = np.mean(poly[:-1], axis=0)
    d = ((P[:, 0] - x[0]) * np.cos(np.radians(56))) ** 2 + (P[:, 1] - x[1]) ** 2
    return names[int(d.argmin())]
days = g.pivot(index="cellId", columns="vinter", values="snedage").reindex(columns=seasons)
mx = g.pivot(index="cellId", columns="vinter", values="max_cm").reindex(columns=seasons)
out = {"seasons": seasons, "cells": []}
for cid in days.index:
    poly = cells[cid]
    out["cells"].append({"id": cid, "n": near(poly), "p": [[round(a, 3), round(b, 3)] for a, b in poly[:-1]],
                         "d": [int(v) for v in days.loc[cid]], "m": [round(float(v), 1) for v in mx.loc[cid]]})
out["munis"] = {k: [round(v[0], 3), round(v[1], 3)] for k, v in munis.items()}
# byer fra GeoNames (CC BY 4.0), kun steder inden for kortets udstrækning
byer = json.loads((HERE / "data/dk_byer.json").read_text())
allp = np.array([p for c in cells.values() for p in c])
x0, y0 = allp.min(axis=0); x1, y1 = allp.max(axis=0)
out["places"] = [b for b in byer if x0 <= b[1] <= x1 and y0 <= b[2] <= y1]
tpl = (HERE / "sne_kort_template.html").read_text()
(HERE / "sne_kort.html").write_text(tpl.replace("/*DATA*/null", json.dumps(out, ensure_ascii=False, separators=(",", ":"))))
print("ok", len(out["cells"]))
