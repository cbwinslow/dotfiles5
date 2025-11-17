# FEATURES — {PROJECT_OR_AGENT_NAME}

> **Type:** {Agent | Project}  
> **Owner:** cbwinslow  
> **Last Updated:** 2025-11-16

---

## 0. How to Use This Document

- Treat **FEATURES.md** as a **catalog of line items** on the future balance sheet.
- Each feature has:
  - A stable ID (`FEAT-###`),
  - Status,
  - Priority,
  - Owner,
  - Mapping to one or more requirements (`FR-###`) in `SRS.md`,
  - Links to tasks (`TASK-###`) and Linear issues.

Keep this synced with:

- Implemented code,
- SRS functional requirements,
- TASKS and Linear.

---

## 1. Feature Table

| ID       | Name                             | Status | Priority | Owner     | SRS Ref        | Tasks / Linear IDs | Notes |
|----------|----------------------------------|--------|----------|-----------|----------------|--------------------|-------|
| FEAT-001 | Doc pack & env snapshot          | 🟢     | High     | cbwinslow | FR-001, FR-002 | TASK-001, TASK-002 |       |
| FEAT-002 | Agent/project intake & audit     | 🟢     | High     | cbwinslow | FR-010         | TASK-002           |       |
| FEAT-003 | MCP & tools bootstrap framework  | ⚪     | High     | cbwinslow | FR-030         | TASK-010           |       |
| FEAT-004 | Multi-agent collaboration hooks  | ⚪     | Medium   | cbwinslow | FR-040         | TASK-020           |       |

Adjust IDs, priorities, and references per project.

---

## 2. Feature Details

### FEAT-001: Doc pack & env snapshot

- **Summary:**  
  Provide a reusable documentation pack (`SRS`, `FEATURES`, `PROJECT_SUMMARY`, `TASKS`, `JOURNAL`) plus snapshot scripts.
- **Motivation:**  
  Standardize how agents and projects are described and audited.
- **SRS References:** `FR-001`, `FR-002`, `NFR-001`, `NFR-002`.
- **Acceptance Criteria:**  
  - All templates exist and can be copied into a repo.
  - Snapshot scripts run cleanly on target environments.

---

### FEAT-002: Agent/project intake & audit

- **Summary:**  
  Analyze a project tree and produce structured metrics and a Markdown intake report.
- **Motivation:**  
  Help agents understand the size, language mix, and doc health of a repo.
- **SRS References:** `FR-010`, `NFR-003`.
- **Acceptance Criteria:**  
  - Report includes extension counts, LOC, docs present/missing, and qualitative complexity.
  - Report suggests next actions and strategy for LLM usage.

---

### FEAT-003: MCP & tools bootstrap framework

- **Summary:**  
  Provide a standard pattern for describing and initializing MCP servers and tools.
- **Motivation:**  
  Make “wire up an agent to tools” a repeatable operation across projects.
- **Acceptance Criteria:**  
  - At least one worked example describing MCP endpoints, auth, and safety.
  - Clear instructions in SRS and PROJECT_SUMMARY.

---

### FEAT-004: Multi-agent collaboration hooks

- **Summary:**  
  Define how multiple agents share docs, logs, and tasks without stepping on each other.
- **Motivation:**  
  Avoid chaotic behavior when several agents operate on the same repo.
- **Acceptance Criteria:**  
  - Naming conventions for doc updates and commit messages.
  - Journal pattern for recording which agent did what and when.

---

## 3. Parking Lot Features

Use this section for future upgrades:

- FEAT-100: Automatic doc/code reconciliation and drift detection.
- FEAT-101: Visualization layer (dashboards or TUIs) for requirements and progress.
- FEAT-102: Automatic Linear ticket generation from SRS / FEATURES deltas.

---

**Related Documents**

- [SRS.md](SRS.md)  
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)  
- [TASKS.md](TASKS.md)  
- [JOURNAL.md](JOURNAL.md)  
