#!/usr/bin/env python3
"""Figure: the two timing blends a tuner has to know about — cranking to running, and idle to running.

    .venv/bin/python tools/figures/tuning_ignition_cranking_idle.py

Left panel maths and constants are the firmware's (paths relative to the rusEFI repository root):
  - getCrankingAdvance: interpolateClamped(minCrankingRpm, crankingTimingAngle, cranking.rpm,
      getRunningAdvance(cranking.rpm, load), rpm)
      (firmware/controllers/algo/ignition/ignition_state.cpp)
  - crankingTimingAngle 6°, cranking.rpm 550 RPM (DEFAULT_CRANKING_ANGLE, setDefaultCranking:
    firmware/controllers/algo/defaults/defaults.h and default_cranking.cpp)
  - the running value comes from the factory table formula getInitialAdvance(rpm, map, 35)
    (firmware/controllers/algo/defaults/default_ignition.cpp)
  - "Table" mode reads the crankingAdvance curve, factory 0° at every point (useSeparateAdvanceForCranking;
    setArrayValues(config->crankingAdvance, 0) in default_cranking.cpp)
  - minCrankingRpm is the lowest RPM measured during this starting attempt
    (RpmCalculator, firmware/controllers/engine_cycle/rpm_calculator.cpp); 250 RPM is assumed here.
Right panel maths is the firmware's:
  - interpolateClamped(idlePidDeactivationTpsThreshold / 2, idleAdvance, idlePidDeactivationTpsThreshold,
      running table value, TPS) (firmware/controllers/algo/ignition/ignition_state.cpp)
  - idlePidDeactivationTpsThreshold default 5 % (firmware/controllers/algo/engine_configuration.cpp)
  - the 20° idle and 12° running angles are assumed, to show the shape of the blend only.

Output: documentation/docs/img/plots/tuning-ignition-cranking-idle.svg
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


def interpolate_clamped(x1, y1, x2, y2, x):  # firmware/util/math/interpolate.cpp interpolateClamped
    if x <= x1:
        return y1
    if x >= x2:
        return y2
    return interpolate(x1, y1, x2, y2, x)


def initial_advance(rpm, load, advance_max=35):  # getInitialAdvance, factory MAP-based table
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


CRANK_RPM = 550          # engineConfiguration->cranking.rpm
CRANK_ANGLE = 6.0        # engineConfiguration->crankingTimingAngle
MIN_CRANK_RPM = 250.0    # assumed minCrankingRpm for this starting attempt
LOAD = 25.0              # kPa of ignition load: closed throttle
IDLE_TPS_THRESHOLD = 5.0  # idlePidDeactivationTpsThreshold default
IDLE_ANGLE, RUNNING_ANGLE = 20.0, 12.0  # assumed table values, to show the blend shape

BLUE, ORANGE, GREEN, RED, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#c8412d", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))

# ---- left: cranking -> running ----
rpms = list(range(100, 1501, 10))
transition = initial_advance(CRANK_RPM, LOAD)
fixed_taper, table_mode, running = [], [], []
for rpm in rpms:
    running.append(initial_advance(rpm, LOAD))
    # above the Cranking RPM limit the firmware uses the running table, so stop the cranking line there
    fixed_taper.append(interpolate_clamped(MIN_CRANK_RPM, CRANK_ANGLE, CRANK_RPM, transition, rpm)
                       if rpm <= CRANK_RPM else math.nan)
    table_mode.append(0.0 if rpm < CRANK_RPM else initial_advance(rpm, LOAD))
a1.plot(rpms, running, color=BLUE, lw=2, label="running table at 25 kPa")
a1.plot(rpms, fixed_taper, color=GREEN, lw=2, label="Fixed (auto taper), 6° while cranking")
a1.plot(rpms, table_mode, color=RED, lw=2, ls="--", label="Table mode, factory curve (0°)")
a1.axvline(CRANK_RPM, color=GREY, lw=1, ls=":")
a1.text(CRANK_RPM + 30, 21.0, "Cranking RPM limit 550", fontsize=8.5, va="top")
a1.axvline(MIN_CRANK_RPM, color=GREY, lw=1, ls=":")
a1.text(MIN_CRANK_RPM - 12, 19.0, "250 RPM", fontsize=8.5, ha="right")
a1.set_xlim(0, 1500)
a1.set_ylim(-2, 24)
a1.set_xlabel("engine speed (RPM)")
a1.set_ylabel("advance (° BTDC)")
a1.set_title("Cranking to running: Timing Advance mode", fontsize=9.5)
a1.legend(loc="lower right", frameon=False, fontsize=8)

# ---- right: idle table -> running table ----
tpss = [i / 10 for i in range(0, 81)]
a2.plot(tpss, [interpolate_clamped(IDLE_TPS_THRESHOLD / 2, IDLE_ANGLE, IDLE_TPS_THRESHOLD,
                                   RUNNING_ANGLE, t) for t in tpss], color=GREEN, lw=2)
a2.axvline(IDLE_TPS_THRESHOLD / 2, color=GREY, lw=1, ls=":")
a2.axvline(IDLE_TPS_THRESHOLD, color=GREY, lw=1, ls=":")
a2.text(IDLE_TPS_THRESHOLD / 2 + 0.1, 23.4, "2.5 %", fontsize=8.5, va="top")
a2.text(IDLE_TPS_THRESHOLD + 0.1, 23.4, "5 %", fontsize=8.5, va="top")
a2.text(1.25, 20.4, "idle curve (20° assumed)", fontsize=8.5)
a2.text(5.6, 12.4, "running table\n(12° assumed)", fontsize=8.5, va="bottom")
a2.text(0.2, 8.6, "TPS threshold 5 % by default", fontsize=8.5)
a2.set_xlim(0, 8)
a2.set_ylim(8, 24)
a2.set_xlabel("throttle position, or pedal position (TPS %)")
a2.set_ylabel("advance (° BTDC)")
a2.set_title("Idle table blended out as the throttle opens", fontsize=9.5)

fig.patch.set_alpha(0)
for ax in (a1, a2):
    ax.patch.set_alpha(0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "tuning-ignition-cranking-idle.svg", transparent=True)
print("wrote tuning-ignition-cranking-idle.svg")
print("running value at 550 RPM / 25 kPa =", transition)
