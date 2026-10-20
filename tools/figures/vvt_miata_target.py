#!/usr/bin/env python3
"""Figure: a shipped rusEFI base tune's intake VVT target table (Mazda MX-5 NB 1.8 VVT).

    .venv/bin/python tools/figures/vvt_miata_target.py

Data (values copied straight out of the firmware):
  firmware/config/engines/mazda/mazda_miata_vvt.cpp
    (vvt18RpmBins, vvt18LoadBins, SCRIPT_TABLE_vvt_target; copied into config->vvtTable1 by
     setMazdaMiataEngineNB2Defaults for the Miata NB base tunes)
  firmware/controllers/actuators/vvt.cpp (initVvtActuators: vvtTable1 drives the intake cams)
Output: documentation/docs/img/plots/vvt-miata-target.svg
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

# firmware/config/engines/mazda/mazda_miata_vvt.cpp
RPM = [700, 1000, 2000, 3000, 3500, 4500, 5500, 6500]          # vvt18RpmBins
# SCRIPT_TABLE_vvt_target, rows in order of vvt18LoadBins {30, 40, 50, 60, 70, 75, 82, 85}
TABLE = {
    30: [1,  3, 10, 20, 27, 28, 11, 5],
    40: [3, 10, 19, 26, 30, 28, 11, 5],
    50: [7, 16, 24, 28, 30, 28, 11, 5],
    60: [11, 20, 27, 28, 30, 28, 11, 5],
    70: [13, 24, 31, 28, 30, 28, 11, 5],
    75: [15, 27, 33, 28, 30, 28, 11, 5],
    82: [17, 28, 33, 28, 30, 28, 11, 5],
    85: [17, 28, 33, 28, 30, 28, 11, 5],
}

fig, ax = plt.subplots(figsize=(8, 3.8))
fig.patch.set_alpha(0); ax.patch.set_alpha(0)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)

for load, colour in ((30, GREY), (50, BLUE), (70, GREEN), (85, ORANGE)):
    ax.plot(RPM, TABLE[load], color=colour, lw=2, marker="o", ms=4, label=f"load bin {load}")

ax.set_xlabel("engine speed (RPM)")
ax.set_ylabel("intake VVT target (deg)")
ax.set_ylim(0, 35)
ax.set_xlim(500, 6700)
fig.subplots_adjust(left=0.085, right=0.985, top=0.84, bottom=0.13)
fig.legend(loc="upper center", ncol=4, frameon=False, fontsize=8.5,
           bbox_to_anchor=(0.5, 1.005), handles=ax.get_legend_handles_labels()[0])
fig.savefig(ROOT / "documentation/docs/img/plots/vvt-miata-target.svg", transparent=True)
print("wrote vvt-miata-target.svg")
