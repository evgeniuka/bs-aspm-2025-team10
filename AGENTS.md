# AGENTS.md

## Project Operating Model

FitCoach Pro 2.0 is a full-stack portfolio app for trainer operations: roster -> program -> live session -> summary -> client history.

Before large changes, read these in order:

1. `README.md`
2. `.codex/project-profile.md`
3. `docs/FITCOACH_AGENT_ROSTER.md`
4. `docs/FITCOACH_FUNCTIONAL_QA_AGENT.md`
5. `docs/sdd/00-context.md`
6. `docs/architecture/system-map.md`
7. `docs/QUALITY_GATE.md`

Treat `docs/sdd/` as the living product contract and `docs/architecture/adr/` as the durable decision log. Update them when behavior, architecture, deployment, security posture, or risk materially changes.

## Agent Roles

Use project-scoped Codex agents from `.codex/agents/` for bounded work:

- `project_mapper`: read-only repo map, commands, docs, ownership, risk hotspots.
- `architecture_planner`: read-only boundaries, flows, ADR candidates, integration risks.
- `sdd_writer`: workspace-write owner for `docs/sdd/` and directly related architecture docs.
- `pipeline_engineer`: workspace-write owner for `.codex/`, workflow templates, quality gates.
- `security_reviewer`: read-only auth, secrets, dependency, CI, and supply-chain review.
- `quality_reviewer`: read-only check of generated operating-system artifacts and contradictions.

The existing product review agents in `docs/FITCOACH_*_AGENT.md` are still authoritative for trainer domain, UX, product realism, testing, and portfolio quality.

## Working Rules

- Preserve user changes. Do not revert unrelated edits.
- This workspace may not contain `.git`; verify repository state before branch, commit, or diff claims.
- Keep changes small, traceable, and covered by the smallest meaningful checks.
- Do not enable active deploy, billing-impacting automation, or repository security settings without explicit approval.
- Keep public demo behavior professional and product-like; avoid AI features unless they are explicitly scoped and validated.
- For UI work, keep the operational SaaS style: dense, clear, trainer-first, no marketing landing page as app entry.

## Local Commands

Backend:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
```

Fallback backend setup:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
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

Repository quality gate:

```powershell
npm run quality:fast
npm run quality
```

Local services:

```powershell
docker compose up -d db
npm run dev:api
npm run dev:web
```

## Done Criteria

- Relevant SDD and ADR entries are current or explicitly not needed.
- Implementation matches the scoped requirement and the FitCoach QA contract.
- Backend and frontend checks have run, or the skipped checks and reason are documented.
- UX changes have a browser or screenshot pass on desktop and mobile when relevant.
- Risks, migrations, rollback, and user-facing behavior are called out in the final note.
