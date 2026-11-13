#!/usr/bin/env bash
# Run from the repository root with scoped desktop access.
set -euo pipefail
root=$1
batch=$2
if [[ "$batch" == remaining ]]; then
    for next in sodium-01 sodium-02 control-02 weather-02; do
        bash "$0" "$root" "$next"
    done
    exit 0
fi
case "$batch" in
    weather-01|weather-02|weather-live|control-01|control-02|sodium-01|sodium-02) ;;
    *) exit 2 ;;
esac
mode=${batch%%-*}
dest="$root/$batch"
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
replay=(python3 evidence/task-21/replay.py)
reference="$root/world-list-reference.png"

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
"${game[@]}" screenshot "$dest/world-list.png"
if [[ ! -f "$reference" ]]; then
    echo 'Inspect the first row and retain its screenshot as world-list-reference.png.'
    exit 0
fi
expected=$(world_name_mask "$reference")
for attempt in {1..8}; do
    if [[ $(world_name_mask "$dest/world-list.png") == "$expected" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo 'Could not verify TASK-21 Weather Scenes in the first row' >&2
        exit 1
    fi
    sleep 2
    "${game[@]}" screenshot "$dest/world-list.png"
done
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 8
if [[ "$batch" == weather-live ]]; then
    "${replay[@]}" transitions "$dest/transitions"
else
    "${replay[@]}" profile "$dest/runs"
    if [[ "$batch" == weather-01 || "$batch" == control-01 ]]; then
        "${replay[@]}" capture "$dest"
    fi
fi
"${game[@]}" stop --timeout 60
"${game[@]}" logs
