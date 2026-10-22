# Read this first: safety and disclaimer

:material-circle:{ .level-basic } Basic

An engine control unit decides when fuel is sprayed, when a spark fires and how far the throttle
opens. Mistakes in wiring or settings can destroy an engine, start a fire or injure someone. Read
this page before you connect anything.

## This manual is unofficial

--8<-- "_edition.md"

## What rusEFI is licensed for

rusEFI is free software, distributed under the GNU General Public License version 3 with three
additional terms, quoted here from the licence:

> **rusEFI#1:** rusEFI is intended for off-road land and water vehicles.
>
> **rusEFI#2:** rusEFI is not compliant with automotive environmental regulations.
>
> **rusEFI#3:** rusEFI is not approved for manned aircraft applications.
<!-- src: license.txt (additional terms rusEFI#1..#3) -->

Whether you may use a modified engine management system on a road vehicle is decided by the law where
you live, not by this manual. Check it before you drive on a public road.

## No warranty

The licence is explicit that rusEFI comes with no warranty:

> THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN
> OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS"
> WITHOUT WARRANTY OF ANY KIND […]
<!-- src: license.txt (section 15, Disclaimer of Warranty) -->

The same applies to this manual. It is written carefully and checked against the rusEFI source code,
but it can be wrong, out of date, or wrong for your engine. **You are responsible for what you build,
wire, configure and run.** The authors and contributors accept no liability for damage, injury or loss
of any kind arising from its use.

## Licence of this manual

This manual (its text, diagrams, plots and screenshots) is licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International licence](https://creativecommons.org/licenses/by-sa/4.0/)
(CC BY-SA 4.0). You may copy it, share it and adapt it, for any purpose including commercial use, as
long as you:

- **credit it**: name *Jason Roughley and the rusEFI Manual contributors*, link to the licence, and say if you changed anything;
- **share alike**: release your adapted version under the same licence.

The licence covers this manual only. Quoted licence text stays under its own terms, and the names
rusEFI, TunerStudio and MegaLogViewer belong to their owners; the licence gives no rights to them.

## The hazards

| Hazard | What can happen | The rule |
|---|---|---|
| **Ignition high voltage** | A coil's output reaches tens of thousands of volts. Testing coils, or touching a plug lead while the engine turns, gives a shock that can kill, especially anyone with a heart condition or a pacemaker. | Hands off ignition leads and coil outputs whenever the ECU is powered. When bench-testing coils, ground the plugs firmly against the engine. |
| **Fuel and fire** | Testing injectors with the fuel pump running sprays fuel. A spark or a hot exhaust ignites it. | Test injectors with the fuel system depressurised or the pump unpowered. Keep a fire extinguisher within reach. Never work on the fuel system near an ignition source. |
| **A throttle that opens by itself** | An electronic throttle can open with nobody on the pedal. A wrong calibration can make a running engine rev or the throttle snap open during calibration. | Fingers out of the throttle bore while the ECU has 12 V. First start with your hand on the key. |
| **Battery current** | A car battery delivers hundreds of amps into a short circuit: wires burn, batteries can explode. | Fuse every supply. Disconnect the battery before wiring. |
| **Moving parts** | A starter can turn the engine over unexpectedly; belts and fans catch hands and clothing. | Keep clear of belts and fans whenever the ECU can crank the engine. |
| **Engine damage** | Too little fuel, too much ignition advance, over-boost or over-revving can destroy an engine in seconds. | Change tables in small steps, log everything, and set the protections in *Limits and engine protection* before you push an engine. |

Throughout the manual, these boxes mark the risks:

!!! warning "Warning"
    Can cost time, a part, or a bad tune.

!!! danger "Danger"
    Can damage the engine or hurt someone.
