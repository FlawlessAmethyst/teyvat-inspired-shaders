#!/usr/bin/env bash
# Contact/cutout crops and matched TASK-25 fog views from native captures.
set -euo pipefail
root=$1
out="$root/comparisons"
mkdir -p "$out"
row() {
    magick montage -font DejaVu-Sans -pointsize 21 \
        -label 'TASK-25 control' "$1${4:-}" -label "$3" "$2${4:-}" \
        -thumbnail 960x540 -tile 2x1 -geometry +4+4 "$5"
}
for scene in contact sunset range; do
    row "$root/full-01/views/$scene/native.png" "$root/shadow-01/views/$scene/native.png" \
        '768 x 768 shadow map' '' "$out/shadow-$scene.jpg"
done
for scene in valley grove rain; do
    for trial in shadow fog; do
        row "$root/full-01/runs/$scene/recording/before.png" \
            "$root/$trial-01/runs/$scene/recording/before.png" "$trial trial" '' \
            "$out/$trial-$scene.jpg"
    done
done
for scene in dusk ridges; do
    row "$root/full-01/views/$scene/native.png" "$root/fog-01/views/$scene/native.png" \
        'Fog arithmetic trial' '' "$out/fog-$scene.jpg"
done
row "$root/full-01/views/sunset/native.png" "$root/shadow-01/views/sunset/native.png" \
    '768 x 768 shadow map' '[1400x460+380+580]' "$out/shadow-cutouts.jpg"
row "$root/full-01/views/contact/native.png" "$root/shadow-01/views/contact/native.png" \
    '768 x 768 shadow map' '[1000x250+790+505]' "$out/shadow-contact-detail.jpg"
row "$root/full-01/views/range/native.png" "$root/shadow-01/views/range/native.png" \
    '768 x 768 shadow map' '[510x205+1220+585]' "$out/shadow-fade.jpg"
