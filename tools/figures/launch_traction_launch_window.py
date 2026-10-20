"""Launch window: spark skip ratio and absolute timing against engine speed.

Curves are the firmware's own formulas (controllers/algo/launch_control.cpp
calculateSparkSkipRatio, controllers/algo/ignition/ignition_state.cpp getRunningAdvance).
RPM values are the firmware defaults (engine_configuration.cpp: launchRpm 3000,
launchRpmWindow 500); launchCorrectionsEndRpm and the cut percentages are the chapter's
Example 1 values (Initial 10 %, Final 40 %, Absolute Timing at Launch 15 deg, with an
assumed 25 deg running advance before the window).
Output: documentation/docs/img/plots/launch-traction-launch-window.svg
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = 3000          # launchRpm (firmware default)
W = 500           # launchRpmWindow (firmware default)
E = 100           # launchCorrectionsEndRpm (example)
S = R - W         # window start
F = R - E         # corrections end
INITIAL = 10      # initialIgnitionCutPercent (Example 1)
FINAL = 40        # finalIgnitionCutPercentBeforeLaunch (Example 1)
LAUNCH_ANGLE = 15  # launchTimingRetard (Example 1)
RUNNING = 25      # running advance at the start of the window (assumed)

out = pathlib.Path(__file__).resolve().parents[2] / "documentation/docs/img/plots/launch-traction-launch-window.svg"
fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(7.4, 5.2), sharex=True)

def skip(rpm):
    if rpm < S:
        return 0
    if rpm >= R:
        return 100
    if rpm < F:
        return INITIAL + (FINAL - INITIAL) * (rpm - S) / (F - S)
    return FINAL

rpm = [r for r in range(2200, 5001, 50)]
ax1.plot(rpm, [skip(r) for r in rpm], color="#e8710a", lw=2)
ax1.set_ylabel("Spark skip requested (%)")
ax1.set_ylim(-5, 110)
ax1.axhline(0, color="#9ca3af", lw=0.8)

def advance(rpm_v):
    if rpm_v < S:
        return RUNNING
    if rpm_v >= R:
        return LAUNCH_ANGLE
    if rpm_v < F:
        return RUNNING + (LAUNCH_ANGLE - RUNNING) * (rpm_v - S) / (F - S)
    return LAUNCH_ANGLE

ax2.plot(rpm, [advance(r) for r in rpm], color="#2563eb", lw=2)
ax2.set_ylabel("Timing from the launch override (deg BTDC)")
ax2.set_xlabel("Engine speed (RPM)")
ax2.set_ylim(0, 32)

for ax in (ax1, ax2):
    ax.axvspan(S, F, color="#2563eb", alpha=0.07)
    ax.axvspan(F, R, color="#e8710a", alpha=0.07)
    ax.axvspan(R, 5000, color="#c8412d", alpha=0.10)
    for x in (S, F, R):
        ax.axvline(x, color="#6b7280", lw=1, ls=":")
    ax.spines[["top", "right"]].set_visible(False)

for ax in (ax1, ax2):
    ax.set_xticks([2200, 2500, 3000, 3500, 4000, 4500, 5000])

ax1.text((R + 5000) / 2, 55, "Launch:\n100 % skip;\nfull fuel/spark cut\nabove Launch RPM", ha="center", va="center", fontsize=8)
ax1.text(2350, 85, "nothing\nhappens", ha="center", va="center", fontsize=8, color="#6b7280")
ax2.text((S + F) / 2, 21, "pre-launch\nramp", ha="center", fontsize=8)
for x, label in ((S, "window start"), (F, "corrections end"), (R, "Launch RPM")):
    ax2.text(x + 15, 1, label, fontsize=8, rotation=90, va="bottom", color="#4b5563")

fig.tight_layout()
fig.savefig(out, transparent=True)
print(out)
