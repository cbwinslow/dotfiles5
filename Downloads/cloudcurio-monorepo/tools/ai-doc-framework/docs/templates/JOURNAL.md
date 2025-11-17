# JOURNAL — {PROJECT_OR_AGENT_NAME}

> **Type:** {Agent | Project}  
> **Owner:** cbwinslow  
> **Last Updated:** 2025-11-16

---

## 0. How to Use This Document

This is your **development and operations journal**.

- It ties together:
  - Environment & intake snapshots (opening balance sheet),
  - Tasks and tickets (income/cash flows),
  - Updated SRS/FEATURES (new balance sheet).
- Every meaningful work session gets an entry.
- AI agents may append entries but should:
  - Identify themselves,
  - Reference TASK-### / FEAT-### / Linear IDs,
  - Keep it factual and professional.

---

## 1. Example Entry

### 2025-11-16 — Initial Setup

**Goals**

- Bootstrap documentation templates for {PROJECT_OR_AGENT_NAME}.  
- Capture environment and project snapshots.  
- Wire this repo into Linear using the provided templates.

**Actions**

- [x] Copied `SRS.md`, `FEATURES.md`, `PROJECT_SUMMARY.md`, `TASKS.md`, `JOURNAL.md` into `docs/`.  
  - Related: `TASK-001`, `FEAT-001`.  
- [x] Ran:
  - `env_snapshot.py --output snapshots/env_snapshot.json`  
  - `project_intake_audit.py --root . --output snapshots/project_intake_report.md`  
  - Related: `TASK-002`, `FEAT-001`.  
- [ ] Started filling out `SRS.md` and `PROJECT_SUMMARY.md`. (`TASK-003`)

**Problems / Blockers**

- Need a finalized list of MCP servers and tools to support. (`TASK-010`)  
- Some hardware detection depends on specific drivers.

**Decisions**

- `snapshots/` at repo root will hold snapshot artifacts.  
- `JOURNAL.md` is the canonical narrative log.

**Next Steps**

- Finish SRS core sections. (`TASK-003`)  
- Define MCP/tool bootstrap plan and document it. (`TASK-010`)  

---

## 2. Daily Entries

Copy and adapt the structure above for each working session.

### {YYYY-MM-DD} — {Short label}

**Goals**

- ...

**Actions**

- ...

**Problems / Blockers**

- ...

**Decisions**

- ...

**Next Steps**

- ...

---

**Related Documents**

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)  
- [SRS.md](SRS.md)  
- [FEATURES.md](FEATURES.md)  
- [TASKS.md](TASKS.md)  
