# The official boards

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** rusEFI runs on a family of official boards; this manual uses the Proteus F7 for
> every example, and this chapter shows what is on each of its three connectors.

## Overview

:material-circle:{ .level-basic } Basic

rusEFI is firmware. The same source is built into a separate firmware file for each board, and each
board directory in the rusEFI source describes that board's connectors, default pins and the options
TunerStudio shows. The manual's reference board is the **Proteus**, built for the STM32F7
microcontroller (**Proteus F7**). Its connectors are described pin by pin in the board's connector
files, and every pin named in this manual comes from them.
<!-- src: firmware/config/boards/readme.md (one BOARD_NAME per folder, connector yaml); firmware/config/boards/proteus/connectors/black23.yaml; firmware/config/boards/proteus/connectors/black35.yaml; firmware/config/boards/proteus/connectors/white35.yaml -->

## The Proteus at a glance

:material-circle:{ .level-basic } Basic

The Proteus has three sealed connectors: one **23-pin** connector (*Black23*) and two **35-pin**
connectors, one black (*Black35*) and one white (*White35*). As a rule of thumb:

| Connector | What is on it |
|---|---|
| **Black23** | power in, power ground, VR and digital (Hall) trigger inputs, both electronic throttle H-bridges, both CAN buses |
| **Black35** | the outputs: 16 low-side, 4 high-side and 12 ignition outputs, plus power ground |
| **White35** | the sensors: analog voltage and temperature inputs, 5 V and 12 V sensor supplies, sensor ground, two knock inputs |
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (all pins); firmware/config/boards/proteus/connectors/black35.yaml (all pins); firmware/config/boards/proteus/connectors/white35.yaml (all pins) -->

Counted from the connector files:

| Type | Count | Pins | TunerStudio names |
|---|---|---|---|
| Low-side outputs | 16 | Black35 3–12, 15, 16, 19–21, 23 | Lowside 1 … Lowside 16 |
| — of which with flyback diode | 4 | Black35 10, 11, 12, 23 | Lowside 13, 14, 15, 16 |
| High-side outputs | 4 | Black35 1, 2, 13, 14 | Highside 1 … 4 |
| Ignition outputs (logic level) | 12 | Black35 22, 25–35 | Ign 1 … Ign 12 |
| H-bridges (DC motor / ETB) | 2 | Black23 7/6 (ETB 1 +/−), 15/8 (ETB 2 +/−) | — |
| Analog voltage inputs | 11 | White35 13–18, 24–28 | Analog Volt 1 … 11 |
| Analog temperature inputs | 4 | White35 19, 20, 30, 31 | Analog Temp 1 … 4 |
| VR inputs | 2 | Black23 5/13 (VR 1 +/−), 4/12 (VR 2 +/−) | VR 1, VR 2 |
| Digital (Hall/switch) inputs | 6 | Black23 1, 2, 3, 9, 10, 11 | Digital 1 … 6 |
| Knock inputs | 2 | White35 34, 35 | — |
| CAN buses | 2 | Black23 17/16 (CAN H/L), 22/21 (CAN2 H/L) | — |
| 5 V sensor supplies | 2 | White35 9/21/32 (#1), 10/22/33 (#2) | — |
| 12 V protected sensor supply | — | White35 11, 12 | — |
| Sensor ground (GNDA) | 10 pins | White35 1–8, 23, 29 | — |
| Power ground | 6 pins | Black23 14, 19, 20; Black35 17, 18, 24 | — |
| Power in | 2 | Black23 18 (ignition switch), 23 (main relay) | Battery Sense (pin 18) |
<!-- src: firmware/config/boards/proteus/connectors/black35.yaml (type inj/ls/hs/ign, "with flyback"); firmware/config/boards/proteus/connectors/black23.yaml (type etb/vr/din/can/12v/gnd); firmware/config/boards/proteus/connectors/white35.yaml (type av/at/5v/12v/agnd, Knock input 1/2); firmware/config/boards/proteus_meta.h (PROTEUS_LS_*, PROTEUS_HS_*, PROTEUS_IGN_*, PROTEUS_DIGITAL_*, PROTEUS_VR_*) -->

The Proteus hardware design, linked from the board's readme, gives these ratings: low-side drivers
4 A, high-side outputs 12 V 3 A, ignition outputs 5 V, two 5 V sensor supplies of 150 mA each, a
protected 12 V sensor supply, and full operation from a 6–24 V supply. Treat these as the design's
figures for the outputs; this manual states no other ratings.
<!-- src: firmware/config/boards/proteus/readme.md (link to the Proteus hardware repository, whose readme lists the hardware features) -->

## The connectors pin by pin

:material-circle:{ .level-basic } Basic

### Power and ground

- **Black23 pin 18** powers the ECU itself: connect it to the **output of the ignition switch**. The
  same pin is the battery-voltage sense (**Battery Sense**).
- **Black23 pin 23** is the supply from the **main relay**. It feeds the electronic throttle drivers
  and the high-side outputs, so it must be on the same main relay that feeds injectors and coils.
- **Power ground** is on Black23 14, 19, 20 and Black35 17, 18, 24. **Sensor ground** (GNDA) is a
  separate set of pins on White35. Never use one for the other.
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (pin 18 Battery Sense "Connect this pin to the output of your ignition switch", pin 23 "Power supply from main relay ... Supplies power to electronic throttle drivers and high side outputs"); firmware/config/boards/proteus/board_configuration.cpp (setupVbatt: vbattAdcChannel EFI_ADC_7) -->

By default the firmware switches the main relay with **Lowside 12** (Black35 21), the cooling fan with
**Lowside 11** (Black35 9) and the fuel pump relay with **Lowside 10** (Black35 20). The connector
file describes those three pins as "Injector #12 or Main relay", "Injector #11 or radiator fan relay"
and "Injector #10 or Fuel Pump relay": on a 12-cylinder engine they become injectors instead.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (proteus_boardDefaultConfiguration: mainRelayPin LS_12, fanPin LS_11, fuelPumpPin LS_10); firmware/config/boards/proteus/connectors/black35.yaml (pins 9, 20, 21) -->

### Inputs

- **Analog voltage inputs** read 0 to about 5 V through an on-board divider (5.6 kΩ / 10 kΩ, ratio
  1.56, on a 3.3 V converter). Some carry a suggested use: Analog Volt 1 for MAP, 2 and 3 for the two
  throttle tracks, 9 and 7 for the two pedal tracks; the firmware also puts an analog wideband on
  Analog Volt 10 by default.
- **Analog temperature inputs** have a **2.7 kΩ pull-up** to 5 V inside the ECU, for two-wire
  thermistors. Analog Temp 3 is the default coolant (CLT) input and Analog Temp 2 the default intake
  air (IAT) input. TunerStudio hides the pull-up value on Proteus, because it is fixed by the board.
- **VR inputs** take a two-wire variable-reluctance sensor on a + and − pin each.
- **Digital inputs** take Hall sensors and switches. **Digital 1** is the default crank (primary
  trigger) input.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (setupVbatt: analogInputDividerCoefficient 1.56, adcVcc 3.3; setupDefaultSensorInputs: clt, iat, tps, map, afr Analog Volt 10, triggerInputPins[0] DIGITAL_1; proteus_boardConfigOverrides: bias_resistor PROTEUS_DEFAULT_AT_PULLUP); firmware/config/boards/proteus_meta.h (PROTEUS_DEFAULT_AT_PULLUP 2700, PROTEUS_IN_*); firmware/config/boards/proteus/prepend.txt (ts_show_clt_iat_pullup false) -->

### Outputs

- **Low-side outputs** switch a load to ground (injectors, relays, solenoids). Lowside 13–16 have a
  flyback diode on board.
- **High-side outputs** switch the main-relay 12 V to a load whose other side is grounded.
- **Ignition outputs** are 5 V logic signals for smart coils or an external igniter, **never** a bare
  coil.
- **H-bridges** drive DC motors — normally the electronic throttle, or a stepper idle valve.
<!-- src: firmware/config/boards/proteus/connectors/black35.yaml (Lowside 13–16 "with flyback", "Smart Ignition Coil N"); firmware/config/boards/readme-boards.md (Smart Ignition Coil N means a logic-level output, never a dumb coil directly); firmware/config/boards/proteus/board_configuration.cpp (setupEtb: setupTLE9201IncludingStepper) -->

How to wire each kind is in *Wiring sensors*, *Wiring outputs* and *CAN bus wiring* (this part).

### Full Proteus pinout

Generated from the board's connector files. *TunerStudio name* is what the pin is called in
TunerStudio's pin lists.

--8<-- "reference/pinout/_proteus.table.md"

## Proteus variants

:material-circle:{ .level-intermediate } Intermediate

The Proteus directory builds several firmware files from the same board files: **proteus_f7** (the
one this manual uses), **proteus_f4** for boards with an STM32F4, a TCU build, and a legacy build for
older revisions. Flash the firmware that matches the microcontroller on your board; the connectors
are the same.
<!-- src: firmware/config/boards/proteus/meta-info-proteus_f7.env; firmware/config/boards/proteus/meta-info-proteus_f4.env; firmware/config/boards/proteus/meta-info-proteus_f7_tcu.env; firmware/config/boards/proteus/meta-info-proteus_legacy.env -->

## The other official boards

:material-circle:{ .level-basic } Basic

rusEFI's own overview of its board directories groups the boards like this:

| Group | Boards | Notes |
|---|---|---|
| Universal boards | microRusEFI (MRE), Proteus, uaEFI (and uaEFI 121, super-uaEFI), AlphaX 2chan / 4chan / 8chan / 4K GDI / Gold / Silver, small CAN board | general-purpose ECUs wired to any engine with your own harness |
| Vehicle-specific boards | Frankenso NA6, Subaru EG33, Hellen boards for GM E67, Honda K, Nissan 121-pin, VAG 121-pin, Mercedes 128-pin, Hyundai/Kia 154-pin, Mazda Miata NA6 / NA 1996 / NB1 / NB2 | plug into the factory harness of a particular car |
| Development boards | STM32 Discovery and Nucleo boards, CI test targets | not recommended as a real ECU |
<!-- src: firmware/config/boards/readme-boards.md (Universal boards, Vehicle-specific boards, Development boards tables) -->

Most of the universal and vehicle-specific boards other than Proteus and microRusEFI are built on
the **Hellen** platform, whose boards share modules and naming. All official boards use the same
naming in their connector files — for example *Smart Ignition Coil N* for logic-level ignition
outputs and *GNDA Analog/Sensor Ground* for sensor ground — so what this manual says about a Proteus
pin type carries over to other boards. Pin numbers do not: always use your own board's pinout.
<!-- src: firmware/config/boards/hellen/readme.md (Hellen One platform); firmware/config/boards/readme-boards.md (Pinout language conventions) -->

## Pitfalls

:material-circle:{ .level-basic } Basic

| Mistake | Result | Do instead |
|---|---|---|
| Pin 18 and pin 23 on Black23 fed from the same unswitched battery wire | ECU never sleeps, or drivers powered with the main relay off | pin 18 from the ignition switch, pin 23 from the main relay |
| Sensor ground on a power ground pin | noisy, offset sensor readings | sensors to White35 GNDA only |
| A bare coil on an ignition output | burnt output | smart coil or igniter (see *Wiring outputs*) |
| Pin numbers taken from another board's pinout | wrong wiring | use the Proteus table above |

## Related

- Part II — Wiring sensors, Wiring outputs, CAN bus wiring
- [Electronic throttle](../part3/electronic-throttle.md) — the H-bridges and the throttle/pedal inputs
- [Safety](../safety.md)
