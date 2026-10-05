"""Fig. A.1 (Appendix A). (a) HF price by grade and source; (b) fluorspar production by country.
Values: price sources in SI Table S3 (Chinese domestic quotes converted at 7.19 CNY/USD and
divided by 1.13 to remove VAT; 49 % solutions converted to 100 % HF); production from
USGS MCS 2026 (2025 estimates).
Output: output/FigA1_price_supply.(png|svg)
"""
from common import MM, C_TXT, set_style, save
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

set_style()
plt.rcParams.update({"xtick.major.width": 0.8, "ytick.major.width": 0.8})   # tick width of the published panel
C_DOM, C_TRD = "#9C6B3C", "#1F4E79"
FX, VAT = 7.19, 1.13
# (grade position, low, high, type, label); dom = Chinese domestic price, trd = trade unit value
PR = [(0, 11583/FX/VAT/1000, 13033/FX/VAT/1000, "dom", "China ex-works"),
      (0, 2.43, 2.55, "trd", "US import"),
      (1, 7885/0.49/FX/VAT/1000, 8750/0.49/FX/VAT/1000, "dom", "China UP, UP-S"),
      (1, 1346.79/0.49/1000, 1346.79/0.49/1000, "trd", "China export"),
      (2, 2949.56/0.49/1000, 2949.56/0.49/1000, "trd", "China import"),
      (2, 42600/0.49/FX/VAT/1000, 42600/0.49/FX/VAT/1000, "dom", "China G5 quote")]
fig = plt.figure(figsize=(159.2*MM, 70*MM))
a = fig.add_axes([0.075, 0.29, 0.40, 0.64]); b = fig.add_axes([0.585, 0.29, 0.40, 0.64])
off = {"dom": -0.16, "trd": 0.16}
MK = {"dom": "s", "trd": "o"}
for g in range(3):                                   # background band per grade
    a.axvspan(g - 0.46, g + 0.46, color="#F1F3F5" if g % 2 == 0 else "#E6EAEE", lw=0, zorder=0)
BELOW = {"China ex-works", "China UP, UP-S", "China G5 quote"}
for g, lo, hi, k, lab in PR:
    x = g + off[k]; c = C_DOM if k == "dom" else C_TRD; mid = (lo + hi)/2
    a.plot(x, mid, MK[k], ms=5, mfc=c, mec="white", mew=0.5, zorder=4)
    val = f"{lo:.1f}–{hi:.1f}" if hi - lo > 0.05 else f"{mid:.1f}"
    if lab in BELOW:
        a.text(x, mid - 0.4, lab + chr(10) + val, ha="center", va="top", fontsize=5.7, color=c, linespacing=1.1)
    else:
        a.text(x, mid + 0.4, lab + chr(10) + val, ha="center", va="bottom", fontsize=5.7, color=c, linespacing=1.1)
a.set_xticks([0, 1, 2]); a.set_xticklabels(["Technical", "High-purity", "Electronic"], fontsize=7)
a.set_xlim(-0.5, 2.5); a.set_ylim(0, 12)
a.set_ylabel(r"HF price (\$/kg HF)")
a.legend(handles=[Line2D([], [], marker="s", ls="", color=C_DOM, ms=5, label="Chinese domestic price, without VAT"),
                  Line2D([], [], marker="o", ls="", color=C_TRD, ms=5, label="Trade unit value")],
         loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=6.2, handlelength=1.0)
cty = [("China", 6.0), ("Mexico", 1.5), ("Mongolia", 1.5), ("South Africa", 0.41), ("Vietnam", 0.16), ("Others", 0.43)]
b.bar(range(len(cty)), [v for _, v in cty], 0.62, color=["#5C6672"] + ["#A9B1B9"]*5)
b.set_xticks(range(len(cty))); b.set_xticklabels([c for c, _ in cty], rotation=35, ha="right", fontsize=6.6)
b.set_ylabel("Fluorspar production (Mt/yr)"); b.set_ylim(0, 7)
b.text(0, 6.12, "60%", ha="center", va="bottom", fontsize=6.4, color=C_TXT)
for ax_, l in ((a, "a"), (b, "b")):
    for sp in ax_.spines.values(): sp.set_visible(True)
    ax_.text(-0.13, 1.03, f"({l})", transform=ax_.transAxes, fontsize=9, fontweight="bold", va="bottom")
save(fig, "FigA1_price_supply")
