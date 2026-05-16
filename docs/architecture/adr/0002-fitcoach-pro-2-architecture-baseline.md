# ADR 0002: FitCoach Pro 2.0 Architecture Baseline

## Status

Accepted

## Context

FitCoach Pro 2.0 is being shaped as a full-stack portfolio project. The app needs to show credible frontend, backend, database, realtime, testing, and deployment skills while staying small enough to run as a public demo.

## Decision

Use a split full-stack architecture:

- `frontend/`: Next.js App Router, React, TypeScript, Tailwind, TanStack Query, Recharts.
- `backend/`: FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, pytest.
- Database: PostgreSQL-first relational model.
- Auth: backend-issued JWT in an HttpOnly cookie.
- Realtime: FastAPI WebSocket endpoint with full-session state broadcasts.
- Demo scope: process-local in-memory WebSocket rooms.
- Deployment target: Vercel frontend, Render backend, Render Postgres or Supabase Postgres.

## Rationale

- The split app shows clear full-stack boundaries and deploys naturally to common portfolio-friendly platforms.
- PostgreSQL fits the relationship-heavy domain: trainers, clients, programs, sessions, summaries, and workout logs.
- HttpOnly cookie auth avoids browser token storage and keeps auth centralized in the backend.
- Full-session WebSocket broadcasts simplify cockpit reconciliation and make the demo more reliable.
- In-memory realtime avoids unnecessary infrastructure before the project needs multi-instance scaling.

## Consequences

- Frontend TypeScript types must stay aligned with backend Pydantic schemas.
- Public deployment must prove cookie/WebSocket host topology; WebSocket auth and trainer ownership are enforced in the app.
- Multi-instance backend deployment requires Redis, Postgres pub/sub, or another fanout layer.
- Production schema management should rely on Alembic, not startup table creation.
- CI should eventually include Playwright e2e, security scans, and deployment smoke checks.

## Related Docs

- `docs/sdd/00-context.md`
- `docs/sdd/02-system-design.md`
- `docs/architecture/system-map.md`
- `.codex/project-profile.md`
