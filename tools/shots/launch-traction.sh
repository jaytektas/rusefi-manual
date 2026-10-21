#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# Example 1: launchControlEnabled=enabled launchActivationMode="Clutch Down Switch" clutchDownPin="Digital 5" launchRpmThreshold=0; enableCanVss=yes canVssNbcType="Hyundai PB"
shot "Advanced ▸ Launch Control" $I/launch-traction-launch-control.png
shot "CAN-bus ▸ CAN Vehicle speed sensor" $I/launch-traction-can-vss.png
# Example 2/3: torqueReductionEnabled=enabled torqueReductionActivationMode="Launch Button" launchActivatePin="Digital 6" torqueReductionArmingRpm=4000 torqueReductionArmingApp=20; retard/cut tables X axis "Vehicle speed" bins 0..100, gear bins 1 2, 12 deg / 10 %; traction tables as in Example 3
shot "Advanced ▸ Torque Control ▸ Shift Torque Reduction (Flat Shift)" $I/launch-traction-flat-shift.png
shot "Advanced ▸ Torque Control ▸ Torque Reduction Ignition Retard Table" $I/launch-traction-retard-table.png
shot "Advanced ▸ Torque Control ▸ Torque Reduction Ignition Cut Table" $I/launch-traction-cut-table.png
shot "Controller ▸ Traction Control Timing Adjustment" $I/launch-traction-tc-timing.png
shot "Controller ▸ Traction Control ETB Drop" $I/launch-traction-tc-etb.png
shot "Controller ▸ Traction Control Skip Ignition" $I/launch-traction-tc-skip.png

# Live (ECU A on USB). tune: clutchDownPin="Digital 5" torqueReductionTimeXaxis="Vehicle speed"
#   torqueReductionTimeXBins="0 20 40 60 80 100" torqueReductionTimeTable=120 x12 totalGearsCount=5
#   gearRatio1..5=3.36 2.07 1.40 1.00 0.81 finalGearRatio=4.10
shot "Sensors ▸ Chassis sensors ▸ Misc sensors" $I/launch-traction-misc-sensors.png
shot "Advanced ▸ Torque Control ▸ Shift Torque Reduction Time table" $I/launch-traction-time-table.png
shot "Sensors ▸ Chassis sensors ▸ Vehicle speed sensor" $I/launch-traction-gear-detection.png
