# Project Profile

Generated: 2026-05-14

## Snapshot

- Project: FitCoach Pro 2.0
- Repository path: `C:\Users\Evgeniuka\Documents\Codex\2026-05-11\https-github-com-evgeniuka-bs-aspm`
- Stack: Next.js App Router, React 19, TypeScript, Tailwind, TanStack Query, Recharts, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL, pytest
- Package manager: npm
- Repository state: this local workspace does not currently expose a `.git` directory, so branch, tracked files, and dirty state must be verified in the real GitHub clone before publishing.

## Commands

- Backend setup: `cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
- Database: `docker compose up -d db`
- Migrations: `cd backend && alembic upgrade head`
- Seed: `cd backend && python -m app.seed`
- Backend dev: `cd backend && uvicorn app.main:app --reload --port 8000`
- Backend tests: `cd backend && .venv\Scripts\python.exe -m pytest`
- Frontend setup: `cd frontend && npm install`
- Frontend dev: `cd frontend && npm run dev`
- Frontend lint: `cd frontend && npm run lint`
- Frontend typecheck: `cd frontend && npm run typecheck`
- Frontend unit tests: `cd frontend && npm run test`
- Frontend build: `cd frontend && npm run build`
- Frontend e2e: `cd frontend && npm run e2e`

## Context Map

- SDD: `docs/sdd/`
- Architecture: `docs/architecture/`
- ADRs: `docs/architecture/adr/`
- Codex agents: `.codex/agents/`
- Proposed automation templates: `.codex/templates/`
- Existing product review agents: `docs/FITCOACH_AGENT_ROSTER.md`
- Existing active CI: `.github/workflows/ci.yml`
- Active quality gate: `docs/QUALITY_GATE.md`, `.github/pull_request_template.md`, and `scripts/quality-gate.ps1`

## Product Profile

- Audience: recruiters and engineering managers evaluating a full-stack portfolio project.
- Primary user: personal trainer running one-to-ten client live sessions.
- Signature workflow: login -> dashboard -> choose clients -> start live cockpit -> complete sets -> end session -> summary -> client profile.
- Current priority: make the trainer workflow simple, stable, and credible rather than adding AI or visual spectacle.

## Runtime Units

- Browser app: `frontend/`, deployed to Vercel in the intended production path.
- API app: `backend/`, deployed to Render in the intended production path.
- Database: PostgreSQL locally through Docker Compose and in production through Render Postgres or Supabase.
- Realtime: FastAPI WebSocket room manager, currently process-local for demo scope.

## Open Questions

- Who owns releases and production incidents?
- Which public branch policy will require the CI jobs before merging?
- Which environments exist and how are secrets managed?
- Which workflows should become Codex app local actions?
- Should active CI add Playwright e2e and security scanning now, or remain lighter until public deployment?
- Which production cookie/WebSocket topology will be used so the deployed cockpit receives the same HttpOnly auth cookie as HTTP routes?

## Initial Risk Register

- WebSocket room join uses cookie/JWT validation and trainer ownership checks; production still needs a same-site cookie/WS smoke test before public launch.
- `Base.metadata.create_all()` on app startup is convenient locally but should not replace Alembic discipline in production.
- `SECRET_KEY` has a development fallback; deployed environments must require a strong secret.
- Active CI runs backend, frontend, contract, and Playwright e2e checks. Dependency audit, secret scanning, CodeQL, and Scorecard remain proposal/template items until public deployment hardening.
- Local build/runtime artifacts such as `node_modules/`, `.next/`, `.venv/`, `__pycache__/`, test results, and local SQLite databases are covered by `.gitignore`; verify they are not tracked in GitHub.
- `.codex/` and `docs/` operating-system files are intended project artifacts, not ignored local scratch files.
