# FitCoach Agent Roster

This file is the operating map for FitCoach Pro 2.0 review agents. Use it before large UI, product, or testing changes.

## Why These Agents Exist

FitCoach Pro should be judged from several real-world angles:

1. Does a trainer actually need this?
2. Can a trainer use it quickly during a session?
3. Does the UI look professional and intentional?
4. Does the flow survive real user behavior and API failures?
5. Does the portfolio make a hiring reviewer trust the engineering?

No single agent should own all of those questions.

## Agent Files

| Agent | File | Role |
| --- | --- | --- |
| Trainer Stories Agent | `docs/FITCOACH_TRAINER_STORIES_AGENT.md` | Domain truth: real trainer jobs, session types, and feature priority. |
| UX Designer Agent | `docs/FITCOACH_UX_DESIGNER_AGENT.md` | Interface quality: hierarchy, layout, flow, accessibility, visual polish. |
| Product Reality Agent | `docs/FITCOACH_PRODUCT_REALITY_AGENT.md` | Market and business realism: whether the feature fits a believable trainer product. |
| Test Pilot Agent | `docs/FITCOACH_TEST_PILOT_AGENT.md` | Manual, automated, and failure-mode testing with real workflows. |
| Portfolio Reviewer Agent | `docs/FITCOACH_PORTFOLIO_REVIEWER_AGENT.md` | Recruiter/hiring-manager view: demo clarity, code quality signals, README, deploy story. |
| Functional QA Agent | `docs/FITCOACH_FUNCTIONAL_QA_AGENT.md` | Final capability matrix and regression checklist. |

## Recommended Review Order

For a feature idea:

1. Trainer Stories Agent: should this exist?
2. Product Reality Agent: does this match the real market and product scope?
3. UX Designer Agent: what should the user experience feel like?
4. Test Pilot Agent: how will this break?
5. Functional QA Agent: what commands and acceptance checks prove it works?
6. Portfolio Reviewer Agent: does this make the project stronger for hiring?

For a bug or broken flow:

1. Test Pilot Agent.
2. Functional QA Agent.
3. UX Designer Agent if the issue is confusing state, layout, or interaction.

For UI redesign:

1. Trainer Stories Agent.
2. UX Designer Agent.
3. Test Pilot Agent.
4. Portfolio Reviewer Agent.

For roadmap cleanup:

1. Trainer Stories Agent.
2. Product Reality Agent.
3. Portfolio Reviewer Agent.

## Agent Rules

- Agents should disagree when needed. A feature can be useful to trainers but too large for the current portfolio scope.
- Prefer concrete acceptance criteria over vague taste.
- Every UI recommendation must connect to a user story or a product risk.
- Every test recommendation must map to a route, API endpoint, or user journey.
- Avoid AI features unless the Trainer Stories Agent and Product Reality Agent both say the workflow is validated.
- Keep FitCoach Pro focused on the trainer-side loop: roster -> program -> live session -> summary -> client history.
