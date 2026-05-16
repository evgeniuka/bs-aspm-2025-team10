# System Design

## Overview

FitCoach Pro 2.0 is a two-app system: a Next.js frontend and a FastAPI backend sharing a relational domain model. The browser communicates with the API over REST for normal workflows and WebSocket for live session updates.

The domain model is intentionally relational: trainers own clients, clients have programs, sessions attach clients to selected programs, and workout logs power summaries and analytics.

## Architecture

- Frontend: `frontend/` owns routes, UI, query caching, forms, realtime rendering, and client-side error states.
- Backend: `backend/` owns auth, role/ownership checks, validation, persistence, domain transitions, serialization, and realtime broadcast.
- Database: PostgreSQL is the production target. Tests and the fast local setup can use SQLite where configured.
- Realtime: `backend/app/realtime.py` keeps process-local WebSocket rooms for demo scope.
- Deployment: Vercel frontend plus Render backend and managed Postgres.

## Interfaces And Contracts

- REST base path: `/api/v1`.
- WebSocket path: `/api/v1/sessions/ws/{session_id}`.
- Auth cookie: `fitcoach_token`, HttpOnly, SameSite lax, secure in production.
- Frontend API boundary: `frontend/src/lib/api.ts` and `frontend/src/lib/http.ts`.
- Backend schema boundary: `backend/app/schemas.py`.
- Backend serializers: `backend/app/serializers.py` aggregates ORM objects into API read models.
- Analytics boundary: `backend/app/routers/analytics.py` derives trainer aggregates directly from workout logs, check-ins, sessions, and program prescriptions.
- Local startup boundary: `scripts/setup-local.ps1` prepares dependencies/env/migrations/seed; `scripts/start-local.ps1` runs backend and frontend with background logs.
- Program update contract: program exercises are replaced from the submitted ordered list.
- Training group contract: saved groups store trainer-owned member order plus an exercise template; starting a group session can use the full group, a confirmed attendance subset, roster substitutes, and per-client program overrides.
- Group template contract: clients without a program override receive a per-session snapshot copied from the saved group template so the live cockpit still works with normal per-client programs.
- Session creation contract: accepts one to ten unique clients with matching program ids.
- Set logging contract: `complete-set` accepts optional actual reps/weight plus expected exercise/set; stale expected state returns `409`.
- Undo contract: `undo-last-set` removes only the latest completed set for that client while the session is active.

## Data Model

- `users`: trainer and future trainee identities.
- `clients`: trainer-owned client profiles.
- `exercises`: seeded exercise library.
- `programs`: client-owned workout plans.
- `programs.is_session_snapshot`: distinguishes reusable trainer-created programs from immutable per-session snapshots generated from group templates.
- `program_exercises`: ordered exercise prescription rows.
- `training_groups`: reusable trainer-owned small-group templates.
- `training_group_members`: ordered client membership for a saved group.
- `training_group_exercises`: ordered reusable exercise prescription rows for a saved group.
- `sessions`: live or completed training event.
- `session_clients`: per-client live progress, notes, next focus, and status.
- `workout_logs`: completed set records used for summaries and analytics.

## Analytics Read Models

- Trainer analytics combine actual workout logs with planned sets, session focus, check-in readiness, and last workout dates.
- Client analytics are serialized from session client history and workout logs, including volume trend, completion rate, average/best session volume, and exercise breakdown.
- Analytics must show useful empty or single-day states rather than implying false trends.

## Failure Modes

- API offline: frontend should surface retryable errors and avoid infinite loading.
- Existing active session: backend currently returns the existing active session instead of creating another.
- WebSocket disconnect: cockpit should still rely on HTTP mutations and latest cached session state.
- Stale cockpit action: backend rejects stale expected exercise/set with `409` and frontend refreshes session state.
- Mistaken set completion: trainer can undo only the latest set for that client before ending the session.
- Empty history: analytics views should show a useful empty state rather than misleading charts.
- Missing local setup: README should point users to `npm run setup:local`; scripts create missing env files without overwriting existing ones.
- Invalid ownership: backend returns not found/forbidden semantics rather than leaking another trainer's data.
- Production config missing: deploy should fail or be blocked if strong secrets and secure cookie settings are missing.

## Migration And Rollback

- Schema changes require Alembic migrations under `backend/alembic/versions/`.
- Demo data changes should remain idempotent through `python -m app.seed`.
- Frontend UI changes should preserve route compatibility for `/dashboard`, `/programs/{id}`, `/sessions/{id}`, `/sessions/{id}/summary`, and `/clients/{id}`.
- For risky workflow changes, keep old route-level behavior working until e2e covers the new path.
- Production rollback should include app rollback plus database migration rollback notes when schema changes are involved.
- Fast local setup defaults to SQLite for reviewer convenience; production deployment remains Postgres-only through `DATABASE_URL`.
