# FitCoach Quality Gate

This document turns the project agent rules into a repeatable gate for local work, pull requests, and CI.

## Gate Levels

| Level | When to run | Required checks |
| --- | --- | --- |
| Fast local gate | Small non-UI changes | Backend pytest, frontend lint, typecheck, unit tests, build |
| Full local gate | Product, API, session, auth, or UI changes | Fast gate plus Playwright e2e and relevant browser/manual QA |
| Pull request gate | Before review or merge | CI green, PR template completed, SDD/ADR/risk docs current |
| Release gate | Before public demo/deploy | Full gate plus demo seed reset, screenshots/GIF, env var review, smoke test |

## Local Commands

Fast gate:

```powershell
npm run quality:fast
```

Full gate:

```powershell
npm run quality
```

The full gate resets demo data before e2e so tests do not depend on manual app state. Optional clean demo reset before screenshots or portfolio walkthroughs:

Before running Playwright, the local gate also stops stale local servers on `3000` and `8000`, then starts a fresh FastAPI backend from the current workspace so e2e does not test a new frontend against an old API process.

```powershell
.\scripts\quality-gate.ps1 -ResetDemo
```

## CI Contract

Active CI in `.github/workflows/ci.yml` must stay aligned with this document:

- `contract`: required project instructions, agent docs, PR template, and local gate script exist.
- `backend`: installs backend dependencies, runs Alembic migrations against Postgres, then runs pytest.
- `frontend`: installs frontend dependencies, runs lint, typecheck, unit tests, and production build.
- `e2e`: runs a real backend with Postgres, seeds the demo, installs Chromium, and runs Playwright e2e.

Security checks remain release-gate or template-level until they are tuned enough not to create noisy false positives:

- frontend `npm audit --audit-level=moderate`
- backend `pip-audit -r requirements.txt`
- backend `bandit -r app`
- optional CodeQL, Dependabot, Scorecard, and secret scanning templates under `.codex/templates/`

## Agent Review Triggers

Use the project agent docs before the following changes:

- Trainer workflow or session setup: Trainer Stories Agent, Product Reality Agent, Functional QA Agent.
- UI layout, navigation, visual polish, accessibility: UX Designer Agent and Test Pilot Agent.
- Auth, ownership, cookies, WebSocket access, secrets, dependencies: Security Reviewer.
- Architecture boundaries, data model, realtime design, migrations: Architecture Planner and ADR update.
- CI, local scripts, release flow, test gates: Pipeline Engineer and Quality Reviewer.
- Portfolio-facing README, screenshots, demo narrative: Portfolio Reviewer.

## Definition Of Done

A change is done only when:

- The behavior matches `docs/FITCOACH_FUNCTIONAL_QA_AGENT.md`.
- SDD, ADR, README, and risk docs are updated or explicitly not needed.
- The smallest meaningful checks pass locally.
- CI is expected to pass with no skipped required gate.
- UI changes have desktop and mobile visual QA evidence.
- Migrations, rollback, demo data impact, and deployment/env impact are named in the PR.

## Allowed Skips

Skipping a check is allowed only with a written reason in the PR:

- E2E may be skipped for docs-only changes.
- Build may be skipped during early local iteration, but not before PR.
- Browser visual QA may be skipped for backend-only changes.
- Security audit may stay manual until public deployment hardening.
