#!/usr/bin/env bash
# Cranking chapter screenshots, offline: TunerStudio on the bench display with the offline Proteus F7
# project (no ECU, Work Offline). Factory cranking defaults; Starter Control set in the tune first:
#   tools/shots/ts_tune_set.py <tune> startStopButtonPin="Digital 3" starterControlPin="Lowside 14 or starter"
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk '{print $1}' | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
DISPLAY=:99 xdotool mousemove 690 68 click 1; sleep 1
DISPLAY=:99 import -window root -crop 326x212+588+82 +repage $I/cranking-menu.png; DISPLAY=:99 xdotool key Escape
shot "Cranking ▸ Cranking settings" $I/cranking-settings.png
shot "Cranking ▸ Cranking Base Fuel (Engine Cycle vs CLT)" $I/cranking-base-fuel.png
shot "Cranking ▸ Cranking Fuel multiplier" $I/cranking-clt-mult.png
shot "Cranking ▸ Priming pulse" $I/cranking-priming.png
shot "Cranking ▸ After-start enrichment" $I/cranking-ase.png
shot "Cranking ▸ Cranking Air Amount vs CLT" $I/cranking-air.png
shot "Setup ▸ Outputs" $I/cranking-starter-control.png
