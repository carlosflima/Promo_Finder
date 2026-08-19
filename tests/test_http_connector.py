import pytest

from app.search.http_connector import HttpConnector, HttpPolicy


def test_http_connector_passes_timeout():
    calls = []

    def request(url, **kwargs):
        calls.append((url, kwargs))
        return {"ok": True}

    result = HttpConnector(request, HttpPolicy(timeout_seconds=3, retries=0)).get_json("https://example.com")
    assert result == {"ok": True}
    assert calls[0][1]["timeout"] == 3


def test_http_connector_retries_then_raises():
    attempts = []

    def request(url, **kwargs):
        attempts.append(1)
        raise RuntimeError("offline")

    with pytest.raises(RuntimeError):
        HttpConnector(request, HttpPolicy(retries=2)).get_json("https://example.com")
    assert len(attempts) == 3
