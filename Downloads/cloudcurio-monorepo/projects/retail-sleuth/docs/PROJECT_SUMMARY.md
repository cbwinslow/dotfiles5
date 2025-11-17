# PROJECT SUMMARY

Retail Sleuth is a homelab-friendly, research-oriented price intelligence
platform. It is built for analysts and experimenters who want to safely and
legally study prices and item metadata across multiple retailers.

## Goals

- Provide a reusable ingestion framework for structured and semi-structured
  price data.
- Make all behavior explicit, observable, and controllable from the terminal.
- Support long-term time-series analysis for research.

## Architecture Overview

1. **Data Sources**
   - Official APIs discovered via Postman recon.
   - HTML pages fetched with crawl4ai when allowed.

2. **Processing**
   - Python ingestion core normalizes data into domain models.
   - Ethics layer enforces robots.txt and rate limits.
   - Results are written to relational and time-series stores.

3. **Access**
   - FastAPI exposes JSON endpoints for programmatic access.
   - Go/Bubbletea TUI provides a comfortable, scriptable UI.
   - BI tools attach to PostgreSQL/Timescale for dashboards.

## Typical Workflow

1. Researcher defines a new retailer in config.
2. User performs Postman recon while using the retailer’s web or mobile app.
3. Node CLI exports discovered endpoints.
4. Developer writes a retailer adapter referencing catalog/HTML selectors.
5. Ingestion job is run (via CLI or TUI).
6. Data appears in DB and can be queried via API or dashboards.

The repository is organized to keep ingestion logic, storage, infra, and UI
loosely coupled, making it easy to extend or replace pieces later.
