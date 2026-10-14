import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


def test_frontend_health_retries_startup_connection_resets_with_a_time_bound(monkeypatch):
    # Import the Linux deployment helper on Windows without acquiring any lock.
    monkeypatch.setitem(sys.modules, "fcntl", SimpleNamespace(LOCK_EX=2, flock=lambda *_: None))
    path = Path(__file__).resolve().parents[2] / "ops" / "deploy_release.py"
    spec = importlib.util.spec_from_file_location("deploy_release_health_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    commands = []
    monkeypatch.setattr(module, "run", lambda command: commands.append(command))

    module.frontend_healthy()

    assert len(commands) == 1
    command = commands[0]
    assert command[0] == "curl"
    assert "--fail" in command
    assert "--retry-all-errors" in command
    assert command[command.index("--retry") + 1] == "5"
    assert command[command.index("--retry-max-time") + 1] == "60"
    assert command[command.index("--max-time") + 1] == "10"
    assert command[-1] == "http://127.0.0.1:8080/health/"
