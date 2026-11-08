"""Snestatistik for Vordingborg Kommune (snedybde, kommuneværdi 0390). Snedag = mindst 1 cm sne."""
from pathlib import Path
import pandas as pd
HERE = Path(__file__).parent
s = pd.read_csv(HERE / "data/sne_kommune_snow_depth.csv", parse_dates=["date"]).set_index("date")["value"]
season = lambda d: f"{d.year-1}/{str(d.year)[2:]}" if d.month < 7 else f"{d.year}/{str(d.year+1)[2:]}"
df = s.to_frame("cm"); df["vinter"] = [season(d) for d in df.index]
rows = []
for k, g in df.groupby("vinter"):
    if len(g) < 150: continue                      # kun hele vintre
    sn = g[g.cm >= 1]
    rows.append({"Vinter": k, "Snedage": len(sn), "Dage ≥5 cm": int((g.cm >= 5).sum()),
                 "Max cm": g.cm.max(), "Første snedag": sn.index.min().date() if len(sn) else "",
                 "Sidste snedag": sn.index.max().date() if len(sn) else ""})
R = pd.DataFrame(rows)
MD = ["jan", "feb", "mar", "apr", "okt", "nov", "dec"]
half = df.index.map(lambda d: f"{d.month:02d}-{'1' if d.day <= 15 else '2'}")
p = (df.groupby(half).cm.apply(lambda x: (x >= 1).mean()) * 100).round(0)
order = [f"{m:02d}-{h}" for m in (10, 11, 12, 1, 2, 3, 4) for h in (1, 2)]
names = {1: "jan", 2: "feb", 3: "mar", 4: "apr", 10: "okt", 11: "nov", 12: "dec"}
ptab = pd.DataFrame({"Periode": [f"{'1.–15.' if o[-1]=='1' else '16.–slut'} {names[int(o[:2])]}" for o in order],
                     "Chance for snedække": [f"{p.get(o, 0):.0f} %" for o in order]})
out = ["# Sne i Vordingborg Kommune", "", "Kilde: DMI Climate Data, `snow_depth` (kommuneværdi 0390). "
       "Snedag = mindst 1 cm sne på jorden.", "", "## Vinter for vinter", "", R.to_markdown(index=False), "",
       "## Hvornår ligger der typisk sne?", "", "Andel af dagene med snedække i hver halve måned, 2011–2026.", "",
       ptab.to_markdown(index=False), ""]
(HERE / "SNE.md").write_text("\n".join(out)); print("\n".join(out))
