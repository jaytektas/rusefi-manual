# Wiring sensors

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-advanced } Advanced

> **In one sentence:** every sensor gets a supply (or nothing), one signal wire, and a return wire of
> its own back to the ECU's sensor ground — and Proteus puts each kind of sensor on its own family of
> pins, so the connector you use tells you what the firmware expects to find there.

## Overview

:material-circle:{ .level-basic } Basic

This chapter decides three things for every sensor on your engine: **which pin**, **which supply**, and
**which return**. The wire itself, the terminals and the crimp are in *Wiring basics*; the difference
between a power ground and a sensor ground is in *Power, grounds and ground loops*; what a sensor
*means* once it is connected — the calibration, the dialog, the fault codes — is in the Sensors chapter.
The full pin list of all three Proteus connectors is in *The official boards*.

A sensor connection is four decisions, in this order:

1. **Which family of input** the sensor belongs to. Proteus sorts them for you: thermistor inputs,
   analog voltage inputs, VR (magnetic pick-up) pairs, digital inputs, knock inputs, CAN.
2. **Where its supply comes from**, if it needs one at all. A thermistor and a VR pick-up need none;
   a MAP sensor needs exactly 5 V; a Hall sensor needs 5 V or 12 V depending on the sensor.
3. **Where its return goes**: a White **GNDA** pin, on its own wire, always.
4. **What cable** the signal wants: a plain pair for a slow 5 V signal, a twisted shielded pair for a
   VR or knock signal.

<figure markdown>
  ![Three sensor types at the Proteus connector: a 3-wire ratiometric sensor on White 9 for 5 V, White 13 for signal and White 1 for sensor ground; a 2-wire thermistor on White 20 with its 2.7 kilohm pull-up inside the ECU and White 2 for ground; a VR sensor as a twisted pair on Black23 pin 5 and Black23 pin 13](../img/diagrams/wiring-sensors-types.svg)
  <figcaption>Figure 1 — Three kinds of sensor, three different connections. Note what the thermistor
  does *not* have: a supply wire. Its 5 V comes from inside the ECU.</figcaption>
</figure>

| Kind | Wires | Where it lands on Proteus | Supply from the ECU? |
|---|---|---|---|
| Thermistor (temperature) | 2 | *Analog Temp 1–4* — White 19, 20, 30, 31 | no: a pull-up inside the ECU feeds it |
| Ratiometric analog (MAP, TPS, pedal, pressure) | 3 | *Analog Volt 1–11* — White 13–18 and 24–28 | yes: 5 V, 5 V and sensor ground |
| VR / magnetic pick-up (crank, cam) | 2 | *VR 1* Black23 pin 5 + / Black23 pin 13 −, *VR 2* Black23 pin 4 + / Black23 pin 12 − | no: it makes its own signal |
| Hall or switch (crank, cam, VSS, flex, clutch, brake) | 2–3 | *Digital 1–6* — Black23 pins 10, 1, 2, 3, 9, 11 (and most analog pins too) | the sensor's own: 5 V or 12 V |
| Knock | 2 | Knock input 1 White 34, Knock input 2 White 35 | no |
| CAN sensor (wideband, EGT, dash speed) | 2 | CAN High/Low Black23 pins 17/16, second bus Black23 pins 22/21 | no: the sensor's controller has its own supply |
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (Analog Volt and Analog Temp pins, ts_name list, knock inputs 34 and 35); firmware/config/boards/proteus/connectors/black23.yaml (VR pairs, Digital 1-6, CAN pairs) -->

!!! danger "12 V is the enemy of a 5 V sensor"
    Every ratiometric sensor on Proteus is a 5 V device: its supply pin, its signal pin and the ECU's
    input behind it expect a few volts. Wiring a sensor's supply to a 12 V feed, or letting a 12 V wire
    chafe onto a sensor harness, destroys the input and usually the sensor. Before the first key-on,
    check every 5 V supply pin against ground with a multimeter, and never probe an ECU pin with a test
    light — it draws far more current than a sensor supply is built for.
    <!-- src: firmware/config/boards/proteus/connectors/white35.yaml (+5 V supply pins and the separate 12 V protected sensor output) -->

## Supplies and returns

:material-circle:{ .level-basic } Basic

Proteus has **two** 5 V sensor supplies, and each one is brought out on three pins of the White
connector: **supply 1 on White 9, 21 and 32**, **supply 2 on White 10, 22 and 33**. They exist so you
can put part of the engine's sensors on one and the cabin's on the other: a shorted MAP sensor then
cannot also take down the pedal sensor's supply. Do not join them, never feed an external 5 V source
into them, and never put 12 V on them.

White **11 and 12** are a **protected 12 V output for sensors**, for sensors and actuators that want
battery voltage rather than 5 V. The board files list the pins but give **no current rating for any of
them**: the ratings live in the Proteus hardware documentation (the connector file points at
wiki.rusefi.com/Proteus-Manual), so size the load from that document and fuse the wire, not the pin.

**Sensor ground** is a separate set of pins: **GNDA on White 1–8, 23 and 29**. Every sensor return —
thermistor, MAP, TPS, pedal, pressure, Hall sensor ground — goes to one of those, each on its own wire.
The reason is in *Power, grounds and ground loops*: a return wire that also carries an injector, coil
or fan current lifts the sensor's ground by hundreds of millivolts, and the sensor reads that as
engine load or throttle.

<figure markdown>
  ![A MAP sensor, a two-track pedal sensor and a Hall trigger sensor, each with supply, signal and its own return, wired to named Proteus pins: White 9 and White 10 for the two 5 V supplies, White 13, 17 and 16 for signals, Black23 pin 10 for the digital signal and White 1, 23 and 2 for the returns. A red panel states the rules](../img/diagrams/wiring-sensors-supply-return.svg)
  <figcaption>Figure 2 — Supplies, signals and returns on a Proteus. Each wire lands on the pin named
  at the right; the two 5 V supplies are kept separate, and every return is its own wire to a GNDA pin.</figcaption>
</figure>

!!! tip "Calibrate and check with the ignition on, never on USB power"
    A ratiometric sensor's output is a *fraction* of the 5 V rail: the ECU assumes that rail is 5.0 V
    and does not measure it. With the ECU powered from USB only, the rail does not reach 5 V and every
    such sensor reads several percent low. The ECU decides the ignition is on when the voltage it
    measures on **Black23 pin 18** exceeds **6 V**, and TunerStudio's calibration buttons stay greyed out
    below that — that is the same rule, enforced for you.
    <!-- src: firmware/controllers/ignition_controller.cpp (isIgnVoltage: 6 V threshold on the battery sense input); firmware/tunerstudio/tunerstudio.template.ini (hasIgnitionVoltage conditions on the calibration command buttons) -->

## Which pin for which sensor

:material-circle:{ .level-basic } Basic

rusEFI starts life on a Proteus already pointed at sensible pins, so if you wire to the suggestions
below there is often nothing to configure at all. The names in the second column are exactly what the
TunerStudio input dropdowns offer.

| Sensor | TunerStudio input name | Proteus pin | Proteus's own note in the board file | Firmware default |
|---|---|---|---|---|
| Coolant (CLT) | *Analog Temp 3* | White 20 | "ECT CLT Coolant Sensor Input" | yes, assigned |
| Intake air (IAT) | *Analog Temp 2* | White 30 | "IAT Sensor Input" | yes, assigned |
| Other temperatures | *Analog Temp 1*, *Analog Temp 4* | White 19, 31 | "Analog Thermistor Input #1 / #4" | unassigned |
| MAP | *Analog Volt 1* | White 13 | "Analog Voltage Input #1 MAP" | yes, assigned |
| Throttle position, track 1 | *Analog Volt 2* | White 24 | "Suggested TPS 1 sensor input" | yes, assigned |
| Throttle position, track 2 | *Analog Volt 3* | White 14 | "Suggested TPS 2 / TPS1_2 sensor input" | unassigned until a preset or you assign it |
| Pedal, primary | *Analog Volt 9* | White 17 | "Suggested PPS input 1" | unassigned until you use the preset |
| Pedal, secondary | *Analog Volt 7* | White 16 | "Suggested PPS input 2" | unassigned until you use the preset |
| Wideband, analog input | *Analog Volt 10* | White 28 | "Auxiliary analog input 10" (the firmware's factory wideband input) | yes, assigned |
| Oil, fuel, A/C pressure, aux | *Analog Volt 4, 5, 6, 8, 11* | White 25, 15, 26, 27, 18 | "Auxiliary analog input" | unassigned |
| Crank | *Digital 1* or *VR 1* | Black23 pin 10, or Black23 pins 5/13 | "Digital trigger/switch input" | crank on *Digital 1*, cam unassigned |
| Cam (Hall) | *Digital 2* | Black23 pin 1 | "Digital trigger/switch input for instance Hall type CAM" | unassigned |
| Vehicle speed, flex, switches | *Digital 3–6* | Black23 pins 2, 3, 9, 11 | VSS, start button, general | unassigned |
| Knock | — (no pin choice) | White 34, White 35 | "Knock input 1", "Knock input 2" | knock sensing on, both channels |
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (pin functions and ts_name values); firmware/config/boards/proteus/connectors/black23.yaml (digital and VR pin functions and ts_name values); firmware/config/boards/proteus/board_configuration.cpp (setupDefaultSensorInputs: clt, iat, tps1_1, map.hwChannel, afr.hwChannel, triggerInputPins, camInputs) -->

Two things to notice in every input dropdown:

- **NONE** means the sensor is not configured, and the firmware simply does not initialise it — an
  unassigned input costs nothing and reports nothing.
- The analog dropdown also lists **Battery Sense**. That is **Black23 pin 18**, the ECU's own ignition power
  and battery measurement. Never wire a sensor there.
  <!-- src: firmware/config/boards/proteus/connectors/black23.yaml (pin 18 Battery Sense, ignition power); firmware/config/boards/proteus/board_configuration.cpp (setupVbatt: vbattAdcChannel) -->

Analog pins are not analog-only: the board file gives every *Analog Volt* and *Analog Temp* pin both
the analog and the switch-input class, and TunerStudio's digital input dropdowns list them. A slow
switch or a frequency input can therefore live on a spare *Analog Volt* pin if the analog pins you need
are all used.
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (class list switch_inputs and analog_inputs on every analog pin); firmware/tunerstudio/tunerstudio.template.ini (switch input pin list containing the Analog Volt and Analog Temp names) -->

!!! note "The ECU already rescales your analog inputs"
    Each Proteus analog input passes through a resistor divider on the board (5.6 kΩ in series, 10 kΩ
    to ground), and the firmware multiplies the sampled volts by **1.56** to undo it — the setting
    **analog input divider coefficient** `analogInputDividerCoefficient`, set by the board file. That is
    inside the ECU and is not yours to change; it is why a signal measured at the connector pin is
    reported correctly.
    <!-- src: firmware/config/boards/proteus/board_configuration.cpp (setupVbatt: divider coefficient 1.56, adcVcc 3.3); firmware/hw_layer/adc/adc_inputs.cpp (adcGetScaledVoltage applying the coefficient) -->

## The families, wire by wire

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

### Thermistors — two wires, no supply

:material-circle:{ .level-basic } Basic

A coolant, intake air, oil or fuel temperature sensor is a thermistor: two wires, no supply pin. Inside
the ECU the input is pulled up to 5 V through a resistor, and the sensor carries the current down to
sensor ground; from the voltage at the pin the firmware computes the resistance and then the
temperature. On Proteus that pull-up is **2700 Ω**, and the board file uses it for the coolant and
intake air inputs.

Wire it with two wires — one to the *Analog Temp* pin, one to a White GNDA pin. It does not matter
which way round the two wires go, and the lead resistance is negligible: 10 m of 0.5 mm² wire adds
about 0.7 Ω to the loop, against a sensor that is typically 100 Ω to 100 kΩ. What is *not* negligible
is choosing the wrong kind of pin: an *Analog Volt* input has no pull-up, so a thermistor wired there
reads either stuck high or stuck low.

!!! warning "A thermistor is not a sensor you can extend with any wire"
    Keep thermistor leads away from coil and injector wires: the pull-up makes the input high-impedance
    and it will pick up noise. If the reading jumps when the coils fire, treat it as a routing problem,
    not a calibration problem.

For the temperature dialogs other than coolant and intake air — **Sensors ▸ Oil temp sensor**, **Fuel
temp sensor**, **Ambient temp sensor**, **AuxTemp1/2 sensor** — the dialog asks for the **Pullup
resistor** of the pin you used. Enter the value that pin really has: the whole temperature scale is
computed from it. The Sensors chapter explains the three temperature-and-resistance pairs and the curve
fitted through them.
<!-- src: firmware/config/boards/proteus_meta.h (PROTEUS_DEFAULT_AT_PULLUP 2700); firmware/config/boards/proteus/board_configuration.cpp (proteus_boardConfigOverrides: clt and iat bias_resistor); firmware/controllers/sensors/converters/resistance_func.cpp (measuring the sensor's resistance from the pin voltage, short and open circuit detection); firmware/init/sensor/init_thermistors.cpp (configureTempSensor for the thermistor dialogs and their bias resistor) -->

### Three-wire 5 V sensors — MAP, TPS, pedal, pressures

:material-circle:{ .level-basic } Basic

A MAP, throttle position, pedal, oil pressure, fuel pressure or A/C pressure sensor is a three-wire
device: **5 V to a White 9/21/32 or 10/22/33 pin, signal to an *Analog Volt* pin, return to a White
GNDA pin**. The signal is a fraction of the supply — that is what *ratiometric* means — so the supply
wire is part of the measurement, not an afterthought. rusEFI turns the signal into a unit with a
straight line through two voltage points you give it (or with a built-in sensor model, which is the
same two points in a list).

**MAP** ships with **Sensor model** set to *MPX4250* and its input on **Analog Volt 1** (White 13), so
with that sensor fitted you only wire it. Beyond the electrical side, a MAP sensor also has a pressure
port: on a naturally aspirated engine that is a hose to the intake manifold; on a turbo engine the
hose must be oil-resistant and routed away from the exhaust, and it must have no kinks or it reads
manifold pressure that is not there.

A throttle or pedal sensor with **two tracks** needs four wires: one 5 V, one sensor ground, and one
signal each. Proteus's suggestions are *Analog Volt 2* and *Analog Volt 3* (White 24, 14) for the
throttle, and *Analog Volt 9* and *Analog Volt 7* (White 17, 16) for the pedal. rusEFI compares the two
tracks and refuses the reading if they disagree — see *Electronic throttle* for the calibration.

!!! example "One button sets up the throttle and pedal inputs for you"
    **Sensors ▸ TPS** has a wiring preset button, **Switch to Cable TPS**, which puts the throttle on
    Proteus's suggested single input and clears the second track and the pedal inputs — the right preset
    for a cable throttle with one position sensor. **Switch to PPS TPS** does the reverse, assigning the
    two throttle tracks and both pedal tracks for an electronic throttle. Both buttons are offered only
    while the engine has not run recently, and the preset writes the assignments without a burn, so
    check them in the dialog afterwards.
    <!-- src: firmware/controllers/algo/basic_configuration.cpp (applyBasicConfiguration: CableTps clears the secondary TPS and both PPS inputs, PpsTps assigns all four); firmware/config/boards/proteus/board_configuration.cpp (applyProteusBasicConfiguration passes PROTEUS_IN_TPS, TPS1_2, PPS, PPS2); firmware/tunerstudio/tunerstudio.template.ini (cmd_switch_to_cable_tps, cmd_switch_to_pps_tps and their engineTurnedRecently condition) -->

!!! warning "Relieve fuel pressure before you touch a fuel pressure sensor"
    A fuel pressure sensor sits on a line that can hold several bar with the engine off. Loosening a
    fitting sprays fuel over hot engine parts and bare electrical contacts. Relieve the pressure per the
    vehicle's procedure, work cold, and keep sparks and open flame away — the same rule as any fuel work
    in *Wiring basics*.

Wire these sensors in 0.5 mm² (20 AWG); screening is not needed for a slow 5 V signal, but the runs
should still stay away from coils, injector wires and the throttle motor cables — see *Shielding and
noise*.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (setupDefaultSensorInputs: map.hwChannel = Analog Volt 1, tps1_1AdcChannel = Analog Volt 2, afr.hwChannel = Analog Volt 10); firmware/controllers/algo/engine_configuration.cpp (factory map.sensor.type = MT_MPX4250); firmware/controllers/sensors/converters/linear_func.cpp (the two-point straight line and its too-low / too-high check); firmware/init/sensor/init_map.cpp (MAP input, filtering and the fast-MAP fallback) -->

### Switch inputs — clutch, brake, start button

:material-circle:{ .level-basic } Basic

A switch has two wires and no supply pin, and you decide what it switches. rusEFI reads the pin's level
and then applies the input's **mode**, so both conventions work:

| Convention | How to wire it | Mode to choose |
|---|---|---|
| Switch to ground (most cars) | one wire to the input pin, one to a White GNDA pin | **PULLUP** (the firmware's default for the clutch and brake inputs) |
| Switch to positive | one wire to the switched positive, one to the input pin | **INVERTED PULLDOWN** |

The settings are on **Sensors ▸ Chassis sensors ▸ Misc sensors** — **Clutch Down** `clutchDownPin` with
**Clutch Down mode** `clutchDownPinMode`, **Brake Pedal** `brakePedalPin` with **Brake Pedal Mode** —
and the modes are *DEFAULT*, *PULLUP*, *PULLDOWN* and the three *INVERTED* variants. A
*PULLUP* / *PULLDOWN* mode uses the microcontroller's own weak pull resistor, so no external resistor
is needed. Proteus labels **Black23 pin 3** (*Digital 4*) for a start button.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (otherSensorInputs panel: Clutch Down, Clutch Down mode, Brake Pedal, Brake Pedal Mode, and the pin_input_mode_e labels); firmware/hw_layer/io_pins.cpp (getInputMode turning PULLUP and PULLDOWN into the chip's own pull resistor); firmware/config/boards/proteus/connectors/black23.yaml (pin 3 noted for a start button) -->

!!! warning "Check the board documentation before you switch 12 V onto an input pin"
    The Proteus connector files call the *Digital* pins "Digital trigger/switch input" but give them no
    voltage rating. Wiring a switch that feeds battery voltage into such a pin is a common source of
    dead inputs and dead boards. Confirm the allowable signal voltage in the Proteus hardware
    documentation, or wire the switch to ground and use a *PULLUP* mode instead.
    <!-- src: firmware/config/boards/proteus/connectors/black23.yaml (digital pin functions, no voltage rating given); firmware/controllers/algo/engine_configuration.cpp (clutchDownPinMode and brakePedalPinMode default to PI_PULLUP); firmware/integration/rusefi_config.txt (pin_input_mode_e input modes) -->

### Crank and cam: VR against Hall

:material-circle:{ .level-intermediate } Intermediate

Two kinds of crank and cam sensor reach the ECU in completely different ways, and the pins are
different too.

A **VR** (variable reluctance) pick-up is a coil and a magnet: two wires, no supply, and an AC signal
that grows with engine speed. Proteus gives it a **differential pair**: *VR 1* is **Black23 pin 5 (+)** and
**Black23 pin 13 (−)**, *VR 2* is **Black23 pin 4 (+)** and **Black23 pin 12 (−)**. There are exactly two VR inputs, so
beyond crank plus cam you use Hall sensors.

A **Hall** sensor has three wires — supply, signal, ground — and puts out a square wave, so it can read
at zero RPM where a VR sensor cannot. Its signal goes to one of the *Digital 1–6* inputs: **Black23 pin 10**
(*Digital 1*) is the firmware's factory crank input, and **Black23 pin 1** (*Digital 2*) is the board's
suggestion for a cam. Its supply is whatever the sensor is built for, the 5 V supplies or the protected
12 V output on White 11, and its ground returns to a White GNDA pin.

<figure markdown>
  ![A 2-wire VR pick-up wired as a twisted shielded pair to Black23 pin 5 and Black23 pin 13, and a 3-wire Hall sensor wired to a Digital input with its 5 V or protected 12 V supply and its own GNDA return; a red panel explains the symptom of reversed VR wires and the Primary Edge setting](../img/diagrams/wiring-sensors-crank-vr-vs-hall.svg)
  <figcaption>Figure 3 — The same 60-tooth wheel read two ways. Note what the VR sensor has and does
  not need: a pair, a twist, a shield, and no supply at all.</figcaption>
</figure>

Use **shielded twisted pair** for a VR sensor and keep the run away from coil wires and injector wires;
the shield terminates at the ECU end only. That advice, and the reason for it, is in *Shielding and
noise*; what the firmware does with the teeth is in the *Trigger* chapter, including the noise filter
and the trigger error counters.

Polarity matters more than people expect. Swap the two VR wires and the firmware still counts the same
number of edges, but for a wheel with one missing tooth the gap appears in the wrong place: a *short*
gap with a *long tooth* before it, and an apparent timing shift that changes with engine speed. Either
swap the wires, or leave them and change **Primary Edge** `invertPrimaryTriggerSignal` on
**Setup ▸ Trigger** — then re-check the timing. Cam inputs have their own edge settings on the same
dialog (**intake Cam Edge Select** `invertCamVVTSignal`, **exhaust Cam Edge Select**).
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (Variable Reluctance positive and negative pairs, Digital 1-6); firmware/config/boards/proteus/board_configuration.cpp (setupDefaultSensorInputs: triggerInputPins[0] = PROTEUS_DIGITAL_1, camInputs[0] unassigned); firmware/config/boards/proteus_meta.h (PROTEUS_VR_1, PROTEUS_VR_2, PROTEUS_DIGITAL_1..6); firmware/tunerstudio/tunerstudio.template.ini (trigger_primary panel: Crank Sensor (Primary channel), Primary Edge, Cam Inputs panel) -->

### Knock — two fixed inputs, shielded and short

:material-circle:{ .level-intermediate } Intermediate

A knock sensor is a piezo element bolted to the block: two wires, no supply, and a signal that is a
few millivolts of ringing at the engine's own resonant frequency. Proteus has **two** of them, **White
34 (Knock input 1)** and **White 35 (Knock input 2)**, and a Proteus starts with **Knock sensing**
`enableSoftwareKnock` **on**.

Those two pins are the only knock inputs there are. The board's knock configuration fixes which
on-chip ADC pins the two channels use, and the firmware notes plainly that unlike other input kinds
there is no channel flexibility — you cannot move knock to another pin in TunerStudio, because the
sampling runs on a dedicated fast ADC at a fixed rate.

What you *can* choose is which cylinders each sensor watches. On **Ignition ▸ Knock Control**, the
panel **Select the nearest sensor for each cylinder** sets **Cylinder 1…12** to **Channel 1** or
**Channel 2**: an inline four uses one sensor on Channel 1 for all cylinders, a V8 with one sensor per
bank splits them. With one sensor fitted, leave every cylinder on **Channel 1**.

Wire knock with the **shortest shielded cable** you can manage, twisted inside the shield, with the
shield landing at the ECU end. Interference inside the knock window either reads as knock that is not
happening, or — more often — raises the noise floor until the calibrator raises the threshold, which is
how real detonation gets hidden. rusEFI listens in a window that by default starts **20°** after the
reference and lasts **45°** of crank, against a threshold that varies with engine speed and is **−20 dB** by default. The Knock
chapter covers detection and tuning; *Shielding and noise* covers why the cable decides the result.

!!! danger "Never chase false knock by raising the threshold"
    A knock level that is high with a bad cable looks identical to a knock level that is high because
    the engine is detonating. Raising the threshold silences both — and detonation under boost destroys
    pistons in seconds. Fix the cable, the routing and the sensor mounting first, and only then touch
    the threshold.
    <!-- src: firmware/config/boards/proteus/knock_config.h (the knock ADC channels, pins and sample rate); firmware/controllers/sensors/impl/software_knock.cpp (efiSetPadMode for knock ch1 and ch2 and the note that there is no channel flexibility, band-pass filtering); firmware/config/boards/proteus/connectors/white35.yaml (pins 34 and 35 Knock input 1 and 2); firmware/config/boards/proteus/board_configuration.cpp (proteus_boardDefaultConfiguration: enableSoftwareKnock); firmware/controllers/algo/engine_configuration.cpp (setDefaultEngineNoiseTable: window start 20 degrees, duration 45 degrees, base noise −20 dB); firmware/controllers/engine_cycle/knock_controller.cpp (getCylinderKnockBank maps a cylinder to a knock channel) -->

### Wideband — three ways to see lambda

:material-circle:{ .level-intermediate } Intermediate → :material-circle:{ .level-advanced } Advanced

A wideband oxygen sensor is always driven by its own controller: the sensor needs a heater and pumping
circuitry the ECU does not provide. What varies is how the controller tells the ECU the answer.

**Over CAN** — the rusEFI Wideband Tools controller or an AEM X-Series — nothing but two wires reaches
the ECU: **CAN High on Black23 pin 17 and CAN Low on Black23 pin 16**, or the second bus on **Black23 pin 22 / Black23 pin 21**.
Turn it on with **Enable CAN Wideband** `enableAemXSeries` on **Sensors ▸ CAN O2 sensors**, choose the
bus with **Wideband CAN bus** `widebandOnSecondBus` (*CAN1* or *CAN2*), and identify each controller
with **UEGO type** `canWbo1_type` (*RusEFI*, *AEM X-series* or *Disabled/Analog*) plus **RusEFI WBO ID**
`canWbo1_reId` or **AEM ID** `canWbo1_aemId`. rusEFI treats a controller that stops talking as a fault,
which is why a broken CAN wire shows up as a missing lambda reading rather than a wrong one. If the
**rusEFI Wideband Tools** entry is missing from the **Sensors** menu, CAN send and receive are off:
switch them on under **CAN-bus ▸ CAN Bus Settings** first.

**Over an analog input** — any wideband controller that outputs a proportional voltage — the ECU gets
one wire on an *Analog Volt* pin, and Proteus's factory choice is **Analog Volt 10** (**White 28**). The
dialog is **Sensors ▸ Analog O2 sensor**: pick a **Type** (`afr_type`: *BPSX*, *Innovate*, *14Point7*,
*PLX*, *Custom*, *AEM*, plus a *Narrow Band* preset in the **O2 Type** selector) or enter the two
scaling points yourself — **low voltage** `afr_v1` → **low value** `afr_value1`, **high voltage**
`afr_v2` → **high value** `afr_value2`. The analog input is used only while the CAN wideband is off;
the dialog says so in its own words: *"Disable CAN O2 sensor(s) to enable this settings"*. The same
dialog offers **Narrowband Heater output** `o2heaterPin` — an ECU **output** pin that switches a
narrow-band sensor's heater on when the engine runs.

**A narrow-band O2** from an old car is wired the same way as the analog case, with the *Narrow Band*
preset: it tells the ECU rich or lean around stoichiometric, not how far off.

Whichever route you choose, the controller is a box of its own with its own fused 12 V supply and its
own ground return, mounted away from heat and water. Keep its sensor cable away from
coil wires, and never let the heater feed or battery voltage near an ECU pin.

<figure markdown>
  ![One or two knock sensors on White 34 and White 35 with short shielded cable; a wideband controller reporting over CAN to Black23 pin 17 and Black23 pin 16; a wideband controller with an analog output on White 28 Analog Volt 10 and its ground on White 3. A red panel states that the heater is never driven by the ECU](../img/diagrams/wiring-sensors-knock-wideband.svg)
  <figcaption>Figure 4 — The two fussiest connections on the engine. The knock inputs are fixed and
  need a short shielded cable; the wideband either lives on the CAN bus or arrives as one scaled voltage.</figcaption>
</figure>

!!! warning "Force O2 sensor heating is a workshop switch"
    **Force O2 sensor heating** `forceO2Heating` runs the sensor's heater with the engine stopped, and
    TunerStudio's own warning on that dialog is that it is for testing only and *"can damage your
    sensor"* if left enabled. Turn it off when you are done.
    <!-- src: firmware/controllers/sensors/can_sensor.h (CAN-fed sensors and their timeout handling); firmware/tunerstudio/tunerstudio.template.ini (egoSettings panel: Enable CAN Wideband, Wideband CAN bus, UEGO type, RusEFI WBO ID, AEM ID, Force O2 sensor heating and its warning lines, Restart all WBO); firmware/config/boards/proteus/board_configuration.cpp (afr.hwChannel = Analog Volt 10 with the wideband note); firmware/tunerstudio/tunerstudio.template.ini (analogEgoSettings panel, O2 Type presets, Narrowband Heater output); firmware/integration/rusefi_config.txt (afr_type and o2heaterPin) -->

## Checking the wiring

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

Do this with the engine stopped, the fuel pump and coil fuses **out**, and the ECU on **12 V with the
ignition on** — never on USB power alone, for the reason given under *Supplies and returns*.

1. **Measure the supply at the sensor**, with the connector mated and a back-probed pin (or at the
   sensor itself): 5 V supply to sensor ground should read very close to 5 V. Anything near 4.4 V means
   you are looking at a USB-powered ECU, or a supply that is loaded down by a short.
2. **Coolant and intake air**: open **Sensors ▸ CLT sensor** and watch the raw input and the computed
   resistance while you compare the sensor with a multimeter. An unconnected thermistor input is
   reported as an open circuit, and a sensor leg that is not returning to GNDA reads as too high.

    <!-- shot: img/ts/wiring-sensors-clt.png | Sensors ▸ CLT sensor | Proteus F7, ignition on (12 V), engine cold and stopped, Input channel Analog Temp 3, raw CLT voltage gauge near 3 V, CLT resistance channel a few thousand ohm, CLT error indicator off | Figure 5 — A coolant sensor wired correctly: a mid-range raw voltage and a plausible resistance. -->

3. **MAP**: with the ignition on and the engine stopped, **Sensors ▸ MAP sensor** should read close to
   your altitude — around 100 kPa at sea level. A reading 5–10 % low is the low 5 V rail; a reading
   that never moves is the wrong input pin, and a reading that goes silly as soon as you crank the
   starter is a supply shared with something else.

    <!-- shot: img/ts/wiring-sensors-map.png | Sensors ▸ MAP sensor | Proteus F7, ignition on, engine stopped, Input pin Analog Volt 1, Sensor model MPX4250, MAP gauge near 100 kPa, Good MAP Input indicator green | Figure 6 — Key-on MAP: with the engine stopped the manifold reads the atmosphere. -->

4. **Throttle and pedal**: hold the throttle half open and look at the raw TPS reading; move the
   throttle slowly through its full travel. The reading must rise smoothly from end to end with no
   flat step (a flat step is a worn track or a chafed wire), and both tracks of a two-track sensor must
   move the whole time.

    <!-- shot: img/ts/wiring-sensors-tps.png | Sensors ▸ TPS | Proteus F7, ignition on, engine stopped, cable throttle: Primary sensor input Analog Volt 2, Secondary sensor input NONE, raw TPS voltage gauge about 2.5 V with the plate held mid-travel | Figure 7 — One track held mid-travel: a mid-range voltage proves the sensor, its 5 V supply and its return are all alive. -->

5. **Crank and cam**: with the fuel and coil fuses still out, crank the engine and watch the RPM
   channel. No RPM at all means the wrong input pin, no supply to a Hall sensor, or an engine that is
   not turning over fast enough for a VR signal. Assignments live on **Setup ▸ Trigger** —
   **Crank Sensor (Primary channel)** `triggerInputPins1` and, for a cam, **Cam sensor bank 1 intake**
   `camInputs1`.

    <!-- shot: img/ts/wiring-sensors-trigger.png | Setup ▸ Trigger | Proteus F7, ignition on, engine stopped: Primary Trigger panel with Trigger type set to the fitted 60-2 type, Crank Sensor (Primary channel) VR 1, Primary Edge Rising; Cam Inputs panel with Cam sensor bank 1 intake Digital 2, dropdowns closed | Figure 8 — Crank on a VR pair, cam on a digital input: the two assignments that decide whether an RPM reading appears at all. -->

    If the teeth arrive but the shape is odd, this is done in the rusEFI console: open the **Engine
    Sniffer** tab, crank the engine and look at the wave. A VR input whose two wires are reversed shows
    up there as an inverted wave, and a Hall sensor picking up ignition noise shows spikes. TunerStudio
    cannot show you the raw wave.
6. **Knock**: with the engine running at idle, watch the per-cylinder knock levels on TunerStudio's
   gauges. The level should sit below the threshold, and should stand out clearly when you tap the
   cylinder head lightly with a long socket extension.

    To see *why* a level is high, this is done in the rusEFI console: open the **Knock Analyzer** tab,
    which shows the spectrum — that is where mains hum, injector noise and real knock ringing stop
    looking alike.

    <!-- shot: img/ts/wiring-sensors-knock.png | Ignition ▸ Knock Control | Proteus F7, engine idling on 12 V: Sense panel with Knock sensing on, Detection Window Start 20, Sampling Duration 45, the panel Select the nearest sensor for each cylinder with Cylinder 1 to Cylinder 4 on Channel 1, knock level gauge visible below the threshold | Figure 9 — Knock wiring that works: the level sits quietly under the threshold at idle. -->

7. **Wideband**: after the controller's warm-up the reading must move with the mixture. On the CAN
   route, the **Sensors ▸ CAN O2 sensors** indicators say what the controller is doing (preheat,
   warmup, closed loop, heating failed); on the analog route, a reading still pinned at one end of the
   scale after the sensor has warmed up is a scaling or supply problem, not an engine problem.

    <!-- shot: img/ts/wiring-sensors-wideband-tools.png | Sensors ▸ rusEFI Wideband Tools | Proteus F7, CAN read and write enabled, engine idling warm, wideband 1 on CAN1 reporting closed loop, RusEFI type so the auto-remap panel is visible | Figure 10 — The wideband controller answering over CAN, with the auto-remap panel for a RusEFI-type controller. -->

## Worked examples

:material-circle:{ .level-intermediate } Intermediate

### Example 1 — Naturally aspirated four-cylinder, VR crank and Hall cam

The whole sensor side of a simple sequential engine on a Proteus F7:

| Sensor | Proteus pins | Supply | Return | Cable |
|---|---|---|---|---|
| Coolant | White 20 (*Analog Temp 3*) | from inside the ECU | White 2 | 2-wire, 0.5 mm² |
| Intake air | White 30 (*Analog Temp 2*) | from inside the ECU | White 4 | 2-wire, 0.5 mm² |
| MAP (1-bar sensor) | White 13 (*Analog Volt 1*) | White 9 (supply 1) | White 1 | 3-wire, 0.5 mm² |
| TPS (one track) | White 24 (*Analog Volt 2*) | White 9 (supply 1) | White 3 | 3-wire, 0.5 mm² |
| Crank, VR 60-2 | Black23 pin 5 (+) / Black23 pin 13 (−) | none | — (differential) | shielded twisted pair |
| Cam, Hall | Black23 pin 1 (*Digital 2*) | White 9 (supply 1) | White 5 | 3-wire, 0.5 mm² |
| Knock, one sensor | White 34 (Knock input 1) | none | — (shield) | short shielded pair |
| Wideband, CAN | Black23 pin 17 / Black23 pin 16 | controller's own fused 12 V | controller's own | twisted pair, terminated |

Why those choices: the coolant, intake air, MAP, TPS and crank pins are exactly rusEFI's factory
assignments on a Proteus, so those five need no configuration at all. Two things do need a setting and a
**Burn**: the cam input (**Cam sensor bank 1 intake** `camInputs1` = *Digital 2*) and the CAN wideband
(**Enable CAN Wideband**, plus its **UEGO type**). The four 5 V sensors all sit on **supply 1**, which is
fine for a four-cylinder with this few loads; a longer harness with the pedal and cabin sensors on
supply 2 keeps an engine-bay short from taking the pedal down with it. The VR pair is the only
differential signal here, so it is the only one that needs a twist and a shield along its whole length.

### Example 2 — Boosted four-cylinder, two knock channels, AEM X-Series

A turbo engine adds pressure range, more sensors, and one more knock input:

| Item | Setting / pin | Why |
|---|---|---|
| 3-bar MAP | *Analog Volt 1* (White 13), **Sensor model** Custom, points 0.5 V → 0 kPa and 4.5 V → 300 kPa | a 1-bar model saturates around 100 kPa; boost needs a 3-bar sensor and its own two points |
| MAP fault limits | **Fault if reading below** 5 kPa, **Fault if reading above** about 320 kPa | a sensor that reads boost with the engine off is a wiring or calibration slip, and the limit is what tells you |
| Oil pressure | *Analog Volt 4* (White 25), supply from White 10 (supply 2) | spare analog input, and the second 5 V supply so a shorted oil sensor cannot kill the MAP |
| Knock, one per bank | White 34 and White 35; **Cylinder 1–4** on Channel 1, **Cylinder 5–8** on Channel 2 for a V8 | the mapping panel tells the ECU which sensor is nearest each cylinder |
| Wideband | **Sensors ▸ CAN O2 sensors**: **Enable CAN Wideband** on, **Wideband CAN bus** *CAN2*, **UEGO type** *AEM X-series*, **AEM ID** as the controller's setting | keeps the wideband off the analog inputs, and off the CAN1 bus if that is already busy |
| Two knock sensors, four cylinders | all cylinders on **Channel 1**, second input unused | one sensor per bank is enough; two sensors on one bank just double the noise you must sort out |

The MAP points in this example are the usual two-point shape for a 3-bar sensor: **rusEFI draws a
straight line through whatever two points you give it**, so what matters is that the voltages come from
the sensor's own data sheet and that the supply really is 5 V when you check them.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (mapSensorAnalog and mapCustomCal panels, mapCommon fault limits); firmware/integration/rusefi_config.txt (mapErrorDetectionTooLow, mapErrorDetectionTooHigh); firmware/controllers/sensors/converters/linear_func.cpp (the two-point line); firmware/tunerstudio/tunerstudio.template.ini (uegoCan panel and canWbo1 fields, knockCylinderMapping panel) -->

### Example 3 — How far can a thermistor lead go?

The pull-up that makes a thermistor work lives in the ECU, so the lead resistance simply adds to the
sensor's resistance: 10 m of 0.5 mm² wire is about 0.7 Ω in the loop. Against a sensor that is 2.5 kΩ
at room temperature that is 0.03 % — nothing. The same 20 m of thin wire in a *MAP* sensor's supply or
return is a different story, because a ratiometric sensor carries current through those wires and the
drop comes off your 5 V reference. That is why the *Power, grounds and ground loops* chapter insists on
short, heavy-enough sensor returns for current-carrying sensors while a thermistor lead can be long.

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-advanced } Advanced

| Symptom | Likely cause | Check |
|---|---|---|
| Every 5 V sensor reads several percent low | the ECU is on USB power, or a 5 V supply is loaded down | ignition on, 12 V; measure the supply at the sensor |
| One sensor reads silly, the others are fine | wrong pin family, or the input is not the one you wired | the dropdown name against the connector pin in the table above |
| Temperature reads the maximum, or reports *input too high* | the sensor's return is not on a GNDA pin, or the connector is unplugged | continuity from the sensor's ground pin to a White GNDA pin |
| Temperature reads plausible but wrong | the three calibration pairs are for another sensor, or the **Pullup resistor** is wrong for that pin | compare the ECU's computed resistance with a multimeter on the sensor |
| Thermistor reads fine but jumps with every spark | lead routed with the coil or injector wires | re-route, cross them at right angles |
| MAP or TPS jumps with engine speed at a steady throttle | sensor return shared with a load, or the supply shared with another sensor | separate return to GNDA, separate supply pin |
| TPS or pedal reports an error at one end of travel | the two tracks disagree, or a calibration grabbed on a low 5 V rail | re-check with the ignition on (see *Electronic throttle*) |
| No RPM while cranking | Hall sensor unpowered, wrong *Digital* pin, VR signal too weak at cranking | supply at the sensor, the input assignment on **Setup ▸ Trigger**, faster cranking |
| A missing-tooth wheel shows a short gap and a long tooth before it | the two VR wires are reversed | swap the pair, or change **Primary Edge**, then re-check timing |
| RPM appears and vanishes, trigger errors climb | VR cable run next to coil wires, no shield, shield grounded at both ends | *Shielding and noise* |
| False knock events at idle | interference in the knock window, long unshielded knock cable, loose sensor mounting | short shielded cable, correct mounting torque per the sensor's data sheet, knock analyzer |
| Knock level high, no audible knock | the sensor is not clamped to the block, or a chafed shield is acting as an antenna | mounting, cable, then the analyzer — never raise the threshold first |
| Wideband never moves off its cold or pinned value | CAN wideband enabled while the sensor is on the analog input, wrong **Type** scaling, controller unpowered | the dialog's own note about disabling the CAN sensors, the four scaling values, the controller's 12 V |
| Wideband reading wanders a full point with no engine change | sensor ground and ECU ground reference differ, or the signal wire runs beside an ignition wire | single-point grounding, re-route |
| A pin that used to work is dead after a rewiring | the old assignment is still in the calibration (the assignment, not the wire) | **NONE**, burn, then the new assignment |

## Settings reference

These dialogs decide what the ECU expects to find on the pins you wired. They are generated from the
official Proteus F7 ini; the same tables list every field with its units, range and tooltip.

### CLT sensor (Sensors ▸ CLT sensor)

--8<-- "reference/settings/_cltSensor.table.md"

### IAT sensor (Sensors ▸ IAT sensor)

--8<-- "reference/settings/_iatSensorDialog.table.md"

### MAP sensor (Sensors ▸ MAP sensor)

--8<-- "reference/settings/_mapSettings.table.md"

### TPS (Sensors ▸ TPS)

--8<-- "reference/settings/_tpsSensor.table.md"

### Accelerator pedal (Sensors ▸ Accelerator pedal)

--8<-- "reference/settings/_pedalSensor.table.md"

### Misc sensors (Sensors ▸ Chassis sensors ▸ Misc sensors)

--8<-- "reference/settings/_otherSensorInputs.table.md"

### Trigger (Setup ▸ Trigger)

--8<-- "reference/settings/_triggerConfiguration.table.md"

### Knock Control (Ignition ▸ Knock Control)

--8<-- "reference/settings/_softwareKnock.table.md"

### CAN O2 sensors (Sensors ▸ CAN O2 sensors)

--8<-- "reference/settings/_egoSettings.table.md"

### Analog O2 sensor (Sensors ▸ Analog O2 sensor)

--8<-- "reference/settings/_analogEgoSettings.table.md"

## Related

- [Wiring basics](wiring-basics.md) — wire sizes, terminals, crimping, and the pre-power checklist
- [Power, grounds and ground loops](power-grounds.md) — the two kinds of ground, the 5 V supplies, and why a shared return corrupts a sensor
- [Shielding and noise](shielding-noise.md) — VR and knock cables: twisting, screening at one end, and keeping away from the coils
- [The official boards](official-boards.md) — the full Proteus F7 pinout table for all three connectors
- [Sensors and calibration](../part3/sensors.md) — what each dialog does, thermistor curves, frequency inputs, sensor faults and fallbacks
- [Trigger](../part3/trigger.md) — trigger wheels, input assignment, noise filtering and trigger error counters
- [Electronic throttle](../part3/electronic-throttle.md) — the two-track throttle and pedal calibration
- [Knock](../part3/knock.md) — detection windows, thresholds and gain tables
