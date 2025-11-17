# CloudCurio / OpenDiscourse — AI Doc & Snapshot Framework

This bundle is a **reusable, AI-friendly documentation and snapshot framework** for:

- Projects (apps, services, infra, experiments),
- AI coding agents (MCP-based, CLI-based, or other).

It is organized using a **financial statement analogy**:

- **Opening balance sheet**  
  - `env_snapshot.py` + `project_intake_audit.py` outputs.
- **Income / cash flows**  
  - `TASKS.md`, Linear issues, and `JOURNAL.md` entries.
- **Updated balance sheet**  
  - `SRS.md` + `FEATURES.md` describing the target and current state.

---

## Included Docs

- `SRS.md` — Requirements and constraints (future state).
- `FEATURES.md` — Feature catalog with IDs, statuses, and mappings to SRS and tasks.
- `PROJECT_SUMMARY.md` — High-level overview and entry point.
- `TASKS.md` — Text-based task ledger.
- `JOURNAL.md` — Chronological log for humans and AI agents.
- `LINEAR_TEMPLATES.md` — Copy-paste templates for Linear epics and tasks.

---

## Included Scripts

- `scripts/env_snapshot.py`
  - Captures OS, CPU, memory, disk, GPU (if any), and Python package preview.
  - Output: JSON snapshot (opening balance sheet of environment).

- `scripts/project_intake_audit.py`
  - Walks a codebase, counts files, approximates LOC, and checks for key docs.
  - Output: Markdown report summarizing size, docs, and suggested next steps.

Both are read-only and safe to run; they favor logging over crashing.

---

## Recommended Initial Workflow

For each new project or agent:

1. **Install Docs**

   - Copy templates from `docs/templates/` into your repo (e.g., `docs/`).
   - Replace `{PROJECT_OR_AGENT_NAME}` and `{REPO_URL}`.
   - Link `PROJECT_SUMMARY.md` from your main `README.md`.

2. **Run Snapshots**

   ```bash
   mkdir -p snapshots
   python3 scripts/env_snapshot.py --output snapshots/env_snapshot.json
   python3 scripts/project_intake_audit.py --root . --output snapshots/project_intake_report.md
   ```

   - Link results in `PROJECT_SUMMARY.md`.
   - Reference them in `JOURNAL.md`.

3. **Wire into Linear**

   - Create an epic using the template in `LINEAR_TEMPLATES.md`.
   - Add tasks for daily journaling, reconciling docs, and MCP bootstrap.

4. **Daily Rhythm**

   - For every working session:
     - Add a `JOURNAL.md` entry,
     - Update `TASKS.md` and Linear,
     - Adjust `FEATURES.md` and SRS when scope or behavior changes.

---

## Realistic Future Enhancements

These are **worth doing** and not just filler:

1. **TOOLS / MCP Specification**
   - Add a `TOOLS_AND_MCP.md` or expand SRS to fully describe agent tools and MCP endpoints.
   - Include installation, configuration, safety, and rate limits.

2. **Doc–Code Drift Checker**
   - A helper CLI that scans docs and code to highlight inconsistencies.
   - Optionally opens Linear tickets automatically.

3. **Visualization & TUI**
   - A Bubbletea or Textual UI that shows:
     - Requirements vs. tasks,
     - Journals, snapshots, and agent runs,
     - Status across multiple projects/agents.

---

Use this framework as the **standard kit** for every agent and project in CloudCurio / OpenDiscourse.

Author: cbwinslow + AI assistant  
Generated: 2025-11-16
