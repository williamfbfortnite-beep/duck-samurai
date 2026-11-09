"""Statistik over Vordingborg-temperaturer (10 hele år: 2016–2025)."""
from pathlib import Path
import pandas as pd

D = Path(__file__).parent / "data"
PARAMS = {"mean_temp": "Middel", "mean_daily_max_temp": "Døgnmax", "mean_daily_min_temp": "Døgnmin"}
Y0, Y1 = 2016, 2025
MDR = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]

def load(src, p, res):
    df = pd.read_csv(D / f"{src}_{p}_{res}.csv", parse_dates=["from"])
    return df.set_index("from")["value"]

def combined(p, res):
    """Kommuneværdi; huller udfyldes med station 06147, korrigeret for den
    gennemsnitlige forskel (kommune − station) pr. kalendermåned i overlapsperioden."""
    k, s = load("kommune", p, res), load("station", p, res)
    idx = s.index.union(k.index)
    k, s = k.reindex(idx), s.reindex(idx)
    diff = (k - s).dropna()
    bias = diff.groupby(diff.index.month).mean()
    filled = s + s.index.month.map(bias).values
    out = k.fillna(filled)
    src = pd.Series("kommune", index=idx).where(k.notna(), "station (korr.)")
    return out, src, bias

lines = ["# Temperaturstatistik – Vordingborg Kommune (0390)", "",
         f"Kilde: DMI Climate Data API, data til og med {load('kommune', 'mean_temp', 'day').index.max():%Y-%m-%d}. "
         f"Statistikken bygger på de 10 hele kalenderår {Y0}–{Y1}.", ""]

monthly, daily, notes = {}, {}, []
for p, name in PARAMS.items():
    m, msrc, mbias = combined(p, "month")
    d, dsrc, _ = combined(p, "day")
    monthly[name], daily[name] = m, d
    n_st = ((msrc != "kommune") & (m.index.year.isin(range(Y0, Y1 + 1)))).sum()
    if n_st:
        notes.append(f"- **{name}**: {n_st} af 120 måneder er udfyldt med station 06147 Vindebæk Kyst "
                     f"(korrektion kommune−station: {mbias.min():+.1f} til {mbias.max():+.1f} °C afhængigt af måned).")

M = pd.DataFrame(monthly)
M10 = M[(M.index.year >= Y0) & (M.index.year <= Y1)]
assert len(M10) == 120 and not M10.isna().any().any(), "Manglende måneder i 10-årsperioden"

# 1. 10-års snit pr. måned og variation
g = M10.groupby(M10.index.month)
t1 = pd.DataFrame({
    "Middel": g["Middel"].mean(),
    "Døgnmax": g["Døgnmax"].mean(),
    "Døgnmin": g["Døgnmin"].mean(),
    "Std.afv.": g["Middel"].std(),
    "Koldeste år": g["Middel"].apply(lambda s: f"{s.min():.1f} ({s.idxmin().year})"),
    "Varmeste år": g["Middel"].apply(lambda s: f"{s.max():.1f} ({s.idxmax().year})"),
    "Spænd": g["Middel"].max() - g["Middel"].min(),
})
t1.index = MDR
lines += ["## 1. Gennemsnitstemperatur pr. måned (10-års snit 2016–2025)", "",
          "Værdier i °C. Std.afv., koldeste/varmeste år og spænd gælder månedens middeltemperatur fra år til år.", "",
          t1.to_markdown(floatfmt=".1f"), "",
          f"Årsmiddel 2016–2025: **{M10['Middel'].mean():.1f} °C** "
          f"(døgnmax {M10['Døgnmax'].mean():.1f} °C, døgnmin {M10['Døgnmin'].mean():.1f} °C).", ""]

# Afvigelse pr. år og måned fra 10-års snittet (middeltemperatur)
anom = M["Middel"] - M["Middel"].index.month.map(g["Middel"].mean()).values
A = anom[anom.index.year >= Y0].to_frame("a")
A["år"], A["mdr"] = A.index.year, A.index.month
piv = A.pivot(index="år", columns="mdr", values="a")
piv.columns = MDR[: len(piv.columns)]
piv["År"] = piv.mean(axis=1)
lines += ["### Afvigelse fra 10-års snittet pr. måned (middeltemperatur, °C)", "",
          "Positiv = varmere end 10-års snittet for den måned. 2026 er medtaget til sammenligning "
          "(indgår ikke i snittet; november er ufuldstændig). Kolonnen \"År\" for 2026 er snittet af de foreliggende måneder.", "",
          piv.map(lambda v: "" if pd.isna(v) else f"{v:+.1f}").to_markdown(stralign="right", disable_numparse=True), ""]

# Ekstremer fra døgndata
Dd = pd.DataFrame(daily)
Dd10 = Dd[(Dd.index.year >= Y0) & (Dd.index.year <= Y1)]
gd = Dd10.groupby(Dd10.index.month)
t3 = pd.DataFrame({
    "Højeste døgnmax": gd["Døgnmax"].apply(lambda s: f"{s.max():.1f} ({s.idxmax():%Y-%m-%d})"),
    "Laveste døgnmin": gd["Døgnmin"].apply(lambda s: f"{s.min():.1f} ({s.idxmin():%Y-%m-%d})"),
    "Dage m. frost (snit/år)": gd["Døgnmin"].apply(lambda s: (s < 0).sum() / 10),
    "Dage >25 °C (snit/år)": gd["Døgnmax"].apply(lambda s: (s > 25).sum() / 10),
})
t3.index = MDR
lines += ["### Ekstremer og tærskeldage fra døgndata (2016–2025)", "", t3.to_markdown(floatfmt=".1f"), ""]

lines += ["## Datagrundlag", "",
          "- Kommuneværdier for Vordingborg (municipalityId 0390) bruges, hvor de findes.",
          "- DMI har ingen kommuneværdier for døgnmax/døgnmin fra nov. 2014 til dec. 2017. Disse huller er udfyldt med "
          "den nærmeste fulde DMI-station, **06147 Vindebæk Kyst** (Møn), korrigeret pr. kalendermåned for den "
          "gennemsnitlige forskel mellem kommune og station i perioden, hvor begge findes.",
          *notes,
          "- På dagsniveau bruger stationen `max_temp_w_date`/`min_temp` (døgnets max/min), "
          "fordi `mean_daily_*` kun findes som måneds-/årsværdier for stationer.",
          "- Rådata: `data/kommune_*.csv` og `data/station_*.csv`. Hent dem igen med `python3 fetch_dmi.py`, "
          "og lav statistikken igen med `python3 analyze.py`.", ""]

(Path(__file__).parent / "STATISTIK.md").write_text("\n".join(lines))
print("\n".join(lines))
