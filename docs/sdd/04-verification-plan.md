# Verification Plan

## Local Checks

Fresh local setup smoke:

```powershell
npm run setup:local
npm run start:local
```

Repository-level quality gate:

```powershell
npm run quality:fast
npm run quality
```

`npm run quality` resets demo data before e2e. Use `npm run quality:fast` when you only need backend, lint, typecheck, unit tests, and build.

Backend:

```powershell
cd backend
python -m app.seed --reset-demo
.venv\Scripts\python.exe -m pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run typecheck
npm run test
npm run build
npm run e2e
```

Optional dependency checks before public release:

```powershell
cd frontend
npm audit --audit-level=moderate
```

```powershell
cd backend
python -m pip install pip-audit bandit
pip-audit -r requirements.txt
bandit -r app
```

## CI Checks

- Active CI: `.github/workflows/ci.yml` runs the project contract check, backend migrations/tests, frontend lint/typecheck/unit/build, and Playwright e2e against a real backend and Postgres service.
- Quality gate contract: `docs/QUALITY_GATE.md`.
- Active PR evidence checklist: `.github/pull_request_template.md`.
- Proposed CI template: `.codex/templates/github-ci.yml` remains as a fuller reference including basic security checks.
- Proposed dependency automation: `.codex/templates/dependabot.yml`.
- Proposed supply-chain signal: `.codex/templates/scorecard.yml`.
- Proposed CodeQL analysis: `.codex/templates/codeql.yml`.
- Proposed secret scanning: `.codex/templates/secret-scan.yml`.

## Manual QA

Inspect these routes on desktop and mobile:

- `/login`
- `/dashboard`
- `/analytics`
- `/client`
- `/programs/{programId}`
- `/sessions/{sessionId}`
- `/sessions/{sessionId}/summary`
- `/clients/{clientId}`

Manual journey:

1. Log in with demo trainer credentials.
2. Log in with demo client credentials and submit today's check-in.
3. Return to trainer login and verify the readiness inbox shows the client signal.
4. Prepare a saved group from the rail or session setup, confirm attendance, add/remove a substitute, preview the group template, and start the group.
5. Open Clients, create a client, edit their profile, and archive them.
6. Return to dashboard and also verify manual selection works for one to ten clients from the roster.
7. Start a session and verify cockpit slots plus the `live` realtime connection state.
8. Complete a set and observe rest/progress changes.
9. Adjust actual reps/weight, undo the last set, then complete it again.
10. End session and land on summary.
11. Verify summary volume comes from actual logged reps/weight.
12. Save coach notes and next focus.
13. Open a client profile and verify history/analytics.
14. Open Analytics and verify daily/weekly volume, focus mix, top exercises, readiness, client load, and attention flags.
15. On a mobile-width viewport, verify the top bar, bottom navigation, dashboard, analytics, client profile, and cockpit fallback layout do not horizontally overflow.

## Observability

- Current app has health check at `GET /health`.
- Browser console should be clear of runtime errors during demo flows.
- Playwright traces and screenshots should be uploaded only on e2e failure when active CI adds e2e.
- Public deployment should add Render/Vercel logs to the release checklist.

## Release Gates

- README setup and demo credentials verified.
- Fast local setup verified with SQLite or explicitly skipped with reason.
- Backend pytest green.
- OpenAPI contract guard covers frontend-critical fields for programs, workout logs, sessions, and summaries.
- OpenAPI contract guard covers client check-in/readiness fields used by the frontend.
- Frontend lint, typecheck, unit tests, build, and e2e green.
- `.github/workflows/ci.yml` green for contract, backend, frontend, and e2e jobs.
- PR template completed with agent review, docs impact, verification, risk, and screenshots/evidence.
- No known P0 ownership/auth gaps for public deployment.
- Production env vars verified: `DATABASE_URL`, `ENVIRONMENT=production`, `SECRET_KEY`, `FRONTEND_ORIGIN`, `SECURE_COOKIES=true`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`.
- Alembic migrations run against the target database.
- Seed command safe and idempotent.
- Demo reset command removes local mutations and recreates curated check-ins/history before screenshots or public demos.
- Smoke test passes after deploy: health, login, dashboard, session start, WebSocket connection, summary.
