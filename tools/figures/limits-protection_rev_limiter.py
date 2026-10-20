#!/usr/bin/env python3
"""Figure: the factory-default RPM limiter, drawn from the firmware defaults.

    .venv/bin/python tools/figures/limits-protection_rev_limiter.py

Data (no measured log): firmware/controllers/algo/defaults/default_base_engine.cpp
(rpmHardLimit 7000, rpmHardLimitHyst 50, rpmSoftLimitTimingRetard 4, rpmSoftLimitFuelAdded left at 0,
cutFuelOnHardLimit and cutSparkOnHardLimit both true).

Shape (firmware/controllers/limp_manager.cpp):
  updateRevLimit()      resumeRpm = m_revLimit - rpmHardLimitHyst; the soft zone is
                        interpolateClamped(resumeRpm, 0, m_revLimit, rpmSoftLimitTimingRetard, rpm)
  updateState()         m_revLimitHysteresis.test(rpm, m_revLimit, resumeRpm) — hysteresis.h uses strict
                        comparisons, so the cut turns on only above the limit and off only below resumeRpm
                        (see getLimitingTimingRetard/getLimitingFuelCorrection for the cut-flag gating).
Output: documentation/docs/img/plots/limits-protection-rev-limiter.svg
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]

LIMIT = 7000          # rpmHardLimit
HYST = 50             # rpmHardLimitHyst
RESUME = LIMIT - HYST  # resumeRpm
RETARD = 4            # rpmSoftLimitTimingRetard, degrees

# house palette (STANDARD.md §6): blue = what is asked for, orange = what is driven, red = safety
BLUE, ORANGE, RED, GREY = "#2563eb", "#e8710a", "#c8412d", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

x = list(range(6700, 7201, 10))
# interpolateClamped(RESUME, 0, LIMIT, RETARD, rpm)
retard = [0 if r <= RESUME else (RETARD if r >= LIMIT else RETARD * (r - RESUME) / (LIMIT - RESUME)) for r in x]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True,
                               gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.1})
for ax in (ax1, ax2):
    ax.patch.set_alpha(0)
    ax.axvspan(RESUME, LIMIT, color=GREY, alpha=0.14, lw=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

# top: the soft zone, timing only at the defaults (rpmSoftLimitFuelAdded is 0)
ax1.plot(x, retard, color=ORANGE, lw=2, label="soft-zone timing retard")
ax1.annotate("4° removed at the limit\n(requires Cut spark on RPM limit)", xy=(LIMIT, RETARD),
             xytext=(7005, 1.2), ha="left", fontsize=8.5, color=ORANGE)
ax1.annotate("soft zone\n6950 to 7000 RPM", xy=(RESUME + 8, 1.0), xytext=(6790, 2.3), fontsize=8.5,
             color=RED, arrowprops=dict(arrowstyle="->", color=RED))
ax1.text(6705, 4.95, "Fuel added is 0 % by default (rpmSoftLimitFuelAdded)", fontsize=8.5)
ax1.text(6880, 0.35, "no retard below 6950 RPM", fontsize=8.5)
ax1.set_ylim(-0.5, 5.6)
ax1.set_yticks([0, 1, 2, 3, 4])
ax1.set_ylabel("timing retard (°)")
ax1.legend(loc="lower right", frameon=False, fontsize=8.5)

# bottom: the cut itself, with its on/off gap
ax2.plot([6700, LIMIT, LIMIT, 7200], [0, 0, 1, 1], color=RED, lw=2, label="RPM rising")
ax2.plot([7200, RESUME, RESUME, 6700], [1.08, 1.08, 0.08, 0.08], color=BLUE, lw=2, ls="--",
         label="RPM falling")
ax2.text(RESUME + 25, 0.55, "keeps\nprevious\nstate", ha="center", va="center", fontsize=8.5, color=RED)
ax2.annotate("cut turns on\nabove 7000 RPM", xy=(LIMIT + 2, 1), xytext=(7030, 0.45), fontsize=8.5, color=RED)
ax2.annotate("both return below\n6950 RPM", xy=(RESUME - 2, 0.08), xytext=(6705, 0.42), fontsize=8.5, color=BLUE)
ax2.set_ylim(-0.35, 2.0)
ax2.set_yticks([0.08, 1])
ax2.set_yticklabels(["allowed", "cut"])
ax2.set_xlabel("engine speed (RPM)")
ax2.set_xlim(6700, 7200)
ax2.set_xticks([6700, 6800, 6900, RESUME, LIMIT, 7050, 7100, 7200])
ax2.legend(loc="upper left", frameon=False, fontsize=8.5, ncol=2, bbox_to_anchor=(0, 1.02))

fig.savefig(ROOT / "documentation/docs/img/plots/limits-protection-rev-limiter.svg", transparent=True)
print("wrote", (ROOT / "documentation/docs/img/plots/limits-protection-rev-limiter.svg").relative_to(ROOT))
