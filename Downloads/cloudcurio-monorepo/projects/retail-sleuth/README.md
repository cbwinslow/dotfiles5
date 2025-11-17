# Retail Sleuth

Research platform for lawful, ethical price and product metadata collection
across multiple retailers.

## Quick Start

1. Start services:

```bash
make dev-up
```

2. Run API (in another terminal):

```bash
cd backend
uvicorn api.main:app --reload
```

3. Run TUI:

```bash
make tui
```

This repository is a starting point: ingestion clients, retailer adapters, and
detailed analytics are meant to be extended over time.
