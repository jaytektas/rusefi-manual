#!/usr/bin/env bash
# Screenshot one TunerStudio dialog, opened through TunerStudio's own search box (reliable, unlike
# clicking menu coordinates). TunerStudio must be running on the bench's virtual display.
#
#   tools/shots/ts_shot.sh "<search text>" <out.png> [result number, default 1] [ImageMagick crop]
#   tools/shots/ts_shot.sh --list "<search text>" <out.png>   (photograph the result list, to pick a number)
#
# The search lists matching sections and fields; result 1 is the first. Captures the dialog window only
# (never TunerStudio's main window, whose title carries the registration name), then closes it.
set -euo pipefail
export DISPLAY="${BENCH_DISPLAY:-:99}"
if [ "${1:-}" = "--list" ]; then
    wmctrl -a "TunerStudio MS"; sleep 0.4; xdotool key Escape; sleep 0.2
    xdotool mousemove 1835 36 click 1; sleep 0.3; xdotool key ctrl+a; xdotool type --delay 40 "$2"; sleep 1.5
    import -window root -crop 760x700+1160+40 +repage "$3"; xdotool key Escape; echo "results: $3"; exit 0
fi
Q="$1"; OUT="$2"; N="${3:-1}"; CROP="${4:-}"
before=$(wmctrl -l | awk '{print $1}' | sort)
wmctrl -a "TunerStudio MS"; sleep 0.4
xdotool key Escape; sleep 0.2
xdotool mousemove 1835 36 click 1; sleep 0.3
xdotool key ctrl+a; xdotool type --delay 40 "$Q"; sleep 1.5
for _ in $(seq "$N"); do xdotool key Down; sleep 0.15; done
xdotool key Return; sleep 3
new=$(comm -13 <(echo "$before") <(wmctrl -l | awk '{print $1}' | sort) | tail -1)
[ -n "$new" ] || { echo "ts_shot: no dialog opened for '$Q'" >&2; exit 1; }
title=$(wmctrl -l | awk -v w="$new" '$1==w {$1=$2=$3=""; sub(/^ +/,""); print}')
mkdir -p "$(dirname "$OUT")"
if [ -n "$CROP" ]; then import -window "$new" -crop "$CROP" +repage "$OUT"; else import -window "$new" "$OUT"; fi
wmctrl -i -c "$new"; sleep 0.8
echo "ts_shot: '$Q' -> [$title] -> $OUT ($(identify -format '%wx%h' "$OUT"))"
