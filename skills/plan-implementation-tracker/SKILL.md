---
name: plan-implementation-tracker
description: Track software implementation plans and execution status across iterations. Use when a user asks to create an implementation plan, execute phased work, report progress, update changelog/handoff artifacts, or keep a running checklist of completed vs pending work.
---

# Plan Implementation Tracker

Use this skill to keep execution aligned with a phased implementation plan.

## Workflow

1. Capture the requested objective and acceptance criteria.
2. Convert requested phases into a numbered checklist with clear deliverables.
3. Mark each item as `pending`, `in_progress`, or `completed` as work progresses.
4. Before edits, state which checklist items are being implemented.
5. After edits, validate implementation with available commands/tests.
6. Update delivery artifacts (`CHANGELOG.md`, `HANDOFF_REPORT.md`) at the end of each iteration.
7. Report residual risks, known limitations, and next recommended steps.

## Tracking Format

Keep a compact status table in working notes:

| Step | Status | Evidence |
|---|---|---|
| 1. Skeleton | completed | folders + `pyproject.toml` |
| 2. ADS client | in_progress | `ads/beckhoff_client.py` |
| 3. CLI wiring | pending | N/A |

Use short evidence pointing to files or commands only.

## Rules

- Keep scope consistent with user constraints (for example: read-only, on-demand).
- Do not silently skip requested deliverables; note any deviations explicitly.
- Prefer incremental, verifiable completion over speculative design.
- Append changelog entries; never rewrite prior history.
- Keep handoff report factual and implementation-focused.

