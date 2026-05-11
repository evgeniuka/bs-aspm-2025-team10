# FitCoach Pro

FitCoach Pro is a full-stack training management app for small-group personal training. It helps a trainer manage 2-4 trainees in the same live session while keeping each trainee's program, progress, rest timer, and workout history separate.

## Why It Matters

Small-group training is hard to manage from a single screen: every trainee can be on a different exercise, set, weight, or rest interval. FitCoach Pro turns that workflow into a live dashboard with role-based trainer and trainee experiences.

## Key Features

- Trainer and trainee authentication with JWT-based role access.
- Trainer dashboard for managing clients and workout programs.
- Exercise library and program builder.
- Real-time 2x2 split-screen session view powered by Socket.IO.
- Set completion, rest timers, and session summaries.
- Trainee history and analytics views.
- Backend and frontend test coverage for core session flows.
- GitHub Actions CI for backend tests with PostgreSQL.

## Tech Stack

- Frontend: React 19, Vite, Material UI, Recharts, Socket.IO client, Vitest.
- Backend: Python, Flask, Flask-SQLAlchemy, Flask-SocketIO, PostgreSQL, JWT.
- Tooling: ESLint, Pytest, GitHub Actions.

## Project Structure

```text
backend/   Flask API, database models, Socket.IO handlers, seed scripts, tests
frontend/  React/Vite application, UI components, pages, frontend tests
docs/      Course documents and product planning artifacts
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask run
```

The backend expects PostgreSQL by default. Configure `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, and `CORS_ORIGINS` in `backend/.env` for local development.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:5000`.

## Tests

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run test
npm run build
```

## Resume Highlights

- Built a role-based full-stack fitness coaching platform with real-time session synchronization.
- Designed a split-screen trainer workflow for monitoring up to four trainees at once.
- Added automated tests for authentication, clients, exercises, programs, session state, and live updates.
- Configured CI with PostgreSQL-backed backend tests.

## Next Improvements

- Add polished screenshots or a short demo GIF to the README.
- Add Docker Compose for one-command local startup.
- Add seed data instructions for a recruiter-friendly demo login.
- Split the frontend bundle into smaller chunks.
