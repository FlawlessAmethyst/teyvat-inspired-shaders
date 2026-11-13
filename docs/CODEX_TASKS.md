# Task entry point

The authoritative numbered plan is the local `task_decomposed.md`.
This entry point deliberately links to it instead of duplicating task definitions.
New explicit user instructions take precedence; [scope overrides](SCOPE_OVERRIDES.md)
resolve the historical brief and baseline recommendations.

Start each session with [STATUS.md](STATUS.md), the requested task in the plan,
and only its listed inputs. Consult [DECISIONS.md](DECISIONS.md) and
[TEST_LOG.md](TEST_LOG.md) as needed. Execute only the requested numbered task;
record evidence, limitations and resume instructions, then stop.

The TASK-00 environment handoff is [minecraft-environment.md](minecraft-environment.md).
This is the actual environment document; the plan's `docs/ENVIRONMENT.md`
reference refers here. Reuse [tools/minecraft.py](../tools/minecraft.py).

See [STATUS.md](STATUS.md) for completed work and the
[final developer handoff](HANDOFF.md).
The [TASK-29 notes](testing/compatibility_notes.md) document the tested
client and version differences that matter for the pack.
The [TASK-28 report](testing/regression_report.md) records runtime coverage
and open bugs for the retained pack.
The [TASK-27 report](testing/optimization.md) records the two measured
trials and the retained pack.
The [TASK-26 report](testing/effect_costs.md) records the profiling control
and measured costs. The [TASK-25 comparison](testing/visual_comparison.md)
records the visual gaps and matched views.
