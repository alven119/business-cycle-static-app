# Phase 70 Product Alignment Cleanup Plan

status: declared_phase_start_registry_update_preview
closure: specs/audits/phase70_declared_phase_start_registry_preview_closure.yaml

## What Changed

Phase 70 adds a research-only dry-run preview for future declared boom start
registry updates. The preview supports:

- exact user-supplied declared phase start date
- user-supplied bounded start window
- missing-input wait state
- dry-run phase-age calculation for exact dates only
- age-range display for bounded windows
- `/tmp` output when explicitly requested

The declared registry is not modified.

## Doctrine Boundaries

- No standalone current phase classifier was added.
- No phase score, rank, winner, or role-count vote was added.
- No candidate/current phase output was emitted.
- Current macro data is not used to infer the declared phase.
- Bounded windows never create exact phase-age precision.
- Registry writes require a later explicit gate and user-confirmed input.

## Remaining Gap

The next product gap is a user-confirmed declared boom start date or bounded
window. A later phase may update the declared registry only through an explicit
write gate that preserves provenance, legal transition semantics, and no false
phase-age precision.
