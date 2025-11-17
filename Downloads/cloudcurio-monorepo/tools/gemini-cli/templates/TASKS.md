# Tasks / TODO – Gemini DevOps Assistant

> This file is the authoritative task list for the project.

## 1. Global Tasks

- [ ] T-000 – Set up base repo structure with `GEMINI.md` and templates.
- [ ] T-001 – Implement `gemini status` CLI command.
- [ ] T-002 – Implement `gemini deploy` command (dry-run by default).
- [ ] T-003 – Wire deployment logs into `JOURNAL_{SESSION_ID}.md`.
- [ ] T-004 – Configure Bitwarden/secret manager integration.

## 2. By Feature

### Feature F-001 – Safe Deployments

- [ ] T-001 – Define deployment playbook and rollback strategy.
- [ ] T-002 – Implement CLI flow for user confirmation on destructive steps.
- [ ] T-003 – Add tests for aborted and successful deployments.

### Feature F-002 – Intelligent Rollbacks

- [ ] T-010 – Integrate health-check API calls.
- [ ] T-011 – Implement heuristic to propose rollback steps.

### Feature F-003 – Journal & Error Dashboard

- [ ] T-020 – Build read-only UI for journals (list + detail).
- [ ] T-021 – Add filtering by project, session, and severity.

## 3. Technical Debt

- [ ] TD-001 – Refactor CLI argument parsing into a shared module.
- [ ] TD-002 – Replace ad-hoc logging with a structured logger.

## 4. Completed Tasks (History)

- [x] T-INIT – Create Gemini constitution draft – Completed: 2025-11-14
