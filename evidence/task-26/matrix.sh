#!/usr/bin/env bash
# Use scoped desktop access for each round. Never run the rounds concurrently.
set -euo pipefail
root=$1
round=$2
case "$round" in
    01)
        bash evidence/task-26/session.sh "$root" sodium-01
        bash evidence/task-26/session.sh "$root" full-01 shadowless-01 cloudless-01 fogless-01 \
            water-depthless-01 water-vanilla-01 gradeless-01 terrain-vanilla-01 rain-neutral-01
        ;;
    02)
        bash evidence/task-26/session.sh "$root" rain-neutral-02 terrain-vanilla-02 gradeless-02 \
            water-vanilla-02 water-depthless-02 fogless-02 cloudless-02 shadowless-02 full-02
        bash evidence/task-26/session.sh "$root" sodium-02
        ;;
    *) exit 2 ;;
esac
