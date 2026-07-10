# Phase 109 Tailscale Private HTTPS Acceptance

Phase 109 hardens the deployed private NAS login surface and records the exact
gap between a healthy LAN deployment and accepted mobile access over Tailscale.

## Product progress

- The app and Postgres containers are healthy on the DS925+.
- Browser login is live and the dashboard shell is prebuilt at container start.
- HTTPS-aware secure cookies, login failure limiting, request size limiting,
  HSTS gating, CSP, frame blocking, referrer policy, and MIME-sniffing protection
  are implemented in the private runtime.
- The NAS Tailscale node is online, but Tailscale Serve is not enabled on the
  tailnet and the deployment account does not have root/operator permission.
- No Tailscale Funnel or public router forwarding is permitted.

## Acceptance blocker

The operator must enable Tailscale Serve in the tailnet, grant the deployment
account Tailscale operator permission or run the command as root, switch the app
publish address back to loopback, enable secure cookies, and complete a phone
test over cellular data with Wi-Fi disabled. Phase 110 must not start until this
private HTTPS acceptance report passes.

## Data reality

The running Postgres container currently has zero business tables. The deployed
dashboard therefore remains a bundled research snapshot rather than a live DB
view. Product progress percentages remain unchanged in this checkpoint; a
formal production-readiness rebaseline is required after private HTTPS and live
DB acceptance so the table does not confuse contract coverage with operational
readiness.

## Doctrine boundary

This phase changes only the private service security boundary. It does not infer
the current phase, emit a candidate phase, change transition rules, run a
backtest, start prospective monitoring, or create portfolio instructions.
