# Features – Gemini DevOps Assistant

> This file lists user-visible features and capabilities for the project.
> Features should map to user value and link back to tasks.

## Feature F-001 – Safe Deployments

- **Status:** In Progress
- **Owner:** Dev Agent
- **Priority:** P0
- **Description:** Allow users to trigger application deployments with guardrails.
- **User Story:** "As a DevOps engineer, I want to deploy safely with AI assistance so that I can avoid mistakes and rollbacks become easy."
- **Non-functional Requirements:**
  - Deployment actions must be auditable via `JOURNAL_{SESSION_ID}.md`.
  - All destructive actions must require explicit confirmation.
- **Dependencies:**
  - CI/CD pipeline
  - Cloud provider credentials
- **Linked Tasks:**
  - T-001, T-002, T-003

---

## Feature F-002 – Intelligent Rollbacks

- **Status:** Planned
- **Owner:** Dev Agent
- **Priority:** P1
- **Description:** Automatically propose rollback strategies when health checks fail.
- **User Story:** "As an SRE, I want suggested rollbacks so I can quickly restore service."
- **Non-functional Requirements:**
  - Must run health checks before and after rollback.
  - Rollback operations must be fully logged.
- **Dependencies:**
  - Monitoring/health-check APIs
- **Linked Tasks:**
  - T-010, T-011

---

## Feature F-003 – Journal & Error Dashboard

- **Status:** Planned
- **Owner:** Docs Agent
- **Priority:** P2
- **Description:** Web UI to visualize journals, error logs, and recent activity.
- **User Story:** "As a team lead, I want a dashboard for AI activity so I can review what Gemini has done."
- **Dependencies:**
  - HTTP server
  - Access to `.gemini/` directory
- **Linked Tasks:**
  - T-020, T-021
