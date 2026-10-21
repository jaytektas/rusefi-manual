#!/usr/bin/env python3
"""Set constants in the offline screenshot project's tune file, before TunerStudio loads it.

    python3 -I tools/shots/ts_tune_set.py <tune.msq> name=value [name=value ...]

A value is written as TunerStudio writes it: a list option or bit name in quotes ("Lowside 14"), a
number bare, a table as space-separated numbers in row order. Restart TunerStudio afterwards (kill it,
so it does not save its own copy over the file) and it opens the project with these values.
Only for the offline project: never point this at a tune that will be written to an ECU.
"""
import html
import re
import sys

tune, pairs = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
text = open(tune, encoding="iso-8859-1").read()
for name, value in pairs:
    # an empty string constant is saved as <constant name="x"/>; a set one holds its text unquoted
    text = re.sub(r'(<constant(?:\s+\w+="[^"]*")*?\s+name="%s"(?:\s+\w+="[^"]*")*)\s*/>' % re.escape(name),
                  r'\1></constant>', text)
    pat = re.compile(r'(<constant(?:\s+\w+="[^"]*")*?\s+name="%s"(?:\s+\w+="[^"]*")*>)(.*?)(</constant>)' % re.escape(name), re.S)
    m = pat.search(text)
    if not m:
        sys.exit(f"{name}: not in {tune}")
    old = m.group(2)
    if not re.fullmatch(r'\s*("[^"]*"|[-+0-9.eE\s]+)\s*', old):
        new = html.escape(value, quote=False)   # a string constant (or an empty one)
    elif old.strip().startswith('"'):
        new = '"' + html.escape(value, quote=False) + '"'
    elif "\n" in old.strip() or len(old.split()) > 1:
        cols = int(re.search(r'cols="(\d+)"', m.group(1)).group(1)) if 'cols="' in m.group(1) else 1
        nums = value.split()
        if len(nums) != len(old.split()):
            sys.exit(f"{name}: {len(old.split())} values expected, {len(nums)} given")
        new = "".join("\n         " + " ".join(nums[r:r + cols]) + " " for r in range(0, len(nums), cols)) + "\n      "
    else:
        new = value
    text = text[:m.start(2)] + new + text[m.end(2):]
    print(f"{name}: {old.strip()[:40]} -> {new.strip()[:40]}")
open(tune, "w", encoding="iso-8859-1").write(text)
