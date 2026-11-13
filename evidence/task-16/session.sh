#!/usr/bin/env bash
# Run in the scoped GenshinShaderDev desktop session.
set -euo pipefail
root=$1
batch=$2
mode=${batch%%-*}
dest="$root/$batch"
replay=(python3 evidence/task-16/replay.py)
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
test ! -e "$dest"
if [[ "$mode" != sodium ]]; then
    mc_dir=$(python3 -c 'import sys; sys.path.insert(0,"tools"); import minecraft; print(minecraft.GAME)')
    diff -rq "$root/variants/$mode/shaders" "$mc_dir/shaderpacks/TASK-16-$mode/shaders"
fi
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
    echo 'Inspect the first row and retain its screenshot as world-list-reference.png.'
    exit 0
fi
for attempt in {1..8}; do
    "${game[@]}" screenshot "$dest/world-list.png"
    if [[ $(world_name_mask "$dest/world-list.png") == "$(world_name_mask "$reference")" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo 'Could not verify TASK-16 Shadow Scenes in the first row' >&2
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
if [[ "$batch" == shadows-motion ]]; then
    "${replay[@]}" motion "$dest/motion"
    "${game[@]}" key F3
    "${game[@]}" screenshot "$dest/motion-debug.png"
    "${game[@]}" key 8 2
    "${game[@]}" screenshot "$dest/shadow-debug.png"
    "${game[@]}" key F3
else
    "${replay[@]}" profile "$dest/runs"
    if [[ "$batch" == *-01 ]]; then
        "${replay[@]}" capture "$dest"
    elif [[ "$batch" == fog-02 || "$batch" == shadows-02 ]]; then
        "${replay[@]}" capture "$dest" cave
    fi
fi
"${game[@]}" stop --timeout 60
"${game[@]}" logs
