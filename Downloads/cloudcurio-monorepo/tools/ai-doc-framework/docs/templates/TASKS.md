# TASKS — {PROJECT_OR_AGENT_NAME}

> **Type:** {Agent | Project}  
> **Owner:** cbwinslow  
> **Last Updated:** 2025-11-16

---

## 0. How to Use This Document

This is the **text-based task ledger** that complements Linear.

- Treat it like the **income / cash flow statement**:
  - New tasks = new flows of work.
  - Completed tasks should reconcile with:
    - Code changes,
    - SRS/FEATURES updates,
    - JOURNAL entries.
- Each task has an ID (`TASK-###`) that can be referenced in:
  - Linear issues,
  - Commit messages,
  - `JOURNAL.md`,
  - Agent prompts.

---

## 1. Task Table

| ID       | Title                                  | Status      | Priority | Type    | Owner     | Features    | Linear ID | Notes |
|----------|----------------------------------------|-------------|----------|---------|-----------|------------|-----------|-------|
| TASK-001 | Copy doc templates into repo           | Done        | High     | Chore   | cbwinslow | FEAT-001   | LIN-XXX   |       |
| TASK-002 | Run env & project snapshot scripts     | Todo        | High     | Ops     | cbwinslow | FEAT-001   | LIN-XXX   |       |
| TASK-003 | Fill SRS for {PROJECT_OR_AGENT_NAME} | Todo        | High     | Docs    | cbwinslow | FEAT-001   | LIN-XXX   |       |
| TASK-010 | Define MCP & tool bootstrap plan       | Todo        | High     | Design  | cbwinslow | FEAT-003   | LIN-XXX   |       |

Edit/add rows as needed.

---

## 2. Task Descriptions

### TASK-001: Copy doc templates into repo

- **Summary:**  
  Install the framework docs into a specific repo or agent folder.
- **Steps:**  
  - [ ] Create `docs/` directory if missing.  
  - [ ] Copy templates from the framework bundle.  
  - [ ] Replace placeholders (`{PROJECT_OR_AGENT_NAME}`, `{REPO_URL}`).  
  - [ ] Link `PROJECT_SUMMARY.md` from the main `README.md`.

---

### TASK-002: Run env & project snapshot scripts

- **Summary:**  
  Capture initial environment and repository snapshot.
- **Steps:**  
  - [ ] `python scripts/env_snapshot.py --output snapshots/env_snapshot.json`  
  - [ ] `python scripts/project_intake_audit.py --root . --output snapshots/project_intake_report.md`  
  - [ ] Link files in `PROJECT_SUMMARY.md`.  
  - [ ] Add notes in `JOURNAL.md`.

---

### TASK-003: Fill SRS

- **Summary:**  
  Customize `SRS.md` for this specific project/agent.
- **Acceptance Criteria:**  
  - `FR-###` requirements listed and mapped to FEATURES.  
  - NFRs defined and realistic.  
  - Data & interfaces at least sketched.

---

### TASK-010: Define MCP & tool bootstrap plan

- **Summary:**  
  Decide which MCP servers, tools, and external services the agent/project will use.
- **Steps:**  
  - [ ] List tools and MCP endpoints.  
  - [ ] Document their configuration in `SRS.md` and `PROJECT_SUMMARY.md`.  
  - [ ] Capture setup procedure in `JOURNAL.md`.  

---

## 3. Backlog / Parking Lot

Use this to store unscheduled ideas.

- TASK-100: Automate sync between TASKS.md and Linear via API.
- TASK-101: Implement doc/code drift checker.
- TASK-102: Build TUI dashboard for requirements & agents.

---

## 4. Completed Task Archive

Move long-completed tasks here to keep the main table tight.

---

**Related Documents**

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)  
- [SRS.md](SRS.md)  
- [FEATURES.md](FEATURES.md)  
- [JOURNAL.md](JOURNAL.md)  
