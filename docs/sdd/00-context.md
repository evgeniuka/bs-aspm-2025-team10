# Context

## Goal

FitCoach Pro 2.0 should read as a credible full-stack portfolio product, not a toy CRUD app. It helps a trainer manage a small live session with one to ten clients while keeping each client's program, progress, rest state, summary, and history separate.

The project goal is to demonstrate professional engineering judgment across frontend UX, backend domain modeling, realtime behavior, testing, deployment readiness, and documentation.

## Users And Stakeholders

- Primary user: personal trainer or small studio coach running semi-private sessions.
- Demo reviewer: recruiter, engineering manager, or peer reviewer opening the public demo.
- Maintainer: the portfolio owner iterating with Codex agents and local checks.
- Secondary user: trainee/client portal user who submits readiness and reviews assigned programs, notes, and history.

## Constraints

- Keep `frontend/` and `backend/` as separate top-level apps.
- Frontend uses Next.js App Router, TypeScript, Tailwind, TanStack Query, and Recharts.
- Backend uses FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL, pytest, JWT HttpOnly cookie auth, and FastAPI WebSockets.
- Demo must be easy to run locally and safe to expose publicly with documented demo credentials.
- UI should feel like operational SaaS: compact, clear, trainer-first, no marketing landing page as the app entry.
- Avoid AI features in v1. Any future AI assistant must be opt-in, constrained, validated, and explainable.
- Current realtime manager is single-process and in-memory for demo scope.

## Non-Goals

- Full gym/studio billing, subscriptions, payroll, or scheduling platform.
- Public marketplace, social feed, or trainee mobile app.
- AI-generated programs in v1.
- Multi-instance WebSocket scaling until public deployment pressure justifies Redis or pub/sub.
- Replacing all hand-written TypeScript types with generated OpenAPI clients in the immediate iteration.

## Glossary

- Trainer: authenticated coach who owns clients, programs, and sessions.
- Client: person being trained by the trainer.
- Program: ordered workout plan containing exercises, sets, reps, weight, and rest.
- Training group: reusable trainer-owned roster plus workout template for recurring small-group sessions.
- Session: live training event with one to ten selected clients.
- Cockpit: responsive realtime live session interface for one to ten selected clients.
- Summary: post-session view with completed work, volume, notes, and next focus.
- SDD: spec-driven development docs in `docs/sdd/`.
- ADR: architecture decision record in `docs/architecture/adr/`.

## Open Questions

- What is the exact public deployment path: Render Postgres, Supabase Postgres, or another managed database?
- Which same-site or ticket-based WebSocket cookie topology should be used for the first public deployment?
- Which CI additions should become active now versus stay as `.codex/templates/` proposals?
- What screenshots or GIFs should be added to the README after deployment?
