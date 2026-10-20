#!/usr/bin/env python3
"""Write the manual's edition notice: which rusEFI commit the manual describes, and that it is unofficial.

    python3 -I tools/edition.py [--rusefi /path/to/rusefi]

The edition is the OLDEST rusEFI commit any chapter was verified against (skills/state/verified.yaml),
so the notice never claims more than every chapter has been checked for. Writes
documentation/docs/_edition.md, included by the home and safety pages (--8<-- "_edition.md").
Run after rusefi-docs-update-chapter moves a chapter's verified commit.
"""
import argparse
import datetime
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--rusefi", default=os.environ.get("RUSEFI", str(ROOT.parent / "rusefi")))
repo = ap.parse_args().rusefi

commits = []
for line in (ROOT / "skills/state/verified.yaml").read_text().splitlines():
    line = line.split("#")[0].strip()
    if ":" in line:
        commits.append(line.split(":", 1)[1].strip())


def show(c, fmt):
    return subprocess.run(["git", "-C", repo, "show", "-s", f"--format={fmt}", c],
                          capture_output=True, text=True, check=True).stdout.strip()


oldest = min(commits, key=lambda c: int(show(c, "%ct")))
full, short = show(oldest, "%H"), show(oldest, "%h")
date = datetime.datetime.fromtimestamp(int(show(oldest, "%ct")), datetime.timezone.utc).strftime("%-d %B %Y")
url = f"https://github.com/rusefi/rusefi/commit/{full}"

text = f"""!!! warning "Unofficial documentation"
    This manual is a community effort. It is **not official rusEFI documentation** and is not
    endorsed or reviewed by the rusEFI project. It describes rusEFI as of commit
    [`{short}`]({url}) ({date}); later firmware may behave differently. It is offered in the hope
    that it helps, **with no warranty of any kind** — see [Read this first](safety.md).
"""
(ROOT / "documentation/docs/_edition.md").write_text(text)
print(f"edition: rusEFI {short} ({date}) from {len(commits)} chapter(s)")
