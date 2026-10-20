#!/usr/bin/env python3
"""Figure: the factory Target lambda / Target AFR table against load.

    .venv/bin/python tools/figures/fuel_target_lambda.py

Data copied from the rusEFI source (no measurement):
  load axis    firmware/controllers/algo/defaults/engine_configuration_defaults.h (DEFAULT_LAMBDA_LOAD_BINS)
  lambda row   same file (DEFAULT_LAMBDA_TABLE_ROW) - every RPM row is identical
  stoich       firmware/controllers/algo/rusefi_types.h (STOICH_RATIO)
  axis setup   firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultLambdaTable)
The right-hand AFR scale is the same curve multiplied by the 14.7 stoichiometric ratio, so both
scales describe one line (fuel_computer.cpp: afr = stoich * lambda).
Output: documentation/docs/img/plots/fuel-target-lambda-default.svg
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/docs/img/plots"
BLUE, GREEN, GREY = "#2563eb", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

load = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 150, 175, 200, 225, 250]
lam = [1, 1, 1, 1, 1, 0.95, 0.92, 0.90, 0.89, 0.88, 0.86, 0.84, 0.8, 0.77, 0.75, 0.73]
stoich = 14.7
lo, hi = 0.68, 1.06

fig, ax = plt.subplots(figsize=(7, 3.4))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
ax.plot(load, lam, color=BLUE, lw=2, marker="o", ms=4)
ax.axhline(1.0, color=GREEN, lw=1, ls=":")
ax2 = ax.twinx()
ax2.set_ylim(lo * stoich, hi * stoich)
ax2.set_yticks([10, 11, 12, 13, 14, 15])
ax2.set_ylabel("same curve as target AFR at E0 (stoichiometric 14.7)", color=BLUE)
ax2.tick_params(axis="y", colors=BLUE)
ax.set_ylim(lo, hi)
ax.set_xlim(20, 260)
ax.set_xlabel("table load axis (kPa of MAP with the default Speed Density load)")
ax.set_ylabel("target lambda")
ax.grid(alpha=0.25)
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
ax.annotate("stoichiometric: lambda 1.00 = 14.7:1", xy=(34, 1.0), xytext=(48, 0.8),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.annotate("factory table is one flat row: the same target at every engine speed",
            xy=(175, 0.77), xytext=(40, 0.71), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / "fuel-target-lambda-default.svg", transparent=True)
print("wrote", OUT / "fuel-target-lambda-default.svg")
