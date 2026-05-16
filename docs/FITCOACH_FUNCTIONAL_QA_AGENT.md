# FitCoach Functional QA Agent

This file is the product contract for FitCoach Pro 2.0. Treat it as a small QA agent: before adding a feature, check the target behavior here; after changing code, audit the app against this file and run the mapped verification commands.

For multi-agent review order, read `docs/FITCOACH_AGENT_ROSTER.md`.

For domain/user-story decisions, read `docs/FITCOACH_TRAINER_STORIES_AGENT.md` first. This QA agent verifies implementation quality; the trainer stories agent verifies whether the feature belongs in the trainer workflow.

For UI work, read `docs/FITCOACH_UX_DESIGNER_AGENT.md`.

For product scope decisions, read `docs/FITCOACH_PRODUCT_REALITY_AGENT.md`.

For test planning, read `docs/FITCOACH_TEST_PILOT_AGENT.md`.

For portfolio polish, read `docs/FITCOACH_PORTFOLIO_REVIEWER_AGENT.md`.

## Agent Mission

Act as a strict but practical full-stack product reviewer. Verify that FitCoach Pro 2.0 feels like a real operational SaaS demo for a full-stack portfolio, not a generated landing page or a toy CRUD app.

When invoked, the agent should:

1. Read this file first.
2. Read the relevant agent files from `docs/FITCOACH_AGENT_ROSTER.md` when feature priority, UX, roadmap scope, testing, or portfolio presentation is involved.
3. Compare current code and UI behavior against the capability matrix.
4. Check that the user journey still works end to end: login -> dashboard -> setup session -> cockpit -> end session -> summary -> client history.
5. Report missing behavior, broken flows, weak UX, and missing tests before proposing new features.
6. Prefer small, testable changes over broad rewrites.

## Product Positioning

- Audience: recruiters and engineering managers reviewing a full-stack developer portfolio.
- Domain: trainer operations for small-group personal training.
- Tone: professional operational SaaS, compact and useful, not a flashy fitness landing page.
- V1 constraint: no AI-generated workouts or chat assistant. Any future AI feature must be opt-in, validated, and explainable.
- Signature feature: realtime coach cockpit for 1-10 selected clients with independent program progress.
- Product roster: the trainer can have more clients than the cockpit capacity. The 10-client cap belongs only to one live cockpit, not to the whole product.

## Core User Journey

1. Demo trainer logs in with public demo credentials.
2. Demo client can log in and submit today's readiness check-in before training.
3. Trainer sees a dense dashboard with clients, readiness, training load, recent sessions, and session setup.
4. Trainer works through a guided session tunnel: choose clients from the full roster, confirm the selected lineup, choose the session focus, and only adjust individual programs when needed.
5. Trainer opens a realtime cockpit with one stable slot per selected client.
6. Trainer completes sets with actual reps/weight when needed, can undo the last mistaken set, manages rest/start-next-set states, and ends the session.
7. App opens session summary, showing planned vs completed work, actual logged volume, notes, and next focus.
8. Trainer saves notes and opens a client profile with history and analytics.

## Trainer Session Setup UX Stories

The session setup UI must be designed around trainer behavior before a live workout. It must not feel like an equalizer, spreadsheet, or technical configuration form.

### Realistic Trainer Cases

| Case | Story | UX requirement |
| --- | --- | --- |
| Scheduled small group | As a trainer, I have a regular group session and most clients are expected to attend. | Offer an explicit saved group shortcut that opens the attendance tunnel, prefills expected attendees, and makes no-shows easy to remove before start. |
| One no-show | As a trainer, one person did not arrive and I need to remove them without rebuilding the session. | Selected client cards must remove in one click, and the full roster must remain available for substitutions. |
| 1:1 substitution | As a trainer, the group session turns into a solo session. | A single selected client must be valid and the CTA must still feel intentional. |
| Shared session focus | As a trainer, today is strength, conditioning, or core/stability for the whole group. | Session focus should be a primary one-click choice that applies to the lineup. |
| Individual modification | As a trainer, one client needs a modified program because of readiness, pain, or progression. | Per-client program overrides should exist, but be visually secondary and not dominate the setup. |
| Late arrival | As a trainer, a late client may be added before the session starts. | Available roster must stay visible and fast to add until the session opens. |
| Large roster | As a trainer, I manage more than one small group and need to pick today's attendees. | The session setup starts from the client list with search, not from four fixed demo people. |
| Recruiter demo | As a reviewer, I should understand the workflow in seconds. | The UI should read as: attendance -> focus -> lineup -> start, without explanatory marketing copy. |

### Session Setup Acceptance Criteria

- Primary controls are a searchable client list, selected lineup cards, and session focus buttons, not repeated dropdowns.
- Selected clients are explicit. Saved groups may prefill expected attendees only after a visible trainer action and must show attendance before start.
- A saved group shortcut is allowed only as a visible action chosen by the trainer.
- The demo roster contains more clients than one cockpit can train at once.
- The main CTA is enabled for 1 to 10 selected clients.
- The selected lineup is visible before starting and uses stable slot/order numbers.
- The global focus applies a sensible program variant to every selected client.
- Per-client program changes are available in a secondary "adjust individual plans" area.
- Removing a client does not erase their stored individual plan preference.
- A max of 10 selected clients is enforced without surprising layout shifts.
- Empty selection explains why the start action is disabled through state, not a cryptic error.
- Mobile must show attendance and lineup without text overlap or tiny checkboxes.
- The setup should feel like pre-session attendance, not like configuring four unrelated forms.
- Program creation belongs in the left workflow panel as a secondary tool; it must not interrupt the main path to start training.

## Capability Matrix

| Area | Required behavior | Verification |
| --- | --- | --- |
| Auth | Email/password login uses HttpOnly cookie auth. Demo credentials are documented. | Backend auth tests, e2e login. |
| Dashboard | Uses a no-body-scroll workbench on desktop: persistent left navigation, functional rail for tunnel/saved groups/programs, and the main setup visible without scrolling. | Visual pass on desktop/mobile, e2e. |
| Session setup | Supports choosing 1 to 10 clients from a roster larger than the cockpit. Uses searchable roster, selected lineup preview, a shared focus selector, and secondary per-client overrides. Active sessions can be resumed. | Backend session tests, e2e, manual UI pass. |
| Client management | Trainer can create, edit, and archive active clients, with completed history preserved and inactive clients removed from active workflows. | Backend client tests, e2e roster management. |
| Client check-in | Client portal supports today's energy, sleep, soreness, pain/limitations, and training goal. Trainer dashboard surfaces readiness, missing submissions, and attention flags before session setup. | Backend trainee portal tests, e2e check-in flow, manual UI pass. |
| Workout variants | Seed data provides multiple practical program variants per client, such as strength, conditioning, and core/stability. | Seed audit, dashboard dropdowns. |
| Saved groups | Trainer can manage recurring small-group rosters and exercise templates, prepare the group in session setup, confirm attendance, add substitutes, preview the template, and start a live session. | Backend group tests, e2e saved-group start, manual UI pass. |
| Program builder | Trainer can create ordered programs with exercise, sets, reps, weight, and rest. | Component/unit coverage where useful, manual create flow. |
| Program editor | Trainer can open and edit an existing program, reorder exercises, update loading/rest, and save. | Backend program tests, manual UI pass. |
| Program hygiene | Session snapshot programs generated from group templates do not clutter normal program lists or client active-program cards. | Backend program/client tests, manual profile pass. |
| Realtime cockpit | Cockpit renders 1-10 stable slots, shows current exercise, set progress, volume, status, rest timer, actual reps/weight logging, last-set undo, and end-session flow. | Cockpit unit test, websocket test, e2e. |
| Session summary | End session leads to `/sessions/{id}/summary`, not a dead dashboard jump. Summary supports actual logged reps/weight/volume, notes, and next focus. | e2e summary flow, backend summary tests. |
| Client profile | Client profile shows programs, session history, status, volume trend, and links back to editable programs/summaries. | Component tests, backend client detail tests. |
| Analytics | Trainer and client analytics use real workout logs and handle empty/single-day data without awkward charts. Trainer analytics include daily/weekly volume, focus mix, top exercises, readiness mix, client load, and attention flags. Client analytics include completion rate, average/best volume, trend, and exercise breakdown. | Backend analytics test, component tests, visual pass. |
| Demo seed | `python -m app.seed --reset-demo` rebuilds a clean curated demo with roster, programs, check-ins, and historical sessions without test-created program names. | Backend seed test, local demo reset before screenshots. |
| Ownership | A trainer cannot read or mutate another trainer's clients, programs, sessions, summaries, or analytics. | Backend ownership tests. |
| UX quality | No text overlap on mobile, no marketing landing page as app entry, no hidden dead buttons, no misleading loading states. | Playwright screenshots, manual browser pass. |
| Reliability | API failures surface useful UI states. Frontend uses typed API client and route helpers. | Unit tests and code review. |
| Deployment readiness | README documents fast SQLite setup, Postgres setup, demo login, env vars, deploy targets, mobile status, and test commands. | README audit, `npm run setup:local`, `npm run start:local`. |

## Regression Commands

Run these before calling a product iteration complete:

```bash
npm run quality
```

Or run the same gate by area:

```bash
cd backend
python -m app.seed --reset-demo
.venv\Scripts\python.exe -m pytest
```

```bash
cd frontend
npm run lint
npm run typecheck
npm run test
npm run build
npm run e2e
```

## Visual QA Targets

Capture or inspect these routes on desktop and mobile:

- `/login`
- `/dashboard`
- `/analytics`
- `/client`
- `/sessions/{id}`
- `/sessions/{id}/summary`
- `/clients/{id}`
- `/programs/{id}`

Check specifically for:

- Text overlap or clipped controls.
- Disabled buttons that do not explain why.
- Cards that look like unrelated boxes instead of one product.
- Charts that look empty or misleading with demo data.
- Session actions that do not visibly change state.

## Current Next Priorities

1. Prove production cookie/WebSocket topology with a deployed smoke test before public launch.
2. Dedicated mobile cockpit polish pass for small phones.
3. Richer seed data and analytics history across multiple dates.
4. WebSocket disconnect/reconnect UI and production realtime notes.
5. Public deployment and README screenshots/GIF.
