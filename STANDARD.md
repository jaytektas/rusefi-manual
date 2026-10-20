# The rusEFI Manual — writing standard

Every chapter is written to this standard. It is the brief each author (person or agent) works from,
and the checklist a chapter is reviewed against before it is accepted. Not shipped.

The sources of truth are rusEFI's own repository and the official board files.

## 1. What the manual is

A **reference book** for rusEFI firmware on official rusEFI hardware, using the rusEFI console and
TunerStudio, that takes a reader from understanding how EFI works to advanced tuning. It is read two
ways, and every chapter serves both:

- **Front to back** by someone learning: concepts build in order, each chapter says what it assumes.
- **Dipped into** by someone with a problem: every heading is findable from the index and search,
  and a section makes sense on its own.

Source is Markdown in `documentation/`, built to a static HTML site with MkDocs + Material, and to
PDF from the same source.

**Scope:** the firmware, the official boards under `rusefi/firmware/config/boards/`, the rusEFI
console, and TunerStudio as rusEFI uses it. **Proteus F7** is the reference board for screenshots and
worked examples; other boards appear where they differ. Unofficial or private boards never appear —
not in text, not in a screenshot (window titles, pin names, firmware signatures).

## 2. Audience and levels

Readers range from someone who has never tuned an engine to a professional calibrator. Every section
carries one level badge, placed directly under its heading:

| Badge | Meaning |
|---|---|
| `:material-circle:{ .level-basic } Basic` | No prior EFI knowledge. Explains every term the first time. |
| `:material-circle:{ .level-intermediate } Intermediate` | Has a running engine and knows what VE, lambda and timing are. |
| `:material-circle:{ .level-advanced } Advanced` | Calibrator, firmware builder, or someone wiring unusual hardware. May assume the rest of the manual. |

A chapter usually moves from Basic at the top to Advanced at the bottom. A reader should be able to
stop at the first Advanced section and still have a working configuration.

## 3. Voice

- Plain English, second person ("you"), present tense, active voice. Short sentences.
- Explain **why** before **how**. A setting described only by its name is not described.
- Metric units first (kPa, °C, mm, ms, lambda); give AFR/°F/psi in brackets where readers expect them.
- Name things exactly as the tool shows them, in **bold**: TunerStudio menus as
  **Sensors ▸ Accelerator pedal**, console tabs and buttons as they are labelled. Settings are named by
  their TunerStudio label, with the internal name in `code` the first time
  (**Primary sensor input** `tps1_1AdcChannel`).
- No marketing language and no comparisons with other ECUs. Naming another product is fine where
  rusEFI **works with** it (TunerStudio, MegaLogViewer, a CAN dash, a wideband controller).

## 4. Accuracy — the rule that overrides every other rule

**Nothing is written from general EFI knowledge where the firmware decides the answer.** Every
behaviour, default, range, unit, limit and sequence is taken from the rusEFI repository:

| Question | Source of truth |
|---|---|
| A setting's name, type, units, range, help text | `firmware/integration/rusefi_config.txt` |
| Where a setting appears in TunerStudio, its label, the dialog layout | `firmware/tunerstudio/tunerstudio.template.ini` (+ board `prepend*.txt` / `board_*.ini`) |
| What the firmware actually does with it | `firmware/controllers/` (the module's source) |
| Defaults | `firmware/controllers/algo/defaults/`, the board's `board_configuration.cpp` |
| Pins, connectors, electrical notes | `firmware/config/boards/<board>/connectors/*.yaml`, `<board>_meta.h` |
| Trigger decoding | `firmware/controllers/trigger/`, `docs/triggers/` |
| Console behaviour | `java_console/` and the running console |
| Error codes | `firmware/controllers/core/obd_error_codes.h` and the code that raises them |
| Flashing, bootloader | `firmware/bootloader/`, bundle scripts in `firmware/` and `misc/` |
| TunerStudio / serial protocol | rusEFI's own implementation: `firmware/console/binary/` (`tunerstudio.cpp` and friends) and the console's `java_console/` client. External protocol documents in `reference/` are background only — where they differ, the rusEFI code wins and the difference is noted. |

Each factual paragraph carries a hidden source note for maintainers, e.g.
`<!-- src: firmware/controllers/actuators/electronic_throttle.cpp (EtbController::getClosedLoop); firmware/integration/rusefi_config.txt (etb.pFactor) -->`.
A note names the FILE, with its full path from the rusEFI repository root, and says in words what to
look for in it — a function, a setting, a table. **Never a line number.** `tools/check_src.py` fails
the build if a note cites a line number or a file that does not exist. When the source is ambiguous or
the author cannot confirm something, it is **not guessed**: it goes in the chapter's `open-questions`
list (section 9) and the text says only what is certain.

General EFI theory (what VE is, why knock happens) may be written from knowledge, but must not
contradict how rusEFI implements it.

The manual as a whole names the rusEFI commit it describes, in one place: the *Unofficial documentation*
notice (`documentation/docs/_edition.md`, generated by `tools/edition.py` from the oldest verified
commit) on the home and safety pages. Chapters themselves carry no commit hashes.

Which rusEFI commit each chapter was last verified against is recorded **outside the chapter**, in
`skills/state/verified.yaml` (`chapter path: commit`), so the shipped Markdown carries no commit hashes
or revision footers (rusEFI's own documentation rule). The update skills read it, compare the
chapter's source notes against `git diff <commit>..HEAD`, and flag chapters whose sources moved.

## 4a. The worked example

**The Electronic throttle chapter (`documentation/docs/part3/electronic-throttle.md`) is the reference
chapter.** Read it before writing, and match its depth, structure, source notes, figures, examples and
tables.

## 5. Chapter template

Chapters come in two shapes. Use the one that fits; keep the section order.

### 5a. Module chapter (one firmware feature, e.g. Electronic throttle, Boost, Launch)

```markdown
# <Feature name as TunerStudio shows it>

<level badge>

> **In one sentence:** what this feature does for the engine.

## What it does                      (Basic)
## How it works                      (Intermediate)   at least one diagram
## Before you start                  (Basic)          hardware, wiring, prerequisites
## Setting it up                     (Basic → Intermediate)
   Numbered steps, one per action, a screenshot for every dialog visited.
   Every setting on the dialog explained in the order it appears.
## Worked examples                   (Intermediate)   at least two, real values, and why
## Tuning it                         (Intermediate → Advanced)
## Diagnostics                       (Intermediate)   error codes, output channels to log, gauges
## Troubleshooting                   (Basic → Advanced)   symptom → causes → checks, as a table
## Settings reference                generated (section 7), never hand-copied
## Related
```

### 5b. Topic chapter (how EFI works, installing, flashing firmware, wiring practice, …)

Same voice and standards, free structure, but always:
**Overview** → **Concepts** (with diagrams) → **Procedure** (numbered steps, one screenshot or diagram
per step that changes something) → **Examples** → **Pitfalls / troubleshooting** → **Related**.

**Which tool.** TunerStudio is the manual's tool for configuring and tuning: every setup and tuning
procedure is written and shot in TunerStudio. The rusEFI console is covered where it does what
TunerStudio cannot (firmware update and recovery, engine sniffer, Lua, pinout, knock analyzer, SD-card
log download, AI troubleshooting). One tool per job, never both: a step done in the console says so in
its first line ("This is done in the rusEFI console"). Part I's *Your two tools* chapter explains the
split once; the console's Setup Wizard and Tuning tab live only in the Part VII appendix *Tuning in the
rusEFI console* — chapters do not mention them.

Where a procedure differs by operating system, use content tabs (**Windows** first, then **Linux**,
then **macOS**) rather than three separate procedures.

## 6. Illustrations — the standard

Rich illustration is required, not decoration. **Minimums per chapter:** one diagram explaining the
mechanism, one screenshot per dialog or tab the chapter tells the reader to use, and one annotated
figure for any procedure with more than three steps.

| Kind | How it is made | Where it lives |
|---|---|---|
| **Tool screenshots** | Never by hand. Taken on the bench (`tools/bench/bench.sh`): the bench ECUs run Proteus-identified bench firmware whose `.ini` is the official Proteus F7 one except for pin-name lists (checked by `tools/bench/compare_ini.py` on every rebuild); TunerStudio and the console run on a virtual display, driven by a script. Never shoot an opened output-pin dropdown or a raw MCU-pin field on the bench. Every chapter keeps its captures in `tools/shots/<chapter>.sh` so all of them can be re-shot after a firmware or UI change. **Show the feature switched on with the chapter's example values**; a dialog of greyed controls documents nothing. Crop to the dialog being discussed. | `documentation/docs/img/ts/`, `documentation/docs/img/console/` |
| **Windows screenshots** | Taken in the Windows 11 VM from a clean snapshot, by script, so installs can be re-shot. | `documentation/docs/img/windows/` |
| **Annotated screenshots** | The capture plus numbered callout markers (SVG overlay) keyed to the steps in the text. | as above |
| **Diagrams** (wiring, signal flow, trigger wheels, state machines, timing) | Hand-written SVG in the house style below. No raster diagrams. | `documentation/docs/img/diagrams/` |
| **Plots** (sensor curves, table shapes, logged traces) | Generated by a script from real data (firmware defaults, bench logs) so they can be regenerated. | `documentation/docs/img/plots/` |

**House style for diagrams:** a `viewBox` and no fixed size, transparent background, colours set by
classes with a `prefers-color-scheme: dark` block so the diagram reads in both themes, one sans font,
2 px strokes, the palette **blue = what is asked for, orange = what is driven, green = closed loop,
red = safety**, wire colours as the real wire (with the colour named in a label), connector pins
labelled with the real connector and pin from the board's `connectors/*.yaml`, signal names in `mono`.

**Every figure** has a number (counted within its page until chapter numbers are fixed), a caption that says what to look at, and alt text:

```markdown
<figure markdown>
  ![ETB control loop: pedal target, PID, H-bridge duty and measured TPS](img/diagrams/etb-loop.svg)
  <figcaption>Figure 2 — The throttle controller closes the loop on TPS.</figcaption>
</figure>
```

## 7. Settings reference — generated

`tools/gen_settings.py` writes one Markdown table per TunerStudio dialog from `rusefi_config.txt` and
the template `.ini`: TunerStudio label, internal name, units, range, and the help text. Chapters
include it (`--8<-- "reference/settings/etb.md"`). Authors do **not** copy settings tables by hand. If
a setting's help text is missing, wrong or unclear, the fix belongs **upstream in
`rusefi_config.txt`** (it is also TunerStudio's tooltip): note it in the chapter's report as a
proposed upstream change.

## 8. Callouts

Material admonitions, used for these meanings only:

| Callout | Use for |
|---|---|
| `!!! tip` | A better way, a shortcut, a rule of thumb from experience. |
| `!!! note` | Background that helps but is not needed to follow along. |
| `!!! example` | A worked example inline. |
| `!!! warning` | Can cost time, a part, or a bad tune. |
| `!!! danger` | Can damage the engine or hurt someone (fuel, fire, runaway throttle, over-boost). |
| `!!! info "Advanced"` | A deeper aside a Basic reader may skip. |

At most one callout per screen of text.

**Bench conditions for live captures:** every calibration and every reading shown in a screenshot is
taken with the ECU on **12 V (ignition on)**, never on USB power alone: on USB the 5 V sensor
supplies cannot reach 5 V (about 4.5 V at best on the bench board), so every ratiometric sensor
(TPS, pedal, MAP) reads wrong. In the manual, state the rule; describe a board's supply circuit
only where its schematic or board files say so. Procedures in the manual say the
same to the reader.

**Check every figure by rendering it** before handing it back: a diagram whose labels overflow their
boxes, or a screenshot of the wrong dialog, is worse than none.

## 9. What an author hands back

With the chapter files, a short report:

- files written and figures made (with their shoot/generate commands);
- **open-questions**: every point the source did not settle, with the file and function looked at;
- **upstream fixes**: help texts in `rusefi_config.txt` that are missing, wrong or unclear, with the
  proposed wording;
- **bugs found**: anything in the firmware, console or `.ini` that behaves differently from its own
  documentation or from common sense, with the file and function — reported, not fixed in the chapter.

## 10. Review checklist

A chapter is accepted when:

- [ ] It follows the template for its kind, sections in order, level badges on every section.
- [ ] Every setting of the feature is covered (the generated table is included, and every setting a
      reader must set is explained in the walkthrough).
- [ ] Figure minimums met; every figure numbered, captioned, alt-texted, and reproducible.
- [ ] Every factual paragraph has a source note; nothing contradicts the code.
- [ ] Verified commit recorded in `skills/state/verified.yaml`.
- [ ] Two or more worked examples with real values.
- [ ] Troubleshooting table present.
- [ ] No screenshot or text shows an unofficial board.
- [ ] Builds without warnings (`mkdocs build --strict`).
