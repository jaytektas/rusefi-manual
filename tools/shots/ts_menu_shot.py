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


def ocr_lines(x, y, w, h):
    """Text lines in a screen region, as (text, centre x, centre y) in screen coordinates."""
    png = run("import", "-window", "root", "-crop", f"{w}x{h}+{x}+{y}", "+repage", "-resize", "200%", "png:-", capture=True)
    tsv = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "11", "tsv"], input=png, capture_output=True).stdout.decode()
    lines = {}
    for row in csv.DictReader(io.StringIO(tsv), delimiter="\t", quoting=csv.QUOTE_NONE):
        if row["level"] != "5" or not row["text"].strip():
            continue
        top = int(row["top"]) // 2
        key = next((k for k in lines if abs(k - top) <= 6), top)
        lines.setdefault(key, []).append((int(row["left"]) // 2, int(row["width"]) // 2, row["text"]))
    out = []
    for top, words in lines.items():
        words.sort()
        text = " ".join(t for _, _, t in words)
        out.append((text, x + words[0][0] + 20, y + top + 8))
    return out


def score(line, want):
    """Similarity of an OCR line to a menu item; a line that contains the item (OCR merges the first
    item with the tab row behind the menu) counts as a match."""
    text = line.lower()
    return 1.0 if want in text else difflib.SequenceMatcher(None, text, want).ratio()


def find(lines, want):
    want = want.lower()
    best = max(lines, key=lambda l: score(l[0], want), default=None)
    if not best or score(best[0], want) < 0.6:
        sys.exit(f"menu item '{want}' not found; menu reads: {[l[0] for l in lines]}")
    return best


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
        text, ix, iy = find(ocr_lines(max(0, left), top, 520, 900), item)
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
