#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py, restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# tune: injector_flow=260.0 (bench tune otherwise: 4 cyl, 2.0 L, 1-3-4-2, Sequential, Lowside 1-4)
shot "Setup ▸ Vehicle Information" $I/fuel-vehicle-information.png
shot "Fuel ▸ Injector Setup ▸ Injection configuration" $I/fuel-injector-config.png
shot "Fuel ▸ Injector Setup ▸ Injection hardware" $I/fuel-injection-hardware.png
shot "Fuel ▸ Injector Setup ▸ Injection Timing" $I/fuel-injection-timing-table.png
shot "Fuel ▸ Injector Setup ▸ Injector deadtime (BatV vs fuel pressure)" $I/fuel-deadtime-table.png
shot "Fuel ▸ Target AFR" $I/fuel-target-afr-table.png      # untick 3D View first
shot "Controller ▸ Injector test" $I/fuel-injector-test.png
# fuel-menu.png: Fuel menu with Injector Setup hovered, cropped to the two menus

# Live shots (ECU A on USB). As shipped: TPS / Lua AE calibration, Staged injection.
shot "Fuel ▸ AE / Transient fueling ▸ TPS / Lua AE calibration" $I/fuel-ae-tps-table.png
shot "Fuel ▸ Staged injection" $I/fuel-staged-injection.png
# tune: tpsAccelLookback=0.3 noFuelTrimAfterAccelTime=1 fuelClosedLoopCorrectionEnabled=enabled coastingFuelCutEnabled=enabled
#       injectorNonlinearMode=Polynomial applyNonlinearBelowPulse=2 useEngineStateMachine=enabled
shot "Fuel ▸ AE / Transient fueling ▸ Acceleration enrichment settings" $I/fuel-accel-enrichment.png
shot "Fuel ▸ Short term fuel trim/Closed loop" $I/fuel-closed-loop.png
shot "Fuel ▸ Deceleration fuel cutoff (DFCO)" $I/fuel-dfco.png
shot "Fuel ▸ Injector Setup ▸ Injector small-pulse correction" $I/fuel-small-pulse-correction.png
shot "Fuel ▸ Fuel Corrections ▸ WOT Enrichment" $I/fuel-wot-enrichment.png
