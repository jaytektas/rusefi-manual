#!/usr/bin/env python3
"""Fail if any forbidden term (.private/forbidden.txt, never committed) appears in the shipped manual.

    python3 -I tools/check_forbidden.py

Searches documentation/ text files (Markdown, YAML, CSS, SVG) and reads every PNG/JPG under
documentation/docs/img with OCR (tesseract), because screenshots are where a private board name,
a firmware signature or a registration name slips in (window titles, pin names, dialogs).
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "documentation"
TERMS = pathlib.Path(os.environ.get("FORBIDDEN_TERMS", ROOT / ".private/forbidden.txt"))
if not TERMS.exists():
    sys.exit(f"no term list at {TERMS} (private, not in the repository): cannot check")
terms = [t.strip() for t in TERMS.read_text().splitlines()
         if t.strip() and not t.startswith("#")]
# the owner's GitHub account name appears in the repository URLs by necessity; nothing else may match
ALLOWED = re.compile(r"jaytektas", re.I)
pattern = re.compile("|".join(re.escape(t) for t in terms), re.I)
hits = []
for f in DOC.rglob("*"):
    if "site" in f.relative_to(DOC).parts[:1] or not f.is_file():
        continue
    if f.suffix in (".md", ".yml", ".yaml", ".css", ".svg", ".html", ".txt"):
        for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            for m in pattern.finditer(ALLOWED.sub("", line)):
                hits.append(f"{f.relative_to(ROOT)}:{n}: '{m.group(0)}'")
if not shutil.which("tesseract"):
    sys.exit("tesseract not installed (apt install tesseract-ocr): screenshots cannot be checked")
images = [f for f in (DOC / "docs/img").rglob("*") if f.suffix.lower() in (".png", ".jpg", ".jpeg")]
for img in images:
    text = subprocess.run(["tesseract", str(img), "-", "--psm", "11"], capture_output=True, text=True).stdout
    for m in pattern.finditer(text):
        hits.append(f"{img.relative_to(ROOT)} (OCR): '{m.group(0)}'")
print(f"{len(terms)} terms, {len(images)} images OCR'd")
print("\n".join(hits) or "OK: nothing forbidden found")
sys.exit(1 if hits else 0)
