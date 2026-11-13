# TASK-28 evidence

The [regression report](../../docs/testing/regression_report.md) records
the tested runtime and prioritized bugs. Run the [exact commands](commands.txt)
from the repository root with GenshinShaderDev idle. The replay uses
the archived TASK-22 world at `artifacts/task-22/world/`, the installed
TASK-03 world as an integrity check, and the retained TASK-25 fog shader
tree and manifest. The session inherits the display, input and other
client settings listed in the handoff. It uses the scoped desktop
toolkit and the same per-user uinput access and KWin recorder as TASK-23.
[Environment](../../docs/minecraft-environment.md),
[Replay setup](../../docs/HANDOFF.md#repeat-the-runtime-checks),
[accepted pack manifest](../task-25/fog-pack.sha256).

Preparation refuses an existing artifact root, pack or disposable world.
Set `root` in the command file to a fresh directory under `artifacts/`
for a live repeat. Keep the existing `artifacts/task-28/` for offline review.
The client phase checks the first world-list row against the reviewed
world-name mask, then checks the copied world's session lock before
sending hotbar commands. If the menu check fails, inspect the saved
world-list image. After a failed capture, stop the client gracefully
and run the restore command before starting with a fresh artifact root.

| Evidence | Content |
| --- | --- |
| [Stills](../../artifacts/task-28/stills/) | Fourteen native PNGs covering the seven original presets, two additional interiors, three dimension views including the return, and two submerged views |
| [Clips](../../artifacts/task-28/clips/) | Six 1440p KWin recordings covering four outdoor motions, one up-and-down waterline clip and one cave entry clip |
| [Weather](../../artifacts/task-28/weather/) | Forty-two native PNGs and capture times for rain onset and clearing at fixed tick 6000 |
| [Visual review](../../artifacts/task-28/review/) | Contact sheets and close crops |
| [Runtime logs](../../artifacts/task-28/logs-20261113-194922/) | Client logs and instance manifest from the accepted run |
| [Verification](verification.txt) | Offline checks, logged positions, clip frame counts and restoration |
| [Fixture and inputs](replay.py) | Scoped world setup, presets, hotbar functions and transition replay |

Keep `artifacts/task-28/` with the handoff. It contains the captures,
archived copied world, shader snapshot, settings and source-world
manifests. The excluded menu trial sits in `menu-trial/`. Re-run the
saved evidence checks with
`python3 evidence/task-28/review.py artifacts/task-28` from the
repository root. It uses FFmpeg, FFprobe and ImageMagick on the saved
captures and reads the saved logs.
TASK-30 repeated the replay with the same shader source and reviewer.
[TASK-30 results](../task-30/verification.txt).
