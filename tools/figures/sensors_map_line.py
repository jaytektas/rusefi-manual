#!/usr/bin/env python3
"""Figure: the two-point MAP line, and the fault band around it.

    .venv/bin/python tools/figures/sensors_map_line.py

Data (no measurements, all from the rusEFI source):
  - conversion: firmware/controllers/sensors/converters/linear_func.cpp (LinearFunc::configure/convert:
    a straight line through two points, and the too-low / too-high output check)
  - sensor model points: firmware/init/sensor/init_map.cpp (getMapCfg: MT_MPX4250, MT_GM_3_BAR,
    MT_BOSCH_3_BAR)
  - factory default model MPX4250: firmware/controllers/algo/engine_configuration.cpp
    (setDefaultEngineConfiguration: map.sensor.type = MT_MPX4250)
  - fault limits: firmware/controllers/algo/engine_configuration.cpp (mapErrorDetectionTooLow = 5,
    mapErrorDetectionTooHigh = 410) and firmware/init/sensor/init_map.cpp (configureMapFunction)
Output: documentation/docs/img/plots/sensors-map-line.svg
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]

# (label, (v1, kpa1, v2, kpa2), colour, style) — getMapCfg() in init_map.cpp
MODELS = [
    ("MPX4250 — factory default", (0.204, 20, 4.896, 250), "#2563eb", "-"),
    ("GM 3 Bar", (0.631, 40, 4.914, 304), "#8a8f98", "--"),
    ("Bosch 3 Bar", (0.39, 11, 4.65, 310), "#8a8f98", ":"),
]
LOW, HIGH = 5.0, 410.0            # mapErrorDetectionTooLow / TooHigh defaults
GREY, RED = "#8a8f98", "#c8412d"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})
fig, ax = plt.subplots(figsize=(8, 4.2))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

# fault bands (LinearFunc rejects the reading, not the clipped value)
ax.axhspan(-20, LOW, color=RED, alpha=0.14, lw=0)
ax.axhspan(HIGH, 440, color=RED, alpha=0.14, lw=0)
ax.text(0.12, LOW - 14, f"reading rejected below {LOW:g} kPa", fontsize=8.5, va="top")
ax.text(4.88, HIGH + 14, f"reading rejected above {HIGH:g} kPa", fontsize=8.5, ha="right")

for label, (v1, p1, v2, p2), colour, ls in MODELS:
    ax.plot([v1, v2], [p1, p2], color=colour, lw=2, ls=ls, label=label)
    for v, p in ((v1, p1), (v2, p2)):
        ax.plot(v, p, "o", ms=6, color=colour, mec="white", mew=1.2)

# key-on, engine stopped: the plenum sits at atmospheric pressure, which is
# what MAP is expected to say on the MPX4250 line
v_atm = 0.204 + (101 - 20) * (4.896 - 0.204) / (250 - 20)
ax.plot([v_atm], [101], marker="*", ms=13, color="#2e9d4f", mec="white", mew=1)
ax.annotate("key on, engine stopped:\n≈ 1.85 V → about 101 kPa\n(the same as baro on a level road)",
            xy=(v_atm, 101), xytext=(2.55, 62), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=GREY))

ax.set_xlim(0, 5)
ax.set_ylim(-20, 440)
ax.set_xlabel("voltage at the input pin (V) — MAP is on Analog Volt 1, White 13")
ax.set_ylabel("manifold pressure (kPa)")
ax.axhline(0, color=GREY, lw=0.5, alpha=0.4)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.92), frameon=False, fontsize=8.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
out = ROOT / "documentation/docs/img/plots/sensors-map-line.svg"
fig.savefig(out, transparent=True)
print("wrote", out.relative_to(ROOT))
