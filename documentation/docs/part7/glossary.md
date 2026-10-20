# Glossary

:material-circle:{ .level-basic } Basic

The terms this manual uses, in alphabetical order. Where a term is a rusEFI or TunerStudio name, it is
written as the software writes it.

**Acceleration enrichment (AE)** — Extra fuel added when the throttle opens quickly, because air
arrives in the cylinder before the fuel wetting the port walls catches up.

**AFR (air-fuel ratio)** — Mass of air divided by mass of fuel. 14.7 is stoichiometric for petrol;
lower is richer. See also *lambda*.

**Alpha-N** — A fuel strategy that estimates engine load from throttle position and RPM instead of
manifold pressure. Used on engines whose MAP signal is unusable, such as individual throttle bodies.

**APP / pedal** — The accelerator pedal position sensor of an electronic throttle. rusEFI reads two
redundant signals from it.

**Baro** — Barometric (atmospheric) pressure, used to correct fuel for altitude and weather.

**Bench test** — Switching one output on and off from TunerStudio to prove its wiring, with the engine
stopped. See [Bench testing](../part5/bench-testing.md).

**Bootloader** — The small program at the start of the ECU's flash that can install new firmware.
rusEFI boards use **OpenBLT**; the STM32 chip also has its own built-in **DFU** bootloader.

**Bundle** — The rusEFI download for one board: firmware, the matching TunerStudio `.ini`, the rusEFI
console and drivers, in one archive.

**Burn** — Copy the settings from the ECU's working memory to its flash, so they survive a power cycle.

**CAN** — Controller Area Network: the two-wire bus cars use to connect ECUs, dashes, gearbox
controllers and wideband controllers.

**CLT** — Coolant temperature.

**Closed loop** — Adjusting fuel automatically from a lambda sensor's reading. See *STFT*, *LTFT* and
[Closed-loop lambda](../part3/closed-loop-lambda.md).

**Cranking** — The engine being turned by the starter, before it runs on its own. rusEFI uses separate
fuel and timing settings until RPM rises above the cranking threshold.

**Dead time (injector lag)** — The time an injector takes to open after it is told to. It depends on
battery voltage and is added to every pulse.

**DFU** — Device Firmware Upgrade: a USB mode in which the STM32's built-in bootloader accepts new
firmware. Used for first flashing and for recovery.

**Dwell** — How long an ignition coil is charged before it fires.

**ECU** — Engine control unit.

**EGT** — Exhaust gas temperature.

**Engine sniffer** — The rusEFI console view that shows trigger edges, injector and coil events on a
time line. TunerStudio cannot show it.

**ETB (electronic throttle body)** — A throttle opened by a motor under ECU control instead of a cable.
See [Electronic throttle](../part3/electronic-throttle.md).

**Firing order** — The order in which the cylinders fire, for example 1-3-4-2.

**Flex fuel** — Fuel of varying ethanol content, measured by a flex sensor so fuel and timing can be
corrected.

**Hall sensor** — A crank or cam sensor that outputs a clean on/off digital signal. Compare *VR sensor*.

**IAT** — Intake air temperature.

**Idle valve (IAC)** — A valve that lets air past a closed throttle to control idle speed. An
electronic throttle does the same job without one.

**`.ini` file** — The file that tells TunerStudio every setting, table and live value a particular
firmware build has, and where they are in memory. It must match the firmware exactly; see *signature*.

**Injector duty cycle** — How much of the available time an injector is open. Near 100 % the injector
cannot deliver more fuel.

**Knock** — Uncontrolled combustion that makes a metallic rattle and can destroy pistons. A knock sensor
hears it so the ECU can retard the timing.

**Lambda (λ)** — Air-fuel ratio divided by the stoichiometric ratio. 1.00 is stoichiometric for any
fuel; below 1 is rich, above 1 is lean.

**Limp mode** — Reduced operation (limited RPM, power or throttle) that rusEFI imposes when a sensor or
actuator fails. See [Limits and engine protection](../part3/limits-protection.md).

**LTFT (long-term fuel trim)** — A correction rusEFI learns over time, cell by cell, from closed-loop
lambda, and can apply on top of the VE table.

**Lua** — The scripting language built into rusEFI, for custom logic: CAN messages, extra outputs,
car-specific behaviour. See [Lua scripting](../part3/lua.md).

**MAF** — Mass air flow sensor: measures the air going into the engine directly.

**MAP** — Manifold absolute pressure, in kPa. Atmospheric pressure is about 100 kPa; boost is above
it, vacuum below.

**MegaLogViewer (MLV)** — The program for viewing and analysing logs (`.mlg` files) recorded by
TunerStudio or on the ECU's SD card.

**MIL** — Malfunction indicator lamp: the check engine light.

**`.msq` file** — A TunerStudio tune file: every setting of one tune.

**OpenBLT** — The open-source bootloader on rusEFI boards. It lets the rusEFI console update firmware
over USB without DFU.

**Output channel** — A live value the ECU reports (RPM, MAP, coolant temperature and hundreds more),
shown on gauges and recorded in logs.

**PID** — Proportional-integral-derivative control: the feedback method rusEFI uses for idle, the
electronic throttle, boost and VVT.

**Proteus** — rusEFI's official board family used as the example in this manual.

**Ratiometric sensor** — A sensor whose output is a fraction of its 5 V supply, such as MAP and
throttle position. Its reading is only correct when the supply is at its full 5 V.

**Restore point** — A copy of the tune TunerStudio saves automatically, so you can go back.

**rusEFI console** — rusEFI's own program for firmware updates, the engine sniffer, Lua editing and
other jobs TunerStudio does not do. See [Your two tools](../part1/two-tools.md).

**SD card logging** — Recording logs onto the ECU's own SD card, without a laptop.

**Self-stimulation** — rusEFI generating a simulated crank signal internally, to test without an
engine. See [Bench testing](../part5/bench-testing.md).

**Semi-sequential / batch** — Injection modes that fire injectors in pairs or all together, instead of
each one at its own cylinder's intake stroke.

**Sequential** — Each injector fires once per cycle, timed to its own cylinder. Needs a cam signal to
know which half of the cycle the engine is in.

**Signature** — The text a firmware build reports to identify itself (branch, date, board and a
configuration hash). TunerStudio uses it to pick the matching `.ini`.

**Speed density** — A fuel strategy that estimates air mass from MAP, air temperature, RPM and the VE
table. rusEFI's default.

**STFT (short-term fuel trim)** — The fast closed-loop correction to fuel from the lambda sensor.

**Stoichiometric** — The exact air-fuel ratio at which all the fuel and oxygen burn: 14.7:1 for petrol,
λ = 1.

**Tooth logger** — A TunerStudio tool that records the time between trigger teeth, to show where a
trigger pattern goes wrong.

**TPS** — Throttle position sensor.

**Trigger** — The crank (and cam) signal rusEFI uses to know where the engine is in its cycle. See
[Trigger](../part3/trigger.md).

**Trigger wheel** — The toothed wheel the crank or cam sensor reads, often with a gap of missing teeth,
such as 60-2 or 36-1.

**TunerStudio (TS)** — The commercial tuning program this manual uses for setting up and tuning rusEFI.

**VE (volumetric efficiency)** — How well the engine fills its cylinders compared with the ideal, as a
percentage; the main table you tune for fuel.

**VR sensor** — Variable reluctance sensor: a two-wire magnetic crank or cam sensor whose output is an
AC voltage that grows with speed. Compare *Hall sensor*.

**VVT** — Variable valve timing: moving the camshaft relative to the crank, controlled by a solenoid.
See [Cam and valve control](../part3/vvt.md).

**Wasted spark** — Firing two cylinders' plugs at once, one on its power stroke and one on its exhaust
stroke. Works without a cam signal.

**Wideband** — A lambda sensor and controller that measure the mixture accurately over a wide range,
rich to lean. Needed for tuning and closed loop.
