#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# tune: useLambdaOnInterface=Lambda
shot "Setup ▸ Vehicle Information" $I/engine-basics-vehicle-information.png
# then: cylindersCount=2 firingOrder="1-2" timing_offset_cylinder2=45
shot "Advanced ▸ Cylinder offsets" $I/engine-basics-cylinder-offsets.png
