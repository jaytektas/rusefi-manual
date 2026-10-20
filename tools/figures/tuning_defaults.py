#!/usr/bin/env python3
"""Figures: the firmware's DEFAULT VE table and DEFAULT ignition table, as curves (illustrative only).

    .venv/bin/python tools/figures/tuning_defaults.py

Data: reproduced from rusEFI firmware defaults, not from an engine:
  firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultVETable hardCodedveTable; setFuelTablesLoadBin(10, 160))
  firmware/controllers/algo/defaults/default_ignition.cpp (getInitialAdvance, buildTimingMap(35), ignitionLoadBins 20..120)
  firmware/util/containers/table_helper.h (setRpmBin, setLinearCurve)
Output: documentation/docs/img/plots/tuning-default-ve.svg, tuning-default-ignition.svg
"""
import pathlib
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]

def efi_round(v, p):
    return round(v / p) * p

def rpm_bins(n, idle=800, top=7000):
    step = int(efi_round((top - idle) / (n - 2), 50) - 150)
    return [idle - 150] + [idle + step * (i - 1) for i in range(1, n - 1)] + [top]

def linear(n, a, b, p):
    return [efi_round(a + (b - a) * i / (n - 1), p) for i in range(n)]

VE = [
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

def initial_advance(rpm, load, amax=35):
    load = min(load, 100)
    adv = amax if rpm >= 3000 else (10 if rpm < 600 else 10 + (amax - 10) * (rpm - 600) / 2400)
    if rpm >= 3000:
        return round(adv + 0.1 * (100 - load), 1)
    return round(adv + 0.1 * (100 - load) * rpm / 3000, 1)

BLUE, ORANGE, GREEN, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})
colors = [GREY, GREEN, BLUE, ORANGE]

def plot(xs, rows, labels, ylabel, title, out):
    fig, ax = plt.subplots(figsize=(8, 3.6))
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    for r, l, c in zip(rows, labels, colors):
        ax.plot(xs, r, color=c, lw=2, marker="o", ms=3, label=l)
    ax.set_xlabel("engine speed (RPM)"); ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(ROOT / "documentation/docs/img/plots" / out, transparent=True)
    print("wrote", out)

ve_rpm = rpm_bins(16); ve_load = linear(16, 10, 160, 1)
idx = [1, 5, 9, 13]
plot(ve_rpm, [VE[i] for i in idx], [f"{ve_load[i]:.0f} kPa" for i in idx], "VE (%)",
     "Factory default VE table (not a tune for any engine)", "tuning-default-ve.svg")

ign_rpm = rpm_bins(16); ign_load = linear(16, 20, 120, 3)
idx = [0, 5, 10, 15]
plot(ign_rpm, [[initial_advance(r, ign_load[i]) for r in ign_rpm] for i in idx],
     [f"{ign_load[i]:.0f} kPa" for i in idx], "advance (° BTDC)",
     "Factory default ignition table (not a tune for any engine)", "tuning-default-ignition.svg")
