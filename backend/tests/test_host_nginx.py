import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def host_guard(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "fcntl", SimpleNamespace(LOCK_EX=2, flock=lambda *_: None))
    spec = importlib.util.spec_from_file_location("deploy_host_test", ROOT / "ops/deploy_release.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = tmp_path / "00-default-host.conf"
    target.write_text((ROOT / "ops/nginx/host-default.conf").read_text(), encoding="utf-8")
    monkeypatch.setattr(module, "HOST_DEFAULT", target)
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout=f"# configuration file {target}:\n")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    return module, target, calls


def test_host_fallback_is_read_only_when_valid(host_guard):
    module, target, calls = host_guard
    before = target.read_bytes()
    module.verify_host_nginx(ROOT)
    assert target.read_bytes() == before
    assert calls == [
        (["/usr/sbin/nginx", "-T"], {"capture_output": True, "text": True, "timeout": 30})
    ]


@pytest.mark.parametrize("state", ["missing", "changed", "symlink"])
def test_host_fallback_refuses_unexpected_state_without_rewriting(host_guard, monkeypatch, state):
    module, target, calls = host_guard
    if state == "missing":
        target.unlink()
    elif state == "changed":
        target.write_text("# managed by another operator\n", encoding="utf-8")
    else:
        monkeypatch.setattr(Path, "is_symlink", lambda self: self == target)
    before = target.read_bytes() if target.exists() else None
    with pytest.raises(RuntimeError, match="missing or changed"):
        module.verify_host_nginx(ROOT)
    assert (target.read_bytes() if target.exists() else None) == before
    assert calls == []


@pytest.mark.parametrize("returncode, output", [(1, ""), (0, "# unrelated configuration")])
def test_host_fallback_requires_valid_loaded_configuration(host_guard, monkeypatch, returncode, output):
    module, target, _ = host_guard
    before = target.read_bytes()
    monkeypatch.setattr(
        module.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=returncode, stdout=output)
    )
    with pytest.raises(RuntimeError, match="deployment stopped"):
        module.verify_host_nginx(ROOT)
    assert target.read_bytes() == before


def test_fallback_never_routes_to_an_application():
    config = (ROOT / "ops/nginx/host-default.conf").read_text()
    for listener in ("80", "[::]:80", "443 ssl", "[::]:443 ssl"):
        assert f"listen {listener} default_server;" in config
    assert "ssl_reject_handshake on;" in config
    assert config.count("return 404;") == 2
    assert "proxy_pass" not in config
    assert "return 301" not in config
    assert "return 302" not in config


def test_guard_runs_before_release_preparation_or_service_changes():
    source = (ROOT / "ops/deploy_release.py").read_text()
    main = source.split("def main():", 1)[1]
    assert main.index("verify_host_nginx(release)") < main.index("prepare_release(")
    assert main.index("verify_host_nginx(release)") < main.index("compose(")
