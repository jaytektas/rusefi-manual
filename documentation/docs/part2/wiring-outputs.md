# Wiring outputs

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-advanced } Advanced

> **In one sentence:** every output on a Proteus is a switch inside the ECU — nearly all of them switch
> the *minus* side of the load — so each actuator wire needs three decisions: which pin, where the load's
> plus side comes from, and what gives an inductive load somewhere to dump its magnetic field when the ECU
> lets go.

## Overview

:material-circle:{ .level-basic } Basic

This chapter is about the wires. *Wiring basics* covers the wire, the terminal and the crimp;
*Power, grounds and ground loops* covers the battery feed, the main relay and the two kinds of ground; the
Sensors side of the connector is in [Wiring sensors](wiring-sensors.md). What the settings mean — which
dialog owns which pin, and what the firmware does with each output — is the Outputs chapter's job. Here you
learn what an output pin electrically *is*, so you can wire an injector, a coil, a relay or a throttle
motor without guessing.

One idea carries the whole chapter. A Proteus output is not a source of power you connect a load to. It is a
switch, and for the sixteen low-side and twelve ignition outputs that switch connects the load to **ground**.
The load's plus side has to come from somewhere else — the main relay's output — and the ECU's job is to
complete the circuit for exactly as long as it decides.

<figure markdown>
  ![Battery plus through a fuse to the main relay contact; the relay's switched 12 V feeds the injectors, the coils and Proteus Black23 pin 23; the main relay coil is switched to ground by Lowside 12 on Black35 pin 21; the fuel pump relay coil, with a diode across it, is fed from the switched 12 V and switched by Lowside 10 on Black35 pin 20; an injector is fed from the switched 12 V and switched by Lowside 1 on Black35 pin 3](../img/diagrams/wiring-outputs-relay.svg)
  <figcaption>Figure 1 — The three output jobs a Proteus does most often. Note where the 12 V comes from, and
  that the ECU only ever switches the small side of the circuit: the relay coil, never the fan or the pump
  itself.</figcaption>
</figure>

The connector files sort the outputs into families for you, and the family tells you what you may connect:

| Family | What the switch does | Proteus pins | What the Proteus hardware documentation states |
|---|---|---|---|
| 16 low-side outputs | completes the load's path **to ground** | Black 35 — *Lowside 1 … 16* | 16 low-side drivers, **4 A** each |
| 12 ignition outputs | a **logic-level** trigger per coil | Black 35 — *Ign 1 … 12* (pins 35, 34, 22, 33, 32, 31, 30, 29, 28, 27, 26, 25) | 12 outputs described as "5 V ignition (or general purpose)" |
| 4 high-side outputs | supplies **plus** to the load | Black 35 — *Highside 1 … 4* (pins 2, 1, 13, 14) | 4 outputs, **12 V 3 A** |
| 2 H-bridges | drive **both** sides of a motor | Black 23 — pins 7 and 6 (ETB 1 + / −), pins 15 and 8 (ETB 2 + / −) | dual H-bridges for electronic throttle, also usable for a stepper idle valve |
| 2 protected 12 V outputs | small plus-side loads | White 11 and 12 | protected, no figure given in the board files |

<!-- src: firmware/config/boards/proteus/connectors/black35.yaml (Lowside, Ign and Highside pins with their type values inj, ls, ign and hs); firmware/config/boards/proteus/connectors/black23.yaml (ETB 1 and 2 pins 6, 7, 8, 15, and the board_url that points at the Proteus Manual); firmware/config/boards/proteus/connectors/white35.yaml (the two protected 12 V sensor outputs) -->

!!! info "Where the current figures come from"
    The rusEFI repository names every pin and says which kind of driver it is, but it does not print an
    amperage figure. The current ratings above are the Proteus hardware documentation's own feature list —
    the Proteus Manual that rusEFI's own board files point at (`board_url` in the connector file, and the
    `MAIN_HELP_URL` the board's TunerStudio menu opens). Size every load from that document, and fuse the
    **wire**, not the pin: a driver rated 4 A is not a fuse, and nothing on the board will save a 20 A short.
    <!-- src: firmware/config/boards/proteus/connectors/black23.yaml (board_url: the Proteus Manual); firmware/config/boards/proteus/prepend.txt (MAIN_HELP_URL) -->

!!! danger "These wires move hardware and carry fuel, sparks and amps"
    Everything in this chapter energises a real wire. An injector test pressurises a fuel system: a loose
    fitting sprays fuel onto a hot exhaust. A spark test delivers enough voltage to jump a gap and to burn a
    coil that has no load. A throttle motor can pull a throttle plate shut or open against your fingers. Do
    the first tests with the engine off, the fuel lines checked, the coil leads seated, and the fan area
    clear. Work with the ECU on **12 V with the ignition on**, never on USB power alone: the main relay, the
    fuel pump and every bench test key off the ignition voltage the ECU measures on **Black23 pin 18**.
    <!-- src: firmware/controllers/ignition_controller.cpp (isIgnVoltage); firmware/controllers/actuators/main_relay.cpp (mainRelayState follows hasIgnitionVoltage) -->

## Five rules for every output

:material-circle:{ .level-basic } Basic

1. **The ECU switches ground.** On a low-side output the load is permanently connected to switched 12 V and
   the pin pulls its other terminal down when the feature wants it running. That is why the board files call
   these pins *Lowside*, and why an injector or relay is wired with its plus lead to the main relay output and
   its minus lead to the ECU.
   <!-- src: firmware/config/boards/proteus/connectors/black35.yaml (the Lowside pins and their ls and inj types) -->
2. **The load's plus comes from the main relay.** Injectors, coils and everything else that runs only when the
   engine runs are fed from the relay's contacts, not straight from the battery. The same switched feed also
   goes to **Black23 pin 23**, whose own board-file description is "Power supply from main relay … Supplies
   power to electronic throttle drivers and high side outputs".
   <!-- src: firmware/config/boards/proteus/connectors/black23.yaml (pin 23 function text) -->
3. **A relay carries the load; the ECU carries only the relay coil.** A fan, a fuel pump, an electric water
   pump or a headlamp is never wired to an ECU pin. The pin switches the relay coil — a fraction of an amp —
   and the relay's contacts carry the load on a fused wire of its own.
   <!-- src: firmware/config/boards/proteus/board_configuration.cpp (proteus_boardDefaultConfiguration: mainRelayPin, fanPin, fuelPumpPin) -->
4. **Every coil-shaped load needs a flyback path.** An injector, a relay coil, a solenoid and an idle valve are
   inductors. When the switch opens, the collapsing field tries to keep the current flowing and lifts the pin
   to a voltage far above 12 V. Somewhere across that coil there has to be a diode, or a clamp, or a driver
   designed to absorb it — see *Relays, solenoids and flyback*.
   <!-- src: firmware/config/boards/proteus/connectors/black35.yaml (Lowside 13, 14, 15 and 16 marked "(with flyback)") -->
5. **One pin, one job.** Two features on the same pin is a fatal error that shuts the outputs down, not a
   warning. The pin numbers in this chapter matter because several Proteus pins have two jobs, and you are the
   one who decides which one they get.
   <!-- src: firmware/hw_layer/pin_repository.cpp (brain_pin_markUsed: the critical error naming both owners) -->

## Injectors: switching fuel at the minus side

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

<figure markdown>
  ![Battery plus through a fuse to the main relay contact and on to a bus that feeds the plus side of four injectors; each injector's minus side goes to its own Proteus Black35 pin — 3, 15, 4 and 16 — where a low-side driver switches it to ground. Side panels give the 4 A driver rating and the dual-purpose Lowside 10, 11 and 12 pins](../img/diagrams/wiring-outputs-injectors.svg)
  <figcaption>Figure 2 — Four injectors on a Proteus. Output number is cylinder number: rusEFI handles the
  firing order, so you wire by cylinder and the firmware decides which ones open together.</figcaption>
</figure>

A Proteus has twelve injector drivers, one per cylinder, and they are low-side switches: **12 V to the
injector's plus terminal, the ECU's pin to the minus terminal.** The factory assignment puts injectors 1 to 12
on the pins below, and it is the assignment you should use unless you have a very good reason not to. TunerStudio's
note above the panel says the rule: *"# wire each output to the corresponding cylinder number"*.

| Injection Output (TunerStudio) | Proteus pin name | Black35 pin | What the board files call that pin |
|---|---|---|---|
| Injection Output 1 | *Lowside 1* | 3 | Injector 1 |
| Injection Output 2 | *Lowside 2* | 15 | Injector 2 |
| Injection Output 3 | *Lowside 3* | 4 | Injector 3 |
| Injection Output 4 | *Lowside 4* | 16 | Injector 4 |
| Injection Output 5 | *Lowside 5* | 5 | Injector 5 |
| Injection Output 6 | *Lowside 6* | 6 | Injector 6 |
| Injection Output 7 | *Lowside 7* | 7 | Injector 7 |
| Injection Output 8 | *Lowside 8* | 19 | Injector 8 |
| Injection Output 9 | *Lowside 9* | 8 | Injector 9 |
| Injection Output 10 | *Lowside 10* | 20 | Injector #10 **or** Fuel Pump relay |
| Injection Output 11 | *Lowside 11* | 9 | Injector #11 **or** radiator fan relay |
| Injection Output 12 | *Lowside 12* | 21 | Injector #12 **or** Main relay |

<!-- src: firmware/config/boards/proteus/board_configuration.cpp (injPins: Lowside 1 to 12 assigned as the injection outputs); firmware/config/boards/proteus_meta.h (PROTEUS_LS_1 … LS_16 with their black35 pin numbers in the comments); firmware/config/boards/proteus/connectors/black35.yaml (pin to function text, including the dual-purpose notes); firmware/tunerstudio/tunerstudio.template.ini (the Injector Outputs panel: Injection Output 1 … 12 and its cylinder-number note) -->

Batch or sequential injection does not change this wiring. In batch mode several outputs fire together and
rusEFI decides which ones; each output is still the cylinder you wired it to.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (Injector Outputs panel: "Use only first half of outputs for batch mode if your board supports two injectors per channel") -->

### What the driver is asked to carry

:material-circle:{ .level-intermediate } Intermediate

A high-impedance injector — the ordinary 12 Ω class that a multi-point engine uses — is a self-limiting load:
12 V across 12 Ω is about 1 A, comfortably inside the 4 A the Proteus documentation gives these drivers.
Read the coil resistance with a multimeter between the injector's two terminals if you do not know what you
have; a low-impedance injector measures a couple of ohms instead of a dozen.

That difference is not a tuning detail, it is a wiring decision. A 2.5 Ω coil on 12 V wants around 5 A — over
the driver's documented rating — and a low-impedance injector held energised for the whole pulse also cooks its
own coil. Injectors of that class are specified for a **current-limited (peak-and-hold) driver**, and that
current limit has to come from the injector's own data sheet and the driver it specifies: it is not something
the injector dialogs set. Nothing in the injector's wiring hides this: the injector dialogs describe flow,
dead time and pressure compensation, not current.

!!! warning "Match the injector to the driver before you crimp anything"
    If the injector's data sheet calls for a peak-and-hold driver, put that driver between the ECU's output and
    the injector, and give the injector its 12 V through the driver. If the injector is a high-impedance type,
    wire it straight to the pin as in Figure 2. Whichever you choose, one injector drawing more than its share
    for a long duty cycle at high RPM shows up first as a driver that runs hot, then as a driver that has
    failed shorted — and a shorted injector driver means a cylinder that is permanently spraying fuel.
    <!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog injChars: Injector flow, flow units, compensation mode — no current field) -->

### The three pins everybody forgets

:material-circle:{ .level-basic } Basic

*Lowside 10*, *11* and *12* (Black35 pins 20, 9 and 21) are the factory **fuel pump**, **radiator fan** and
**main relay** outputs — and they are also injectors 10, 11 and 12. On a four-, six- or eight-cylinder engine
they are relays. On a twelve-cylinder engine they are injectors, and the three relay jobs have to move to the
spare outputs *Lowside 13 … 16* (Black35 pins 10, 11, 12 and 23), which the board files single out as having a
flyback diode on the board.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (proteus_boardDefaultConfiguration: mainRelayPin, fanPin, fuelPumpPin on Lowside 12, 11 and 10); firmware/config/boards/proteus/connectors/black35.yaml (Lowside 13 to 16 "with flyback") -->

### Setting the outputs and proving the wiring

:material-circle:{ .level-basic } Basic

Open **Fuel ▸ Injector Setup ▸ Injection hardware**. **Injection Output 1 … 12** name the pin for each cylinder;
on a factory tune they already point at the pins in the table above, so with the harness wired as in Figure 2
there is usually nothing to change here. Burn if you changed anything.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog injectionSettings with the Injector Outputs panel) -->

<!-- shot: img/ts/wiring-outputs-injection-hardware.png | Fuel ▸ Injector Setup ▸ Injection hardware | state: Proteus F7, ignition on, engine stopped, cylinders 4, Injector Outputs panel showing Firing order and Injection Output 1 to 4 set to Lowside 1, Lowside 2, Lowside 3 and Lowside 4, Injection Output 5 to 12 unassigned, Injector Test panel visible with Injector #1 to #4 buttons, every dropdown closed | Caption: Injection hardware on a four-cylinder: four injector pins named, four spare low-side outputs still free. -->

Then prove it with the engine off. **Controller ▸ Bench test** has an **Injector Test** panel: press
**Injector #1** and you should hear that injector click, with the pulse count and length taken from the bench
test's **Count**, **On Time** and **Off Time** fields. If a different cylinder clicks, the harness and the
setting disagree — fix the setting or re-make the wire, but do not leave them disagreeing.

<!-- shot: img/ts/wiring-outputs-bench-test.png | Controller ▸ Bench test | state: Proteus F7, ignition on, engine off, fuel pump relay unpowered or the rail depressurised, dialog open with Count 3, On Time and Off Time fields, Spark panel and Injector Test panel with Injector #1 to #4 buttons visible, all dropdowns closed | Caption: The bench test's Injector Test panel: the cheapest way to find a swapped injector pair before the first start. -->

!!! danger "An injector test sprays fuel"
    The injector opens; whatever is in the rail comes out. Do it with the engine off, the rail fittings and
    the injectors' seals confirmed tight, and no fuel spraying near hot exhaust or sparks. Depressurise the
    rail before you pull an injector, and keep the spark plugs in their leads when you are testing ignition.
    <!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog ioTest with the testInjectors panel: Injector #1 … #12 and Abort test); firmware/controllers/bench_test.cpp (the bench test command handling and its Count, On Time and Off Time fields) -->

## Coils: logic coils, and everything else

:material-circle:{ .level-intermediate } Intermediate

<figure markdown>
  ![Left panel: a logic-level smart coil pack with its power stage inside the housing, connected by fused 12 V, ground and a trigger wire to Proteus Black35 pin 35 (Ign 1). Right panel: a coil whose minus terminal carries the primary current, wired through an external driver which the ECU's Ign 1 signal drives, with a dashed red cross showing that the coil minus must never go straight to an ECU pin](../img/diagrams/wiring-outputs-coils.svg)
  <figcaption>Figure 3 — The two coil connections. Proteus's twelve ignition outputs are logic-level trigger
  outputs: they tell a coil what to do, they do not carry the coil's current.</figcaption>
</figure>

Proteus's twelve ignition outputs are Black35 pins 35, 34, 22, 33, 32, 31, 30, 29, 28, 27, 26 and 25, and the
board files call them **Smart Ignition Coil 1 … 12**. The firmware drives one per cylinder in the order the
firing order says, and what it does on the pin is simple: it pulls the output **active** to start charging the
coil (that is dwell), and it releases it — the spark happens at that release.
<!-- src: firmware/config/boards/proteus_meta.h (PROTEUS_IGN_1 … IGN_12 with their black35 pin numbers); firmware/config/boards/proteus/board_configuration.cpp (setIgnitionPins: ignitionPins from PROTEUS_IGN_1 to IGN_12); firmware/controllers/engine_cycle/spark_logic.cpp (dwell starts by driving the spark pin active, the spark is the fall of the output); firmware/config/boards/proteus/connectors/black35.yaml (Ign 1 to 12: "Smart Ignition Coil N") -->

### A logic-level coil — what these outputs expect

:material-circle:{ .level-intermediate } Intermediate

A **logic-level coil** (also called a smart coil, a coil-near-plug, a pencil coil, or a coil pack with the
driver inside) contains its own power stage. It has three terminals: plus 12 V, ground, and a trigger. Only the
trigger wire reaches the ECU, and the current that matters — several amps in the coil's primary — circulates
between the coil and its own housing. That is the kind of coil these outputs are built for: the Proteus
documentation describes them as 5 V ignition or general-purpose outputs, the board files call them smart-coil
outputs, and the board's own build configuration even uses one of them to switch a 5 V supply for adapter
circuitry.
<!-- src: firmware/config/boards/proteus/board.mk (VR_SUPPLY_VOLTAGE 5 with the comment that adapter boards are controlled via a 5v ignition output); firmware/config/boards/proteus/connectors/black35.yaml (the ign-type ignition output pins) -->

Wire a logic-level coil as three separate connections: fused switched 12 V from the main relay, its own ground
back to the ECU's power ground or the engine, and the trigger to its *Ign* pin. The 12 V and ground carry the
current the spark is made of, so they must be substantial wires — the trigger wire carries almost nothing.

### A coil that is not logic-level

:material-circle:{ .level-intermediate } Intermediate

A classic canister or drum coil whose **minus terminal must be switched** is a different animal: the switching
device has to carry several amps of primary current, which is exactly what these pins do *not* do. Put a driver
between them — an external ignition driver module, an ignition amplifier, or a driver board — and connect the
Proteus output to that driver's input, never to the coil terminal.

!!! danger "Do not hang a power-switched coil on an ECU output"
    Asking a logic-level output to interrupt a coil's primary current will destroy the driver, and the
    inductive spike on the way in can take the rest of the ECU with it. rusEFI's own warning on the Ignition
    Outputs panel is blunt about the related trap: *"Output Mode is dangerous and can burn out your coils, 99%
    installs is default, some Hondas are default inverted"*. On a Proteus there is no output-mode field for
    coils or injectors in TunerStudio — the board's drivers are wired for the default — so the only thing you
    decide here is which coil type you fit and how it is powered.
    <!-- src: firmware/tunerstudio/tunerstudio.template.ini (the ignitionOutputs panel note: Output Mode is dangerous and can burn out your coils) -->

### Which cylinder fires which output

:material-circle:{ .level-intermediate } Intermediate

Open **Ignition ▸ Ignition hardware**. **Mode** `ignitionMode` chooses *Single Coil*, *Individual Coils* or
*Wasted Spark*; **Ignition Cylinder 1 … 12** `ignitionPins1` … name the pin per cylinder, and on a Proteus
already point at *Ign 1 … 12* in order. If you wire one coil per cylinder but want the engine to fire in wasted
spark, that is **Individually wired Wasted Spark** `twoWireBatchIgnition` — a setting, not a rewiring job.
<!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog ignitionSettings with the ignitionOutputs panel); firmware/integration/rusefi_config.txt (ignitionMode and twoWireBatchIgnition help) -->

Prove the wiring with **Controller ▸ Bench test** and its **Spark** panel (**Spark #1 … #12**), with the coil
leads seated on plugs that are grounded. Watch the coil's share of the cycle in a log with the dwell duty
channel (`coilDutyCycle`) — at high RPM the charge time becomes a large fraction of the time available between
sparks, and that is where dwell is worth looking at (the dwell settings themselves belong to the Ignition
chapter).

<!-- shot: img/ts/wiring-outputs-ignition-hardware.png | Ignition ▸ Ignition hardware | state: Proteus F7, ignition on, engine stopped, Spark on, Mode Individual Coils, cylinders 4, Ignition Cylinder 1 to 4 set to Ign 1, Ign 2, Ign 3 and Ign 4, Firing order 1-3-4-2, the note about Output Mode being dangerous visible above the fields, every dropdown closed | Caption: Ignition hardware: one coil output per cylinder, already pointed at the board's smart-coil pins. -->

## Relays, solenoids and flyback

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

Almost every output that is not an injector, a coil or a throttle motor drives a **relay**. A standard
automotive relay has four terminals, and knowing them ends most relay confusion:

| Terminal | What it is | Where it goes |
|---|---|---|
| 85 and 86 | the **coil** — one of these goes to the ECU's output pin, the other to switched 12 V | the small side of the circuit |
| 30 | the contact's input | fused 12 V straight from the battery, or from the main relay |
| 87 | the contact's output | the fan, pump or accessory that actually draws the current |

The ECU never sees the load's current. It sees the coil: roughly 0.2 A at 12 V for a typical 60 Ω coil, against
the 4 A these drivers are documented for. That is the whole reason relays belong in a harness: they let a
4 A output control a 30 A accessory without the ECU's wiring anywhere near the accessory.

<!-- src: firmware/config/boards/proteus/board_configuration.cpp (the relay outputs the board names by default: mainRelayPin on Lowside 12, fuelPumpPin on Lowside 10, fanPin on Lowside 11) -->

### Flyback: where the magnetic field goes

:material-circle:{ .level-intermediate } Intermediate

A relay coil, a solenoid, an idle valve and an injector store energy in a magnetic field while current flows.
The instant the low-side driver opens, that field collapses and generates whatever voltage it needs to keep the
current going — tens of volts above the battery, on a pin that is meant to sit near ground. Without a path to
follow, the energy leaves through the driver.

The path is a diode across the coil, fitted in the reverse direction: cathode (band) to the coil's 12 V side,
anode to the pin the ECU switches. With it, the field circulates harmlessly around the coil for a few
milliseconds instead of punching a hole in the output stage. Two things follow:

- **Prefer a relay with a built-in diode**, or add one at the relay, across terminals 85 and 86.
- **The Proteus board files mark only four of the free low-side outputs as having a flyback diode on the
  board** — *Lowside 13, 14, 15* and *16* (Black35 pins 10, 11, 12 and 23). Nothing in the board files makes
  that claim for the other low-side pins, so for anything wired to those, fit the diode (or buy a relay that
  already has one) and do not assume the board did it for you.

<!-- src: firmware/config/boards/proteus/connectors/black35.yaml (the "(with flyback)" notes on Lowside 13 to 16 and their absence on the other low-side pins) -->

!!! note "A diode is not free"
    A diode makes a load release *slower*: the field has to bleed away through it. For a fuel pump relay or a
    fan that is irrelevant. For something the ECU modulates quickly — a boost solenoid, an idle valve, a
    variable valve timing solenoid — the driver and the valve are designed together, and that is what the
    Boost, Idle and VVT chapters cover rather than this one.

### High-side outputs: switching the plus

:material-circle:{ .level-basic } Basic

Four of Proteus's outputs do the opposite of the low-side family: they supply plus, and the load's other
terminal goes to ground. These are *Highside 1 … 4* — Black35 pins 2, 1, 13 and 14 — documented in the Proteus
hardware documentation as four 12 V 3 A outputs, and they are fed from the main-relay supply on Black23 pin 23.
A check-engine lamp is the classic use: the bulb's other terminal goes to ground, and the ECU feeds it 12 V.

Because a high-side output sources current rather than sinking it, the "inverted" question comes up again in its
**Output mode** field: the mode tells the firmware which electrical level means "on". Leave it at *default*
unless you know exactly why you are changing it.
<!-- src: firmware/config/boards/proteus/connectors/black35.yaml (Highside 1 to 4 on pins 2, 1, 13 and 14); firmware/config/boards/proteus/connectors/black23.yaml (pin 23 supplies the high side outputs); firmware/tunerstudio/tunerstudio.template.ini (pin_output_mode_e_enum: default, default inverted, open collector, open collector inverted) -->

## The electronic throttle H-bridge

:material-circle:{ .level-intermediate } Intermediate

A throttle motor has to turn both ways, so it cannot have one side tied to 12 V. Proteus answers this with two
H-bridges: instead of one switch to ground, a pair of switches per side, driven by a driver chip on the board.
rusEFI configures them through three control lines each — a PWM line, a direction line and a disable line —
which is exactly the trio the board's setup code passes for each bridge.

<figure markdown>
  ![Inside the ECU the throttle controller's duty command drives the MCU's three control lines D12 Control, D10 DIR and D11 DIS, which drive a TLE9201 half-bridge chip; the chip's 12 V is Black23 pin 23 from the main relay; its two outputs leave on Black23 pin 7 (ETB 1 positive) and Black23 pin 6 (ETB 1 negative) to the throttle motor. A panel lists the ±90 percent duty clamp, the 100 to 3000 Hz frequency range and the chip's overcurrent and overtemperature shutdowns](../img/diagrams/wiring-outputs-etb-hbridge.svg)
  <figcaption>Figure 4 — H-bridge #1 from command to motor. The part to remember is the red one: the bridge's
  own 12 V is a separate input, Black23 pin 23.</figcaption>
</figure>

The wiring is on the **Black23 pin 23** connector: throttle 1 is pins **7** (positive) and **6** (negative), throttle 2
is pins **15** (positive) and **8** (negative). Swap the two wires of a bridge and the throttle runs backwards;
rusEFI's own bench test (**Bench Test ETB 1 (open 300ms)**, in the Electronic throttle chapter) is how you check
which way it turns.
<!-- src: firmware/config/boards/proteus/connectors/black23.yaml (ETB 1 and ETB 2 positive and negative pins 6, 7, 8 and 15) -->

Three numbers govern what those pins can be asked to do:

- **Duty is clamped to ±90 %** of the bridge's range, in the throttle controller itself.
- **PWM frequency** is raised to at least 100 Hz, and above the board's maximum of **3000 Hz** the firmware
  raises a fatal error naming the frequency rather than driving the motor badly.
- The **TLE9201** driver chip reports its own faults, polled ten times a second: overcurrent shutdown,
  overtemperature shutdown and outputs-disabled are all distinguishable in the ECU's log. A throttle that
  stops moving mid-drive with an overcurrent record has a wiring or binding problem, not a tuning one.

<!-- src: firmware/controllers/actuators/electronic_throttle.cpp (ETB_DUTY_LIMIT 0.9); firmware/controllers/actuators/dc_motors.cpp (DcHardware::start: clamp to at least 100 Hz, criticalError above ETB_HW_MAX_FREQUENCY); firmware/controllers/generated/rusefi_generated_proteus_f7.h (ETB_HW_MAX_FREQUENCY 3000); firmware/hw_layer/drivers/gpio/tle9201.h (TLE9201_POLL_INTERVAL_MS); firmware/hw_layer/drivers/gpio/tle9201.cpp (overcurrent, overtemperature and outputs-disabled diagnostics) -->

The supply is the part that catches people out. The bridge's power is **Black23 pin 23**, fed from the output
of the car's main relay, exactly as that pin's own board-file description says. If that pin has no 12 V, the
throttle will not move *at all* even though the ECU is alive, the sensors read correctly and TunerStudio looks
healthy — and the same pin feeds the high-side outputs.

!!! info "Advanced"
    Two things are deliberately left alone. **Advanced ▸ DC motor actuator(s) function** decides which bridge
    drives what — by default *Throttle 1* and *Throttle 2*, and a bridge you do not use should be set to
    *None*. **Advanced ▸ DC motor actuator(s) hardware** holds the driver chip's own wiring: **Two-wire mode**
    stays off, because rusEFI's own help text for that field says the TLE9201 does not use two-wire mode, and
    the four *Direction*, *Control* and *Disable* pin fields are how the board's wires are routed. Either bridge
    can instead drive a stepper idle air valve, which the board also pre-wires — see the Idle chapter.
    <!-- src: firmware/config/boards/proteus/board_configuration.cpp (setupEtb: setupTLE9201IncludingStepper for both bridges); firmware/controllers/algo/defaults/default_base_engine.cpp (setupTLE9201 and setupTLE9201IncludingStepper: DIR, PWM and DIS control lines, etb_use_two_wires false); firmware/tunerstudio/tunerstudio.template.ini (dialog dcMotorActuatorHw: Two-wire mode help naming TLE9201, and dcMotorActuatorFunction: H-Bridge #1 and #2 function) -->

<figure markdown>
  ![DC motor actuator(s) function dialog: H-Bridge #1 function Throttle 1, H-Bridge #2 function Throttle 2](../img/ts/etb-hbridge-function.png)
  <figcaption>Figure 5 — H-bridge functions as they leave the factory: both bridges are throttles. A bridge you
  do not use is set to <i>None</i> here; the pin fields in the hardware dialog stay untouched.</figcaption>
</figure>

!!! danger "A throttle motor is strong enough to hurt you"
    Every ETB test and calibration moves the throttle plate hard and fast. Keep hands, tools and tie-wraps out
    of the bore with 12 V applied, and do the first motor-direction check with the throttle free and the intake
    tube off. The Electronic throttle chapter covers the calibration sequence and what to do if the throttle
    draws several amps against its stop.

## Wiring an output, step by step

:material-circle:{ .level-basic } Basic

1. **Find the pin you need in TunerStudio first, before you cut any wire.** Open
   **Controller ▸ Full pinout - Output**: every output setting in one place, with the pin names the connector
   carries. This is also where you spot a pin two features are fighting over.
   <!-- src: firmware/tunerstudio/tunerstudio.template.ini (dialog allPinsOutputs: the full output pin list) -->
2. **Decide what the ECU is switching**: a relay coil, an injector, a logic-level coil, a lamp, or a motor. If
   the answer is anything that draws more than a couple of amps on its own, the answer includes a relay.
3. **Give the load its plus from the right place.** Relays, injectors and coils are fed from the main relay's
   contacts; Black23 pin 23 carries that same switched supply into the ECU for the H-bridges and the high
   sides. Battery-fed accessories get their own fused wire — see *Power, grounds and ground loops*.
4. **Run the control wire to the named pin**, sized like any other signal wire, and kept out of the same loom as
   the trigger and knock cables (see [Shielding and noise](shielding-noise.md)).
5. **Fit the flyback diode** across any relay coil or solenoid that is not on a pin the board files mark as
   having one.
6. **Assign the pin in the feature's dialog and Burn.** There is no separate "pin map" screen: each feature
   names the pin it uses.
7. **Prove it with the engine off**, using the feature's own bench test — Injector Test, Spark, Test Fuel Pump,
   **Test Fan 1**, **Test Main Relay** — with the ECU on 12 V and the ignition on.
8. **Log it once with the engine running.** Injector duty cycle, dwell duty and the relevant status channel tell
   you the output is doing what the settings asked.
   <!-- src: firmware/console/binary/output_channels.txt (injectorDutyCycle and coilDutyCycle channels); firmware/tunerstudio/tunerstudio.template.ini (the bench test command buttons) -->

<!-- shot: img/ts/wiring-outputs-full-pinout.png | Controller ▸ Full pinout - Output | state: Proteus F7, ignition on, engine stopped, factory tune: Main Relay Pin Lowside 12, Fuel Pump output Lowside 10, Fan Pin Lowside 11, Fan 2 unassigned, Check Engine unassigned, Tachometer output unassigned, injection and ignition pin fields visible in the second panel, every dropdown closed | Caption: Step 1: every output setting on one screen. This is where a pin that two features want shows up before you find it on the bench. -->

## Worked examples

:material-circle:{ .level-intermediate } Intermediate

### Example 1 — naturally aspirated four-cylinder, coil-near-plug, one fan

Every output wire this engine needs on a Proteus, with the factory pin for each:

| Load | Proteus pin | Black35 pin | Assigned in | Notes |
|---|---|---|---|---|
| Injector 1 … 4 | *Lowside 1 … 4* | 3, 15, 4, 16 | Fuel ▸ Injector Setup ▸ Injection hardware | plus side from the main relay, common fused feed |
| Coil 1 … 4 (logic-level) | *Ign 1 … 4* | 35, 34, 22, 33 | Ignition ▸ Ignition hardware | plus 12 V and ground at the coil pack, trigger only at the ECU |
| Main relay coil | *Lowside 12* | 21 | Setup ▸ Outputs | follows ignition voltage; diode across the coil |
| Fuel pump relay coil | *Lowside 10* | 20 | Setup ▸ Fuel Pump Control | diode across the coil |
| Radiator fan relay coil | *Lowside 11* | 9 | Setup ▸ Cooling Fans | diode across the coil |
| Check-engine lamp | *Highside 1* | 2 | Setup ▸ Check Engine Settings | lamp's other terminal to ground |
| Unused | *Lowside 13 … 16* | 10, 11, 12, 23 | — | the flyback-diode-protected spares |

Why it looks like this: every one of those pins is rusEFI's factory choice on a Proteus, so the harness and the
tune agree before you open a dialog. Only two things need a setting and a **Burn** if you want them: the
check-engine pin (unassigned by default) and the second fan.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (proteus_boardDefaultConfiguration with mainRelayPin, fanPin and fuelPumpPin, and setupDefaultSensorInputs); firmware/config/boards/proteus/connectors/black35.yaml (pin numbers for every pin in the table) -->

<!-- shot: img/ts/wiring-outputs-check-engine.png | Setup ▸ Check Engine Settings | state: Proteus F7, ignition on, engine stopped, Settings panel: Output Highside 1, Output mode default, Minimum battery voltage 6.0, Maximum battery voltage 18.0, Test Check Engine button visible, the Battery / Raw MAP / Raw IAT / Raw TPS readouts on the right, all dropdowns closed | Caption: The check-engine lamp is the one Proteus high-side output most builders actually use. -->

### Example 2 — a big electric fan, and why the ECU pin is not the wire

A 200 W electric cooling fan draws about 17 A at 12 V — four times what a 4 A low-side driver is documented
for, and enough to melt an un-fused signal wire. The wiring is: battery → a 25 A fuse → the relay's terminal 30
→ terminal 87 → the fan; the fan's other terminal to a good chassis or engine ground; and the relay coil across
*Lowside 11* and switched 12 V. The ECU then decides *when*, the relay decides *how much current*, and the fuse
protects the wire the relay switches. The fan's on and off temperatures, and PWM fan control, are in the
Outputs chapter and the Idle chapter.

!!! tip "Buy the relay with the diode already inside"
    A diode-equipped relay is the same price and the same size, and it saves the one flyback mistake that
    kills low-side drivers. If you already have a plain relay, add a diode across the coil — band to the 12 V
    side — and it does not matter which way round the coil's two wires go afterwards.

### Example 3 — twelve cylinders: where the relays go instead

On a V12 every *Lowside 1 … 12* pin is an injector, so the fuel pump, fan and main relay have to move to the
four protected spares — say main relay to *Lowside 13*, fuel pump to *Lowside 14* and fan to *Lowside 15*
(Black35 pins 10, 11 and 12). Those four pins are the ones the board files mark as having a flyback diode, so
they are a sensible home for relay coils. Then change the three settings — **Output** in **Setup ▸ Outputs** and
**Setup ▸ Fuel Pump Control**, and **Output** in **Setup ▸ Cooling Fans** — and **Burn**. If you leave the fan
pointed at *Lowside 11* while injector 11 is also using it, the ECU will not let you run: it reports which two
features want the pin and shuts the outputs down.

<!-- shot: img/ts/wiring-outputs-main-relay.png | Setup ▸ Outputs | state: Proteus F7, ignition on, engine stopped, Main relay output panel: Output Lowside 12, Output mode default, Main Relay Disable Time 1, Test Main Relay button visible, Fuel Pump panel alongside with Output Lowside 10, all dropdowns closed | Caption: The main relay pin and its output mode: the pin switches the coil, the relay carries the harness. -->

<!-- shot: img/ts/wiring-outputs-fuel-pump.png | Setup ▸ Fuel Pump Control | state: Proteus F7, ignition on, engine stopped, Control mode Single relay, Output Lowside 10, Output mode default, Prime duration 4 seconds, Secondary relay and PWM pressure control panels hidden by the mode, all dropdowns closed | Caption: The fuel pump relay pin lives in its own dialog, not in a pin map. -->

<!-- shot: img/ts/wiring-outputs-cooling-fans.png | Setup ▸ Cooling Fans | state: Proteus F7, ignition on, engine stopped, Fan 1 panel with Output Lowside 11 and Output mode default, Fan 2 panel with Output unassigned, On temperature 92 and Off temperature 88 visible, Test Fan 1 and Test Fan 2 buttons along the bottom, all dropdowns closed | Caption: Fan 1 on Lowside 11 by default, Fan 2 free: on a twelve-cylinder engine this is where the fan moves to Lowside 15. -->

The same engine is a reminder about the ignition side too: twelve coils need *Ign 1 … 12*, which is every
ignition output the board has, so there is no spare ignition pin left for a general-purpose job — those go on
the low-side or high-side outputs.
<!-- src: firmware/config/boards/proteus/board_configuration.cpp (injPins uses Lowside 1 to 12, ignPins uses Ign 1 to 12); firmware/config/boards/proteus_meta.h (the sixteen Lowside pins and the four Highside pins); firmware/hw_layer/pin_repository.cpp (brain_pin_markUsed: the two-owners critical error) -->

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-advanced } Advanced

| Symptom | Likely cause | Check |
|---|---|---|
| No injector click on the bench test | pin assigned to another cylinder, wrong connector pin, or the injectors have no switched 12 V | the Injection Output list against the harness; 12 V at the injector rail with the main relay in |
| One cylinder misfires only when the engine is warm | injector driver failing hot, or an over-current injector (low-impedance on a switch rated 4 A) | coil resistance, injector duty cycle at temperature, swap the injector to another output to see whether the fault follows |
| Main relay drops out at cranking or when the fan runs | the relay coil is on a pin whose supply collapses, or the ignition feed is not on Black23 pin 18 | battery voltage during the drop, the ignition feed, the main relay's own ground path |
| Everything works on the bench, nothing moves under the hood | Black23 pin 23 unpowered, or the main relay contacts are not feeding the harness | 12 V on Black23 pin 23 with the ignition on |
| Throttle does not move, ETB calibration fails, "check your wiring" | no bridge supply, or the motor wires are on the wrong connector | 12 V on Black23 pin 23; motor leads on Black23 pins 7 and 6 for throttle 1 |
| Throttle moves, then stops, and the log shows an overcurrent record | shorted motor wiring, or a binding throttle shaft | motor lead insulation, the throttle's freedom by hand with power off |
| A fan or pump stays on for ever | the pin is shorted to ground externally, or the relay contacts have welded | unplug the relay: if the fault stays, the driver is shorted; if it goes, the relay is |
| Outputs die and the ECU names two owners of one pin | the same pin assigned to two features | **Controller ▸ Full pinout - Output** and the error text, which names both features |
| An output works only when you hold the settings the opposite way round | a load wired to plus where the firmware expects a sink, or vice versa | the **Output mode** field of that feature, and which side of the load the pin actually switches |
| A driver dies repeatedly after fitting relays | no flyback path on a pin the board does not protect | a diode across the coil, or a relay with its own diode |
| Sensor readings jump when the coils or injectors fire | actuator leads sharing a loom or a return with sensor wiring | [Shielding and noise](shielding-noise.md) and *Power, grounds and ground loops* |
| Bench test buttons do nothing | the ECU is on USB power only, so it does not see ignition voltage | run the ECU on 12 V with the ignition on |

## Settings reference

Generated from the official Proteus F7 ini. These are the dialogs this chapter tells you to use; the settings
themselves are explained in the Outputs chapter.

### Injector hardware (Fuel ▸ Injector Setup ▸ Injection hardware)

--8<-- "reference/settings/_injectionSettings.table.md"

### Ignition hardware (Ignition ▸ Ignition hardware)

--8<-- "reference/settings/_ignitionSettings.table.md"

### Outputs (Setup ▸ Outputs)

--8<-- "reference/settings/_outputsDialog.table.md"

### Fuel Pump Control (Setup ▸ Fuel Pump Control)

--8<-- "reference/settings/_fuelPumpSettings.table.md"

### DC motor actuator(s) function (Advanced ▸ DC motor actuator(s) function)

--8<-- "reference/settings/_dcMotorActuatorFunction.table.md"

### DC motor actuator(s) hardware (Advanced ▸ DC motor actuator(s) hardware)

Read-only in practice: these are the driver chip's own wires as the board makes them.

--8<-- "reference/settings/_dcMotorActuatorHw.table.md"

### Cooling Fans (Setup ▸ Cooling Fans)

--8<-- "reference/settings/_fanSettings.table.md"

### Check Engine Settings (Setup ▸ Check Engine Settings)

--8<-- "reference/settings/_malfunctionDialog.table.md"

### Bench Test & Commands (Controller ▸ Bench test)

--8<-- "reference/settings/_ioTest.table.md"

### Full pinout - Output (Controller ▸ Full pinout - Output)

--8<-- "reference/settings/_allPinsOutputs.table.md"

## Related

- [Wiring basics](wiring-basics.md) — wire size, terminals, crimping, and the pre-power checklist
- [Power, grounds and ground loops](power-grounds.md) — the main relay, fusing, and why the switched 12 V matters
- [Shielding and noise](shielding-noise.md) — keeping actuator current out of trigger and knock signals
- [The official boards](official-boards.md) — the complete Proteus F7 pinout for all three connectors
- [Outputs and pins](../part3/outputs.md) — which setting owns which pin, and how the firmware guards it
- [Fuel](../part3/fuel.md) — injector flow, dead time and the pulse widths that decide an injector's duty
- [Ignition](../part3/ignition.md) — dwell, charge time and coil energy
- [Electronic throttle](../part3/electronic-throttle.md) — calibrating and tuning the throttle the H-bridge drives
- [Idle](../part3/idle.md) — the stepper idle valve that can take one of the H-bridges
