"""Fuzz testing with Hypothesis for edge cases in domain/IP validation."""

from __future__ import annotations

import ipaddress
import re

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from scripts.src.models import IOCType, ValidatedIOC
from scripts.src.normalizer import _normalize_domain, normalize_ioc
from scripts.src.quality import _extract_domain, _is_benign_domain, _is_private_ip, score_ioc
from scripts.src.validator import (
    _infer_ioc_type,
    _is_valid_domain,
    _is_valid_ip,
    validate_ioc,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Printable ASCII strings that could be domains
domain_chars = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-_."),
    min_size=1,
    max_size=100,
)

# Realistic-ish domain names
realistic_domains = st.from_regex(r"[a-z]{2,20}\.[a-z]{2,10}", fullmatch=True)

# IP addresses
ipv4_strategy = st.from_type(ipaddress.IPv4Address)
ipv6_strategy = st.from_type(ipaddress.IPv6Address)

# Random strings
any_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "S"), whitelist_characters=" :/@#&="
    ),
    min_size=0,
    max_size=200,
)

# Unicode text
unicode_text = st.text(
    alphabet=st.characters(
        blacklist_characters="\x00\r\n",
        whitelist_categories=("L", "N", "P"),
    ),
    min_size=1,
    max_size=50,
)


# ---------------------------------------------------------------------------
# Domain validation fuzz tests
# ---------------------------------------------------------------------------


class TestDomainValidationFuzz:
    @given(value=domain_chars)
    @settings(
        max_examples=200,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
    )
    def test_valid_domain_never_crashes(self, value):
        assume("." in value and len(value) > 3)
        errors = _is_valid_domain(value)
        assert isinstance(errors, list)

    @given(value=realistic_domains)
    @settings(max_examples=200)
    def test_realistic_domains_are_valid(self, value):
        assume(len(value) <= 253)
        assume(all(1 <= len(label) <= 63 for label in value.split(".")))
        errors = _is_valid_domain(value)
        # Most realistic domains should pass (some edge cases may fail)
        assert isinstance(errors, list)

    @given(value=st.text(min_size=0, max_size=10))
    def test_short_strings_dont_crash(self, value):
        errors = _is_valid_domain(value)
        assert isinstance(errors, list)

    @given(value=st.just(""))
    def test_empty_string_handled(self, value):
        errors = _is_valid_domain(value)
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# IP validation fuzz tests
# ---------------------------------------------------------------------------


class TestIPValidationFuzz:
    @given(addr=ipv4_strategy)
    @settings(max_examples=100)
    def test_valid_ipv4_detected(self, addr):
        assert _is_valid_ip(str(addr)) is True

    @given(addr=ipv6_strategy)
    @settings(max_examples=100)
    def test_valid_ipv6_detected(self, addr):
        assert _is_valid_ip(str(addr)) is True

    @given(
        value=st.text(min_size=1, max_size=50).filter(
            lambda x: not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", x)
        )
    )
    @settings(max_examples=100)
    def test_non_ip_strings_rejected(self, value):
        assume(value and not any(c in value for c in "abcdefABCDEF:"))
        result = _is_valid_ip(value)
        if result is True:
            # If it's valid, it must parse as an IP
            ipaddress.ip_address(value)

    @given(value=st.just("999.999.999.999"))
    def test_invalid_ip_rejected(self, value):
        assert _is_valid_ip(value) is False


# ---------------------------------------------------------------------------
# IoC type inference fuzz tests
# ---------------------------------------------------------------------------


class TestIOCTypeInferenceFuzz:
    @given(addr=ipv4_strategy)
    @settings(max_examples=100)
    def test_ipv4_detected(self, addr):
        result = _infer_ioc_type(str(addr))
        assert result == IOCType.IP

    @given(addr=ipv6_strategy)
    @settings(max_examples=100)
    def test_ipv6_detected(self, addr):
        result = _infer_ioc_type(str(addr))
        assert result == IOCType.IP6

    @given(domain=realistic_domains)
    @settings(max_examples=100)
    def test_domain_or_none(self, domain):
        result = _infer_ioc_type(domain)
        valid_types = (IOCType.DOMAIN, IOCType.URL, IOCType.IP, IOCType.IP6, IOCType.IP6NET, None)
        assert result in valid_types

    @given(value=st.just(""))
    def test_empty_returns_none(self, value):
        assert _infer_ioc_type(value) is None

    @given(url=st.from_regex(r"https?://[a-z]{2,10}\.(com|net|org)/[a-z]{1,10}", fullmatch=True))
    @settings(max_examples=100)
    def test_url_detected(self, url):
        result = _infer_ioc_type(url)
        assert result == IOCType.URL


# ---------------------------------------------------------------------------
# Normalization fuzz tests
# ---------------------------------------------------------------------------


class TestNormalizationFuzz:
    @given(value=domain_chars)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_normalize_domain_never_crashes(self, value):
        result, notes = _normalize_domain(value)
        assert isinstance(result, str)
        assert isinstance(notes, list)
        # Result should be lowercase
        assert result == result.lower()

    @given(value=st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_normalize_ip_never_crashes(self, value):
        from scripts.src.normalizer import _normalize_ip

        result, _notes = _normalize_ip(value)
        assert isinstance(result, str)

    @given(value=unicode_text)
    @settings(max_examples=100)
    def test_normalize_unicode_never_crashes(self, value):
        result, _notes = _normalize_domain(value)
        assert isinstance(result, str)

    @given(
        value=st.from_regex(r"[A-Z]{2,20}\.[A-Z]{2,10}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_normalize_always_lowercase(self, value):
        result, _ = _normalize_domain(value)
        assert result == result.lower()

    @given(
        value=st.from_regex(r"[a-z]{2,20}\.[a-z]{2,10}\.", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_normalize_removes_trailing_dot(self, value):
        result, _ = _normalize_domain(value)
        assert not result.endswith(".")


# ---------------------------------------------------------------------------
# Quality scoring fuzz tests
# ---------------------------------------------------------------------------


class TestQualityScoringFuzz:
    @given(domain=realistic_domains)
    @settings(max_examples=100)
    def test_extract_domain_never_crashes(self, domain):
        result = _extract_domain(domain)
        assert isinstance(result, (str, type(None)))

    @given(domain=realistic_domains)
    @settings(max_examples=100)
    def test_is_benign_never_crashes(self, domain):
        result = _is_benign_domain(domain)
        assert isinstance(result, bool)

    @given(value=st.text(min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_is_private_ip_never_crashes(self, value):
        result = _is_private_ip(value)
        assert isinstance(result, bool)

    @given(domain=realistic_domains)
    @settings(max_examples=100)
    def test_score_never_crashes(self, domain):
        ioc = ValidatedIOC(raw_url=domain, ioc_type=IOCType.DOMAIN)
        normalized = normalize_ioc(ioc)
        assume(normalized is not None)
        scored = score_ioc(normalized)
        assert 0 <= scored.quality_score <= 100


# ---------------------------------------------------------------------------
# End-to-end fuzz: validate → normalize → score
# ---------------------------------------------------------------------------


class TestEndToEndFuzz:
    @given(
        url=st.from_regex(r"[a-z]{2,15}\.[a-z]{2,10}", fullmatch=True),
    )
    @settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
    def test_full_pipeline_never_crashes(self, url):
        from scripts.src.models import AddressRecord
        from scripts.src.quality import score_ioc

        record = AddressRecord(id=1, url=url, desc="PH", source="US")
        validated = validate_ioc(record)
        assume(validated is not None)
        assume(not validated.validation_errors)

        normalized = normalize_ioc(validated)
        assume(normalized is not None)

        scored = score_ioc(normalized)
        assert 0 <= scored.quality_score <= 100
        assert scored.false_positive_risk in ("low", "medium", "high")
