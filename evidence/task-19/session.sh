#!/usr/bin/env bash
# Run from the repository root with scoped desktop access.
set -euo pipefail
root=$1
batch=$2
mode=${batch%%-*}
dest="$root/$batch"
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
replay=(python3 evidence/task-19/replay.py)
reference="$root/world-list-reference.png"

if [[ ${3:-} != open ]]; then
    test ! -e "$dest"
    "${replay[@]}" "$mode" "$root"
    if ! "${game[@]}" launch --timeout 90; then
        "${game[@]}" launch --timeout 150
    fi
    sleep 10
    "${game[@]}" screenshot "$dest/title.png"
    "${game[@]}" click 1280 535
fi
"${game[@]}" screenshot "$dest/world-list.png"
if [[ ! -f "$reference" ]]; then
    echo 'Inspect the first row and retain its screenshot as world-list-reference.png.'
    exit 0
fi

world_name_mask() {
    magick "$1" -crop 390x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}
if [[ $(world_name_mask "$dest/world-list.png") != "$(world_name_mask "$reference")" ]]; then
    echo 'Could not verify TASK-19 Water Scenes in the first row' >&2
    exit 1
fi
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 8
if [[ "$batch" == depth ]]; then
    "${replay[@]}" build "$root"
    "${replay[@]}" capture "$dest" basin shore underwater underside
elif [[ "$batch" == control-01 || "$batch" == water-01 ]]; then
    "${replay[@]}" capture "$dest" basin
    "${replay[@]}" profile "$dest/runs"
    "${replay[@]}" capture "$dest" basin-sunset underwater basin-rain underside open-water shore
else
    "${replay[@]}" profile "$dest/runs"
fi
"${game[@]}" stop --timeout 60
"${game[@]}" logs
