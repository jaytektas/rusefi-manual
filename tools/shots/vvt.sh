#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# tune: trigger_type=60-2 triggerInputPins1="VR 1" globalTriggerAngleOffset=0 vvtMode1="Single Tooth" isPhaseSyncRequiredForIgnition=yes vvtPins1="Lowside 15", vvtTable1 bins 700..6500 / 30..85
shot "Setup ▸ Trigger" $I/vvt-cam-inputs.png
shot "Setup ▸ Advanced Trigger" $I/vvt-advanced-trigger.png
shot "Advanced ▸ VVT intake target" $I/vvt-intake-target-table.png
