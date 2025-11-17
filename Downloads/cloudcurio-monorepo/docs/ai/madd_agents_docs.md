# PROJECT_SUMMARY.md

## Project Name
Multi-Agent Democratic Dev (MADD) — codename: **MADD-Agents**

## One-Liner
A multi-agent, decentralized, democratic, self-healing system for software development that uses strongly-typed project docs (SRS, TASKS, FEATURES, etc.) and layered memories to minimize hallucinations and task drift.

## Problem Statement
LLM-based agents are powerful but:
- Drift from the original task.
- Hallucinate APIs, files, or behaviors.
- Lose track of long-term goals and constraints.
- Don’t cross-check each other by default.

We want an architecture where:
- Agents **collaboratively** develop software from a rigorous spec.
- Long-term and short-term memory are explicitly modeled.
- Agents **review each other’s work** and **vote** on actions.
- The system can **self-heal** by:
  - Detecting drift, hallucinations, or repeated failure patterns.
  - Updating prompts, rules, and tasks automatically.

## High-Level Approach
1. Define a **typed documentation backbone**:
   - `SRS.md`, `FEATURES.md`, `TASKS.md`, `AGENTS.md`, `DEVELOPMENT.md`, etc.
2. Define a set of **agent roles**:
   - Architect, Planner, Coder, Reviewer, QA, Spec Guardian, Traceability Enforcer, Democracy Coordinator.
3. Implement **coordination patterns**:
   - Autoregressive review chains.
   - Democratic voting on proposals.
   - Critic–Defender loops.
   - Rule- and spec-based gating of all actions.
4. Run **experiments** comparing:
   - Single-agent vs multi-agent.
   - No-guardian vs Spec Guardian.
   - No-traceability vs enforced traceability.

## Outcomes
- A reusable architecture + set of documents that:
  - Can be applied to *any* software project.
  - Reduces hallucinations & task drift.
  - Produces higher-quality, well-documented code.

---

# SRS.md — Multi-Agent Democratic Dev System (MADD)

## 1. Introduction

### 1.1 Purpose
Define the functional and non-functional requirements for MADD, a multi-agent software development system with:
- Democratic decision-making.
- Self-healing long/short-term memory.
- Strongly typed documentation and traceability.

### 1.2 Scope
MADD will:
- Ingest a high-level problem description.
- Generate and maintain project documents (`SRS.md`, `TASKS.md`, etc.).
- Use multiple agents to:
  - Plan work.
  - Write code.
  - Review code.
  - Enforce constraints.
- Provide a machine-readable representation of project state so other tools (CI, dashboards, etc.) can integrate.

### 1.3 Definitions
- **Agent**: An LLM-powered process with a defined role and policy.
- **Long-Term Memory (LTM)**: Stable project artifacts:
  - SRS, FEATURES, AGENTS, DEVELOPMENT, DEPLOYMENT, USAGE, CONTRIBUTING.
- **Short-Term Memory (STM)**: Context for the current task:
  - Current TASKS slice, recent messages, current diff, relevant sections of SRS.
- **Rule / Hard Constraint**: A non-negotiable requirement (e.g., “Must not expose secrets”, “Language = Python for backend”).
- **Self-Healing**: The system detects failures (task drift, hallucinations, repeated errors) and:
  - Updates prompts.
  - Adds new rules.
  - Adjusts task decomposition.

---

## 2. Overall Description

### 2.1 Product Perspective
MADD is a meta-system:
- It sits above traditional dev tools (git, CI, editors).
- It orchestrates LLM/agents to operate in iterative “sprints” or “cycles”.

### 2.2 User Classes
- **Project Owner**: Defines high-level goals and approves major changes.
- **Developer** (human): Can intervene, adjust docs, or override decisions.
- **Observer**: May read generated artifacts, but cannot modify.

### 2.3 Operating Environment
- CLI-based orchestration (Python/TypeScript).
- Agents running via API (e.g., OpenAI, OpenRouter, local models).
- Git repository with markdown docs and code.

---

## 3. Functional Requirements

### FR-1: Document Backbone
- FR-1.1: System must maintain:
  - `PROJECT_SUMMARY.md`
  - `SRS.md`
  - `FEATURES.md`
  - `TASKS.md`
  - `AGENTS.md`
  - `THOUGHTS.md`
  - `DEVELOPMENT.md`
  - `DEPLOYMENT.md`
  - `USAGE.md`
  - `CONTRIBUTING.md`
- FR-1.2: Documents must be updated by agents **only** through a controlled workflow:
  - Proposal → Review → Approval (via democratic or guardian process).

### FR-2: Agent Roles & Registry
- FR-2.1: System must maintain a registry of agent roles in `AGENTS.md`.
- FR-2.2: Each role includes:
  - Name, description, responsibilities.
  - Allowed actions (e.g., “edit code”, “edit SRS”, “comment-only”).
  - Memory access (LTM/STM subsets).

### FR-3: Task Management
- FR-3.1: Tasks must be tracked in `TASKS.md` with:
  - Task ID, title, description, status, assigned agent(s), dependencies, links to SRS/FEATURES.
- FR-3.2: Agents cannot modify code without referencing a Task ID.

### FR-4: Coordination Patterns
- FR-4.1: The system must support **Autoregressive Review Chain**:
  - At least two distinct agents in sequence (Producer → Reviewer).
- FR-4.2: The system must support **Democratic Voting**:
  - At least three agents producing proposals for non-trivial tasks.
- FR-4.3: The system must support a **Critic–Defender loop** for high-risk changes.
- FR-4.4: The system must support a **Spec Guardian** agent that:
  - Can veto actions violating SRS or RULES.
- FR-4.5: The system must support a **Traceability Enforcer** that:
  - Ensures each change references `Task ID` + `SRS section`.

### FR-5: Memory Handling
- FR-5.1: Long-Term Memory (LTM) must be stored in version-controlled documents.
- FR-5.2: Short-Term Memory (STM) must be dynamically assembled per task:
  - Relevant SRS sections, TASK entries, prior diffs, and agent notes.
- FR-5.3: Self-Healing:
  - FR-5.3.1: On repeated failure or hallucination, system must:
    - Create a “Memory Patch” note in `THOUGHTS.md`.
    - Optionally add a new rule to `AGENTS.md` or SRS.

### FR-6: Experiment Mode
- FR-6.1: System must support running “experiments”:
  - E.g., Single-agent vs MADD agents on the same task.
- FR-6.2: For each experiment, record:
  - Setup, agents, configuration, metrics (success, errors, drift, tokens).

---

## 4. Non-Functional Requirements

### NFR-1: Traceability
Every code change must be traceable to:
- SRS Section(s)
- Feature ID(s)
- Task ID(s)
- Responsible agent(s)

### NFR-2: Transparency
All agent communications and decisions should be logged in a human-readable format (e.g., `logs/` or `THOUGHTS.md` references).

### NFR-3: Extensibility
It should be possible to:
- Add new agent roles.
- Plug in different LLM providers.
- Swap out coordination strategies (chain, voting, etc.).

### NFR-4: Safety
- No direct write access to production until:
  - At least one Reviewer agent and one Spec Guardian approve.

---

## 5. Rules & Constraints

### R-1: No Silent Scope Changes
- Agents may not expand or shrink scope without:
  - Updating SRS and TASKS.
  - Getting Spec Guardian approval.

### R-2: No Ungrounded Claims in Final Artifacts
- Any claim about external APIs, file paths, or behavior must be:
  - Backed by an existing artifact, or
  - Explicitly tagged as an "assumption" with rationale.

### R-3: Single Source of Truth
- SRS is the source of truth for requirements.
- TASKS must not contradict SRS.
- FEATURES must be consistent with SRS.

---

# FEATURES.md

## Core Feature Set

### F-1: Typed Documentation Backbone
- Strongly structured markdown for:
  - Requirements (SRS)
  - Tasks (TASKS)
  - Features (this file)
  - Agents (AGENTS)
  - Dev & deployment workflows (DEVELOPMENT, DEPLOYMENT)
  - Usage and contributing (USAGE, CONTRIBUTING)
  - Design log / meta-thoughts (THOUGHTS)

### F-2: Agent Role System
- Configurable roles:
  - Architect, Planner, Coder, Reviewer, QA, Spec Guardian, Traceability Enforcer, Democracy Coordinator.
- Role capabilities:
  - Read/Write access to docs, code, and logs.
  - Role-specific prompts and policies.

### F-3: Multi-Agent Coordination Patterns
- Autoregressive Review Chains.
- Democratic voting with:
  - Score-based selection.
  - Confidence-based voting.
- Critic–Defender loops for adversarial testing.
- Market/auction-based task assignment (future).

### F-4: Long/Short-Term Memory Layers
- Long-term:
  - Version-controlled docs.
  - Stable rules and constraints.
- Short-term:
  - Slice of relevant context for each task.
  - Recent agent messages and diffs.

### F-5: Self-Healing Mechanisms
- Drift detection:
  - Compare outputs to SRS / TASKS.
- Hallucination detection:
  - Require evidence/citations or explicit “assumption” tags.
- Auto-prompt refinement:
  - Log failure patterns and update role prompts.
- Memory patches:
  - Append rules and lessons to `THOUGHTS.md` and `AGENTS.md`.

### F-6: Experiment Framework
- Run controlled experiments:
  - Single-agent vs multi-agent.
  - With vs without Spec Guardian.
  - With vs without voting.
- Collect metrics:
  - Spec violations.
  - Time/tokens to completion.
  - Number of iterations.

### F-7: Integration Hooks (Future)
- Git integration (branches, PRs).
- CI integration (tests, lint).
- Visualization (simple dashboard over docs).

---

# AGENTS.md

> Registry of agent roles and their responsibilities.

## Core Agent Roles

### 1. Architect Agent
- **Purpose**: Interpret high-level goals and maintain SRS + FEATURES.
- **Responsibilities**:
  - Decompose user goals into features and requirements.
  - Keep SRS internally consistent.
  - Approve major scope changes.
- **Can edit**:
  - PROJECT_SUMMARY, SRS, FEATURES, THOUGHTS.
- **Cannot edit**:
  - Production code directly.

---

### 2. Planner Agent
- **Purpose**: Turn features into concrete tasks.
- **Responsibilities**:
  - Maintain `TASKS.md`.
  - Assign tasks to roles or role groups.
  - Maintain dependencies and priorities.
- **Can edit**:
  - TASKS, THOUGHTS.
- **Cannot edit**:
  - SRS (except via proposals to Architect).

---

### 3. Coder Agent
- **Purpose**: Implement tasks in code.
- **Responsibilities**:
  - Take TASKS as input.
  - Propose code changes and diffs.
  - Document implementation details in DEVELOPMENT.
- **Can edit**:
  - Code files, DEVELOPMENT.
- **Requires**:
  - Task ID and SRS/Feature references for each change.

---

### 4. Reviewer Agent
- **Purpose**: Review code and doc changes.
- **Responsibilities**:
  - Validate that changes match SRS + TASKS.
  - Flag hallucinations / missing pieces.
  - Recommend corrections or reject changes.
- **Can edit**:
  - DEVELOPMENT, THOUGHTS (review notes).
- **Votes**:
  - Approve/Reject proposals.

---

### 5. QA Agent
- **Purpose**: Think in terms of tests, edge-cases, and robustness.
- **Responsibilities**:
  - Propose tests.
  - Evaluate expected vs actual behavior.
- **Can edit**:
  - DEVELOPMENT (test plan sections), THOUGHTS.

---

### 6. Spec Guardian Agent
- **Purpose**: Enforce long-term rules and SRS.
- **Responsibilities**:
  - Deny changes that conflict with:
    - SRS requirements.
    - Hard rules (e.g., security constraints).
  - Suggest corrections or necessary SRS updates.
- **Can edit**:
  - THOUGHTS (explanations), RULE sections in SRS.
- **Authority**:
  - Veto power for any proposed change.

---

### 7. Traceability Enforcer Agent
- **Purpose**: Maintain strict traceability.
- **Responsibilities**:
  - Ensure each change includes:
    - Task ID(s)
    - SRS section(s)
    - Feature ID(s)
  - Flag ungrounded assertions.
- **Can edit**:
  - THOUGHTS (traceability audits).
- **Output**:
  - “Traceability reports” per commit or iteration.

---

### 8. Democracy Coordinator Agent
- **Purpose**: Run democratic decision-making.
- **Responsibilities**:
  - Collect proposals from agents (Coder, Reviewer, QA, etc.).
  - Collect votes/confidence scores.
  - Choose winning proposal or merge top K.
- **Can edit**:
  - THOUGHTS (decision logs).

---

## Typed Role Schema (Conceptual)

```ts
type AgentRole = {
  name: string;
  description: string;
  allowedEdits: string[];    // markdown files / code scopes
  forbiddenEdits: string[];
  capabilities: string[];    // "plan", "code", "review", "vote", "veto"
  memoryAccess: {
    longTerm: string[];      // which docs
    shortTerm: string[];     // which context slices
  };
};
```

---

# TASKS.md

> Master task list. Each task should be traceable to SRS + FEATURE IDs.

## Legend
- Status:
  - TODO, IN_PROGRESS, BLOCKED, DONE, EXPERIMENT
- Priority:
  - P0 (critical), P1 (high), P2 (medium), P3 (nice-to-have)

---

## Phase 0 — Bootstrapping

### T-0001 — Define Agent Role Config Schema
- **Status**: TODO
- **Priority**: P0
- **Description**: Define a JSON/YAML schema for agent roles (fields: name, description, capabilities, memory access, etc.).
- **Owner**: Architect / Planner
- **Related**:
  - SRS: FR-2
  - Feature: F-2

### T-0002 — Implement Document Loader/Writer
- **Status**: TODO
- **Priority**: P0
- **Description**: Implement a module that loads and saves core markdown docs with structured sections.
- **Owner**: Coder
- **Related**:
  - SRS: FR-1
  - Feature: F-1

### T-0003 — Implement Autoregressive Review Chain
- **Status**: TODO
- **Priority**: P0
- **Description**: Implement a function that:
  - Sends a prompt to Producer agent.
  - Sends output to Reviewer agent.
  - Logs notes and produces a corrected proposal.
- **Owner**: Coder / Reviewer
- **Related**:
  - SRS: FR-4.1
  - Features: F-3, F-5

### T-0004 — Implement Democratic Voting Mechanism
- **Status**: TODO
- **Priority**: P1
- **Description**: Implement a function to:
  - Gather proposals from N agents.
  - Gather votes/confidences.
  - Pick/merge winning proposal.
- **Owner**: Coder / Democracy Coordinator
- **Related**:
  - SRS: FR-4.2
  - Feature: F-3

### T-0005 — Spec Guardian Rule Engine
- **Status**: TODO
- **Priority**: P1
- **Description**: Agent + rule engine that:
  - Reads SRS + RULES.
  - Evaluates proposals and can veto.
- **Owner**: Coder / Architect
- **Related**:
  - SRS: FR-4.4, FR-5.3
  - Features: F-4, F-5

### T-0006 — Traceability Enforcer Implementation
- **Status**: TODO
- **Priority**: P1
- **Description**: Implement the traceability checks that ensure each change references tasks and SRS sections.
- **Owner**: Coder / Traceability Enforcer
- **Related**:
  - SRS: NFR-1
  - Feature: F-5

---

## Phase 1 — Experimentation Framework

### T-0100 — Experiment Harness (Single vs Multi-Agent)
- **Status**: EXPERIMENT
- **Priority**: P1
- **Description**: Build a CLI or script to run:
  - Same coding task under:
    - Single-agent.
    - MADD agents (chain + voting + guardian).
  - Collect metrics and store in `THOUGHTS.md` or `experiments/`.
- **Owner**: Coder / QA
- **Related**:
  - SRS: FR-6
  - Feature: F-6

### T-0101 — Drift & Hallucination Metrics
- **Status**: TODO
- **Priority**: P2
- **Description**: Define how to measure:
  - Drift (distance from SRS/TASK).
  - Hallucination rate (claims without evidence).
- **Owner**: QA / Traceability Enforcer
- **Related**:
  - SRS: FR-5.3
  - Feature: F-5

### T-0102 — Memory Patch Mechanism
- **Status**: TODO
- **Priority**: P2
- **Description**: Implement a mechanism to append "lessons learned" and new rules into THOUGHTS and SRS based on repeated failures.
- **Owner**: Coder / Spec Guardian
- **Related**:
  - SRS: FR-5.3
  - Feature: F-5

---

# THOUGHTS.md

> Running design log, meta-comments, and lessons learned.

## 2025-11-13 — Initial Concept

- Goal: Use multiple agents with different roles to build software in a way that:
  - Minimizes hallucinations and task drift.
  - Makes all reasoning and changes traceable.
- Approach:
  - Start with a highly-structured set of markdown docs.
  - Treat those docs as the “long-term memory.”
  - Use STM slices per task.

Notes:
- Important to have an Agent whose job is “Do NOT be creative, only enforce rules.”
- Experiments will be critical:
  - Compare single-agent vs multi-agent on the same task.
- We should log *why* changes are made, not just *what*.

## 2025-11-13 — Improvements & Experiment Ideas

- Add rules and constraints explicitly in SRS to prevent scope creep.
- Add a Memory Patch subsystem to:
  - Detect repeated failure patterns.
  - Automatically update prompts and rules.
- For experiments, we should define:
  - Small, deterministic tasks for fast comparison.
  - Larger, messy tasks to stress-test drift.

Open Questions:
- How to implement reliable hallucination detection without external ground truth?
- How to weight agent votes (simple majority vs weighted by past performance)?

---

# DEVELOPMENT.md

> How we develop the MADD system itself.

## 1. Development Workflow

1. Define or update features in `FEATURES.md`.
2. Planner breaks features into tasks in `TASKS.md`.
3. Coder agents propose code changes for specific Task IDs.
4. Reviewer agents run:
   - Autoregressive review chain.
   - Critic–Defender loops (when configured).
5. Spec Guardian and Traceability Enforcer run checks:
   - Rules and SRS compliance.
   - Task/Feature references are present.
6. Democracy Coordinator:
   - If multiple proposals: runs voting and picks a winner.
7. Code is merged and linked back to tasks + SRS.

## 2. Code Structure (Planned)

- `src/`
  - `agents/`
    - `architect.ts`
    - `planner.ts`
    - `coder.ts`
    - `reviewer.ts`
    - `qa.ts`
    - `spec_guardian.ts`
    - `trace_enforcer.ts`
    - `democracy_coordinator.ts`
  - `memory/`
    - `long_term_loader.ts`     // read/write markdown docs
    - `short_term_builder.ts`   // context assembly
  - `coordination/`
    - `autoregressive_chain.ts`
    - `voting.ts`
    - `critic_defender.ts`
  - `experiments/`
    - `runner.ts`
    - `metrics.ts`
- `docs/`
  - The markdown files defined in this repo.

## 3. Experiments Setup

### Experiment 1 — Single vs Multi-Agent Implementation

- **Task**: Implement a small pure function, e.g., “Given a list of tasks, group by status and sort by priority.”
- **Conditions**:
  - C1: Single-agent (Coder only).
  - C2: Coder + Reviewer.
  - C3: Full chain:
    - Coder → Reviewer → Spec Guardian → Democracy (if multiple variants).
- **Metrics**:
  - Did the implementation fully match SRS?
  - Number of iterations.
  - Number of spec violations or hallucinated behaviors.
  - Tokens/time used.

### Experiment 2 — Drift Stress Test

- **Task**: “Create a module following X requirements.”
- **Scenarios**:
  - SRS is long and detailed.
  - Many similar but slightly different tasks.
- **Goal**:
  - Measure how often agents drift into adjacent tasks.
  - Compare with vs without Spec Guardian + Traceability Enforcer.

### Experiment 3 — Democratic Design Decision

- **Task**: “Choose a database layer design for a sample project.”
- **Process**:
  - Architect, Coder, QA each propose a design.
  - Democracy Coordinator runs a vote.
- **Goal**:
  - See if the chosen design better satisfies SRS compared to any single agent.

## 4. Testing

- Unit tests for:
  - Document parsing, role config, coordination logic.
- Integration tests:
  - Simulate entire “mini-sprints” with recorded prompts/responses.

---

# DEPLOYMENT.md

> How to deploy the MADD system (initial concept).

## 1. Environments

- **Local Dev**:
  - Run agents via CLI with a local config file.
- **Server Mode (Future)**:
  - Long-running orchestrator process.
  - Agents called via HTTP or message bus.

## 2. Dependencies (Conceptual)

- Runtime:
  - Node.js or Python (TBD).
- External:
  - LLM providers (e.g., OpenAI/OpenRouter/local models).
- Storage:
  - Git repo for code + docs.
  - (Optional) Vector DB for richer LTM.

## 3. Deployment Steps (First Iteration)

1. Clone repo.
2. Install dependencies.
3. Configure:
   - `agents.config.(json|yaml)`
   - `llm.config.(json|yaml)`
4. Run `experiments/runner` in local mode.
5. (Future) Deploy orchestrator as a service:
   - Systemd, Docker, or Kubernetes.

---

# USAGE.md

> How to run and interact with the system.

## 1. Basic Usage

1. Define your project in:
   - `PROJECT_SUMMARY.md`
   - `SRS.md`
   - `FEATURES.md`
2. Run the Planner to generate TASKS:
   - `madd planner --update-tasks`
3. Run a dev cycle:
   - `madd cycle --task T-0003 --agents coder,reviewer,spec_guardian`
4. Review the results:
   - Check `TASKS.md`, `DEVELOPMENT.md`, diffs, and `THOUGHTS.md`.

## 2. Experiment Mode

- Run predefined experiments:
  - `madd experiment --name single_vs_multi`
- Outputs:
  - Metrics, logs, and analysis.

---

# CONTRIBUTING.md

## 1. Philosophy

This project is about:
- Making AI development **transparent**.
- Treating LLMs as **collaborative agents** with clear roles.
- Reducing hallucinations and drift via **structured memory** and **checks & balances**.

## 2. Contribution Guidelines

- Keep all major changes traceable to:
  - SRS sections.
  - Feature IDs.
  - Task IDs.
- Update documentation alongside code.
- When adding new agents or patterns:
  - Document in `AGENTS.md` and `FEATURES.md`.
  - Add or update experiments in `DEVELOPMENT.md`.

## 3. Code Style & Testing

- Prefer small, composable modules.
- Add unit tests for new coordination or memory logic.
- Run experiments when appropriate and record results in `THOUGHTS.md`.

## 4. Experiment Proposals

If you propose a new experiment:
- Describe it in `DEVELOPMENT.md` under Experiments.
- Include:
  - Hypothesis.
  - Setup.
  - Metrics.
  - Expected outcomes (if any).

