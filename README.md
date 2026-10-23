# Fluorosilicic acid as an alternative to fluorspar for electronic-grade hydrogen fluoride production

Process model, input tables, and figure scripts for

> Jeong, W., Kim, J. Fluorosilicic acid as an alternative to fluorspar for electronic-grade hydrogen fluoride production: A grade-resolved techno-economic and life cycle assessment. *Resources, Conservation and Recycling* (submitted).

The model compares hydrogen fluoride (HF) made from mined fluorspar with HF made from fluorosilicic acid (FSA), a by-product of phosphate processing. It covers three purity grades (technical, high-purity, electronic) at a Korean reference site with 2025 prices. For each route and grade it reports the unit production cost and the greenhouse gas emissions, on-site and cradle-to-gate. The functional unit is 1 kg of HF (100 %).

## Contents

| Path | Content |
|---|---|
| `model/hf_tea_lca.py` | Techno-economic and life cycle model: parameters `P`, cost and emission items by route and grade, multifunctionality scenarios, one-at-a-time sensitivity list `SENS` |
| `model/monte_carlo.py` | Monte Carlo analysis (triangular distributions, N = 5,000, seed 20260929) |
| `results/mc_results.npz` | Monte Carlo output read by the figure scripts (regenerated exactly by `model/monte_carlo.py`) |
| `inputs/parameters.csv` | Every model input with its base value, Monte Carlo range, unit, and the Supplementary Information table that gives its source |
| `data/usgs_mcs2026_production_2025.csv` | Fluorspar and phosphate rock production by country, 2025 estimates (USGS Mineral Commodity Summaries 2026) |
| `data/figure_source_data.xlsx` | Plotted values of every figure, one sheet per figure, and all 5,000 Monte Carlo draws with their sampled inputs (built by `figures/build_source_data.py`) |
| `data/source_dossier.xlsx` | Non-English and web sources behind the input values, with the original wording, an English translation, and the capital-cost anchors |
| `figures/` | Scripts that draw Figs. 2–4, Fig. A.1, and Fig. S1 |

## Requirements

Python 3.10 or later with `numpy`, `matplotlib`, and `openpyxl` (tested with Python 3.14, numpy 2.4, matplotlib 3.10, openpyxl 3.1). The figure scripts use the Arial font; matplotlib falls back to its default font if Arial is not installed.

```
pip install -r requirements.txt
```

## Reproducing the results

Run from the repository root.

```
python model/hf_tea_lca.py          # base case, cost and emission breakdowns, scenarios, sensitivity
python model/monte_carlo.py         # Monte Carlo; writes results/mc_results.npz
python figures/fig2_cost_ghg.py
python figures/fig3_resource.py
python figures/fig4_sensitivity_qualification.py
python figures/figA1_price_supply.py
python figures/figS1_system_boundary.py
python figures/build_source_data.py   # rebuilds data/figure_source_data.xlsx
```

Figures are written to `output/` as PNG (500 dpi) and SVG.

| Figure in the article | Script | Output |
|---|---|---|
| Fig. 1 | schematic drawn by the authors, no model values | – |
| Fig. 2a, 2b | `figures/fig2_cost_ghg.py` | `Fig2a_cost`, `Fig2b_ghg` |
| Fig. 3 | `figures/fig3_resource.py` | `Fig3_resource` |
| Fig. 4 | `figures/fig4_sensitivity_qualification.py` | `Fig4_sensitivity_qualification` |
| Fig. A.1 | `figures/figA1_price_supply.py` | `FigA1_price_supply` |
| Fig. A.2 | values in `data/figure_source_data.xlsx`, sheet `FigA.2` | – |
| Fig. S1 | `figures/figS1_system_boundary.py` | `FigS1_system_boundary` |

The published figures were assembled and lettered in PowerPoint from these outputs; the plotted values are identical.

## Base-case results (electronic grade)

| | Fluorspar route | FSA route |
|---|---|---|
| Unit production cost ($/kg HF) | 2.92 | 1.90 |
| Cradle-to-gate emissions (kgCO2eq/kg HF) | 1.91 | 2.48 |

## Model conventions

- Capital cost is annualized with a capital recovery factor at 8 % over 30 years; fixed operating cost is 3 % of capital per year; labor overhead is 15 %.
- The FSA upstream burden is allocated economically between phosphoric acid and FSA and follows the FSA price. Cut-off and mass allocation, avoided neutralization of marginal FSA, silica sale, and a non-integrated site are run as scenarios (`CRED` in `model/hf_tea_lca.py`), with the combination rules enforced by `validate`.
- Source tags in the code comments refer to Supplementary Information Tables S2–S8 of the article, where each value is traced to its source.

## Versions

- v1.2: version revised after co-author review. Article retitled and author affiliations updated; Supplementary Information sections renumbered (Section S14 for the supply and demand ranges in Fig. 3c); Fig. S2 moved to Appendix Fig. A.2 (sheet `FigA.2`); Fig. 3c redrawn on the AHF basis (1.39 t AHF per t electronic-grade HF) and Fig. 4 re-laid out with the input values in the tornado labels; units written as kgCO2eq; source dossier cites the 2025 fluorspar review and records the co-product basis of the Kaisheng report. Model inputs and results are unchanged from v1.1.
- v1.1: corrected the GREET phosphoric acid factor to a metric-tonne basis (1,379 kgCO2eq/t P2O5), put the FSA-route steam on the same enthalpy basis as the steam price (14 GJ/t HF), set the electronic-grade AHF input to the disclosed design ratio (1.39), and aligned several input ranges with their sources; added the source dossier.
- v1.0: version submitted with the manuscript.

## License

Code: MIT License (`LICENSE`). Data and tables in `inputs/`, `data/`, and `results/`: Creative Commons Attribution 4.0 International (CC BY 4.0).

## Contact

Jiyong Kim, School of Chemical Engineering, Sungkyunkwan University, Republic of Korea.
