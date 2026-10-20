# The rusEFI system at a glance

:material-circle:{ .level-basic } Basic

> **In one sentence:** a rusEFI installation is an ECU board running a firmware build made for that
> board, a bootloader that lets you replace that firmware, and two programs on your PC — TunerStudio
> and the rusEFI console — that both come with a matching set of files called a bundle.

## Overview

:material-circle:{ .level-basic } Basic

This chapter names every piece you will meet in the rest of the manual and shows how they fit
together. Nothing here changes your ECU; read it once, and come back to it when a later chapter
mentions a file or a program you do not recognise.

The pieces are:

| Piece | What it is | Where it lives |
|---|---|---|
| **Board** | The ECU hardware: a circuit board with a microcontroller, drivers for injectors, coils and motors, and connectors | in the car |
| **Firmware** | The rusEFI program that runs the engine, built for one board | in the ECU's flash memory |
| **Bootloader** | A small program at the start of the flash that can replace the firmware | in the ECU's flash memory |
| **Bundle** | A zip file with everything for one board: firmware files, the TunerStudio `.ini`, the console, drivers and scripts | on your PC |
| **TunerStudio** | The program you use to set up and tune the engine | on your PC |
| **rusEFI console** | The program you use to look after the ECU: firmware, recovery, diagnostics | on your PC |
| **Tune** | All your settings, saved as an `.msq` file | in the ECU, and as a file on your PC |
| **Datalog** | A recording of sensor readings and engine values over time, an `.mlg` file | on your PC, or on the ECU's SD card |
| **Simulator** | rusEFI running as a program on your PC, with no ECU | on your PC |

The *Your two tools* chapter explains which of the two PC programs to use for what.

## Concepts

:material-circle:{ .level-basic } Basic

<figure markdown>
  ![The pieces of a rusEFI system: on the PC, TunerStudio and the rusEFI console both connect to the ECU firmware over USB, one at a time; the console loads the update .srec through the OpenBLT bootloader or the full .bin through the chip's DFU mode; the simulator runs on the PC and is reached over TCP; the ECU's SD card appears on the PC as a USB drive holding .mlg datalogs, which MegaLogViewer opens; the bundle folder holds firmware files, the .ini, the console, drivers and scripts](../img/diagrams/rusefi-system-overview.svg)
  <figcaption>Figure 1 — The pieces and what talks to what. Blue is a program on your PC, orange is
  what runs in the ECU. Blue lines are live connections; orange lines are firmware being loaded.</figcaption>
</figure>

### The board

rusEFI runs on many boards. The repository's own board overview sorts the boards it builds firmware
for into three groups:

- **Universal boards** — general-purpose ECUs you wire to any engine: **Proteus** (F4, F7 and H7
  variants, including a transmission-controller variant), **microRusEFI** (F4 and F7), the
  **uaEFI** family (uaEFI, uaEFI Pro, uaEFI with the 121-pin automotive header, and super-uaEFI),
  and the **AlphaX** family (2chan, 4chan, 8chan, 4K GDI, Gold and Silver).
- **Vehicle-specific boards** — boards made to plug into one car's original wiring, for example
  the Mazda Miata NA and NB boards, Honda K series, GM E67, Hyundai/Kia, Nissan and VAG boards.
- **Development boards** — STM32 Discovery and Nucleo evaluation boards. They are listed as *not
  recommended as a real ECU*.
<!-- src: firmware/config/boards/readme-boards.md (Universal boards, Vehicle-specific boards, Development boards tables) -->

Most of these boards are built on the Hellen platform, whose files live under
`firmware/config/boards/hellen/`. This manual uses **Proteus F7** for every example and screenshot;
other boards are mentioned where they behave differently.
<!-- src: firmware/config/boards/readme-boards.md (hellen/ entries); firmware/config/boards/hellen/readme.md (Hellen-One platform) -->

!!! note "One firmware per board"
    The ECU's main serial port, the critical-error LED and a few other basic pins cannot be changed
    from TunerStudio. That is one reason each board has its own firmware build rather than one
    firmware for all boards.
    <!-- src: firmware/config/boards/readme.md (FAQ: how do I change Primary UART pins via TS) -->

### The firmware

The firmware is the program in the ECU that reads the sensors and fires the injectors and coils.
All boards share the same source code, but each board gets its own build, configured for that
board's microcontroller, pins and features. A build is identified by a short **board name** — for
Proteus with an STM32F7 microcontroller it is `proteus_f7`; the F4 version is `proteus_f4`, and
microRusEFI's builds are `mre_f4` and `mre_f7`.
<!-- src: firmware/config/boards/readme.md (one BOARD_NAME, several binaries from the same firmware files); firmware/config/boards/proteus/meta-info-proteus_f7.env (SHORT_BOARD_NAME); firmware/config/boards/proteus/meta-info-proteus_f4.env (SHORT_BOARD_NAME); firmware/config/boards/microrusefi/meta-info-mre_f7.env (SHORT_BOARD_NAME) -->

### The firmware signature, and why the .ini must match it

Your settings are stored in the ECU as one block of memory. Each setting sits at a fixed position in
that block, and the layout changes from one firmware version to the next as settings are added.
TunerStudio has no built-in knowledge of rusEFI: it learns the layout — every setting's position,
type, units, range, and the menus and dialogs to show it in — from a text file called the
**`.ini`** (for Proteus F7, `rusefi_proteus_f7.ini`). The `.ini` is generated from the same source
files as the firmware, so each firmware build has exactly one `.ini` that matches it.
<!-- src: firmware/tunerstudio/readme.md (rusefi*.ini generated from rusefi_config.txt, tunerstudio.template.ini and prepend.txt) -->

To tell the two apart, every build carries a **signature**, a line of text such as:

```
rusEFI master.2026.10.20.proteus_f7.1972639898
```

It is made of the name *rusEFI*, the source branch the firmware was built from, the build date,
the board name, and a **hash** — a number calculated from all the files that define the settings
layout. Change the layout and the hash changes.
<!-- src: firmware/gen_signature.sh (TS_SIGNATURE format: white label, branch, date, board, SIGNATURE_HASH); java_tools/configuration_definition/src/main/java/com/rusefi/ConfigDefinition.java (SIGNATURE_HASH from the CRC32 of the input files) -->

The firmware keeps its signature in `controllers/generated/signature_<board>.h` and the same text is
written into the `.ini` on its `signature=` line. When TunerStudio connects, it asks the ECU for its
signature and compares the answer with the `.ini` in your project. If they differ, TunerStudio
warns you about a signature mismatch: the `.ini` describes a different layout, and the values it
would show and write could land in the wrong places. The fix is always to use the `.ini` that came
in the same bundle as the firmware.
<!-- src: firmware/controllers/generated/signature_proteus_f7.h (TS_SIGNATURE, SIGNATURE_HASH); firmware/console/binary/signature.cpp (getTsSignature); firmware/console/binary/tunerstudio.cpp (handleQueryCommand: replies with the signature); java_console/io/src/main/java/com/rusefi/ts/TsProjectUpdater.java (TS complains about a signature mismatch after a firmware update) -->

### The bundle

A **bundle** is one zip file per board build, named `rusefi_bundle_<board>.zip` — for Proteus F7,
`rusefi_bundle_proteus_f7.zip`. Unzipped, it is a folder named `rusefi.snapshot.proteus_f7` for a
development (snapshot) build. It holds:

| In the bundle | What it is for |
|---|---|
| `rusefi_…_proteus_f7_…_update.srec` | The firmware alone, in the format the OpenBLT bootloader loads |
| `rusefi_…_proteus_f7_….bin` | A complete flash image — bootloader and firmware together — for DFU |
| `rusefi_proteus_f7.ini` | The TunerStudio definition that matches this firmware |
| `rusefi_updater.exe`, `rusefi_updater.sh` | Start the rusEFI console (Windows; Linux and macOS) |
| `readme.html` | A short page with links to the source code and documentation |
| `console/rusefi_console.jar` | The rusEFI console itself |
| `console/rusefi_simulator.exe` | The simulator (Windows build) |
| `console/rusefi_ts_plugin_launcher.jar` | A TunerStudio plugin that adds rusEFI tools inside TunerStudio |
| `console/STM32_Programmer_CLI/` | ST's programming tool, which the console uses for DFU |
| `drivers/silent_st_drivers2.exe` | USB drivers for Windows |
| `bin/` | Command-line scripts (for example `flash_dfu.sh`) |
| `bin/device/openblt_….bin` | The OpenBLT bootloader on its own |
<!-- src: firmware/bundle.mk (FOLDER, BUNDLE_FULL_NAME, SREC_NAME, BIN_TARGET, UPDATE_CONSOLE_FOLDER_SOURCES, CONSOLE_FOLDER_SOURCES, ROOT_FOLDER_SOURCES, ST_DRIVERS, BOOTLOADER_BIN_OUT, .h2d-sentinel: bootloader and firmware merged into the .bin); misc/console_launcher/rusefi_updater.sh (starts console/rusefi_console.jar); java_tools/ts_plugin_launcher/readme.md (TS plugin) -->

Keep the bundle folder together: the console finds the firmware files and the `.ini` next to
itself, and the firmware and `.ini` in one bundle always match each other.

!!! tip "The console keeps its bundle up to date"
    When it starts, the console can check the rusEFI build server for a newer bundle for your board
    and download it in the background (the **Auto-update Software** box on the **Device** tab turns
    this on and off). Holding Caps Lock while the console starts skips the update check.
    <!-- src: docs/frontend.md (Launcher#main runs Autoupdate.runSilentUpdate, autoupdate_bundle flag, Caps Lock skips the update); java_console/ui/src/main/java/com/rusefi/DevicePane.java (Auto-update Software checkbox) -->

### The bootloader (OpenBLT) and DFU

There are two ways to put new firmware into the ECU:

- **OpenBLT** is a bootloader: a small, separate program that rusEFI places at the start of the
  ECU's flash memory. It starts first at every power-up and hands over to the firmware. On request,
  it stays in charge instead and accepts new firmware — the `_update.srec` file — over USB (or CAN).
  Updating this way replaces the firmware but leaves the bootloader alone. Proteus F7 and most
  other current boards use OpenBLT.
- **DFU** (Device Firmware Update) is a mode built into the STM32 microcontroller itself, so it is
  there even if the flash is empty or the firmware is broken. DFU writes the complete `.bin` image,
  which contains the bootloader and the firmware together. It is the recovery path, and the only
  path on boards built without OpenBLT.
<!-- src: firmware/Makefile (USE_OPENBLT: reserve start of flash for OpenBLT); firmware/bundle.mk (USE_OPENBLT, SREC_TARGET, .h2d-sentinel: hex2dfu merges BOOTLOADER_HEX with the firmware into the .bin); firmware/bootloader/readme.md (ChibiOS with OpenBLT, firmware update via CAN); firmware/config/boards/proteus/meta-info-proteus_f7.env (USE_OPENBLT=yes); java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (STM32_Programmer_CLI) -->

You do not choose between them by hand in normal use: the console's **Update Firmware** button
picks the right method for the board it finds. The console can also switch a running ECU into
OpenBLT or DFU mode, and offers a full DFU erase for recovery. Flashing is covered step by step in
the *Flashing firmware* chapter.
<!-- src: java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (default mode for a live ECU: OPENBLT_AUTO, menu items DFU_SWITCH, OPENBLT_SWITCH, DFU_ERASE); java_console/ui/src/main/java/com/rusefi/maintenance/UpdateMode.java (display texts) -->

### TunerStudio, the project and the tune

**TunerStudio** is a tuning program made by EFI Analytics; rusEFI does not make it, but rusEFI
generates the `.ini` that TunerStudio needs, and this manual uses TunerStudio for every setup and
tuning step.
<!-- src: java_console/readme.md (TunerStudio is the primary calibration frontend) -->

TunerStudio organises its work in a **project**: a folder, normally under
`TunerStudioProjects` in your home folder, that holds:

- `projectCfg/mainController.ini` — the copy of the `.ini` this project uses;
- `projectCfg/project.properties` — the project's own settings, such as the connection;
- `CurrentTune.msq` — the tune, the last copy of your settings read from the ECU.
<!-- src: java_console/io/src/main/java/com/rusefi/ts/TsProjectCreator.java (project scaffold: projectCfg/mainController.ini, CurrentTune.msq, projectCfg/project.properties, ~/TunerStudioProjects) -->

An **`.msq` file** is a tune saved on your PC. You can keep as many as you like, compare them, and
load one into the ECU. The tune inside the ECU is the one the engine actually runs.

When you change a setting in TunerStudio, the change goes into the ECU's working memory straight
away and the engine uses it at once. It is only kept after a power-off once you **Burn**: burning
tells the ECU to write its settings to flash memory.
<!-- src: firmware/console/binary/tunerstudio.cpp (handleWriteChunkCommand writes to the working configuration, handleBurnCommand requests the flash write) -->

### The rusEFI console

The **rusEFI console** is rusEFI's own PC program. It updates and recovers firmware, and has the
diagnostic tools TunerStudio does not: the engine sniffer, the Lua script editor, the pinout
viewer, the knock analyzer, error-code history and an AI troubleshooting assistant. It is a Java
program (Java 11 or newer), started with `rusefi_updater.exe` on Windows or `rusefi_updater.sh` on
Linux and macOS.
<!-- src: java_console/readme.md (firmware update and advanced troubleshooting); docs/frontend.md (Launcher verifies Java 11+, launcher chain); misc/console_launcher/rusefi_updater.sh (Linux/macOS launcher) -->

### Datalogs and MegaLogViewer

A **datalog** records chosen engine values — RPM, MAP, lambda, timing and many more — many times a
second, so you can look at what happened after a drive. rusEFI's datalogs are `.mlg` files. There
are two ways to get one:

- **TunerStudio** records a datalog on your PC while it is connected.
- **The ECU** writes `.mlg` logs to its own SD card, on boards that have one, with no PC attached.
  When you then plug USB in, the ECU normally stops logging and shows the SD card to your PC as a
  USB drive, so you can copy the files off (a setting can make it keep logging instead).
<!-- src: firmware/console/binary_mlg_log/binary_mlg_logging.cpp (MLVLG file header); firmware/hw_layer/mmc_card.cpp (sdModeSelector: USB connected gives SD_MODE_PC mass storage, alwaysWriteSdCard forces ECU logging) -->

**MegaLogViewer**, also from EFI Analytics, opens `.mlg` files and plots the values against time.
Datalogging is covered in its own chapter.

### The simulator

The **simulator** is the rusEFI firmware built as a PC program, with simulated sensors and outputs.
It is a way to try rusEFI — explore the menus, try settings — without any hardware. On the
console's start screen, **Start Virtual Simulator** launches it (the Windows build is in the bundle)
and connects the console to it. The simulator listens on TCP port 29001; the simulator's notes say
you need a licensed (paid) version of TunerStudio to connect TunerStudio to it.
<!-- src: simulator/readme.md (run rusEFI on a PC, TCP ports 29001 and 29002, licensed TS needed, mocked sensors and outputs); java_console/ui/src/main/java/com/rusefi/SimulatorHelper.java (Start Virtual Simulator, rusefi_simulator.exe); firmware/bundle.mk (SIMULATOR_EXE in the console folder) -->

## Procedure: look inside a bundle

:material-circle:{ .level-basic } Basic

Installing the software is the next chapter but one; this short walk-through only shows you the
pieces described above in a real bundle.

1. **Unzip the bundle** for your board (for Proteus F7, `rusefi_bundle_proteus_f7.zip`) into a
   folder of its own. You get one folder, `rusefi.snapshot.proteus_f7`, laid out as in Figure 1's
   bundle box.
   <!-- src: firmware/bundle.mk (FOLDER = rusefi.<branch part>.<bundle name>, ZIP target) -->
2. **Find the two firmware files.** The file ending in `_update.srec` is what the console sends to
   the OpenBLT bootloader; the `.bin` is the complete image for DFU. You do not open either of
   them yourself — the console uses them.
3. **Open the `.ini` in a text editor** and search for `signature=`. This is the signature of the
   firmware in the same bundle. TunerStudio compares it with the ECU every time it connects.
   <!-- src: firmware/gen_signature.sh (TS_SIGNATURE); firmware/console/binary/tunerstudio.cpp (handleQueryCommand) -->
4. **Start the console** from the bundle folder. On a Proteus F7 bundle its start screen shows a
   blinking *WARNING: Proteus F7* notice about F7 boards needing a full erase in some cases — the
   *Flashing firmware* chapter explains when that applies.
   <!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (proteusWarning: WARNING: Proteus F7, F7-requires-full-erase) -->

=== "Windows"

    Double-click `rusefi_updater.exe`.

=== "Linux"

    Run `./rusefi_updater.sh` from the bundle folder. It changes into `console/` and starts
    `rusefi_console.jar` with Java.

=== "macOS"

    Run `./rusefi_updater.sh` from the bundle folder, as on Linux.

<!-- src: misc/console_launcher/rusefi_updater.sh (cd into console, java -jar rusefi_console.jar); docs/frontend.md (rusefi_updater.exe launch4j wrapper) -->

## Examples

:material-circle:{ .level-basic } Basic

### Example 1 — Reading a signature

The signature `rusEFI master.2026.10.20.proteus_f7.1972639898` reads as:

| Part | Value | Meaning |
|---|---|---|
| Name | `rusEFI` | the firmware's name |
| Branch | `master` | the source branch it was built from |
| Date | `2026.10.20` | the build date (UK time) |
| Board | `proteus_f7` | the board build — Proteus with an STM32F7 |
| Hash | `1972639898` | the settings layout; a different number means a different layout |

Two builds with the same hash have the same settings layout, even if they were built on different
days. A different hash means the `.ini` from one will not match the other.
<!-- src: firmware/gen_signature.sh (TZ=Europe/London date, branch name, SHORT_BOARD_NAME, SIGNATURE_HASH placeholder); java_tools/configuration_definition/src/main/java/com/rusefi/ConfigDefinition.java (FirmwareVersion from CRC32 of input files) -->

### Example 2 — Reading a firmware file name

The update file in a locally built Proteus F7 bundle is called
`rusefi_development_yymmdd_proteus_f7_nohash_local_update.srec`. Its parts are:

| Part | Here | In a build-server bundle |
|---|---|---|
| Branch | `development` | `development`, or the release name for a long-term-support build |
| Date | `yymmdd` | the build date |
| Bundle | `proteus_f7` | the board build |
| Signature hash | `nohash` | the same hash as in the signature |
| Source commit | `local` | the source commit the firmware was built from |

Because the hash is in the file name, the console can tell which `.ini` a firmware file belongs to.
<!-- src: firmware/bundle.mk (SREC_NAME, BIN_TARGET, BRANCH_REF_FOR_BUNDLE, BUNDLE_DATE default yymmdd, SIGNATURE_HASH default nohash, GITHUB_SHA default local, comment on pairing an update artifact with its .ini) -->

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic

| Symptom | Likely cause | Check |
|---|---|---|
| TunerStudio reports a signature mismatch when it connects | the project's `.ini` is from a different firmware build than the one in the ECU — typically after a firmware update | use the `.ini` from the bundle the firmware came from |
| The console says **Unsupported ECU** — *This console bundle does not support the detected controller* | the bundle is for a different board than the one plugged in | use the bundle for your board; the card's **Download compatible bundle** button fetches it where one is known |
| The console cannot connect while TunerStudio is open | only one program can use the ECU's USB port at a time | close TunerStudio (see *Your two tools*) |
| **Start Virtual Simulator** is missing; the start screen says `rusefi_simulator.exe not found` | the simulator file is not in the console folder (the bundle ships the Windows build) | start the console from an unchanged bundle, on Windows |
| Settings changed in TunerStudio are gone after a power-off | the changes were never burned | **Burn** after every change you want to keep |
<!-- src: java_console/io/src/main/java/com/rusefi/ts/TsProjectUpdater.java (signature mismatch after an update); java_console/ui/src/main/java/com/rusefi/UnsupportedEcuCardHost.java (Unsupported ECU card, Download compatible bundle); java_console/ui/src/main/java/com/rusefi/StartupFrame.java (tip: make sure you are disconnected from TunerStudio); java_console/ui/src/main/java/com/rusefi/SimulatorHelper.java (createSimulatorComponent: not found label); firmware/console/binary/tunerstudio.cpp (handleBurnCommand) -->

## Related

- *Your two tools* — which program to use for which job
- *Installing the software* — TunerStudio, the bundle and drivers, on Windows, Linux and macOS
- *Flashing firmware* — OpenBLT and DFU step by step
- *First connection* — creating the TunerStudio project
- Datalogging — TunerStudio logs, SD-card logs and MegaLogViewer
- [Read this first — safety and disclaimer](../safety.md)
