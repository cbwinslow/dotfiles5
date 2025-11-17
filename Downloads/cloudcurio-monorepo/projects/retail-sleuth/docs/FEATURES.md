# FEATURES – Expanded

## 1. Retailer Catalog

- CRUD operations on retailers (via API and CLI).
- Store base URLs, robots.txt URLs, rate limits, and strategy flags.
- Tag retailers with categories (electronics, grocery, etc.).
- Flag test retailers / demo sources separate from real ones.

## 2. API Recon Tooling (Postman + Node)

- Shared Postman collection `Retail API Recon`.
- Tests tab script captures:
  - Method, path, status
  - Request and response headers
  - Partial body sample
- Environment variable `discovered_endpoints` accumulates session results.
- Node CLI:
  - Fetches Postman environment via Postman API (optional)
  - Writes `tools/postman/discovered/api_endpoints.json`
  - Cleans and de-duplicates endpoints.

## 3. Ingestion Core (Python Library)

- OOP domain models with strong validation.
- Separate layers:
  - `datasources` – REST and HTML clients.
  - `ethics` – Robots.txt and rate limit policy.
  - `storage` – Repositories for Postgres and time-series backend.
  - `utils` – HTTP helpers, retries, validation.

Key features:

- Per-retailer rate limit enforcement.
- Configurable backoff and retry policies.
- Detailed structured logging for each request.

## 4. Time Series Storage

- Use TimescaleDB hypertable for price snapshots:
  - Fast time-based queries.
  - Downsampling and retention policies later.
- Optional InfluxDB client for experimentation:
  - Write the same snapshots to InfluxDB bucket.

## 5. REST API (FastAPI)

Endpoints:

- `GET /health` – health check.
- `GET /retailers/` – list retailers.
- `GET /retailers/{id}` – retailer detail.
- `GET /items/` – search by name, SKU, or retailer.
- `GET /items/{id}` – item detail.
- `GET /items/{id}/prices` – time-series price data.

Features:

- Pagination and filtering.
- Input validation via Pydantic.
- OpenAPI docs at `/docs`.

## 6. TUI (Go + Bubbletea)

Views:

1. **Dashboard View**
   - Summary cards: number of retailers, items, total snapshots.
   - Last ingestion status.

2. **Retailer View**
   - List of retailers with status indicators.
   - Key-bindings:
     - `Enter` – open details.
     - `r` – run ingestion job.
     - `l` – view logs.

3. **Item View**
   - Paginated item list filtered by retailer or search query.
   - Selecting an item shows details in the right pane.

4. **Price History View**
   - ASCII sparkline of prices.
   - Min/Max/Median stats.
   - Last updated timestamp.

Global features:

- Configurable color theme.
- Detailed error messages and log panel.

## 7. Analytics + Dashboards

Using Apache Superset or Grafana:

- Dashboard: "Price Trajectories"
- Dashboard: "Retailer Health" (error rates, latency, status)
- Dashboard: "Cross-Retailer Price Comparison"

## 8. Extensibility

- Retailer adapters as small Python classes implementing `BaseClient`.
- Plug-in registry maps retailer slug → adapter class path.
- Developers add new retailer by:
  - Writing adapter
  - Adding config entry
  - Running tests.
