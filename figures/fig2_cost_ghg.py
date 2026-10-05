"""Fig. 2. (a) Unit production cost and (b) cradle-to-gate GHG emissions of the two
routes by purity grade, with on-site emissions as markers.
Values: model/hf_tea_lca.py (flat_breakdown, totals).
Output: output/Fig2a_cost.(png|svg), output/Fig2b_ghg.(png|svg)
"""
from common import MM, C_TXT, set_style, save
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from hf_tea_lca import GRADES, ROUTES, flat_breakdown, totals

set_style()
GL = {"Technical": "Technical", "HighPurity": "High-purity", "Electronic": "Electronic"}

def agg(d, cmap):
    """Sum model items into the plotted categories."""
    out = {k: 0.0 for k in dict.fromkeys(cmap.values())}
    for k, v in d.items():
        base = k.split(":")[-1]; purif = k.startswith("purif:")
        key = cmap.get(("purif" if purif else "") + base) or cmap.get(base)
        if key is None: raise KeyError(k)
        out[key] += v
    return out

def bars(ax, idx, scale, cmap, colors, hatch_key, bd="CtG"):
    xs, xt, tot, cats = [], [], [], list(colors)
    x = 0
    for g in GRADES:
        for r in ROUTES:
            d = agg(flat_breakdown(r, g, bd=bd)[idx], cmap)
            pos, neg = 0.0, 0.0
            for c in cats:
                v = d.get(c, 0.0)/scale
                if v >= 0:
                    ax.bar(x, v, 0.72, bottom=pos, color=colors[c], edgecolor="white", lw=0.4,
                           hatch="////" if c == hatch_key else None)
                    pos += v
                else:
                    ax.bar(x, v, 0.72, bottom=neg, color=colors[c], edgecolor="white", lw=0.4)
                    neg += v
            tot.append((x, pos + neg, pos))
            xs.append(x); xt.append(r); x += 1
        x += 0.6
    return xs, xt, tot

def grade_axis(ax, xs, xt):
    ax.set_xticks(xs); ax.set_xticklabels(xt, fontsize=6.5)
    for i, g in enumerate(GRADES):
        ax.text((xs[2*i] + xs[2*i+1])/2, -0.13, GL[g], transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=7.5, fontweight="bold")
    ax.axhline(0, color=C_TXT, lw=0.6)
    for sp in ax.spines.values(): sp.set_visible(True)

def pair_brackets(ax, tot, lab_h, fmt, note):
    """Bracket over the two bars of each grade with the gap (fluorspar minus FSA) and ratio (fluorspar to FSA)."""
    for i in range(len(GRADES)):
        (x1, n1, t1), (x2, n2, t2) = tot[2*i], tot[2*i+1]
        y = max(t1, t2) + lab_h
        h = lab_h*0.35
        ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], color=C_TXT, lw=0.6)
        ax.text((x1 + x2)/2, y + h*1.5, f"Gap {fmt(n1 - n2)}" + chr(10) + f"Ratio {n1/n2:.2f}",
                ha="center", va="bottom", fontsize=6.2, color=C_TXT, linespacing=1.4)
    ax.text(0.015, 1.0, note, transform=ax.transAxes, ha="left", va="top", fontsize=6.2, color=C_TXT, style="italic")

NOTE = "Gap = fluorspar minus FSA; ratio = fluorspar to FSA"

# ---------------- (a) unit production cost ----------------
cmap2 = {"feed": "Feedstock", "reagents": "Reagents", "fuel": "Fuel and steam", "steam": "Fuel and steam",
         "elec": "Electricity", "capex": "Capital and maintenance", "fixed_om": "Capital and maintenance",
         "labor": "Labor", "disposal": "Disposal and co-products", "coproduct": "Disposal and co-products",
         "purifsteam": "Purification increment", "purifelec": "Purification increment", "purifcapex": "Purification increment",
         "puriffixed_om": "Purification increment", "puriflabor": "Purification increment", "purifp_removal": "Purification increment",
         "purifbyprod_hf": "Industrial-grade HF co-product"}
col2 = {"Feedstock": "#9C6B3C", "Reagents": "#C9A27A", "Fuel and steam": "#5C6672", "Electricity": "#A9B1B9",
        "Capital and maintenance": "#1F4E79", "Labor": "#6E9BC7", "Disposal and co-products": "#D8C9B4",
        "Purification increment": "#C8D6E5", "Industrial-grade HF co-product": "#B9C7A0"}
fig, ax = plt.subplots(figsize=(159.2*MM, 80*MM))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.3, top=0.97)
xs, xt, tot = bars(ax, 0, 1000, cmap2, col2, "Purification increment")
grade_axis(ax, xs, xt)
for x, net, top in tot:
    ax.plot([x-0.36, x+0.36], [net, net], color="black", lw=1.3, zorder=6)
    ax.text(x, top + 0.05, f"{net:.2f}", ha="center", va="bottom", fontsize=6.5, color=C_TXT)
pair_brackets(ax, tot, 0.32, lambda v: f"{v:.2f}", NOTE)
ax.set_ylabel(r"Unit production cost (\$/kg HF)")
ax.set_ylim(-0.6, 4.5)
h = [Patch(facecolor=col2[c], edgecolor="white", hatch="////" if c == "Purification increment" else None, label=c) for c in col2]
h.insert(0, plt.Line2D([], [], color="black", lw=1.3, label="Net unit production cost"))
ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.46, -0.27), ncol=5, frameon=False, fontsize=6.0, handlelength=1.2, columnspacing=0.8, handletextpad=0.5)
save(fig, "Fig2a_cost"); plt.close(fig)

# ---------------- (b) cradle-to-gate GHG emissions ----------------
cmap3 = {"feed": "Feedstock", "reagents": "Sulfuric acid and lime", "fuel": "Fuel", "steam": "Steam", "elec": "Electricity",
         "disposal": "Waste treatment", "credit": "Co-product credit",
         "purifsteam": "Purification increment", "purifelec": "Purification increment", "purifp_removal": "Purification increment"}
col3 = {"Feedstock": "#9C6B3C", "Sulfuric acid and lime": "#C9A27A", "Fuel": "#5C6672", "Steam": "#1F4E79",
        "Electricity": "#A9B1B9", "Waste treatment": "#D8C9B4", "Purification increment": "#C8D6E5", "Co-product credit": "#B9C7A0"}
fig, ax = plt.subplots(figsize=(159.2*MM, 80*MM))
fig.subplots_adjust(left=0.085, right=0.985, bottom=0.3, top=0.97)
xs, xt, tot = bars(ax, 1, 1, cmap3, col3, "Purification increment", bd="CtG")
grade_axis(ax, xs, xt)
i = 0
for g in GRADES:
    for r in ROUTES:
        on = totals(r, g, bd="GtG")[1]                      # on-site emissions (scope 1 + 2)
        ax.plot(xs[i], on, marker="D", ms=4.2, mfc="white", mec="black", mew=0.8, zorder=6)
        x, net, top = tot[i]
        ax.text(x, top + 0.04, f"{net:.2f}", ha="center", va="bottom", fontsize=6.5, color=C_TXT)
        i += 1
pair_brackets(ax, tot, 0.19, lambda v: f"{v:.2f}".replace("-", "−"), NOTE)
ax.set_ylabel("GHG emissions (kg CO$_{2eq}$/kg HF)")
ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]); ax.set_ylim(-0.1, 3.3)
h = [Patch(facecolor=col3[c], edgecolor="white", hatch="////" if c == "Purification increment" else None, label=c) for c in col3]
h.append(plt.Line2D([], [], marker="D", ls="", ms=4.2, mfc="white", mec="black", mew=0.8, label="On-site emissions"))
ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.46, -0.27), ncol=5, frameon=False, fontsize=6.0, handlelength=1.2, columnspacing=0.8, handletextpad=0.5)
save(fig, "Fig2b_ghg"); plt.close(fig)
