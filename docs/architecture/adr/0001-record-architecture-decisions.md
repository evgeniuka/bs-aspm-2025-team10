# ADR 0001: Record Architecture Decisions

## Status

Accepted

## Context

The project needs lightweight, durable records for decisions that affect architecture, operations, security, or long-term maintenance.

## Decision

Record meaningful decisions as ADRs in `docs/architecture/adr/`.

## Consequences

- Future humans and agents can understand why choices were made.
- ADRs should stay concise and link to SDD sections or implementation PRs when useful.
- New ADRs should be added for decisions that affect deployment, security, data model, realtime architecture, or public demo behavior.
