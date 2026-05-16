# Risk Register

| Risk | Area | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- | --- |
| WebSocket join could drift from HTTP-equivalent auth/ownership checks | Security | Low | High | Cookie/JWT validation, trainer ownership, and WS origin checks are enforced; keep websocket ownership tests in CI | Security reviewer + backend |
| Browser cookie scope can diverge between frontend host and direct WebSocket host | Realtime/Security | Medium | High | Local WS URLs now match loopback host; production must use a same-site API/WS topology or a validated ticket flow plus deployed smoke test | Architecture planner + security reviewer |
| In-memory WebSocket rooms fail across multiple backend instances | Realtime | Medium | Medium | Keep single-instance demo scope or add Redis/Postgres pub-sub before scaling | Architecture planner |
| `Base.metadata.create_all()` blurs migration discipline | Database | Medium | Medium | Use Alembic for production schema management and document startup behavior | Backend |
| Default development `SECRET_KEY` could be deployed accidentally | Security | Medium | High | Add production config validation and release checklist gate | Security reviewer |
| Active CI e2e can become slow or flaky | Delivery | Medium | Medium | Keep e2e isolated in its own job, upload Playwright artifacts on failure, and move e2e back to template only if instability blocks productive work | Pipeline engineer |
| Security scans are documented but not enforced in active CI | Security/Supply chain | Medium | Medium | Keep audit commands and security templates available; tune dependency and static checks before making them required for every PR | Security reviewer + pipeline engineer |
| Frontend TypeScript types can drift from Pydantic schemas | Contract | Medium | Medium | OpenAPI contract guard now checks critical fields; consider generated OpenAPI types later | Architecture planner |
| Session setup UX can become overloaded | Product/UX | Medium | Medium | Use trainer stories and UX agent before changing dashboard setup flow | UX designer agent |
| Saved group sessions can create too many snapshot programs over repeated demos | Product/Data | Medium | Low | Treat snapshots as session records in v1, reset demo data before screenshots, and consider hiding generated snapshots from general program lists later | Backend + product |
| Readiness check-in could be mistaken for medical screening | Product/Privacy | Medium | Medium | Keep language operational and lightweight; do not provide diagnosis or medical advice; store only demo-safe notes | Product reality + security reviewer |
| Readiness state can become stale across time zones | Product/Reliability | Medium | Low | Treat v1 as a same-day demo workflow and revisit trainer-local date handling before public production use | Backend |
| Double-click or stale cockpit action can log the wrong set | Reliability | Low | High | Send expected program-exercise/exercise/set in complete-set payload, reject stale state with `409`, and refresh cockpit state | Backend + Test pilot |
| Local workspace lacks `.git` metadata | Delivery | High | Low | Verify real clone status before publish, commit, or tracked-file claims | Project mapper |
| Build/runtime artifacts may be accidentally published | Supply chain | Low | Medium | Keep `.gitignore` current and verify tracked files in real GitHub repo; `.codex/` scaffold files are intentional project docs | Pipeline engineer |
