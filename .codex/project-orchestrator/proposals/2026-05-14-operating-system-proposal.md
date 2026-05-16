# FitCoach Pro 2.0 Project Operating System Proposal

## Dry Run Result

The project-orchestrator dry run proposed only missing scaffold files:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/project-profile.md`
- `.codex/agents/*.toml`
- `.codex/templates/*.yml`
- `.codex/templates/pull_request_template.md`
- `docs/sdd/*.md`
- `docs/architecture/system-map.md`
- `docs/architecture/adr/0001-record-architecture-decisions.md`

No existing file was scheduled for overwrite. Active `.github/workflows/ci.yml` already existed and was intentionally left unchanged.

## Applied Safe Scaffold

The scaffold was applied without `--overwrite` and without `--github`, so it created only missing project operating-system files. The generated files were then adapted to the actual FitCoach Pro 2.0 stack:

- Next.js App Router frontend in `frontend/`.
- FastAPI, SQLAlchemy, Alembic backend in `backend/`.
- PostgreSQL local/production target.
- Existing product review agents in `docs/FITCOACH_*_AGENT.md`.
- Existing active CI in `.github/workflows/ci.yml`.

## Proposed Activation Later

The files in `.codex/templates/` are proposals, not active automation. Promote them into `.github/` only after review:

1. Add Playwright e2e to CI.
2. Add Dependabot for `/frontend`, `/backend`, and GitHub Actions.
3. Add OpenSSF Scorecard.
4. Add dependency and static security checks.
5. Add CodeQL analysis for JavaScript/TypeScript and Python.
6. Add secret scanning with Gitleaks or an equivalent scanner.
7. Add a PR template requiring SDD/ADR and verification evidence.

## Current Highest Priority Risks

1. WebSocket session join needs HTTP-equivalent auth and ownership checks before public deployment.
2. Production config should reject weak/default `SECRET_KEY` and require secure cookie settings.
3. Active CI does not yet run e2e or security checks.
4. This local workspace does not expose `.git`, so tracked-file and branch state must be verified in the real clone before publishing.
