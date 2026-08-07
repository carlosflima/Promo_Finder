from app.search.discovery import approved_candidates, discover_candidates
from app.search.trust import assess_site


def test_https_brazilian_store_is_approved():
    assessment = assess_site("https://loja.exemplo.com.br")
    assert assessment.approved
    assert assessment.https
    assert assessment.score >= 60


def test_http_is_not_approved_by_default():
    assessment = assess_site("http://loja.exemplo.com.br")
    assert not assessment.approved


def test_local_host_is_rejected():
    assessment = assess_site("http://localhost:5000")
    assert not assessment.approved


def test_discovery_is_bounded_and_deduplicated():
    candidates = discover_candidates(["https://amazon.com.br", "https://nova-loja.com.br"])
    hosts = [candidate.hostname for candidate in candidates]
    assert len(hosts) == len(set(hosts))
    assert "amazon.com.br" in hosts
    assert "nova-loja.com.br" in hosts


def test_approved_candidates_exclude_http_custom_site():
    candidates = approved_candidates(["http://nova-loja.com.br", "https://nova-loja.com.br"])
    assert all(candidate.trust.approved for candidate in candidates)
