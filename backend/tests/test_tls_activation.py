import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import URLError


def tls_module():
    path = Path(__file__).resolve().parents[2] / "ops" / "activate_tls.py"
    spec = importlib.util.spec_from_file_location("activate_tls", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_certificate_request_before_both_domains_reach_our_origin():
    module = tls_module()
    with patch.object(module, "urlopen", side_effect=URLError("DNS pending")):
        assert not module.public_origin_ready()


def test_public_probe_must_match_exactly_for_each_domain():
    module = tls_module()
    response = Mock(status=200)
    response.read.return_value = b"not our origin"
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=None)
    with patch.object(module, "urlopen", return_value=response):
        assert not module.public_origin_ready()
    response.read.return_value = module.PROBE.encode()
    with patch.object(module, "urlopen", return_value=response) as request:
        assert module.public_origin_ready()
        assert request.call_count == 2
