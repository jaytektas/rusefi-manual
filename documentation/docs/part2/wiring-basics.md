# Wiring basics

:material-circle:{ .level-basic } Basic → :material-circle:{ .level-intermediate } Intermediate

> **In one sentence:** a reliable engine harness is made with the right tools, automotive wire,
> properly crimped and sealed terminals, and careful routing — and is checked before it ever sees power.

## Overview

:material-circle:{ .level-basic } Basic

This chapter is for you if you have never wired a car. It covers the tools, the materials, how to
crimp and splice, how to route and protect a harness, and a checklist before the first power-up.
Proteus pin numbers come from the next chapters (*Power, grounds and ground loops*, *Wiring sensors*).

!!! danger "Airbag circuits"
    Never cut, probe or re-route airbag (SRS) wiring — usually in yellow sheathing with yellow
    connectors. A multimeter or test light can fire an airbag and injure you. Disconnect the battery
    and follow the vehicle maker's waiting time before working near it, and leave it alone.

!!! danger "Battery shorts"
    Disconnect the battery negative before you start. A tool across the battery terminals or an
    unfused wire touching the body can melt, burn and start a fire.

## Concepts

:material-circle:{ .level-basic } Basic

### Tools

| Tool | Why |
|---|---|
| **Crimper matched to the terminal type** | Each terminal family (open-barrel sealed terminals, insulated butt splices, ring terminals) needs its own die. A pair of pliers or a wrong die makes a crimp that looks fine and fails later. |
| **Wire strippers** (self-adjusting or sized) | Strip insulation without nicking strands. |
| **Multimeter** | Voltage, continuity, resistance, voltage drop. The one test tool you must have. |
| **Test light** | Fine for checking a fuse or relay feed — **never on ECU pins**: it draws far more current than an ECU input or sensor supply is designed for and can damage it. Use the multimeter on ECU pins. |
| **Heat gun** | Shrinks heatshrink evenly. A lighter scorches it and the wire. |
| **Soldering iron** | For circuit boards and the odd repair. See *When not to solder*. |
| **Pin extraction tools** | Remove terminals from connector housings without damage. |

### Wire

Use automotive wire with cross-linked or thin-wall insulation rated for engine bay temperatures (for
example SAE J1128 TXL/GXL or ISO 6722 types). Household or speaker wire is not suitable.

| Size (mm²) | ≈ AWG | Typical use |
|---|---|---|
| 0.35 | 22 | low-current signals in a light harness |
| 0.5 | 20 | sensors, sensor grounds, 5 V supplies, CAN, relay coils |
| 0.75 | 18 | injectors, coil signal wires, small relays' loads |
| 1.0 | 18–17 | ECU power feeds, power ground wires |
| 1.5–2.5 | 16–14 | fuel pump, fans, main relay output to a fuse block |
| 4–6 | 12–10 | main feeds |

Pick the size for the current and the length: longer runs need thicker wire. The fuse is chosen for the
wire (see the next chapter).

### Terminals, connectors and seals

Use the terminals made for your connector housing and wire size, with the matching **seal** in sealed
connectors — a seal that is too large lets water in, one that is too small splits. The Proteus board
files list pins, not connector part numbers; take those from the Proteus hardware documentation.
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (info: pin list only, board_url in black23.yaml) -->

### Protection

- **Heatshrink**, preferably adhesive-lined, over every splice.
- **Loom**: split convolute tube, braided sleeve, or harness tape (cloth tape in the bay, never PVC
  electrical tape in hot areas).
- **Grommets** wherever a harness passes through metal.

### What a good crimp looks like

<!-- figure: wiring-basics-crimp.svg (good vs bad crimp) requested, not yet drawn — see report -->

An open-barrel terminal has two crimps: the **conductor crimp** grips the bare strands, the
**insulation crimp** grips the insulation behind it as strain relief. In a good crimp the strands just
show past the conductor crimp, no strands are outside the barrel, the insulation reaches into the
insulation crimp but not into the conductor crimp, and the terminal is not bent.

Bad crimps: insulation trapped under the conductor crimp (high resistance), strands folded back or
cut, the wire stripped too short (not gripped) or too long (bare copper exposed), the wrong die
(crushed or loose).

## Procedure

:material-circle:{ .level-basic } Basic

### Crimping a terminal

1. Slide the seal onto the wire first, if the connector uses one.
2. Strip the length the terminal needs — the strands should fill the conductor crimp and just show out
   of its front. Do not twist or tin the strands.
3. Put the terminal in the correct die position, insert the wire with the seal against the insulation
   crimp, and close the crimper fully (ratchet crimpers release only at full closure).
4. **Pull test:** pull the wire firmly by hand. It must not move. If it does, cut it off and redo it.
5. Push the terminal into the housing until it clicks, then tug gently to check it is locked.

### Splicing

Use a crimped splice (butt splice or an open-barrel splice) covered with adhesive heatshrink. Stagger
splices in a bundle so they do not form one lump. Never splice a sensor ground into a power ground —
see *Power, grounds and ground loops*.

### When not to solder

Solder wicks up the strands and makes the wire stiff right where it leaves the joint; engine vibration
then breaks it there. Crimp terminals and splices in an engine harness; do not solder crimped
terminals. Solder is fine on circuit boards and in places that are fully supported and do not vibrate.

### Routing

- Keep the harness away from the exhaust and turbo, and from sharp edges and moving parts (belts,
  throttle linkage, steering).
- Keep sensor wires — especially crank and cam sensors and knock sensors — away from ignition leads,
  coils, injector wires and the throttle motor wires; cross them at right angles (see *Shielding and
  noise*).
- Leave a loop of slack where the engine moves on its mounts relative to the body.
- **Strain relief:** clip the harness down near each connector so the connector does not carry the
  harness weight.
- **Label** both ends of every wire (heatshrink labels or numbered markers) and keep a written list of
  wire, colour and pin.

### Before first power-up

1. Every wire checked against your pin list, end to end, with the multimeter (continuity).
2. No continuity between 12 V and ground, between each 5 V sensor supply (White 9/21/32,
   White 10/22/33) and ground, or between 12 V and any sensor pin.
3. Every supply fused; fuses of the right value fitted.
4. All power grounds (Black23 14/19/20, Black35 17/18/24) to the block; sensor grounds only to
   White 1–8/23/29.
5. ECU unplugged: battery connected, key on — 12 V present on Black23 pin 18 (ignition feed); main relay off.
6. ECU plugged in, fuel pump fuse out, coils' fuse out: key on, connect TunerStudio, check sensors read
   sensibly, then fit the fuses one at a time.
<!-- src: firmware/config/boards/proteus/connectors/white35.yaml (+5 supply #1/#2, GNDA); firmware/config/boards/proteus/connectors/black23.yaml (pin 18, gnd pins); firmware/config/boards/proteus/connectors/black35.yaml (gnd pins) -->

## Examples

:material-circle:{ .level-intermediate } Intermediate

| Circuit | Wire | Notes |
|---|---|---|
| Coolant sensor to Proteus | 0.5 mm² signal + 0.5 mm² sensor ground | ground to a White GNDA pin |
| Injector | 0.75 mm² | 12 V from the main relay fuse block, signal to a Black lowside |
| ECU power ground | 1.0 mm² each, six wires | each to the block star point |
| Fuel pump | 1.5–2.5 mm² | own fuse and relay |

## Pitfalls and troubleshooting

:material-circle:{ .level-basic } Basic

**Do:** use the right crimper; pull-test every crimp; fuse every supply; label everything; seal every
splice; route away from heat and ignition.
**Don't:** twist-and-tape; solder crimp terminals; use a test light on ECU pins; ground sensors to the
block; touch airbag wiring.

| Symptom | Likely cause | Check |
|---|---|---|
| Intermittent sensor or output | crimp pulled out or loose in the housing | pull test, terminal lock |
| Wire broken just behind a terminal | soldered or no strain relief | re-crimp, clip the harness |
| Corroded terminals | missing or wrong-size seal | replace terminal and seal |
| Fuse blows on key-on | short to ground | disconnect circuits one by one |

## Related

- Power, grounds and ground loops
- Shielding and noise
- Wiring sensors, Wiring outputs
- [Safety](../safety.md)
