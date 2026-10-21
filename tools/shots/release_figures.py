#!/usr/bin/env python3
"""Release held figures whose image now exists: unwrap their <!-- pending-figure ... pending-figure --> block.

    python3 -I tools/shots/release_figures.py [--list] [chapter.md ...]

A held figure is a finished <figure> wrapped in a hidden block until its screenshot is taken. When the
image file it names exists under documentation/docs, the wrapper lines are removed and the figure shows.
--list prints every held figure and whether its image exists, without changing anything.
Run tools/check_forbidden.py before releasing: the image goes public with the page.
"""
import pathlib
import re
import sys

DOCS = pathlib.Path(__file__).resolve().parent.parent.parent / "documentation/docs"
BLOCK = re.compile(r"^[ \t]*<!-- pending-figure[ \t]*\n(.*?)^[ \t]*pending-figure -->[ \t]*\n", re.M | re.S)
IMG = re.compile(r"\]\((\.\./img/[^)]+)\)")

listing = "--list" in sys.argv
pages = [pathlib.Path(p).resolve() for p in sys.argv[1:] if p != "--list"] or sorted(DOCS.rglob("*.md"))
for page in pages:
    text = page.read_text()

    def release(m):
        img = IMG.search(m.group(1))
        target = (page.parent / img.group(1)).resolve() if img else None
        exists = bool(target and target.exists())
        if listing:
            print(f"{'ready ' if exists else 'held  '} {page.relative_to(DOCS)}  {img.group(1) if img else '(no image)'}")
            return m.group(0)
        if exists:
            print(f"released {page.relative_to(DOCS)}  {img.group(1)}")
            return m.group(1)
        return m.group(0)

    new = BLOCK.sub(release, text)
    if new != text and not listing:
        page.write_text(new)
