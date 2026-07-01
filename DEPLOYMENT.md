# FitCoach Pro 2.0 — Deployment (Render + Vercel)

Frontend on **Vercel**, backend + Postgres on **Render**. Frontend and backend live on
different domains (`*.vercel.app` and `*.onrender.com`), so this is a **cross-site cookie**
setup: the HttpOnly auth cookie is issued `SameSite=None; Secure` in production (enforced by
`SECURE_COOKIES=true`) so the browser attaches it to both API `fetch` calls and the cockpit
WebSocket. This is handled in code — you only set the env vars below.

> **Browser note:** cross-site cookies work in Chrome, Firefox and Edge. Safari's
> "Prevent cross-site tracking" (on by default) can block them. For a bulletproof demo in every
> browser, use the custom-domain variant at the bottom (frontend + backend under one parent domain).

## Order of operations
1. Deploy the **backend + database** on Render → note its URL `https://<backend>.onrender.com`.
2. Run **migrations** (and optionally the demo **seed**) on the database.
3. Deploy the **frontend** on Vercel with the backend URL → note `https://<app>.vercel.app`.
4. Set the backend's **`FRONTEND_ORIGIN`** to the Vercel URL and redeploy the backend.
5. **Smoke test**: log in, open a session, confirm the cockpit reaches `live`.

---

## 1. Backend + Postgres on Render

**Option A — Blueprint (recommended).** Render dashboard → **New +** → **Blueprint** → pick this
repo/branch. `render.yaml` creates the `fitcoach-backend` web service + `fitcoach-db` Postgres,
wires `DATABASE_URL`, generates a strong `SECRET_KEY`, and sets `ENVIRONMENT=production` +
`SECURE_COOKIES=true`. Leave `FRONTEND_ORIGIN` blank for now (step 4).

**Option B — Manual web service.** New + → Web Service → this repo, **Root Directory** `backend`:
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- Create a Render Postgres (New + → PostgreSQL) and copy its **Internal Connection String**.
- Env vars:
  | Key | Value |
  |---|---|
  | `ENVIRONMENT` | `production` |
  | `SECURE_COOKIES` | `true` |
  | `SECRET_KEY` | a strong random string, **≥ 32 chars** (`openssl rand -hex 32`) |
  | `DATABASE_URL` | the Postgres connection string (see driver note) |
  | `FRONTEND_ORIGIN` | (set in step 4) |
  | `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (optional) |

> **Driver note:** Render/Supabase hand out `postgres://` or `postgresql://`. The app + Alembic
> use **psycopg3**, and `config.normalize_database_url` rewrites the scheme to
> `postgresql+psycopg://` automatically, so you can paste the URL as-is.

## 2. Migrations + seed
`render.yaml` runs `alembic upgrade head` on each deploy **on paid instances**. On the **free plan**,
`preDeployCommand` does not run — open the Render **Shell** for the backend service and run once:
```bash
alembic upgrade head
python -m app.seed --reset-demo   # optional: loads the demo trainer/clients/history
```
`--reset-demo` is safe to re-run before a demo; omit it for non-destructive seeding.
Demo logins: `trainer@fitcoach.dev` / `maya@fitcoach.dev`, password `demo-password`.

## 3. Frontend on Vercel
New Project → this repo, **Root Directory** `frontend` (framework auto-detected as Next.js).
Environment variables:
| Key | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<backend>.onrender.com/api/v1` |
| `NEXT_PUBLIC_WS_URL` | `wss://<backend>.onrender.com/api/v1` |

Deploy → note the resulting `https://<app>.vercel.app`.

## 4. Close the loop
Set the backend's **`FRONTEND_ORIGIN`** = `https://<app>.vercel.app` (comma-separate extra origins,
e.g. a preview domain) and redeploy the backend. This drives both CORS (`allow_credentials`) and the
WebSocket `Origin` allow-list.

## 5. Smoke test
- Open `https://<app>.vercel.app/login` → "Sign in to demo" (trainer).
- Home loads (not 401). Start a session → the cockpit connection badge reaches **`live`**
  (proves the cross-site cookie reached the WebSocket).
- Complete a set → end session → summary renders.

---

## Gotchas
- **Cross-site cookie** needs `SameSite=None; Secure` — done in code when `SECURE_COOKIES=true`.
  If login "works" but every call is 401, `SECURE_COOKIES`/`ENVIRONMENT` or `FRONTEND_ORIGIN` is wrong.
- **The app refuses to boot** if `ENVIRONMENT=production` and: `SECRET_KEY` is weak/default,
  `SECURE_COOKIES` ≠ `true`, `FRONTEND_ORIGIN` contains `localhost`, or `DATABASE_URL` is sqlite/local.
  These guards (`config._validate_config`) are intentional.
- **Render free tier** sleeps after inactivity → first request is slow; the frontend has a 12s
  fetch timeout, so a cold backend can time out the first login. Retry, or use a paid instance.
- **Python**: backend needs **3.11+** (`datetime.UTC`, PEP 604 unions). If a Render build picks an
  older interpreter, set `PYTHON_VERSION` (e.g. `3.12.7`).
- **WebSocket URL** auto-upgrades `ws://`→`wss://` on HTTPS pages; still set `NEXT_PUBLIC_WS_URL`
  to `wss://` explicitly for clarity.

## Custom-domain variant (works in every browser, incl. Safari)
Put both apps under one parent domain so the cookie is same-site:
- Frontend: add `app.yourdomain.com` to the Vercel project.
- Backend: add `api.yourdomain.com` to the Render service.
- Set `NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1`, `NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/api/v1`,
  `FRONTEND_ORIGIN=https://app.yourdomain.com`.
- Then the cookie can be `SameSite=Lax` with `Domain=.yourdomain.com`. (Ask and I'll wire the
  `Domain` attribute + a `COOKIE_DOMAIN` env var — a small follow-up code change.)
