#!/usr/bin/env bash
# Offline screenshots: TunerStudio on the bench display with the offline Proteus F7 project (no ECU).
# Set the tune with ts_tune_set.py (values below), restart TunerStudio (kill it so it does not save), then run.
set -euo pipefail
cd "$(dirname "$0")/../.."
I=documentation/docs/img/ts
shot() { python3 -I tools/shots/ts_menu_shot.py "$1" "$2" | awk "{print \$1}" | xargs -r -I{} env DISPLAY=:99 wmctrl -i -c {}; }
# lua-advanced-menu.png: Advanced menu with the Lua group hovered, cropped to the menus

# Live (ECU A on USB). tune: auxAnalogInputs1="Analog Volt 5" auxAnalogInputs2="Analog Volt 6" luaDigitalInputPins1="Digital 1"
#   luaDigitalInputPinModes1=PULLUP luaOutputPins1="Lowside 16" scriptSettingName1/2, scriptSetting1=2 scriptSetting2=2.5,
#   scriptTableName1="A/C bump", scriptTable1 rows "2 2 1.5 1 0 0 0 0", benchTestOnTime=10 benchTestOffTime=100
#   (names typed in the dialogs: the ECU keeps string constants as sent)
shot "Advanced ▸ Lua ▸ Lua Analog Inputs" $I/lua-analog-inputs.png
shot "Advanced ▸ Lua ▸ Lua Digital Inputs" $I/lua-digital-inputs.png
shot "Advanced ▸ Lua ▸ Lua Script PWM Outputs" $I/lua-outputs.png
shot "Advanced ▸ Lua ▸ Lua Buttons" $I/lua-buttons.png
shot "Advanced ▸ Lua Calibrations ▸ Lua Script Settings" $I/lua-script-settings.png
shot "Advanced ▸ Lua Calibrations ▸ Script Table #1" $I/lua-script-table1.png   # window widened to 460
# lua-bench-test-luaout.png: Controller ▸ Bench test cropped to the counters and the Lua Out Test column
