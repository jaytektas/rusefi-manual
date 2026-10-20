#!/usr/bin/env python3
"""Figure: factory warm-up (CLT) and IAT fuel multipliers against temperature.

    .venv/bin/python tools/figures/fuel_wue_default.py

Data copied from the rusEFI source (no measurement):
  CLT curve  firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultWarmupFuelEnrichment, 16-point branch)
  IAT curve  firmware/controllers/algo/engine_configuration.cpp (initTemperatureCurve(IAT_FUEL_CORRECTION_CURVE, 1))
             firmware/controllers/algo/engine_configuration.h (IAT_FUEL_CORRECTION_CURVE)
Output: documentation/docs/img/plots/fuel-wue-default.svg
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

clt_bins = [-40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
clt_mult = [1.50, 1.50, 1.42, 1.36, 1.28, 1.19, 1.12, 1.10, 1.06, 1.06, 1.03, 1.01, 1, 1, 1, 1]
# initTemperatureCurve: bins -40 + 10*i, values all 1
iat_bins = [-40 + 10 * i for i in range(16)]
iat_mult = [1.0] * 16

fig, ax = plt.subplots(figsize=(7, 3.4))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
ax.plot(clt_bins, clt_mult, color=BLUE, lw=2, marker="o", ms=4, label="Warmup enrichment (CLT)")
ax.plot(iat_bins, iat_mult, color=ORANGE, lw=2, ls="--", label="IAT multiplier")
ax.axhline(1.0, color=GREEN, lw=1, ls=":")
ax.set_xlabel("sensor temperature (deg C)")
ax.set_ylabel("multiplier applied to base fuel")
ax.set_xlim(-45, 115); ax.set_ylim(0.9, 1.6)
ax.legend(frameon=False, fontsize=8.5)
ax.grid(alpha=0.25)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.annotate("1.50x fuel at -40 deg C", xy=(-40, 1.5), xytext=(-6, 1.45),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.annotate("flat 1.00: the IAT multiplier is neutral until you calibrate it",
            xy=(60, 1.0), xytext=(-40, 0.94), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / "fuel-wue-default.svg", transparent=True)
print("wrote", OUT / "fuel-wue-default.svg")
