# Prospective Manual Start Runbook

This runbook is for the future manual append flow after the canonical first
eligible as-of has arrived and all required releases have been verified. QA12
does not execute the append.

## Required Checks

1. Verify freeze lineage: alpha5 observation freeze, monitoring v1, and
   `prospective_shadow_manual_start_v1`.
2. Verify the current UTC date is not before `2026-08-31`.
3. Verify the canonical period manifest for `2026-07`.
4. Run the no-write official source preflight.
5. Capture raw artifacts and input snapshots only after the manual command is
   explicitly requested.
6. Verify checksums, release dates, data mode, and source identity.
7. Build input snapshots and observation records.
8. Execute observation-only evaluators.
9. Build the preview bundle and inspect blockers.
10. Verify period completeness for required core roles.
11. Verify candidate capability remains disabled.
12. Request registry append explicitly.
13. Validate idempotency before append.
14. Append records without overwrite.
15. Validate the registry hash chain.
16. Produce a non-public operational summary.
17. Preserve source corrections as new records.

## Stop Conditions

Stop before append if the UTC date is too early, a required release is late, a
source schema changes, provenance is incomplete, checksums mismatch, a core
role is missing, or any candidate/current phase field appears in the preview.

## Failure Recovery

Network failure, delayed release, correction notices, partial capture, and
evaluator abstention are handled by waiting, retrying the no-write checks, or
appending a later correction record after the explicit manual flow is allowed.
Existing records are never deleted, overwritten, compacted, or rewritten.

## Prohibited Actions

Do not use preview files as registry records. Do not shorten major-group
requirements because a role is blocked. Do not substitute supporting or modern
extension roles for missing core roles. Do not add schedules, backfill prior
periods, inspect sealed evidence for tuning, or enable candidate monitoring.
