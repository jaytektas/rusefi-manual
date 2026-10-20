#!/usr/bin/env python3
"""Hide figures whose image does not exist yet, and show them again once it does.

    python3 -I tools/pending_figures.py

A chapter may place a <figure> for a screenshot that is still to be taken (its <!-- shot: --> marker
sits beside it). Until the image exists the strict build fails on the broken link, so the figure is
wrapped in <!-- pending-figure ... pending-figure --> instead. When the screenshot pass adds the image,
the next run unwraps it. "--" inside a held figure is stored as "&#45;&#45;" and restored on unwrap.
"""
import pathlib
import re

DOCS = pathlib.Path(__file__).resolve().parent.parent / "documentation/docs"
FIG = re.compile(r"<figure markdown>\n.*?</figure>", re.S)
HELD = re.compile(r"<!-- pending-figure\n(.*?)\npending-figure -->", re.S)
held = shown = 0


def missing(block, page):
    for target in re.findall(r"\]\(([^)\s]+\.(?:png|svg|jpg))\)", block):
        if not (page.parent / target).resolve().exists():
            return True
    return False


for page in sorted(DOCS.rglob("*.md")):
    text = page.read_text()
    new = HELD.sub(lambda m: (m.group(0) if missing(m.group(1).replace("&#45;&#45;", "--"), page)
                              else m.group(1).replace("&#45;&#45;", "--")), text)
    before = len(HELD.findall(new))
    shown += len(HELD.findall(text)) - before
    new = FIG.sub(lambda m: ("<!-- pending-figure\n" + m.group(0).replace("--", "&#45;&#45;") + "\npending-figure -->"
                             if missing(m.group(0), page) else m.group(0)), new)
    held += len(HELD.findall(new)) - before
    if new != text:
        page.write_text(new)
print(f"held back {held} figure(s) with missing images, showed {shown} whose image now exists")
