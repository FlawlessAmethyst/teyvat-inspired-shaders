#!/usr/bin/env bash
# Run from the repository root with scoped desktop access.
set -euo pipefail
root=$1
batch=$2
mode=${batch%%-*}
case "$batch" in
    control-01|control-02|lighting-01|lighting-02|sodium-01|sodium-02) ;;
    *) exit 2 ;;
esac
dest="$root/$batch"
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
replay=(python3 evidence/task-22/replay.py)

world_name_mask() {
    magick "$1" -crop 390x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}

if [[ ${3:-} != open ]]; then
    test ! -e "$dest"
    "${replay[@]}" "$mode" "$root"
    "${game[@]}" launch --timeout 120
    sleep 10
    "${game[@]}" screenshot "$dest/title.png"
    "${game[@]}" click 1280 535
fi
expected=$(world_name_mask "$root/world-list-reference.png")
for attempt in {1..8}; do
    "${game[@]}" screenshot "$dest/world-list.png"
    if [[ $(world_name_mask "$dest/world-list.png") == "$expected" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo 'Could not verify TASK-22 Lighting Scenes in the first row' >&2
        exit 1
    fi
    sleep 2
done
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 8
if [[ "$batch" == control-01 ]]; then
    "${replay[@]}" capture "$dest" build
fi
if [[ "$batch" == *-01 ]]; then
    "${replay[@]}" capture "$dest"
    "${replay[@]}" capture "$dest/return" daylight
fi
"${replay[@]}" profile "$dest/runs"
"${game[@]}" stop --timeout 60
"${game[@]}" logs
