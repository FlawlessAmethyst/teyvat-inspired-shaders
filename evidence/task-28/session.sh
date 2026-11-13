#!/usr/bin/env bash
# Run from the repository root with scoped desktop access.
set -euo pipefail
root=$1
game=(python3 tools/minecraft.py --artifacts-dir "$root")
replay=(python3 evidence/task-28/replay.py)
instance=$("${game[@]}" paths | python3 -c 'import json, sys; print(json.load(sys.stdin)["minecraft"])')
crashes() {
    if [[ -d "$instance/crash-reports" ]]; then
        find "$instance/crash-reports" -maxdepth 1 -type f -printf '%f\n' | LC_ALL=C sort
    fi
}
close_and_log() {
    "${game[@]}" stop --timeout 60
    "${game[@]}" logs
    crashes > "$root/crashes-after.txt"
    cmp "$root/crashes-before.txt" "$root/crashes-after.txt"
}

test ! -e "$root/stills"
test -x "$root/motion-input"
crashes > "$root/crashes-before.txt"
"${game[@]}" launch --timeout 120
trap close_and_log EXIT
sleep 12
"${game[@]}" screenshot "$root/title.png"
"${game[@]}" click 1280 535
for attempt in {1..8}; do
    "${game[@]}" screenshot "$root/world-list.png"
    world_name=$(magick "$root/world-list.png" -crop 425x26+984+155 +repage -alpha off \
        -separate -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum)
    if [[ ${world_name%% *} == "$(cat evidence/task-28/world-name.sha256)" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo 'Could not verify TASK-28 Runtime Regression in the first row' >&2
        exit 1
    fi
    sleep 2
done
"${game[@]}" click 1200 195
"${game[@]}" click 1050 1315
sleep 10
"${replay[@]}" run "$root"
