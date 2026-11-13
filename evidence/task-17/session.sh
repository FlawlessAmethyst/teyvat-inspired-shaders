#!/usr/bin/env bash
# Run from the repository root in the scoped GenshinShaderDev desktop session.
set -euo pipefail
root=$1
batch=$2
dest="$root/$batch"
mode=${batch%%-*}
replay=(python3 evidence/task-17/replay.py)
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
reference="$root/world-list-reference.png"

if [[ ${3:-} != open ]]; then
    test ! -e "$dest"
    mc_dir=$(python3 -c 'import sys; sys.path.insert(0,"tools"); import minecraft; print(minecraft.GAME)')
    diff -rq "$root/shaders" "$mc_dir/shaderpacks/TASK-17-prototype/shaders"
    "${replay[@]}" "$mode" "$root"
    "${game[@]}" launch --timeout 240
    sleep 10
    "${game[@]}" screenshot "$dest/title.png"
    "${game[@]}" click 1280 535
fi
"${game[@]}" screenshot "$dest/world-list.png"
if [[ ! -f "$reference" ]]; then
    echo 'Inspect the first row and copy its screenshot to world-list-reference.png.'
    exit 0
fi

world_name_mask() {
    magick "$1" -crop 390x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}
if [[ $(world_name_mask "$dest/world-list.png") != "$(world_name_mask "$reference")" ]]; then
    echo 'Could not verify TASK-17 Prototype Scenes in the first row' >&2
    exit 1
fi
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 8
"${replay[@]}" profile "$dest/runs"
"${game[@]}" stop --timeout 60
"${game[@]}" logs
