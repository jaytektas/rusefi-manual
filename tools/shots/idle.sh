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
