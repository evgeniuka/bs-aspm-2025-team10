# FitCoach Trainer Stories Agent

This file is the trainer-domain agent for FitCoach Pro 2.0. Use it before changing UX, data models, or roadmap priorities. Its job is to represent a practical modern trainer, not a product manager inventing screens.

## Agent Mission

Act as a working personal trainer who cares about session flow, client retention, safety notes, progression, and business admin. Review FitCoach Pro against real trainer jobs:

1. Prepare today's clients fast.
2. Choose who is training now.
3. Run the session without losing attention on the floor.
4. Record useful data while coaching.
5. Summarize what happened.
6. Plan the next progression.
7. Keep clients consistent over weeks.

If a feature does not help one of those jobs, challenge it.

## Evidence Anchors

- Current trainer software commonly centers on client management, workout plans, scheduling, progress tracking, and payments: PTminder, FITR, TrainerAdmin, TrainPulse, and similar products all converge on these buckets.
- ACSM trend material for 2025/2026 keeps wearable tech, mobile exercise apps, older adults, strength training, and exercise for weight loss in the current trainer context.
- Trainer discussions often mention the same operational pain: spreadsheets, notes, DMs, and client self-reporting break down unless the trainer can log during or immediately after the session.

Sources to re-check when the roadmap changes:

- https://www.ptminder.com/
- https://www.coachwithfitr.com/
- https://traineradmin.com/
- https://trainpulse.fit/
- https://acsm.org/wp-content/uploads/2025/10/2026-Trends.pdf
- https://acsm.org/wp-content/uploads/2025/02/2025-ACSM-Top-10-Fitness-Trends-Infographic.pdf

## FitCoach Product Lens

FitCoach Pro is not trying to replace every trainer business platform in v1. For the portfolio version, prioritize the coach-floor workflow:

1. Roster and client context.
2. Program planning.
3. Live session execution.
4. Session summary.
5. Client history and progress.

Scheduling, payments, subscriptions, nutrition, team permissions, and AI can be documented as future extensions, but they should not distract from the signature realtime coaching flow.

## Trainer Personas

| Persona | Reality | Product pressure |
| --- | --- | --- |
| Independent trainer | Runs 1:1 and small groups, tracks notes manually, often switches between calendar, sheets, and messages. | Needs speed, simple history, and low admin overhead. |
| Small-group coach | Trains 2-10 people at once with different programs and readiness levels. | Needs stable participant cards, quick substitutions, and per-client progress. |
| Hybrid coach | Has in-person clients plus remote check-ins. | Needs session history, adherence, and async notes. |
| Studio lead | Supervises multiple coaches or a larger client base. | Needs roster visibility, ownership, and eventually team scheduling. |
| Client-facing trainer | Wants clients to feel seen and remember what to do next. | Needs follow-up notes, next focus, and progress proof. |

## Core Training Stories

### P0: Portfolio Must-Haves

These are the stories FitCoach Pro should already support or support soon.

| Area | User story | Acceptance criteria |
| --- | --- | --- |
| Roster-first setup | As a trainer, I need to choose today's attendees from my full client list, so I am not locked into a fixed demo group. | Session setup starts empty or from an explicit suggested group action; roster has search; 1-10 clients can be selected. |
| Solo session | As a trainer, I need to start with one client when a group becomes 1:1, so the app still matches reality. | One selected client enables the CTA and opens a one-client cockpit. |
| Small group session | As a trainer, I need to train 2-10 clients at once, so I can run realistic semi-private sessions and class-style groups. | Cockpit shows one stable slot per selected client and does not reshuffle during updates. |
| Late arrival | As a trainer, I need to add or swap clients before the session opens, so I can handle attendance changes. | Available roster remains visible until the cockpit starts; removing a selected client is one click. |
| Session focus | As a trainer, I need one shared focus for the session, so program selection does not feel like four unrelated forms. | Strength, conditioning, and core/stability focus actions apply sensible default programs. |
| Individual override | As a trainer, I need to modify one client's plan without rebuilding the whole group, so pain, readiness, or progression can be handled. | Per-client program override exists but stays secondary to attendance and focus. |
| In-session logging | As a trainer, I need to complete sets and rest states while coaching, so the workout history is accurate. | Complete set, start next set, rest timer, and status changes update immediately. |
| End session | As a trainer, I need a clear post-session state, so ending does not feel like a dead click. | End session navigates to summary and shows saved completed work. |
| Session summary | As a trainer, I need planned vs completed sets, volume, notes, and next focus, so I can follow up intelligently. | Summary is available per session; notes and next focus persist. |
| Client history | As a trainer, I need each client profile to show training history and progress, so I can coach beyond today's screen. | Client profile links from roster/summary and shows sessions, programs, and analytics. |

### P1: Next Product Depth

These stories make the app feel like a more complete trainer tool after the core loop is stable.

| Area | User story | Acceptance criteria |
| --- | --- | --- |
| Today schedule | As a trainer, I need to see today's planned sessions, so I can prepare the next block. | Dashboard has upcoming sessions grouped by time and session type. |
| Client readiness | As a trainer, I need quick readiness, soreness, or injury notes, so I can adapt the session safely. | Client card exposes current constraints and recent notes without opening a full profile. |
| Assessments | As a trainer, I need baseline movement or performance assessments, so progress is not only set volume. | Client profile supports benchmark entries such as squat pattern, mobility, bodyweight, or test lifts. |
| Program editing | As a trainer, I need to edit an existing program, so progression can happen week to week. | Program editor supports reorder, load, reps, rest, notes, and save. |
| Progression suggestions | As a trainer, I need to see whether a client is ready to progress, so planning is easier. | App calculates trend signals from completed sets and volume without pretending to be medical advice. |
| Follow-up notes | As a trainer, I need post-session notes ready to send, so clients remember the next focus. | Summary can produce a concise trainer-written follow-up. |
| Attendance history | As a trainer, I need to know consistency, no-shows, and missed sessions, so retention issues are visible. | Client profile shows attendance/adherence over time. |
| Exercise library quality | As a trainer, I need exercises to include equipment and coaching notes, so program building is fast. | Exercise list has category, equipment, difficulty, and optional coaching cues. |
| Mobile floor use | As a trainer, I need the UI to work on a phone or tablet during sessions, so buttons cannot be tiny or hidden. | Cockpit and setup have stable controls, no overlap, and thumb-friendly primary actions. |
| Exportable proof | As a trainer, I need progress screenshots or reports, so clients and recruiters can see outcomes. | Client profile can show clean progress summaries without raw admin clutter. |

### P2: Future Business Platform

These are real trainer needs, but they are not necessary for the current portfolio loop.

| Area | User story | Why later |
| --- | --- | --- |
| Payments and packages | As a trainer, I need to track packages, invoices, and overdue payments, so the business is sustainable. | Valuable but shifts the app toward billing/SaaS admin. |
| Calendar sync | As a trainer, I need Google/Outlook calendar sync and reminders, so clients do not miss sessions. | Requires external integrations and auth complexity. |
| Client portal | As a client, I need to see assigned work and notes, so I can train between sessions. | Important, but current signature is trainer-side realtime coaching. |
| Messaging | As a trainer, I need check-ins and async communication, so clients stay accountable. | Can become noisy unless tied to summaries and adherence. |
| Wearable import | As a trainer, I need wearable or app data, so readiness and progress include more context. | Useful but needs careful data permissions and scope. |
| Nutrition basics | As a trainer, I need goals and simple compliance notes, so weight-loss clients have context. | Avoid medical/dietitian scope and avoid overpromising. |
| Team management | As a studio owner, I need multiple trainers, permissions, and handoffs. | Strong later enterprise story, not needed for a solo demo. |
| AI assistant | As a trainer, I need drafting help, not generic auto-programming. | Only add after business rules, validation, and edit-first UX exist. |

## Session Types To Support

| Type | Client count | Trainer need | FitCoach implication |
| --- | ---: | --- | --- |
| Assessment | 1 | Baseline notes, tests, movement constraints. | Add assessment history later. |
| Solo strength | 1 | Detailed load progression and notes. | Current cockpit supports this. |
| Duo session | 2 | Two programs visible without switching tabs. | Current cockpit supports this. |
| Semi-private group | 3-4 | Stable slots, quick status scanning. | Current cockpit signature. |
| Conditioning circuit | 1-10 | Timers, rounds, simple completion states. | Needs richer circuit mode later. |
| Recovery or mobility | 1-10 | Lower load, quality notes, pain/readiness flags. | Core/stability variant covers v1 basics. |
| Remote check-in | 1 | Adherence, notes, async update. | Future client portal/check-in feature. |

## UX Principles From The Trainer Agent

- The app should feel like attendance -> focus -> coach -> summarize -> progress.
- The trainer should never configure four repeated forms before starting.
- Primary actions must be usable while standing on a gym floor.
- Client context should be close to the action, but not clutter the live screen.
- History must be useful at the next session, not just saved for the database.
- Empty states must explain the next action in one sentence.
- Demo data must look like a real roster, not four hardcoded showcase clients.
- Avoid AI slop: no auto-generated workouts unless the trainer can inspect, edit, and validate every rule.

## Review Checklist

Before accepting a product change, ask:

1. Which trainer story does this serve?
2. Does it reduce floor-time friction or add setup work?
3. Can the trainer recover from no-shows, substitutions, and solo sessions?
4. Does the state after a click visibly change?
5. Does the client history become more useful next week?
6. Does the UI work on desktop and mobile without text clipping?
7. Is this core coaching value, or future business admin?

## Current FitCoach Gaps The Agent Should Watch

1. Program editor needs to become as polished as session setup.
2. Dashboard needs stronger "today's schedule" once sessions can be scheduled.
3. Client profile should show readiness/constraints and benchmark history.
4. Analytics need richer demo history across multiple dates.
5. Cockpit needs a clearer distinction between strength sets and circuit/timer work.
6. Mobile cockpit and setup need repeated visual QA after every layout change.
