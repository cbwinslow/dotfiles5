import pathlib
from tools import gemini_extension_installer as inst

def test_state_roundtrip(tmp_path: pathlib.Path):
    state_file = tmp_path / "state.json"
    state = {"ext-1": {"version": "1.0.0"}}
    inst.save_state(state_file, state)
    loaded = inst.load_state(state_file)
    assert loaded == state
