# Power, grounds and ground loops

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** the ECU, its sensors and its outputs need clean 12 V in, separate ground paths
> back out, and a fuse on every supply — get this right and most "strange sensor" problems never happen.

## Overview

:material-circle:{ .level-basic } Basic

Every circuit is a loop: current leaves the battery's positive terminal, goes through a fuse, a
switch or relay and the load, and comes back to the battery's negative terminal through the
**ground**. In a car the engine block and the body are part of that return path. This chapter
explains how power reaches a Proteus, why it has two kinds of ground pin, and how a badly placed
ground wire can make a sensor read wrong. It assumes you have read *Wiring basics*.

!!! danger "A battery can start a fire"
    A car battery delivers hundreds of amps into a short circuit. A spanner across the terminals,
    or an unfused wire chafing on the body, glows red and sets the harness alight. Disconnect the
    battery negative before you wire anything, fuse every supply as close to the battery as you can,
    and reconnect the negative last.

## Concepts

:material-circle:{ .level-basic } Basic

### How power reaches a Proteus

<figure markdown>
  ![Battery positive through a main fuse; one branch through the ignition switch and a fuse to Black23 pin 18; one branch through a fuse to the main relay, whose output feeds Black23 pin 23 and the injectors and coils; the relay coil and the fuel pump relay coil are switched to ground by Lowside 12 (Black35 pin 21) and Lowside 10 (Black35 pin 20); power grounds return to the block](../img/diagrams/power-grounds-supply.svg)
  <figcaption>Figure 1 — Power on a Proteus. Red is battery 12 V, blue the ignition-switched feed,
  orange what the ECU switches, black the power grounds.</figcaption>
</figure>

A Proteus takes 12 V on two pins of the Black 23-pin connector:

- **Black23 pin 18 — ignition power.** The board files say: connect this pin to the output of your
  ignition switch. It powers the ECU, and the ECU measures battery voltage on it.
- **Black23 pin 23 — power from the main relay.** Connect it to the output of the car's main relay, the
  relay that also powers the injectors and coils. It supplies the electronic throttle drivers and the
  high-side outputs.
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (pin 18 Battery Sense / ignition power, pin 23 power supply from main relay); firmware/config/boards/proteus/board_configuration.cpp (setupVbatt: vbattAdcChannel EFI_ADC_7) -->

The ECU decides that the ignition is on when the voltage it measures is above **6 V**. (A separate
key-sense input can be set in **Setup ▸ Ignition key input Settings**; most installations do not
need it.)
<!-- src: firmware/controllers/ignition_controller.cpp (isIgnVoltage: 6.0 V threshold, IgnKeyVoltage or BatteryVoltage) -->

### The main relay

The **main relay** switches the heavy loads — injectors, coils, the throttle drivers — so their
current does not pass through the ignition switch. On Proteus the ECU drives the relay's coil from
**Lowside 12** (Black35 pin 21), which is the factory setting of **Setup ▸ Outputs ▸ Main relay
output**. A *low-side* output switches to ground: the relay coil gets fused 12 V on one side, and the
ECU completes the circuit on the other.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (proteus_boardDefaultConfiguration: mainRelayPin = PROTEUS_LS_12); firmware/config/boards/proteus/connectors/black35.yaml (pin 21 Injector #12 or Main relay) -->

The ECU turns the relay on while it sees ignition voltage, and keeps it on for **Main Relay Disable
Time** `mainRelayDisableTime` after the ignition goes off (1–60 s), so a short dip while the
starter engages does not kill the engine.
<!-- src: firmware/controllers/actuators/main_relay.cpp (MainRelayController::onSlowCallback, needsDelayedShutoff); firmware/integration/rusefi_config.txt (mainRelayDisableTime) -->

The fuel pump relay is driven the same way from **Lowside 10** (Black35 pin 20) and the radiator fan
relay from **Lowside 11** (Black35 pin 9) by default.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (fuelPumpPin = PROTEUS_LS_10, fanPin = PROTEUS_LS_11); firmware/config/boards/proteus/connectors/black35.yaml (pins 9, 20) -->

!!! danger "Fuel pump wiring"
    Wire the pump through its own fuse and the ECU-controlled relay, never straight from the
    ignition switch. The ECU runs the pump for the prime time after key-on and then only while the
    engine is turning, and switches it off on a firmware error — so after a crash or a stall the
    pump stops spraying fuel. A hot-wired pump keeps running. Never test a pump with the fuel line
    open near anything that can spark.
    <!-- src: firmware/controllers/modules/fuel_pump/fuel_pump.cpp (FuelPumpController::onSlowCallback: isPrime, engineMovedRecently, hasFirmwareError) -->

### Fuses

A fuse protects the **wire**, not the device: choose it for the smallest wire it feeds, and put it
as close to the power source as you can, so a short anywhere along the wire blows it. One fuse per
circuit (ECU, injectors, coils, pump, fan) also tells you where a fault is. The Proteus board files
do not state current ratings for any pin; size fuses for the wire and the load you connect, and check
the Proteus hardware documentation (wiki.rusefi.com/Proteus-Manual) for the board's own limits.
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (info.board_url; no current ratings in the pin list) -->

### Two kinds of ground

:material-circle:{ .level-basic } Basic

| Kind | Proteus pins | What returns there |
|---|---|---|
| **Power ground** (Power/Chassis GND) | Black23 14, 19, 20 · Black35 17, 18, 24 | the ECU's own current and its outputs' current — wire each pin to the engine block |
| **Sensor ground** (GNDA Analog/Sensor Ground) | White 1–8, 23, 29 | only the return of sensors: coolant, air temperature, TPS, pedal, MAP, other 5 V sensors |
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (pins 14, 19, 20 gnd); firmware/config/boards/proteus/connectors/black35.yaml (pins 17, 18, 24 gnd); firmware/config/boards/proteus/connectors/white35.yaml (pins 1–8, 23, 29 agnd) -->

A sensor ground wire goes from the sensor **back to a White GNDA pin, and nowhere else** — not to
the block, not to a nearby bolt. The next section shows why.

### Star grounding

Run every power ground on its own wire to **one point** on the engine block (a clean, bare stud),
and run the battery negative and the body strap to the same point. That point is the *star*: every
return current has its own path to it, and none of them shares a wire with another.

### Why shared returns corrupt sensor readings

:material-circle:{ .level-intermediate } Intermediate

A wire has resistance. When current flows in it, the two ends are at different voltages:
voltage = current × resistance. Copper of 0.5 mm² has about 0.035 Ω per metre.

Suppose a TPS ground is spliced into an ignition coil's ground, and the two share 1 m of 0.5 mm²
wire to the block. When the coil charges, 5 A flows in that metre: 5 A × 0.035 Ω ≈ **0.18 V**. For
that moment the TPS ground is 0.18 V above the block, so the sensor's output is 0.18 V higher than it
should be. On a TPS whose travel spans 4 V, that is about 4 % of throttle — and it comes and goes with
every spark, so the reading jumps. The same happens with a throttle motor's current, a fan, or the
whole ECU's return when a sensor is grounded at the block instead of at the ECU.

A sensor returned to a White GNDA pin on its own wire carries only the sensor's few milliamps, so its
offset is negligible, and the ECU measures it against its own sensor ground.

!!! example "Reading the symptom"
    A coolant temperature that drops a few degrees whenever the fan runs, or a TPS that wobbles with
    engine speed at a steady pedal, is the classic sign of a shared return.

### The 5 V sensor supplies

Proteus has two 5 V sensor supplies, each on three pins: **supply 1 on White 9, 21, 32** and
**supply 2 on White 10, 22, 33**. Use them only to feed sensors. Never connect them to an outside
5 V source, never join supply 1 to supply 2, and never feed 12 V into them. Splitting sensors between
the two (for example throttle on one, pedal on the other) means a short on one sensor does not take
both down.
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (pins 9, 21, 32 +5 supply #1; pins 10, 22, 33 +5 supply #2) -->

White 11 and 12 are a **12 V protected output for sensors**, for sensors that need 12 V. The board
files give no current rating for them.
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (pins 11, 12) -->

Check and calibrate sensors with the ignition on: on USB power alone the 5 V supplies do not reach
5 V, so every ratiometric sensor reads wrong.

### Why the voltage at the ECU matters

The ECU corrects injector dead time and coil dwell for the battery voltage it measures. A voltage drop
in the ECU's supply or ground wiring makes it believe the battery is lower than it is, and it fuels
and charges the coils for that wrong voltage.
<!-- src: firmware/controllers/algo/fuel/injector_model.cpp (InjectorModelWithConfig::getDeadtime: BatteryVoltage); firmware/controllers/algo/ignition/ignition_state.cpp (dwellVoltageCorrection: BatteryVoltage) -->

## Procedure

:material-circle:{ .level-basic } Basic

### Wiring power and grounds

1. Disconnect the battery negative.
2. Fit the main fuse at the battery positive; run fused feeds to the main relay contact (30), the
   fuel pump relay contact, and through the ignition switch and a small fuse to **Black23 pin 18**.
3. Wire main relay output (87) through a fuse block to **Black23 pin 23**, the injectors' and coils' 12 V.
4. Feed each relay coil (86) from fused 12 V; wire its other side (85) to **Black35 pin 21**
   (main relay) or **pin 20** (fuel pump).
5. Run each of the six power ground pins on its own wire to the block star point.
6. Return every sensor to a White GNDA pin on its own wire.
7. Reconnect the battery negative.

### Checking the outputs

Open **Setup ▸ Outputs** and check **Main relay output ▸ Output** is *Lowside 12* and **Fuel Pump ▸
Output** is *Lowside 10* (the Proteus defaults), or the pins you actually wired.

<!-- shot: img/ts/power-grounds-outputs.png | Setup ▸ Outputs | Proteus F7 defaults, ignition on: Main relay output Lowside 12, Fuel Pump Lowside 10 | The Outputs dialog with the Proteus main relay and fuel pump defaults -->

### Measuring voltage drop

:material-circle:{ .level-intermediate } Intermediate

A voltage drop test finds bad grounds and crimps that a resistance test misses, because it is done
with current flowing:

1. Ignition on, the loads running (engine idling, or fuel pump and fan forced on).
2. Put the multimeter's black probe on the battery negative post and the red probe on an ECU power
   ground pin (back-probe the connector). Good wiring reads a few tens of millivolts; several hundred
   millivolts means a bad ground.
3. Red probe on battery positive, black on Black23 pin 18 or Black23 pin 23: the drop along the feed.
4. Compare the front-page **Battery** gauge (`VBatt`) with the voltage at the battery. A large
   difference is a drop in the ECU's feed or ground.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (VBattGauge "Battery", front page gauge6) -->

## Examples

:material-circle:{ .level-intermediate } Intermediate

| Situation | Offset | Effect |
|---|---|---|
| TPS ground shares 1 m of 0.5 mm² with a coil ground, 5 A | ≈ 0.18 V | TPS jumps ≈ 4 % with each spark |
| Sensor grounded at the block, ECU ground wire carries 10 A over 0.01 Ω | 0.1 V | every block-grounded sensor reads 0.1 V high |
| Sensor returned to White GNDA on its own wire | ≈ 0 | correct reading |

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

| Symptom | Likely cause | Check |
|---|---|---|
| ECU does not power up | no 12 V on Black23 pin 18, blown fuse | voltage at Black23 pin 18 with key on |
| ECU on, but injectors, coils or throttle dead | main relay not closing, nothing on Black23 pin 23 | relay coil feed, Black35 pin 21 wiring, *Main relay on* indicator |
| Engine dies just as the starter engages | supply dips | battery, grounds, voltage drop test |
| Sensor reading shifts when fan, pump or lights switch | sensor ground shared with a load | return the sensor to White GNDA alone |
| Battery gauge lower than the battery | drop in ECU feed or ground | voltage drop test |
| Several 5 V sensors fail together | short on a 5 V supply | unplug sensors one by one; split across supplies 1 and 2 |
| Fuel pump runs with the engine stopped | pump hot-wired, or relay stuck | wire through the ECU-controlled relay |

## Settings reference

### Outputs (Setup ▸ Outputs)

--8<-- "reference/settings/_outputsDialog.table.md"

## Related

- Wiring basics — tools, wire, crimping and fusing practice
- Shielding and noise — VR and knock wiring
- Wiring sensors — which sensor goes on which White pin
- [Safety](../safety.md)
