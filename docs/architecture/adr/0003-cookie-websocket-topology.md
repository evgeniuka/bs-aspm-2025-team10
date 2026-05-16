# ADR 0003: Cookie And WebSocket Topology

## Status

Accepted for local demo, pending production smoke test

## Context

FitCoach Pro uses an HttpOnly cookie for trainer auth and a WebSocket room for the live cockpit. Browser cookies are host-scoped, so a frontend opened on `localhost` will not send the same cookie to a WebSocket URL hardcoded to `127.0.0.1`, even though both point to the same machine.

## Decision

- The frontend WebSocket client derives the loopback host from the current browser location when `NEXT_PUBLIC_WS_URL` points at `localhost`, `127.0.0.1`, or `::1`.
- The backend WebSocket endpoint validates the auth cookie, trainer role, session ownership, and allowed browser `Origin`.
- Production must use a same-site HTTP/WebSocket topology or a separately designed one-time WebSocket ticket flow before public launch.

## Consequences

- Local demos work whether the reviewer opens `http://localhost:3000` or `http://127.0.0.1:3000`.
- E2E must assert that the cockpit reaches the `live` connection state, not only that HTTP mutations work.
- Vercel-to-Render direct WebSocket auth is not assumed safe until deployed cookie scope is proven.

## Related Docs

- `docs/sdd/03-implementation-plan.md`
- `docs/sdd/04-verification-plan.md`
- `docs/sdd/05-risk-register.md`
- `docs/architecture/system-map.md`
