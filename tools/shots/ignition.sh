#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py, restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# state A tune: ignitionMode="Individual Coils" multisparkEnable="yes" enableTrailingSparks="yes"
shot "Setup ▸ Vehicle Information" $I/ignition-vehicle-info.png
shot "Ignition ▸ Ignition hardware" $I/ignition-hardware-cop.png
shot "Ignition ▸ Dwell" $I/ignition-dwell.png
shot "Cranking ▸ Cranking settings" $I/ignition-cranking.png
shot "Ignition ▸ Ignition advance" $I/ignition-advance-table.png
shot "Ignition ▸ CLT timing correction" $I/ignition-clt-corr.png
shot "Ignition ▸ IAT timing correction" $I/ignition-iat-corr.png
shot "Ignition ▸ Multispark" $I/ignition-multispark.png
shot "Controller ▸ Rotary" $I/ignition-rotary.png
# state B: timingMode="fixed" fixedTiming=10.0
shot "Ignition ▸ Ignition hardware" $I/ignition-hardware-fixed.png
# state C: ignitionMode="Wasted Spark" ignitionPins1="Ign 1" ignitionPins2="NONE" ignitionPins3="Ign 2" ignitionPins4="NONE" timingMode="dynamic"
shot "Ignition ▸ Ignition hardware" $I/ignition-hardware-wasted.png
# ignition-menu.png: Ignition menu cropped to the menu
