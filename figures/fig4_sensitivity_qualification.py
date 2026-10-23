"""Fig. 4. Uncertainty of the electronic-grade cost gap and the volume at which it
absorbs a one-time qualification cost.
(a) One-at-a-time sensitivity of the electronic-grade cost gap (12 largest inputs),
    with the low, base, and high input values listed beside each bar;
(b) Monte Carlo cost gap by grade, labelled with the median, the 5th and 95th
    percentiles, and the standard deviation;
(c) one-time cost absorbed versus annual qualified volume and contract term.
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
FS, FS_AX, FS_LAB = 7, 9, 9       # ticks, annotations, legends / axis titles / panel labels
plt.rcParams.update({"axes.labelsize": FS_AX})
W = 159.2                         # figure width, mm (height follows from the number of rows)
RP = 4.6                          # row height of (a), mm
B_Y0 = 22.0                       # bottom of the bottom-row axes, mm
def ax_mm(fig, x, y, w, h): return fig.add_axes([x/W, y/H, w/W, h/H])
def ftext(x, y, s, **kw): return fig.text(x/W, y/H, s, **kw)
def fline(x0, x1, y, **kw): fig.add_artist(Line2D([x0/W, x1/W], [y/H, y/H], transform=fig.transFigure, **kw))

# ---------- one-at-a-time sensitivity of the electronic-grade cost gap ----------
G = "Electronic"
def gap(p): return totals("Fluorspar", G, p)[0] - totals("FSA", G, p)[0]
g0 = gap(P)
rows = []
for name, lo, hi in SENS:
    a_, b_ = gap(with_(**lo)) if lo else g0, gap(with_(**hi)) if hi else g0
    rows.append((name, a_, b_))
# input values listed in (a): unit, low, base, high
TAB = {
    "Location factor": ("–", "0.956", "1.0", "1.84"), "Sulfuric acid price": ("$/t", "32", "60", "125"),
    "FSA price": ("$/t", "105", "190", "246"), "Fluorspar price": ("$/t", "405", "470", "504"),
    "Purification AHF input": ("t/t", "1.14", "1.39", "1.39"),
    "Fluorspar-route capital cost": ("$/(t/yr)", "1,388", "2,234", "2,355"),
    "Gypsum landfill cost": ("$/t", "3.5", "20", "70"), "Oleum price ratio": ("–", "1.0", "1.1", "2.5"),
    "FSA-route steam": ("GJ/t", "12", "14", "16"), "Phosphorus removal increment": ("$/kg", "0", "0", "0.094"),
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
# the (c) axes box equals the (a) axes box; (b) shares the top and bottom lines of (c)
B_H = len(rows)*RP                # bottom-row axes height = (a) axes height
A_Y0 = B_Y0 + B_H + 17.5          # bottom of the (a) axes, mm
H = A_Y0 + len(rows)*RP + 11.3    # figure height, mm
C_LO, C_HI = "#E07B39", "#1F4E79"
mc = load_mc()
esc = lambda s: s.replace("$", r"\$")

fig = plt.figure(figsize=(W*MM, H*MM))
_r = fig.canvas.get_renderer()
def width_mm(t): return t.get_window_extent(_r).width / fig.dpi * 25.4

# ---------- (a) tornado with the input values as label columns ----------
n_r = len(rows)
XN = 4.0                                            # left edge of the parameter column, mm
names = [ftext(XN, A_Y0 + (i + 0.5)*RP, esc(f"{r[0]} ({TAB[r[0]][0]})" if TAB[r[0]][0] != "–" else r[0]),
               ha="left", va="center", fontsize=FS) for i, r in enumerate(rows)]
fig.canvas.draw()
name_w = max(width_mm(t) for t in names)
CW = 10.5                                           # width of each value column, mm
XL = XN + name_w + 2.0 + CW/2; XB = XL + CW; XH = XB + CW
AX0 = XH + CW/2 + 3.0
AW = W - AX0 - 2.5
a = ax_mm(fig, AX0, A_Y0, AW, n_r*RP)
for i, r in enumerate(rows):
    _, lo, ba, hi = TAB[r[0]]
    y = A_Y0 + (i + 0.5)*RP
    for x, v in ((XL, lo), (XB, ba), (XH, hi)):
        ftext(x, y, v, ha="center", va="center", fontsize=FS)
ytop = A_Y0 + n_r*RP
for x, h, c in ((XN, "Parameter", "black"), (XL, "Low", C_LO), (XB, "Base", "black"), (XH, "High", C_HI)):
    ftext(x, ytop + 2.4, h, ha="left" if h == "Parameter" else "center", va="center", fontsize=FS, fontweight="bold", color=c)
for k in range(n_r + 1):                            # row rules from the parameter column to the axes
    fline(XN, AX0, A_Y0 + k*RP, color="#D9DDE1", lw=0.4, zorder=0)
fline(XN, AX0 - 1.5, ytop, color="black", lw=0.6)   # header rule, level with the top of the axes
pct = [((lo - g0)/g0*100, (hi - g0)/g0*100) for _, lo, hi in rows]
for i, (dl, dh) in enumerate(pct):
    for v, c in ((dl, C_LO), (dh, C_HI)):
        a.barh(i, v, left=0, height=0.62, color=c, edgecolor="none", zorder=3)
    for v, c in ((dl, C_LO), (dh, C_HI)):
        if abs(v) < 0.05: continue
        a.text(v + (0.8 if v > 0 else -0.8), i, f"{v:+.0f}%".replace("-", "−") if abs(v) >= 1 else f"{v:+.1f}%".replace("-", "−"),
               ha="left" if v > 0 else "right", va="center", fontsize=FS, color="black", zorder=4)
a.axvline(0, color="black", lw=0.7, zorder=4)
for y in np.arange(-0.5, n_r, 1):
    a.axhline(y, color="#D9DDE1", lw=0.4, zorder=1)
a.set_yticks([])
a.set_ylim(-0.5, n_r - 0.5)
a.set_xlim(-40, 35); a.set_xticks(range(-40, 31, 10))
a.set_xticklabels([f"{v}".replace("-", "−") for v in range(-40, 31, 10)])
a.set_xlabel("Change in cost gap (%)")
for sp in a.spines.values(): sp.set_visible(True)
a.annotate("", xy=(0, n_r - 0.5), xytext=(0, n_r + 0.45), annotation_clip=False,
           arrowprops=dict(arrowstyle="-|>", color="black", lw=0.8, mutation_scale=7))
a.text(0, n_r + 0.55, f"Base cost gap, electronic grade\n{g0:.2f} \\$/kg HF", ha="center", va="bottom",
       fontsize=8, fontweight="bold", linespacing=1.3)
fig.legend(handles=[Patch(color=C_LO, label="Low value"), Patch(color=C_HI, label="High value")],   # below the value columns
           loc="center left", bbox_to_anchor=(XN/W, (A_Y0 - 4.6)/H), ncol=2, frameon=False, fontsize=FS,
           handlelength=0.9, handleheight=0.9, handletextpad=0.4, borderaxespad=0.0, borderpad=0.0, columnspacing=1.5)

# ---------- (b) Monte Carlo cost gap with median, 5-95 %, and standard deviation ----------
b = ax_mm(fig, 19.0, B_Y0, 46.0, B_H)
data = [mc[f"U_S_{g}"] - mc[f"U_F_{g}"] for g in GRADES]
vp = b.violinplot(data, positions=[0, 1, 2], widths=0.7, showextrema=False)
for body in vp["bodies"]:
    body.set_facecolor("#6E9BC7"); body.set_edgecolor("none"); body.set_alpha(0.55)
stats = []
for i, d in enumerate(data):
    q5, q50, q95 = np.percentile(d, [5, 50, 95]); sd = d.std(ddof=1)
    stats.append((GRADES[i], q50, q5, q95, d.mean(), sd))
    b.plot([i, i], [q5, q95], color="#1F4E79", lw=1.2)
    b.plot(i, q50, "o", ms=4, mfc="white", mec="#1F4E79", mew=1.0, zorder=5)
    b.text(i + 0.10, q50, f"{q50:.2f}", ha="left", va="center", fontsize=FS, fontweight="bold", zorder=6)
    b.text(i + 0.06, q95, f"{q95:.2f}", ha="left", va="center", fontsize=FS, zorder=6)
    b.text(i + 0.06, q5, f"{q5:.2f}", ha="left", va="center", fontsize=FS, zorder=6)
    b.text(i, 1.60, f"SD {sd:.2f}", ha="center", va="bottom", fontsize=FS, zorder=6)
b.axhline(0, color=C_TXT, lw=0.6)
b.set_xticks([0, 1, 2]); b.set_xticklabels(["Technical", "High-purity", "Electronic"])
b.set_xlim(-0.55, 2.55)
b.set_ylabel("Cost gap, fluorspar minus FSA" + chr(10) + r"(\$/kg HF)", linespacing=1.3)
b.set_ylim(-0.1, 1.75)
for sp in b.spines.values(): sp.set_visible(True)
b.legend(handles=[Patch(facecolor="#6E9BC7", alpha=0.55, label="Monte Carlo distribution"),
                  Line2D([], [], color="#1F4E79", lw=0, marker="o", ms=4, mfc="white", mec="#1F4E79", mew=1.0, label="Median"),
                  Line2D([], [], color="#1F4E79", lw=1.2, label="5–95% range")],
         loc="upper center", bbox_to_anchor=(0.5, -7.44/B_H), ncol=1, frameon=False, fontsize=FS,
         handlelength=1.6, labelspacing=0.3)

# ---------- (c) one-time qualification cost absorbed ----------
C, C_BAND, C_REF = "#1F4E79", "#6E9BC7", "#8A939C"
D = g0                                           # $/kg = M$ per kt
gapmc = mc[f"U_S_{G}"] - mc[f"U_F_{G}"]
p5, p95 = np.percentile(gapmc, [5, 95])
V = np.linspace(0, 8, 161)
dax = ax_mm(fig, AX0, B_Y0, AW, B_H)      # same x, width, and height as the (a) axes
dax.fill_between(V, p5*V*5, p95*V*5, color=C_BAND, alpha=0.25, lw=0)
for tt, lw, al in ((1.5, 1.0, 0.55), (3, 1.0, 0.55), (5, 2.0, 1.0), (10, 1.0, 0.55)):
    dax.plot(V, D*V*tt, color=C, lw=lw, alpha=al)
# contract-term labels inside the axes near the line ends: 10 yr above its line, 5 yr above the 5-95 % band,
# 3 yr below its line (the band lies above it), 1.5 yr above its line and offset to the left of the 3 yr label
HH = 1.25/(B_H/90) + 1.0                 # half the 7 pt text height plus a margin, in y units
for tt, xr, y in ((10, 7.88, D*7.88*10 + HH), (5, 7.88, p95*5*7.88 + HH), (3, 7.88, D*7.43*3 - HH), (1.5, 7.33, D*7.33*1.5 + HH)):
    dax.text(xr, y, f"{tt:g} yr", ha="right", va="center", fontsize=FS, color=C, fontweight="bold" if tt == 5 else "normal")
dax.axhline(10, color=C_REF, lw=0.9, ls="--")
v5, v15 = 10/(D*5), 10/(D*1.5)
dax.plot(v5, 10, "o", ms=5, mfc="white", mec=C_RED, mew=1.2, zorder=5)
dax.annotate(f"{v5:.1f} kt/yr, 5 yr", (v5, 10), xytext=(0.35, 40.0), fontsize=FS, color=C_RED, va="center", ha="left",
             arrowprops=dict(arrowstyle="-", color=C_RED, lw=0.6, shrinkA=0, shrinkB=3))
dax.plot(v15, 10, "o", ms=5, mfc="white", mec=C_RED, mew=1.2, zorder=5)
dax.text(7.88, 5.2, f"{v15:.1f} kt/yr, 18 months", fontsize=FS, color=C_RED, va="center", ha="right")
dax.set_xlim(0, 8); dax.set_ylim(0, 90)
dax.set_xlabel("Annual volume (kt/yr)")
dax.set_ylabel("One-time cost absorbed\n($ million)".replace("$", r"\$"), linespacing=1.25)
for sp in dax.spines.values(): sp.set_visible(True)
dax.legend(handles=[Line2D([], [], color=C, lw=2.0, label="Base cost gap, by contract term"),
                    Patch(color=C_BAND, alpha=0.4, label="5–95% range of cost gap, 5-yr term"),
                    Line2D([], [], color=C_REF, lw=0.9, ls="--", label="$10 million qualification cost".replace("$", r"\$"))],
           loc="upper center", bbox_to_anchor=(0.5, -7.44/B_H), ncol=1, frameon=False, fontsize=FS,
           handlelength=1.6, labelspacing=0.3)

# ---------- panel labels: 0.3 mm left of the y-axis title of the same column ----------
fig.canvas.draw()
_r = fig.canvas.get_renderer(); _inv = fig.transFigure.inverted()
def x0_mm(t): return _inv.transform((t.get_window_extent(_r).x0, 0))[0]*W
xb = x0_mm(b.yaxis.label) - 0.3
xc = x0_mm(dax.yaxis.label) - 0.3
xa = min(xb, XN - 0.3)                              # (a) has no y-axis title; aligned with (b)
LAB = dict(fontsize=FS_LAB, fontweight="bold", va="bottom", ha="left")
ftext(xa, H - 4.6, "(a)", **LAB)
ftext(xb, B_Y0 + B_H + 3.2, "(b)", **LAB)
ftext(xc, B_Y0 + B_H + 3.2, "(c)", **LAB)
save(fig, "Fig4_sensitivity_qualification")
print(f"base electronic-grade cost gap {g0:.3f} $/kg; tornado range {min(min(p) for p in pct):.1f} to {max(max(p) for p in pct):.1f} %;"
      f" volume absorbing $10 million: {v5:.2f} kt/yr over 5 yr, {v15:.2f} kt/yr over 18 months")
for g, q50, q5, q95, mu, sd in stats:
    print(f"Monte Carlo {g}: median {q50:.3f}, 5-95 % {q5:.3f}-{q95:.3f}, mean {mu:.3f}, SD {sd:.3f}")
