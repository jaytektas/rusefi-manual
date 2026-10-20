#!/usr/bin/env python3
"""Figures: firmware default injector dead-time curve and default VE table.

    .venv/bin/python tools/figures/fuel_defaults.py

Data copied from the rusEFI source (no measurement):
  dead time  firmware/controllers/algo/engine_configuration_defaults.h (INJECTOR_BATT_LAG_CURR)
             firmware/controllers/algo/defaults/default_fuel.cpp (setBosch02880155868: vBattBins, pressureBins)
  VE table   firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultVETable: hardCodedveTable)
  VE axes    firmware/controllers/algo/engine_configuration.cpp (setFuelTablesLoadBin 10..160 kPa);
             firmware/util/containers/table_helper.h (setRpmBin 800..7000)
Output: documentation/docs/img/plots/fuel-deadtime-default.svg, fuel-ve-default.svg
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/docs/img/plots"
BLUE, ORANGE, GREEN, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})

# ---- dead time -------------------------------------------------------------
vbatt = [6.0, 8.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
press = [206.843, 413.685]
lag = [[4.240, 2.483, 1.739, 1.501, 1.308, 1.149, 0.964, 0.913],
       [3.084, 1.641, 1.149, 1.194, 0.992, 0.759, 0.637, 0.603]]
ref = 300.0  # fuelReferencePressure default; used for the lookup when no fuel pressure sensor is set
f = (ref - press[0]) / (press[1] - press[0])
lag_ref = [a + (b - a) * f for a, b in zip(*lag)]

fig, ax = plt.subplots(figsize=(7, 3.6))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
ax.plot(vbatt, lag[0], color=BLUE, lw=2, marker="o", label="row 1: 206.8 kPa (30 psi)")
ax.plot(vbatt, lag[1], color=BLUE, lw=2, ls="--", marker="o", label="row 2: 413.7 kPa (60 psi)")
ax.plot(vbatt, lag_ref, color=ORANGE, lw=2, label="used at 300 kPa (default reference)")
ax.annotate(f"{lag_ref[6]:.2f} ms at 14 V", xy=(14, lag_ref[6]), xytext=(11.6, 2.2),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.set_xlabel("battery voltage (V)"); ax.set_ylabel("dead time (ms)")
ax.set_xlim(5.5, 15.5); ax.set_ylim(0, 4.6)
ax.legend(frameon=False, fontsize=8.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "fuel-deadtime-default.svg", transparent=True)

# ---- VE table --------------------------------------------------------------
ve = [
[49.3,49.3,49.4,49.6,50.2,51.4,52.6,53.8,54.4,54.6,54.4,53.7,52.8,51.8,50.9,50.0],
[49.6,50.5,51.5,54.1,57.5,60.7,62.9,64.4,65.0,65.0,64.5,63.5,62.3,61.1,60.0,58.8],
[50.3,52.4,54.3,58.5,62.7,66.1,68.2,69.7,70.2,70.1,69.5,68.4,67.1,65.8,64.5,63.3],
[51.4,55.2,58.2,63.5,68.0,71.4,73.5,74.9,75.3,75.2,74.5,73.3,71.8,70.4,69.0,67.7],
[54.3,60.9,64.9,70.7,75.1,78.3,80.3,81.7,82.1,81.9,81.1,79.7,78.1,76.5,75.0,73.5],
[56.4,64.4,68.7,74.5,78.7,81.8,83.8,85.1,85.5,85.3,84.4,83.0,81.3,79.6,78.0,76.4],
[60.7,70.2,74.5,79.9,83.8,86.8,88.9,90.2,90.6,90.3,89.4,87.8,86.0,84.2,82.5,80.8],
[65.8,76.0,80.0,85.0,88.8,91.8,93.9,95.2,95.6,95.3,94.3,92.6,90.7,88.8,87.0,85.2],
[69.4,79.1,82.9,87.8,91.7,94.8,97.0,98.3,98.8,98.4,97.4,95.6,93.5,91.5,89.6,87.7],
[73.0,82.2,85.9,90.7,94.6,97.8,100.0,101.5,101.9,101.6,100.4,98.5,96.4,94.2,92.2,90.2],
[76.6,85.3,88.8,93.5,97.4,100.7,103.1,104.6,105.1,104.7,103.5,101.5,99.2,96.9,94.8,92.6],
[80.3,88.5,91.8,96.4,100.3,103.7,106.2,107.8,108.2,107.8,106.5,104.4,102.0,99.7,97.4,95.1],
[83.9,91.6,94.7,99.2,103.2,106.7,109.2,110.9,111.4,110.9,109.6,107.4,104.8,102.4,99.9,97.6],
[87.5,94.7,97.6,102.0,106.1,109.7,112.3,114.0,114.5,114.1,112.6,110.3,107.7,105.1,102.5,100.1],
[91.1,97.8,100.6,104.9,108.9,112.6,115.3,117.2,117.7,117.2,115.7,113.3,110.5,107.8,105.1,102.5],
[94.7,100.9,103.5,107.7,111.8,115.6,118.4,120.3,120.8,120.3,118.7,116.2,113.3,110.5,107.7,105.0],
]
load = [10 + 10 * i for i in range(16)]  # setFuelTablesLoadBin(10, 160)
step = int(round((7000 - 800) / 14 / 50) * 50 - 150)  # setRpmBin
rpm = [650] + [800 + step * i for i in range(14)] + [7000]

fig, ax = plt.subplots(figsize=(8, 4.6))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
im = ax.imshow(ve, origin="lower", cmap="viridis", aspect="auto")
ax.set_xticks(range(16)); ax.set_xticklabels(rpm, rotation=60, fontsize=7.5)
ax.set_yticks(range(16)); ax.set_yticklabels(load, fontsize=7.5)
ax.set_xlabel("engine speed (RPM) — table column"); ax.set_ylabel("MAP (kPa) — table row")
for r in range(16):
    for c in range(16):
        ax.text(c, r, f"{ve[r][c]:.0f}", ha="center", va="center", fontsize=6,
                color="white" if ve[r][c] < 85 else "black")
cb = fig.colorbar(im, ax=ax); cb.set_label("VE (%)")
fig.tight_layout()
fig.savefig(OUT / "fuel-ve-default.svg", transparent=True)
print("rpm axis", rpm)
