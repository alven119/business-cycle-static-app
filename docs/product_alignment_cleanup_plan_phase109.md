# Phase 109 Tailscale Private HTTPS Acceptance

Phase 109 hardens and accepts the deployed private NAS login surface over
Tailscale private HTTPS.

## Product progress

- The app and Postgres containers are healthy on the DS925+.
- Browser login is live and the dashboard shell is prebuilt at container start.
- HTTPS-aware secure cookies, login failure limiting, request size limiting,
  HSTS gating, CSP, frame blocking, referrer policy, and MIME-sniffing protection
  are implemented in the private runtime.
- Tailscale Serve proxies the loopback-only app endpoint over tailnet HTTPS.
- HTTPS health, readiness, login, logout, Secure Cookie, and phone cellular
  access have passed operator acceptance.
- No Tailscale Funnel or public router forwarding is permitted.

## Acceptance result

The deployment account has Tailscale operator permission, Funnel remains off,
the app is published only on loopback, and the user confirmed the private HTTPS
dashboard on a phone over cellular data with Wi-Fi disabled. No tailnet identity
or secret is committed.

## Data reality

Phase 110 subsequently migrated the 11-table macro schema and imported 22,131
revised observations. The deployed dashboard still renders a bundled research
snapshot rather than reading Postgres, so live DB dashboard wiring remains the
single production-readiness rebaseline gap.

## Doctrine boundary

This phase changes only the private service security boundary. It does not infer
the current phase, emit a candidate phase, change transition rules, run a
backtest, start prospective monitoring, or create portfolio instructions.
