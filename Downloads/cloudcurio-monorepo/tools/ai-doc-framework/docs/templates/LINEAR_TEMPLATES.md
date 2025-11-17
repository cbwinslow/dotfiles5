# LINEAR_TEMPLATES — Doc & Workflow Patterns

Use these as copy-paste bodies for Linear epics and tasks.

---

## 1. Epic — Doc Pack & Env Snapshot

**Title**

> [DOC] Bootstrap doc pack & environment snapshot for {{PROJECT_OR_AGENT_NAME}}

**Description (Markdown)**

```markdown
## Summary

Set up the standardized documentation and environment snapshots for **{{PROJECT_OR_AGENT_NAME}}**.

## Goals

- Copy and customize:
  - `PROJECT_SUMMARY.md`
  - `SRS.md`
  - `FEATURES.md`
  - `TASKS.md`
  - `JOURNAL.md`
- Generate opening environment & project snapshots.
- Link everything together for AI agents and humans.

## Checklist

- [ ] Copy doc templates from the framework bundle into the repo under `docs/`.
- [ ] Replace placeholders (`{{PROJECT_OR_AGENT_NAME}}`, `{{REPO_URL}}`).
- [ ] Add links to these docs from the repo `README.md`.
- [ ] Run:
  - `python scripts/env_snapshot.py --output snapshots/env_snapshot.json`
  - `python scripts/project_intake_audit.py --root . --output snapshots/project_intake_report.md`
- [ ] Link snapshot outputs in `PROJECT_SUMMARY.md` and `JOURNAL.md`.
- [ ] Create at least one initial `JOURNAL.md` entry describing this setup.
```

---

## 2. Task — Daily Journal Entry

**Title**

> [JOURNAL] Daily entry for {{YYYY-MM-DD}} — {{PROJECT_OR_AGENT_NAME}}

**Description (Markdown)**

```markdown
## Objective

Record today's work for **{{PROJECT_OR_AGENT_NAME}}** in `JOURNAL.md`.

## Checklist

- [ ] Add a new section in `JOURNAL.md` for `{{YYYY-MM-DD}}`.
- [ ] Fill in:
  - Goals,
  - Actions (with TASK-### / FEAT-### / Linear ticket references),
  - Problems / blockers,
  - Decisions,
  - Next steps.
- [ ] Commit updated `JOURNAL.md` with a descriptive message.
```

---

## 3. Task — Reconcile SRS / FEATURES / TASKS

**Title**

> [RECONCILE] Align SRS, FEATURES, TASKS for {{PROJECT_OR_AGENT_NAME}}

**Description (Markdown)**

```markdown
## Objective

Ensure `SRS.md`, `FEATURES.md`, and `TASKS.md` are aligned and consistent.

## Checklist

- [ ] Review implemented features vs. `FEATURES.md`.
- [ ] Update `FEATURES.md` statuses and notes.
- [ ] Confirm each feature maps to at least one requirement in `SRS.md` (FR-###).
- [ ] Confirm each feature and FR-### has at least one task (TASK-###) linked.
- [ ] Add a brief summary of reconciled changes to `JOURNAL.md`.
```

---

## 4. Task — MCP / Tools Bootstrap

**Title**

> [MCP] Bootstrap tools & MCP servers for {{PROJECT_OR_AGENT_NAME}}

**Description (Markdown)**

```markdown
## Objective

Set up and document all MCP servers and tools required for **{{PROJECT_OR_AGENT_NAME}}**.

## Checklist

- [ ] Enumerate all required MCP servers and tools.
- [ ] For each:
  - [ ] Installation / deployment steps.
  - [ ] Configuration (endpoints, tokens via Bitwarden, env vars).
  - [ ] Safety constraints and rate limits.
- [ ] Document the bootstrap procedure in:
  - `SRS.md` (Interfaces & Integrations section),
  - `PROJECT_SUMMARY.md` (Getting Started),
  - `JOURNAL.md` (entry describing first setup).
- [ ] Validate that AI agents can connect to and use these tools.
```

---

You can extend this file with templates for:

- Incident reports,
- Refactor epics,
- Infra changes,
- Multi-agent experiments.
