# SRS – Gemini DevOps Assistant

## 1. Introduction

### 1.1 Purpose

This SRS defines the functional and non-functional requirements for the
Gemini DevOps Assistant, which uses the Gemini CLI constitution to safely
orchestrate DevOps tasks.

### 1.2 Scope

The system will:
- Provide safe, auditable deployment and rollback operations.
- Integrate with CI/CD, monitoring, and secret management.
- Maintain detailed journals and error logs for all actions.

### 1.3 Definitions, Acronyms, Abbreviations

- **Gemini** – AI-driven CLI assistant.
- **SRS** – Software Requirements Specification.
- **LLM** – Large Language Model.
- **CI/CD** – Continuous Integration / Continuous Deployment.

### 1.4 References

- `GEMINI.md` – Core constitution.
- `PROJECT_SUMMARY.md`
- `FEATURES.md`
- `TASKS.md`

---

## 2. Overall Description

### 2.1 Product Perspective

The assistant is a command-line tool that wraps existing DevOps automation
(scripts, CI/CD pipelines, cloud APIs) and adds AI-driven planning,
explanation, and journaling.

### 2.2 Product Functions

- Show system and deployment status.
- Propose and execute deployment plans safely.
- Detect failures and propose rollback plans.
- Maintain journals and error logs for every operation.

### 2.3 User Characteristics

- DevOps engineers and SREs.
- Comfortable with CLI tools and basic scripting.
- Expect clear explanations and auditability.

### 2.4 Constraints

- Must not perform destructive actions without explicit user confirmation.
- Must abide by security and secrets rules from `GEMINI.md`.
- Must run on Linux-based systems (e.g., Ubuntu, RHEL).

### 2.5 Assumptions & Dependencies

- CI/CD and monitoring are already in place.
- Secret manager or `.env` conventions exist.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

- **FR-1:** The system SHALL provide a `status` command that reports key
  service health indicators.
- **FR-2:** The system SHALL provide a `deploy` command that:
  - Generates a deployment plan.
  - Asks for explicit confirmation.
  - Logs all steps to the journal.
- **FR-3:** The system SHALL provide a `rollback` command that is
  available when a deployment fails.
- **FR-4:** The system SHALL maintain `TASKS.md` and `FEATURES.md`
  in sync with major work items.

### 3.2 Non-functional Requirements

- **NFR-1 (Performance):** Core CLI commands should respond within a few
  seconds, excluding external network calls.
- **NFR-2 (Security):** Secrets must never be logged in plaintext.
- **NFR-3 (Reliability):** Journals and logs must persist across sessions.

### 3.3 Interface Requirements

- CLI interface (`gemini` command).
- Configuration via `.env` and YAML config files.
- Optional HTTP endpoint for dashboards.

---

## 4. Data Requirements

- Journals, error logs, and config files live under `.gemini/`.
- Memory entries stored in SQLite + vector index.

---

## 5. Acceptance Criteria & Testing

- All FRs have automated tests where feasible.
- Destructive flows are covered by unit and integration tests.
- Manual checklist completed for first production deployment.
