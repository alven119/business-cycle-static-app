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

## Product Doctrine Addendum

Future phase prompts should also require:

```text
Read docs/investment_cycle_product_doctrine.md and specs/common/investment_cycle_product_doctrine.yaml.
Treat the mature product as current_declared_cycle_phase + ordered cycle state machine + phase-specific transition monitor + evidence explanation + portfolio policy research template + historical replay/backtest.
Do not add standalone current phase classifier, phase rank/winner, role-count voting selector, arbitrary phase score, or isolated candidate phase classifier.
Report product_doctrine_alignment_status, cycle_state_machine_alignment_status, standalone_classifier_added_count, phase_rank_or_score_added_count, legal_transition_semantics_preserved, portfolio_policy_research_alignment, historical_replay_backtest_alignment, deviation_cleanup_needed_count, production_behavior_change_count, and semantic_drift_count.
Every phase must answer whether it advances transition detection, portfolio policy research, replay/backtest, dashboard education, or a documented cleanup/safety blocker.
```
