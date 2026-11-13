#!/usr/bin/env bash
# Capture one fresh session in the verified TASK-03 Visual Scenes world.
set -euo pipefail
root=$1
batch=$2
case "$batch" in
    ambient-01|sky-01|sky-02|ambient-02|sky-video) ;;
    *) exit 2 ;;
esac
variant=${batch%-0[12]}
dest="$root/$batch"
test ! -e "$dest"

world_name_mask() {
    magick "$1" -crop 350x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}

reference=$(world_name_mask artifacts/task-13/ambient-01/world-list.png)
python3 evidence/task-14/replay.py "$variant" "$root"
python3 tools/minecraft.py --artifacts-dir "$dest" launch --timeout 120
sleep 10
python3 tools/minecraft.py screenshot "$dest/title.png"
for attempt in {1..8}; do
    python3 tools/minecraft.py click 1280 535
    python3 tools/minecraft.py screenshot "$dest/world-list.png"
    if [[ $(world_name_mask "$dest/world-list.png") == "$reference" ]]; then
        break
    fi
    if [[ "$attempt" == 8 ]]; then
        echo "Could not verify TASK-03 Visual Scenes in the first row" >&2
        exit 1
    fi
done
python3 tools/minecraft.py click 1200 195
python3 tools/minecraft.py click 1050 1315
sleep 8

if [[ "$batch" == sky-video ]]; then
    for transition in dusk dawn; do
        python3 evidence/task-14/replay.py "$transition" "$dest/$transition"
        python3 evidence/task-14/review.py clean "$dest/$transition/transition.mp4"
    done
else
    python3 scripts/scenes.py profile "$dest/runs" daylight sunset
    if [[ "$batch" == *-01 ]]; then
        for scene in daylight night cave; do
            python3 scripts/scenes.py capture "$scene" "$dest/$scene"
        done
        python3 evidence/task-14/replay.py sweep "$dest/sweep"
    fi
fi
python3 tools/minecraft.py stop --timeout 60
python3 tools/minecraft.py --artifacts-dir "$dest" logs
