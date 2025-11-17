import pathlib
from tools import journaling_tool_example as j

def test_log_journal_entry(tmp_path: pathlib.Path):
    session_id = "TEST-SESSION"
    base_dir = str(tmp_path)
    path = j.log_journal_entry(session_id, base_dir, summary="Test entry")
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Test entry" in content
