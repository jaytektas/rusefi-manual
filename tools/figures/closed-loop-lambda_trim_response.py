#!/usr/bin/env python3
"""Figure: how fast STFT and LTFT move, replaying the firmware's own integrator.

    .venv/bin/python tools/figures/closed-loop-lambda_trim_response.py

Data is not measured: the two curves are produced by stepping the same update equations the
firmware runs, with the factory settings.

  short term   firmware/controllers/math/closed_loop_fuel_cell.cpp (ClosedLoopFuelCellBase::update:
               adjust = lambdaError / timeConstant * dt + adjustment, clamped by max add / max remove
               and hard-capped at 25 %; fixed +-0.1 error when stftIgnoreErrorMagnitude is on)
  long term    firmware/controllers/long_term_fuel_trim.cpp (LongTermFuelTrim::learn:
               newTrim = trim + dt / timeConstant * weight * (stftCorrection - trim))
  update rate  firmware/controllers/core/main_loop.h (FAST_CALLBACK_RATE 200 Hz -> dt = 5 ms)
  settings     firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultStftSettings:
               30 s time constant, +-5 % cell limits; setDefaultLtftSettings: 3000 / 1500 / 300 / 30 s
               per region, +-12.5 % limits)
Both panels hold lambda 0.05 lean of target, i.e. an error of +0.05, which is what the code integrates.
Output: documentation/docs/img/plots/closed-loop-lambda-trim-response.svg
"""
import pathlib

import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "documentation/docs/img/plots"
BLUE, ORANGE, GREEN, GREY = "#2563eb", "#e8710a", "#2e9d4f", "#8a8f98"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

DT = 1000 / 200 * 0.001          # FAST_CALLBACK_PERIOD_MS, seconds
ERROR = 0.05                     # measured lambda minus target lambda
CELL_LIMIT = 0.05                # stft cellCfgs maxAdd / maxRemove, factory 5 %


def stft(seconds, time_constant, fixed_rate=False):
    """One cell's correction, stepped exactly like ClosedLoopFuelCellBase::update()."""
    out, adjust, t = [0.0], 0.0, 0.0
    while t < seconds:
        err = (0.1 if ERROR > 0 else -0.1) if fixed_rate else ERROR
        adjust = min(max(adjust + err / time_constant * DT, -CELL_LIMIT), CELL_LIMIT)
        t += DT
        out.append(100 * adjust)
    return out


def ltft(seconds, time_constant, target):
    """A trim table cell, stepped like LongTermFuelTrim::learn() with weight = 1 (cell centre)."""
    out, trim, t = [0.0], 0.0, 0.0
    gain = 1 / min(max(time_constant, 1), 3000)
    while t < seconds:
        trim += gain * DT * (target - trim)
        t += DT
        out.append(100 * trim)
    return out


fig, (a, b) = plt.subplots(2, 1, figsize=(7, 6.4))
fig.patch.set_alpha(0)

# ---- panel A: short term trim ----
t60 = [i * DT for i in range(int(60 / DT) + 1)]
a.plot(t60, stft(60, 1), color=BLUE, lw=2, label="time const 1 s")
a.plot(t60, stft(60, 5), color=BLUE, lw=2, label="time const 5 s")
a.plot(t60, stft(60, 30), color=BLUE, lw=2, label="time const 30 s (factory)")
a.plot(t60, stft(60, 30, fixed_rate=True), color=ORANGE, ls="--", lw=2,
       label="time const 30 s, fixed rate")
a.axhline(100 * CELL_LIMIT, color=GREEN, lw=1, ls=":")
a.set_xlim(0, 62)
a.set_ylim(0, 6.6)
a.set_xlabel("seconds since the lambda error appeared")
a.set_ylabel("STFT correction, %")
a.grid(alpha=0.25)
a.spines["top"].set_visible(False)
a.spines["right"].set_visible(False)
a.legend(frameon=False, fontsize=8.5, loc="lower right")
a.text(61.5, 5.2, "factory cell limit: Max add 5 %", color=GREEN, fontsize=8.5,
       ha="right", va="bottom")

# ---- panel B: long term trim ----
t3600 = [i * DT for i in range(int(3600 / DT) + 1)]
for tau, name in ((30, "Power region, time const 30 s"), (300, "Cruise region, 300 s"),
                  (1500, "Overrun region, 1500 s"), (3000, "Idle region, 3000 s")):
    b.plot([s / 60 for s in t3600], ltft(3600, tau, 0.05), color=BLUE, lw=2, label=name)
b.axhline(5, color=GREEN, lw=1, ls=":")
b.set_xlim(0, 62)
b.set_ylim(0, 6.9)
b.set_xlabel("minutes spent in that region with a steady 5 % short term trim")
b.set_ylabel("LTFT cell value, %")
b.grid(alpha=0.25)
b.spines["top"].set_visible(False)
b.spines["right"].set_visible(False)
b.legend(frameon=False, fontsize=8.5, loc="lower right", bbox_to_anchor=(1.0, 0.05))
b.text(0.4, 5.2, "the short term loop holds 5 %: the long term trim chases it and never quite reaches it",
       color=GREEN, fontsize=8.5, va="bottom")

fig.tight_layout()
fig.savefig(OUT / "closed-loop-lambda-trim-response.svg", transparent=True)
print("wrote", OUT / "closed-loop-lambda-trim-response.svg")
