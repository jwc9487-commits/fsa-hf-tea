"""Fig. S1. System boundary and multifunctional points M1-M6 of the two HF routes
(schematic; no model values). Output: output/FigS1_system_boundary.(png|svg)
"""
from common import MM, save
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

plt.rcParams["svg.fonttype"] = "none"
plt.rcParams.update({"font.family": "Arial", "font.size": 6.8})
MM = 1/25.4
W, H = 159.2, 88
fig = plt.figure(figsize=(W*MM, H*MM))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
C_TXT, C_SP, C_FSA, C_PUR, C_UP, C_LN = "#3A3F45", "#EFE3D3", "#DCE6F0", "#E4E8EC", "#F4F5F6", "#5C6672"
NL = "\n"

def box(x, y, w, h, text, fc, bold=False, fs=6.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=fc, ec=C_LN, lw=0.7, zorder=3))
    if text:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, color=C_TXT,
                fontweight="bold" if bold else "normal", zorder=4, linespacing=1.15)

def arrow(p0, p1, rad=0.0):
    ax.annotate("", xy=p1, xytext=p0, zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=C_LN, lw=0.9, mutation_scale=7,
                                shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"))

def badge(x, y, n):
    ax.add_patch(Circle((x, y), 2.3, fc="#B02418", ec="none", zorder=6))
    ax.text(x, y, f"M{n}", ha="center", va="center", fontsize=5.6, color="white", fontweight="bold", zorder=7)

def label(x, y, t, ha="center", va="center", color=C_TXT, fs=6.3, style="normal", bold=False):
    ax.text(x, y, t, ha=ha, va=va, fontsize=fs, color=color, style=style,
            fontweight="bold" if bold else "normal", zorder=5, linespacing=1.15)

# ---------- boundaries ----------
ax.add_patch(FancyBboxPatch((2, 6), 122, 78, boxstyle="round,pad=0,rounding_size=2", fc="none", ec=C_TXT, lw=1.0, zorder=1))
label(4, 81.2, "Cradle-to-gate boundary", ha="left", bold=True, fs=6.6)
ax.add_patch(FancyBboxPatch((42, 10), 80, 66, boxstyle="round,pad=0,rounding_size=2", fc="none", ec=C_LN, lw=0.9, ls=(0, (4, 2)), zorder=1))
label(44, 73.2, "On-site boundary", ha="left", bold=True, fs=6.6, color=C_LN)

# ---------- fluorspar route ----------
label(4, 70, "Fluorspar route", ha="left", bold=True, fs=7)
box(5, 56, 26, 9, "Fluorspar mining", C_SP)
box(5, 44, 26, 9, "Sulfuric acid and" + NL + "oleum production", C_SP)
box(45.5, 50, 31, 11, "Kiln reaction and" + NL + "AHF distillation", C_SP, bold=True, fs=6.4)
arrow((31, 60.5), (45.5, 57.5)); arrow((31, 48.5), (45.5, 53.5))
arrow((57, 61), (57, 68.5)); label(57, 70.2, "Fluorogypsum", fs=6.2); badge(52.5, 65.5, 4)
arrow((68, 61), (80, 68.5)); label(86, 70.2, "By-product FSA", fs=6.2); badge(79.5, 64, 5)

# ---------- FSA route ----------
label(4, 36, "FSA route", ha="left", bold=True, fs=7)
box(5, 22, 26, 9, "Phosphate rock mining", C_FSA)
box(5, 10, 26, 9, "Wet-process" + NL + "phosphoric acid plant", C_FSA)
arrow((18, 22), (18, 19))
arrow((18, 10), (18, 2.2)); label(20, 3.2, "Phosphoric acid, main product", ha="left", fs=5.8, style="italic")
box(45.5, 22, 31, 11, "FSA decomposition in" + NL + "concentrated sulfuric acid", C_FSA, bold=True, fs=6.3)
arrow((31, 16.5), (45.5, 25.5)); label(35.5, 24.5, "FSA", fs=6.2, style="italic"); badge(37.5, 17.2, 1)
arrow((53, 22), (31, 12.3), rad=-0.15)
badge(49.5, 15.2, 2); badge(54.8, 15.2, 3); label(58.3, 15.2, "Silica, diluted acid", ha="left", fs=5.9, style="italic")

# ---------- common AHF and shared purification ----------
box(77, 36, 22, 11, "Technical-grade" + NL + "AHF", "#FFFFFF", bold=True, fs=6.2)
arrow((76.5, 55.5), (84, 47)); arrow((76.5, 27.5), (84, 36))
box(100, 30, 21.5, 23, "", C_PUR)
label(110.75, 48.5, "Shared" + NL + "purification", bold=True, fs=6.4)
label(110.75, 38.5, "Arsenic oxidation" + NL + "Multistage rectification" + NL + "Membrane filtration", fs=5.5)
arrow((99, 41.5), (100, 41.5))
box(128, 56, 29, 9, "Technical grade" + NL + "AHF", C_UP)
box(128, 40, 29, 9, "High-purity grade" + NL + "UP, UP-S", C_UP)
box(128, 24, 29, 9, "Electronic grade" + NL + "UPSS, UPSSS", C_UP)
ax.plot([88, 88], [47, 60.5], color=C_LN, lw=0.9, zorder=2); arrow((88, 60.5), (128, 60.5))
arrow((121.5, 44), (128, 44.5)); arrow((121.5, 36), (128, 28.5))
arrow((110.75, 30), (110.75, 19)); label(110.75, 15.8, "Industrial-grade HF" + NL + "co-product", fs=5.9, style="italic"); badge(105.5, 23.5, 6)

# ---------- legend and exclusions ----------
ax.add_patch(Circle((130, 13.5), 2.1, fc="#B02418", ec="none"))
ax.text(130, 13.5, "Mn", ha="center", va="center", fontsize=5.2, color="white", fontweight="bold")
label(133.5, 13.5, "Multifunctional point", ha="left", fs=6.2)
label(127.5, 7.2, "Excluded: product transport," + NL + "packaging, quality control," + NL + "capital goods", ha="left", fs=5.7, color=C_LN)

save(fig, "FigS1_system_boundary")
