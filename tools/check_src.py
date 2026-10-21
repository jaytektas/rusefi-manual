#!/usr/bin/env python3
"""Check every hidden source note in the manual (STANDARD.md section 4).

    python3 -I tools/check_src.py [rusefi checkout]   (default $RUSEFI, else ../rusefi next to this repo)

A note looks like  <!-- src: firmware/path/file.cpp (what to look for); other/file.h (...) -->
Each part names a FILE (path from the rusEFI repository root) and says in words what to look for.
Fails (exit 1) if a cited file does not exist, a note cites a line number, or a comment is left unclosed.
"""
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUSEFI = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("RUSEFI", ROOT.parent / "rusefi"))
NOTE = re.compile(r"<!--\s*src:(.*?)-->", re.S)
LINE_NO = re.compile(r"(:\d+\b|\bline\s+\d+|\bL\d+\b|#L\d+)", re.I)

problems, notes = [], 0
for md in sorted((ROOT / "documentation" / "docs").rglob("*.md")):
    text = md.read_text()
    # an unclosed <!-- hides everything after it until the next --> (held figures, notes): the page loses prose silently
    depth = 0
    for n, tok in enumerate(re.findall(r"<!--|-->", text)):
        depth += 1 if tok == "<!--" else -1
        if depth not in (0, 1):
            problems.append(f"{md.relative_to(ROOT)}: comment opened inside another comment (an earlier <!-- is not closed)")
            break
    if depth == 1:
        problems.append(f"{md.relative_to(ROOT)}: a <!-- comment is never closed")
    for m in NOTE.finditer(text):
        notes += 1
        where = f"{md.relative_to(ROOT)}: <!-- src:{m.group(1).strip()[:60]}... -->"
        if LINE_NO.search(m.group(1)):
            problems.append(f"{where}\n    cites a line number")
        for part in re.split(r";(?![^()]*\))", m.group(1)):
            path = part.strip().split(" ")[0].strip()
            if path and not (RUSEFI / path).exists():
                problems.append(f"{where}\n    no such file: {path}")
print(f"{notes} source notes checked")
print("\n".join(problems) or "OK")
sys.exit(1 if problems else 0)
