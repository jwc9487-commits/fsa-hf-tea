"""
Monte Carlo analysis of the HF model (SI Table S8).

- Distributions: triangular (low, base, high), with the same ranges as the
  one-at-a-time sensitivity in hf_tea_lca.SENS.
- Not sampled (treated as separate scenarios): location (Chinese wages, other
  capital-cost bases), FSA status (cut-off, avoided neutralization), silica
  sale, non-integrated site.
- Reported: median (5th-95th percentile), share of draws, Spearman rank
  correlation.

Run from the repository root:  python model/monte_carlo.py
Writes results/mc_results.npz (N = 5,000, seed 20260929), which the figure
scripts read.
"""
import os, sys, copy
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hf_tea_lca import P, GRADES, totals

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N, SEED = 5000, 20260929
rng = np.random.default_rng(SEED)

# name: (low, base, high); the base must equal the value in P (checked below).
# The order of this dictionary fixes the random stream and must not be changed.
TRI = {
    "p_elec":      (0.108, 0.118, 0.128),   # KEPCO industrial 2023 / 2024 / 2025, / 1,422 KRW/USD
    "p_ng":        (12.9*1.11, 16.7, 18.2*1.11),
    "p_steam":     (30/2.34, 18.8, 55/2.34),
    "p_h2so4":     (32, 60, 125),
    "p_fsa":       (105, 190, 246),          # the M1 allocation follows p_fsa
    "p_p2o5":      (900, 1000, 1300),
    "e_p2o5":      (1379, 1379, 1488),       # high = GREET cradle-to-gate including product transport
    "m_fsa_p2o5":  (0.027, 0.040, 0.053),   # BREF
    "p_spar":      (405, 470, 504),
    "oleum_mult":  (1.0, 1.1, 2.5),
    "lab_ahf":     (1.44, 1.92, 2.40),
    "ng_spar":     (4.0, 5.0, 6.8),
    "el_spar":     (150, 250, 556),
    "stm_fsa":     (12, 14, 16),
    "el_fsa":      (220, 270, 315),
    "capex_spar":  (1388, 2234, 2355),
    "capex_fsa":   (2254, 2337, 2466),
    "loc_cn_kr":   (0.956, 1.0, 1.84),
    "capex_hp":    (417/0.495, 1380, 949/0.495),
    "capex_ehf":   (3416, 4764, 6612),
    "hp_energy_frac": (0.2, 0.4, 0.7),
    "ahf_in":      (1/0.88, 1.39, 1.39),     # electronic-grade yield 88-73 %
    "ahf_in_hp":   (1/0.94, 1.17, 1/0.80),   # high-purity yield 94-80 %
    "p_ind_hf":    (787, 1060, 1600),
    "gyp_sold":    (0.25, 0.5, 0.9),
    "c_landfill":  (3.5, 20, 70),
    "ci_h2so4_ctg": (0.045, 0.17, 0.17),
    "ci_elec_ctg":  (0.495, 0.53, 0.53),
}
P_HIGH = dict(p_capex_frac=0.05, p_rm_steam=0.25, p_rm_elec=15, p_yield=0.03)   # phosphorus removal, high case

def tri(lo, mode, hi, n):
    return np.full(n, mode) if hi == lo else rng.triangular(lo, mode, hi, n)

S = {k: tri(*v, N) for k, v in TRI.items()}
S["p_rm_scale"] = rng.uniform(0, 1, N)                 # phosphorus removal increment: uniform between 0 (base) and the high case

def build(i):
    p = copy.deepcopy(P)
    for k in TRI:
        if k == "ci_h2so4_ctg":
            p["ci_h2so4"] = (0.0, S[k][i]); p["ci_oleum"] = (0.0, S[k][i]*P["ci_oleum"][1]/P["ci_h2so4"][1])
        elif k == "ci_elec_ctg": p["ci_elec"] = (P["ci_elec"][0], S[k][i])
        else: p[k] = S[k][i]
    p["capex_fsa"] = S["capex_fsa"][i]*S["loc_cn_kr"][i]
    for k, v in P_HIGH.items(): p[k] = v*S["p_rm_scale"][i]
    return p

# check that each base value equals the model value
for k, (lo, m, hi) in TRI.items():
    base = {"ci_h2so4_ctg": P["ci_h2so4"][1], "ci_elec_ctg": P["ci_elec"][1]}.get(k, P.get(k))
    assert abs(base - m) < 1e-6 * max(1, abs(m)), (k, base, m)

# U = unit production cost ($/kg), N = cradle-to-gate emissions (kg CO2eq/kg); S = fluorspar route, F = FSA route
OUT = {f"{m}_{r}_{g}": np.empty(N) for m in ("U", "N") for r in ("S", "F") for g in GRADES}
for i in range(N):
    p = build(i)
    for g in GRADES:
        (us, es), (uf, ef) = totals("Fluorspar", g, p), totals("FSA", g, p)
        OUT[f"U_S_{g}"][i], OUT[f"U_F_{g}"][i] = us, uf
        OUT[f"N_S_{g}"][i], OUT[f"N_F_{g}"][i] = es, ef

def q(x): return f"{np.median(x):5.2f} ({np.percentile(x,5):5.2f}-{np.percentile(x,95):5.2f})"

if __name__ == "__main__":
    print(f"MC N={N} seed={SEED} · median (5th-95th percentile)\n")
    print(f"{'':11s} {'UPC fluorspar':>20s} {'UPC FSA':>20s} {'gap $/kg':>20s} {'ratio':>20s} {'P(FSA cheaper)':>14s}")
    for g in GRADES:
        us, uf = OUT[f"U_S_{g}"], OUT[f"U_F_{g}"]
        print(f"{g:11s} {q(us):>20s} {q(uf):>20s} {q(us-uf):>20s} {q(us/uf):>20s} {np.mean(us>uf)*100:13.1f}%")
    print(f"\n{'':11s} {'CtG fluorspar':>20s} {'CtG FSA':>20s} {'ratio':>20s} {'P(FSA lower)':>13s}")
    for g in GRADES:
        es, ef = OUT[f"N_S_{g}"], OUT[f"N_F_{g}"]
        print(f"{g:11s} {q(es):>20s} {q(ef):>20s} {q(es/ef):>20s} {np.mean(ef<es)*100:12.1f}%")

    gap = OUT["U_S_Electronic"] - OUT["U_F_Electronic"]
    AF8 = sum(1/1.08**k for k in range(1, 6))
    print(f"\nCost absorbed at 5 kt/yr over 5 yr: undiscounted {q(gap*25)} M$ · 8 % discount {q(gap*5*AF8)} M$")
    print(f"Months to recover $10 million at 5 kt/yr: {q(10/(gap*5)*12)}")

    def spearman(x, y):
        rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
        return np.corrcoef(rx, ry)[0, 1]
    for label, y in [("electronic-grade cost gap", gap),
                     ("electronic-grade CtG ratio", OUT["N_S_Electronic"]/OUT["N_F_Electronic"])]:
        rho = sorted(((k, spearman(v, y)) for k, v in S.items()), key=lambda t: -abs(t[1]))
        print(f"\nSpearman, {label}: " + " · ".join(f"{k} {r:+.2f}" for k, r in rho[:6]))

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    np.savez(os.path.join(ROOT, "results", "mc_results.npz"), **OUT, **{"in_"+k: v for k, v in S.items()})
    print("\nsaved results/mc_results.npz")
