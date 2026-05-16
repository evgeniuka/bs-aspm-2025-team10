# FitCoach Multi-Agent Review - 2026-05-13

> Historical snapshot. Some P0 findings in this report, including WebSocket auth/ownership, have since been implemented. Use `docs/FITCOACH_FUNCTIONAL_QA_AGENT.md`, `docs/sdd/`, and the latest verification output as the current product contract.

This report captures a full staged review of FitCoach Pro 2.0 using the project agents:

- Trainer Stories Agent
- UX Designer Agent
- Product Reality Agent
- Test Pilot Agent
- Portfolio Reviewer Agent
- Functional QA Agent

The focus was the current product loop and the active browser route `/programs/31`.

## Evidence Collected

Local checks:

```text
backend pytest: 10 passed
frontend lint: passed
frontend typecheck: passed
frontend unit tests: passed on isolated rerun
frontend build: passed
frontend e2e: 1 passed
```

Notes:

- One parallel `npm run test` execution timed out while `next build` was also running. A clean isolated rerun passed. Treat this as a minor test-runtime reliability observation, not a product failure.
- Playwright opened `/programs/31` on desktop and mobile.
- `/programs/31` desktop had no console errors.
- `/programs/31` mobile has page-level horizontal overflow caused by the wide exercise table.
- The current workspace folder is not a git repository. Before portfolio publishing, verify the actual GitHub repo state, branch, `.gitignore`, and tracked artifacts.

Screenshot artifacts:

- `frontend/test-results/program-31-agent-review-desktop.png`
- `frontend/test-results/program-31-agent-review-mobile.png`

## Overall Verdict

FitCoach Pro is no longer a toy CRUD app. The core full-stack loop is real:

```text
roster -> program -> live session -> summary -> client history
```

The strongest portfolio signal is the realtime small-group cockpit combined with trainer-side workflow. The weakest current product area is `/programs/[programId]`: it works technically, but still feels like an admin table rather than a trainer planning workspace.

Primary blockers before public portfolio/demo:

1. WebSocket auth and ownership.
2. Program editor UX and mobile overflow.
3. Honest and stronger program builder/editor capability.
4. Realistic multi-week demo history.
5. README/deploy/screenshots/GIF/architecture packaging.

## Agent 1: Trainer Stories Agent

### Verdict

The product direction is correct. FitCoach now supports the skeleton of a real trainer workflow, especially after moving session setup to a roster-first model. It is no longer locked to four hardcoded demo clients.

However, the product still lacks trainer context at key decision points. A real trainer does not only edit sets and reps. They need to know what happened last time, what the client struggled with, what to progress, and what to watch for.

### What Already Matches Trainer Stories

- Roster-first setup with 10 clients, search, `Solo`, `Add`, selected lineup, shared focus, and overrides.
- 1-client and 1-10 small-group sessions are supported by frontend and backend.
- Live cockpit has stable slots, set completion, rest status, WebSocket updates, and end-session flow.
- Summary captures planned/completed work, volume, coach notes, next focus, and profile links.
- Client profile exists with programs, analytics, and workout history.
- E2E covers login -> dashboard -> select client -> cockpit -> complete set -> summary -> notes -> client profile.

### Gaps

P0:

- `/programs/31` is a table editor, not a coaching-aware planning screen.
- Exercise row `notes` exist in the backend shape but are not editable in the UI.
- `Add` exercise silently adds the first exercise instead of opening a searchable exercise library.
- Cockpit logs prescribed reps/weight, not actual reps/weight.
- No undo or adjust-set flow after mistaken set logging.
- Client profile does not answer: "What should I do with this client next time?"
- Demo history looks shaped by test/manual runs instead of a realistic training timeline.

P1:

- Readiness, soreness, injury, and constraint notes.
- Program progression signals: last load, suggested increase, repeated missed sets.
- Exercise library search/filter by category, equipment, difficulty.
- Mobile-friendly program editor.
- Session modes: assessment, strength, circuit, mobility.

P2:

- Scheduling, payments, calendar sync, client portal, messaging, wearables, nutrition, team roles, AI assistant.

### Trainer Acceptance Criteria

- `/programs/{id}` shows last workout date, last note, next focus, recent completion rate.
- Exercise rows support sets, reps, weight, rest, and coaching cues.
- Add exercise opens searchable/filterable library.
- Dirty state is visible.
- Program page has a primary action to start training with this program.
- Cockpit complete-set flow allows actual reps/weight.
- Last saved set can be undone.
- Client profile shows "next session prep" above raw analytics.

### Trainer Priority

1. Rebuild `/programs/31` into a trainer planning screen.
2. Add `Start session with this program`.
3. Upgrade cockpit logging to actual reps/weight plus undo.
4. Seed realistic multi-week history.

## Agent 2: UX Designer Agent

### Verdict

The product visual direction is improving. Dashboard/session setup is now closer to operational SaaS. But `/programs/31` is only around 5/10 from a product design perspective.

The problem is not mainly color or spacing. The problem is UX model. A trainer sees a CRUD table, not a workout plan.

### What Works

- Calm shell, compact cards, and clear primary button.
- Header is not overloaded.
- Desktop exercise rows are readable enough.
- The product no longer looks like a landing page.

### Design Problems

- `Program editor` is too generic. It should communicate client + program + next session plan.
- `Details` is too visually equal to the actual exercise plan.
- Visible copy like "Stable rows, compact controls, no layout jumping" sounds like an internal acceptance note, not user-facing UI.
- Demo note text such as "Built from the portfolio demo program builder" breaks product believability.
- The `Add` action does not match trainer expectations.
- No `Unsaved changes`, `Saved just now`, or `Save failed` state.
- No obvious path from program to training.

### Accessibility Problems

- Row number inputs do not have row-specific accessible labels.
- Exercise selects do not have contextual labels.
- `Move up`, `Move down`, `Remove` buttons lack exercise context.
- 32px icon buttons are small for mobile/touch use.

### Mobile Problem

`/programs/31` overflows horizontally:

- Desktop 1440px measured overflow.
- Mobile 390px measured page width around 810px.
- Cause: `min-w-[760px]` table inside the page grid.

### Designer Acceptance Criteria

- `/programs/31` has no page-level horizontal scroll at 390px, 834px, or 1440px.
- Mobile uses stacked exercise cards, not a desktop table.
- All row inputs/actions have unique accessible labels.
- Touch targets are at least 40-44px where practical.
- `Add exercise` opens a searchable picker.
- Save/dirty/error states are visible.
- No implementation/meta/demo copy is visible in the product UI.

### Designer Priority

Turn `/programs/31` into a "Trainer Plan Builder" rather than polishing the current table.

## Agent 3: Product Reality Agent

### Verdict

FitCoach is credible as a portfolio product if it stays narrow. It should not try to copy broad trainer platforms such as PTminder, FITR, TrainerAdmin, or TrainPulse. Those products cover client management, workout plans, progress, booking, payments, reminders, messaging, and more.

FitCoach's believable wedge is:

```text
trainer-side realtime small-group coaching + useful client history
```

### Core V1

Keep v1 focused on:

- `/dashboard`: roster-first session setup.
- `/programs/[programId]`: believable program editing.
- `/sessions/[sessionId]`: realtime cockpit.
- `/sessions/[sessionId]/summary`: saved recap and notes.
- `/clients/[clientId]`: history, programs, progress.
- Backend auth, ownership, lifecycle, analytics, WebSocket.
- Demo seed that looks intentional and resettable.

### Product Reality Gaps

- Dashboard analytics look like test residue: low completion rate, 0m average session, single training day.
- `/programs/31` lacks previous performance, last note, next focus, readiness, and progression context.
- Per-exercise notes are missing from UI.
- Program duplication/templates/effective week can wait, but will matter later.

### Product P0 Priorities

1. Controlled demo data reset/seed with realistic sessions across 4-6 weeks.
2. Program editor v1.5: previous performance, per-exercise notes, validation, dirty state, client context.
3. Client profile: readiness/constraints and last coach note above charts.
4. Summary should hand off cleanly into next program edit.
5. Rename `Suggested 4` to something more believable until scheduling exists, such as `Quick pick`.

### Do Not Build Now

- Payments.
- AI generator.
- Nutrition.
- Client portal.
- Wearable imports.
- Team management.

These are real market needs, but they dilute the portfolio story before the core coaching loop is excellent.

## Agent 4: Test Pilot Agent

### Verdict

The happy-path demo is covered, but the test suite does not yet protect the product from real-world behavior.

The strongest P0 testing/security concern is WebSocket auth and ownership.

### Covered Today

Backend:

- Auth cookie and `/me`.
- Session create, complete set, rest, start next set, end.
- Summary, notes, client detail analytics.
- Program get/update happy path.
- WebSocket happy path receives join and rest events.

Frontend:

- Login -> dashboard -> select client -> cockpit -> complete set -> end -> summary -> save notes -> client profile.
- Component tests for HTTP client, cockpit quadrant, analytics, summary card, client history, empty analytics chart.

### P0 Test Gaps

- WebSocket unauthenticated connection rejected.
- Other trainer cannot subscribe to someone else's session.
- Other trainer cannot mutate/end/patch another trainer's session.
- Program get/update/create ownership tests.
- Duplicate clients and invalid client/program assignment on session start.
- Double-click/retry `complete-set` must not accidentally log two sets.
- `/programs/31` e2e: edit row, reorder, save, reload, verify persistence.
- Session setup e2e: search, add 1/2/10 clients, max 10 disabled, remove/substitute.

### P1 Test Gaps

- Component tests for `StartSessionPanel`, `ProgramEditor`, `ProgramBuilder`, `DashboardError`, `SessionSummaryView`.
- Mobile visual tests for key routes.
- WebSocket disconnect/reconnect UI.
- Empty states: no clients, no programs, no sessions, empty analytics.
- Expired token behavior.

### Test Pilot Priority

1. Add WebSocket auth/ownership tests and implementation.
2. Add mutation ownership tests.
3. Add double-complete protection.
4. Add `/programs/31` e2e.
5. Add visual QA matrix.

## Agent 5: Portfolio Reviewer Agent

### Verdict

FitCoach is already around 7/10 as a hiring artifact. It proves more than a school CRUD project:

- Next.js App Router and TypeScript.
- FastAPI, SQLAlchemy, Alembic, Postgres-ready structure.
- HttpOnly cookie auth.
- Typed API client.
- WebSocket realtime cockpit.
- Tests and e2e.
- Product loop with summary/history.

The remaining weakness is presentation: README, deploy, screenshots, and the polish of `/programs/31`.

### Strong Hiring Signals

- Real full-stack architecture.
- Realtime feature that is memorable.
- Product thinking beyond CRUD.
- Test culture.
- No unsupported AI claims.

### Weak Hiring Signals

- README does not yet sell the project.
- No live demo URL.
- No GIF/screenshots of the cockpit flow.
- No architecture diagram.
- `/programs/31` feels like an admin table.
- Current local workspace is not a git repo, so GitHub hygiene must be verified elsewhere.

### Portfolio Requirements

README should include:

- One-sentence pitch.
- Live demo URL.
- Demo credentials.
- GIF: login -> dashboard -> choose clients -> cockpit -> summary.
- Screenshots: dashboard, cockpit, summary, client profile/program editor.
- Architecture diagram.
- Setup and test commands.
- Deployment notes.
- Tradeoffs: in-memory WebSocket manager, no Redis yet, demo auth, no billing/scheduling yet.
- Next improvements.

### Portfolio Priority

1. Deploy + live demo.
2. README with cockpit GIF.
3. Rebuild `/programs/31` into trainer-first workspace.
4. Add screenshots and architecture diagram.
5. Verify GitHub branch/history/artifacts.
6. Add e2e for program editor.

## Agent 6: Functional QA Agent

### Capability Matrix

| Area | Status | Conclusion |
| --- | --- | --- |
| Auth | PASS | Email/password with HttpOnly cookie works locally. Production cookie strategy still needs proof. |
| Dashboard | PASS | Core dashboard, metrics, recent sessions, and setup are present. |
| Session setup | PASS | Roster-first setup now matches pre-session attendance flow. |
| Program builder/editor | PARTIAL | Editor can load/edit/reorder/save. Builder is closer to a quick template generator than a true builder. |
| Cockpit | PARTIAL | Realtime happy path works, but WebSocket auth/ownership is missing. |
| Summary | PASS/PARTIAL | Notes and next focus persist. Error/success handling can improve. |
| Client profile | PASS/PARTIAL | Programs/history/analytics exist. Readiness/constraints/benchmarks missing. |
| Analytics | PARTIAL | Computed from logs, but seed data is not rich enough for credible demo analytics. |
| Ownership | FAIL/PARTIAL | HTTP endpoints mostly filter by trainer_id, but WebSocket reads session by id without user ownership. |
| UX quality | PARTIAL | Dashboard improved. `/programs/31` mobile overflows and still feels like admin table. |
| Reliability | PARTIAL | Typed client and recovery states exist. No WS reconnect/error UI. |
| Deployment readiness | PARTIAL | README/env/CI basics exist. No live URL, screenshots/GIF, or proven deploy cookie/WebSocket flow. |

### P0 QA Fixes

1. Secure WebSocket auth and ownership.
2. Make Program Builder claims honest: build a real builder or rename it to quick template.
3. Verify production cookie and WebSocket deploy strategy.

### P1 QA Fixes

1. Responsive `/programs/[id]` without horizontal overflow.
2. Program editor tests.
3. Backend ownership tests for programs and WebSocket.
4. Summary PATCH error UI and dirty/saved state.
5. WebSocket disconnect/reconnect state.
6. Demo history across multiple dates.
7. Expanded e2e coverage.

## Unified P0 Action Plan

Do these before public portfolio sharing:

1. Secure WebSocket route with auth and trainer ownership.
2. Fix `/programs/[id]` mobile overflow and accessibility labels.
3. Redesign `/programs/[id]` from "Program editor" into a trainer planning workspace.
4. Add program editor e2e and backend ownership tests.
5. Create realistic demo history and reset/seed story.
6. Improve README with demo path, screenshots/GIF, architecture, tradeoffs.
7. Verify deploy cookie/WebSocket strategy.

## Recommended Next Implementation Slice

The highest-value next slice is:

```text
Program Workspace v1.5
```

Scope:

- Rename/reframe screen around client + program context.
- Add client context panel: goal, last session, next focus, recent completion.
- Add per-exercise coaching notes.
- Add dirty/saved/error states.
- Add row-specific accessible labels.
- Remove page-level horizontal overflow.
- Use stacked mobile cards.
- Add e2e for edit/reorder/save/reload.

This slice addresses Trainer Stories, UX Designer, Product Reality, Test Pilot, Functional QA, and Portfolio Reviewer at once.

## Later P1/P2

P1:

- Actual reps/weight logging.
- Undo last set.
- Readiness/constraints.
- Session modes.
- Exercise library search/filter.
- Multi-week analytics seed.
- WebSocket disconnect UI.

P2:

- Scheduling.
- Payments.
- Calendar sync.
- Client portal.
- Messaging.
- Wearables.
- Nutrition.
- AI assistant.
