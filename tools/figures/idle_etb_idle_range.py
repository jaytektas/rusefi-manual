#!/usr/bin/env python3
"""Figure: how the idle controller's position shifts the ETB pedal-target map upward.

    .venv/bin/python tools/figures/idle_etb_idle_range.py

Data (rusEFI firmware defaults and arithmetic, copied from source):
  firmware/controllers/actuators/electronic_throttle.cpp
    (EtbController::getSetpointEtb: etbIdleAddition = etbIdleThrottleRange * idle position / 100,
     target = interpolateClamped(0, etbIdleAddition, 100, 100, pedal target);
     setDefaultEtbParameters: etbIdleThrottleRange = 15)
  firmware/controllers/actuators/electronic_throttle.cpp (setDefaultEtbParameters: the default
    pedal target table is one-to-one, so pedal target == pedal position)
Output: documentation/docs/img/plots/idle-etb-idle-range.svg
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

RANGE = 15.0          # etbIdleThrottleRange, default
pedal = [p * 10 for p in range(11)]     # 0 .. 100 % pedal (the default one-to-one pedal map)

def throttle_target(idle_position_pct):
    idle_add = RANGE * idle_position_pct / 100.0
    # interpolateClamped(0, idle_add, 100, 100, pedal): squeeze [0,100] into [idle_add, 100]
    return [idle_add + (100.0 - idle_add) * p / 100.0 for p in pedal]

fig, ax = plt.subplots(figsize=(8, 3.6))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

for idle_pct, colour, style in ((0, GREY, "--"), (25, BLUE, "-"), (50, GREEN, "-"), (100, ORANGE, "-")):
    ax.plot(pedal, throttle_target(idle_pct), color=colour, lw=2, ls=style,
            label=f"idle position {idle_pct} %  →  {RANGE * idle_pct / 100:.2f} % throttle at rest")

ax.set_xlabel("pedal target from the ETB pedal target table (%)")
ax.set_ylabel("throttle position the ETB aims for (%)")
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
fig.tight_layout()
fig.savefig(ROOT / "documentation/docs/img/plots/idle-etb-idle-range.svg", transparent=True)
print("wrote idle-etb-idle-range.svg")
