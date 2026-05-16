# ADR 0004: Quality Gates And CI

## Status

Accepted

## Context

FitCoach Pro 2.0 is maintained as a portfolio-grade full-stack product with project-specific review agents, SDD docs, and architecture records. The project already had backend and frontend CI, but the complete trainer journey and agent contract were not enforced by a single quality gate.

## Decision

Adopt a layered quality gate:

- Keep product and review expectations in `docs/FITCOACH_*_AGENT.md`.
- Keep the executable local gate in `scripts/quality-gate.ps1`.
- Keep active CI in `.github/workflows/ci.yml` with contract, backend, frontend, and e2e jobs.
- Keep PR evidence in `.github/pull_request_template.md`.
- Keep the full gate definition in `docs/QUALITY_GATE.md`.

Security and supply-chain checks remain documented and templated until tuned for low-noise CI enforcement.

## Consequences

- Every non-trivial change has a clear path from product intent to automated checks.
- The live session journey is covered by active e2e CI instead of remaining a manual-only confidence check.
- PRs now carry explicit evidence for agent review, SDD/ADR impact, tests, risks, and screenshots.
- CI runtime increases because Playwright e2e runs as a dedicated job.

## Rollback

If e2e becomes too slow or flaky, keep backend/frontend/contract jobs active and move the e2e job back to `.codex/templates/github-ci.yml` until the instability is fixed.
