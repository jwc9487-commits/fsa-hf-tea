"""Fig. 4. Uncertainty of the electronic-grade cost gap and the volume at which it
absorbs a one-time qualification cost.
(a) One-at-a-time sensitivity of the electronic-grade cost gap (12 largest inputs);
(b) input values of (a); (c) Monte Carlo cost gap by grade (median and 5-95 %);
(d) one-time cost absorbed versus annual qualified volume and contract term.
Values: model/hf_tea_lca.py (SENS), results/mc_results.npz (model/monte_carlo.py).
Output: output/Fig4_sensitivity_qualification.(png|svg)
"""
import numpy as np
from common import MM, C_TXT, C_RED, set_style, save, load_mc
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from hf_tea_lca import P, GRADES, totals, with_, SENS

set_style()
W, H = 159.2, 184.0       # figure size, mm
TOPY = 108.0              # bottom of the top-row axes, mm
BOTY, BOTH = 24.0, 49.0   # bottom and height of the bottom-row axes, mm
def ax_mm(fig, x, y, w, h): return fig.add_axes([x/W, y/H, w/W, h/H])

# ---------- one-at-a-time sensitivity of the electronic-grade cost gap ----------
G = "Electronic"
def gap(p): return totals("Fluorspar", G, p)[0] - totals("FSA", G, p)[0]
g0 = gap(P)
rows = []
for name, lo, hi in SENS:
    a_, b_ = gap(with_(**lo)) if lo else g0, gap(with_(**hi)) if hi else g0
    rows.append((name, a_, b_))
# input values shown in (b): unit, low, base, high
TAB = {
    "Location factor": ("–", "0.956", "1.0", "1.84"), "Sulfuric acid price": ("$/t", "32", "60", "125"),
    "FSA price": ("$/t", "105", "190", "246"), "Fluorspar price": ("$/t", "405", "470", "504"),
    "Purification AHF input": ("t/t", "1.14", "1.39", "1.39"),
    "Fluorspar-route capital cost": ("$/(t/yr)", "1,388", "2,234", "2,355"),
    "Gypsum landfill cost": ("$/t", "3.5", "20", "70"), "Oleum price ratio": ("–", "1.0", "1.1", "2.5"),
    "FSA-route steam": ("GJ/t", "12", "14", "16"), "Phosphorus removal increment": ("–", "0", "0", "High case"),
    "Steam price": ("$/GJ", "12.8", "18.8", "23.5"), "Fluorspar-route electricity": ("kWh/t", "150", "250", "556"),
    "Electricity price": ("$/kWh", "0.108", "0.118", "0.128"), "Natural gas price": ("$/GJ", "14.3", "16.7", "20.2"),
    "AHF plant staffing": ("persons/kt", "1.44", "1.92", "2.40"), "Kiln fuel": ("GJ/t", "4.0", "5.0", "6.8"),
    "FSA-route electricity": ("kWh/t", "220", "270", "315"), "FSA-route capital cost": ("$/(t/yr)", "2,254", "2,337", "2,466"),
    "Purification capital cost": ("$/(t/yr)", "3,416", "4,764", "6,612"),
    "Industrial-grade HF price": ("$/t", "787", "1,060", "1,600"), "Labor cost": ("k$/person", "20.8", "58.7", "64.0"),
    "Phosphate value": ("$/t", "1,300", "1,000", "900"), "Capacity utilization": ("%", "100", "100", "85")}
rows = [(n, a_, b_) for n, a_, b_ in rows if abs(a_-g0) + abs(b_-g0) > 1e-3]
rows.sort(key=lambda t: max(abs(t[1]-g0), abs(t[2]-g0)))
rows = rows[-12:]
C_LO, C_HI = "#E07B39", "#1F4E79"
mc = load_mc()

fig = plt.figure(figsize=(W*MM, H*MM))
# ---------- (a) tornado ----------
a = ax_mm(fig, 40.0, TOPY, 53.0, 58.0)
n_r = len(rows)
pct = [((lo - g0)/g0*100, (hi - g0)/g0*100) for _, lo, hi in rows]
for i, (dl, dh) in enumerate(pct):
    for v, c in ((dl, C_LO), (dh, C_HI)):
        a.barh(i, v, left=0, height=0.62, color=c, edgecolor="none", zorder=3)
    for v, c in ((dl, C_LO), (dh, C_HI)):
        if abs(v) < 0.05: continue
        a.text(v + (0.8 if v > 0 else -0.8), i, f"{v:+.0f}%".replace("-", "−") if abs(v) >= 1 else f"{v:+.1f}%".replace("-", "−"),
               ha="left" if v > 0 else "right", va="center", fontsize=5.6, color="black", zorder=4)
a.axvline(0, color="black", lw=0.7, zorder=4)
for y in np.arange(-0.5, n_r, 1):
    a.axhline(y, color="#D9DDE1", lw=0.4, zorder=1)
a.set_yticks(range(n_r)); a.set_yticklabels([r[0] for r in rows], fontsize=6.3)
a.tick_params(axis="y", length=0, pad=3)
a.set_ylim(-0.5, n_r - 0.5)
a.set_xlim(-40, 35); a.set_xticks(range(-40, 31, 10))
a.set_xticklabels([f"{v}".replace("-", "−") for v in range(-40, 31, 10)])
a.set_xlabel("Change in cost gap (%)")
for sp in a.spines.values(): sp.set_visible(True)
a.annotate("", xy=(0, n_r - 0.5), xytext=(0, n_r + 0.35), annotation_clip=False,
           arrowprops=dict(arrowstyle="-|>", color="black", lw=0.8, mutation_scale=7))
a.text(0, n_r + 0.45, f"Base cost gap, electronic grade\n{g0:.2f} \\$/kg HF", ha="center", va="bottom",
       fontsize=7, fontweight="bold", linespacing=1.3)
a.legend(handles=[Patch(color=C_LO, label="Low value"), Patch(color=C_HI, label="High value")],
         loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False, fontsize=6.0,
         handlelength=0.9, handleheight=0.9, handletextpad=0.4, borderaxespad=0.2, columnspacing=1.2)

# ---------- (c) Monte Carlo cost gap ----------
b = ax_mm(fig, 20.0, BOTY, 56.0, BOTH)
data = [mc[f"U_S_{g}"] - mc[f"U_F_{g}"] for g in GRADES]
vp = b.violinplot(data, positions=[0, 1, 2], widths=0.7, showextrema=False)
for body in vp["bodies"]:
    body.set_facecolor("#6E9BC7"); body.set_edgecolor("none"); body.set_alpha(0.55)
for i, d in enumerate(data):
    q5, q50, q95 = np.percentile(d, [5, 50, 95])
    b.plot([i, i], [q5, q95], color="#1F4E79", lw=1.2)
    b.plot(i, q50, "o", ms=4, mfc="white", mec="#1F4E79", mew=1.0)
b.axhline(0, color=C_TXT, lw=0.6)
b.set_xticks([0, 1, 2]); b.set_xticklabels(["Technical", "High-" + chr(10) + "purity", "Electronic"], fontsize=6.6)
b.set_ylabel("Cost gap, fluorspar minus FSA" + chr(10) + r"(\$/kg HF)", linespacing=1.3)
b.set_ylim(-0.1, 1.6)
for sp in b.spines.values(): sp.set_visible(True)

# ---------- (b) input values; top rule level with the top of (a) ----------
TX0, TW = 96.0, 62.0
t = ax_mm(fig, TX0, TOPY, TW, 58.0); t.axis("off"); t.set_xlim(0, 1); t.set_ylim(TOPY, TOPY + 58.0)   # y data in mm
col = {"name": 0.0, "lo": 0.655, "base": 0.785, "hi": 0.915}
TK = dict(fontsize=6.2, va="center", clip_on=False)
ytop = TOPY + 58.0; HDR = 5.0; DY = 4.0
t.plot([0, 1], [ytop, ytop], color="black", lw=0.9, clip_on=False)
for k, h in (("lo", "Low"), ("base", "Base"), ("hi", "High")):
    t.text(col[k], ytop - HDR/2, h, ha="center", **TK)
t.plot([0, 1], [ytop - HDR, ytop - HDR], color="black", lw=0.5, clip_on=False)
for j_, r in enumerate(rows[::-1]):                           # same order as the tornado, top down
    u, lo, ba, hi = TAB[r[0]]
    y = ytop - HDR - (j_ + 0.5)*DY
    t.text(col["name"], y, f"{r[0]} ({u})" if u != "–" else r[0], ha="left", **TK)
    for k, v in (("lo", lo), ("base", ba), ("hi", hi)):
        t.text(col[k], y, v, ha="center", **TK)
ybot = ytop - HDR - len(rows)*DY
t.plot([0, 1], [ybot, ybot], color="black", lw=0.9, clip_on=False)

# ---------- (d) one-time qualification cost absorbed ----------
C, C_BAND, C_REF = "#1F4E79", "#6E9BC7", "#8A939C"
D = g0                                           # $/kg = M$ per kt
gapmc = mc[f"U_S_{G}"] - mc[f"U_F_{G}"]
p5, p95 = np.percentile(gapmc, [5, 95])
DEM = 350                                        # world electronic-grade demand, kt/yr (midpoint of 0.3-0.4 Mt)
V = np.linspace(0, 8, 161)
dax = ax_mm(fig, 92.0, BOTY, 58.0, BOTH)
dax.fill_between(V, p5*V*5, p95*V*5, color=C_BAND, alpha=0.25, lw=0)
for tt, lw, al in ((1.5, 1.0, 0.55), (3, 1.0, 0.55), (5, 2.0, 1.0), (10, 1.0, 0.55)):
    dax.plot(V, D*V*tt, color=C, lw=lw, alpha=al)
    yend = D*8*tt
    if yend <= 88: dax.text(8.12, yend, f"{tt:g} yr", va="center", fontsize=6.3, color=C)
    else:
        xe = 88/(D*tt); dax.text(xe, 89, f"{tt:g} yr", ha="center", va="bottom", fontsize=6.3, color=C)
dax.axhline(10, color=C_REF, lw=0.9, ls="--")
v5, v15 = 10/(D*5), 10/(D*1.5)
for v, lab, xt, yt, ha in ((v5, f"{v5:.1f} kt/yr, 5 yr", 0.25, 34.0, "left"), (v15, f"{v15:.1f} kt/yr, 18 months", 7.75, 4.6, "right")):
    dax.plot(v, 10, "o", ms=5, mfc="white", mec=C_RED, mew=1.2, zorder=5)
    dax.annotate(lab, (v, 10), xytext=(xt, yt), fontsize=6.3, color=C_RED, va="center", ha=ha,
                 arrowprops=dict(arrowstyle="-", color=C_RED, lw=0.6, shrinkA=0, shrinkB=3))
dax.set_xlim(0, 8); dax.set_ylim(0, 90)
dax.set_xlabel("Annual qualified volume (kt/yr)")
dax.set_ylabel("One-time cost absorbed\n($ million)".replace("$", r"\$"), linespacing=1.25)
top = dax.secondary_xaxis("top", functions=(lambda v: v/DEM*100, lambda s: s*DEM/100))
top.set_xlabel("Share of world electronic-grade demand (%)", fontweight="bold"); top.tick_params(labelsize=7)
for sp in dax.spines.values(): sp.set_visible(True)
dax.legend(handles=[Line2D([], [], color=C, lw=2.0, label="Base cost gap, by contract term"),
                    Patch(color=C_BAND, alpha=0.4, label="5–95% range of cost gap, 5-yr term"),
                    Line2D([], [], color=C_REF, lw=0.9, ls="--", label="$10 million qualification cost".replace("$", r"\$"))],
           loc="upper center", bbox_to_anchor=((92.0 + 58.0*0.45)/W, 13.0/H), bbox_transform=fig.transFigure,
           ncol=1, frameon=False, fontsize=6.2, handlelength=1.6, labelspacing=0.35)

# ---------- panel labels ----------
fig.canvas.draw()
_rr = fig.canvas.get_renderer(); _inv = fig.transFigure.inverted()
off = 0.3/W
_xa = min(_inv.transform((tl.get_window_extent(_rr).x0, 0))[0] for tl in a.get_yticklabels()) - off
_xa = min(_xa, 2.0/W)
_xb = _inv.transform((b.yaxis.label.get_window_extent(_rr).x0, 0))[0] - off
_xd = _inv.transform((dax.yaxis.label.get_window_extent(_rr).x0, 0))[0] - off
_ytop = (TOPY + 58.0 + 12.4)/H
_ybot = (BOTY + BOTH + 8.6)/H
LAB = dict(fontsize=9, fontweight="bold", va="bottom", ha="right")
fig.text(_xa + 4.6/W, _ytop, "(a)", **LAB)
fig.text((TX0 + 4.6)/W, _ytop, "(b)", **LAB)
fig.text((TX0 + 6.0)/W, _ytop + 0.001, "Parameter values for the sensitivity analysis", fontsize=7.1, fontweight="bold", va="bottom", ha="left")
fig.text(_xb, _ybot, "(c)", **LAB)
fig.text(_xd, _ybot, "(d)", **LAB)
save(fig, "Fig4_sensitivity_qualification")
print(f"base electronic-grade cost gap {g0:.3f} $/kg; tornado range {min(min(p) for p in pct):.1f} to {max(max(p) for p in pct):.1f} %;"
      f" volume absorbing $10 million: {v5:.2f} kt/yr over 5 yr, {v15:.2f} kt/yr over 18 months")
