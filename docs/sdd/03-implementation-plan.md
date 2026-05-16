# Implementation Plan

## Slices

1. Stabilize the operating system docs.
   - Keep `AGENTS.md`, `.codex/project-profile.md`, SDD, ADRs, and templates current.
   - Make active CI and proposed templates explicit.

2. Fix deployment-blocking security gaps.
   - Keep WebSocket auth/ownership checks covered and prove the deployed cookie/WS topology.
   - Add production config validation for `SECRET_KEY`, `FRONTEND_ORIGIN`, and `SECURE_COOKIES`.
   - Document CSRF posture for cookie-auth state-changing requests.

3. Improve trainer-first session setup.
   - Use searchable roster and selected lineup as the primary flow.
   - Support one to ten selected clients.
   - Keep individual program overrides secondary.

4. Strengthen demo data and analytics.
   - Keep roster larger than one cockpit.
   - Add realistic workout history across several dates.
   - Verify empty/sparse analytics states.

5. Harden realtime and summary flows.
   - Ensure cockpit state transitions, actual set logging, and last-set undo are covered by backend tests and e2e.
   - Assert the browser cockpit reaches a `live` WebSocket connection in e2e.
   - Ensure `End session` reliably routes to `/sessions/{id}/summary`.

6. Prepare public portfolio launch.
   - Add README screenshots or GIF.
   - Add deployment smoke checklist.
   - Decide which `.codex/templates/` workflows should become active `.github/` files.

## Dependencies

- Local Postgres through Docker Compose.
- Backend virtual environment with `backend/requirements.txt`.
- Frontend `node_modules` from `frontend/package-lock.json`.
- Demo credentials and seed data from `backend/app/seed.py`.
- Vercel, Render, and managed Postgres for public deployment.

## Ownership

- Product/domain: `docs/FITCOACH_TRAINER_STORIES_AGENT.md`.
- UX: `docs/FITCOACH_UX_DESIGNER_AGENT.md`.
- QA contract: `docs/FITCOACH_FUNCTIONAL_QA_AGENT.md`.
- Architecture: `.codex/agents/architecture-planner.toml` plus `docs/architecture/`.
- Pipeline: `.codex/agents/pipeline-engineer.toml` plus `.codex/templates/`.
- Security: `.codex/agents/security-reviewer.toml`.
- SDD: `.codex/agents/sdd-writer.toml`.

## Rollback Points

- Documentation-only changes can be reverted by removing the new scaffold files or restoring previous sections.
- Frontend UI changes can be rolled back per route or component if e2e catches a workflow regression.
- Backend route changes must preserve migration compatibility or include Alembic downgrade notes.
- Active CI changes should be introduced from `.codex/templates/` in small PRs, one workflow at a time.
