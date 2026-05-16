# ADR 0003: Saved Training Groups

## Status

Accepted

## Context

Trainers often run recurring small-group formats such as strength, conditioning, or core sessions. Rebuilding the same roster and workout template before every live cockpit session makes the product feel like a form tool instead of a trainer workflow.

## Decision

Add trainer-owned saved training groups with ordered members and ordered exercise templates. Starting a group session supports the default full group, a confirmed attendance subset, roster substitutes, and per-client program overrides. Clients without an override receive a session snapshot copied from the saved group template, then those programs are attached to the live session.

## Consequences

- The cockpit can keep using the existing per-client program/session model.
- Trainers can manage reusable rosters and exercises without changing the realtime session state machine.
- Attendance and substitutions are represented as session-start payload choices, not as mutations to the saved group itself.
- Demo seed now includes curated saved groups for strength, endurance, and core workflows.
- Repeated group starts create snapshot programs; this is acceptable for the portfolio demo but should be filtered or modeled as immutable session plans in a later product pass.
