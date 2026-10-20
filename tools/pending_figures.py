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
FIG = re.compile(r"^([ \t]*)<figure markdown>\n.*?</figure>", re.S | re.M)   # keeps the figure's indent (figures inside tabs)
HELD = re.compile(r"^([ \t]*)<!-- pending-figure\n(.*?)\n[ \t]*pending-figure -->", re.S | re.M)
held = shown = 0


def missing(block, page):
    for target in re.findall(r"\]\(([^)\s]+\.(?:png|svg|jpg))\)", block):
        if not (page.parent / target).resolve().exists():
            return True
    return False


for page in sorted(DOCS.rglob("*.md")):
    text = page.read_text()
    new = HELD.sub(lambda m: (m.group(0) if missing(m.group(2).replace("&#45;&#45;", "--"), page)
                              else m.group(2).replace("&#45;&#45;", "--")), text)
    before = len(HELD.findall(new))
    shown += len(HELD.findall(text)) - before
    def hold(m):
        ind = m.group(1)
        if not missing(m.group(0), page) or new[max(0, m.start() - 40):m.start()].rstrip().endswith("<!-- pending-figure"):
            return m.group(0)
        return f"{ind}<!-- pending-figure\n" + m.group(0).replace("--", "&#45;&#45;") + f"\n{ind}pending-figure -->"
    new = FIG.sub(hold, new)
    held += len(HELD.findall(new)) - before
    if new != text:
        page.write_text(new)
print(f"held back {held} figure(s) with missing images, showed {shown} whose image now exists")
