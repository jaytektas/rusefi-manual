# Diagnostics and error codes

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** rusEFI reports problems at three levels — a warning it can live with, a
> configuration error it refuses to run with, and a critical error that stops the engine — and shows
> each of them in TunerStudio and on the check engine light.

## Three kinds of problem

:material-circle:{ .level-basic } Basic

| Kind | What it means | What the engine does | Where you see it |
|---|---|---|---|
| **Warning** | Something is wrong but survivable: a sensor out of range, a trigger glitch, a CAN timeout | Keeps running; the affected function may fall back to a safe value | **Warning** indicator, the warning-code channels, the check engine light |
| **Configuration error** | The tune contradicts itself or is incomplete | The ECU stays connected so you can fix it, but the affected function refuses to work | **Config Error** indicator and its message in TunerStudio |
| **Critical error** | The firmware cannot safely drive the engine | Fuel and spark are cut, outputs are switched off, the error LED lights | **Config Error** indicator and its message; the ECU must be fixed and restarted |

<!-- src: firmware/controllers/core/error_handling.h (header comment: warning, configError, firmwareError and criticalError); firmware/controllers/core/error_handling.cpp (firmwareErrorV: getLimpManager()->fatalError, criticalShutdown, communicationLedPin) -->

A critical error keeps the first message it receives and ignores later ones, because the first one
is the cause. The message ends with the firmware version and board, so a screenshot of it is
useful in a bug report as it stands.
<!-- src: firmware/controllers/core/error_handling.cpp (firmwareErrorV: hasCriticalFirmwareErrorFlag latch, versionBuffer appended to criticalErrorMessageBuffer) -->

## Warnings and their codes

:material-circle:{ .level-basic } Basic

Every warning carries a code. Codes below 6000 follow the standard OBD-II numbering and are shown
with a **P** in front (P0107 is "MAP sensor low"); codes from 6000 up are rusEFI's own and are shown
with a **C**. The full list, with what each one means, is in
[Error codes](../part7/error-codes.md).
<!-- src: firmware/controllers/core/error_handling.cpp (warningVA: "P" or "C" prefix from ObdCodeIsCustom); firmware/controllers/algo/obd_error_codes.h (enum class ObdCode) -->

A warning is **active** for as long as it keeps happening, plus a hold time: **10 seconds** by
default (`warningPeriod`, which can be set from 3 to 60 seconds). A sensor that is unplugged keeps
its warning active the whole time; a single trigger glitch shows for ten seconds and then clears
itself. You do not need to clear warnings by hand.
<!-- src: firmware/controllers/gauges/malfunction_central.cpp (WarningCodeState::refresh and isWarningNow: maxI(3, warningPeriod)); firmware/controllers/algo/defaults/default_base_engine.cpp (warningPeriod = 10); firmware/integration/rusefi_config.txt (warningPeriod, 0 to 60 seconds) -->

The same warning repeating is not reported again and again: rusEFI only restarts its hold timer, so
the console log shows one line per new warning, not thousands.
<!-- src: firmware/controllers/core/error_handling.cpp (warningVA: known warning only resets its timer) -->

!!! tip "P0107 on a bench ECU is normal"
    With no MAP sensor connected the MAP input reads near 0 V and rusEFI reports **P0107**. On the
    bench, with nothing plugged in, expect a handful of sensor warnings. They mean "nothing is
    there", not "something is broken".

## The check engine light

:material-circle:{ .level-basic } Basic

If an output is assigned to the check engine light (**Setup ▸ Check Engine Settings**), rusEFI
drives it like a factory ECU:

- **Ignition on, engine stopped, no codes:** the light is on. This is the bulb check.
- **Engine running, no codes:** the light is off.
- **Any active code:** the light comes on steady for a moment, then **blinks the code out digit by
  digit**, each digit as one more blink than its value (so a 0 is one blink, a 1 two blinks), and
  moves on to the next active code.
- **Ignition off:** the light is off.

<!-- src: firmware/controllers/modules/malfunction_indicator/malfunction_indicator.cpp (MILController::onSlowCallback: lamp follows rpmCalculator.isStopped with no codes, startPrelude, startDigit pulses = digit + 1, lamp off without ignition); firmware/tunerstudio/tunerstudio.template.ini (malfunctionDialog) -->

**Test Check Engine** in the same dialog blinks the light 16 times so you can check the bulb and
the wiring; see the Bench testing chapter.

## What TunerStudio shows

:material-circle:{ .level-basic } Basic

The indicator row at the bottom of the TunerStudio dashboard has the lights you need:

- **Warning** — at least one warning is active now.
- **Check Engine** — at least one code is present (the same codes the lamp blinks).
- **Config Error** — despite its name, this lights for a critical error, a configuration error, or a
  warning message that wants your attention; its text appears in TunerStudio.

A fourth indicator, **Error report on SD**, is inside **Controller ▸ SD Card Logger**: it means a fault
report from an earlier crash or reboot is saved on the card.

<!-- src: firmware/console/status_loop.cpp (updateTunerStudioState: isWarnNow, checkEngine = hasErrorCodes, hasCriticalError from hasFirmwareError, hasConfigError and hasWarningMessage, hasFaultReportFile); firmware/tunerstudio/tunerstudio.template.ini ([FrontPage] indicators Config Error, Warning, Check Engine; sdCard indicator Error report on SD) -->

The First connection chapter goes through every indicator on the dashboard. To see *which* codes
are active, log or watch the warning-code channels, or read the console's message window, where
each new warning appears as a line starting with `WARNING:`.
<!-- src: firmware/controllers/core/error_handling.cpp (warningVA: efiPrintf "WARNING: %s") -->

## Fault reports on the SD card

:material-circle:{ .level-intermediate } Intermediate

When the ECU crashes or is reset by its watchdog, rusEFI keeps evidence in a small battery-backed
memory and, at the next start, writes it to the SD card as a file such as
`00042_fail_HardFault.txt`, and **Error report on SD** lights in the SD Card Logger dialog.
<!-- src: firmware/controllers/core/error_handling.cpp (firmwareErrorV: backup SRAM cookie and stack saved first); firmware/tunerstudio/tunerstudio.template.ini (help sdCardHelp: *_fail_*.txt reports) -->

To read the report:

1. **Controller ▸ SD Card Logger**: press **Mount to PC**. The card appears on your computer as a
   USB drive. (Or power the ECU off and use a card reader.)
2. Open the `*_fail_*.txt` files in a text editor.
3. Copy them somewhere safe, then attach them to a bug report on the rusEFI GitHub or forum, with
   your board, firmware version and what happened before.
4. To clear the reminder: eject the drive, press **Mount to ECU**, then **Remove all fail reports**.

<!-- src: firmware/tunerstudio/tunerstudio.template.ini (sdCard dialog: Mount to PC, Mount to ECU, Remove all fail reports; help sdCardHelp) -->

!!! warning "Removing a report does not fix anything"
    The report is the only record of what went wrong. Keep a copy before deleting it, and if new
    reports keep appearing, share those too.

## When the ECU will not run at all

:material-circle:{ .level-intermediate } Intermediate

A critical error at start-up, typically from a configuration the firmware cannot accept (a
thermistor calibration that fails its sanity check, two functions on one pin), stops the engine
before it starts but leaves TunerStudio connected. Read the message, fix the setting it names, burn,
and restart the ECU.

If the configuration itself is the problem and you cannot find the bad setting, the Recovering an
ECU chapter covers resetting to defaults and restoring a tune.

## Settings reference

:material-circle:{ .level-advanced } Advanced

**Setup ▸ Check Engine Settings**

--8<-- "reference/settings/_malfunctionDialog.table.md"

**Controller ▸ SD Card Logger**

--8<-- "reference/settings/_sdCard.table.md"
