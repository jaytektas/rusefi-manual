#!/usr/bin/env python3
"""Figure: the firmware's default TPS-to-TPS acceleration-enrichment table as curves.

    .venv/bin/python tools/figures/tuning_fuel_ae_table.py

Data copied from the rusEFI source (no measurement):
  table values  firmware/controllers/algo/defaults/default_fuel.cpp (tpsTpsTable, setMazdaMiataNbTpsTps)
  table bins    same function: setLinearCurve(tpsTpsAccelFromRpmBins / tpsTpsAccelToRpmBins, 0, 100, 10)
                -> 0, 10, 30, 40, 60, 70, 90, 100 per cent throttle
  RPM curve     firmware/controllers/algo/defaults/default_fuel.cpp (setLinearCurve(tpsTspCorrValues, 1, 1))
Output: documentation/docs/img/plots/tuning-fuel-ae-default.svg

Row index of tpsTpsTable is the TPS the step ENDED at, column index the TPS it STARTED at
(interpolate3d in firmware/controllers/algo/accel_enrichment.cpp is called with
tpsTpsAccelToRpmBins/tpsTo first).
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/docs/img/plots"
BLUE, ORANGE, GREEN, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

# setLinearCurve(bins, 0, 100, precision 10) over 8 points
bins = [0, 10, 30, 40, 60, 70, 90, 100]

# tpsTpsTable in default_fuel.cpp, rows indexed by the ending TPS, columns by the starting TPS
ae = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [10, 0, 0, 0, 0, 0, 0, 0],
    [17, 10, 0, 0, 0, 0, 0, 0],
    [23, 17, 10, 0, 0, 0, 0, 0],
    [28, 23, 17, 10, 0, 0, 0, 0],
    [32, 28, 23, 17, 10, 0, 0, 0],
    [35, 32, 28, 23, 17, 10, 0, 0],
    [37, 35, 32, 28, 23, 17, 10, 0],
]

fig, ax = plt.subplots(figsize=(7.4, 3.8))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
for start_tps, start_col, colour, style in [(0, 0, BLUE, "-"), (40, 3, ORANGE, "--"), (70, 5, GREEN, ":")]:
    ax.plot(bins, [row[start_col] for row in ae], color=colour, lw=2, ls=style, marker="o", ms=4,
            label=f"step starting at {start_tps} % TPS")
ax.set_xlabel("throttle position the step ends at (% TPS)")
ax.set_ylabel("extra injection (ms, MS Adder mode)")
ax.set_xlim(-3, 103); ax.set_ylim(-1, 42)
ax.grid(alpha=0.25)
ax.legend(frameon=False, fontsize=8.5)
ax.annotate("0 -> 100 % step: 37 ms on top of the computed pulse",
            xy=(100, 37), xytext=(34, 39.2),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.annotate("a step that ends below where it started adds nothing",
            xy=(10, 0), xytext=(26, 5.5),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "tuning-fuel-ae-default.svg", transparent=True)
print("wrote", OUT / "tuning-fuel-ae-default.svg")
