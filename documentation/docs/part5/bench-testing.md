# Bench testing

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** before the engine ever turns, you can make rusEFI pulse each injector, fire
> each coil, click each relay and run each fan from TunerStudio, so every wire is proven before the
> first crank.

## Why test on the bench

:material-circle:{ .level-basic } Basic

Most first-start problems are wiring problems: injector 3 wired to cylinder 4's output, a coil on
the wrong pin, a fuel pump relay that never clicks. Every one of them can be found with the engine
stopped. TunerStudio has a button for nearly every output rusEFI drives. Press it, and rusEFI
switches that one output on and off a few times, so you can hear, see or measure the result.

The order that works:

1. Relays first: main relay, fuel pump, fans. You will hear each one click.
2. Injectors, one at a time, with **no fuel pressure**. Each one ticks.
3. Coils, one at a time, with the spark plugs grounded to the engine. Each one sparks.
4. Actuators: idle valve, VVT solenoids, boost solenoid, and the electronic throttle (see
   [Electronic throttle](../part3/electronic-throttle.md)).
5. The check engine light. It blinks so you can walk round and look at the dash.

!!! danger "Bench tests switch real outputs"
    A bench test drives the output exactly as a running engine would. A coil test makes a spark of
    tens of thousands of volts: hands off leads and coils, and ground the plugs firmly to the
    engine. An injector test with the fuel pump running sprays fuel into the intake or onto the
    floor: depressurise the fuel system and unplug the pump first. Read [Read this first](../safety.md).

## The bench test dialog

:material-circle:{ .level-basic } Basic

Open **Controller ▸ Bench test**. TunerStudio titles the dialog *Bench Test & Commands*
(`ioTest`). It has five panels:

| Panel | What it holds |
|---|---|
| **Spark** | **Spark #1** … one button per cylinder, and **Abort test** |
| **Injector Test** | **Injector #1** … one button per cylinder, and **Abort test** |
| *(test settings)* | **Count**, **On Time**, **Off Time**, and **Reset firmware settings** |
| **Lua Out Test** | **Lua Out #1** … **#8**, and **Abort test** |
| **Misc** | **A/C Relay**, **Idle Air Valve**, **Idle Second Air Valve**, **Stop Engine**, **Write Config**, **Reboot ECU**, **Reset to DFU**, **No flash Burn mode** |

<!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog ioTest, testSpark, testInjectors, testOther, testLuaOut, testMisc) -->

TunerStudio only shows as many spark and injector buttons as the engine has cylinders: with
**Number of cylinders** set to 4, buttons 5 to 12 are hidden.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (testSpark and testInjectors buttons gated on cylindersCount) -->

<!-- shot: img/ts/bench-testing-dialog.png | Controller ▸ Bench test | 4-cylinder tune, default Count/On Time/Off Time | The Bench Test & Commands dialog for a four-cylinder engine -->

<figure markdown>
  ![Controller ▸ Bench test: 4-cylinder tune, default Count/On Time/Off Time](../img/ts/bench-testing-dialog.png)
  <figcaption>Figure 1 — The Bench Test & Commands dialog for a four-cylinder engine</figcaption>
</figure>

**Controller ▸ Injector test** (`injTest`) is a second view of the injector buttons, with the same
three test settings (labelled **Iterations** here) and two gauges: battery voltage, and **Test
Bench Iterations**, which counts the pulses as they go out.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog injTest, injTest_l, injTest_r, testBenchIterGauge); firmware/controllers/bench_test.cpp (runBench: outputChannels.testBenchIter) -->

### What the three settings do

| Setting | Name | Default | Range | Meaning |
|---|---|---|---|---|
| **Count** | `benchTestCount` | 3 | 1 – 10 000 000 | How many pulses |
| **On Time** | `benchTestOnTime` | 4 ms | 0 – 500 ms | How long the output is on in each pulse |
| **Off Time** | `benchTestOffTime` | 500 ms | 5 – 2000 ms | Gap between pulses |

<!-- src: firmware/integration/rusefi_config.txt (benchTestOnTime, benchTestOffTime, benchTestCount); firmware/controllers/algo/defaults/default_base_engine.cpp (benchTestOnTime = 4, benchTestOffTime = 500, benchTestCount = 3) -->

The defaults give three 4 ms pulses half a second apart. That is a sensible coil dwell and an
injector pulse you can hear. If a value is empty or out of range when the settings change, rusEFI
puts the default back: an **On Time** of 0 becomes 4 ms, an **Off Time** under 5 ms becomes 500 ms,
and a **Count** under 1 becomes 3.
<!-- src: firmware/controllers/bench_test.cpp (onConfigurationChangeBenchTest) -->

!!! warning "Keep the coil on-time short"
    For a spark test, **On Time** is the coil's dwell. A coil charged for much longer than it was
    designed for (typically a few milliseconds) gets hot, and its driver too. Leave **On Time** at
    4 ms for coils; use longer pulses only for injectors and solenoids.

### Rules rusEFI applies

- **Spark, injector, transmission-solenoid and Lua-output tests only run with the engine
  stopped.** If rusEFI sees the engine turning, it ignores the button.
  <!-- src: firmware/controllers/bench_test.cpp (executeTSCommand: running = !rpmCalculator.isStopped(), TS_IGNITION_CATEGORY, TS_INJECTOR_CATEGORY, TS_SOLENOID_CATEGORY, TS_LUA_OUTPUT_CATEGORY) -->
- **One test at a time.** Tests run one after another in a background task; **Abort test** stops
  the pulse train that is running.
  <!-- src: firmware/controllers/bench_test.cpp (BenchController::ThreadTask, cancelBenchTest) -->
- **The output must be assigned.** A test drives whatever pin the output is set to. An output set
  to *NONE* does nothing.
- **Timing is exact.** Each pulse is scheduled with the same scheduler that fires injectors and coils
  on a running engine, so a 4 ms pulse is 4 ms on a scope.
  <!-- src: firmware/controllers/bench_test.cpp (runBench: engine->scheduler.schedule bstart/bend) -->

## Testing each output

:material-circle:{ .level-basic } Basic

### Injectors

1. Fuel pump unplugged, or its fuse pulled, and the fuel rail depressurised.
2. Ignition on (12 V on the ECU, not just USB).
3. **Controller ▸ Bench test ▸ Injector #1**. Injector 1 ticks three times. Put a finger or a
   screwdriver handle on it if the workshop is noisy.
4. Repeat for each cylinder. The injector that ticks must be the one on that cylinder.

If the wrong injector ticks, swap the output pins in **Fuel ▸ Injector Setup ▸ Injection hardware** (or rewire), not
the firing order.

### Coils

1. Remove the spark plugs from the engine, plug each one into its coil or lead, and lay the plugs
   so their threads touch bare engine metal. Or use a spark tester.
2. Ignition on.
3. **Controller ▸ Bench test ▸ Spark #1**. Plug 1 sparks three times.
4. Repeat for each cylinder.

!!! danger "Tens of thousands of volts"
    A coil's output can kill. Never hold a plug or lead while pressing a spark button, and never
    let the spark jump to anything but engine ground: a coil firing into open air can damage itself
    and the ECU's driver.

### Relays, fans, pumps and lights

These buttons are in the dialog where the output is set up. Each runs for a fixed time:

| Button | Where | What it does |
|---|---|---|
| **Test Fuel Pump** | **Setup ▸ Fuel Pump Control** | Fuel pump relay on for 3 s |
| **Test Fan 1** / **Test Fan 2** | **Setup ▸ Cooling Fans** | Fan 1 relay on for 2 s; fan 2 for 3 s |
| **Test Main Relay** | **Setup ▸ Outputs** | Main relay **off** for 1 s, then on again |
| **Test Starter Relay** | **Setup ▸ Outputs** | Starter relay on for 4 s |
| **Test Starter Disable** | **Setup ▸ Outputs** | Starter-disable relay on for 4 s |
| **Test Check Engine** | **Setup ▸ Check Engine Settings** | Check engine light blinks 16 times, ½ s on, ½ s off |
| **A/C Relay** | **Controller ▸ Bench test** | A/C compressor relay on for 0.8 s |

<!-- src: firmware/integration/ts_protocol.txt (BENCH_FUEL_PUMP_DURATION, BENCH_FAN_DURATION, BENCH_MAIN_RELAY_DURATION, BENCH_STARTER_DURATION, BENCH_AC_RELAY_DURATION); firmware/controllers/bench_test.cpp (fan2Bench, milBench, mainRelayBench with swapOnOff, starterRelayBench, starterRelayDisableBench); firmware/tunerstudio/tunerstudio.template.ini (fuelPumpDialog, fanBottom, mainRelayDialog, starterRelayDialog, startStopDialog, celSettings) -->

The main relay test works the other way round because the main relay is normally on while the ECU
runs: it switches the relay off for a second so you hear it drop out and pull in again.

!!! danger "The starter test cranks the engine"
    **Test Starter Relay** energises the starter for four seconds. With the engine assembled and in
    gear, the car moves. Neutral, handbrake on, and nobody near the belts.

### Actuators

| Button | Where | What it does |
|---|---|---|
| **Idle Air Valve** | **Controller ▸ Bench test** | Lets the idle controller drive the idle valve for 3 s |
| **Idle Second Air Valve** | **Controller ▸ Bench test** | Pulses the second coil of a two-wire idle valve with **Count**/**On Time**/**Off Time** |
| **Bench bank 1** / **Bench bank 2** | **Advanced ▸ VVT outputs and PID** (intake and exhaust panels) | Opens that VVT solenoid for 300 ms; only with the engine stopped |
| **Bench Test Boost Solenoid** | **Advanced ▸ Boost Control ▸ Boost control options** | Pulses the boost solenoid with **Count**/**On Time**/**Off Time** |
| **Bench Test ETB 1 (open 300ms)** | **Advanced ▸ Electronic Throttle Body actuator** | See [Electronic throttle](../part3/electronic-throttle.md) |

<!-- src: firmware/controllers/actuators/idle_thread_io.cpp (startIdleBench: timeToStopIdleTest 3000 ms); firmware/controllers/bench_test.cpp (secondIdleValveBench, vvtValveBench, boostValveBench); firmware/integration/ts_protocol.txt (BENCH_VVT_DURATION); firmware/tunerstudio/tunerstudio.template.ini (vvtPidDialog1, vvtPidDialog2 buttons gated on engineTurnedRecently == 0, boostDialog, etbTps1Calib) -->

### Lua outputs

**Lua Out #1** … **#8** pulse the outputs a Lua script drives, with 4 ms pulses and the
**Off Time** and **Count** settings. Use them to prove the wiring before the script is written.
<!-- src: firmware/controllers/bench_test.cpp (executeTSCommand: TS_LUA_OUTPUT_CATEGORY, doRunBenchTestLuaOutput with 4.0 ms) -->

## The Misc buttons

:material-circle:{ .level-intermediate } Intermediate

These are commands, not output tests:

| Button | What it does |
|---|---|
| **Stop Engine** | Asks rusEFI to stop the engine (cuts fuel and spark) |
| **Write Config** | Writes the settings in RAM to the ECU's flash, as **Burn** does |
| **Reboot ECU** | Restarts the ECU |
| **Reset to DFU** | Restarts the ECU into its DFU bootloader, for flashing (see the Flashing chapter) |
| **No flash Burn mode** | Makes **Burn** stop writing to flash, for quick experiments that should not be kept |
| **Reset firmware settings** | Replaces **every** setting with the firmware's defaults |

<!-- src: firmware/controllers/bench_test.cpp (executeTSCommand: TS_STOP_ENGINE, JUMP_DFU_COMMAND, REBOOT_COMMAND, TS_SET_DEFAULT_ENGINE, handleCommandX14: TS_WRITE_FLASH); firmware/tunerstudio/tunerstudio.template.ini (testMisc, testOther) -->

!!! warning "Reset firmware settings erases your tune"
    **Reset firmware settings** loads the default configuration over everything: pins, trigger,
    fuel and ignition tables, calibrations. Save the tune to a file first (**File ▸ Save Tune As**).

## Testing without an engine: the trigger stimulator

:material-circle:{ .level-intermediate } Intermediate

To see the whole engine logic work (RPM, fuel and spark scheduling, logging) with no engine, rusEFI
can feed itself a simulated crank signal. Open **Controller ▸ ECU stimulator**:

- **Trigger Simulator** (`triggerSimulatorRpm`) sets the simulated engine speed in RPM.
- **Enable internal trigger simulation** starts it; **Disable trigger simulation** stops it.

<!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog ecuStimulator); firmware/controllers/bench_test.cpp (handleCommandX14: TS_TRIGGER_STIMULATOR_ENABLE, TS_TRIGGER_STIMULATOR_DISABLE); firmware/controllers/trigger/trigger_emulator_algo.cpp (enableTriggerStimulator: directSelfStimulation, disableTriggerStimulator, setTriggerEmulatorRPM) -->

The simulated signal goes straight into the trigger decoder, shaped like the trigger wheel selected
in **Setup ▸ Trigger**. From there on rusEFI behaves as if the engine were turning: it shows RPM
and it schedules fuel and spark.

!!! danger "A simulated engine fires real outputs"
    With the stimulator running, rusEFI drives injectors and coils as for a running engine. On a
    car with fuel pressure and coils connected, that means fuel in the cylinders and sparks. Use the
    stimulator only with the fuel pump disconnected and the coils unplugged, or on an ECU on the
    bench.

An external stimulator, such as a crank-signal generator wired to the trigger inputs, tests the
input wiring and the trigger settings as well. Seeing what the ECU decodes from it, tooth by tooth,
is done with TunerStudio's tooth logger and the console's engine sniffer: see the Trigger chapter.

## Settings reference

:material-circle:{ .level-advanced } Advanced

**Controller ▸ Bench test**

--8<-- "reference/settings/_testOther.table.md"

**Controller ▸ ECU stimulator**

--8<-- "reference/settings/_ecuStimulator.table.md"

The console commands behind these buttons (`fuelbench`, `sparkbench`, `milbench` and others) are
listed in [Console commands](../part7/console-commands.md); TunerStudio is the tool for bench testing.
