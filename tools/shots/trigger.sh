#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py, restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# bench tune (60-2 on VR 1, factory advanced trigger)
shot "Setup ▸ Advanced Trigger" $I/trigger-advanced.png
shot "Setup ▸ Trigger Gap Override" $I/trigger-gap-override.png
# Example 1: timingMode="fixed" fixedTiming=10.0 globalTriggerAngleOffset=114.0 vvtMode1="Single Tooth" injectionMode="Batch"
shot "Setup ▸ Trigger" $I/trigger-dialog.png
shot "Ignition ▸ Ignition hardware" $I/trigger-ignition-fixed-timing.png
shot "Fuel ▸ Injector Setup ▸ Injection configuration" $I/trigger-injection-batch.png
# Example 2: trigger_type="36-1" triggerInputPins1="Digital 1" globalTriggerAngleOffset=90.0 vvtMode1="Inactive" injectionMode="Sequential" timingMode="dynamic"
shot "Setup ▸ Trigger" $I/trigger-dialog-36-1-hall.png
