#!/usr/bin/env python3
"""Figure: ETB auto-calibration seen in a TunerStudio datalog (both TPS tracks against time).

    .venv/bin/python tools/figures/etb_autocal.py

Input:  tools/figures/data/etb-autocal.csv — Time and both raw TPS voltages, extracted with
        `tools/mlg.py csv <log> Time rawTps1Primary rawTps1Secondary` from a TunerStudio log of
        "Auto Calibrate ETB 1" on the bench (Bosch 82 mm throttle, 12 V on), recorded 2026-10-20.
Output: documentation/docs/img/plots/etb-autocal.svg
"""
import pathlib
import sys

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
import csv  # noqa: E402

rows = list(csv.DictReader(open(ROOT / "tools/figures/data/etb-autocal.csv")))
t = [float(r["Time"]) for r in rows]
pri = [float(r["rawTps1Primary"]) for r in rows]
sec = [float(r["rawTps1Secondary"]) for r in rows]

# the sweep: first sample where the primary leaves the idle position, then 3.5 s around it
start = next(i for i, v in enumerate(pri) if v < pri[0] - 0.3)
t0 = t[start] - 0.4
sel = [i for i in range(len(t)) if t0 <= t[i] <= t0 + 3.6]
x = [t[i] - t0 for i in sel]

# house palette (STANDARD.md §6): blue = what is asked for, orange = what is driven, green = closed loop
BLUE, ORANGE, GREEN, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})
fig, ax = plt.subplots(figsize=(8, 3.6))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# phases, from the code: open for 1000 ms, closed for 1000 ms, then the motor is released
t_open = t[start] - t0
phases = [(0, t_open, "holding idle target", GREEN), (t_open, t_open + 1.0, "driven open (+50 %)", ORANGE),
          (t_open + 1.0, t_open + 2.0, "driven closed (−50 %)", ORANGE), (t_open + 2.0, 3.6, "released: spring rest", GREY)]
for a, b, label, c in phases:
    ax.axvspan(a, b, color=c, alpha=0.08, lw=0)
    ax.text((a + b) / 2, 5.15, label, ha="center", va="bottom", fontsize=8.5)

ax.plot(x, [pri[i] for i in sel], color=BLUE, lw=2, label="TPS 1 primary (raw V)")
ax.plot(x, [sec[i] for i in sel], color=BLUE, lw=2, ls="--", label="TPS 1 secondary (raw V)")
ax.annotate("open recorded\n0.29 V / 4.69 V", xy=(t_open + 0.98, 0.29), xytext=(t_open + 0.35, 1.2),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.annotate("closed recorded\n4.48 V / 0.50 V", xy=(t_open + 1.98, 4.48), xytext=(t_open + 1.25, 2.9),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.set_xlim(0, 3.6)
ax.set_ylim(0, 5.6)
ax.set_xlabel("time (s)")
ax.set_ylabel("sensor voltage (V)")
ax.legend(loc=(0.70, 0.38), frameon=False, fontsize=8.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
out = ROOT / "documentation/docs/img/plots/etb-autocal.svg"
fig.savefig(out, transparent=True)
print("wrote", out.relative_to(ROOT))
