#!/usr/bin/env bash
# Run one fresh TASK-11 session from the repository root through the scoped toolkit.
set -euo pipefail
root=$1
batch=$2
case "$batch" in
    graded-01|graded-02|neutral-02|diagnostic) ;;
    *) exit 2 ;;
esac
variant=${batch%%-*}
dest="$root/$batch"

world_name_mask() {
    magick "$1" -crop 350x26+984+155 +repage -alpha off -separate \
        -evaluate-sequence Min -threshold 80% -depth 8 gray:- | sha256sum
}

# Check the title pixels of the first row against the previously inspected world list.
# Ignore its modification date and rotating panorama.
reference=$(world_name_mask "$root/neutral-01/world-list.png")
python3 evidence/task-11/configure.py --artifacts-dir "$root" "$variant"
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

if [[ "$variant" == diagnostic ]]; then
    python3 scripts/scenes.py capture daylight "$dest/ramp"
else
    python3 scripts/scenes.py profile "$dest/runs" daylight forest cave
    if [[ "$batch" == graded-01 ]]; then
        for scene in daylight forest sunset night cave; do
            python3 scripts/scenes.py capture "$scene" "$dest/$scene"
        done
        python3 evidence/task-11/snow.py "$dest/snow"
    fi
fi
python3 tools/minecraft.py stop --timeout 60
python3 tools/minecraft.py --artifacts-dir "$dest" logs
