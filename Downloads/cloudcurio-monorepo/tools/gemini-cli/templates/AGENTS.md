# Agents & Roles – Gemini DevOps Assistant

> This file defines all AI agents, tools, and roles participating in the project.

## 1. Orchestrator Agent

- **Name:** Orchestrator
- **Role:** High-level planner & router for tasks.
- **Responsibilities:**
  - Interpret user prompts and map them to features and tasks.
  - Decide when to call Dev, Docs, Memory, or Security agents.
  - Maintain the project-level view in `TASKS.md` and `PROJECT_SUMMARY.md`.

## 2. Developer Agent

- **Name:** Dev Agent
- **Role:** Code generation, refactoring, and implementation.
- **Tools:** Editor APIs, test runner, formatter, linter.
- **Inputs:** `SRS.md`, `FEATURES.md`, `TASKS.md`.
- **Outputs:** Code changes, PRs, updated tasks.

## 3. Memory / Knowledge Agent

- **Name:** Memory Agent
- **Role:** Read/write from the memory database and journals.
- **Responsibilities:**
  - Store or update long-term knowledge after tasks complete.
  - Summarize journals for future reference.
  - De-duplicate and compact memory entries.

## 4. Security / Secrets Agent

- **Name:** Security Agent
- **Role:** Manage secrets & secure configuration.
- **Responsibilities:**
  - Interact with Bitwarden / secret manager APIs.
  - Validate `.env` permissions and paths.
  - Enforce the constitution’s secret management rules.

## 5. Documentation Agent

- **Name:** Docs Agent
- **Role:** Maintain docs such as `PROJECT_SUMMARY.md`, `SRS.md`, `FEATURES.md`.
- **Responsibilities:**
  - Keep docs in sync with the current implementation.
  - Generate usage examples and README updates.

## 6. Observability Agent (Optional)

- **Name:** Observability Agent
- **Role:** Integrate monitoring/metrics into Gemini workflows.
- **Responsibilities:**
  - Query monitoring systems.
  - Surface health checks and anomaly alerts.
  - Propose remediation tasks in `TASKS.md`.

## 7. Custom Agents

Additional agents can be introduced as needed, following the pattern above.
