"""Shared paths and plotting style for the figure scripts.

Each figure script is run from the repository root, for example
    python figures/fig2_cost_ghg.py
and writes PNG (500 dpi) and SVG files to output/.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "model"))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

MM = 1/25.4            # inch per mm; double-column width is 159.2 mm
C_TXT, C_RED = "#3A3F45", "#B02418"

def set_style():
    plt.rcParams["svg.fonttype"] = "none"            # keep SVG text editable
    plt.rcParams["mathtext.default"] = "regular"     # subscripts in the body font
    plt.rcParams.update({"font.family": "Arial", "font.size": 7, "axes.linewidth": 0.7,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.labelsize": 8,
                         "axes.labelweight": "bold", "xtick.major.width": 0.6, "ytick.major.width": 0.6})

def load_mc():
    """Monte Carlo results written by model/monte_carlo.py."""
    f = os.path.join(ROOT, "results", "mc_results.npz")
    if not os.path.exists(f):
        raise FileNotFoundError("results/mc_results.npz not found; run python model/monte_carlo.py first")
    return np.load(f)

def save(fig, name):
    base = os.path.join(OUT, name)
    fig.savefig(base + ".png", dpi=500); fig.savefig(base + ".svg")
    print("saved", os.path.relpath(base, ROOT) + ".png/.svg")
