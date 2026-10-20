#!/usr/bin/env python3
"""Figures: firmware default cranking fuel / priming vs CLT, and default idle target RPM / open-loop position vs CLT.

    .venv/bin/python tools/figures/cranking_idle_defaults.py

Data (rusEFI firmware defaults, copied from source):
  firmware/controllers/algo/defaults/default_cranking.cpp (crankingCoef, crankingBins, crankingCycleBaseFuel 27 mg)
  firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultPriming: primeBins, primeValues)
  firmware/controllers/algo/engine_configuration.cpp (setDefaultIdleSpeedTarget, setDefaultIdleOpenLoopParameters)
Output: documentation/docs/img/plots/cranking-default-fuel.svg, idle-default-target.svg
"""
import pathlib
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
BLUE, ORANGE, GREEN, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})

def style(fig, ax):
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# cranking: base 27 mg x coolant multiplier (TPS multiplier default 1.0)
bins = [-20, -10, 5, 20, 35, 50, 65, 90]
coef = [2.8, 2.2, 1.8, 1.55, 1.3, 1.1, 1.0, 1.0]
crank = [27 * c for c in coef]
pbins = [-40, -20, 0, 20, 40, 60, 80, 100]
prime = [755, 605, 265, 140, 75, 50, 45, 40]
fig, ax = plt.subplots(figsize=(8, 3.6)); style(fig, ax)
ax.plot(bins, crank, color=ORANGE, lw=2, marker="o", label="cranking fuel per cylinder per engine cycle (mg)")
ax.plot(pbins, prime, color=BLUE, lw=2, ls="--", marker="s", label="priming pulse (mg, once at key-on)")
ax.set_yscale("log"); ax.set_xlabel("coolant temperature (°C)"); ax.set_ylabel("fuel mass (mg)")
ax.set_xlim(-45, 105); ax.legend(frameon=False, fontsize=8.5)
fig.tight_layout(); fig.savefig(ROOT / "documentation/docs/img/plots/cranking-default-fuel.svg", transparent=True)

# idle: target RPM and default open-loop position
tb = [-30, -20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
tr = [1350, 1350, 1300, 1200, 1150, 1100, 1050, 1000, 1000, 950, 950, 930, 900, 900, 1000, 1100]
ob = [-40 + i * 180 / 7 for i in range(8)]
ov = [75 - i * 25 / 7 for i in range(8)]
fig, ax = plt.subplots(figsize=(8, 3.6)); style(fig, ax)
ax.plot(tb, tr, color=BLUE, lw=2, marker="o", label="Idle Target RPM from CLT (RPM)")
ax.set_xlabel("coolant temperature (°C)"); ax.set_ylabel("target (RPM)", color=BLUE); ax.set_ylim(0, 1500)
ax2 = ax.twinx(); ax2.patch.set_alpha(0)
ax2.plot(ob, ov, color=ORANGE, lw=2, ls="--", marker="s", label="open-loop idle position (%)")
ax2.axhline(50, color=GREEN, lw=1.5, ls=":", label="cranking idle air (%)")
ax2.set_ylim(0, 100); ax2.set_ylabel("idle position (%)", color=ORANGE)
for s in ("top",): ax2.spines[s].set_visible(False)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8.5, loc="lower left")
fig.tight_layout(); fig.savefig(ROOT / "documentation/docs/img/plots/idle-default-target.svg", transparent=True)
print("wrote 2 plots")
