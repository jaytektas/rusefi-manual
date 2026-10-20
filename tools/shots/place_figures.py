#!/usr/bin/env python3
"""Put a figure under every <!-- shot: --> marker whose screenshot now exists.

    python3 -I tools/shots/place_figures.py [chapter.md ...]

The marker reads  <!-- shot: <image> | <where> | <state> | <caption> -->. Its figure gets the image, an
alt text built from where and state, and the caption. A caption that already starts "Figure N —" keeps
its number; one without gets the next number after the figure before it, and the chapter is refused if
that number is already used later on, so in-text "Figure N" references never silently go stale.
A marker whose image is already shown (held or not) is left alone.
"""
import os
import pathlib
import re
import sys

DOCS = pathlib.Path(__file__).resolve().parent.parent.parent / "documentation/docs"
MARK = re.compile(r"^<!-- shot: ([^ |]+) \| ([^|]+)\| ([^|]+)\|([^\n]*?)-->\n", re.M)
NUM = re.compile(r"figcaption>Figure (\d+)|\| *Figure (\d+) —")

pages = [pathlib.Path(p).resolve() for p in sys.argv[1:]] or sorted(DOCS.rglob("*.md"))


def place_one(page, text):
    """Text with the first placeable marker's figure added, or None when there is none left."""
    for m in MARK.finditer(text):
        img, where, state, caption = (g.strip() for g in m.groups())
        rel = os.path.relpath(DOCS / img, page.parent)
        if not (DOCS / img).exists() or f"]({rel})" in text:
            continue
        before = [int(a or b) for a, b in NUM.findall(text[:m.start()])]
        after = [int(a or b) for a, b in NUM.findall(text[m.end():])]
        if not re.match(r"Figure \d+ —", caption):
            n = max(before, default=0) + 1
            if n in after:
                sys.exit(f"{page.name}: {img} would be Figure {n}, already used later; number it in the marker")
            caption = f"Figure {n} — {caption}"
        alt = f"{where}: {state}".replace("]", ")").replace("[", "(")
        fig = f"\n<figure markdown>\n  ![{alt}]({rel})\n  <figcaption>{caption}</figcaption>\n</figure>\n"
        return text[:m.end()] + fig + text[m.end():]
    return None


for page in pages:
    text, placed = page.read_text(), 0
    while (new := place_one(page, text)) is not None:
        text, placed = new, placed + 1
    if placed:
        page.write_text(text)
        print(f"{page.relative_to(DOCS)}: placed {placed} figure(s)")
