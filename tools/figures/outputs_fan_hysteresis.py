"""Fan 1 on/off hysteresis from firmware defaults (FanController::setDefaultConfiguration:
fanOnTemperature 92 C, fanOffTemperature 88 C). Output: documentation/docs/img/plots/outputs-fan-hysteresis.svg"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ON, OFF = 92, 88
out = pathlib.Path(__file__).resolve().parents[2] / "documentation/docs/img/plots/outputs-fan-hysteresis.svg"
fig, ax = plt.subplots(figsize=(7, 3.2))
# warming: off until > ON
ax.plot([80, ON, ON, 100], [0, 0, 1, 1], color="#e8710a", lw=2, label="warming up")
# cooling: on until < OFF
ax.plot([100, OFF, OFF, 80], [1.04, 1.04, 0.04, 0.04], color="#2563eb", lw=2, ls="--", label="cooling down")
ax.axvspan(OFF, ON, color="#9ca3af", alpha=0.2)
ax.text((ON + OFF) / 2, 0.5, "keeps previous\nstate", ha="center", va="center", fontsize=9)
ax.set_xlabel("Coolant temperature (°C)")
ax.set_yticks([0, 1]); ax.set_yticklabels(["fan off", "fan on"])
ax.set_xticks([80, 84, OFF, ON, 96, 100])
ax.set_xlim(80, 100); ax.set_ylim(-0.2, 1.25)
ax.legend(loc="upper left", frameon=False, fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(out, transparent=True)
print(out)
