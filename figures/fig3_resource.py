"""Fig. 3. Resource conservation and its emission trade-off for FSA-derived HF.
(a) Change in cradle-to-gate emissions per kg of fluorspar conserved versus the
    marginal FSA share of supply; (b) the same versus the share of silica sold.
(c) Fluorspar avoided versus AHF supplied from FSA, with the AHF required for the
    electronic-grade demand (2025 and projected 2035; 1.39 t AHF per t electronic-grade
    HF, the remainder leaving purification as industrial-grade HF) and the AHF that
    current and potential FSA recovery could supply. (d) Producer shares of fluorspar and phosphate rock.
Values: model/hf_tea_lca.py; data/usgs_mcs2026_production_2025.csv (USGS MCS 2026);
demand and recovery ranges in SI Section S14.
Output: output/Fig3_resource.(png|svg)
"""
import csv, os
import numpy as np
import matplotlib
from common import MM, C_TXT, C_RED, DATA, set_style, save
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from hf_tea_lca import P, totals, with_

set_style()
C_FSA, C_SPAR, C_GREY, C_FSA2 = "#1F4E79", "#9C6B3C", "#8A939C", "#6E9BC7"
SPAR = P["spar_t"]; G = "Electronic"

def dghg(p):     # (FSA minus fluorspar route) cradle-to-gate emissions per kg of fluorspar conserved
    return (totals("FSA", G, p)[1] - totals("Fluorspar", G, p)[1]) / SPAR
base = dghg(P)

# (a) marginal share x: a share x of the FSA supply is cut-off plus avoided neutralization,
#     the rest keeps the economic allocation (linear mixture)
x = np.linspace(0, 0.4, 81)
A = {}
for n, lab in ((1.5, "Limestone neutralization"), (2.3, "Lime neutralization")):
    end = dghg(with_(fsa_alloc=0.0, cr_neutral=-n))
    A[lab] = base + x*(end - base)
# (b) share of silica sold s
s = np.linspace(0, 1, 101)
Bs = {}
for c, lab in ((0.75, "Sodium silicate substituted"), (1.3, "Silica gel substituted")):
    end = dghg(with_(cr_silica=-c, silica_sold=1))
    Bs[lab] = base + s*(end - base)

# (c) scale
V = np.linspace(0, 2.2, 221)
DEM = (0.3, 0.4)                                # electronic-grade HF demand 2025, Mt/yr
GROW = 0.06                                     # MarketsandMarkets 2025-2030 value growth used as a volume proxy, extended to 2035
DEM35 = tuple(v*(1 + GROW)**10 for v in DEM)    # 2035: 0.537-0.716 Mt/yr
AHF_IN = P["ahf_in"]                            # t AHF per t electronic-grade HF (gross feed requirement)
DEM_AHF = tuple(v*AHF_IN for v in DEM)          # 2025: 0.417-0.556 Mt AHF/yr
DEM35_AHF = tuple(v*AHF_IN for v in DEM35)      # 2035: 0.747-0.996 Mt AHF/yr
FSA_HFEQ = P["fsa_t"] * 6 * 20.006 / 144.09     # 1.55 t FSA = 1.29 t HF-eq per t AHF supplied
REC_NOW = tuple(v / FSA_HFEQ for v in (0.3, 1.0))      # current recovery 0.3-1.0 Mt HF-eq -> AHF that could be supplied
REC_REAL = tuple(v / FSA_HFEQ for v in (0.5, 2.0))     # potential recovery 0.5-2.0 Mt HF-eq (SI Section S14)
WORLD_SPAR = 10.0                               # Mt/yr world fluorspar production, 2025

# (d) producer shares (USGS MCS 2026, 2025 estimates)
fl, ph = {}, {}
with open(os.path.join(DATA, "usgs_mcs2026_production_2025.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        fl[r["country"]] = float(r["fluorspar_kt"]); ph[r["country"]] = float(r["phosphate_rock_kt"])
def shares(d, tot, k=3):
    """Three largest producers (country, %) and the Herfindahl-Hirschman index over all listed rows,
    with shares of the USGS world total. 'Other countries' (2 % of fluorspar, 0.3 % of phosphate rock)
    is counted as one producer; splitting it changes the index by less than 10 points."""
    top = sorted(d.items(), key=lambda kv: -kv[1])[:k]
    return [(c, v/tot*100) for c, v in top], sum((v/tot*100)**2 for v in d.values())
SF, HF_ = shares(fl, 10000); SP, HP = shares(ph, 250000)

fig = plt.figure(figsize=(159.2*MM, 148*MM))
gs = fig.add_gridspec(2, 2, left=0.105, right=0.975, bottom=0.128, top=0.958, wspace=0.36, hspace=0.52)
ax = [fig.add_subplot(gs[i, j]) for i in (0, 1) for j in (0, 1)]

def zero_line(a):
    a.axhline(0, color=C_TXT, lw=0.6, zorder=1)

# ---- (a)
a = ax[0]; zero_line(a)
for (lab, y), ls in zip(A.items(), ("--", "-")):
    a.plot(x*100, y, ls, color=C_FSA, lw=1.4, label=lab)
    xb = np.interp(0, -y, x*100)
    a.plot([xb], [0], "o", ms=4.5, mfc="white", mec=C_RED, mew=1.1, zorder=5)
a.set_xlim(0, 40); a.set_ylim(-0.45, 0.3)
a.set_xlabel("Marginal FSA share of supply (%)")
a.set_ylabel("ΔGHG per fluorspar conserved\n(kgCO$_{2eq}$/kg fluorspar)")
a.text(39.5, 0.285, "Higher emission, FSA route", ha="right", va="top", fontsize=6.2, color=C_GREY)
a.text(39.5, -0.435, "Lower emission, FSA route", ha="right", va="bottom", fontsize=6.2, color=C_GREY)
a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, fontsize=6.0, frameon=False, handlelength=2.0, columnspacing=1.0)

# ---- (b)
a = ax[1]; zero_line(a)
for (lab, y), ls in zip(Bs.items(), ("--", "-")):
    a.plot(s*100, y, ls, color=C_FSA2, lw=1.4, label=lab)
    xb = np.interp(0, -y, s*100)
    a.plot([xb], [0], "o", ms=4.5, mfc="white", mec=C_RED, mew=1.1, zorder=5)
a.set_xlim(0, 100); a.set_ylim(-0.6, 0.3)
a.set_xlabel("Silica sold as co-product (%)")
a.set_ylabel("ΔGHG per fluorspar conserved\n(kgCO$_{2eq}$/kg fluorspar)")
a.text(99, 0.285, "Higher emission, FSA route", ha="right", va="top", fontsize=6.2, color=C_GREY)
a.text(99, -0.585, "Lower emission, FSA route", ha="right", va="bottom", fontsize=6.2, color=C_GREY)
a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, fontsize=6.0, frameon=False, handlelength=2.0, columnspacing=1.0)

# ---- (c)
a = ax[2]
a.axvspan(*DEM_AHF, color=C_RED, alpha=0.22, lw=0)
C_RED35 = tuple(0.9 + 0.1*c for c in matplotlib.colors.to_rgb(C_RED))    # 2035 band: light solid fill with dashed edges
a.axvspan(*DEM35_AHF, color=C_RED35, lw=0, zorder=0)
for xe in DEM35_AHF:
    a.axvline(xe, color=C_RED, lw=0.8, ls=(0, (3, 2)), zorder=1)
for (x0, x1), yb, col, lab, (tx, ty, tva) in (
        (REC_REAL, 4.95, C_FSA2, "Potential FSA recovery", (DEM35_AHF[1] + 0.04, 4.95 + 0.17, "bottom")),
        (REC_NOW, 4.45, C_FSA, "Current FSA recovery", (DEM35_AHF[1] + 0.04, 4.45, "center"))):
    a.plot([x0, x1], [yb, yb], "-", color=col, lw=2.0, solid_capstyle="butt", zorder=4)
    for xe in (x0, x1):
        a.plot([xe, xe], [yb - 0.13, yb + 0.13], "-", color=col, lw=1.0, zorder=4)
    a.text(tx, ty, lab, ha="left", va=tva, fontsize=7, fontweight="bold", color="black")
a.plot(V, V*SPAR, "-", color=C_SPAR, lw=1.6)
a.set_xlim(0, 2.2); a.set_ylim(0, 5.5)
a.set_xlabel("AHF supplied from FSA (Mt/yr)", fontsize=9)
a.set_ylabel("Fluorspar avoided (Mt/yr)", fontsize=9)
sec = a.secondary_yaxis("right", functions=(lambda y: y/WORLD_SPAR*100, lambda p: p*WORLD_SPAR/100))
sec.set_ylabel("World fluorspar output (%)", fontweight="bold", fontsize=9)
sec.tick_params(labelsize=7)
a.legend(handles=[Patch(facecolor=C_RED, alpha=0.22, lw=0, label="AHF for electronic-grade demand, 2025"),
                  Patch(facecolor=C_RED35, edgecolor=C_RED, ls=(0, (3, 2)), lw=0.8, label="AHF for projected demand, 2035")],
         loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=1, fontsize=7, frameon=False,
         handlelength=1.4, handleheight=0.9, labelspacing=0.3)

# ---- (d)
a = ax[3]
cols = {"China": "#5C6672", "Mexico": "#A9B1B9", "Mongolia": "#C9CED3", "Morocco": "#A9B1B9", "United States": "#C9CED3"}
for yi, (lab, sh, h) in enumerate((("Phosphate rock", SP, HP), ("Fluorspar", SF, HF_))):
    left = 0
    for c, v in sh:
        a.barh(yi, v, left=left, height=0.46, color=cols.get(c, "#DDE1E5"), edgecolor="white", lw=0.6)
        if v >= 7:
            a.text(left + v/2, yi, c if v >= 13 else c[:2].upper() if c != "United States" else "US",
                   ha="center", va="center", fontsize=5.4, color="white" if c == "China" else C_TXT)
        left += v
    a.barh(yi, 100-left, left=left, height=0.46, color="#EEF0F2", edgecolor="white", lw=0.6)
    if 100-left >= 20:
        a.text((left+100)/2, yi, "Others", ha="center", va="center", fontsize=5.4, color=C_TXT)
a.set_yticks([])
for yi, lab in ((0, f"Phosphate rock, HHI ≈{round(HP, -2):,.0f}"), (1, f"Fluorspar, HHI ≈{round(HF_, -2):,.0f}")):
    a.text(1.5, yi + 0.27, lab, ha="left", va="bottom", fontsize=6.5, fontweight="bold", color=C_TXT)
a.set_xlim(0, 100); a.set_ylim(-0.45, 1.75)
a.set_xlabel("Share of world production (%)")

# panel labels left of the y-axis title of each column (measured after rendering) minus 0.3 mm
fig.canvas.draw()
_r = fig.canvas.get_renderer()
_inv = fig.transFigure.inverted()
def _ylab_x0(a):
    return _inv.transform((a.yaxis.label.get_window_extent(_r).x0, 0))[0]
_pad = 0.3/25.4/fig.get_figwidth()
col_x = {0: min(_ylab_x0(ax[0]), _ylab_x0(ax[2])) - _pad, 1: _ylab_x0(ax[1]) - _pad}
for k, (a, l) in enumerate(zip(ax, "abcd")):
    pos = a.get_position()
    fig.text(col_x[k % 2], pos.y1 + 0.05*pos.height, f"({l})", fontsize=9, fontweight="bold", ha="left", va="bottom")
    for sp in a.spines.values(): sp.set_visible(True)

save(fig, "Fig3_resource")
print(f"base ΔGHG {base:.3f} kgCO2eq/kg fluorspar; break-even (a) marginal FSA share %:",
      [round(float(np.interp(0, -y, x*100)), 1) for y in A.values()],
      "(b) silica sold %:", [round(float(np.interp(0, -y, s*100)), 1) for y in Bs.values()])
print("fluorspar top 3", [(c, round(v, 1)) for c, v in SF], "HHI", round(HF_),
      "| phosphate rock top 3", [(c, round(v, 1)) for c, v in SP], "HHI", round(HP))
