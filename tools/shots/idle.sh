#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# tune: useIdleTimingPidControl=yes; idleMode="Open Loop + Closed Loop" useIacPidMultTable=yes (8x8 table 0.3..1.0); useStepperIdle=yes useHbridgesToDriveIdleStepper=yes
shot "Idle ▸ Closed-loop Ignition idle timing" $I/idle-timing-pid-panel.png
shot "Idle ▸ Idle settings" $I/idle-pid-panel.png
shot "Idle ▸ IAC PID multiplier" $I/idle-pid-mult-table.png
shot "Idle ▸ Idle After Start (Crank-to-Run) Taper vs CLT" $I/idle-taper-curve.png
# idle-stepper-hbridge-panel.png: Idle ▸ Idle hardware, cropped to the Stepper H-Bridge Hardware panel

# Live shots (ECU A connected on USB): set values with ts_tune_set.py on the live project, restart TunerStudio
# and press Send Current TunerStudio Settings in the Difference Report.
# tune: as shipped (useStepperIdle=no, idle_solenoidPin=NONE)
shot "Idle ▸ Idle hardware" $I/idle-hardware.png
shot "Idle ▸ Idle Target RPM from CLT" $I/idle-target-rpm-curve.png
# idle-open-loop-table.png: Idle ▸ Idle Position from CLT vs Idle Target RPM, window resized to 1000x560
# idle-menu.png: Idle toolbar menu dropped, cropped to the menu
# tune: idleMode="Open Loop + Closed Loop" idle_solenoidPin="Lowside 15"
# idle-solenoid-panel.png: Idle ▸ Idle hardware cropped to the top and Solenoid panel
# idle-settings.png / idle-extra-panel.png: Idle ▸ Idle settings cropped to the top / Extra Idle Features
# idle-bench-test.png: Controller ▸ Bench test cropped to the Misc column
# tune: useStepperIdle=yes useHbridgesToDriveIdleStepper=yes stepperForceParkingEveryRestart=no idle_solenoidPin=NONE
# idle-stepper-panel.png: Idle ▸ Idle hardware, the top rows and the Stepper panel stacked
