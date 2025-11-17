"""Example memory tool stub for Gemini.

This is a placeholder for a real memory subsystem (e.g., SQLite + vectors).
"""

from dataclasses import dataclass
from pathlib import Path
import json
import datetime as _dt
from typing import Literal

@dataclass
class MemoryEntry:
    scope: Literal["global", "project", "task"]
    summary: str
    outcome: Literal["success", "failure", "partial"]
    project_id: str | None = None
    task_id: str | None = None
    created_at: str | None = None

def write_memory(base_path: str, entry: MemoryEntry) -> None:
    """Append a memory entry to a simple JSONL log for now."""
    path = Path(base_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    record = entry.__dict__.copy()
    record["created_at"] = record.get("created_at") or _dt.datetime.utcnow().isoformat() + "Z"

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
