#!/usr/bin/env bash
set -euo pipefail
root=$1
mkdir -p "$root/review"
for scene in daylight forest open-water; do
    case "$scene" in
        daylight) crop=460x130+2050+375 ;;
        forest) crop=260x150+218+228 ;;
        open-water) crop=340x150+410+895 ;;
    esac
    rows=()
    for mode in sodium control spatial; do
        case "$mode" in
            sodium) label='Sodium, shaders off' ;;
            control) label='TASK-22 control' ;;
            spatial) label='Five-sample spatial trial' ;;
        esac
        native="$root/$mode-01/$scene/native.png"
        patch="$root/review/$scene-$mode.png"
        magick "$native" -crop "$crop" +repage -scale 300% "$patch"
        rows+=(-label "$label" "$patch")
    done
    magick montage -font DejaVu-Sans -pointsize 20 "${rows[@]}" -tile 1x3 -geometry +4+4 "$root/review/$scene-detail.png"
    for mode in control spatial sodium; do
        clip="$root/$mode-02/$scene/motion.mp4"
        if [[ "$mode" == sodium ]]; then clip="$root/sodium-motion/$scene/motion.mp4"; fi
        ffmpeg -hide_banner -loglevel error -y -i "$clip" -vf 'fps=2,scale=640:-1,tile=3x4' \
            -frames:v 1 "$root/review/$scene-$mode-motion.jpg"
    done
done

# Review an early moving interval at near-native scale. Left is control.
for scene in daylight forest open-water; do
    case "$scene" in
        daylight) crop=512:240:1630:330 ;;
        forest) crop=740:360:100:170 ;;
        open-water) crop=620:360:0:845 ;;
    esac
    ffmpeg -hide_banner -loglevel error -y \
        -ss 1.85 -i "$root/control-02/$scene/motion.mp4" \
        -ss 1.85 -i "$root/spatial-02/$scene/motion.mp4" \
        -filter_complex "[0:v]crop=$crop,fps=24,scale=640:-2[a];[1:v]crop=$crop,fps=24,scale=640:-2[b];[a][b]hstack" \
        -t 0.75 -c:v libx264 -crf 14 "$root/review/$scene-motion-detail.mp4"
done
