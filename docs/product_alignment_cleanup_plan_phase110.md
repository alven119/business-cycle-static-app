---
phase_id: 110
phase_label: nas_postgres_live_revised_history_import
status: completed_live_revised_import
---

# Phase 110 NAS Postgres Live Revised History Import

Phase 110 moves the private NAS data warehouse from rehearsal to an
operator-authorized live revised-data foundation. It applies the existing
PIT-ready schema, fetches full revised history for 26 governed FRED series,
stores checksummed source CSV artifacts outside the repository, and upserts one
series per transaction with an atomic resume checkpoint.

Revised observations remain explicitly separate from vintage/PIT data. This
phase does not derive a current phase, select a candidate phase, calculate a
phase rank, execute a backtest, or produce portfolio instructions.

## Live sequence

1. Preserve an empty-database baseline backup outside the repository.
2. Build the Phase 110 NAS image with the PostgreSQL client.
3. Apply the idempotent `macro` schema migration.
4. Fetch and import 26 official revised source series.
5. Preserve raw CSV checksums, per-series transactions, and checkpoint state in
   the NAS source-artifact volume.
6. Verify schema, series, artifact, observation, and latest-date counts through
   read-only SQL.

The four composite or turning-point roles remain deferred to server-side
snapshot materialization. Their input series are imported, but the role names
are not stored as fake official source series.

Phase 109 private HTTPS was accepted after this import: Tailscale Serve is
private-only, Funnel is off, the app port is loopback-only, Secure Cookie is
enabled, and phone access over cellular data passed. The remaining service gap
is the dashboard live Postgres read path.
