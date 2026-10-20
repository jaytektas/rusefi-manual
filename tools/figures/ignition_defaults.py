#!/usr/bin/env python3
"""Figures: rusEFI's factory ignition defaults, computed exactly as the firmware computes them.

    .venv/bin/python tools/figures/ignition_defaults.py

No input file: the values are the firmware defaults, re-implemented from the rusEFI source
(paths relative to the rusEFI repository root):
  - dwell: setConstantDwell(4) in firmware/controllers/algo/defaults/default_ignition.cpp
    (bins 0, 1000 ... 7000 RPM, firmware/controllers/algo/engine_configuration.cpp), cranking
    dwell DEFAULT_CRANKING_DWELL_MS = 6 (firmware/controllers/algo/defaults/defaults.h);
    coil duty as getCoilDutyCycle / getNumberOfSparks (firmware/controllers/engine_cycle/spark_logic.cpp).
  - timing table: buildTimingMap(35) / getInitialAdvance in default_ignition.cpp, RPM axis
    setTimingRpmBin(800, 7000) -> setRpmBin (firmware/util/containers/table_helper.h), load axis
    setLinearCurve(20, 120, 3); 16 x 16 cells as on Proteus F7 (IGN_RPM_COUNT / IGN_LOAD_COUNT).
Output: documentation/docs/img/plots/ignition-default-dwell.svg
        documentation/docs/img/plots/ignition-default-timing.svg
"""
import math
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/docs/img/plots"


def efi_round(value, precision):  # firmware/util/efilib.cpp efiRound (roundf: half away from zero)
    a = value / precision
    a = math.floor(a + 0.5) if a >= 0 else -math.floor(-a + 0.5)
    return a * precision


def interpolate(x1, y1, x2, y2, x):
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def rpm_bins(size, idle, top):  # setRpmBin
    step = int(efi_round((top - idle) / (size - 2), 50) - 150)
    return [idle - 150] + [idle + step * (i - 1) for i in range(1, size - 1)] + [top]


def initial_advance(rpm, load, advance_max=35):  # getAdvanceForRpm + getInitialAdvance
    load = min(load, 100.0)
    if rpm >= 3000:
        adv = advance_max
    elif rpm < 600:
        adv = 10
    else:
        adv = interpolate(600, 10, 3000, advance_max, rpm)
    if rpm >= 3000:
        return efi_round(adv + 0.1 * (100 - load), 0.1)
    return efi_round(adv + 0.1 * (100 - load) * rpm / 3000, 0.1)


# house palette (STANDARD.md section 6): blue = asked for, orange = driven, green = closed loop, red = safety
BLUE, ORANGE, GREEN, RED, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#c8412d", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})


def finish(fig, axes, name):
    fig.patch.set_alpha(0)
    for ax in axes:
        ax.patch.set_alpha(0)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / name, transparent=True)
    print("wrote", (OUT / name).relative_to(ROOT))


# ---- Figure: default dwell and the coil duty it produces on a 4-cylinder engine ----
dwell_rpm = [1000 * i for i in range(8)]
dwell_ms = [4.0] * 8
CRANK_DWELL = 6.0
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.4))
a1.plot(dwell_rpm, dwell_ms, color=BLUE, lw=2, marker="o", ms=4, label="Dwell time base (running)")
a1.axhline(CRANK_DWELL, color=GREY, lw=1.5, ls="--")
a1.text(7000, CRANK_DWELL + 0.15, "Fixed Cranking Dwell 6 ms", ha="right", va="bottom", fontsize=8.5)
a1.set_xlim(0, 7200)
a1.set_ylim(0, 8)
a1.set_xlabel("engine speed (RPM)")
a1.set_ylabel("dwell (ms)")
a1.set_title("Factory dwell: 4 ms at every engine speed", fontsize=10)
a1.legend(loc="lower left", frameon=False, fontsize=8.5)

rpm = list(range(500, 7001, 50))
cycle_ms = [2 * 60000 / r for r in rpm]  # four-stroke cycle = two revolutions
sparks = {"Individual Coils (1 spark per coil per cycle)": (1, BLUE, "-"),
          "Wasted Spark (2)": (2, ORANGE, "-"),
          "Single Coil, 4 cylinders (4)": (4, RED, "-")}
for label, (n, c, ls) in sparks.items():
    a2.plot(rpm, [100 * 4.0 * n / cy for cy in cycle_ms], color=c, lw=2, ls=ls, label=label)
a2.set_xlim(0, 7200)
a2.set_ylim(0, 100)
a2.set_xlabel("engine speed (RPM)")
a2.set_ylabel("coil duty cycle (%)")
a2.set_title("Coil duty with 4 ms dwell", fontsize=10)
a2.legend(loc="upper left", frameon=False, fontsize=8)
finish(fig, (a1, a2), "ignition-default-dwell.svg")

# ---- Figure: default ignition table shape ----
rpms = rpm_bins(16, 800, 7000)
loads = [efi_round(interpolate(0, 20, 15, 120, i), 3) for i in range(16)]
fig, ax = plt.subplots(figsize=(8, 3.8))
show = [loads[0], loads[4], loads[8], loads[15]]  # 99-120 kPa rows are identical: the formula clamps load at 100
colours = [BLUE, "#4f7fe0", GREY, ORANGE]
for load, c in zip(show, colours):
    ax.plot(rpms, [initial_advance(r, load) for r in rpms], color=c, lw=2, marker="o", ms=3.5,
            label=f"{load:.0f} kPa" + (" (and 99-114)" if load == loads[15] else ""))
ax.set_xlim(0, 7200)
ax.set_ylim(0, 50)
ax.set_xlabel("engine speed (RPM) — the table's 16 RPM columns")
ax.set_ylabel("ignition advance (° BTDC)")
ax.legend(title="load (MAP)", loc="lower right", frameon=False, fontsize=8.5, title_fontsize=8.5)
ax.annotate("advance rises with RPM up to 3000 RPM,\nthen stays flat", xy=(3200, 42.9), xytext=(3700, 46.5),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
ax.annotate("less advance at\nhigher load", xy=(4700, 35.0), xytext=(5200, 23),
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)
finish(fig, (ax,), "ignition-default-timing.svg")
print("rpm bins", rpms)
print("load bins", loads)
