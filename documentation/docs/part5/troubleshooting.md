# Troubleshooting guide

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** start from what you can see — the TunerStudio indicators, a warning code, or
> what the engine does — and this chapter sends you to the check and the chapter that fixes it.

## Read the dashboard first

:material-circle:{ .level-basic } Basic

Before changing anything, look at the indicator row at the bottom of the TunerStudio dashboard. Four
of its lights say what rusEFI is refusing to do and why:

| Indicator | When it lights | What it tells you |
|---|---|---|
| **Trigger ERR** | rusEFI saw trigger errors recently | The crank or cam signal is wrong, noisy or set up wrongly |
| **Fuel cut: …** | Injection is being cut | The text names the reason, for example a limit or a protection |
| **Ign cut: …** | Spark is being cut | The text names the reason |
| **ETB: …** | The electronic throttle is switched off | The text names the fault |

<!-- src: firmware/tunerstudio/tunerstudio.template.ini ([FrontPage] indicators isTriggerError, fuelCutReasonBlinker with fuelIgnCutCodeList, sparkCutReasonBlinker, etb1etbErrorCodeBlinker with etbCutCodeList) -->

**Warning** and **Check Engine** mean a code is active; **Config Error** means the firmware has a
message for you. [Diagnostics and error codes](diagnostics.md) explains all three, and
[Error codes](../part7/error-codes.md) lists every code.

!!! tip "One change at a time"
    Change one setting, burn, and test again. Two changes at once and you will not know which one
    fixed it, or which one broke something else.

## No connection

:material-circle:{ .level-basic } Basic

| Symptom | Likely cause | Check |
|---|---|---|
| TunerStudio cannot find the ECU | Driver missing (Windows), no permission on the serial port (Linux), wrong port | [Installing the software](../part1/installing.md), [First connection](../part1/first-connection.md) |
| TunerStudio warns that the firmware signature differs, or settings look wrong | The project's `.ini` is for another firmware build | [First connection](../part1/first-connection.md): create the project from the ECU's own `.ini` |
| Connects, then drops | Another program holds the port (the rusEFI console, a second TunerStudio) | Close the other program: only one program can use the port at a time ([Your two tools](../part1/two-tools.md)) |
| Nothing on USB at all | Firmware not running; ECU in its bootloader | [Flashing firmware](../part1/flashing-firmware.md); the recovery chapter |

## Engine cranks but does not start

:material-circle:{ .level-basic } Basic

Work down this list in order: each step needs the one above it.

1. **RPM while cranking.** Watch the RPM gauge as the engine cranks. **0 RPM** means no trigger: check
   the trigger type, the input pins and the sensor wiring ([Trigger](../part3/trigger.md),
   [Wiring sensors](../part2/wiring-sensors.md)). Jumping RPM or **Trigger ERR** means a noisy or
   wrongly-set-up signal ([Shielding and noise](../part2/shielding-noise.md)).
2. **Spark.** Prove each coil fires with **Controller ▸ Bench test** and grounded plugs
   ([Bench testing](bench-testing.md)). If they fire on the bench but not while cranking, check
   **Ign cut** on the dashboard and the ignition settings ([Ignition](../part3/ignition.md)).
3. **Timing.** A wrong trigger angle offset fires the plugs at the wrong time: the engine coughs, backfires
   or kicks back. Check it with a timing light ([Trigger](../part3/trigger.md)).
4. **Fuel.** Prove each injector with the bench test, then check fuel pressure, **Fuel cut** on the
   dashboard and the cranking fuel ([Cranking and starting](../part3/cranking.md),
   [Fuel](../part3/fuel.md)).
5. **Sensors.** A coolant sensor reading −40 °C or 140 °C gives far too much or far too little cranking
   fuel. Check every temperature reads sensibly with the engine cold ([Sensors and calibration](../part3/sensors.md)).

!!! danger "Cranking with fuel and spark"
    A flooded engine or a timing error can ignite fuel in the intake or exhaust. Keep the area clear,
    keep a fire extinguisher at hand, and stop cranking after a few seconds if nothing happens. Read
    [Read this first](../safety.md).

## Starts, then dies or runs badly

:material-circle:{ .level-intermediate } Intermediate

| Symptom | Likely cause | Where to look |
|---|---|---|
| Starts, dies as the key is released | Run circuit or main relay not powered; cranking-to-run fuel too lean | Power wiring ([Power, grounds and ground loops](../part2/power-grounds.md)); [Cranking and starting](../part3/cranking.md) |
| Idles too high or hunts | Idle air, idle target or idle PID | [Idle](../part3/idle.md) |
| Stalls when the throttle closes | Not enough idle air; deceleration fuel cut too eager | [Idle](../part3/idle.md); [Fuel](../part3/fuel.md) |
| Rich or lean everywhere | Injector flow, dead time or fuel pressure wrong | [Fuel](../part3/fuel.md) |
| Rich or lean in some places | VE table | Tuning fuel (Part IV) |
| Closed loop does nothing | Wideband not read, or closed-loop conditions not met | [Closed-loop lambda](../part3/closed-loop-lambda.md) |
| Hesitates when the throttle opens | Acceleration enrichment | [Fuel](../part3/fuel.md) |
| Misfires under load | Spark blown out (plug gap, coil dwell), lean mixture | [Ignition](../part3/ignition.md); [Fuel](../part3/fuel.md) |
| Hits a limit for no clear reason | A protection is acting — check **Fuel cut** / **Ign cut** | [Limits and engine protection](../part3/limits-protection.md) |

## Trigger errors

:material-circle:{ .level-intermediate } Intermediate

**Trigger ERR** while the engine turns means rusEFI saw a tooth pattern it did not expect. In order of
how often each is the cause:

1. **Wrong trigger setup** — trigger type, missing-tooth position, or a cam input assigned that is not
   wired. See [Trigger](../part3/trigger.md).
2. **Noise** — an unshielded VR cable, a shield grounded at both ends, or the sensor cable run beside
   coil or injector wires. See [Shielding and noise](../part2/shielding-noise.md).
3. **Sensor polarity or gap** — a VR sensor wired backwards triggers on the wrong edge; a Hall sensor
   with too large an air gap drops teeth at low speed. See [Wiring sensors](../part2/wiring-sensors.md).

The trigger chapter's *Diagnostics* section explains the tooth logger, which shows exactly where in the
wheel the pattern goes wrong.

## Sensor faults

:material-circle:{ .level-basic } Basic

| Code | Meaning | Usual cause |
|---|---|---|
| **P0107** | MAP reading too low | MAP sensor unplugged or no 5 V supply — normal on a bench with no sensor |
| **P0112** / **P0117** | IAT / coolant reading too low | Sensor shorted to ground, or the wrong input assigned |
| **P0122** | Throttle position 1 too low | TPS unplugged or calibration wrong |
| **P2135** | The two throttle sensors disagree | Calibration of one sensor, or a wiring fault |
| **P0335** | Crank sensor fault | No crank signal; see *Trigger errors* |

<!-- src: firmware/controllers/algo/obd_error_codes.h (OBD_Map_Low 107, OBD_Iat_Low 112, OBD_Clt_Low 117, OBD_TPS1_Primary_Low 122, OBD_TPS1_Correlation 2135, OBD_Crankshaft_Position_Sensor_A_Circuit_Malfunction 335) -->

The fix is in [Sensors and calibration](../part3/sensors.md) and [Wiring sensors](../part2/wiring-sensors.md).
Calibrate with the ignition on, never on USB power alone: on USB the sensor supplies cannot reach 5 V
and every calibration comes out wrong.

## The electronic throttle

:material-circle:{ .level-intermediate } Intermediate

If **ETB: …** lights, rusEFI has switched the throttle motor off and the throttle has sprung to its rest
position. The text says why: a sensor disagreement, a calibration that was never done, or the throttle
failing to follow its target. [Electronic throttle](../part3/electronic-throttle.md) covers every one,
with calibration and the autotune.

!!! danger "A throttle that opens by itself"
    Never work inside the throttle body while the ECU has 12 V: calibration and the bench test move the
    plate hard.

## When nothing here helps

:material-circle:{ .level-basic } Basic

1. Save the tune (**File ▸ Save Tune As**) and a log of the problem (the datalogging chapter).
2. Note the firmware signature: TunerStudio shows it for the connected ECU (see [First connection](../part1/first-connection.md)).
3. If the ECU crashed or reset, copy the fault reports from the SD card ([Diagnostics and error
   codes](diagnostics.md)).
4. Ask with all three attached: the getting-help chapter lists where.
