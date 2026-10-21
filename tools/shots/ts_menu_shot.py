#!/usr/bin/env python3
"""Open a TunerStudio dialog by its menu path and capture only that dialog.

    python3 -I tools/shots/ts_menu_shot.py "Fuel ▸ Injector Setup ▸ Injection configuration" out.png

The first step is a toolbar button (Setup, Fuel, … View) or the File menu; each later step is a menu
item, found by reading the open menu with tesseract, so it does not depend on fixed coordinates.
Prints the opened window's id and title; the dialog stays open so values can be set before a re-capture
(`import -window <id>`). TunerStudio must be running on the bench display (BENCH_DISPLAY, default :99).
"""
import csv
import difflib
import io
import os
import re
import subprocess
import sys
import time

TOOLBAR = {"setup": 110, "fuel": 290, "ignition": 494, "cranking": 690, "idle": 876, "advanced": 1070,
           "sensors": 1250, "can-bus": 1434, "controller": 1630, "view": 1824}   # button centres at y 68, 1920 px wide
ENV = dict(os.environ, DISPLAY=os.environ.get("BENCH_DISPLAY", ":99"))


def run(*cmd, capture=False):
    r = subprocess.run(cmd, env=ENV, capture_output=True, text=not capture)
    return r.stdout


def windows():
    return {l.split()[0]: " ".join(l.split()[3:]) for l in run("wmctrl", "-l").splitlines() if l.strip()}


def ocr_lines(x, y, w, h, psm=4):
    """Text lines in a screen region, as (text, x, centre y) in screen coordinates. Tesseract groups the
    words into lines itself (a menu is one column of text, page segmentation mode 4; mode 6, one block,
    reads some lines that mode 4 drops)."""
    png = run("import", "-window", "root", "-crop", f"{w}x{h}+{x}+{y}", "+repage", "-colorspace", "Gray",
              "-resize", "300%", "png:-", capture=True)
    tsv = subprocess.run(["tesseract", "stdin", "stdout", "--psm", str(psm), "tsv"], input=png, capture_output=True).stdout.decode()
    lines = {}
    for row in csv.DictReader(io.StringIO(tsv), delimiter="\t", quoting=csv.QUOTE_NONE):
        if row["level"] != "5" or not row["text"].strip():
            continue
        key = (row["block_num"], row["par_num"], row["line_num"])
        cy = (int(row["top"]) + int(row["height"]) // 2) // 3
        lines.setdefault(key, []).append((int(row["left"]) // 3, cy, row["text"]))
    out = []
    for words in lines.values():
        words.sort()
        # menu icons read as short junk tokens ("©,", "I)", "DD)") ahead of the item text
        while len(words) > 1 and (len(words[0][2]) <= 2 or re.search(r"[^\w-]", words[0][2])):
            words.pop(0)
        text = " ".join(w for _, _, w in words)
        cy = sorted(c for _, c, _ in words)[len(words) // 2]
        out.append((text, x + words[0][0] + 10, y + cy))
    return out


def score(line, want):
    """Similarity of an OCR line to a menu item; a line that contains the item (OCR merges the first
    item with the tab row behind the menu) counts as a match."""
    text = line.lower()
    ratio = difflib.SequenceMatcher(None, text, want).ratio()
    if text.strip() == want:
        return 2.0
    return max(ratio, 0.9) if want in text else ratio


def find(region, want):
    want = want.lower()
    x, y, w, h = region
    for psm, width in ((4, w), (6, w), (4, w * 6 // 10), (6, w * 6 // 10)):   # narrower: less of the gauges behind
        lines = ocr_lines(x, y, width, h, psm=psm)
        best = max(lines, key=lambda l: score(l[0], want), default=None)
        if best and score(best[0], want) >= 0.6:
            return best
    sys.exit(f"menu item '{want}' not found; menu reads: {[l[0] for l in lines]}")


def main():
    path, out = [p.strip() for p in sys.argv[1].split("▸")], sys.argv[2]
    before = windows()
    run("wmctrl", "-a", "TunerStudio MS"); time.sleep(0.3); run("xdotool", "key", "Escape"); time.sleep(0.2)
    if path[0].lower() == "file":
        mx, my = 15, 35
    else:
        mx, my = TOOLBAR[path[0].lower()], 68
    run("xdotool", "mousemove", str(mx), str(my), "click", "1"); time.sleep(0.9)
    left, top = mx - 120, my + 12
    for i, item in enumerate(path[1:]):
        text, ix, iy = find((max(0, left), top, 520, 900), item)
        last = i == len(path) - 2
        run("xdotool", "mousemove", str(ix), str(iy)); time.sleep(0.6)
        if last:
            run("xdotool", "click", "1")
        else:
            run("xdotool", "click", "1"); time.sleep(0.8)
            left, top = ix + 150, iy - 30
    time.sleep(3)
    new = [w for w in windows() if w not in before]
    if not new:
        sys.exit(f"no dialog opened for {sys.argv[1]}")
    wid = new[-1]
    run("import", "-window", wid, out)
    print(wid, windows()[wid])


main()
