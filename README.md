# The rusEFI Manual

*From first spark to full tune.*

A community manual for [rusEFI](https://github.com/rusefi/rusefi) on official rusEFI hardware, using
TunerStudio and the rusEFI console: how electronic fuel injection works, installing, flashing firmware,
wiring, configuring, tuning and troubleshooting. Examples use the Proteus F7.

**Read it:** https://jaytektas.github.io/rusefi-manual/

Every fact in the manual is checked against the rusEFI source code; each paragraph carries a hidden
source note naming the file it came from. See [`STANDARD.md`](STANDARD.md) for how chapters are written.

## Found a mistake?

Open an issue: say which chapter and section, what is wrong, what you expected, and your rusEFI firmware
version and board. Reports are checked against the rusEFI source before anything changes.

## Building it yourself

```
python3 -m venv .venv
.venv/bin/pip install -r documentation/requirements.txt
cd documentation && ../.venv/bin/mkdocs serve
```

## Tools

| Script | Does |
|---|---|
| `tools/check_src.py` | every source note cites a file that exists in the rusEFI checkout (`$RUSEFI`, default `../rusefi`) |
| `tools/gen_settings.py` | generates the settings-reference tables from the official TunerStudio `.ini` (`$RUSEFI_INI`) |
| `tools/stale_chapters.py` | lists chapters whose sources changed in rusEFI since they were verified |
| `tools/mlg.py` | reads MegaLogViewer binary logs (`.mlg`) for figures |
| `tools/figures/` | scripts that draw the manual's plots from recorded data |

## Licence

The manual (text, diagrams, plots and screenshots) and everything else in this repository is licensed
under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); see [`LICENSE`](LICENSE). Credit
*Jason Roughley and the rusEFI Manual contributors* and share adaptations under the same licence. The names rusEFI,
TunerStudio and MegaLogViewer belong to their owners.

rusEFI itself is free software under the GPL v3 with additional terms; see the manual's
*Read this first* page.
