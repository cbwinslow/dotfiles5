// Multi-Agent Democratic Orchestrator (TypeScript)
// -----------------------------------------------------------------------------
// This canvas document represents a full TypeScript project. Each fenced block
// is a file you can export into your filesystem.
// -----------------------------------------------------------------------------

```jsonc
// File: package.json
{
  "name": "multi-agent-orchestrator",
  "version": "0.2.0",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts",
    "lint": "echo 'add your linter here'"
  },
  "dependencies": {
    "@openrouter/sdk": "^0.3.0",
    "@google/generative-ai": "^0.21.0",
    "@google/adk": "^0.1.0",
    "langfuse": "^4.0.0",
    "@opentelemetry/sdk-node": "^0.54.0",
    "@opentelemetry/api": "^1.9.0",
    "prom-client": "^15.1.0",
    "pino": "^9.4.0",
    "zod": "^3.23.8",
    "@langchain/core": "^0.3.0",
    "@langchain/langgraph": "^0.1.0"
  },
  "devDependencies": {
    "typescript": "^5.6.3",
    "tsx": "^4.19.0"
  }
}
```

```jsonc
// File: tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "outDir": "dist",
    "rootDir": "src",
    "types": ["node"]
  },
  "include": ["src"]
}
```

```ts
// File: src/config/env.ts
// -----------------------------------------------------------------------------
// Script Name   : env.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Centralized, type-safe environment configuration loader.
// Inputs        : Process environment variables.
// Outputs       : Frozen EnvConfig object with validated configuration values.
// Modification Log:
//   2025-11-16 - Initial version for multi-agent orchestrator.
//   2025-11-16 - v0.2.0: Added more toggles for Gemini/ADK and LangGraph.
// -----------------------------------------------------------------------------

import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),

  OPENROUTER_API_KEY: z.string().min(1, "OPENROUTER_API_KEY is required"),
  OPENROUTER_APP_URL: z.string().optional(),
  OPENROUTER_APP_NAME: z.string().optional(),

  GOOGLE_API_KEY: z.string().optional(),

  LANGFUSE_SECRET_KEY: z.string().optional(),
  LANGFUSE_PUBLIC_KEY: z.string().optional(),
  LANGFUSE_BASE_URL: z.string().optional(),

  PROMETHEUS_PORT: z
    .string()
    .transform((v) => Number.parseInt(v, 10))
    .or(z.number())
    .default(9464),

  ORCHESTRATOR_DEFAULT_MODEL: z.string().optional(),

  // Feature flags so we can keep optional integrations safe.
  ENABLE_GEMINI: z.string().optional(),
  ENABLE_GOOGLE_ADK: z.string().optional(),
  ENABLE_LANGGRAPH: z.string().optional(),
});

export type EnvConfig = z.infer<typeof EnvSchema>;

let cachedEnv: Readonly<EnvConfig> | null = null;

export function getEnv(): Readonly<EnvConfig> {
  if (cachedEnv) return cachedEnv;

  const parsed = EnvSchema.safeParse(process.env);

  if (!parsed.success) {
    // eslint-disable-next-line no-console
    console.error("[env] Invalid environment configuration:", parsed.error.format());
    throw new Error("Invalid environment configuration. See logs for details.");
  }

  cachedEnv = Object.freeze(parsed.data);
  return cachedEnv;
}
```

```ts
// File: src/telemetry/logger.ts
// -----------------------------------------------------------------------------
// Script Name   : logger.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Pino-based structured logger with sane defaults.
// Inputs        : Log messages + contextual metadata.
// Outputs       : JSON logs to stdout, suitable for shipping to Loki/ELK/etc.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import pino from "pino";
import { getEnv } from "../config/env.js";

const env = getEnv();

export const logger = pino({
  level: env.NODE_ENV === "production" ? "info" : "debug",
  transport:
    env.NODE_ENV === "development"
      ? {
          target: "pino-pretty",
          options: {
            colorize: true,
            ignore: "pid,hostname",
          },
        }
      : undefined,
});

export type LogContext = Record<string, unknown>;

export function logAgentEvent(
  level: "debug" | "info" | "warn" | "error",
  msg: string,
  context: LogContext = {},
): void {
  logger[level]({ component: "agent", ...context }, msg);
}
```

```ts
// File: src/telemetry/metrics.ts
// -----------------------------------------------------------------------------
// Script Name   : metrics.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Prometheus metrics registry and HTTP /metrics exporter.
// Inputs        : Agent lifecycle events and timings.
// Outputs       : Prometheus metrics endpoint for scraping.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import http from "http";
import client from "prom-client";
import { getEnv } from "../config/env.js";
import { logger } from "./logger.js";

const env = getEnv();

client.collectDefaultMetrics();

export const agentRunCounter = new client.Counter({
  name: "agent_runs_total",
  help: "Total number of agent runs",
  labelNames: ["agent", "role"],
});

export const agentErrorCounter = new client.Counter({
  name: "agent_errors_total",
  help: "Total number of agent errors",
  labelNames: ["agent", "role", "error_type"],
});

export const agentLatencyHistogram = new client.Histogram({
  name: "agent_run_duration_seconds",
  help: "Latency of agent runs in seconds",
  labelNames: ["agent", "role"],
  buckets: [0.5, 1, 2, 5, 10, 30, 60],
});

export function startMetricsServer(): void {
  const server = http.createServer(async (_req, res) => {
    if (_req.url === "/metrics") {
      try {
        const metrics = await client.register.metrics();
        res.writeHead(200, { "Content-Type": client.register.contentType });
        res.end(metrics);
      } catch (err) {
        logger.error({ err }, "Error generating Prometheus metrics");
        res.writeHead(500);
        res.end("metrics_error");
      }
    } else {
      res.writeHead(404);
      res.end("not_found");
    }
  });

  server.listen(env.PROMETHEUS_PORT, () => {
    logger.info({ port: env.PROMETHEUS_PORT }, "Prometheus metrics server started");
  });
}
```

```ts
// File: src/telemetry/langfuse.ts
// -----------------------------------------------------------------------------
// Script Name   : langfuse.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Minimal Langfuse initialization + helper utilities for
//                 tracing agent runs and LLM calls.
// Inputs        : Trace/observation metadata from agents.
// Outputs       : Events sent to Langfuse for observability.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import { Langfuse } from "langfuse";
import { getEnv } from "../config/env.js";
import { logger } from "./logger.js";

const env = getEnv();

export const langfuse =
  env.LANGFUSE_SECRET_KEY && env.LANGFUSE_PUBLIC_KEY && env.LANGFUSE_BASE_URL
    ? new Langfuse({
        secretKey: env.LANGFUSE_SECRET_KEY,
        publicKey: env.LANGFUSE_PUBLIC_KEY,
        baseUrl: env.LANGFUSE_BASE_URL,
      })
    : null;

export interface TraceContext {
  traceName: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

export function startTrace(ctx: TraceContext) {
  if (!langfuse) {
    logger.debug({ traceName: ctx.traceName }, "Langfuse disabled; skipping trace start");
    return null;
  }

  return langfuse.trace({
    name: ctx.traceName,
    userId: ctx.userId,
    metadata: ctx.metadata,
  });
}

export async function flushLangfuse(): Promise<void> {
  if (!langfuse) return;
  try {
    await langfuse.shutdownAsync();
  } catch (err) {
    logger.warn({ err }, "Error flushing Langfuse");
  }
}
```

```ts
// File: src/llm/openrouterClient.ts
// -----------------------------------------------------------------------------
// Script Name   : openrouterClient.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Thin OpenRouter SDK wrapper with utilities to discover free
//                 models and perform chat completions.
// Inputs        : High-level prompt + messages from agents.
// Outputs       : LLM responses, plus metadata for logging/metrics.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import { OpenRouter } from "@openrouter/sdk";
import type { components } from "@openrouter/sdk/types.gen";
import { getEnv } from "../config/env.js";
import { logger } from "../telemetry/logger.js";

const env = getEnv();

export type OpenRouterModel = components["schemas"]["Model"];

const openRouter = new OpenRouter({
  apiKey: env.OPENROUTER_API_KEY,
  defaultHeaders: {
    "HTTP-Referer": env.OPENROUTER_APP_URL ?? "https://cloudcurio.cc",
    "X-Title": env.OPENROUTER_APP_NAME ?? "CloudCurio Multi-Agent Orchestrator",
  },
});

/**
 * Heuristic list of known free models on OpenRouter.
 * NOTE: This is intentionally conservative and should be refreshed periodically.
 */
const FREE_MODEL_ALLOWLIST: string[] = [
  "mistral/mistral-small-latest",
  "openai/gpt-4o-mini",
  "google/gemini-2.0-flash",
];

export async function listFreeModels(): Promise<OpenRouterModel[]> {
  const all = await openRouter.models.list();
  const models = all.data ?? [];

  const freeModels = models.filter((m) => {
    if (!m.id) return false;
    if (FREE_MODEL_ALLOWLIST.includes(m.id)) return true;

    const pricing = (m as any).pricing ?? undefined;
    if (!pricing) return false;

    const prompt = Number(pricing.prompt ?? 0);
    const completion = Number(pricing.completion ?? 0);
    const isFreeByPrice = prompt === 0 && completion === 0;

    return isFreeByPrice;
  });

  logger.info({ freeCount: freeModels.length }, "Discovered candidate free OpenRouter models");
  return freeModels;
}

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
}

export interface ChatResult {
  model: string;
  content: string;
  raw: unknown;
}

export async function chatWithOpenRouter(
  messages: ChatMessage[],
  options: ChatOptions = {},
): Promise<ChatResult> {
  const modelId = options.model ?? env.ORCHESTRATOR_DEFAULT_MODEL ?? FREE_MODEL_ALLOWLIST[0];

  logger.debug({ model: modelId }, "Calling OpenRouter chat.send");

  const res = await openRouter.chat.send({
    model: modelId,
    messages,
    temperature: options.temperature ?? 0.3,
    maxTokens: options.maxTokens ?? 2048,
    stream: false,
  });

  const choice = res.choices?.[0];
  const content = choice?.message?.content;

  if (!content || typeof content !== "string") {
    logger.warn({ model: modelId }, "Empty or non-string content from OpenRouter");
  }

  return {
    model: modelId,
    content: typeof content === "string" ? content : "",
    raw: res,
  };
}
```

```ts
// File: src/llm/geminiClient.ts
// -----------------------------------------------------------------------------
// Script Name   : geminiClient.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Optional Gemini client wrapper using @google/generative-ai.
//                 This module is fully optional and guarded by feature flags.
// Inputs        : Prompt text and messages.
// Outputs       : Text responses from Gemini when enabled.
// Modification Log:
//   2025-11-16 - Initial version (optional integration).
// -----------------------------------------------------------------------------

import { getEnv } from "../config/env.js";
import { logger } from "../telemetry/logger.js";

// We import lazily to avoid crashing if the SDK is missing.

export interface GeminiChatOptions {
  model?: string;
  temperature?: number;
}

export interface GeminiChatResult {
  model: string;
  content: string;
}

export async function chatWithGemini(
  prompt: string,
  options: GeminiChatOptions = {},
): Promise<GeminiChatResult | null> {
  const env = getEnv();

  if (!env.GOOGLE_API_KEY || env.ENABLE_GEMINI !== "1") {
    logger.debug("Gemini disabled or GOOGLE_API_KEY missing; skipping Gemini call");
    return null;
  }

  try {
    const { GoogleGenerativeAI } = await import("@google/generative-ai");
    const client = new GoogleGenerativeAI(env.GOOGLE_API_KEY);
    const modelId = options.model ?? "gemini-1.5-flash";
    const model = client.getGenerativeModel({ model: modelId });

    const res = await model.generateContent({
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: options.temperature ?? 0.3,
      },
    });

    const text = res.response.text();
    return { model: modelId, content: text };
  } catch (err: any) {
    logger.warn({ err }, "Gemini call failed; continuing without Gemini");
    return null;
  }
}
```

```ts
// File: src/memory/memory.ts
// -----------------------------------------------------------------------------
// Script Name   : memory.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Short/long-term memory abstraction with an in-memory store
//                 and a simple JSON-file persistent backend for durability.
// Inputs        : Agent observations, decisions, and artifacts.
// Outputs       : Memory retrieval API used by orchestrator + agents.
// Modification Log:
//   2025-11-16 - Initial version (in-memory only).
//   2025-11-16 - v0.2.0: Added JSON persistence and semantic tags.
// -----------------------------------------------------------------------------

import fs from "fs";
import path from "path";

export type MemoryScope = "short" | "long";

export interface MemoryItem {
  id: string;
  scope: MemoryScope;
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
  content: string;
  metadata?: Record<string, unknown>;
}

export interface MemoryQuery {
  scope?: MemoryScope;
  tags?: string[];
  limit?: number;
}

export interface MemoryStore {
  save(item: Omit<MemoryItem, "id" | "createdAt" | "updatedAt">): Promise<MemoryItem>;
  update(id: string, patch: Partial<Omit<MemoryItem, "id">>): Promise<MemoryItem | null>;
  get(id: string): Promise<MemoryItem | null>;
  query(q: MemoryQuery): Promise<MemoryItem[]>;
}

export class InMemoryStore implements MemoryStore {
  private store = new Map<string, MemoryItem>();

  async save(item: Omit<MemoryItem, "id" | "createdAt" | "updatedAt">): Promise<MemoryItem> {
    const id = crypto.randomUUID();
    const now = new Date();
    const full: MemoryItem = { id, createdAt: now, updatedAt: now, ...item };
    this.store.set(id, full);
    return full;
  }

  async update(
    id: string,
    patch: Partial<Omit<MemoryItem, "id">>,
  ): Promise<MemoryItem | null> {
    const existing = this.store.get(id);
    if (!existing) return null;
    const updated: MemoryItem = {
      ...existing,
      ...patch,
      updatedAt: new Date(),
    };
    this.store.set(id, updated);
    return updated;
  }

  async get(id: string): Promise<MemoryItem | null> {
    return this.store.get(id) ?? null;
  }

  async query(q: MemoryQuery): Promise<MemoryItem[]> {
    let items = Array.from(this.store.values());

    if (q.scope) {
      items = items.filter((i) => i.scope === q.scope);
    }

    if (q.tags && q.tags.length > 0) {
      items = items.filter((i) => q.tags?.every((t) => i.tags.includes(t)));
    }

    if (q.limit && q.limit > 0) {
      items = items.slice(0, q.limit);
    }

    return items;
  }
}

// Simple JSON-file-backed persistent store for long-term memory.

export class JsonFileStore implements MemoryStore {
  private filePath: string;

  private cache = new Map<string, MemoryItem>();

  constructor(filePath = path.join(process.cwd(), "data", "memory.json")) {
    this.filePath = filePath;
    this.loadFromDisk();
  }

  private loadFromDisk(): void {
    try {
      if (!fs.existsSync(this.filePath)) {
        fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
        fs.writeFileSync(this.filePath, "[]", "utf8");
      }

      const raw = fs.readFileSync(this.filePath, "utf8");
      const parsed: any[] = JSON.parse(raw);
      for (const item of parsed) {
        const full: MemoryItem = {
          ...item,
          createdAt: new Date(item.createdAt),
          updatedAt: new Date(item.updatedAt),
        };
        this.cache.set(full.id, full);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[memory] Failed to load JSON memory store", err);
    }
  }

  private persist(): void {
    const arr = Array.from(this.cache.values()).map((i) => ({
      ...i,
      createdAt: i.createdAt.toISOString(),
      updatedAt: i.updatedAt.toISOString(),
    }));
    fs.writeFileSync(this.filePath, JSON.stringify(arr, null, 2), "utf8");
  }

  async save(item: Omit<MemoryItem, "id" | "createdAt" | "updatedAt">): Promise<MemoryItem> {
    const id = crypto.randomUUID();
    const now = new Date();
    const full: MemoryItem = { id, createdAt: now, updatedAt: now, ...item };
    this.cache.set(id, full);
    this.persist();
    return full;
  }

  async update(
    id: string,
    patch: Partial<Omit<MemoryItem, "id">>,
  ): Promise<MemoryItem | null> {
    const existing = this.cache.get(id);
    if (!existing) return null;
    const updated: MemoryItem = {
      ...existing,
      ...patch,
      updatedAt: new Date(),
    };
    this.cache.set(id, updated);
    this.persist();
    return updated;
  }

  async get(id: string): Promise<MemoryItem | null> {
    return this.cache.get(id) ?? null;
  }

  async query(q: MemoryQuery): Promise<MemoryItem[]> {
    let items = Array.from(this.cache.values());

    if (q.scope) {
      items = items.filter((i) => i.scope === q.scope);
    }

    if (q.tags && q.tags.length > 0) {
      items = items.filter((i) => q.tags?.every((t) => i.tags.includes(t)));
    }

    if (q.limit && q.limit > 0) {
      items = items.slice(0, q.limit);
    }

    return items;
  }
}

// By default, we use in-memory for short-term, JSON-file for long-term.

export const shortTermMemory = new InMemoryStore();
export const longTermMemory = new JsonFileStore();
```

```ts
// File: src/agents/types.ts
// -----------------------------------------------------------------------------
// Script Name   : types.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Core type definitions for agents, tasks, and democratic
//                 orchestration.
// Inputs        : Task descriptions, SRS entries, agent configs.
// Outputs       : Strongly-typed contracts for orchestrator + agents.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

export type AgentRole =
  | "architect" // designs SRS + overall plan
  | "planner" // breaks into tasks
  | "implementer" // writes code or artifacts
  | "reviewer" // checks for hallucinations & drift
  | "memory" // curates short/long-term memories
  | "orchestrator"; // coordinates and votes

export interface AgentConfig {
  id: string;
  name: string;
  role: AgentRole;
  description: string;
  preferredModel?: string;
}

export interface TaskSpec {
  id: string;
  title: string;
  description: string;
  targetArtifacts: string[]; // e.g. ["SRS.md", "TASKS.md"]
  maxAgentPasses?: number;
}

export interface AgentInputMessage {
  agentId: string;
  role: AgentRole;
  content: string;
}

export interface AgentInput {
  task: TaskSpec;
  sharedContextMarkdown: string; // concatenated SRS/TASKS/etc.
  priorMessages: AgentInputMessage[];
}

export interface AgentOutput {
  agentId: string;
  role: AgentRole;
  content: string; // markdown patch / commentary / diff
  hallucinationFlags?: string[];
  driftFlags?: string[];
}

export interface Agent {
  readonly config: AgentConfig;
  run(input: AgentInput): Promise<AgentOutput>;
}
```

```ts
// File: src/agents/baseAgent.ts
// -----------------------------------------------------------------------------
// Script Name   : baseAgent.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Base LLM-backed agent using OpenRouter (primary) and optional
//                 Gemini fallback.
// Inputs        : AgentInput, high-level instructions.
// Outputs       : AgentOutput with markdown content.
// Modification Log:
//   2025-11-16 - Initial version.
//   2025-11-16 - v0.2.0: Added Gemini fallback path.
// -----------------------------------------------------------------------------

import type { Agent, AgentInput, AgentOutput } from "./types.js";
import { chatWithOpenRouter } from "../llm/openrouterClient.js";
import { chatWithGemini } from "../llm/geminiClient.js";
import { agentLatencyHistogram, agentRunCounter } from "../telemetry/metrics.js";
import { logAgentEvent } from "../telemetry/logger.js";

export abstract class BaseOpenRouterAgent implements Agent {
  public readonly config;

  protected constructor(config: Agent["config"]) {
    this.config = config;
  }

  protected abstract systemPrompt(): string;

  protected abstract buildUserPrompt(input: AgentInput): string;

  async run(input: AgentInput): Promise<AgentOutput> {
    const endTimer = agentLatencyHistogram
      .labels(this.config.id, this.config.role)
      .startTimer();

    agentRunCounter.labels(this.config.id, this.config.role).inc();

    const userPrompt = this.buildUserPrompt(input);

    logAgentEvent("info", "Agent run started", {
      agentId: this.config.id,
      role: this.config.role,
      taskId: input.task.id,
    });

    try {
      // Primary: OpenRouter
      const res = await chatWithOpenRouter([
        { role: "system", content: this.systemPrompt() },
        {
          role: "user",
          content: userPrompt,
        },
      ], {
        model: this.config.preferredModel,
      });

      const output: AgentOutput = {
        agentId: this.config.id,
        role: this.config.role,
        content: res.content,
      };

      endTimer();

      logAgentEvent("info", "Agent run completed via OpenRouter", {
        agentId: this.config.id,
        role: this.config.role,
        taskId: input.task.id,
        model: res.model,
      });

      return output;
    } catch (primaryError: any) {
      logAgentEvent("warn", "OpenRouter call failed; attempting Gemini fallback", {
        agentId: this.config.id,
        role: this.config.role,
        taskId: input.task.id,
        errorMessage: primaryError?.message ?? "unknown_error",
      });

      try {
        const gemini = await chatWithGemini(
          [this.systemPrompt(), "", userPrompt].join("\n\n"),
          {},
        );

        if (gemini) {
          const output: AgentOutput = {
            agentId: this.config.id,
            role: this.config.role,
            content: gemini.content,
          };

          endTimer();

          logAgentEvent("info", "Agent run completed via Gemini fallback", {
            agentId: this.config.id,
            role: this.config.role,
            taskId: input.task.id,
            model: gemini.model,
          });

          return output;
        }
      } catch (fallbackError: any) {
        logAgentEvent("error", "Gemini fallback also failed", {
          agentId: this.config.id,
          role: this.config.role,
          taskId: input.task.id,
          errorMessage: fallbackError?.message ?? "unknown_error",
        });
      }

      endTimer();
      throw primaryError;
    }
  }
}
```

```ts
// File: src/agents/softwareSpecAgent.ts
// -----------------------------------------------------------------------------
// Script Name   : softwareSpecAgent.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Architect agent that maintains SRS.md, FEATURES.md, and
//                 PROJECT_SUMMARY.md as a cohesive, strongly-typed spec.
// Inputs        : TaskSpec + existing markdown context.
// Outputs       : Markdown patch/content for spec-related files.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import type { AgentInput } from "./types.js";
import { BaseOpenRouterAgent } from "./baseAgent.js";

export class SoftwareSpecAgent extends BaseOpenRouterAgent {
  protected systemPrompt(): string {
    return [
      "You are the ARCHITECT agent in a multi-agent democratic software",
      "development system.",
      "Your responsibilities:",
      "- Maintain a precise, strongly-typed SRS.md, FEATURES.md, and PROJECT_SUMMARY.md.",
      "- Never invent requirements that conflict with existing docs.",
      "- When you add or change requirements, explain WHY in comments.",
      "- Output ONLY valid markdown content representing the updated spec.",
    ].join("\n");
  }

  protected buildUserPrompt(input: AgentInput): string {
    const prior = input.priorMessages
      .map((m) => `- [${m.role}:${m.agentId}] ${m.content.substring(0, 200)}`)
      .join("\n");

    return [
      `Task: ${input.task.title} (ID: ${input.task.id})`,
      "",
      "High-level description:",
      input.task.description,
      "",
      "Existing shared context (SRS/TASKS/etc):",
      "```markdown",
      input.sharedContextMarkdown,
      "```",
      "",
      "Recent agent notes (truncated):",
      prior || "(none)",
      "",
      "Update or extend the SRS.md, FEATURES.md, and PROJECT_SUMMARY.md.",
      "Return ONLY the new or updated content for these files in markdown.",
    ].join("\n");
  }
}
```

```ts
// File: src/agents/plannerAgent.ts
// -----------------------------------------------------------------------------
// Script Name   : plannerAgent.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Planner agent. Reads SRS/features and produces a task list
//                 patch for TASKS.md.
// Inputs        : SRS/features context + high-level task.
// Outputs       : Markdown suitable for TASKS.md.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import type { AgentInput } from "./types.js";
import { BaseOpenRouterAgent } from "./baseAgent.js";

export class PlannerAgent extends BaseOpenRouterAgent {
  protected systemPrompt(): string {
    return [
      "You are the PLANNER agent.",
      "You break high-level objectives and SRS into concrete, atomic tasks.",
      "- Produce a markdown task table or list suitable for TASKS.md.",
      "- Each task should have an ID, title, description, and status TODO.",
      "- Reference SRS and Feature IDs where possible.",
    ].join("\n");
  }

  protected buildUserPrompt(input: AgentInput): string {
    return [
      `Task: ${input.task.title} (ID: ${input.task.id})`,
      "",
      "Shared context (SRS/FEATURES/TASKS):",
      "```markdown",
      input.sharedContextMarkdown,
      "```",
      "",
      "Please produce an updated TASKS.md section that decomposes this work.",
    ].join("\n");
  }
}
```

```ts
// File: src/agents/implementerAgent.ts
// -----------------------------------------------------------------------------
// Script Name   : implementerAgent.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Implementer (coder) agent. Takes tasks and spec and proposes
//                 concrete code or markdown changes.
// Inputs        : TaskSpec + context.
// Outputs       : Markdown diff or code snippets.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import type { AgentInput } from "./types.js";
import { BaseOpenRouterAgent } from "./baseAgent.js";

export class ImplementerAgent extends BaseOpenRouterAgent {
  protected systemPrompt(): string {
    return [
      "You are the IMPLEMENTER (coder) agent.",
      "You propose concrete code changes or markdown patches.",
      "- Respect the SRS and TASKS.",
      "- Produce diffs or code blocks that can be applied directly.",
      "- Do not change scope or invent new requirements.",
    ].join("\n");
  }

  protected buildUserPrompt(input: AgentInput): string {
    return [
      `Task: ${input.task.title} (ID: ${input.task.id})`,
      "",
      "Target artifacts:",
      input.task.targetArtifacts.join(", "),
      "",
      "Shared context (SRS/FEATURES/TASKS + recent messages):",
      "```markdown",
      input.sharedContextMarkdown,
      "```",
      "",
      "Propose concrete code or markdown changes that move this task forward.",
    ].join("\n");
  }
}
```

```ts
// File: src/agents/memoryAgent.ts
// -----------------------------------------------------------------------------
// Script Name   : memoryAgent.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Memory curator agent. Summarizes key learnings and stores
//                 them into long-term memory as compact notes with tags.
// Inputs        : Recent messages and context.
// Outputs       : Short summaries suitable for reuse.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import type { AgentInput } from "./types.js";
import { BaseOpenRouterAgent } from "./baseAgent.js";
import { longTermMemory } from "../memory/memory.js";

export class MemoryAgent extends BaseOpenRouterAgent {
  protected systemPrompt(): string {
    return [
      "You are the MEMORY curator agent.",
      "Your job is to summarize key decisions, fixes, and rules into short notes.",
      "Focus on lessons that will prevent future hallucinations and drift.",
    ].join("\n");
  }

  protected buildUserPrompt(input: AgentInput): string {
    const transcript = input.priorMessages
      .map((m) => `- [${m.role}:${m.agentId}] ${m.content.substring(0, 200)}`)
      .join("\n");

    return [
      "Summarize the following conversation into 3-7 durable lessons.",
      "Each lesson should be a single bullet with any relevant tags.",
      "",
      "Conversation:",
      transcript || "(none)",
    ].join("\n");
  }

  async run(input: AgentInput) {
    const out = await super.run(input);

    const lines = out.content
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.startsWith("- ") || l.startsWith("* "));

    if (lines.length > 0) {
      await longTermMemory.save({
        scope: "long",
        tags: ["lesson", "drift-prevention", input.task.id],
        content: lines.join("\n"),
        metadata: { taskId: input.task.id },
      });
    }

    return out;
  }
}
```

```ts
// File: src/agents/reviewerAgent.ts
// -----------------------------------------------------------------------------
// Script Name   : reviewerAgent.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Reviewer/critic agent that looks for hallucinations and
//                 task drift and annotates issues for the next agent.
// Inputs        : AgentInput including the most recent agent response.
// Outputs       : AgentOutput with hallucination/drift flags.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import type { AgentInput, AgentOutput } from "./types.js";
import { BaseOpenRouterAgent } from "./baseAgent.js";

export class ReviewerAgent extends BaseOpenRouterAgent {
  protected systemPrompt(): string {
    return [
      "You are the REVIEWER agent in a multi-agent democratic system.",
      "Your job is to detect hallucinations and task drift.",
      "- Hallucination: content that cannot be justified from the task or prior context.",
      "- Drift: content that moves away from the requested task or spec.",
      "Return a markdown report with sections:",
      "# REVIEW\n## HALLUCINATIONS\n- ...\n## DRIFT\n- ...\n## SUGGESTED_CORRECTIONS\n- ...",
    ].join("\n");
  }

  protected buildUserPrompt(input: AgentInput): string {
    const lastMessage = input.priorMessages[input.priorMessages.length - 1];

    return [
      `Task: ${input.task.title} (ID: ${input.task.id})`,
      "",
      "Shared context:",
      "```markdown",
      input.sharedContextMarkdown,
      "```",
      "",
      "Most recent agent output:",
      lastMessage
        ? `Agent ${lastMessage.agentId} (${lastMessage.role}) wrote:\n\n${lastMessage.content}`
        : "(none)",
      "",
      "Identify any hallucinations or drift and propose precise corrections.",
    ].join("\n");
  }

  async run(input: AgentInput): Promise<AgentOutput> {
    const base = await super.run(input);

    const hallucinationFlags: string[] = [];
    const driftFlags: string[] = [];

    const lines = base.content.split("\n");
    for (const line of lines) {
      const trimmed = line.toLowerCase();
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (trimmed.includes("hallucination") || trimmed.includes("unsupported")) {
          hallucinationFlags.push(line.trim());
        }
        if (trimmed.includes("drift") || trimmed.includes("off-topic")) {
          driftFlags.push(line.trim());
        }
      }
    }

    return {
      ...base,
      hallucinationFlags,
      driftFlags,
    };
  }
}
```

```ts
// File: src/agents/democracyOrchestrator.ts
// -----------------------------------------------------------------------------
// Script Name   : democracyOrchestrator.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Democratic multi-agent orchestration loop. Each task is
//                 processed by architect + planner + implementer agents;
//                 reviewer checks for hallucinations & drift, memory agent
//                 distills lessons, and the final answer is selected by a
//                 simple score-based vote.
// Inputs        : TaskSpec + initial markdown context.
// Outputs       : Aggregated markdown result + per-agent reports.
// Modification Log:
//   2025-11-16 - Initial version (architect + reviewer).
//   2025-11-16 - v0.2.0: Added planner, implementer, memory agents and scoring.
// -----------------------------------------------------------------------------

import type { Agent, AgentInput, AgentOutput, TaskSpec } from "./types.js";
import { SoftwareSpecAgent } from "./softwareSpecAgent.js";
import { PlannerAgent } from "./plannerAgent.js";
import { ImplementerAgent } from "./implementerAgent.js";
import { MemoryAgent } from "./memoryAgent.js";
import { ReviewerAgent } from "./reviewerAgent.js";
import { agentErrorCounter } from "../telemetry/metrics.js";
import { logAgentEvent, logger } from "../telemetry/logger.js";

export interface OrchestrationResult {
  task: TaskSpec;
  finalContent: string;
  agentOutputs: AgentOutput[];
}

export class DemocracyOrchestrator {
  private readonly agents: Agent[];

  constructor() {
    this.agents = [
      new SoftwareSpecAgent({
        id: "architect-1",
        name: "Architect",
        role: "architect",
        description: "Maintains SRS/FEATURES/PROJECT_SUMMARY",
      }),
      new PlannerAgent({
        id: "planner-1",
        name: "Planner",
        role: "planner",
        description: "Breaks features into tasks",
      }),
      new ImplementerAgent({
        id: "implementer-1",
        name: "Implementer",
        role: "implementer",
        description: "Writes code or markdown diffs",
      }),
      new ReviewerAgent({
        id: "reviewer-1",
        name: "Reviewer",
        role: "reviewer",
        description: "Critic that flags hallucinations & drift",
      }),
      new MemoryAgent({
        id: "memory-1",
        name: "Memory",
        role: "memory",
        description: "Summarizes lessons into long-term memory",
      }),
    ];
  }

  async runTask(task: TaskSpec, sharedContextMarkdown: string): Promise<OrchestrationResult> {
    const priorMessages: AgentInput["priorMessages"] = [];
    const outputs: AgentOutput[] = [];

    for (const agent of this.agents) {
      const input: AgentInput = {
        task,
        sharedContextMarkdown,
        priorMessages,
      };

      try {
        const out = await agent.run(input);
        outputs.push(out);

        priorMessages.push({
          agentId: out.agentId,
          role: out.role,
          content: out.content,
        });
      } catch (err: any) {
        agentErrorCounter.labels(agent.config.id, agent.config.role, "runtime_error").inc();
        logAgentEvent("error", "Error in democratic orchestrator", {
          agentId: agent.config.id,
          role: agent.config.role,
          taskId: task.id,
          errorMessage: err?.message ?? "unknown_error",
        });
      }
    }

    // Democratic scoring: prefer implementer output with fewest flags.
    const scored = outputs.map((o) => {
      const hallucinations = o.hallucinationFlags?.length ?? 0;
      const drift = o.driftFlags?.length ?? 0;
      const penalty = hallucinations * 2 + drift; // hallucinations cost more.
      const baseScore = o.role === "implementer" ? 10 : o.role === "architect" ? 6 : 4;
      const score = baseScore - penalty;
      return { out: o, score };
    });

    scored.sort((a, b) => b.score - a.score);
    const best = scored[0]?.out ?? outputs[0];

    const finalContent = best?.content ?? "";

    logger.info({ taskId: task.id, winningAgent: best?.agentId }, "Orchestration completed");

    return {
      task,
      finalContent,
      agentOutputs: outputs,
    };
  }
}
```

```ts
// File: src/orchestration/langgraphGraph.ts
// -----------------------------------------------------------------------------
// Script Name   : langgraphGraph.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Optional LangGraph-based orchestration graph. This wraps the
//                 same agents as DemocracyOrchestrator but arranges them in a
//                 graph that can support retries and branching.
// Inputs        : TaskSpec + context.
// Outputs       : Final content and state, when LangGraph is enabled.
// Modification Log:
//   2025-11-16 - Initial version (optional).
// -----------------------------------------------------------------------------

import { getEnv } from "../config/env.js";
import { logger } from "../telemetry/logger.js";
import type { TaskSpec, AgentOutput } from "../agents/types.js";

export interface LanggraphOrchestrationResult {
  task: TaskSpec;
  finalContent: string;
  agentOutputs: AgentOutput[];
}

export async function runLanggraphFlow(
  _task: TaskSpec,
  _sharedContext: string,
): Promise<LanggraphOrchestrationResult | null> {
  const env = getEnv();

  if (env.ENABLE_LANGGRAPH !== "1") {
    logger.debug("LangGraph disabled; skipping LangGraph orchestration");
    return null;
  }

  try {
    const { StateGraph } = await import("@langchain/langgraph");
    // NOTE: This is a placeholder sketch. You can expand this to wire concrete
    // agent calls into LangGraph nodes; for now we just log that LangGraph
    // would be used here.

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const graph = new StateGraph({
      channels: {},
      channelsConfig: {},
    });

    logger.info("LangGraph flow is not fully implemented yet; falling back.");
    return null;
  } catch (err: any) {
    logger.warn({ err }, "LangGraph import or execution failed; falling back");
    return null;
  }
}
```

```ts
// File: src/experiments/demo.ts
// -----------------------------------------------------------------------------
// Script Name   : demo.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Simple experiment harness to run a democratic orchestration
//                 cycle over a toy software task.
// Inputs        : Hard-coded TaskSpec + empty markdown context.
// Outputs       : Console logs of finalContent and per-agent outputs.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import { DemocracyOrchestrator } from "../agents/democracyOrchestrator.js";
import type { TaskSpec } from "../agents/types.js";
import { logger } from "../telemetry/logger.js";
import { runLanggraphFlow } from "../orchestration/langgraphGraph.js";

export async function runDemo(): Promise<void> {
  const orchestrator = new DemocracyOrchestrator();

  const task: TaskSpec = {
    id: "demo-001",
    title: "Design multi-agent democratic SRS system",
    description:
      "Create or refine SRS.md, FEATURES.md, PROJECT_SUMMARY.md describing a multi-agent, " +
      "democratic, self-healing software development system using free OpenRouter models.",
    targetArtifacts: ["SRS.md", "FEATURES.md", "PROJECT_SUMMARY.md"],
    maxAgentPasses: 5,
  };

  const sharedContext = [
    "# PROJECT_SUMMARY.md (initial)",
    "This is an empty placeholder; agents should fill this in.",
    "",
    "# SRS.md (initial)",
    "- TBD",
    "",
    "# FEATURES.md (initial)",
    "- TBD",
  ].join("\n");

  // Try LangGraph path first if enabled.
  const graphResult = await runLanggraphFlow(task, sharedContext);

  const result =
    graphResult ?? (await orchestrator.runTask(task, sharedContext));

  logger.info({ finalContentSnippet: result.finalContent.substring(0, 400) }, "Demo result");

  for (const out of result.agentOutputs) {
    logger.info(
      {
        agentId: out.agentId,
        role: out.role,
        hallucinations: out.hallucinationFlags?.length ?? 0,
        drift: out.driftFlags?.length ?? 0,
      },
      "Agent output summary",
    );
  }
}
```

```ts
// File: src/index.ts
// -----------------------------------------------------------------------------
// Script Name   : index.ts
// Author        : cbwinslow + ChatGPT
// Created       : 2025-11-16
// Summary       : Entry point. Starts Prometheus metrics server and runs a demo
//                 orchestration flow to verify that everything is wired up.
// Inputs        : Environment variables, no CLI args yet.
// Outputs       : Logs, metrics, and a sample orchestration run.
// Modification Log:
//   2025-11-16 - Initial version.
// -----------------------------------------------------------------------------

import { startMetricsServer } from "./telemetry/metrics.js";
import { runDemo } from "./experiments/demo.js";
import { logger } from "./telemetry/logger.js";
import { flushLangfuse } from "./telemetry/langfuse.js";

async function main(): Promise<void> {
  startMetricsServer();

  try {
    await runDemo();
  } catch (err: any) {
    logger.error({ err }, "Demo run failed");
  } finally {
    await flushLangfuse();
  }
}

// eslint-disable-next-line unicorn/prefer-top-level-await
main().catch((err) => {
  logger.error({ err }, "Fatal error in main()");
});
```

```md
// File: README_ORCHESTRATOR.md

# Multi-Agent Democratic Orchestrator (TypeScript)

This repository contains an experimental multi-agent, democratic TypeScript orchestrator designed for:

- **OpenRouter** as the primary LLM backend (using only free models by default).
- Optional **Gemini** support via `@google/generative-ai`.
- Future **Google ADK / A2A** integration (hook in via a separate adapter module).
- **Langfuse** for rich observability and traces.
- **Prometheus** for metrics (`/metrics` on `PROMETHEUS_PORT`, default 9464).
- A pluggable short/long-term **memory** abstraction with JSON-backed persistence.

## Quickstart

1. Install dependencies:

```bash
npm install
```

2. Set environment variables (for development):

```bash
export OPENROUTER_API_KEY="your_openrouter_key_here"
export OPENROUTER_APP_URL="https://cloudcurio.cc"
export OPENROUTER_APP_NAME="CloudCurio Orchestrator"
# Optional observability:
# export LANGFUSE_SECRET_KEY=...
# export LANGFUSE_PUBLIC_KEY=...
# export LANGFUSE_BASE_URL=...
# Optional Gemini:
# export GOOGLE_API_KEY=...
# export ENABLE_GEMINI=1
# Optional LangGraph:
# export ENABLE_LANGGRAPH=1
# Metrics port (default 9464):
# export PROMETHEUS_PORT=9464
```

3. Run the demo:

```bash
npm run dev
```

4. Scrape Prometheus metrics from:

```text
http://localhost:9464/metrics
```

5. Point Langfuse at your instance to inspect traces.

## Agents

Implemented agents:

- **Architect** (`SoftwareSpecAgent`) — maintains SRS/FEATURES/PROJECT_SUMMARY.
- **Planner** (`PlannerAgent`) — breaks features into tasks.
- **Implementer** (`ImplementerAgent`) — writes code/markdown diffs.
- **Reviewer** (`ReviewerAgent`) — flags hallucinations & drift.
- **Memory** (`MemoryAgent`) — summarizes lessons into long-term memory.

## Orchestration

- `DemocracyOrchestrator` wires agents into a sequence:
  - Architect → Planner → Implementer → Reviewer → Memory.
- Outputs are scored by:
  - Base score per role (Implementer > Architect > others).
  - Penalties for hallucination and drift flags.
- Highest-scoring output is treated as the democratic winner.

## LangGraph

- Optional `runLanggraphFlow` hook (in `src/orchestration/langgraphGraph.ts`) sketches how
  to move this pipeline into a LangGraph state graph for retries and branching.
- Controlled by `ENABLE_LANGGRAPH=1`.

## Persistent & Semantic Memory

- Short-term memory: `InMemoryStore`.
- Long-term memory: `JsonFileStore` at `./data/memory.json`.
- Memory items can be tagged, and you can later add an embeddings layer on top
  to support semantic recall.

## Next Steps / Improvements

1. **Google ADK / A2A adapter**
   - Implement a module that exposes some of these agents over A2A and/or calls
     external ADK agents as tools.
2. **Semantic embeddings**
   - Add an embedding model (e.g., free OpenRouter embedding model) and store
     vectors alongside `MemoryItem` records.
3. **LangGraph full wiring**
   - Represent the orchestration plan as a real LangGraph graph with retry
     policies and branches for heavy drift vs light drift.
```
