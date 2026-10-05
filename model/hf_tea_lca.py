"""
Grade-resolved techno-economic and life-cycle model of hydrogen fluoride (HF)
production from fluorspar and from fluorosilicic acid (FSA).

Companion code for:
  Jeong, W., Kim, J. Fluorspar versus fluorosilicic acid for electronic-grade
  hydrogen fluoride: A grade-resolved techno-economic, life-cycle, and impurity
  assessment. Resources, Conservation and Recycling (submitted).

Scope
-----
Reference site: Korea, 2025 prices. Functional unit: 1 kg HF (100 %).
Grades (representative specifications):
  Technical  = anhydrous HF (AHF), >= 99.98 % (GB/T 7746 class I)
  HighPurity = UP / UP-S grade (solar and display use, 49 % solution),
               one rectification column
  Electronic = semiconductor grade (UPSS / UPSSS), six rectification columns
Both routes produce technical-grade AHF, which then passes through the same
purification train (shared purification).

System boundaries
  GtG ("on-site")   = on-site fuel combustion (scope 1) + combustion share of
                      purchased electricity and steam (scope 2).
  CtG (cradle-to-gate) = GtG + upstream energy supply (LNG liquefaction and
                      transport, upstream fuel for power generation) + upstream
                      raw materials and reagents (fluorspar mining, sulfuric
                      acid, lime) + FSA upstream burden (multifunctional point M1).
  Excluded in both: product transport, packaging, quality control, capital goods.

Source tags in the comments
  [S2]-[S8]  value taken from, or documented in, Supplementary Information
             Tables S2-S8 of the article, where each value is traced to its source
  [DERIVED]  derived from sourced values
  [ASSUME]   assumption, varied in the sensitivity analysis
  [LAB]      economic convention of the research group

Units: costs in $/t HF inside the model and $/kg HF in `totals`; emissions in
kg CO2eq/kg HF.

Run `python model/hf_tea_lca.py` to print the base-case results, the cost and
emission breakdowns, the multifunctionality scenarios, and the one-at-a-time
sensitivity table.
"""
import copy

RATE, LIFE = 0.08, 30
CRF = RATE*(1+RATE)**LIFE/((1+RATE)**LIFE-1)      # capital recovery factor, 0.0888 [LAB]
FIXED_OM = 0.03                                     # maintenance and insurance, 3 % of capital cost per year [LAB]
LAB_OVH = 0.15                                      # labor overhead, 15 % of direct labor [LAB]

P = {
    # ---- Prices (Korea, 2025) [S3] ----
    "p_spar":    470,     # $/t acid-grade fluorspar, CIF [USGS MCS 2026]
    "p_fsa":     190,     # $/t H2SiF6 (100 %), VAT excluded; median ex-works price of four Chinese regions, 12 Feb 2025 (215 incl. VAT / 1.13); range 93-246
    "p_h2so4":   60,      # $/t sulfuric acid 98 %, FOB Busan, 2025 Q3
    "oleum_share": 0.38,  # share of oleum in the sulfuric acid of the fluorspar route [S2: Sanmei EIA, 1.01/2.62]
    "oleum_mult": 1.1,    # price ratio oleum / 98 % acid [DERIVED: 20-65 % oleum = 1.045-1.146 t H2SO4-eq; low 1.0 = BusinessAnalytiq North America 2026; high 2.5 = Expert Market Research China 2025]
    "p_lime":    274,     # $/t Ca(OH)2 [USGS MCS 2026, United States as proxy]
    "p_ng":      16.7,    # $/GJ LHV natural gas (industrial city-gas tariff 21.33 KRW/MJ HHV = 15.0 $/GJ HHV x 1.11)
    "p_steam":   18.8,    # $/GJ steam energy (44 $/t / enthalpy rise 2.34 GJ/t; same basis as ci_steam)
    "p_elec":    0.118,   # $/kWh (KEPCO industrial average sales price 2024, 168.17 KRW/kWh / 1,422 KRW/USD)
    "salary":    58700,   # $/person/yr (manufacturing total labor cost 83.5 million KRW, 2023 / 1,422 KRW/USD) [S4]
    "p_silica":  750,     # $/t precipitated silica [range 500-1,050]; used only in the silica-sale scenario
    # ---- Material and energy inputs per t HF [S2] ----
    "spar_t":    2.14,  "h2so4_spar": 2.6, "lime_spar": 0.03,       # t fluorspar, t H2SO4, t lime
    "ng_spar":   5.0,   "stm_spar":   1.1, "el_spar":   250,        # GJ LHV natural gas (4.0-6.8), GJ steam, kWh (150-556)
    "fsa_t":     1.55,  "h2so4_fsa":  0.0,                          # t FSA (100 %); no net acid use at an integrated site (diluted acid returned)
    "stm_fsa":   12.0,  "el_fsa":     270,                          # GJ steam (12-16), kWh (220-315)
    "silica_t":  0.5,                                                # t dry SiO2 co-produced
    "gypsum_t":  3.65,                                               # t fluorogypsum (resource indicator)
    # ---- Purification increment (AHF purchased and purified; identical for both routes) [S2] ----
    "ahf_in":    1.37,    # t AHF per t electronic-grade HF (Kaisheng)
    "el_ehf":    814, "stm_ehf": 1.655,                              # kWh and GJ steam per t (1.45 GJ on a 2.05 GJ/t latent-heat basis x 2.34/2.05, same basis as p_steam)
    "hp_energy_frac": 0.4,  # energy of high-purity purification relative to electronic grade [DERIVED: one vs six columns, 0.2-0.7]
    "ahf_in_hp": 1.17,      # t AHF per t high-purity HF (yield 85.3 %, Zhongxin Gaobao)
    "p_ind_hf":  1062,    # $/t HF (100 %) industrial-grade HF co-product, VAT excluded [S3: 2025 average AHF price x 0.70 / 7.19 / 1.13; range 788-1,602]
    # ---- Capital cost, $/(t/yr) HF (100 %), 2025 $ (CEPCI 2025 = 812.8) [S4] ----
    "loc_cn_kr": 1.0,      # location factor China -> Korea [DERIVED: Korean anchor 2,234 / median of four Chinese plants 2,315 = 0.965; upper bound 1.84]
    "capex_spar": 2234,   # fluorspar route, Korean anchor (50 kt/yr, 150 billion KRW, 2024, x 1.016)
    "capex_fsa":  2315,   # FSA route, median of four new Chinese plants (2,254-2,466) x loc_cn_kr
    "capex_hp":   1700,   # high-purity purification increment (420-1,300 $/t solution / 0.495 = 848-2,626; midpoint)
    "capex_ehf":  4764,   # electronic-grade purification increment (Kaisheng 2,056 $/t solution / 0.495 = 4,154 in 2021 $ x 812.8/708.8; range 3,416-6,612)
    # ---- Staffing, persons per kt/yr [S4] ----
    "lab_ahf":   1.92,    # AHF plant (96 persons, 50 kt/yr fluorspar AHF plant); same for the FSA route, +/- 25 %
    "lab_ehf":   3.4,     # purification (30 persons / 8.9 kt HF, Kaisheng)
    # ---- Phosphorus removal increment, electronic grade, FSA route (base 0; high case in SENS) [S2] ----
    "p_capex_frac": 0.0, "p_rm_steam": 0.0, "p_rm_elec": 0.0, "p_yield": 0.0,
    # ---- Emission factors (GtG, CtG) [S5] ----
    "ci_elec":   (0.4541, 0.53),     # kg/kWh: GIR 2024 consumption-end / Korean life-cycle factor
    "ci_steam":  (0.0706, 0.0957),   # kg/MJ steam: combustion / + LNG upstream 20.3 g/MJ
    "ci_ng":     (0.0562, 0.0768),   # kg/MJ fuel: IPCC 2006 / + LNG upstream
    "ci_spar":   (0.0, 0.0945),      # kg/kg acid-grade fluorspar (GREET 2023)
    "fsa_alloc": None,               # FSA upstream burden (M1): None = economic allocation linked to p_fsa; scenarios 0 (cut-off) and 1.86 (mass)
    "e_p2o5": 1251, "m_fsa_p2o5": 0.040, "p_p2o5": 1000,   # kg CO2eq/t P2O5 (GREET) · t FSA/t P2O5 (BREF) · $/t P2O5 (900-1,300)
    "ci_h2so4":  (0.0, 0.17),        # kg/kg sulfuric acid 98 % (KEITI; GREET 0.045 = low value)
    "ci_oleum":  (0.0, 0.197),       # kg/kg H2SO4-eq oleum (KEITI 0.206/kg product / 1.045)
    "ci_lime":   (0.0, 0.97),        # kg/kg lime (GREET 2023)
    # ---- Credits and burdens (kg CO2eq/kg HF), 0 in the base case [S6, S7] ----
    "cr_neutral": 0.0,    # avoided neutralization of FSA (lime -2.3; limestone -1.5); marginal FSA only
    "cr_silica":  0.0,    # silica substitution (-0.75 to -1.3); paired with silica revenue in the TEA
    "bd_acid":    0.0,    # reconcentration of diluted acid at a non-integrated site (+2.4 to +3.6)
    "c_acid_reconc": 0.0,  # $/t HF TEA cost of the same scenario [DERIVED lower bound: 28-38 GJ/t x p_steam ~ 530-710; excludes equipment and power]
    "silica_sold": 0,
    # ---- Fluorspar-route co-products [S2, S3, S6] ----
    "gyp_sold":  0.5,     # share of fluorogypsum sold (0.25-0.9)
    "p_gyp":     0.0,     # $/t selling price of fluorogypsum (-5 to +4.2)
    "c_landfill":20.0,    # $/t landfill or stacking of unsold fluorogypsum (3.5-70)
    "ci_gyp_avoid": 0.0,   # 0 = economic allocation (gypsum value 0 $/t). System-expansion scenarios 0.0092-0.065
    "ci_landfill":  0.0057, # kg/kg landfill (KEITI 0.0051-0.0064)
    "fsa_by_t":  0.116, "fsa_by_conc": 0.40,  # t of 40 % FSA solution sold per t HF; priced at p_fsa (100 % basis)
}

GRADES = ["Technical", "HighPurity", "Electronic"]
ROUTES = ["Fluorspar", "FSA"]
B = {"GtG": 0, "CtG": 1}

def fsa_upstream(p):
    """M1: upstream burden allocated to FSA, kg CO2eq/kg HF. If fsa_alloc is None,
    economic allocation between P2O5 and FSA is computed from p_fsa."""
    if p["fsa_alloc"] is not None:
        return p["fsa_alloc"]
    pf = p["p_fsa"]
    return p["e_p2o5"]*pf/(p["p_p2o5"] + p["m_fsa_p2o5"]*pf) * p["fsa_t"]/1000

def fsa_by_rev(p):      # $/t HF, by-product FSA sold by the fluorspar route
    return p["fsa_by_t"]*p["fsa_by_conc"]*p["p_fsa"]

def fsa_by_share(p):    # M5 economic allocation: value share of by-product FSA (HF valued at the industrial-grade price)
    r = fsa_by_rev(p); return r/(r + p["p_ind_hf"])

def validate(p):
    """Scenario combination rules: one method per multifunctional flow."""
    if p["cr_neutral"] < 0 and p["fsa_alloc"] != 0:
        raise ValueError("The avoided-neutralization credit is paired only with the FSA cut-off (fsa_alloc=0)")
    if p["cr_neutral"] < 0 and p["bd_acid"] > 0:
        raise ValueError("Avoided neutralization (integrated site, marginal FSA) and acid reconcentration (non-integrated site) are exclusive")
    if (p["cr_silica"] < 0) != bool(p["silica_sold"]):
        raise ValueError("Silica: the LCA credit and the TEA revenue are switched on and off together")
    if (p["bd_acid"] > 0) != (p["c_acid_reconc"] > 0):
        raise ValueError("Non-integrated site: the LCA burden and the TEA cost are switched on together")

def ahf(route, p, bd):
    """Technical-grade AHF: cost items ($/t HF) and emission items (kg CO2eq/kg HF)."""
    i = B[bd]
    if route == "Fluorspar":
        c = dict(feed=p["spar_t"]*p["p_spar"],
                 reagents=p["h2so4_spar"]*p["p_h2so4"]*(1 + p["oleum_share"]*(p["oleum_mult"]-1)) + p["lime_spar"]*p["p_lime"],
                 fuel=p["ng_spar"]*p["p_ng"], steam=p["stm_spar"]*p["p_steam"], elec=p["el_spar"]*p["p_elec"],
                 capex=p["capex_spar"]*CRF, fixed_om=p["capex_spar"]*FIXED_OM,
                 labor=p["lab_ahf"]*p["salary"]*(1+LAB_OVH)/1000,
                 coproduct=-(p["gypsum_t"]*p["gyp_sold"]*p["p_gyp"] + fsa_by_rev(p)),
                 disposal=p["gypsum_t"]*(1-p["gyp_sold"])*p["c_landfill"])
        e = dict(feed=p["spar_t"]*p["ci_spar"][i],
                 reagents=p["h2so4_spar"]*((1-p["oleum_share"])*p["ci_h2so4"][i] + p["oleum_share"]*p["ci_oleum"][i]) + p["lime_spar"]*p["ci_lime"][i],
                 fuel=p["ng_spar"]*p["ci_ng"][i], steam=p["stm_spar"]*p["ci_steam"][i],
                 elec=p["el_spar"]*p["ci_elec"][i]/1000,
                 disposal=p["gypsum_t"]*(1-p["gyp_sold"])*p["ci_landfill"] if bd == "CtG" else 0.0,
                 credit=-p["gypsum_t"]*p["gyp_sold"]*p["ci_gyp_avoid"] if bd == "CtG" else 0.0)
        if bd == "CtG":                                   # M5: economic allocation to the by-product FSA
            e = {k: v*(1-fsa_by_share(p)) for k, v in e.items()}
    else:
        sold = p["silica_sold"]
        c = dict(feed=p["fsa_t"]*p["p_fsa"],
                 reagents=p["h2so4_fsa"]*p["p_h2so4"],
                 fuel=0.0, steam=p["stm_fsa"]*p["p_steam"], elec=p["el_fsa"]*p["p_elec"],
                 capex=p["capex_fsa"]*CRF, fixed_om=p["capex_fsa"]*FIXED_OM,
                 labor=p["lab_ahf"]*p["salary"]*(1+LAB_OVH)/1000,
                 coproduct=-sold*p["silica_t"]*p["p_silica"], disposal=p["c_acid_reconc"])
        e = dict(feed=fsa_upstream(p) if bd == "CtG" else 0.0,   # M1 allocation
                 reagents=p["h2so4_fsa"]*p["ci_h2so4"][i] + (p["bd_acid"] if bd == "CtG" else 0.0),
                 fuel=0.0, steam=p["stm_fsa"]*p["ci_steam"][i],
                 elec=p["el_fsa"]*p["ci_elec"][i]/1000, disposal=0.0,
                 credit=(p["cr_neutral"] + p["cr_silica"]) if bd == "CtG" else 0.0)
    return c, e      # $/t HF, kg CO2eq/kg HF

def route_grade(route, grade, p=None, bd="CtG"):
    """Cost and emission items of one route at one grade (AHF plus purification increment)."""
    p = p or P
    validate(p)
    c, e = ahf(route, p, bd)
    if grade == "Technical":
        return c, e
    i = B[bd]
    elec_g = grade == "Electronic"
    a_in = p["ahf_in"] if elec_g else p["ahf_in_hp"]
    net_ahf = a_in                                       # cost: all AHF input is charged; the industrial-grade HF leaving purification is credited at its market price
    frac = 1.0 if elec_g else p["hp_energy_frac"]
    capex_inc = (p["capex_ehf"] if elec_g else p["capex_hp"]) * p["loc_cn_kr"]
    st, el = p["stm_ehf"]*frac, p["el_ehf"]*frac
    yl, xst, xel = 1.0, 0.0, 0.0
    if route == "FSA" and elec_g:
        capex_inc *= 1 + p["p_capex_frac"]; xst, xel = p["p_rm_steam"], p["p_rm_elec"]; yl = 1 - p["p_yield"]
    cc = dict(ahf_feed=sum(c.values())*net_ahf,
              steam=st*p["p_steam"], elec=el*p["p_elec"],
              p_removal=xst*p["p_steam"] + xel*p["p_elec"],
              capex=capex_inc*CRF, fixed_om=capex_inc*FIXED_OM,
              labor=p["lab_ehf"]*p["salary"]*(1+LAB_OVH)/1000,
              byprod_hf=-(a_in-1)*p["p_ind_hf"])
    ee = dict(ahf_feed=sum(e.values())*1.0,              # emissions: mass allocation between the product and the industrial-grade HF
              steam=st*p["ci_steam"][i], elec=el*p["ci_elec"][i]/1000,
              p_removal=xst*p["ci_steam"][i] + xel*p["ci_elec"][i]/1000)
    return {k: v/yl for k, v in cc.items()}, {k: v/yl for k, v in ee.items()}

def totals(route, grade, p=None, bd="CtG"):
    """Unit production cost ($/kg HF) and GHG emissions (kg CO2eq/kg HF)."""
    c, e = route_grade(route, grade, p, bd)
    return sum(c.values())/1000, sum(e.values())

def flat_breakdown(route, grade, p=None, bd="CtG"):
    """Cost and emission items with the AHF feed split into its own items (used for the stacked bars)."""
    p = p or P
    c, e = route_grade(route, grade, p, bd)
    if grade == "Technical":
        return c, e
    c0, e0 = ahf(route, p, bd)
    tc, te = sum(c0.values()), sum(e0.values())
    fc = {("AHF:"+k): v*c["ahf_feed"]/tc for k, v in c0.items()}
    fe = {("AHF:"+k): (v*e["ahf_feed"]/te if te else 0.0) for k, v in e0.items()}
    fc.update({("purif:"+k): v for k, v in c.items() if k != "ahf_feed"})
    fe.update({("purif:"+k): v for k, v in e.items() if k != "ahf_feed"})
    return fc, fe

def with_(**kw):
    """Copy of the base parameters with the given values replaced."""
    p = copy.deepcopy(P); p.update(kw); return p

# One-at-a-time sensitivity (label, low-value changes, high-value changes); ranges in SI Tables S2-S5.
# The labels are those used in Fig. 4a; the figure shows the 12 inputs with the largest effect on the
# electronic-grade cost gap.
SENS = [
    ("Electricity price",              dict(p_elec=0.108), dict(p_elec=0.128)),   # KEPCO industrial 2023 153.71 / 2025 181.9 KRW/kWh / 1,422
    ("Natural gas price",              dict(p_ng=12.9*1.11), dict(p_ng=18.2*1.11)),   # 14.3 / 20.2 $/GJ LHV
    ("Steam price",                    dict(p_steam=30/2.34), dict(p_steam=55/2.34)), # 12.8 / 23.5 $/GJ
    ("Sulfuric acid price",            dict(p_h2so4=32), dict(p_h2so4=125)),
    ("FSA price",                      dict(p_fsa=93), dict(p_fsa=246)),          # the M1 allocation follows p_fsa
    ("Fluorspar price",                dict(p_spar=405), dict(p_spar=504)),
    ("AHF plant staffing",             dict(lab_ahf=1.44), dict(lab_ahf=2.40)),   # +/- 25 %
    ("Kiln fuel",                      dict(ng_spar=4.0), dict(ng_spar=6.8)),
    ("Fluorspar-route electricity",    dict(el_spar=150), dict(el_spar=556)),
    ("FSA-route steam",                {}, dict(stm_fsa=16)),
    ("FSA-route electricity",          dict(el_fsa=220), dict(el_fsa=315)),
    ("FSA-route capital cost",         dict(capex_fsa=2254), dict(capex_fsa=2466)),
    ("Fluorspar-route capital cost",   dict(capex_spar=1388), dict(capex_spar=2355)),
    ("Location factor",                dict(loc_cn_kr=0.965, capex_fsa=2315*0.965), dict(loc_cn_kr=1.84, capex_fsa=2315*1.84)),
    ("Purification capital cost",      dict(capex_ehf=3416), dict(capex_ehf=6612)),
    ("Purification AHF input",         dict(ahf_in=1/0.88), {}),                  # electronic-grade yield 88 % / 73 %
    ("Industrial-grade HF price",      dict(p_ind_hf=788), dict(p_ind_hf=1602)),
    ("Labor cost",                     dict(salary=20800), dict(salary=64000)),   # 20.8 k$ (China) / 64 k$
    ("Oleum price ratio",              dict(oleum_mult=1.0), dict(oleum_mult=2.5)),
    ("Gypsum landfill cost",           dict(c_landfill=3.5), dict(c_landfill=70)),
    ("Phosphate value",                dict(p_p2o5=1300), dict(p_p2o5=900)),
    ("Phosphorus removal increment",   {}, dict(p_capex_frac=0.05, p_rm_steam=0.25, p_rm_elec=15, p_yield=0.03)),
    ("Sulfuric acid emission factor",  dict(ci_h2so4=(0, 0.045), ci_oleum=(0, 0.045*0.197/0.17)), {}),   # oleum factor scaled with it
    ("Electricity emission factor",    dict(ci_elec=(0.4541, 0.495)), {}),        # CtG 0.495 / 0.53
    ("Capacity utilization",           {}, dict(capex_spar=2234/0.85, capex_fsa=2315/0.85, capex_ehf=4764/0.85, capex_hp=1700/0.85, lab_ahf=1.92/0.85, lab_ehf=3.4/0.85)),  # 85 %: capital and labor / 0.85
]

if __name__ == "__main__":
    cols = [(r, g) for r in ROUTES for g in GRADES]
    print(f"CRF {CRF:.4f} · fixed O&M 3 % · labor overhead 15 % · Korean 2025 prices\n")
    print("="*96); print(" Results: UPC $/kg · GHG kg CO2eq/kg (on-site GtG / cradle-to-gate CtG); base case: M1 economic allocation linked to p_fsa, gypsum value 0, integrated site, silica returned"); print("="*96)
    for g in GRADES:
        us, _ = totals("Fluorspar", g); uf, _ = totals("FSA", g)
        n = {(r, b): totals(r, g, bd=b)[1] for r in ROUTES for b in B}
        print(f" {g:11s} UPC {us:4.2f}/{uf:4.2f} ({us/uf:4.2f}x, {us-uf:+.2f})"
              f" | GtG {n['Fluorspar','GtG']:4.2f}/{n['FSA','GtG']:4.2f} ({n['Fluorspar','GtG']/n['FSA','GtG']:4.2f}x)"
              f" | CtG {n['Fluorspar','CtG']:4.2f}/{n['FSA','CtG']:4.2f} ({n['Fluorspar','CtG']/n['FSA','CtG']:4.2f}x)")

    def table(title, idx, scale, bd="CtG"):
        data = {col: flat_breakdown(*col, bd=bd)[idx] for col in cols}
        keys = []
        for d in data.values():
            keys += [k for k in d if k not in keys]
        print("\n" + "="*96); print(" " + title); print("="*96)
        print(f" {'':20s}" + "".join(f"{(r[:4]+'-'+g[:4]):>12s}" for r, g in cols))
        for k in keys:
            vals = [data[col].get(k, 0.0)/scale for col in cols]
            if all(abs(v) < 5e-4 for v in vals) and not k.endswith(("credit", "coproduct")): continue
            print(f" {k:20s}" + "".join(f"{v:12.3f}" for v in vals))
        print(f" {'TOTAL':20s}" + "".join(f"{sum(data[col].values())/scale:12.3f}" for col in cols))
    table("UPC breakdown ($/kg HF)", 0, 1000)
    table("GHG breakdown, on-site GtG (kg CO2eq/kg HF)", 1, 1, "GtG")
    table("GHG breakdown, cradle-to-gate CtG (kg CO2eq/kg HF, base case)", 1, 1, "CtG")

    print("\n" + "="*96); print(" Multifunctionality and site scenarios (CtG, fluorspar/FSA, ratio, UPC gap)"); print("="*96)
    CRED = [
        ("Base (M1 economic, p_fsa-linked)",           {}),
        ("M1 cut-off",                                 dict(fsa_alloc=0.0)),
        ("M1 mass allocation 1.86 (upper reference)",  dict(fsa_alloc=1.86)),
        ("Marginal FSA: cut-off + limestone -1.5",     dict(cr_neutral=-1.5, fsa_alloc=0.0)),
        ("Marginal FSA: cut-off + lime -2.3",          dict(cr_neutral=-2.3, fsa_alloc=0.0)),
        ("M2 silica sold -0.75 (+TEA revenue)",        dict(cr_silica=-0.75, silica_sold=1)),
        ("M2 silica sold -1.3 (+TEA revenue)",         dict(cr_silica=-1.3, silica_sold=1)),
        ("M3 non-integrated site +2.4 / 500 $/t",      dict(bd_acid=2.4, c_acid_reconc=500)),
        ("M3 non-integrated site +3.6 / 700 $/t",      dict(bd_acid=3.6, c_acid_reconc=700)),
        ("M4 gypsum 50 % substitution 0.0092",         dict(ci_gyp_avoid=0.0092)),
        ("M4 gypsum 90 % sold, substitution 0.065",    dict(gyp_sold=0.9, ci_gyp_avoid=0.065)),
        ("M4 gypsum 25 % sold",                        dict(gyp_sold=0.25)),
        ("Most favorable to FSA: lime -2.3 + silica -1.3", dict(cr_neutral=-2.3, fsa_alloc=0.0, cr_silica=-1.3, silica_sold=1)),
    ]
    for name, kw in CRED:
        p = with_(**kw); out = []
        for g in GRADES:
            (us, es), (uf, ef) = totals("Fluorspar", g, p), totals("FSA", g, p)
            out.append(f"{g[:4]} {es:4.2f}/{ef:5.2f} ({es/ef:5.2f}x) U{us-uf:+.2f}")
        print(f" {name:30s} " + " | ".join(out))

    print("\n" + "="*96); print(" One-at-a-time sensitivity, electronic grade (UPC ratio and gap, CtG ratio): low || high"); print("="*96)
    for name, lo, hi in SENS:
        out = []
        for kw in (lo, hi):
            p = with_(**kw)
            (us, es), (uf, ef) = totals("Fluorspar", "Electronic", p), totals("FSA", "Electronic", p)
            out.append(f"U {us/uf:4.2f}({us-uf:+.2f}) N {es/ef:4.2f}")
        print(f" {name:30s} " + "  ||  ".join(out))

    print("\n Resource indicators per kg HF: fluorspar route = 2.14 kg acid-grade fluorspar mined, 3.65 kg fluorogypsum / FSA route = 0, 0")
