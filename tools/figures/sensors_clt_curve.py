#!/usr/bin/env python3
"""Figure: coolant temperature against input voltage on a Proteus temperature input.

    .venv/bin/python tools/figures/sensors_clt_curve.py

Data (no measurements, all from the rusEFI source):
  - conversion: firmware/controllers/sensors/converters/resistance_func.cpp (ResistanceFunc::convert:
    R = pull-up / (supply / V - 1), short below 0.05 V, open above 98 % of supply) and
    firmware/controllers/sensors/converters/thermistor_func.cpp (ThermistorFunc::configure/convert:
    three-point Steinhart-Hart, valid -50 ... 250 C)
  - supply 5.0 V: firmware/init/sensor/init_thermistors.cpp (configureTempSensorFunction default)
  - pull-up 2700 ohm: firmware/config/boards/proteus_meta.h (PROTEUS_DEFAULT_AT_PULLUP)
  - factory CLT points 0 C / 9500, 23.8889 C / 2100, 48.8889 C / 1000 ohm:
    firmware/controllers/algo/engine_configuration.cpp (setDefaultEngineConfiguration: clt.config)
  - presets "GM CLT" and "Bosch Various": "Common CLT Sensors" in the official Proteus F7 .ini
Output: documentation/docs/img/plots/sensors-clt-curve.svg
"""
import math
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
PULLUP, SUPPLY = 2700.0, 5.0


def coeffs(t1, r1, t2, r2, t3, r3):
    """Same algebra as ThermistorFunc::configure."""
    l1, l2, l3 = (math.log(r) for r in (r1, r2, r3))
    y1, y2, y3 = (1 / (t + 273.15) for t in (t1, t2, t3))
    u2 = (y2 - y1) / (l2 - l1)
    u3 = (y3 - y1) / (l3 - l1)
    c = ((u3 - u2) / (l3 - l2)) / (l1 + l2 + l3)
    b = u2 - c * (l1 * l1 + l1 * l2 + l2 * l2)
    a = y1 - (b + l1 * l1 * c) * l1
    return a, b, c


def temp_from_volts(v, abc):
    """ResistanceFunc + ThermistorFunc; None where the firmware reports the sensor invalid."""
    if v < 0.05 or v > 0.98 * SUPPLY:
        return None
    r = PULLUP / (SUPPLY / v - 1)
    a, b, c = abc
    lr = math.log(r)
    t = 1 / (a + b * lr + c * lr ** 3) - 273.15
    return t if -50 <= t <= 250 else None


curves = [
    ("factory default", (0, 9500, 23.8889, 2100, 48.8889, 1000), "#2563eb", "-"),
    ("preset “Bosch Various”", (0, 5896, 50, 834, 100, 187), "#8a8f98", "--"),
    ("preset “GM CLT”", (-40, 100000, 40, 1459, 130, 70), "#8a8f98", ":"),
]

GREY, RED = "#8a8f98", "#c8412d"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "text.color": GREY})
fig, ax = plt.subplots(figsize=(8, 4.2))
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)

volts = [0.02 + i * 0.002 for i in range(2490)]
for label, pts, colour, ls in curves:
    abc = coeffs(*pts)
    xs, ys = [], []
    for v in volts:
        t = temp_from_volts(v, abc)
        xs.append(v)
        ys.append(float("nan") if t is None else t)
    ax.plot(xs, ys, color=colour, lw=2, ls=ls, label=label)
    # calibration points, converted to the voltage the input sees
    for t, r in zip(pts[0::2], pts[1::2]):
        ax.plot(SUPPLY * r / (r + PULLUP), t, "o", ms=6, color=colour, mec="white", mew=1.2)

# invalid bands (ResistanceFunc): short below 0.05 V, open above 4.9 V
ax.axvspan(0, 0.05, color=RED, alpha=0.15, lw=0)
ax.axvspan(0.98 * SUPPLY, 5.0, color=RED, alpha=0.15, lw=0)
ax.text(0.09, -30, "short\n< 0.05 V", fontsize=8.5, va="top")
ax.text(4.88, 140, "open\n> 4.9 V", fontsize=8.5, va="top", ha="right")

# the fold in the factory curve (minimum of 1/T in ln R)
a, b, c = coeffs(*curves[0][1])
r_fold = math.exp(math.sqrt(b / (-3 * c)))
v_fold = SUPPLY * r_fold / (r_fold + PULLUP)
t_fold = temp_from_volts(v_fold, (a, b, c))
ax.annotate(f"factory curve turns back:\ncoldest it can show ≈ {t_fold:.0f} °C at {v_fold:.2f} V",
            xy=(v_fold, t_fold), xytext=(2.75, -38), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=GREY))

ax.set_xlim(0, 5)
ax.set_ylim(-50, 150)
ax.set_xlabel("voltage at the input pin (V), 2700 Ω pull-up to 5 V")
ax.set_ylabel("temperature shown (°C)")
ax.axhline(0, color=GREY, lw=0.5, alpha=0.4)
ax.legend(loc="upper right", bbox_to_anchor=(0.97, 0.80), frameon=False, fontsize=8.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
out = ROOT / "documentation/docs/img/plots/sensors-clt-curve.svg"
fig.savefig(out, transparent=True)
print("wrote", out.relative_to(ROOT))
