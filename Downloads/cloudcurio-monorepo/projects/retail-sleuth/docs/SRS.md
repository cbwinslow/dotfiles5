# Software Requirements Specification (SRS)
## Project: Retail Sleuth – Multi-Retailer Price Research Platform
## Version: 0.3.0
## Author: cbwinslow & AI Collaborator
## Last Updated: 2025-11-16

---

## 1. Introduction

### 1.1 Purpose

Retail Sleuth is a research platform for collecting, normalizing, and analyzing
product prices, images, and metadata across multiple retailers. It is designed
for *lawful, ethical research only* and must:

- Respect robots.txt
- Respect rate limits and Terms of Service
- Avoid bypassing authentication, paywalls, or anti-bot measures

The platform exposes clean, queryable datasets and time series of prices that
can be used for analytics, modeling, and policy / market research.

### 1.2 Scope

Retail Sleuth consists of:

- A **Python backend library** for ingestion (HTTP APIs + HTML using crawl4ai)
- A **PostgreSQL + TimescaleDB** data store for canonical and time-series data
- Optional **InfluxDB**/TSDB experiments for time-series comparison
- A **Go/Bubbletea TUI** for interactive control, monitoring, and data browsing
- **Postman-based recon tooling** for discovering and documenting retailer APIs
- **Docker-based infrastructure** for local and future cluster deployment

Out of scope:

- Automated purchasing, carts, or non-research automation
- Scraping of sites disallowing such access
- Any attempt to evade security controls

---

## 2. System Overview

### 2.1 High-Level Architecture

Components:

1. **Recon Layer (Postman + Node CLI)**
   - Observes traffic to retailer APIs
   - Records endpoints, parameters, and inferred rate limits
   - Writes `api_endpoints.json` catalog consumed by backend

2. **Ingestion Core (Python OOP)**
   - Implements domain models: `Retailer`, `Item`, `PriceSnapshot`
   - Wraps HTTP/API and HTML crawling (via crawl4ai)
   - Encapsulates rate limit and robots.txt policies
   - Persists data into PostgreSQL and TimescaleDB

3. **API Layer (FastAPI)**
   - Serves REST endpoints for:
     - Retailer metadata
     - Item metadata
     - Price history and summary stats

4. **TUI Layer (Go + Bubbletea)**
   - Terminal UI for:
     - Browsing retailers and items
     - Triggering ingestion jobs
     - Viewing status, logs, and basic charts

5. **Data + Infra Layer**
   - PostgreSQL (+TimescaleDB extension)
   - Optional Kafka for stream ingestion
   - Optional Airflow for scheduled pipelines
   - Optional Superset/Grafana for dashboards

---

## 3. Functional Requirements

### FR-1 Retailer Management

- FR-1.1: User can create, update, and delete retailer entries.
- FR-1.2: For each retailer, system stores:
  - Name, slug, base_url
  - robots_txt_url (optional, defaults to base_url + `/robots.txt`)
  - allowed_paths / disallowed_paths overrides
  - rate_limit configuration (max requests / window)
  - ingestion strategy (`rest`, `html`, `mixed`)

### FR-2 API Endpoint Catalog

- FR-2.1: Postman collection logs each request/response pair.
- FR-2.2: Node CLI exports accumulated logs into `api_endpoints.json`.
- FR-2.3: Python backend loads `api_endpoints.json` into a `ApiEndpointCatalog`
  class used by `RestClient`.

### FR-3 Robots.txt Compliance

- FR-3.1: Before any HTML fetch, ingestion core checks robots.txt via
  `RobotsChecker`.
- FR-3.2: If robots.txt denies a path and no explicit override is configured,
  the request must not be sent.
- FR-3.3: All blocked requests are logged with reason.

### FR-4 Price Snapshot Ingestion

- FR-4.1: Ingestion jobs produce `PriceSnapshot` objects for each SKU or item.
- FR-4.2: Each snapshot includes:
  - retailer_id, item_id
  - price (numeric)
  - currency (ISO code)
  - availability flags
  - collected_at (UTC timestamp)
- FR-4.3: Snapshots are inserted into:
  - A normalized `item_prices` table in PostgreSQL
  - A hypertable in TimescaleDB (or TSDB analog)

### FR-5 Query & Analytics API

- FR-5.1: REST API supports:
  - `/retailers/`
  - `/items/?q=...`
  - `/items/{item_id}/prices?from=...&to=...`
- FR-5.2: Responses must be JSON and documented in OpenAPI.

### FR-6 TUI Operations

- FR-6.1: TUI can:
  - List retailers
  - Show last run status per retailer
  - Trigger single-run ingestion job
  - View recent price history for a selected item
- FR-6.2: TUI must handle network errors gracefully with clear messages.

---

## 4. Non-Functional Requirements

### NFR-1 Legal & Ethics

- System must never:
  - Circumvent authentication
  - Spoof human behavior to bypass controls
- All configurations must explicitly acknowledge that user is responsible for
  ensuring lawful use.

### NFR-2 Reliability & Recoverability

- Critical write operations must be idempotent.
- Failed ingestion job must not corrupt historical data.
- Logs must allow reconstruction of ingestion events after the fact.

### NFR-3 Performance

- Target: handle at least 10k price snapshots/day per retailer on a modest
  homelab server.
- Ingestion concurrency is configurable to avoid overloading targets.

### NFR-4 Security

- Secrets (DB passwords, API keys) must be sourced from environment variables,
  local secret store, or external secret manager.
- No secrets may be committed to git.

---

## 5. Data Model (High Level)

Entities:

- Retailer
- Item
- PriceSnapshot
- CrawlJob
- ApiEndpoint

(See `docs/DATABASE_DESIGN.md` for table-level detail.)

---

## 6. Assumptions & Dependencies

- User has Python 3.10+, Go 1.22+, Docker, and docker-compose.
- crawl4ai is installed and configured.
- PostgreSQL is reachable and migrations run successfully.
