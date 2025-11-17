"""Example journaling tool for Gemini.

This is a simple example of how a journaling function might be exposed
to a higher-level agent or OpenAI tool wrapper.
"""

import datetime as _dt
from pathlib import Path
from typing import List

def log_journal_entry(session_id: str, base_dir: str, summary: str,
                      user_prompt: str = "", actions: List[str] | None = None,
                      files_touched: List[str] | None = None,
                      confidence: float | None = None) -> Path:
    """Append a structured entry to a JOURNAL_{SESSION_ID}.md file."""
    actions = actions or []
    files_touched = files_touched or []

    ts = _dt.datetime.utcnow().isoformat() + "Z"
    journals_dir = Path(base_dir).expanduser()
    journals_dir.mkdir(parents=True, exist_ok=True)

    path = journals_dir / f"JOURNAL_{session_id}.md"
    header = f"""\n\n## Entry – {ts}\n\n"""
    body = [header]
    if user_prompt:
        body.append("### User Prompt\n\n````text\n" + user_prompt + "\n````\n\n")
    body.append("### Summary\n\n" + summary + "\n\n")
    if actions:
        body.append("### Actions\n\n" + "\n".join(f"- {a}" for a in actions) + "\n\n")
    if files_touched:
        body.append("### Files Touched\n\n" + "\n".join(f"- {p}" for p in files_touched) + "\n\n")
    if confidence is not None:
        body.append(f"Confidence: {confidence:.1f}%\n")

    with path.open("a", encoding="utf-8") as f:
        f.writelines(body)

    return path
