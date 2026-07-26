"""Tests for quality scoring and false positive detection."""

from __future__ import annotations

from datetime import datetime

from scripts.src.models import (
    ConnectionType,
    DescriptionCategory,
    IOCType,
    NormalizedIOC,
    ScoredIOC,
    Source,
)
from scripts.src.quality import (
    _extract_domain,
    _has_suspicious_patterns,
    _is_benign_domain,
    _is_benign_ip,
    _is_private_ip,
    filter_false_positives,
    score_ioc,
)


def _make_ioc(
    value: str,
    ioc_type: IOCType = IOCType.DOMAIN,
    desc: DescriptionCategory | None = DescriptionCategory.PHISHING,
    source: Source | None = Source.USOM,
    criticality_level: int = 5,
    date: datetime | None = datetime(2024, 1, 1),
    connectiontype: ConnectionType | None = ConnectionType.PHISHING,
) -> NormalizedIOC:
    return NormalizedIOC(
        value=value, ioc_type=ioc_type, desc=desc, source=source,
        date=date, criticality_level=criticality_level,
        connectiontype=connectiontype,
    )


# ---------------------------------------------------------------------------
# _extract_domain
# ---------------------------------------------------------------------------

class TestExtractDomain:
    def test_plain_domain(self):
        assert _extract_domain("evil.com") == "evil.com"

    def test_url(self):
        assert _extract_domain("https://evil.com/path") == "evil.com"

    def test_trailing_dot(self):
        assert _extract_domain("evil.com.") == "evil.com"

    def test_lowercases(self):
        assert _extract_domain("EVIL.COM") == "evil.com"


# ---------------------------------------------------------------------------
# _is_benign_domain
# ---------------------------------------------------------------------------

class TestIsBenignDomain:
    def test_google(self):
        assert _is_benign_domain("google.com") is True

    def test_microsoft(self):
        assert _is_benign_domain("microsoft.com") is True

    def test_github(self):
        assert _is_benign_domain("github.com") is True

    def test_subdomain_google(self):
        assert _is_benign_domain("mail.google.com") is True

    def test_not_benign(self):
        assert _is_benign_domain("totally-malicious.xyz") is False

    def test_empty(self):
        assert _is_benign_domain("") is False


# ---------------------------------------------------------------------------
# _is_benign_ip
# ---------------------------------------------------------------------------

class TestIsBenignIP:
    def test_cloudflare(self):
        assert _is_benign_ip("1.1.1.1") is True

    def test_google_dns(self):
        assert _is_benign_ip("8.8.8.8") is True

    def test_quad9(self):
        assert _is_benign_ip("9.9.9.9") is True

    def test_not_benign(self):
        assert _is_benign_ip("45.33.32.1") is False


# ---------------------------------------------------------------------------
# _is_private_ip
# ---------------------------------------------------------------------------

class TestIsPrivateIP:
    def test_loopback(self):
        assert _is_private_ip("127.0.0.1") is True

    def test_10_network(self):
        assert _is_private_ip("10.0.0.1") is True

    def test_172_network(self):
        assert _is_private_ip("172.16.0.1") is True

    def test_192_168(self):
        assert _is_private_ip("192.168.1.1") is True

    def test_link_local(self):
        assert _is_private_ip("169.254.1.1") is True

    def test_public(self):
        assert _is_private_ip("8.8.8.8") is False

    def test_invalid(self):
        assert _is_private_ip("not-an-ip") is False


# ---------------------------------------------------------------------------
# _has_suspicious_patterns
# ---------------------------------------------------------------------------

class TestHasSuspiciousPatterns:
    def test_ip_in_domain(self):
        flags = _has_suspicious_patterns("1.2.3.4.evil.com")
        assert "ip_in_domain" in flags

    def test_long_domain(self):
        flags = _has_suspicious_patterns("a" * 60 + ".com")
        assert "long_domain" in flags

    def test_many_hyphens(self):
        flags = _has_suspicious_patterns("a-b-c-d-e-f-g.com")
        assert "many_hyphens" in flags

    def test_numeric_subdomain(self):
        flags = _has_suspicious_patterns("12345.example.com")
        assert "numeric_subdomain" in flags

    def test_very_short(self):
        flags = _has_suspicious_patterns("ab.com")
        assert "very_short_domain" in flags

    def test_clean_domain(self):
        flags = _has_suspicious_patterns("totally-normal-evil.com")
        # May have some flags, but not ip_in_domain
        assert "ip_in_domain" not in flags


# ---------------------------------------------------------------------------
# score_ioc
# ---------------------------------------------------------------------------

class TestScoreIOC:
    def test_malicious_domain_high_score(self):
        ioc = _make_ioc("malware-cnc.evil.xyz")
        scored = score_ioc(ioc)
        assert scored.quality_score >= 80
        assert scored.false_positive_risk == "low"

    def test_benign_domain_low_score(self):
        ioc = _make_ioc("google.com")
        scored = score_ioc(ioc)
        assert scored.quality_score < 40
        assert scored.false_positive_risk in ("medium", "high")
        assert "benign_domain" in scored.flags

    def test_benign_ip_low_score(self):
        ioc = _make_ioc("8.8.8.8", ioc_type=IOCType.IP)
        scored = score_ioc(ioc)
        assert scored.quality_score < 30
        assert "benign_ip" in scored.flags

    def test_private_ip_penalty(self):
        ioc = _make_ioc("192.168.1.1", ioc_type=IOCType.IP)
        scored = score_ioc(ioc)
        assert scored.false_positive_risk in ("medium", "high")
        assert "private_ip" in scored.flags

    def test_no_source_penalty(self):
        ioc = _make_ioc("evil.com", source=None)
        scored = score_ioc(ioc)
        assert "no_source" in scored.flags

    def test_with_source_bonus(self):
        ioc = _make_ioc("evil.com", source=Source.USOM)
        scored = score_ioc(ioc)
        assert "no_source" not in scored.flags

    def test_high_criticality_bonus(self):
        ioc = _make_ioc("evil.com", criticality_level=1)
        scored = score_ioc(ioc)
        assert scored.quality_score > 90

    def test_low_criticality_penalty(self):
        ioc = _make_ioc("evil.com", criticality_level=10, source=None, desc=None, date=None)
        scored = score_ioc(ioc)
        assert scored.quality_score < 90

    def test_score_clamped_to_100(self):
        ioc = _make_ioc("very-evil.net", criticality_level=1,
                        source=Source.USOM, desc=DescriptionCategory.PHISHING)
        scored = score_ioc(ioc)
        assert scored.quality_score <= 100.0

    def test_score_clamped_to_0(self):
        ioc = _make_ioc("google.com", ioc_type=IOCType.IP,
                        source=None, desc=None, criticality_level=10)
        # Override to make it an IP
        ioc.value = "8.8.8.8"
        scored = score_ioc(ioc)
        assert scored.quality_score >= 0.0

    def test_scored_ioc_preserves_metadata(self):
        ioc = _make_ioc("evil.com", criticality_level=3, date=datetime(2024, 6, 1))
        scored = score_ioc(ioc)
        assert scored.criticality_level == 3
        assert scored.date == datetime(2024, 6, 1)

    def test_url_domain_extraction(self):
        ioc = _make_ioc("https://google.com/path", ioc_type=IOCType.URL)
        scored = score_ioc(ioc)
        assert "benign_domain" in scored.flags

    def test_medium_risk_boundary(self):
        # Score ~40 -> medium risk
        ioc = _make_ioc("no-source.com", source=None, desc=None,
                        criticality_level=8)
        scored = score_ioc(ioc)
        # Should be low or medium
        assert scored.false_positive_risk in ("low", "medium")


# ---------------------------------------------------------------------------
# filter_false_positives
# ---------------------------------------------------------------------------

class TestFilterFalsePositives:
    def test_all_pass(self):
        scored = [
            ScoredIOC(value="a.com", ioc_type=IOCType.DOMAIN, quality_score=90),
            ScoredIOC(value="b.com", ioc_type=IOCType.DOMAIN, quality_score=80),
        ]
        accepted, rejected = filter_false_positives(scored, min_score=20)
        assert len(accepted) == 2
        assert rejected == 0

    def test_some_filtered(self):
        scored = [
            ScoredIOC(value="a.com", ioc_type=IOCType.DOMAIN, quality_score=90),
            ScoredIOC(value="b.com", ioc_type=IOCType.DOMAIN, quality_score=10),
        ]
        accepted, rejected = filter_false_positives(scored, min_score=20)
        assert len(accepted) == 1
        assert rejected == 1

    def test_all_filtered(self):
        scored = [
            ScoredIOC(value="a.com", ioc_type=IOCType.DOMAIN, quality_score=5),
            ScoredIOC(value="b.com", ioc_type=IOCType.DOMAIN, quality_score=10),
        ]
        accepted, rejected = filter_false_positives(scored, min_score=20)
        assert len(accepted) == 0
        assert rejected == 2

    def test_empty_input(self):
        accepted, rejected = filter_false_positives([], min_score=20)
        assert accepted == []
        assert rejected == 0

    def test_exact_threshold(self):
        scored = [ScoredIOC(value="a.com", ioc_type=IOCType.DOMAIN, quality_score=20)]
        accepted, rejected = filter_false_positives(scored, min_score=20)
        assert len(accepted) == 1
        assert rejected == 0

    def test_just_below_threshold(self):
        scored = [ScoredIOC(value="a.com", ioc_type=IOCType.DOMAIN, quality_score=19.9)]
        accepted, rejected = filter_false_positives(scored, min_score=20)
        assert len(accepted) == 0
        assert rejected == 1
