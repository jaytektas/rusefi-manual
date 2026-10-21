#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# Example 1: isBoostControlEnabled=enabled boostControlPin="Lowside 13" boostOpenLoopLoadBins="0 20 40 50 60 70 80 100", open-loop rows 0 0 0 10 20 23 26 30
shot "Advanced ▸ Boost Control ▸ Boost control options" $I/boost-options.png
shot "Advanced ▸ Boost Control ▸ Boost control Open loop base duty cycle" $I/boost-open-loop.png
# Example 2: boostType="Open + Closed Loop" minimumBoostClosedLoopMap=120 boostClosedLoopLoadBins="0 30 40 50 60 70 80 100", target rows 100 100 116 132 148 164 180 180; boostCutPressure=200
shot "Advanced ▸ Boost Control ▸ Boost control target" $I/boost-target.png
shot "Advanced ▸ Boost Control ▸ Boost control PID" $I/boost-pid.png
shot "Setup ▸ Limits and protection ▸ Limits and fallbacks" $I/boost-limits.png

# Live (ECU A on USB). tune: isBoostControlEnabled=enabled boostOpenLoopBlends1_blendParameter=IAT
#   boostOpenLoopBlends1_blendBins="0 10 20 30 40 50 60 70" boostOpenLoopBlends1_blendValues="0 0 0 10 25 50 75 100"
shot "Advanced ▸ Boost blend tables ▸ Open loop 1 bias" $I/boost-blend.png
