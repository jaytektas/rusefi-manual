#!/usr/bin/env python3
"""Figure: what rusEFI's knock controller does to timing, computed with the firmware's own rules.

    .venv/bin/python tools/figures/tuning_ignition_knock_retard.py

No input file: the maths and the constants are the firmware's (paths relative to the rusEFI
repository root):
  - one event's retard amount: (that cylinder's current timing - (-20)) * knockRetardAggression %,
    accumulated then clamped to the Max knock retard table
    (KnockControllerBase::onKnockSenseCompleted, firmware/controllers/engine_cycle/knock_controller.cpp)
  - retard removed every 10 ms at knockRetardReapplyRate (KnockControllerBase::onFastCallback, same file;
    FAST_CALLBACK_PERIOD_MS = 10, firmware/controllers/algo/engine_cycle_constants.h)
  - retard and fuel trim reset to zero below knockSuppressMin Tps (same function)
  - defaults: knockRetardAggression 20 %, knockRetardReapplyRate 3 deg/s, knockSuppressMinTps 10 %,
    Max knock retard table 2 deg everywhere (firmware/controllers/algo/defaults/default_base_engine.cpp)
  - retard is subtracted only while Timing Mode is dynamic (EngineState::periodicFastCallback,
    firmware/controllers/algo/engine2.cpp)

Scenario (stated in the figure, not firmware data): 4 cylinders at 3500 RPM, full throttle, the table
asking 25 deg for that cylinder, a knock event reported every 0.1 s from 0.5 s to 1.5 s.

Output: documentation/docs/img/plots/tuning-ignition-knock-retard.svg
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/docs/img/plots"

# firmware defaults
AGGRESSION = 20.0          # knockRetardAggression, %
REAPPLY = 3.0              # knockRetardReapplyRate, deg per second
SUPPRESS_TPS = 10.0        # knockSuppressMinTps, %
DT = 0.01                  # FAST_CALLBACK_PERIOD_MS
BASE = 25.0                # assumed table value for the cylinder, deg BTDC
TPS = 100.0                # assumed throttle position, %
EVENTS = [0.5 + 0.1 * i for i in range(11)]


def simulate(max_retard, t_end=3.0):
    """Return (t, knock retard, resulting spark advance) as the firmware would."""
    retard = 0.0
    t, r, applied = [], [], []
    step = 0
    while True:
        now = step * DT
        if TPS < SUPPRESS_TPS:
            retard = 0.0
        else:
            retard = max(0.0, retard - REAPPLY * DT)
        if now in EVENTS:
            # the cylinder's current timing already carries the retard applied so far
            cylinder_timing = BASE - retard
            amount = (cylinder_timing - (-20.0)) * AGGRESSION * 0.01
            retard = min(max(retard + amount, 0.0), max_retard)
        t.append(now)
        r.append(retard)
        applied.append(BASE - retard)
        if now >= t_end:
            return t, r, applied
        step += 1


# house palette (STANDARD.md section 6): blue = asked for, orange = driven, green = closed loop, red = safety
BLUE, ORANGE, GREEN, RED, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#c8412d", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))

for max_retard, colour, name in ((2.0, RED, "Max retard 2° (factory)"),
                                 (8.0, ORANGE, "Max retard 8°")):
    t, r, applied = simulate(max_retard)
    a1.plot(t, r, color=colour, lw=2, label=name)
    a2.plot(t, applied, color=colour, lw=2, label=name)
a2.plot([0, 3.1], [BASE, BASE], color=GREY, lw=1, ls=":", label="table request 25°")

a1.set_xlim(0, 3.1)
a1.set_ylim(0, 9)
a1.set_xlabel("time (s)")
a1.set_ylabel("knock retard (°)")
a1.set_title("Retard: 20 % aggression, an event every 0.1 s\nfrom 0.5 s to 1.5 s", fontsize=9.5)
a1.axvspan(0.5, 1.5, color=GREY, alpha=0.15, lw=0)
a1.text(1.0, 0.4, "knock events", ha="center", fontsize=8.5)

a2.set_xlim(0, 3.1)
a2.set_ylim(15, 27)
a2.set_xlabel("time (s)")
a2.set_ylabel("spark advance (° BTDC)")
a2.set_title("What that cylinder actually gets", fontsize=9.5)
a2.annotate("given back at\n3 °/s", xy=(2.35, 21.3), xytext=(2.5, 16.6), ha="center",
            arrowprops=dict(arrowstyle="->", color=GREY), fontsize=8.5)

handles, labels = a2.get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8.5,
           bbox_to_anchor=(0.5, -0.02))
fig.patch.set_alpha(0)
for ax in (a1, a2):
    ax.patch.set_alpha(0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(OUT / "tuning-ignition-knock-retard.svg", transparent=True)
print("wrote tuning-ignition-knock-retard.svg")

# the numbers the figure shows, for the caption and the chapter text
for max_retard in (2.0, 8.0):
    t, r, applied = simulate(max_retard)
    peak = max(r)
    print(f"max retard {max_retard}: first event amount {(BASE + 20) * 0.2:.2f}°, "
          f"peak retard {peak:.2f}°, time to give it all back {peak / REAPPLY:.2f} s")
