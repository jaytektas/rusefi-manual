#!/usr/bin/env python3
"""Read a MegaLogViewer binary log (.mlg, format 2), as written by TunerStudio and rusEFI's SD logger.

    python3 -I tools/mlg.py fields <log.mlg>                 list the logged fields
    python3 -I tools/mlg.py csv <log.mlg> <field> [field...] > out.csv

Layout (rusEFI docs/AI/sd_card_logging.md; firmware/console/binary_mlg_log/mlg_types.h, mlg_field.h):
24-byte header, 89-byte field descriptors, big-endian values, value = (raw + transform) * scale.
Data blocks: type(0) counter timestamp16 [fields] checksum; marker blocks (type 1) are skipped.
"""
import csv
import struct
import sys

TYPES = {0: ">B", 1: ">b", 2: ">H", 3: ">h", 4: ">I", 5: ">i", 6: ">q", 7: ">f"}


def read(path):
    data = open(path, "rb").read()
    magic, version, _ts, _info, data_begin, rec_len, n = struct.unpack(">6sHIIIHH", data[:24])
    if magic != b"MLVLG\0" or version != 2:
        sys.exit(f"{path}: not an MLG v2 file ({magic!r}, version {version})")
    fields, off = [], 24
    for _ in range(n):
        typ, name, units, _style, scale, transform, digits = struct.unpack(">B34s10sBffb", data[off:off + 55])
        fields.append(dict(type=typ, name=name.split(b"\0")[0].decode(errors="replace"),
                           units=units.split(b"\0")[0].decode(errors="replace"),
                           scale=scale, transform=transform, digits=digits))
        off += 89
    widths = [struct.calcsize(TYPES[f["type"]]) for f in fields]
    assert sum(widths) == rec_len, f"field widths {sum(widths)} != record length {rec_len}"
    rows, pos = [], data_begin
    while pos + 4 <= len(data):
        btype = data[pos]
        if btype == 1:                      # marker block: type, counter, timestamp, 50-byte message
            pos += 4 + 50
            continue
        if btype != 0 or pos + 4 + rec_len + 1 > len(data):
            break
        payload = data[pos + 4: pos + 4 + rec_len]
        if sum(payload) % 256 != data[pos + 4 + rec_len]:
            pos += 4 + rec_len + 1
            continue                         # bad checksum: drop the record
        vals, o = [], 0
        for f, w in zip(fields, widths):
            raw = struct.unpack(TYPES[f["type"]], payload[o:o + w])[0]
            vals.append((raw + f["transform"]) * f["scale"])
            o += w
        rows.append(vals)
        pos += 4 + rec_len + 1
    return fields, rows


def main(argv):
    cmd, path = argv[1], argv[2]
    fields, rows = read(path)
    if cmd == "fields":
        for i, f in enumerate(fields):
            print(f"{i:3} {f['name']} [{f['units']}]")
        print(f"{len(rows)} records", file=sys.stderr)
    elif cmd == "csv":
        names = [f["name"] for f in fields]
        idx = [names.index(n) for n in argv[3:]]
        w = csv.writer(sys.stdout)
        w.writerow(argv[3:])
        for r in rows:
            w.writerow([r[i] for i in idx])


if __name__ == "__main__":
    main(sys.argv)
