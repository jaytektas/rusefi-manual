# What rusEFI is, and how mature it is

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** rusEFI is open-source engine control firmware that anyone can read, build and
> fix; this chapter says what it is, what its licence lets you do, and what the project's own
> repository shows about how it is tested and released.

## Overview

:material-circle:{ .level-basic } Basic

An **engine control unit (ECU)** is a small computer that reads the engine's sensors and decides,
many times per revolution, when to fire each spark plug and how long to open each injector.
**rusEFI** is the firmware, the program, that runs inside such a computer. It runs on STM32
microcontrollers, and it is built on the ChibiOS real-time operating system.
<!-- src: README.md (What do we have here: Firmware for stm32 chips); firmware/readme.md (built on top of ChibiOS); CLAUDE.md (Project Overview) -->

The rusEFI repository holds more than the firmware itself:

| Part | What it is |
|---|---|
| Firmware | The program that runs in the ECU, with one configuration per supported board |
| rusEFI console | rusEFI's own PC program for firmware updates, diagnostics and more |
| Simulator | The firmware built as a PC program (Windows or Linux), so you can explore it without hardware |
| Unit tests | Automated tests of firmware pieces, run on a PC |
| Hardware | KiCad design files for some older boards |
<!-- src: README.md (What do we have here: Firmware, Hardware, rusEFI console, Simulator, Unit Tests) -->

The settings that adapt the firmware to your engine, the **tune**, are edited with TunerStudio,
which reads a description of every setting (the `.ini` file) that is generated for each board
together with its firmware. This manual uses TunerStudio for setup and tuning and the rusEFI console
for the jobs TunerStudio cannot do; Part I's *Your two tools* chapter explains the split.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (template the per-board .ini is generated from); firmware/bundle.mk (bundle contains the board .ini, console and drivers) -->

This manual covers rusEFI on the official boards. Its examples use the **Proteus F7**.

## The licence

:material-circle:{ .level-basic } Basic

rusEFI is free software under the **GNU General Public License, version 3** (GPL v3). The licence
file opens with three additional terms, quoted here exactly:

> rusEFI software is distributed under the terms of GNU version 3 license with the following
> additional terms:
>
> rusEFI#1: rusEFI is intended for off-road land and water vehicles.
>
> rusEFI#2: rusEFI is not compliant with automotive environmental regulations.
>
> rusEFI#3: rusEFI is not approved for manned aircraft applications.
<!-- src: license.txt (additional terms rusEFI#1..#3, before the GPL text) -->

The GPL also states that the program comes with **no warranty**. What that means for you, and what
the law where you live may say about using an engine management system on a road vehicle, is on
[Read this first — safety and disclaimer](../safety.md). Read it before you connect anything.
<!-- src: license.txt (section 15, Disclaimer of Warranty) -->

!!! danger "The licence does not make anything safe"
    rusEFI controls fuel, spark and, with an electronic throttle, the throttle itself. A wrong
    setting can destroy an engine or start a fire. The licence is explicit that no one guarantees
    the firmware works for your engine: checking that it does is your job.

## What open source means for you

:material-circle:{ .level-basic } Basic

"Open source" here means that the complete source code of the firmware, the console and the tools
is published, and the GPL gives you the right to use, study, change and share it. The licence's own
preamble puts it this way:

> Our General Public Licenses are designed to make sure that you have the freedom to distribute
> copies of free software (and charge for them if you wish), that you receive source code or can
> get it if you want it, that you can change the software or use pieces of it in new free
> programs, and that you know you can do these things.
<!-- src: license.txt (Preamble) -->

In practice that gives a user four things:

1. **You can read exactly what the firmware does.** When this manual says how a feature behaves,
   it is describing the code, and every paragraph carries a note pointing at the file it came from.
   You can open the same file and check. When a setting's behaviour surprises you, the answer is in
   the source, not in a guess.
2. **You can build it yourself.** The repository has everything needed to compile the firmware for
   every supported board. Most users never need to: ready-built firmware is published for every
   board (see *How it is released* below).
3. **You can fix it.** If you find a bug, you can change the code, test the change, and send it to
   the project as a pull request on GitHub. The project's stated model is a single `master` branch
   that each pull request is expected not to break.
4. **You can share fixes.** The GPL lets you give your changed firmware to others. If you do, it
   asks you to pass on the same freedoms: the people you give it to must be able to get the source
   code of your version, under the same licence.
<!-- src: README.md (Cloning the repository, Building the Code); misc/SoftwareDevelopmentProcess.md (stable master, Pull Requests); license.txt (Preamble: pass on to the recipients the same freedoms) -->

The licence is the authority on what you may and must do; the summary above is not legal advice.

## How mature is rusEFI? The evidence in the repository

:material-circle:{ .level-intermediate } Intermediate

"Mature" and "reliable" are claims, and this manual makes no claim it cannot point to. What it can
point to is how the project tests and releases its own code. Everything below can be checked in the
rusEFI repository; the numbers are from the commit this manual describes (see the *Unofficial
documentation* notice on [Read this first](../safety.md)).

### Unit tests

The firmware's logic is tested by **unit tests**: small programs, built for a PC rather than for the
ECU, that feed a piece of the firmware known inputs and check its outputs. They use the GoogleTest
framework and do not depend on the ECU's operating system or processor.
<!-- src: unit_tests/readme.md (googletest; not aware of ChibiOS or ARM) -->

At this commit the repository contains **1652 test cases** in **274 test files**, under
`unit_tests/tests/`, grouped by subsystem (actuators, sensors, triggers, ignition and injection,
Lua, launch control and more). You can count them yourself from the repository root:

```bash
grep -rhoE '^\s*TEST(_F)?\(' unit_tests --include=*.cpp | wc -l    # test cases
grep -rlE  '^\s*TEST(_F)?\(' unit_tests --include=*.cpp | wc -l    # files containing tests
```
<!-- src: unit_tests/tests (test sources, one folder per subsystem) -->

The project publishes a **coverage report** for these tests, which shows which lines of firmware
code the tests actually run: <https://rusefi.com/docs/unit_tests_coverage/>. A test count says
nothing about quality on its own; coverage, and reading the tests for the feature you care about,
say more.
<!-- src: README.md (Unit Tests coverage report link); unit_tests/readme.md (Published CI Coverage Report); unit_tests/ci_gcov.sh (coverage generation in CI) -->

### Continuous integration

**Continuous integration (CI)** means every change is built and tested automatically by GitHub
Actions, the build service attached to the rusEFI repository on GitHub. The workflow files live in
`.github/workflows/`. The ones that test the firmware are:

| Workflow | What it does | When it runs |
|---|---|---|
| **Firmware at GHA** (`build-firmware.yaml`) | Builds the firmware and bundle for every board configuration (42 build targets at this commit) | every push and pull request, nightly, on demand |
| **Unit Tests** (`build-unit-tests.yaml`) | Builds and runs all unit tests on Linux and macOS, then builds the coverage report | every push and pull request |
| **Unit Tests on Windows** (`build-unit-tests-windows.yaml`) | The same tests built on Windows | every push and pull request |
| **Simulator** (`build-simulator.yaml`) | Builds the Linux simulator, runs a functional test against it over the TunerStudio protocol, and runs it for 10 seconds | every push and pull request |
| **HW CI** (`hardware-ci.yaml`) | Flashes real boards and runs tests on them (see below) | every push and pull request |
| **Validate TunerStudio INI** (`validate-tunerstudio-template.yml`) | Checks the TunerStudio `.ini` template | every push and pull request |
| **Firmware on Windows**, **Only Bootloader**, **rusEFI validate console** | Build the firmware on Windows, the bootloader, and the console | every push and pull request |
<!-- src: .github/workflows/build-firmware.yaml (generate-matrix job, schedule nightly, workflow_dispatch); firmware/bin/generate_matrix.sh (one target per meta-info env file); .github/workflows/build-unit-tests.yaml (matrix ubuntu-latest and macos-latest, Run Tests); .github/workflows/build-unit-tests-windows.yaml (Unit Tests on Windows); .github/workflows/build-simulator.yaml (Run Simulator Functional Test, Run Linux Simulator for 10 seconds); java_console/autotest/src/main/java/com/rusefi/SimulatorFunctionalTestLauncher.java (runs SimulatorFunctionalTest over the binary protocol); .github/workflows/validate-tunerstudio-template.yml (Validate TunerStudio INI); .github/workflows/build-firmware-windows.yaml (Firmware on Windows); .github/workflows/build-bootloader.yaml (Only Bootloader); .github/workflows/build-rusEFI-console.yaml (validate console) -->

Two details matter when you read these results:

- **Not every board is built on every push.** Building all boards is the heaviest job the project
  runs, so a board's configuration can set a skip rate, and on an ordinary push some boards are
  skipped at random. Pull requests, the nightly run and manual runs build every board whose skip
  rate is below 100 %; a few variants are set never to build automatically. The Proteus F7 has no
  skip rate and is built every time.
  <!-- src: .github/workflows/build-firmware.yaml (comment on skip_rate and only: syntax); firmware/bin/generate_matrix.sh (getTarget: SKIP_RATE, EVENT_NAME, ONLY); firmware/config/boards/proteus/meta-info-proteus_f7.env (no SKIP_RATE) -->
- **The project calls its own automated testing limited.** Its development-process note describes
  "continuous integration and *limited* automated testing", and lists making the gate check more
  reliable and more complete as an open need. That note is old (it refers to November 2019), but it
  is the project's own statement of where it stands.
  <!-- src: misc/SoftwareDevelopmentProcess.md (stable master; limited automated testing; TODO gate check) -->

### Hardware-in-the-loop CI

Unit tests and the simulator run on a PC. **Hardware CI** runs the real firmware on real
microcontrollers: a test machine builds the firmware, erases and flashes it onto a board through an
ST-LINK programmer, and then a Java test suite connects to the board over USB and checks it. The
tests include burning settings, the composite logger, PWM outputs, a vehicle-speed input loop,
analog inputs and MAP, and running at high RPM, with jumper wires on the board connecting outputs
back to inputs.
<!-- src: .github/workflows/hardware-ci.yaml (Build Firmware, st-flash wipe and flash, Run Hardware CI); .github/workflows/hw-ci/run_hw_ci.sh (runs the test suite); .github/workflows/hw-ci/st_flash_wipe_and_flash.sh (erase and flash with retries); java_console/autotest/src/main/java/com/rusefi/HwCiNucleoF7.java (test classes, MAP fixture); java_console/autotest/src/main/java/com/rusefi/HwCiF4Discovery.java (test classes, jumper wires) -->

At this commit the hardware CI runs on two **development boards**, an STM32F407 Discovery and an
STM32F767 Nucleo, not on a production ECU. A Proteus F7 entry exists in the workflow but is switched
off with the comment "proteus F7 HW CI is not 100% reliable #6002". In other words: the firmware
for the Proteus F7 is built on every change and its logic is unit-tested, but this commit's CI does
not run it on a Proteus.
<!-- src: .github/workflows/hardware-ci.yaml (matrix build-target f407-discovery and nucleo_f767; proteus_f7 commented out, issue 6002); .github/workflows/hw-ci/how_to_local_hwci.md (wiring for F4-Discovery and F767-Nucleo) -->

### How it is released

Each build produces a **bundle** for a board: a zip with the firmware (in the forms the bootloader
and the update tools need), the matching TunerStudio `.ini`, the rusEFI console and the drivers. The
firmware's file name carries the build date, the board, the **signature hash** that identifies the
layout of the settings, and the source commit, so a file can always be traced back to the code it
was built from.
<!-- src: firmware/bundle.mk (BIN_TARGET name: branch, date, BUNDLE_NAME, SIGNATURE_HASH, GITHUB_SHA; CONSOLE_FOLDER, DRIVERS_FOLDER; release.txt) -->

There are three streams of builds:

| Stream | How it is made | Where it goes |
|---|---|---|
| **Development snapshot** | every push to `master` | the rusEFI build server, <http://rusefi.com/build_server/> |
| **Nightly** | a scheduled run once a day | a GitHub pre-release called *Nightly* plus the date, at <https://github.com/rusefi/rusefi/releases>, with a list of the commits since the previous nightly |
| **LTS** (long-term support) | a manual run with the LTS option set | bundles named after the release branch, such as `lts-26` |
<!-- src: .github/workflows/build-firmware.yaml (Set run condition variables: schedule creates nightly, push to master uploads to server, lts input; ncipollo/release-action prerelease Nightly; upload_bundle.sh); misc/actions/nightly_changelog.sh (commits since the previous nightly tag); README.md (build server link); java_console/mcp_ecu/README.md (download_bundle branch: development, master or an LTS name such as lts-26) -->

The project's **changelog**, `firmware/CHANGELOG.md`, lists named releases back to 2020 (the most
recent at this commit is *August 2026 "Day 1631"*), each with breaking changes, additions and fixes,
plus an *Unreleased* section for what has changed since.
<!-- src: firmware/CHANGELOG.md (Unreleased; August 2026 "Day 1631"; release template with Breaking Changes, Added, Fixed) -->

### The issue tracker

Bugs and feature requests are tracked in the open on GitHub:
<https://github.com/rusefi/rusefi/issues>. Anyone can read every report, how it was discussed, and
which change closed it. Many settings' help texts and code comments link to the issue they came
from. The *Getting help* chapter explains how to search it and how to file a good report.
<!-- src: .github/ISSUE_TEMPLATE/bug_report.md (bug report template); .github/ISSUE_TEMPLATE/config.yml (Support and LLM policy links); firmware/tunerstudio/tunerstudio.template.ini (help texts linking github.com/rusefi/rusefi/issues) -->

## What is settled and what is still moving

:material-circle:{ .level-intermediate } Intermediate

The repository itself marks some things as unfinished. These are the signs to look for:

- **Settings labelled experimental.** TunerStudio's **Controller** menu has **Experimental 1**,
  **Experimental 2** and **Experimental 3**; the first opens a dialog titled *Experimental/Broken*.
  The **Fuel** menu has a dialog titled *Experimental settings, do not touch*. Treat anything there
  as unfinished unless you have read the code behind it.
  <!-- src: firmware/tunerstudio/tunerstudio.template.ini (subMenu parkingLot "Experimental 1", parkingLot2, parkingLot3; dialog parkingLot "Experimental/Broken"; dialog fuelExperimental "Experimental settings, do not touch") -->
- **The *Unreleased* section of the changelog.** New features land there first. At this commit it
  lists, among others, an optional engine state machine, rolling launch control, burst knock
  retard and new triggers. New code has had less time in use than code that has been in several
  releases.
  <!-- src: firmware/CHANGELOG.md (Unreleased: Added) -->
- **Features the project itself calls preliminary.** For example, the console's AI Troubleshooting
  tab is described in its documentation as available "for acceptance testing", with tools that
  change the ECU left as "follow-ups".
  <!-- src: docs/llm-troubleshooting.md (acceptance testing; ECU write tools remain follow-ups) -->
- **Breaking changes.** Each release in the changelog has a *Breaking Changes* list: things that
  behave differently after an update, which you must check against your tune.
  <!-- src: firmware/CHANGELOG.md (Breaking Changes sections) -->

The core of an ECU, reading the trigger, scheduling spark and injection, the fuel and ignition
tables, has unit tests in `unit_tests/tests/trigger`, `unit_tests/tests/ignition_injection` and
neighbouring folders, and is built for every board. That is evidence of testing, not a guarantee:
the checks in the rest of this manual (first start, logging, watching the engine) still apply to
every engine.
<!-- src: unit_tests/tests/trigger (trigger decoder tests); unit_tests/tests/ignition_injection (ignition and injection tests); unit_tests/tests/test_engine_math.cpp (engine math tests) -->

!!! warning "A master build can carry a fresh bug"
    The development snapshot is built from whatever was merged last. The project's model is that
    `master` stays working, but a build from yesterday's change has had one day of use. If you want
    firmware that has been out longer, use a named or LTS release, and read the changelog's
    *Breaking Changes* before you update.

## Checking a feature's status yourself

:material-circle:{ .level-intermediate } Intermediate

Before you rely on a feature, especially one that can damage the engine, spend ten minutes finding
out how settled it is. You need a web browser; for steps 3 and 4, a copy of the source (download the
repository from GitHub, or browse it there).

1. **Read the help text.** In TunerStudio, hover over the setting or open the dialog's help. The
   help text comes from the firmware's own setting definitions, and often says what is unfinished
   or links an issue.
   <!-- src: firmware/integration/rusefi_config.txt (setting help texts, which become TunerStudio tooltips) -->
2. **Search the issue tracker.** On <https://github.com/rusefi/rusefi/issues>, search for the
   feature's name and its internal name (shown in `code` in this manual). Search **closed** issues
   too: a closed issue shows what was fixed and when. Open issues show what is known not to work.
3. **Look for its tests.** Search the `unit_tests/tests` folder for the feature's name or its
   internal name. A feature with tests that exercise its edge cases has been thought about; a
   feature with none relies on users having tried it.
4. **Read the code.** Each section of this manual has hidden source notes naming the file and
   function it was written from (view the page source, or the Markdown on GitHub). Open that file:
   comments such as `todo` or `not finished` are the authors' own notes about what is missing.
5. **Check the changelog** for when it was added and whether it changed recently.
6. **Ask.** If you are still unsure, ask on the forum (see the *Getting help* chapter). Say what you
   found in steps 1 to 5.

## Examples

:material-circle:{ .level-intermediate } Intermediate

!!! example "Example 1 — Is electronic throttle jam detection tested?"
    The [Electronic throttle](../part3/electronic-throttle.md) chapter describes jam detection,
    which disables the throttle motor and limits engine speed if the throttle cannot follow its
    target. To check how it is tested:

    1. Search the unit tests for `jam`. It finds `TEST(etb, jamDetection)` in
       `unit_tests/tests/actuators/test_etb.cpp`, one of 34 test cases in that file.
    2. Read the test to see which situations it covers.
    3. The chapter's source note points at `EtbController::checkJam` in
       `firmware/controllers/actuators/electronic_throttle.cpp`. Reading it shows that the
       timeout defaults to 0, which switches the feature off — which is what the chapter says.

    Result: the logic is unit-tested, and the default is understood. It is still worth logging the
    throttle on your own engine before relying on it.
    <!-- src: unit_tests/tests/actuators/test_etb.cpp (TEST etb jamDetection); firmware/controllers/actuators/electronic_throttle.cpp (EtbController::checkJam) -->

!!! example "Example 2 — A setting found under Experimental"
    You find a setting in **Controller ▸ Experimental 1**. The dialog's title is
    *Experimental/Broken*. Before switching it on, search the issue tracker and the unit tests for
    its internal name. If neither has anything, treat it as untested: try it on the bench or with the
    engine at idle, with a log running, and be ready to switch it off.
    <!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog parkingLot "Experimental/Broken") -->

## Pitfalls

:material-circle:{ .level-basic } Basic

| Pitfall | Why it matters | What to do |
|---|---|---|
| Taking a forum post or video as the current behaviour | rusEFI changes between releases; old advice can describe old firmware | check the changelog and the code for your firmware's date |
| Updating firmware without reading the changelog | *Breaking Changes* can alter how a setting behaves | read the entries since your current release first |
| Assuming a green CI run means the feature works on your engine | CI checks the code against its tests, not against your engine and wiring | do your own first-start checks and log |
| Assuming the hardware CI ran on your board | at this commit it runs on two development boards, not on a Proteus | rely on the unit tests and your own testing |
| Treating this manual as official | it is a community manual | the code is the authority; see [Read this first](../safety.md) |

## Related

- [Read this first — safety and disclaimer](../safety.md) — the licence terms, no warranty, road use
- Getting help — where to ask, what to gather, AI assistants, reporting a bug
- Building rusEFI yourself and contributing a fix — building the firmware and running the unit tests
- Part VI — Firmware and maintenance: choosing a release and updating
