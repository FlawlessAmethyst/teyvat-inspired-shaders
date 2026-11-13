#!/usr/bin/env bash
# Run inside the scoped GenshinShaderDev desktop session.
set -euo pipefail
root=$1
batch=$2
mode=${batch%-0[12]}
dest="$root/$batch"
replay=(python3 evidence/task-15/replay.py)
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
test ! -e "$dest"
"${replay[@]}" "$mode" "$root"
"${game[@]}" launch --timeout 120
sleep 10

world_name_mask() {
    magick "$1" -crop 350x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}

reference="$root/world-list-reference.png"
if [[ ! -f "$reference" ]]; then
    "${game[@]}" screenshot "$dest/title.png"
    "${game[@]}" click 1280 535
    "${game[@]}" screenshot "$dest/world-list.png"
    echo 'Inspect the first world row and retain its screenshot as world-list-reference.png.'
    exit 0
fi
for attempt in {1..8}; do
    "${game[@]}" screenshot "$dest/world-list.png"
    if [[ $(world_name_mask "$dest/world-list.png") == "$(world_name_mask "$reference")" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo 'Could not verify TASK-15 Fog Scenes in the first row' >&2
        exit 1
    fi
    "${game[@]}" click 1280 535
done
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 8
if [[ "$batch" == sodium-01 ]]; then
    "${replay[@]}" build "$root"
fi
"${replay[@]}" profile "$dest/runs" daylight sunset
if [[ "$batch" == *-01 ]]; then
    "${replay[@]}" capture "$dest" daylight sunset rain night open-water cave
fi
"${game[@]}" stop --timeout 60
"${game[@]}" logs
