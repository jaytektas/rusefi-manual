#!/usr/bin/env python3
"""Put a figure under every <!-- shot: --> marker whose screenshot now exists.

    python3 -I tools/shots/place_figures.py [chapter.md ...]

The marker reads  <!-- shot: <image> | <where> | <state> | <caption> -->. Its figure gets the image, an
alt text built from where and state, and the caption. A caption that already starts "Figure N —" keeps
its number; one without gets the next number after the figure before it. If that number is already used
later on, the chapter's figures are renumbered in order and every in-text "Figure N" follows its figure,
so references never silently go stale.
A marker whose image is already shown (held or not) is left alone.
"""
import os
import pathlib
import re
import sys

DOCS = pathlib.Path(__file__).resolve().parent.parent.parent / "documentation/docs"
MARK = re.compile(r"^([ \t]*)<!-- shot: ([^ |]+) \| ([^|]+)\| ([^|]+)\|([^\n]*?)-->\n", re.M)   # keeps the marker's indent (inside tabs)
NUM = re.compile(r"figcaption>Figure (\d+)|\| *Figure (\d+) —")

pages = [pathlib.Path(p).resolve() for p in sys.argv[1:]] or sorted(DOCS.rglob("*.md"))


def place_one(page, text):
    """Text with the first placeable marker's figure added, or None when there is none left."""
    for m in MARK.finditer(text):
        ind = m.group(1)
        img, where, state, caption = (g.strip() for g in m.groups()[1:])
        rel = os.path.relpath(DOCS / img, page.parent)
        if not (DOCS / img).exists() or f"]({rel})" in text:
            continue
        alt = f"{where}: {state}".replace("]", ")").replace("[", "(")
        if text[:m.start()].rstrip().endswith("<figure markdown>"):
            # the marker stands in for the image inside a figure the chapter already wrote
            return text[:m.end()] + f"{ind}![{alt}]({rel})\n" + text[m.end():]
        before = [int(a or b) for a, b in NUM.findall(text[:m.start()])]
        after = [int(a or b) for a, b in NUM.findall(text[m.end():])]
        if not re.match(r"Figure \d+ —", caption):
            n = max(before, default=0) + 1
            caption = f"Figure {0 if n in after else n} — {caption}"   # 0: renumbered below
        alt = f"{where}: {state}".replace("]", ")").replace("[", "(")
        fig = f"\n{ind}<figure markdown>\n{ind}  ![{alt}]({rel})\n{ind}  <figcaption>{caption}</figcaption>\n{ind}</figure>\n"
        return text[:m.end()] + fig + text[m.end():]
    return None


def renumber(text):
    """Number the figures 1, 2, 3 … in order and move every in-text reference with its figure."""
    caps = list(re.finditer(r"(figcaption>Figure )(\d+)", text))
    old = [int(m.group(2)) for m in caps]
    if old == list(range(1, len(old) + 1)):
        return text
    if len([o for o in old if o]) != len(set(o for o in old if o)):
        sys.exit("figure numbers repeat; fix them by hand")
    new = {o: i + 1 for i, o in enumerate(old) if o}
    marks = {m.start(2): str(i + 1) for i, m in enumerate(caps)}

    def ref(m):
        if m.start(1) in marks:
            return m.group(0)[:m.start(1) - m.start(0)] + marks[m.start(1)]
        n = int(m.group(1))
        return m.group(0)[:m.start(1) - m.start(0)] + str(new.get(n, n))
    return re.sub(r"Figure (\d+)", ref, text)


for page in pages:
    text, placed = page.read_text(), 0
    while (new := place_one(page, text)) is not None:
        text, placed = new, placed + 1
    if placed:
        text = renumber(text)
        page.write_text(text)
        print(f"{page.relative_to(DOCS)}: placed {placed} figure(s)")
