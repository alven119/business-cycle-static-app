# Prompt Templates

## Autonomous Phase Prompt Suffix

Use this suffix for future phase prompts when the task should be completed autonomously:

```text
Autonomous completion policy:

* Do not stop after first implementation.
* Run all required validation commands.
* Parse relevant JSON outputs.
* Compare against hard gates listed in this prompt and specs/backtests/phase_acceptance_gates.yaml.
* If hard gates fail, inspect root cause, fix, and rerun.
* Repeat until all hard gates pass or a real blocker is reached.
* Do not report intermediate failed attempts unless blocked.
* Final report must include:

  * pytest result
  * ruff result
  * domain command stdout
  * hard gate status
  * soft warnings
  * files changed
  * git diff --stat
  * git status --ignored

Blocked report must include:

* failing gate
* root cause hypothesis
* attempted fixes
* why further repair is unsafe
```

This suffix does not authorize changes to formal scoring, resolver logic, FRED provider behavior, dashboard integration, GitHub Pages workflow, generated data, public output, secrets, or investment advice unless the main prompt explicitly requests them.

## North Star Phase Addendum

Future phase prompts should require:

```text
Read docs/project_north_star.md and specs/common/project_north_star_contract.yaml.
Map the phase to product_capabilities_advanced, milestone_ids_advanced, and web_surfaces_advanced.
Report north_star_alignment_status, deferred_capability_gaps, semantic_drift_count, and production_behavior_change_count.
Do not mark the phase complete when semantic_drift_count > 0.
Preserve: observation != phase evidence, watch != confirmation, candidate phase != current phase, revised diagnostic != point-in-time result, structural readiness != economic validation, and portfolio research != investment recommendation.
```
