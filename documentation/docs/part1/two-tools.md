# Your two tools

:material-circle:{ .level-basic } Basic

> **In one sentence:** if you're changing how the engine runs, use TunerStudio; if you're looking
> after the ECU itself, use the rusEFI console.

## Overview

:material-circle:{ .level-basic } Basic

You will use two programs on your PC with rusEFI. Both connect to the same ECU over the same USB
cable, and some of what they show overlaps, so it is worth knowing from the start which one each
job belongs to. rusEFI's own description of the console puts it the same way: TunerStudio is the
main program for calibration, and the console is the second program, for firmware updates and
advanced troubleshooting.
<!-- src: java_console/readme.md (TunerStudio is the primary calibration frontend, console for firmware update and advanced troubleshooting) -->

| | TunerStudio | rusEFI console |
|---|---|---|
| **Use it for** | setting up and tuning the engine | looking after the ECU |
| **Made by** | EFI Analytics, for many ECUs; rusEFI supplies the `.ini` | rusEFI, in every bundle |
| **Typical jobs** | sensors, injectors, ignition, fuel and timing tables, idle, boost, datalogging, gauges | firmware update and recovery, engine sniffer, Lua scripts, pinout, knock analyzer, error codes, AI troubleshooting |
| **In this manual** | every setup and tuning procedure | only what TunerStudio cannot do |

## Concepts

:material-circle:{ .level-basic } Basic

### The rule

> **If you're changing how the engine runs, use TunerStudio. If you're looking after the ECU
> itself, use the console.**

*Changing how the engine runs* means anything that ends in a setting being changed and burned:
choosing a trigger, calibrating a sensor, setting injector data, editing a fuel or timing table,
setting up idle, boost or launch control, recording a datalog to tune from. All of it is done in
TunerStudio, and every setup and tuning chapter in this manual is written and illustrated in
TunerStudio.

*Looking after the ECU* means the jobs around the firmware and the hardware:

- **Updating the firmware**, and **recovering** an ECU whose firmware does not start.
- **Watching injection and spark events** with the engine sniffer.
- **Writing and loading Lua scripts.**
- **Checking the pinout**: which pin on which connector does what, and what your tune has assigned
  to it.
- **Looking at knock** with the knock analyzer's spectrogram.
- **Reading the error-code history.**
- **Asking the AI troubleshooting assistant** about a problem.

Getting logs off the ECU's SD card needs neither program: with USB plugged in, the ECU shows its SD
card to the PC as a USB drive (see *The rusEFI system at a glance*).
<!-- src: java_console/ui/src/main/java/com/rusefi/ConsoleUI.java (tabs: Lua Scripting, Engine Sniffer, Knock Analyzer, Pinout, Device, OBD Codes, AI Troubleshooting); firmware/hw_layer/mmc_card.cpp (sdModeSelector: SD_MODE_PC when USB is connected) -->

Wherever a step in this manual is done in the console, its first line says **"This is done in the
rusEFI console"**. A job is never described in both programs.

### One program at a time

The ECU's USB connection appears on your PC as a serial port, and only one program can have a
serial port open at a time. So TunerStudio and the console cannot both be connected to the ECU at
once: close one before you connect the other. The console says as much in its own tips — *Make sure
you are disconnected from TunerStudio* — and its **Open TunerStudio** button starts TunerStudio and
closes the console *so the serial port is released*.
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (connect card tips: Make sure you are disconnected from TunerStudio, Open TunerStudio button tooltip: close this console so the serial port is released) -->

On Windows, the console also checks at start-up whether TunerStudio is running. If it is, the
console shows *TunerStudio is running. Do you want to close it?* with **Yes** and **No**, and two
boxes: **Auto-close TS** (close it without asking next time) and **Check if TS is running** (untick
to stop the check).
<!-- src: java_console/ui/src/main/java/com/rusefi/tools/TunerStudioHelper.java (checkTunerStudio, isTsRunning: Windows only, attemptClosingTunerStudio); java_console/ui/src/main/java/com/rusefi/ui/TunerStudioPanel.java (labels and checkboxes) -->

!!! warning "Never interrupt a firmware update"
    Do not close the console, start TunerStudio or unplug the USB cable while the console is
    updating firmware. The console locks its other tabs while an update runs; wait until it reports
    that the update has finished.
    <!-- src: java_console/ui/src/main/java/com/rusefi/ConsoleUI.java (setFirmwareUpdateInProgress while SessionState.FLASHING); docs/frontend.md (startup tabs disabled while a firmware operation is in progress) -->

### Tuning in the console

The console has its own **Tuning** tab and a setup wizard, and it is gaining tuning features. This
edition of the manual documents all setup and tuning in TunerStudio. The console's tuning features
are described only in the Part VII appendix *Tuning in the rusEFI console*, and no other chapter
uses them.
<!-- src: java_console/ui/src/main/java/com/rusefi/ConsoleUI.java (Tuning tab, WizardContainer) -->

## TunerStudio

:material-circle:{ .level-basic } Basic

TunerStudio shows rusEFI's menus, dialogs, tables and gauges exactly as the `.ini` in your project
describes them, so what you see depends on the firmware build. Menus in this manual are written
**Menu ▸ Dialog**, for example **Sensors ▸ TPS**, and settings by their label as TunerStudio shows
it. Installing TunerStudio and creating a project are covered in *Installing the software* and
*First connection*.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (menuDialog = main, top-level menus); firmware/tunerstudio/readme.md (ini files configure TunerStudio for a specific board) -->

<!-- shot: img/ts/two-tools-ts-main.png | TunerStudio main window | Proteus F7 project connected to the ECU on 12 V, engine stopped, front page gauges and the top-level menu bar visible; title bar must show an official build (rusEFI v<date>@<hash>) | Figure 1 — TunerStudio connected to a Proteus F7: the menus across the top hold every setup and tuning dialog in this manual. -->

## The rusEFI console

:material-circle:{ .level-basic } Basic

### The start screen

When the console starts, it opens a start screen with three tabs. It remembers which tab you used
last.
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (outerTabs: Update Firmware, Manage Tunes, Connect, STARTUP_TAB_INDEX) -->

| Tab | What it is for |
|---|---|
| **Update Firmware** | Shows the ECU the console has found and the firmware it would load, with the **Update Firmware** button and a **Migrate Settings** option that carries your settings over to the new firmware. Used in the *Flashing firmware* chapter. |
| **Manage Tunes** | Loads and saves tune (`.msq`) files with the console. This manual saves and loads tunes in TunerStudio, so this tab is not used here. |
| **Connect** | *Connect to your ECU*: the **Device** list of detected ports, the **Connect** and **Open TunerStudio** buttons, **Remember last used port**, a list of things to check when no ECU is found, and **Start Virtual Simulator**. |
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (firmwareTabPanel: selector, update and rollback buttons, getMigrateSettings, and buildConnectCard: title, subtitle, Device label, Connect, Open TunerStudio, Remember last used port, tips, simulator row); java_console/ui/src/main/java/com/rusefi/ui/basic/TuneManagementTab.java (Load Tune File, .msq filter); java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (Update Firmware button) -->

The Connect tab tells you to plug the ECU in by USB: it is detected automatically, and when exactly
one ECU is found the console usually connects to it by itself. If nothing is found, the tab lists
what to check: the cables, the drivers, that the blue LED on the ECU is blinking, and that
TunerStudio is not connected.
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (subtitle: Plug your ECU in by USB. It is detected automatically, REVEAL_CONTROLS_DELAY_MS single-ECU auto-connect, tips list, NO_PORTS_FOUND) -->

<!-- shot: img/console/two-tools-startup-connect.png | rusEFI console start screen ▸ Connect | Proteus F7 bundle, ECU unplugged so the full card shows: Connect to your ECU title, Device list, Connect and Open TunerStudio buttons, tips list and Start Virtual Simulator; the blinking WARNING: Proteus F7 banner captured in its visible phase | Figure 2 — The console's start screen, Connect tab. -->

<!-- shot: img/console/two-tools-startup-update.png | rusEFI console start screen ▸ Update Firmware | Proteus F7 plugged in by USB and detected, nothing started; Update Firmware button and Migrate Settings visible | Figure 3 — The Update Firmware tab, with a Proteus F7 detected. -->

### The main window

Once connected, the console opens its main window. Along the top is a row of tabs; on the right of
the row, an icon shows the connection state (it changes colour when the ECU is in DFU or OpenBLT
bootloader mode).
<!-- src: java_console/ui/src/main/java/com/rusefi/ConsoleUI.java (TabbedPanel, ConnectionStatusIcon in the corner panel, bootloaderMode client property) -->

<!-- shot: img/console/two-tools-main-window.png | rusEFI console main window ▸ Gauges | connected to Proteus F7 on 12 V, engine stopped, default gauge grid, whole tab row and connection icon visible | Figure 4 — The console's main window, Gauges tab, with the full row of tabs. -->

The tabs, in the order the console shows them:

| Tab | What it does | Covered in |
|---|---|---|
| **Gauges** | A grid of live gauges. **Add Gauge** adds one; **Layout** switches between a fixed grid and a free layout. | — |
| **Messages** | Text messages from the ECU and from the console itself. | Diagnostics |
| **Lua Scripting** | The Lua script editor. **Write to ECU** sends the script into the ECU's working memory; **Burn to ECU** then stores it in flash so it survives a power-off. | Lua scripting |
| **Engine Sniffer** | Charts of spark and injection events, so you can see when each coil and injector fires. | Diagnostics |
| **Tuning** | The console's tuning screens — not used in this manual (see *Tuning in the console* above). | Part VII appendix |
| **Knock Analyzer** | A knock spectrogram: press **Start**, run the engine, and see the frequencies the knock sensor picks up. | Knock control |
| **Pinout** | The connected board's connectors, as pictures with every pin marked, and a table of each pin's function and what your tune uses it for. | Part II |
| **Device** | Firmware update and recovery for the connected ECU, with the **Auto-update Software** and **Migrate Settings** options. | Flashing firmware |
| **OBD Codes** | The last error code and the history of recent codes reported by the ECU. **Clear history** empties the list. | Diagnostics |
| **AI Troubleshooting** | An assistant that looks at the connected ECU and answers questions about a problem. | Diagnostics |
<!-- src: java_console/ui/src/main/java/com/rusefi/ConsoleUI.java (tab order: Gauges, Messages, Lua Scripting, Engine Sniffer, Tuning, Knock Analyzer, Pinout, Manage Tunes, Device, OBD Codes, AI Troubleshooting); java_console/ui/src/main/java/com/rusefi/ui/GaugesPanel.java (Add Gauge, Layout); java_console/ui/src/main/java/com/rusefi/ui/MessagesPane.java (top level tab); java_console/ui/src/main/java/com/rusefi/ui/lua/LuaScriptPanel.java (Write to ECU, Burn to ECU); java_console/ui/src/main/java/com/rusefi/ui/engine/EngineSnifferPanel.java (spark and injection charts); java_console/ui/src/main/java/com/rusefi/ui/KnockPane.java (knock spectrogram, Start); java_console/ui/src/main/java/com/rusefi/ui/PinoutPane.java (connector images, pin table, tune assignments); java_console/ui/src/main/java/com/rusefi/DevicePane.java (Auto-update Software, Migrate Settings, DFU and OpenBLT); java_console/ui/src/main/java/com/rusefi/ui/obd/ObdCodesPane.java (lastErrorCode, recentErrorCode, Clear history); java_console/ui/src/main/java/com/rusefi/ui/llm/LLMTab.java (AI troubleshooting) -->

A few tabs only appear in some situations:

- **SLCAN Sniffer** appears when the connected firmware's `.ini` says it supports CAN sniffing.
- **Manage Tunes** appears in the main window only when the bundle is set up with a list of tunes
  to download; it is not there by default.
- **OBD Codes** and **AI Troubleshooting** need a live ECU connection.
<!-- src: java_console/ui/src/main/java/com/rusefi/ui/SlcanTabController.java (SLCAN Sniffer tab); java_console/ui/src/main/java/com/rusefi/ui/SlcanTab.java (shown when the connected INI advertises CAN sniffing); java_console/ui/src/main/java/com/rusefi/ui/basic/TuneManagementTab.java (getTunesManifestUrl: tunes_manifest property); java_console/shared_io/src/main/resources/shared_io.properties (no tunes_manifest by default); java_console/ui/src/main/java/com/rusefi/ConsoleUI.java (OBD Codes and AI Troubleshooting only when not offline) -->

!!! note "What the AI assistant sends"
    **AI Troubleshooting** works through a ChatGPT account you sign in to with **Continue with
    ChatGPT**. Its access to the ECU is read-only, but your questions and the ECU data it looks at
    — which can include tune values and your Lua script — are sent to OpenAI.
    <!-- src: docs/llm-troubleshooting.md (ChatGPT sign-in, read-only ECU access, what is sent to OpenAI); java_console/ui/src/main/java/com/rusefi/ui/llm/LLMTab.java (Continue with ChatGPT) -->

## Procedure: switching between the two tools

:material-circle:{ .level-basic } Basic

Because only one program can be connected at a time, every switch follows the same pattern: let go
of the ECU in one program, then connect with the other.

### From the console to TunerStudio

1. Finish what you were doing in the console. If a firmware update is running, wait for it to
   finish.
2. On the start screen's **Connect** tab, press **Open TunerStudio**. The console starts
   TunerStudio and closes itself. (Or simply close the console and start TunerStudio yourself.)
   <!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (openTunerStudio action: launchTunerStudio, then close the frame); java_console/ui/src/main/java/com/rusefi/tools/TunerStudioHelper.java (launchTunerStudio: saved path, common install paths, else asks) -->
3. Open your project in TunerStudio. It connects to the ECU.

The first time you press **Open TunerStudio**, the console may ask you where TunerStudio is
installed if it cannot find it; it remembers the answer.
<!-- src: java_console/ui/src/main/java/com/rusefi/tools/TunerStudioHelper.java (resolveTunerStudioExecutable, TS_EXECUTABLE_PATH persisted) -->

### From TunerStudio to the console

1. **Burn** any changes you want to keep, then close TunerStudio.
2. Start the console (`rusefi_updater.exe` on Windows, `rusefi_updater.sh` on Linux and macOS).
3. If TunerStudio is still running on Windows, the console asks whether to close it: answer
   **Yes**.
4. On the **Connect** tab, wait for the ECU to be detected, then press **Connect** if the console
   has not already connected by itself.
<!-- src: java_console/ui/src/main/java/com/rusefi/ui/TunerStudioPanel.java (Yes closes TunerStudio); java_console/ui/src/main/java/com/rusefi/StartupFrame.java (Connect button) -->

## Examples

:material-circle:{ .level-basic } Basic

### Example 1 — Which tool for which job

| Job | Tool | Why |
|---|---|---|
| Set the injector flow rate | TunerStudio | changes how the engine runs |
| Calibrate the throttle | TunerStudio | changes how the engine runs (see [Electronic throttle](../part3/electronic-throttle.md)) |
| Record a datalog while tuning | TunerStudio | part of tuning |
| Update to a new firmware | console | looks after the ECU |
| Revive an ECU that does not start after a failed update | console (DFU) | recovery |
| Check that each coil fires at the right time | console (Engine Sniffer) | TunerStudio has no engine sniffer |
| Find which connector pin is *Analog Volt 2* | console (Pinout) | TunerStudio has no pinout view |
| Write a Lua script | console (Lua Scripting) | the console's editor writes and burns the script |
| See which error codes the ECU has reported | console (OBD Codes) | the console keeps the history |

### Example 2 — A firmware update in the middle of tuning

You are tuning in TunerStudio and want to update to a newer firmware:

1. In TunerStudio, **Burn**, save your tune to an `.msq` file as a backup, and close TunerStudio.
2. In the console, update the firmware (this is done in the rusEFI console — see the *Flashing
   firmware* chapter). Leave **Migrate Settings** ticked so your settings are carried over.
3. Close the console and open TunerStudio. The new firmware has a new signature, so TunerStudio
   will tell you the project's `.ini` no longer matches; give the project the `.ini` from the new
   bundle (*First connection* shows how).
<!-- src: java_console/ui/src/main/java/com/rusefi/DevicePane.java (Migrate Settings checkbox, default ticked); java_console/io/src/main/java/com/rusefi/ts/TsProjectUpdater.java (after a migration, the TS project .ini no longer matches) -->

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic

| Symptom | Likely cause | Check |
|---|---|---|
| The console finds no ECU, or TunerStudio cannot open the port | the other program is still connected | close the other program; on Windows, let the console close TunerStudio |
| The console keeps closing TunerStudio without asking | **Auto-close TS** was ticked | untick it in the *TunerStudio is running* prompt, or untick **Check if TS is running** |
| **Open TunerStudio** asks where TunerStudio is | the console could not find the program | point it at the TunerStudio program file once |
| A tab described here is missing | some tabs appear only with a live connection or on some boards | connect to the ECU; see the list under *The main window* |
| The console shows **Unsupported ECU** and blocks the connection | the bundle is for a different board | use the bundle for your board (see *The rusEFI system at a glance*) |
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (tips, Open TunerStudio); java_console/ui/src/main/java/com/rusefi/ui/TunerStudioPanel.java (Auto-close TS, Check if TS is running); java_console/ui/src/main/java/com/rusefi/tools/TunerStudioHelper.java (resolveTunerStudioExecutable); java_console/ui/src/main/java/com/rusefi/UnsupportedEcuCardHost.java (Unsupported ECU, CONNECTION BLOCKED) -->

## Related

- *The rusEFI system at a glance* — the firmware, the bundle, the bootloader and the files
- *Installing the software* — getting TunerStudio and the console onto your PC
- *Flashing firmware* — the console's Update Firmware and Device tabs in use
- *First connection* — creating your TunerStudio project
- Part VII appendix — *Tuning in the rusEFI console*
- [Electronic throttle](../part3/electronic-throttle.md) — a full setup chapter done in TunerStudio
