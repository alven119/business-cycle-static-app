# Phase 134-136 Source Reliability And Resilience Roadmap

## Purpose

This roadmap records the active dependency order for source correctness and
operations work through Phase 136. It advances the private NAS research
service without changing the declared cycle state, selecting a candidate
phase, or turning supporting sources into silent book-core substitutes.

## Phase 134: Release-Aware Freshness And Source Identity Remediation

- Judge freshness from the end of the source reference period and the latest
  registered official release, rather than from an observation-period start
  date alone.
- Preserve the raw observation date and expose the freshness basis and reason.
- Correct `AAA` and `BAA` to monthly frequency for the selected FRED series.
- Use BEA `PNFIC1` for the recovery and growth private nonresidential fixed
  investment roles; keep `FPIC1` for the broader private fixed investment role.
- Normalize the real disposable-income/consumption relation to monthly
  `DSPIC96` and `PCEC96` inputs.
- Add FRED-distributed `ADPMNUSNERSA` for the ADP private-employment role with
  visible private-source, citation, annual rebenchmarking, and revised-only
  caveats. `PAYEMS` remains a separate BLS role and is never an ADP substitute.
- Keep consumer confidence unresolved as an exact Conference Board book-core
  source pending Phase 136.

## Phase 135: Source Health Incident Center And Governed Fallbacks

- Add persistent, operator-readable source incidents for fetch failures,
  schema drift, identity/unit/frequency changes, discontinued series,
  authentication/rate limits, parser/checksum failures, and a release that is
  due while the local series remains stale.
- Show affected roles and cycle lanes, last good observation, expected release,
  attempts, fallback status, next action, and recovery receipt.
- Permit only pre-reviewed fallback states. A fallback may be supporting-only
  and must never silently replace a required book-core source.

## Phase 136: Consumer Confidence Resolution And Failure Drills

- Preserve the exact Conference Board Consumer Confidence Index as an
  access-limited book-core concept unless authorized data is supplied.
- Add an OECD directional/turning-point lane as a near-equivalent transformed
  source, University of Michigan sentiment as an independent proxy, and New
  York Fed Survey of Consumer Expectations components as explanatory context.
- Keep all three alternatives visibly separated and do not create an arbitrary
  composite score.
- Run deterministic source-failure and recovery drills covering exact,
  near-equivalent, proxy, and unavailable states.

## Dependency And Safety Rules

1. Phase 135 depends on the corrected Phase 134 source identity and freshness
   fields.
2. Phase 136 depends on the Phase 135 incident and fallback-state model.
3. Revised data never becomes a point-in-time result by relabeling.
4. Source readiness never becomes phase evidence without its evaluator rule.
5. No phase in this roadmap may emit a candidate/current phase, modify the
   declared state, or produce personalized portfolio/trade instructions.
6. No runtime dependency on MacroMicro or another paid data portal is allowed;
   such sites may be used only as semantic/UX cross-checks.
