#!/usr/bin/env python3
"""Put a figure under every <!-- shot: --> marker whose screenshot now exists.

    python3 -I tools/shots/place_figures.py [--renumber] [chapter.md ...]

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

FORCE = "--renumber" in sys.argv   # renumber even when nothing new is placed
pages = [pathlib.Path(p).resolve() for p in sys.argv[1:] if p != "--renumber"] or sorted(DOCS.rglob("*.md"))


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


def renumber(text, page):
    """Number the figures 1, 2, 3 … in order and move every in-text reference with its figure. A marker
    whose figure is not placed yet keeps a number of its own, so placing it later shifts nothing."""
    slots = []   # (start of the number, old number or 0, is a marker)
    for m in re.finditer(r"figcaption>Figure (\d+)", text):
        slots.append((m.start(1), int(m.group(1)), False))
    for m in MARK.finditer(text):
        img = m.group(2)
        if f"]({os.path.relpath(DOCS / img, page.parent)})" in text:
            continue   # its figure follows and is counted by its caption
        n = re.match(r"\s*Figure (\d+) —", m.group(5))
        start = m.start(5) + n.start(1) if n else None
        slots.append((start if n else m.start(5), int(n.group(1)) if n else 0, not n))
    slots.sort()
    old = [o for _, o, _ in slots if o]
    if len(old) != len(set(old)):
        sys.exit(f"{page.name}: figure numbers repeat; fix them by hand")
    new = {o: i + 1 for i, (_, o, _) in enumerate(slots) if o}
    at = {s: (i + 1, bare) for i, (s, o, bare) in enumerate(slots)}
    out, last = [], 0
    for s in sorted(at):
        n, bare = at[s]
        if bare:   # an unnumbered marker caption: give it its number
            out.append(text[last:s] + f" Figure {n} —")
            last = s
        else:
            m = re.match(r"\d+", text[s:])
            out.append(text[last:s] + str(n))
            last = s + m.end()
    text = "".join(out) + text[last:]
    # in-text references, outside captions and marker numbers already set above
    return re.sub(r"(?<!figcaption>)(?<!\| )Figure (\d+)(?! —)",
                  lambda m: f"Figure {new.get(int(m.group(1)), int(m.group(1)))}", text)


for page in pages:
    text, placed = page.read_text(), 0
    while (new := place_one(page, text)) is not None:
        text, placed = new, placed + 1
    if placed or FORCE:
        new = renumber(text, page)
        if new != text or placed:
            page.write_text(new)
        print(f"{page.relative_to(DOCS)}: placed {placed} figure(s)")
