#!/usr/bin/env bash
# Open the verified TASK-03 world and collect one fresh session.
set -euo pipefail
root=$1
batch=$2
case "$batch" in
    sunlight-01|ambient-01|ambient-02|sunlight-02) ;;
    *) exit 2 ;;
esac
variant=${batch%%-*}
dest="$root/$batch"
test ! -e "$dest"

world_name_mask() {
    magick "$1" -crop 350x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}

reference=$(world_name_mask artifacts/task-12/sunlight-01/world-list.png)
python3 evidence/task-13/configure.py "$variant" "$root"
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

python3 scripts/scenes.py profile "$dest/runs" forest cave night
if [[ "$batch" == *-01 ]]; then
    for scene in daylight sunset forest cave night; do
        python3 scripts/scenes.py capture "$scene" "$dest/$scene"
    done
fi
python3 tools/minecraft.py stop --timeout 60
python3 tools/minecraft.py --artifacts-dir "$dest" logs
