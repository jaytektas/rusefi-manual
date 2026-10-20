# Flashing firmware

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** flashing writes a new rusEFI firmware into the ECU's processor — normally with
> one button in the rusEFI console, which saves your tune first and puts it back afterwards — and it
> leaves your settings where they are.

## Overview

:material-circle:{ .level-basic } Basic

The ECU's processor (on a Proteus F7, an STM32F7 microcontroller) keeps its program in **flash
memory**, the same kind of memory as a USB stick: it keeps its contents with the power off and can be
rewritten. **Flashing** means writing a new program — a new rusEFI **firmware** — into that memory.
You flash when you set up a new ECU, when you want a newer rusEFI with new features or fixes, and when
you recover an ECU whose firmware is damaged.

Everything you need comes in the **rusEFI bundle** for your board: a zip with the firmware files, the
matching TunerStudio `.ini`, the rusEFI console and the flashing tools. For a Proteus F7 the bundle
folder is called `rusefi.snapshot.proteus_f7` (or `rusefi.<release>.proteus_f7` for a release).
Installing it is covered in the chapter *Installing the software*.
<!-- src: firmware/bundle.mk (FOLDER, BUNDLE_FILES, CONSOLE_FOLDER_SOURCES, ST_DRIVERS) -->

There are three ways to get firmware into the ECU, and this chapter covers all three:

| Way | What you need | When to use it |
|---|---|---|
| **OpenBLT update** from the rusEFI console | a USB cable | every normal update |
| **DFU** (the STM32's own USB bootloader) | a USB cable | a new or blank ECU, refreshing the bootloader, recovery |
| **ST-Link** (a debug probe) | an ST-Link probe on the board's debug connector | last resort, when nothing answers on USB |

Flashing is done in the rusEFI console, not in TunerStudio: TunerStudio cannot write firmware.
<!-- src: java_console/ui/src/main/java/com/rusefi/maintenance/UpdateMode.java (DFU_AUTO, OPENBLT_AUTO, ST_LINK); java_console/ui/src/main/java/com/rusefi/StartupFrame.java (Update Firmware tab) -->

## Concepts

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

### Two programs in one ECU: the bootloader and the firmware

The flash memory of a Proteus F7 holds two programs, one after the other:

- the **OpenBLT bootloader**, a small program (32 KB) at the very start of flash. It runs first at
  every power-on, checks that the firmware is intact, and starts it. It can also receive a new
  firmware over USB without any other tool;
- the **rusEFI firmware** itself, which starts right after the bootloader, at address `0x0800 8000`.

Further up, in their own area, are your **settings** (the tune) — two copies, so that one damaged copy
can be replaced by the other. They are written by the firmware itself when you burn in TunerStudio,
not by flashing.

Separately from all of this, every STM32 has a **DFU bootloader** built into read-only memory by the
chip maker. It cannot be erased, so it is always there as a way in, even when everything in flash is
broken.
<!-- src: firmware/hw_layer/ports/stm32/stm32f7/STM32F7.ld (bootloader_size 32k, flash_start, image_size); firmware/bootloader/openblt_chibios/openblt_flash.cpp (FlashGetUserProgOffset, FlashVerifyChecksum); firmware/hw_layer/ports/stm32/stm32f7/mpu_util.cpp (getFlashAddrFirstCopy, getFlashAddrSecondCopy); firmware/hw_layer/ports/stm32/stm32f7/dfu_init.h (system memory 0x1FF00000); firmware/controllers/flash_main.cpp (writeToFlashNowImpl: two copies) -->

<figure markdown>
  ![Flash memory map of a Proteus F7: STM32 DFU bootloader in ROM at 0x1FF0 0000; in internal flash the 32 KB OpenBLT bootloader at 0x0800 0000 with its BL10 version marker at 0x0800 0024, the rusEFI firmware from 0x0800 8000, unused space, and two copies of the settings (0x0810 0000 on a 2 MB chip). The full .bin image covers bootloader and firmware and is written by DFU or ST-Link; the _update.srec covers only the firmware and is written by OpenBLT; settings are kept by both; a full DFU erase wipes everything](../img/diagrams/flashing-firmware-flash-layout.svg)
  <figcaption>Figure 1 — What is where in a Proteus F7's flash, and which image writes which part.
  Blue is the file you choose, orange the path that writes it, green your settings, red the one
  operation that erases them.</figcaption>
</figure>

Where the settings live depends on the chip: on an STM32F7 with 2 MB of flash they start at
`0x0810 0000`; on a 1 MB part they sit at `0x080C 0000` and `0x080E 0000`. Either way they are above
the firmware's area, which the linker limits to 736 KB.
<!-- src: firmware/hw_layer/ports/stm32/stm32f7/mpu_util.cpp (getFlashAddrFirstCopy, getFlashAddrSecondCopy: DualBank1MB, SingleBank2MB, DualBank2MB); firmware/hw_layer/ports/stm32/stm32f7/STM32F7.ld (flash_size 768k, image_size) -->

### The two firmware files in the bundle

A Proteus F7 bundle holds the firmware twice, in two forms. Their names carry the branch, date, board,
a configuration hash and the source commit, for example
`rusefi_development_<date>_proteus_f7_<hash>_<commit>.bin`:

| File | Contains | Starts at | Written by | Use it for |
|---|---|---|---|---|
| `rusefi_…_proteus_f7_….bin` — the **full image** | OpenBLT bootloader **and** firmware, merged | `0x0800 0000` | DFU or ST-Link | a blank ECU, a new bootloader, recovery |
| `rusefi_…_update.srec` — the **update image** | firmware only | `0x0800 8000` | OpenBLT | normal updates |

The bundle also has the bootloader on its own (`bin/device/openblt_….bin`), which the console uses
for its **Install OpenBLT** option.
<!-- src: firmware/bundle.mk (BIN_TARGET, SREC_NAME, SREC_TARGET, BOOTLOADER_BIN_OUT, .h2d-sentinel: hex2dfu merges BOOTLOADER_HEX and the firmware hex; rusefi.srec rule --change-addresses HEX_BASE_ADDRESS) -->

The configuration hash in the name is the same one TunerStudio sees in the firmware's signature, so
the `.bin`, the `.srec` and the `.ini` of one bundle belong together. Use the `.ini` from the same
bundle as the firmware you flash.
<!-- src: firmware/bundle.mk (SIGNATURE_HASH comment: pairs an update artifact with the exact .ini) -->

The update image can never damage the bootloader: OpenBLT refuses to erase or write anything below
the firmware's start address. That is why the normal update path is safe to repeat — if it is
interrupted, OpenBLT is still there to try again.
<!-- src: firmware/bootloader/openblt_chibios/openblt_flash.cpp (FlashWrite, FlashErase: "don't allow overwriting the bootloader") -->

### What happens to your settings

Flashing firmware writes the firmware area and nothing else, so **the settings stay in flash**. When
the new firmware starts, it reads them and checks three things: the stored checksum (CRC), a
**configuration version number**, and the size of the stored settings. Then:

| What the firmware finds | What it does |
|---|---|
| CRC, version and size all match | uses your settings ("Read valid configuration from flash!") |
| a different version number or size | resets everything to factory defaults, but **keeps the engine type** |
| a bad CRC, or blank flash | resets everything to factory defaults (and raises a *flash CRC failed* warning for a bad CRC) |
<!-- src: firmware/controllers/flash_main.cpp (readConfiguration, validatePersistentState, readFromFlash: CrcFailed, IncompatibleVersion, NotFound) -->

The version number (`FLASH_DATA_VERSION`) is changed by the rusEFI developers whenever they make an
incompatible change to the settings layout. Settings survive an update as long as it has not changed
and the size is the same.
<!-- src: firmware/integration/rusefi_config.txt (FLASH_DATA_VERSION comment: "update this string to the current date") -->

!!! warning "Same size is not the same layout"
    The check does not look at what each byte means. If a new firmware rearranged the settings without
    changing their size or the version number — or if you flash firmware for another board whose
    settings happen to be the same size — the old bytes are loaded into the wrong places, and some
    settings come up with nonsense values. This is why you save your tune before every flash, and why
    the console's update converts the tune by name (next section) instead of relying on the bytes in
    flash.
    <!-- src: firmware/controllers/flash_main.cpp (validatePersistentState: only crc, version and size are compared); firmware/controllers/algo/persistent_configuration.h (persistent_config_container_s: version, size, crc) -->

### What the console does around a flash: backup and Migrate Settings

When you update a running ECU from the console, it does more than write the firmware:

1. It reads the whole tune from the ECU and saves it in the bundle's `console/state/` folder, as
   `<date>-<time>_backup_from_ecu.msq` together with the `.ini` it was read with.
2. It flashes the firmware.
3. It waits for the ECU to come back, and reads the tune the new firmware is now holding.
4. With **Migrate Settings** ticked (the default), it takes your old values, matches them **by name**
   to the new firmware's settings — converting where a setting changed — and writes the result to
   the ECU. Fields that cannot be carried over are listed, and you choose whether to keep the rest or
   start from defaults.

Each stage leaves its own files in `console/state/` (`after_firmware_update`, `merged_to_write`,
`merged_from_ecu`), so you can always go back to the tune as it was before the flash.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/CalibrationsHelper.java (updateFirmwareAndRestorePreviousCalibrations, mergeCalibrationsWithPartialFailure, backUpCalibrationsInfo, getFileNameWithoutExtension, DATE_FORMAT); java_console/io/src/main/java/com/rusefi/binaryprotocol/BinaryProtocolLocalCache.java (STATE_FOLDER); java_console/ui/src/main/java/com/rusefi/ui/basic/StartupUpdateActions.java (migrateSettings default selected) -->

If the board is already sitting in a bootloader (so there is no live ECU to read first), the console
restores the last tune it read from an ECU in the same session, if it has one.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/CalibrationsHelper.java (restorePreviousCalibrationsAfterManualFlash, lastEcuCalibrations) -->

!!! tip "Save your tune in TunerStudio as well"
    The console's backup is good, but keep your own: in TunerStudio, **File ▸ Save Tune As** before
    every flash. That `.msq` is the copy you know where to find.

## Procedure

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

!!! danger "Never interrupt a flash"
    Do not unplug the USB cable, switch off the ECU's power, or close the console while firmware is
    being written. The engine must be stopped. An interrupted OpenBLT update leaves the ECU in its
    bootloader, from where you simply flash again; an interrupted DFU or ST-Link write can leave
    *both* the bootloader and the firmware broken, and then only the recovery methods in the chapter
    *Recovering an ECU* will bring it back. The console asks for confirmation if you try to close it
    during an update.
    <!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (windowClosing: "A firmware update is still in progress"); firmware/bootloader/openblt_chibios/openblt_flash.cpp (FlashVerifyChecksum: half-written image); firmware/ext/openblt/Target/Source/ARMCM7_STM32F7/cpu.c (CpuStartUserProgram) -->

Before any of the methods:

- Save your tune in TunerStudio (**File ▸ Save Tune As**).
- **Close TunerStudio** or disconnect it from the ECU. The ECU's USB port can only be used by one
  program at a time; the console says *"Make sure you are disconnected from TunerStudio"* when it sees
  the port but cannot talk to the ECU.
- Unzip the bundle for your board and start the console from it: `rusefi_updater.exe` on Windows,
  `rusefi_updater.sh` on Linux and macOS.
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (noPortsMessage "Make sure you are disconnected from TunerStudio", openTunerStudio tooltip "so the serial port is released"); firmware/bundle.mk (ROOT_FOLDER_SOURCES rusefi_updater.exe, rusefi_updater.sh) -->

### Method A · Update with the rusEFI console (OpenBLT)

This is done in the rusEFI console. It is the method for every normal update of a working ECU.

1. Connect the ECU by USB and start the console. The start window opens with three tabs:
   **Update Firmware**, **Manage Tunes** and **Connect**.
2. Open the **Update Firmware** tab. When the console has found the ECU it shows the **Update
   Firmware** button.
3. Leave **Migrate Settings** ticked.
4. Press **Update Firmware**. The console backs up your tune, sends the ECU into its OpenBLT
   bootloader, writes the update image, waits for the ECU to restart and puts your tune back. The
   log below the button shows each step; the progress bar shows the write.
5. When the log reports success and the ECU is connected again, close the console and open
   TunerStudio with the `.ini` from the same bundle.
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (outerTabs: Update Firmware, Manage Tunes, Connect; firmwareTabPanel); java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (mainButtonModeFor: OPENBLT_AUTO with a live connection, button text "Update Firmware"); java_console/ecu_shared/src/main/java/com/rusefi/maintenance/FirmwareOperations.java (OpenBLT update via updateFirmwareAndRestorePreviousCalibrations) -->

<!-- shot: img/console/flashing-update-firmware-tab.png | rusEFI console start window ▸ Update Firmware tab | Proteus F7 connected on USB and detected; Update Firmware button enabled; Migrate Settings ticked; annotate 1 = tab, 2 = Migrate Settings, 3 = Update Firmware button, 4 = status log | Figure 2 — The console's Update Firmware tab with an ECU detected. -->

<!-- shot: img/console/flashing-update-done.png | rusEFI console start window ▸ Update Firmware tab | after a successful OpenBLT update: log shows the backup to state/…_backup_from_ecu, the write, "ECU is found on port … after firmware update", the merge and write of the tune | Figure 3 — The log of a successful update: backup, write, reconnect, tune restored. -->

The arrow beside the button opens the other ways to flash. Which entries appear depends on what the
console has detected and on your operating system:

| Entry | What it does |
|---|---|
| **Auto DFU Update** | reboots the ECU into the STM32 DFU bootloader and writes the full image, with the same backup and restore as above (Windows, Linux) |
| **Switch to DFU Mode** | only reboots the ECU into DFU |
| **Manual DFU Update** | writes the full image to a board already in DFU |
| **Pick Custom File [DFU]** | writes a `.bin` you choose to a board in DFU |
| **Install OpenBLT** | writes the bootloader alone, to a board in DFU |
| **Full DFU Erase** | erases the whole flash — firmware, bootloader **and settings** |
| **Switch to OpenBLT Mode** | only reboots the ECU into OpenBLT |
| **Manual OpenBLT Update** | writes the update image to a board already in OpenBLT |
| **ST-LINK Update** | writes with an ST-Link probe (Windows only) |
<!-- src: java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (apply: menu items and their conditions; addCustomFirmwareMenuItem); java_console/ui/src/main/java/com/rusefi/maintenance/UpdateMode.java (display texts); java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (isDfuProgrammingSupported: Windows or Linux; getDfuEraseCommand "-e all") -->

<!-- shot: img/console/flashing-update-menu.png | rusEFI console start window ▸ Update Firmware tab ▸ arrow beside Update Firmware | Proteus F7 connected; menu open showing Auto DFU Update, Switch to DFU Mode, Switch to OpenBLT Mode, Manual OpenBLT Update | Figure 4 — The other flashing options, under the arrow beside the button. -->

!!! note "Update Software is not Update Firmware"
    The **Update Software** button, when it is shown, updates the *bundle* on your computer — the
    console and the firmware files — from the rusEFI servers. It does not touch the ECU. It appears
    only when automatic updates are switched off or the automatic update failed. After it has run,
    flash the ECU with **Update Firmware** as usual.
    <!-- src: java_console/ui/src/main/java/com/rusefi/ui/basic/StartupUpdateActions.java (updateSoftwareButton visible when !Autoupdate.isAutoUpdateEnabled, applySoftwareUpdateOutcome); java_console/autoupdate/src/main/java/com/rusefi/autoupdate/Autoupdate.java (class comment: "Update Software" updates the bundle, runManualUpdate) -->

The console refuses to write a firmware file that was built for a different board than the one it
detected, and asks before writing one it cannot verify.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/MaintenanceUtil.java (confirmFirmwareMatchesBoard, ensureFirmwareForConnectedTarget); java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (executeDFU: "firmware/board mismatch") -->

!!! warning "Proteus F7: read the console's warning first"
    With a Proteus F7 bundle the console shows a blinking **WARNING: Proteus F7** link on its Connect
    tab, pointing to the rusEFI wiki page *F7 requires full erase*. Read that page before you flash a
    Proteus F7 for the first time.
    <!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (proteusWarning: "WARNING: Proteus F7", wiki.rusefi.com/F7-requires-full-erase) -->

### Method B · Flash the full image over DFU

Use DFU for an ECU that has no rusEFI on it yet, to put a fresh bootloader on, or to recover an ECU
whose OpenBLT does not work. DFU always writes the **full image** (`rusefi_…_proteus_f7_….bin`),
starting at `0x0800 0000`.

#### 1 · Get the ECU into DFU

The ECU has to be in the STM32's DFU bootloader. There are three ways, depending on whether the
firmware still runs:

- **From the console** (firmware running): this is done in the rusEFI console. Use **Switch to DFU
  Mode** (or **Auto DFU Update**, which switches and flashes in one go). You can also type the
  command `reboot_dfu` in the console's **Messages** tab, or run `bin/switch_to_dfu.sh`
  (`bin\switch_to_dfu.bat` on Windows) from the bundle folder, which sends the same command.
- **From TunerStudio** (firmware running): **Controller ▸ Bench test**, button **Reset to DFU**.
- **With the BOOT0 pin** (firmware not running): an STM32 enters its DFU bootloader when its BOOT0
  pin is held high at reset. Some boards have a **PROG** or **BOOT0** button for this — hold it while
  you power up or reset the board. The Proteus board files in the rusEFI repository do not say
  whether a Proteus has one; check your board's documentation.
<!-- src: firmware/rusefi.cpp (addConsoleAction CMD_REBOOT_DFU jump_to_bootloader); firmware/hw_layer/ports/stm32/stm32_common.cpp (jump_to_bootloader, reset_and_jump); firmware/controllers/bench_test.cpp (JUMP_DFU_COMMAND); firmware/tunerstudio/tunerstudio.template.ini (testMisc: "Reset to DFU", cmd_dfu); java_console/bin/switch_to_dfu.sh (reboot_dfu); java_console/connectivity/src/main/java/com/rusefi/SerialPortScanner.java (class comment: "PROG/BOOT0 button or software reboot into DFU") -->

In DFU the ECU's normal USB serial port disappears and an **STM32 BOOTLOADER** USB device appears in
its place (USB ID `0483:df11`). The console notices and says *"Board is in the DFU bootloader"*; its
main button changes to **Manual DFU Update**.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (STM32_DFU_USB_ID 0483:df11, WMIC_DFU_QUERY_COMMAND "STM32" "Bootloader"); java_console/ui/src/main/java/com/rusefi/DevicePane.java (bootloaderGuidance); java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (mainButtonModeFor: Dfu → DFU_MANUAL) -->

<!-- shot: img/console/flashing-dfu-device.png | rusEFI console start window ▸ Update Firmware tab | Proteus F7 sitting in STM32 DFU; main button reads Manual DFU Update; log line "Board is in the DFU bootloader" | Figure 5 — A board in DFU: the button becomes Manual DFU Update. -->

#### 2 · Write the full image

The simplest way is the console: this is done in the rusEFI console — press **Manual DFU Update**.
It writes the bundle's full image and checks it. If you prefer the command line, the tools are in the
bundle:

=== "Windows"

    The first time, install the STM32 DFU driver: the console's start window has an **Install
    Drivers** button, or run `drivers\silent_st_drivers2.exe` from the bundle.

    Then, in the bundle's `console\STM32_Programmer_CLI\bin` folder, run the same command the console
    uses:

    ```
    STM32_Programmer_CLI.exe -c port=usb1 -w <bundle folder>\rusefi_…_proteus_f7_….bin 0x08000000 -v -s
    ```

    `-w … 0x08000000` writes the image at the start of flash, `-v` verifies it, `-s` starts it.
    The tool prints *Download verified successfully* when it worked. If the ECU does not restart by
    itself, power-cycle it.

=== "Linux"

    Install `dfu-util` from your distribution. To use it without `sudo`, copy the bundle's
    `bin/st.rules` into `/etc/udev/rules.d/` and reconnect the ECU.

    Then, from the bundle folder:

    ```
    dfu-util --device 0483:df11 --alt 0 --dfuse-address 0x08000000:leave --download rusefi_…_proteus_f7_….bin
    ```

    `:leave` makes the chip leave DFU and start the new firmware when the write is done. The bundle's
    `bin/flash_dfu.sh` runs the same thing (`sudo dfu-util --alt 0 --download rusefi.bin -s
    0x8000000:leave`), but it expects the file to be called `rusefi.bin` — copy or rename the
    bundle's `.bin` first.

=== "macOS"

    The console does not support DFU on macOS: use Method A (OpenBLT), which works on every system.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (getDfuWriteCommand, getDfuUtilWriteCommand, executeDFU: "Download verified successfully", "Please power cycle device to exit DFU mode", isDfuProgrammingSupported); java_console/ui/src/main/java/com/rusefi/maintenance/DriverInstall.java ("Install Drivers"); firmware/bundle.mk (ST_DRIVERS, CONSOLE_FOLDER_SOURCES STM32_Programmer_CLI); java_console/bin/flash_dfu.sh; java_console/bin/st.rules -->

DFU writes only the part of flash that the image covers, so your settings survive this too. The one
exception is **Full DFU Erase**, which wipes the whole chip.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (getDfuWriteCommand writes at 0x08000000 without "-e all"; getDfuEraseCommand "-e all"; getDfuUtilEraseCommand mass-erase) -->

### Method C · Flash with an ST-Link

An **ST-Link** is a small debug probe from ST that talks to the processor directly through its debug
pins (SWD), with no help from any program on the ECU. It is the last resort when nothing answers on
USB. You need the probe and access to the board's SWD debug connector; the Proteus board files in the
rusEFI repository do not document one, so check your board's documentation.

=== "Windows"

    The console's **ST-LINK Update** entry appears when it sees an ST-Link, but it needs OpenOCD,
    which the Proteus F7 bundle does not include. Use ST's own programming software instead and
    write the full image `rusefi_…_proteus_f7_….bin` to address `0x08000000`.

=== "Linux"

    Install `st-flash` (the `stlink-tools` package). The bundle's `bin/flash_stlink.sh` runs:

    ```
    st-flash write rusefi.bin 0x08000000
    ```

    Like `flash_dfu.sh`, it expects a file called `rusefi.bin`: copy or rename the bundle's full
    image first, or type the command with the real file name.
<!-- src: java_console/bin/flash_stlink.sh; java_console/ecu_shared/src/main/java/com/rusefi/maintenance/StLinkFlasher.java (OPENOCD_EXE); java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (ST_LINK only on Windows); firmware/bundle.mk (BUNDLE_OPENOCD) -->

### After flashing: check the bootloader version

This is done in the rusEFI console. The update image never rewrites the bootloader, so an ECU that
has only ever been updated through OpenBLT keeps the bootloader it got with its last *full* image.
To see whether that bootloader is the one this firmware expects, connect with the console, open the
**Messages** tab and type:

```
show_blt_version
```

The firmware reads a four-letter marker that the bundle stamps into the bootloader area (at
`0x0800 0024`) and compares it with the one it was built for. The answer ends in **CURRENT** when they
match, for example `blt=30314c42 CURRENT version` (`42 4c 31 30` is "BL10"), or **UNEXPECTED** when the
ECU runs new firmware on an older bootloader.
<!-- src: firmware/console/eficonsole.cpp (show_blt_version, EFI_USE_OPENBLT); firmware/hw_layer/ports/mpu_util.h (BLT_CURRENT_VERSION, BLT_BIN_VERSION_ADDR, getOpenBltVersion); firmware/bin/set_bl_bin_version.sh (BL10 at offset 0x24) -->

<!-- shot: img/console/flashing-show-blt-version.png | rusEFI console ▸ Messages tab | Proteus F7 connected; show_blt_version typed; reply line "blt=30314c42 CURRENT version" visible | Figure 6 — show_blt_version on a Proteus F7 with a current bootloader. -->

An **UNEXPECTED** bootloader still starts the firmware; a rusEFI release that needs a newer bootloader
says so. To refresh it, flash the **full image** over DFU (Method B). Only the full `.bin` carries the
marker: the bootloader-only file used by **Install OpenBLT** is not stamped, so after installing it
`show_blt_version` reports UNEXPECTED even though the bootloader is new.
<!-- src: firmware/bundle.mk (.h2d-sentinel: bin/set_bl_bin_version.sh $(DBIN) only); firmware/bin/set_bl_bin_version.sh; firmware/bundle.mk (BOOTLOADER_BIN_OUT is the unstamped openblt_*.bin) -->

## Examples

:material-circle:{ .level-intermediate } Intermediate

### Example 1 — Routine update of a running Proteus F7

A Proteus F7 runs an older rusEFI and you have downloaded a new Proteus F7 bundle.

1. In TunerStudio, **File ▸ Save Tune As** → `before-update.msq`. Close TunerStudio.
2. Start the console from the new bundle, **Update Firmware** tab, **Migrate Settings** ticked,
   **Update Firmware**.
3. The log shows the tune backed up to `state/<date>-<time>_backup_from_ecu.msq`, the OpenBLT write,
   the ECU found again, and the merged tune written back. If some fields could not be carried over,
   the console lists them and asks whether to keep the rest; with a big jump between versions that
   is normal — check those settings in TunerStudio afterwards.
4. Open TunerStudio with the new bundle's `.ini`, connect, and look over the tune before starting
   the engine.
<!-- src: java_console/ecu_shared/src/main/java/com/rusefi/maintenance/CalibrationsHelper.java (updateFirmwareAndRestorePreviousCalibrations, showCalibrationFailureDialog, "field(s) could not be migrated") -->

### Example 2 — A Proteus F7 that has never had rusEFI, or whose bootloader is old

1. Put the board into DFU (from TunerStudio's **Reset to DFU** if it runs any rusEFI, otherwise with
   BOOT0 if your board has a button for it).
2. In the console, **Manual DFU Update** — or on Linux
   `dfu-util --device 0483:df11 --alt 0 --dfuse-address 0x08000000:leave --download rusefi_…_proteus_f7_….bin`.
3. The ECU starts the new firmware. If it had no settings yet, it starts on factory defaults. If it
   had settings and the layout version is unchanged, it keeps them.
4. In the console's **Messages** tab, `show_blt_version` now answers **CURRENT**. From now on, use
   Method A for updates.
<!-- src: firmware/controllers/flash_main.cpp (readFromFlash: NotFound → resetConfigurationExt(DEFAULT_ENGINE_TYPE)); firmware/console/eficonsole.cpp (show_blt_version) -->

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

| Symptom | Likely cause | Check |
|---|---|---|
| Console says *"Make sure you are disconnected from TunerStudio"* | TunerStudio holds the USB port | close TunerStudio |
| Console shows *"Nothing detected"* | cable, power, or driver | try another cable (some carry power only); on Windows **Install Drivers**; see *Recovering an ECU* |
| *"Board in OpenBLT bootloader on … — use the Update Firmware tab"* | an update was interrupted, or the firmware is not valid | flash again with **Manual OpenBLT Update** |
| *"STM32 DFU device 0483:df11 was not detected"* (Linux) | the ECU is not in DFU, or no USB permission | Method B step 1; install `bin/st.rules` |
| *"Target device not found"* / *"DRIVER ERROR?"* (Windows) | the DFU driver is missing | **Install Drivers**, or `drivers\silent_st_drivers2.exe` |
| `flash_dfu.sh` or `flash_stlink.sh`: file not found | the scripts expect `rusefi.bin`, the bundle's file has a long name | copy or rename the full image, or run the command with its name |
| *"Firmware update aborted — firmware/board mismatch"* | the file is for another board | use the bundle for your board |
| Settings changed to defaults after an update | the settings version or size changed | restore from the console's backup or your saved `.msq` |
| Some settings look wrong after an update, others fine | the layout changed but size and version did not | restore your saved tune from TunerStudio |
| `show_blt_version` says UNEXPECTED | the bootloader came from an older full image (or from **Install OpenBLT**) | flash the full image over DFU |
| The ECU does nothing after a DFU or ST-Link write was interrupted | bootloader and firmware damaged | the chapter *Recovering an ECU* |
<!-- src: java_console/ui/src/main/java/com/rusefi/StartupFrame.java (noPortsMessage texts); java_console/ui/src/main/java/com/rusefi/maintenance/ProgramSelector.java (noHardware "Nothing detected"); java_console/ecu_shared/src/main/java/com/rusefi/maintenance/DfuFlasher.java (executeDFU messages); java_console/bin/flash_dfu.sh; java_console/bin/flash_stlink.sh -->

## Related

- Installing the software — the bundle, the console, the drivers
- First connection — TunerStudio and the bundle's `.ini`
- Updating firmware — keeping an ECU up to date
- Recovering an ECU — when flashing has gone wrong
- Tunes and backups — saving and restoring tunes
