#!/usr/bin/env bash
# Generate review sheets. The full-resolution evidence is in each recording.
set -euo pipefail
root=$1
mkdir -p "$root/comparisons"
scenes=(daylight sunset night rain forest open-water cave)
for scene in "${scenes[@]}"; do
    magick montage -font DejaVu-Sans -pointsize 17 \
        -label 'Sodium, shaders off' "$root/sodium-01/runs/$scene/recording/before.png" \
        -label 'TASK-17 prototype' "$root/prototype-01/runs/$scene/recording/before.png" \
        -tile 2x1 -geometry 800x450+4+4 "$root/comparisons/$scene.jpg"
done
for frame in before after; do
    panels=()
    for batch in sodium-01 prototype-01 prototype-02 sodium-02; do
        for scene in "${scenes[@]}"; do
            panels+=(-label "$batch · $scene" "$root/$batch/runs/$scene/recording/$frame.png")
        done
    done
    magick montage -font DejaVu-Sans -pointsize 12 "${panels[@]}" \
        -tile 7x -geometry 240x135+3+3 "$root/comparisons/repeats-$frame.jpg"
done
magick montage -font DejaVu-Sans -pointsize 17 \
    -label 'R1  valley' artifacts/task-04/video-01/frame-001.png \
    -label 'R2  walkway' artifacts/task-04/video-06/frame-001.png \
    -label 'R3  mountain layers' artifacts/task-04/video-03/frame-009.png \
    -label 'R4  rain' artifacts/task-04/video-02/frame-010.png \
    -label 'R5  warm shoreline' artifacts/task-04/video-08/frame-008.png \
    -label 'R6  blue settlement' artifacts/task-04/video-09/frame-013.png \
    -label 'R7  shallow oasis' artifacts/task-04/video-07/frame-009.png \
    -label 'R8  snow village' artifacts/task-04/video-11/frame-004.png \
    -label 'R9  clear coast' artifacts/task-04/video-02/frame-001.png \
    -label 'R10  purple landscape' artifacts/task-04/video-10/frame-011.png \
    -tile 2x -geometry 490x276+4+4 "$root/reference-review.jpg"
