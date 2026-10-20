#!/usr/bin/env python3
"""Figure: the sampling grid inside a real TunerStudio datalog, and a gap in it.

    .venv/bin/python tools/figures/datalogging_log_grid.py

Input:  tools/figures/data/datalogging-log-times.csv — the Time and Uptime columns plus the
        "Trigger Error Counter" channel, extracted from a TunerStudio .mlg log with
        `tools/mlg.py csv <log> Time Uptime "Trigger Error Counter"`.
        The log is a 25 s bench session (Proteus F7, 12 V, engine stopped, ETB auto-calibration),
        recorded 2026-10-20 — the same session as the Electronic throttle chapter's
        auto-calibration figure.
Output: documentation/docs/img/plots/datalogging-log-grid.svg
"""
import csv
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]

rows = list(csv.DictReader(open(ROOT / "tools/figures/data/datalogging-log-times.csv")))
t = np.array([float(r["Time"]) for r in rows])
gap = np.diff(t)
gap[gap < 0] = 0                       # the Time column is millisecond-rounded; a few rows repeat
i = int(np.argmax(gap))                # the one real gap

# house palette (STANDARD.md §6): blue = what is asked for, orange = what is driven
BLUE, ORANGE, GREY = "#2563eb", "#e8710a", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.2))
fig.patch.set_alpha(0)
for ax in (ax1, ax2):
    ax.patch.set_alpha(0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# left: how the rows are spaced, excluding the one gap
positive = gap[(gap > 0) & (gap < 0.035)]
counts, edges = np.histogram(positive, bins=np.arange(0.001, 0.036, 0.001))
ax1.bar(edges[:-1], counts, width=0.001, color=BLUE)
ax1.set_yscale("log")
ax1.set_xlim(0, 0.035)
ax1.set_ylim(0.6, 3e4)
ax1.set_xlabel("interval between rows (s)")
ax1.set_ylabel("rows")
ax1.text(0.02, 0.99, f"{(len(gap) - 1) / (t[-1] - t[0]):.0f} rows per second, "
                     f"median interval {np.median(gap):.3f} s",
         transform=ax1.transAxes, ha="left", va="top", fontsize=8.5)
ax1.text(0.02, 0.92, f"the {gap[i]:.2f} s gap is off the right-hand end of this axis",
         transform=ax1.transAxes, ha="left", va="top", fontsize=8.5)

# right: row number against log time, zoomed on the gap — missing rows are a flat step
sel = (t > t[i] - 0.6) & (t < t[i] + gap[i] + 0.6)
idx = np.arange(len(t))
ax2.plot(t[sel], idx[sel], color=ORANGE, lw=2)
ax2.axvspan(t[i], t[i + 1], color=ORANGE, alpha=0.12, lw=0)
ax2.set_xlim(t[i] - 0.6, t[i] + gap[i] + 0.6)
ax2.set_ylim(idx[sel].min() - 5, idx[sel].max() + 12)
ax2.set_xlabel("log time (s)")
ax2.set_ylabel("row number")
ax2.annotate("nothing recorded\nfor 0.87 s", xy=(t[i] + gap[i] / 2, idx[sel].max() + 4),
             ha="center", va="top", fontsize=8.5)

fig.tight_layout()
out = ROOT / "documentation/docs/img/plots/datalogging-log-grid.svg"
fig.savefig(out, transparent=True)
print("wrote", out.relative_to(ROOT))
print(f"rows {len(t)}, span {t[-1] - t[0]:.1f} s, median interval {np.median(gap):.3f} s, "
      f"biggest gap {gap[i]:.2f} s at t={t[i]:.2f} s, rows sharing a timestamp "
      f"{int((gap == 0).sum())}")
