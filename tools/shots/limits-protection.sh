#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# tune: rpmHardLimit=6800 rpmHardLimitHyst=100 rpmSoftLimitTimingRetard=5 boostCutPressure=250 lambdaProtectionEnable=enabled lambdaProtectionMinLoad=60 lambdaProtectionMinTps=50 lambdaProtectionMinRpm=2500 lambdaProtectionTimeout=0.5 lambdaProtectionRestoreLoad=30 lambdaProtectionRestoreTps=20 lambdaProtectionRestoreRpm=2000 lambdaMaxDeviationTable=0.1x16 maxOilPressureTimeout=1.0 coastingFuelCutEnabled=enabled dfcoRetardDeg=5 dfcoRetardRampInTime=0.5
shot "Setup ▸ Limits and protection ▸ Limits and fallbacks" $I/limits-protection-limits.png
shot "Setup ▸ Limits and protection ▸ Lambda protection" $I/limits-protection-lambda.png
shot "Setup ▸ Limits and protection ▸ High oil pressure protection" $I/limits-protection-oil-high.png
shot "Fuel ▸ Deceleration fuel cutoff (DFCO)" $I/limits-protection-dfco.png
# then: useCltBasedRpmLimit=yes cltRevLimitRpm="4000 4500 5500 6800"
shot "Setup ▸ Limits and protection ▸ Limits and fallbacks" $I/limits-protection-clt-curve.png

# Live (ECU A on USB). tune: minOilPressureAfterStart=70 enableOilPressureProtect=yes minimumOilPressureTimeout=0.5
#   minimumOilPressureBins="700 1000 2000 3000 4000 5000 6000 7000" minimumOilPressureValues="100 110 140 170 200 230 250 250"
shot "Setup ▸ Limits and protection ▸ Low oil pressure protection" $I/limits-protection-oil-low.png
