#!/usr/bin/env bash
# Run from the repository root with scoped desktop access.
set -euo pipefail
root=$1
mode=$2
shift 2
case "$mode" in
    pack|sodium|pack-repeat) ;;
    *) exit 2 ;;
esac
dest="$root/$mode"
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
replay=(python3 evidence/task-25/replay.py)

world_name_mask() {
    magick "$1" -crop 425x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}

if [[ ${1:-} == open ]]; then
    shift
else
    test ! -e "$dest"
    "${replay[@]}" "${mode%-repeat}" "$root"
    "${game[@]}" launch --timeout 120
    sleep 10
    "${game[@]}" screenshot "$dest/title.png"
    "${game[@]}" click 1280 535
fi
"${game[@]}" screenshot "$dest/world-list.png"
test "$(world_name_mask "$dest/world-list.png")" = "$(world_name_mask "$root/world-list-reference.png")"
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 10
"${replay[@]}" capture "$dest" "$@"
"${game[@]}" stop --timeout 60
"${game[@]}" logs
