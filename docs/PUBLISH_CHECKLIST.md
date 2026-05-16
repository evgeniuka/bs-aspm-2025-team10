# Publish Checklist

Use this before pushing FitCoach Pro 2.0 to GitHub or opening a public portfolio demo.

## Repository State

- `git status --short` works from the project root.
- No local-only files are staged:
  - `.env`, `.env.local`
  - `.venv/`, `node_modules/`, `.next/`
  - `backend/*.db`
  - `*.log`, `.codex/logs/`
  - `frontend/test-results/`, `frontend/playwright-report/`
- Public files are present:
  - `README.md`
  - `backend/.env.example`
  - `frontend/.env.example`
  - `docker-compose.yml`
  - `docs/screenshots/*.png`
  - `.github/workflows/ci.yml`

## Local Release Gate

From the repository root:

```powershell
npm run quality
```

Manual fallback:

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
```

```powershell
cd frontend
npm run lint
npm run typecheck
npm run test
npm run build
npm run e2e
```

Reset the curated demo after e2e or screenshot capture:

```powershell
cd backend
.venv\Scripts\python.exe -m app.seed --reset-demo
```

## README Review

- Demo credentials are documented.
- Fast local setup works from a fresh clone.
- Screenshots match the current app.
- Architecture and deployment notes are realistic.
- "What I Would Improve Next" is honest and not framed as finished production work.

## Publish Notes

This Codex workspace may be a copied working directory rather than a git clone. If `git status` says `not a git repository`, publish from the real clone or initialize git only after confirming the target remote:

```powershell
git init
git remote add origin https://github.com/evgeniuka/bs-aspm-2025-team10.git
git checkout -b fitcoach-pro-2-release
git add .
git commit -m "Prepare FitCoach Pro 2.0 portfolio release"
git push -u origin fitcoach-pro-2-release
```

Do not force-push or overwrite the old course project history unless that is the intended repository strategy.
