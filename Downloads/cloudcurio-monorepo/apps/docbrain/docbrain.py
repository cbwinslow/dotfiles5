#!/usr/bin/env python3
"""docbrain.py
----------------------------------------------------------------------
Author      : cbwinslow / ChatGPT
Created     : 2025-11-16
Summary     : Personal documentation engine that scans directories for
              Python and Markdown files, extracts functions/concepts,
              and stores structured documentation in a local SQLite DB.

Inputs      :
    - CLI arguments (see `main()` / argparse help).
    - One or more filesystem paths to scan for documentation candidates.
    - Existing SQLite database file (will be created if missing).

Outputs     :
    - SQLite database containing structured documentation entries.
    - Human-readable console output for search/view commands.
    - Optional log file with diagnostic information.

Key Features:
    - Scans Python files using AST to extract functions and classes.
    - Scans Markdown files to extract concepts and sections.
    - Stores results in a normalized SQLite schema.
    - Provides a CLI (`scan`, `search`, `view`, `recent`, `init-db`).
    - Designed as a starting point for future AI-powered doc generation.

Modification Log:
    - 2025-11-16: Initial version (MVP) with Python + Markdown ingestion,
                  basic search and view commands, and robust error handling.
----------------------------------------------------------------------
"""

import argparse
import ast
import datetime
import logging
import os
import sqlite3
import sys
import textwrap
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Iterable, Tuple

# ------------------------------------------------------------------
# Constants & global configuration
# ------------------------------------------------------------------

DEFAULT_DB_PATH = os.path.expanduser("~/.docbrain/docbrain.sqlite3")
DEFAULT_LOG_PATH = "/tmp/CBW-docbrain.log"

DOC_TYPE_FUNCTION = "function"
DOC_TYPE_CLASS = "class"
DOC_TYPE_CONCEPT = "concept"

# ------------------------------------------------------------------
# Data model
# ------------------------------------------------------------------


@dataclass
class DocObject:
    """In-memory representation of a documentation object.

    This model is intentionally simple and JSON-serializable to make it
    easy to evolve and move into other storage engines later.
    """

    doc_id: str                    # Stable identifier (e.g., python:module.func)
    doc_type: str                  # function | class | concept | other
    title: str                     # Human-readable title
    summary: str                   # Short TL;DR-style summary
    details: str                   # Longer explanation/notes
    language: Optional[str]        # e.g. python, markdown, bash
    kind: Optional[str]            # e.g. function, class, section
    module: Optional[str]          # Python module path if applicable
    file_path: Optional[str]       # Absolute path to source file
    signature: Optional[str]       # Function signature (textual)
    parameters: Optional[str]      # JSON-encoded parameter list
    returns: Optional[str]         # Description of return value(s)
    examples: Optional[str]        # JSON-encoded examples
    tags: Optional[str]            # Comma-separated tags
    source_refs: Optional[str]     # JSON-encoded list of source references
    created_at: str                # ISO-8601 creation timestamp
    updated_at: str                # ISO-8601 last-update timestamp


# ------------------------------------------------------------------
# Logging utilities
# ------------------------------------------------------------------


def setup_logging(verbose: bool = False, log_path: str = DEFAULT_LOG_PATH) -> None:
    """Configure the root logger with file + console handlers.

    Parameters
    ----------
    verbose : bool
        If True, enable DEBUG logging to the console.
    log_path : str
        Filesystem path where the log file should be written.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])


logger = logging.getLogger("docbrain")


# ------------------------------------------------------------------
# SQLite helpers
# ------------------------------------------------------------------


def get_connection(db_path: str) -> sqlite3.Connection:
    """Create or open a SQLite database connection.

    Ensures that the parent directories exist.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize the SQLite schema if it does not already exist."""
    logger.debug("Initializing database schema if needed...")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            doc_id      TEXT PRIMARY KEY,
            doc_type    TEXT NOT NULL,
            title       TEXT NOT NULL,
            summary     TEXT,
            details     TEXT,
            language    TEXT,
            kind        TEXT,
            module      TEXT,
            file_path   TEXT,
            signature   TEXT,
            parameters  TEXT,
            returns     TEXT,
            examples    TEXT,
            tags        TEXT,
            source_refs TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_docs_type_title
        ON docs (doc_type, title);
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_docs_updated_at
        ON docs (updated_at);
        """
    )
    conn.commit()
    logger.info("Database initialized.")


def upsert_doc(conn: sqlite3.Connection, doc: DocObject) -> None:
    """Insert or update a documentation object in SQLite."""
    logger.debug("Upserting doc_id=%s title=%s", doc.doc_id, doc.title)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO docs (
            doc_id, doc_type, title, summary, details, language, kind,
            module, file_path, signature, parameters, returns, examples,
            tags, source_refs, created_at, updated_at
        ) VALUES (
            :doc_id, :doc_type, :title, :summary, :details, :language, :kind,
            :module, :file_path, :signature, :parameters, :returns, :examples,
            :tags, :source_refs, :created_at, :updated_at
        )
        ON CONFLICT(doc_id) DO UPDATE SET
            doc_type    = excluded.doc_type,
            title       = excluded.title,
            summary     = excluded.summary,
            details     = excluded.details,
            language    = excluded.language,
            kind        = excluded.kind,
            module      = excluded.module,
            file_path   = excluded.file_path,
            signature   = excluded.signature,
            parameters  = excluded.parameters,
            returns     = excluded.returns,
            examples    = excluded.examples,
            tags        = excluded.tags,
            source_refs = excluded.source_refs,
            updated_at  = excluded.updated_at;
        """,
        asdict(doc),
    )
    conn.commit()


def search_docs(conn: sqlite3.Connection, query: str, limit: int = 20) -> List[sqlite3.Row]:
    """Simple full-text search over title, summary, and details."""
    logger.debug("Searching docs for query=%r limit=%d", query, limit)
    cur = conn.cursor()
    wildcard = f"%{query}%"
    cur.execute(
        """
        SELECT * FROM docs
        WHERE title   LIKE :q
           OR summary LIKE :q
           OR details LIKE :q
        ORDER BY updated_at DESC
        LIMIT :limit;
        """,
        {"q": wildcard, "limit": limit},
    )
    return cur.fetchall()


def get_doc_by_id(conn: sqlite3.Connection, doc_id: str) -> Optional[sqlite3.Row]:
    """Fetch a single documentation entry by its identifier."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM docs WHERE doc_id = ?", (doc_id,))
    row = cur.fetchone()
    return row


def get_recent_docs(conn: sqlite3.Connection, limit: int = 20) -> List[sqlite3.Row]:
    """Return recently updated documentation entries."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM docs
        ORDER BY updated_at DESC
        LIMIT ?;
        """,
        (limit,),
    )
    return cur.fetchall()


# ------------------------------------------------------------------
# Python file parsing
# ------------------------------------------------------------------


def _safe_read_text(path: str) -> Optional[str]:
    """Read a file as UTF-8 text with basic error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to read %s: %s", path, exc)
        return None


def infer_module_name(file_path: str, root_path: str) -> str:
    """Infer a Python module path from a file path relative to a root.

    Example:
        root_path = /home/user/dev/project
        file_path = /home/user/dev/project/pkg/utils/helpers.py
        -> module = pkg.utils.helpers
    """
    try:
        rel = os.path.relpath(file_path, root_path)
    except ValueError:
        rel = os.path.basename(file_path)

    rel_no_ext = os.path.splitext(rel)[0]
    parts = [p for p in rel_no_ext.split(os.sep) if p not in (".", "")]
    return ".".join(parts)


def extract_functions_and_classes(
    file_path: str, root_path: str
) -> Iterable[DocObject]:
    """Parse a Python source file and yield DocObject instances.

    This is a static-analysis-only approach using `ast`, which is safe to
    run on untrusted code because it does not execute it.
    """
    logger.debug("Parsing Python file: %s", file_path)
    source = _safe_read_text(file_path)
    if source is None:
        return []

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as exc:
        logger.warning("SyntaxError while parsing %s: %s", file_path, exc)
        return []

    module_name = infer_module_name(file_path, root_path)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    docs: List[DocObject] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"
            func_name = node.name
            doc_id = f"python:{module_name}.{func_name}" if module_name else f"python:{func_name}"

            docstring = ast.get_docstring(node) or ""
            first_line, _, rest = docstring.partition("\n")
            summary = first_line.strip() or f"Python {kind} {func_name}()"
            details = rest.strip()

            # Build a simple signature representation
            arg_names = [a.arg for a in node.args.args]
            signature = f"{func_name}({', '.join(arg_names)})"

            doc = DocObject(
                doc_id=doc_id,
                doc_type=DOC_TYPE_FUNCTION,
                title=func_name,
                summary=summary,
                details=details,
                language="python",
                kind=kind,
                module=module_name,
                file_path=os.path.abspath(file_path),
                signature=signature,
                parameters=None,
                returns=None,
                examples=None,
                tags="python,code,auto" if module_name else "python,code",
                source_refs=None,
                created_at=now,
                updated_at=now,
            )
            docs.append(doc)

        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            doc_id = f"python:{module_name}.{class_name}" if module_name else f"python:{class_name}"

            docstring = ast.get_docstring(node) or ""
            first_line, _, rest = docstring.partition("\n")
            summary = first_line.strip() or f"Python class {class_name}"
            details = rest.strip()

            doc = DocObject(
                doc_id=doc_id,
                doc_type=DOC_TYPE_CLASS,
                title=class_name,
                summary=summary,
                details=details,
                language="python",
                kind="class",
                module=module_name,
                file_path=os.path.abspath(file_path),
                signature=None,
                parameters=None,
                returns=None,
                examples=None,
                tags="python,code,class",
                source_refs=None,
                created_at=now,
                updated_at=now,
            )
            docs.append(doc)

    return docs


# ------------------------------------------------------------------
# Markdown parsing
# ------------------------------------------------------------------


def extract_concepts_from_markdown(file_path: str) -> Iterable[DocObject]:
    """Extract heading-based "concept" docs from a Markdown file.

    This is a deliberately simple parser that looks for lines starting with
    one or more `#` characters (H1/H2/H3), then captures the following text
    as the concept body until the next heading.
    """
    logger.debug("Parsing Markdown file: %s", file_path)
    text = _safe_read_text(file_path)
    if text is None:
        return []

    lines = text.splitlines()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    docs: List[DocObject] = []

    current_heading = None
    current_level = None
    current_body: List[str] = []

    def flush_current() -> None:
        nonlocal current_heading, current_body, current_level
        if current_heading is None:
            return
        title = current_heading.strip()
        body = "\n".join(current_body).strip()
        # Use file path + heading as a stable ID
        slug = title.lower().replace(" ", "-")
        doc_id = f"concept:{os.path.abspath(file_path)}#{slug}"

        # Summary: first sentence or line
        summary_line = body.split("\n", 1)[0] if body else title
        summary_line = summary_line.strip()

        doc = DocObject(
            doc_id=doc_id,
            doc_type=DOC_TYPE_CONCEPT,
            title=title,
            summary=summary_line[:300],
            details=body,
            language="markdown",
            kind=f"heading{current_level}",
            module=None,
            file_path=os.path.abspath(file_path),
            signature=None,
            parameters=None,
            returns=None,
            examples=None,
            tags="markdown,concept,notes",
            source_refs=None,
            created_at=now,
            updated_at=now,
        )
        docs.append(doc)
        current_heading = None
        current_body = []
        current_level = None

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#") and not stripped.startswith("###### #"):
            # New heading encountered
            flush_current()
            hashes = len(stripped) - len(stripped.lstrip("#"))
            heading_text = stripped[hashes:].strip(" #") or "Untitled"
            current_heading = heading_text
            current_level = hashes
            current_body = []
        else:
            if current_heading is not None:
                current_body.append(line)

    # Flush final heading
    flush_current()
    return docs


# ------------------------------------------------------------------
# Directory scanning
# ------------------------------------------------------------------


def iter_files(root: str, exts: Tuple[str, ...]) -> Iterable[str]:
    """Yield file paths under `root` with extensions in `exts`."""
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.startswith("."):
                continue
            if os.path.splitext(name)[1].lower() in exts:
                yield os.path.join(dirpath, name)


def scan_path_for_docs(conn: sqlite3.Connection, root: str) -> None:
    """Scan a root directory for Python/Markdown docs and upsert them."""
    logger.info("Scanning root: %s", root)
    root = os.path.abspath(root)

    # Python files
    for py_path in iter_files(root, (".py",)):
        for doc in extract_functions_and_classes(py_path, root):
            upsert_doc(conn, doc)

    # Markdown files
    for md_path in iter_files(root, (".md", ".markdown")):
        for doc in extract_concepts_from_markdown(md_path):
            upsert_doc(conn, doc)

    logger.info("Completed scan for root: %s", root)


# ------------------------------------------------------------------
# CLI presentation helpers
# ------------------------------------------------------------------


def format_doc_for_console(row: sqlite3.Row) -> str:
    """Render a documentation row as a human-readable text block."""
    title = row["title"]
    doc_id = row["doc_id"]
    doc_type = row["doc_type"]
    summary = row["summary"] or "(no summary)"
    details = row["details"] or ""
    language = row["language"] or "n/a"
    file_path = row["file_path"] or "n/a"
    updated_at = row["updated_at"] or "n/a"

    wrapper = textwrap.TextWrapper(width=88, subsequent_indent="    ")

    lines = [
        f"ID:        {doc_id}",
        f"Title:     {title}",
        f"Type:      {doc_type}",
        f"Language:  {language}",
        f"File:      {file_path}",
        f"Updated:   {updated_at}",
        "",
        "Summary:",
    ]
    lines.extend(wrapper.wrap(summary))
    if details:
        lines.append("\nDetails:")
        lines.extend(wrapper.wrap(details))

    return "\n".join(lines)


def print_search_results(rows: List[sqlite3.Row]) -> None:
    if not rows:
        print("No results found.")
        return
    for row in rows:
        print("-" * 80)
        print(format_doc_for_console(row))
    print("-" * 80)
    print(f"Total results: {len(rows)}")


# ------------------------------------------------------------------
# CLI entrypoints
# ------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DocBrain: personal documentation engine (MVP)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db",
        dest="db_path",
        default=DEFAULT_DB_PATH,
        help="Path to the SQLite database.",
    )
    parser.add_argument(
        "--log",            dest="log_path",            default=DEFAULT_LOG_PATH,            help="Path to the log file.",        )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init-db
    subparsers.add_parser("init-db", help="Initialize the database schema.")

    # scan
    scan_parser = subparsers.add_parser(
        "scan", help="Scan one or more directories for documentation candidates."
    )
    scan_parser.add_argument(
        "paths",
        nargs="+",            help="One or more root directories to scan.",
    )

    # search
    search_parser = subparsers.add_parser("search", help="Search docs by text.")
    search_parser.add_argument("query", help="Search query text.")
    search_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of results to return.",
    )

    # view
    view_parser = subparsers.add_parser("view", help="View a single doc by ID.")
    view_parser.add_argument("doc_id", help="Documentation identifier.")

    # recent
    recent_parser = subparsers.add_parser(
        "recent", help="Show recently updated documentation entries."
    )
    recent_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results to show.",
    )

    return parser


def cmd_init_db(args: argparse.Namespace) -> int:
    conn = get_connection(args.db_path)
    try:
        init_db(conn)
    finally:
        conn.close()
    print(f"Initialized database at {args.db_path}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    conn = get_connection(args.db_path)
    try:
        init_db(conn)
        for path in args.paths:
            if not os.path.exists(path):
                logger.warning("Path does not exist, skipping: %s", path)
                continue
            scan_path_for_docs(conn, path)
    finally:
        conn.close()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    conn = get_connection(args.db_path)
    try:
        init_db(conn)
        rows = search_docs(conn, args.query, limit=args.limit)
        print_search_results(rows)
    finally:
        conn.close()
    return 0


def cmd_view(args: argparse.Namespace) -> int:
    conn = get_connection(args.db_path)
    try:
        init_db(conn)
        row = get_doc_by_id(conn, args.doc_id)
        if row is None:
            print(f"No doc found with id: {args.doc_id}")
            return 1
        print(format_doc_for_console(row))
    finally:
        conn.close()
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    conn = get_connection(args.db_path)
    try:
        init_db(conn)
        rows = get_recent_docs(conn, limit=args.limit)
        print_search_results(rows)
    finally:
        conn.close()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose, log_path=args.log_path)
    logger.debug("Starting docbrain with args: %s", args)

    command = args.command
    if command == "init-db":
        return cmd_init_db(args)
    elif command == "scan":
        return cmd_scan(args)
    elif command == "search":
        return cmd_search(args)
    elif command == "view":
        return cmd_view(args)
    elif command == "recent":
        return cmd_recent(args)
    else:  # pragma: no cover - defensive
        parser.error(f"Unknown command: {command}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
