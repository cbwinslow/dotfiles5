# DocBrain (MVP)

DocBrain is a personal documentation engine that scans your projects for Python code
and Markdown notes, extracts functions/classes/concepts, and stores them in a local
SQLite database. You can then search and view your own "super-man pages" for your
code and notes.

## Features

- Scan directories for:
  - Python files: extract functions and classes via `ast`
  - Markdown files: extract headings as "concept" docs
- Store docs in SQLite with a simple normalized schema
- CLI commands:
  - `init-db` — initialize the database
  - `scan` — scan one or more directories
  - `search` — search docs by text
  - `view` — view a single doc by `doc_id`
  - `recent` — show recently updated docs

## Quickstart

```bash
# 1) Make the script executable
chmod +x docbrain.py

# 2) Initialize the database (defaults to ~/.docbrain/docbrain.sqlite3)
./docbrain.py init-db

# 3) Scan one or more project directories
./docbrain.py scan ~/dev ~/infra-ansible

# 4) Search for docs
./docbrain.py search "cloudflare"

# 5) View a specific doc by ID (as printed in search results)
./docbrain.py view python:myproject.module.func_name

# 6) Show recent docs
./docbrain.py recent
```

## Notes & Next Steps

This is an MVP focused on static extraction. Obvious next upgrades include:

- Adding an AI layer to refine `summary`, `details`, and `examples` using LLMs.
- Ingesting other languages (Go, Bash, TypeScript) and config formats.
- Integrating with your editor/IDE for inline hover docs.
- Adding a TUI or web UI on top of the SQLite database.
