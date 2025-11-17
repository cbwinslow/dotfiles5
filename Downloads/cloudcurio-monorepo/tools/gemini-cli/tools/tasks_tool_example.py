"""Example task list management helper for TASKS.md."""

from pathlib import Path

def append_task(tasks_file: str, task_id: str, description: str, owner: str = "", section: str = "Global Tasks") -> None:
    """Append a markdown checklist item to TASKS.md under the specified section.

    This is intentionally simple and can be replaced with a structured parser later.
    """
    path = Path(tasks_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(f"# Tasks / TODO\n\n## {section}\n\n", encoding="utf-8")

    content = path.read_text(encoding="utf-8")
    marker = f"## {section}\n"
    if marker not in content:
        content += f"\n{marker}\n\n"

    new_line = f"- [ ] {task_id} – {description}"
    if owner:
        new_line += f" – Owner: {owner}"
    new_line += "\n"

    # naive append to end for now
    content += new_line
    path.write_text(content, encoding="utf-8")
