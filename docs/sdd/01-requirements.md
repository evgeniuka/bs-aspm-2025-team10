# Requirements

## Functional Requirements

- Auth: trainer can log in with demo credentials and receives a JWT in an HttpOnly cookie.
- Auth: client can log in with demo credentials and receives only client-scoped data.
- Dashboard: trainer sees clients, programs, active session state, recent sessions, analytics, and session setup.
- Client management: trainer can create, edit, and archive active clients while preserving completed session history.
- Session setup: trainer selects one to ten clients from a roster larger than cockpit capacity.
- Client check-in: trainee can submit today's energy, sleep, soreness, pain/limitation notes, and training goal.
- Trainer readiness: dashboard surfaces today's client check-ins, missing submissions, and attention flags before session setup.
- Workout variants: demo data provides realistic program variants, such as strength, conditioning, and core/stability.
- Saved groups: trainer can create, edit, archive, and start recurring small-group sessions from saved rosters and exercise templates.
- Group session setup: trainer can choose a saved group, mark expected members present/absent, add substitutes from the roster, preview the group workout template, and override a client's program before starting.
- Program builder/editor: trainer can create and edit ordered exercises with sets, reps, weight, rest, and coach cues.
- Realtime cockpit: trainer can run stable one-to-ten client slots, log actual reps/weight, undo the last mistaken set, manage rest, and end the session.
- Session summary: ending a session opens a summary with planned vs completed work, actual logged reps/weight/volume, notes, and next focus.
- Client profile: trainer can inspect programs, workout history, summary notes, and volume/progress analytics.
- Client portal: trainee can inspect assigned programs, coach notes, next focus, workout history, and personal analytics.
- Analytics: trainer and client analytics are derived from real workout logs and handle empty or sparse history.
- Trainer analytics: trainer can inspect daily volume, weekly volume, focus mix, top exercises, readiness mix, client load, and attention flags.
- Client analytics: trainer and client can inspect completion rate, average/best volume, planned/completed sets, trend, and exercise breakdown.
- Mobile web: app provides a responsive web shell with mobile header and bottom navigation; the cockpit remains optimized for tablet/desktop visibility.
- Demo seed: safe public demo credentials and idempotent seed data are documented and repeatable.
- Program hygiene: per-session group template snapshots are hidden from normal program lists while remaining available through session history.

## Non-Functional Requirements

- The main trainer journey must be understandable within seconds in a demo.
- UI must not overlap, clip, or create horizontal overflow on common desktop and mobile widths.
- Loading, empty, disabled, and failure states must be explicit enough for manual testers.
- Frontend server-state should go through `frontend/src/lib/api.ts` and TanStack Query.
- Backend route behavior should be covered by pytest for ownership, validation, and core transitions.
- WebSocket state should remain deterministic in single-instance demo mode.
- Local setup should work from README instructions without hidden manual steps.
- A fresh reviewer should be able to run the app with `npm run setup:local` and `npm run start:local` without Docker.

## Security And Privacy Requirements

- Do not store JWTs in browser localStorage or sessionStorage.
- Authenticated HTTP routes must enforce trainer ownership for clients, programs, sessions, summaries, and analytics.
- Authenticated trainee routes must enforce `clients.user_id` ownership and never expose other clients in group sessions.
- WebSocket session joins must use equivalent auth/ownership checks before public deployment.
- Production environments must set a strong `SECRET_KEY`, exact HTTPS `FRONTEND_ORIGIN`, and `SECURE_COOKIES=true`.
- Demo data must not contain real personal data.
- CI or release checks should include dependency audit, secret scanning, and static security review before public launch.

## Operational Requirements

- Fast local setup uses SQLite through `npm run setup:local` and `npm run start:local`.
- Local Postgres remains available through `docker compose up -d db` and `npm run setup:local:postgres`.
- Backend migrations are managed by Alembic.
- Frontend deploy target is Vercel.
- Backend deploy target is Render Web Service.
- Production database target is Render Postgres or Supabase Postgres via `DATABASE_URL`.
- Active CI should at minimum run backend pytest, frontend lint/typecheck/unit/build.
- Proposed CI should add Playwright e2e, dependency audit, CodeQL, and secret scanning before public release.

## Acceptance Criteria

- Demo reviewer can log in, start or resume a live session, complete at least one set, end the session, view summary, save notes, and open a client profile.
- Demo reviewer can log in as the client and view only that client's hub, programs, history, and session summaries.
- Trainer can adjust actual reps/weight before completing a set, undo the last set for a client, then complete it again.
- Trainer can start a valid session with one to ten selected clients.
- Trainer can start a live session from a saved group after confirming attendance, adding substitutes if needed, and choosing whether each client uses the group template or an individual program override.
- Trainer can manage the active client roster without editing seed files or touching completed workout history.
- Client can submit today's check-in and trainer can see the readiness signal before choosing clients.
- Trainer can open analytics and see daily/weekly workload, focus distribution, top exercises, readiness, client load, and attention flags from workout logs.
- A fresh local setup can be completed from README commands without manually creating env files.
- Mobile web navigation works for dashboard, clients, groups, active session, analytics, client hub, and profiles without horizontal overflow.
- Program screen opens in a simple read-first mode and hides editing controls until `Edit plan`.
- Dashboard session setup feels like attendance and lineup selection, not a technical equalizer.
- Backend pytest passes.
- Frontend lint, typecheck, unit tests, build, and e2e pass.
- README and SDD describe any known production limitations honestly.
