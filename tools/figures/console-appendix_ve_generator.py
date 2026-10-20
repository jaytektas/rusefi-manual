#!/usr/bin/env python3
"""Figure: what the console's Base VE generator proposes, on the rusEFI factory VE axes.

    .venv/bin/python tools/figures/console-appendix_ve_generator.py

Data, all from the rusEFI repository (no measurements, no invented numbers):
  axes          firmware/controllers/algo/defaults/default_fuel.cpp (setFuelTablesLoadBin(10, 160);
                setRpmBin idle 800 / top 7000) via firmware/util/containers/table_helper.h
                — same reproduction used by tools/figures/tuning_defaults.py
  factory VE    firmware/controllers/algo/defaults/default_fuel.cpp (setDefaultVETable hardCodedveTable)
  proposed VE   java_console/models/src/main/java/com/rusefi/tune/ve/ArchetypeBaseVeV1.java
                (MAP_FACTORS, HeadArchetype, CamBehavior, generate) and
                java_console/models/src/main/java/com/rusefi/tune/ve/BaseVeGenerator.java
                (clamp 35–125, two weighted 3×3 smoothPass passes, lerp)
The Python below is a direct port of that Java; the self-checks at the bottom are the values
asserted by java_console/models/src/test/java/com/rusefi/tune/ve/BaseVeGeneratorTest.java.

Questionnaire used here (the panel's own labels): Head archetype "Stock modern 4-valve",
Cam profile "Stock", Aspiration "Naturally aspirated", VVT unticked, Idle RPM 800, Max RPM 6500.

Output: documentation/docs/img/plots/console-appendix-ve-generator.svg
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


RPM = rpm_bins(16)
LOAD = linear(16, 10, 160, 1)

# setDefaultVETable rows, one per LOAD bin (factory default, not a tune for any engine)
FACTORY = [
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

CLAMP_MIN, CLAMP_MAX = 35.0, 125.0
MAP_FACTORS = [[10, 0.60], [20, 0.65], [40, 0.72], [60, 0.82], [80, 0.92], [100, 1.00]]
HEADS = {  # HeadArchetype: label -> peak VE
    "Restrictive/legacy 2-valve": 85.0, "Good/ported 2-valve": 92.0,
    "Stock modern 4-valve": 98.0, "High-flow/performance 4-valve": 104.0,
}
CAMS = {  # CamBehavior: label -> (peakPosition, idleDrop, lowRpmDrop, redlineDrop)
    "Stock": (0.48, 28, 10, 18), "Mild": (0.58, 34, 14, 14), "Aggressive": (0.68, 42, 20, 10),
}


def clamp(v):
    return max(CLAMP_MIN, min(CLAMP_MAX, v))


def lerp(x0, y0, x1, y1, x):
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def map_ve_factor(kpa):
    if kpa <= MAP_FACTORS[0][0]:
        return MAP_FACTORS[0][1]
    if kpa >= MAP_FACTORS[-1][0]:
        return MAP_FACTORS[-1][1]
    for i in range(1, len(MAP_FACTORS)):
        if kpa <= MAP_FACTORS[i][0]:
            return lerp(MAP_FACTORS[i - 1][0], MAP_FACTORS[i - 1][1],
                        MAP_FACTORS[i][0], MAP_FACTORS[i][1], kpa)
    return MAP_FACTORS[-1][1]


def rpm_ve(rpm, idle, low, peak, high, maximum, idle_ve, low_ve, peak_ve, high_ve, redline_ve):
    if rpm <= idle:
        return idle_ve
    if rpm >= maximum:
        return redline_ve
    if rpm <= low:
        return lerp(idle, idle_ve, low, low_ve, rpm)
    if rpm <= peak:
        return lerp(low, low_ve, peak, peak_ve, rpm)
    if rpm <= high:
        return lerp(peak, peak_ve, high, high_ve, rpm)
    return lerp(high, high_ve, maximum, redline_ve, rpm)


def smooth_pass(table):
    rows, cols = len(table), len(table[0])
    out = [row[:] for row in table]
    for r in range(rows):
        for c in range(cols):
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                out[r][c] = table[r][c]
            else:
                out[r][c] = (4 * table[r][c]
                             + 2 * (table[r - 1][c] + table[r + 1][c]
                                    + table[r][c - 1] + table[r][c + 1])
                             + table[r - 1][c - 1] + table[r - 1][c + 1]
                             + table[r + 1][c - 1] + table[r + 1][c + 1]) / 16.0
    return out


def generate(head, cam, has_vvt, idle_rpm, max_rpm):
    """ArchetypeBaseVeV1.generate() over the factory axes."""
    idle_drop, low_drop, red_drop = CAMS[cam][1], CAMS[cam][2], CAMS[cam][3]
    if has_vvt:
        idle_drop *= 0.90
        low_drop *= 0.75
        red_drop *= 0.75
    peak_rpm = idle_rpm + CAMS[cam][0] * (max_rpm - idle_rpm)
    low_rpm = idle_rpm + 0.5 * (peak_rpm - idle_rpm)
    high_rpm = peak_rpm + 0.5 * (max_rpm - peak_rpm)
    peak_ve = HEADS[head]
    idle_ve = peak_ve - idle_drop
    low_ve = peak_ve - low_drop
    high_ve = peak_ve - red_drop / 2.0
    redline_ve = peak_ve - red_drop
    rpm_curve = [rpm_ve(r, idle_rpm, low_rpm, peak_rpm, high_rpm, max_rpm,
                        idle_ve, low_ve, peak_ve, high_ve, redline_ve) for r in RPM]
    table = [[clamp(rpm_curve[c] * map_ve_factor(k)) for c in range(len(RPM))] for k in LOAD]
    table = smooth_pass(smooth_pass(table))
    return [[clamp(v) for v in row] for row in table]


# self-checks: the exact values asserted by BaseVeGeneratorTest
assert abs(map_ve_factor(30) - 0.685) < 1e-9
assert abs(map_ve_factor(50) - 0.77) < 1e-9
assert abs(map_ve_factor(90) - 0.96) < 1e-9
assert map_ve_factor(5) == 0.60 and map_ve_factor(120) == 1.00
assert abs(rpm_ve(4050, 1000, 2200, 3400, 4700, 6000, 70, 88, 98, 89, 80) - 93.5) < 1e-9

PROPOSED = generate("Stock modern 4-valve", "Stock", False, 800.0, 6500.0)

GREY, ORANGE, BLUE, GREEN = "#8a8f98", "#e8710a", "#2563eb", "#2e9d4f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
                     "axes.edgecolor": GREY, "axes.labelcolor": GREY, "xtick.color": GREY,
                     "ytick.color": GREY, "text.color": GREY})

fig, ax = plt.subplots(figsize=(8.0, 3.6))
i100 = LOAD.index(100)
i30 = LOAD.index(30)
ax.plot(RPM, FACTORY[i100], color=GREY, lw=2, label="factory default, 100 kPa row")
ax.plot(RPM, PROPOSED[i100], color=BLUE, lw=2, label="proposed, 100 kPa (WOT)")
ax.plot(RPM, PROPOSED[i30], color=GREEN, lw=2, ls="--", label="proposed, 30 kPa (part throttle)")
ax.set_xlabel("Engine speed (RPM)")
ax.set_ylabel("VE (%)")
ax.set_title("Console Base VE generator: stock modern 4-valve, stock cam, "
             "naturally aspirated", fontsize=11)
ax.grid(True, color=GREY, lw=0.4, alpha=0.35)
ax.legend(frameon=False, fontsize=9)
fig.tight_layout()
out = ROOT / "documentation/docs/img/plots"
out.mkdir(parents=True, exist_ok=True)
fig.savefig(out / "console-appendix-ve-generator.svg")
print(f"wrote {(out / 'console-appendix-ve-generator.svg').relative_to(ROOT)}")
print(f"axes RPM={RPM}")
print(f"axes LOAD={LOAD}")
print(f"proposed 100 kPa row: {[round(v, 1) for v in PROPOSED[i100]]}")
print(f"proposed  30 kPa row: {[round(v, 1) for v in PROPOSED[i30]]}")
