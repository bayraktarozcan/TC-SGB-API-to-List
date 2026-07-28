"""Tests for normalization: lowercase, trim, trailing dot, IDN/punycode, dedup, invalid removal."""

from __future__ import annotations

from scripts.src.models import IOCType, ValidatedIOC
from scripts.src.normalizer import (
    _normalize_domain,
    _normalize_ip,
    _normalize_url,
    normalize_batch,
    normalize_ioc,
)

# ---------------------------------------------------------------------------
# _normalize_domain
# ---------------------------------------------------------------------------


class TestNormalizeDomain:
    def test_lowercase(self):
        val, notes = _normalize_domain("EVIL.COM")
        assert val == "evil.com"
        assert "lowercased" in notes

    def test_trim(self):
        val, notes = _normalize_domain("  evil.com  ")
        assert val == "evil.com"
        assert "trimmed whitespace" in notes

    def test_trailing_dot(self):
        val, notes = _normalize_domain("evil.com.")
        assert val == "evil.com"
        assert "removed trailing dot" in notes

    def test_leading_dot(self):
        val, notes = _normalize_domain(".evil.com")
        assert val == "evil.com"
        assert "removed leading dot" in notes

    def test_consecutive_dots(self):
        val, notes = _normalize_domain("evil..com")
        assert val == "evil.com"
        assert any("consecutive dots" in n.lower() for n in notes)

    def test_idn_punycode(self):
        val, notes = _normalize_domain("münchen.de")
        assert val == "xn--mnchen-3ya.de"
        assert any("punycode" in n.lower() or "idn" in n.lower() for n in notes)

    def test_already_ascii(self):
        val, notes = _normalize_domain("evil.com")
        assert val == "evil.com"
        assert not any("punycode" in n.lower() for n in notes)

    def test_complex_idn(self):
        val, _notes = _normalize_domain("москва.рф")
        assert "xn--" in val


# ---------------------------------------------------------------------------
# _normalize_url
# ---------------------------------------------------------------------------


class TestNormalizeUrl:
    def test_adds_scheme(self):
        val, notes = _normalize_url("evil.com/path")
        assert val.startswith("https://")
        assert "added https scheme" in notes

    def test_preserves_scheme(self):
        val, notes = _normalize_url("http://evil.com/path")
        assert val.startswith("http://")
        assert "added https scheme" not in notes

    def test_hostname_is_parsed_lowercase(self):
        from urllib.parse import urlparse

        val, _notes = _normalize_url("https://EVIL.COM/path")
        parsed = urlparse(val)
        assert parsed.hostname == "evil.com"

    def test_trims_whitespace(self):
        val, notes = _normalize_url("  https://evil.com  ")
        assert val.startswith("https://")
        assert "trimmed" in notes[0].lower() if notes else False

    def test_preserves_query(self):
        val, _ = _normalize_url("https://evil.com/path?q=1&r=2")
        assert "q=1" in val
        assert "r=2" in val

    def test_preserves_fragment(self):
        val, _ = _normalize_url("https://evil.com/path#section")
        assert "#section" in val

    def test_non_standard_port_preserved_on_normalize(self):
        """Line 76: port_part added when host normalization changes hostname."""
        val, notes = _normalize_url("https://MÜNCHEN.DE:8443/path")
        assert "8443" in val
        assert any("normalized hostname" in n for n in notes)

    def test_standard_port_80_443_not_in_output(self):
        val, notes = _normalize_url("https://MÜNCHEN.DE:443/path")
        assert ":443" not in val


# ---------------------------------------------------------------------------
# _normalize_ip
# ---------------------------------------------------------------------------


class TestNormalizeIP:
    def test_trim(self):
        val, notes = _normalize_ip("  8.8.8.8  ")
        assert val == "8.8.8.8"
        assert "trimmed" in notes[0].lower() if notes else False

    def test_lowercase_ipv6(self):
        val, _notes = _normalize_ip("2001:DB8::1")
        assert val == "2001:db8::1"


# ---------------------------------------------------------------------------
# normalize_ioc (integration)
# ---------------------------------------------------------------------------


class TestNormalizeIOC:
    def test_domain_normalization(self):
        v = ValidatedIOC(raw_url="EVIL.COM.", ioc_type=IOCType.DOMAIN)
        result = normalize_ioc(v)
        assert result is not None
        assert result.value == "evil.com"

    def test_url_normalization(self):
        v = ValidatedIOC(raw_url="HTTPS://EVIL.COM/path", ioc_type=IOCType.URL)
        result = normalize_ioc(v)
        assert result is not None
        assert result.value == "HTTPS://EVIL.COM/path"

    def test_ip_normalization(self):
        v = ValidatedIOC(raw_url="8.8.8.8", ioc_type=IOCType.IP)
        result = normalize_ioc(v)
        assert result is not None
        assert result.value == "8.8.8.8"

    def test_empty_returns_none(self):
        v = ValidatedIOC(raw_url="", ioc_type=IOCType.DOMAIN)
        result = normalize_ioc(v)
        assert result is None

    def test_only_dot_returns_none(self):
        v = ValidatedIOC(raw_url=".", ioc_type=IOCType.DOMAIN)
        result = normalize_ioc(v)
        assert result is None

    def test_preserves_metadata(self):
        v = ValidatedIOC(
            raw_url="EVIL.COM",
            ioc_type=IOCType.DOMAIN,
            criticality_level=3,
            original_id=42,
        )
        result = normalize_ioc(v)
        assert result is not None
        assert result.criticality_level == 3
        assert result.original_id == 42

    def test_notes_populated(self):
        v = ValidatedIOC(raw_url="EVIL.COM.", ioc_type=IOCType.DOMAIN)
        result = normalize_ioc(v)
        assert result is not None
        assert len(result.normalization_notes) > 0

    def test_ip6_normalization(self):
        v = ValidatedIOC(raw_url="2001:DB8::1", ioc_type=IOCType.IP6)
        result = normalize_ioc(v)
        assert result is not None
        assert result.value == "2001:db8::1"

    def test_url_with_idn_hostname(self):
        v = ValidatedIOC(raw_url="https://münchen.de/path", ioc_type=IOCType.URL)
        result = normalize_ioc(v)
        assert result is not None
        assert "xn--" in result.value

    def test_domain_with_whitespace(self):
        v = ValidatedIOC(raw_url="  evil.com  ", ioc_type=IOCType.DOMAIN)
        result = normalize_ioc(v)
        assert result is not None
        assert result.value == "evil.com"


# ---------------------------------------------------------------------------
# normalize_batch
# ---------------------------------------------------------------------------


class TestNormalizeBatch:
    def test_filters_invalid(self):
        iocs = [
            ValidatedIOC(raw_url="EVIL.COM", ioc_type=IOCType.DOMAIN),
            ValidatedIOC(raw_url="", ioc_type=IOCType.DOMAIN),
            ValidatedIOC(raw_url="good.net", ioc_type=IOCType.DOMAIN),
        ]
        result = normalize_batch(iocs)
        assert len(result) == 2

    def test_empty_input(self):
        assert normalize_batch([]) == []

    def test_all_invalid(self):
        iocs = [
            ValidatedIOC(raw_url="", ioc_type=IOCType.DOMAIN),
            ValidatedIOC(raw_url=".", ioc_type=IOCType.DOMAIN),
        ]
        result = normalize_batch(iocs)
        assert len(result) == 0

    def test_batch_lowercase(self):
        iocs = [
            ValidatedIOC(raw_url="A.COM", ioc_type=IOCType.DOMAIN),
            ValidatedIOC(raw_url="B.NET", ioc_type=IOCType.DOMAIN),
        ]
        result = normalize_batch(iocs)
        assert result[0].value == "a.com"
        assert result[1].value == "b.net"
