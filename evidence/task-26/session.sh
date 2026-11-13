#!/usr/bin/env bash
# Run from the repository root with scoped desktop access.
set -euo pipefail
root=$1
shift
first=$1
dest="$root/$first"
game=(python3 tools/minecraft.py --artifacts-dir "$dest")
replay=(python3 evidence/task-26/replay.py)
telemetry() {
    nvidia-smi --query-gpu=name,driver_version,pstate,temperature.gpu,clocks.gr,clocks.mem,power.draw --format=csv > "$root/gpu-$1-$2.csv"
}
world_name_mask() {
    magick "$1" -crop 425x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}
close_and_log() {
    "${game[@]}" stop --timeout 60
    "${game[@]}" logs
}

for batch in "$@"; do
    test ! -e "$root/$batch"
done
"${replay[@]}" configure "$root" "${first%-*}"
telemetry "$first" start
"${game[@]}" launch --timeout 120
trap close_and_log EXIT
sleep 12
"${game[@]}" screenshot "$dest/title.png"
"${game[@]}" click 1280 535
expected=$(world_name_mask "$root/world-list-reference.png")
for attempt in {1..8}; do
    "${game[@]}" screenshot "$dest/world-list.png"
    if [[ $(world_name_mask "$dest/world-list.png") == "$expected" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo 'Could not verify TASK-25 Visual Comparison in the first row' >&2
        exit 1
    fi
    sleep 2
done
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 10

for batch in "$@"; do
    mode=${batch%-*}
    if [[ "$batch" != "$first" ]]; then
        "${replay[@]}" switch "$root" "$mode"
        telemetry "$batch" start
    fi
    "${replay[@]}" profile "$root/$batch/runs" "$mode"
    telemetry "$batch" end
done
