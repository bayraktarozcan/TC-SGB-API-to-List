"""Tests for IOC validation: empty fields, invalid domains, RFC6761,
private TLDs, reserved domains, unicode, IP, URL validation."""

from __future__ import annotations

from scripts.src.models import AddressRecord, IOCType
from scripts.src.validator import (
    _has_private_suffix,
    _infer_ioc_type,
    _is_reserved_domain,
    _is_rfc6761,
    _is_valid_domain,
    _is_valid_ip,
    _is_valid_ip_network,
    validate_ioc,
)

# ---------------------------------------------------------------------------
# _is_valid_ip
# ---------------------------------------------------------------------------


class TestIsValidIP:
    def test_valid_ipv4(self):
        assert _is_valid_ip("8.8.8.8") is True

    def test_valid_ipv6(self):
        assert _is_valid_ip("2001:db8::1") is True

    def test_invalid(self):
        assert _is_valid_ip("999.999.999.999") is False
        assert _is_valid_ip("not-an-ip") is False
        assert _is_valid_ip("") is False

    def test_loopback(self):
        assert _is_valid_ip("127.0.0.1") is True


class TestIsValidIPNetwork:
    def test_valid_cidr(self):
        assert _is_valid_ip_network("192.168.0.0/24") is True

    def test_valid_ipv6_cidr(self):
        assert _is_valid_ip_network("2001:db8::/32") is True

    def test_invalid(self):
        assert _is_valid_ip_network("not-a-network") is False


# ---------------------------------------------------------------------------
# _is_rfc6761
# ---------------------------------------------------------------------------


class TestIsRFC6761:
    def test_localhost(self):
        assert _is_rfc6761("localhost") is True

    def test_example_com(self):
        assert _is_rfc6761("example.com") is True

    def test_example_net(self):
        assert _is_rfc6761("example.net") is True

    def test_example_org(self):
        assert _is_rfc6761("example.org") is True

    def test_test_tld(self):
        assert _is_rfc6761("test") is True

    def test_invalid(self):
        assert _is_rfc6761("invalid") is True

    def test_not_rfc6761(self):
        assert _is_rfc6761("evil.com") is False

    def test_case_insensitive(self):
        assert _is_rfc6761("LOCALHOST") is True
        assert _is_rfc6761("Example.COM") is True


# ---------------------------------------------------------------------------
# _has_private_suffix
# ---------------------------------------------------------------------------


class TestHasPrivateSuffix:
    def test_local(self):
        assert _has_private_suffix("myhost.local") is True

    def test_lan(self):
        assert _has_private_suffix("printer.lan") is True

    def test_home(self):
        assert _has_private_suffix("nas.home") is True

    def test_corp(self):
        assert _has_private_suffix("internal.corp") is True

    def test_not_private(self):
        assert _has_private_suffix("evil.com") is False

    def test_test_suffix(self):
        assert _has_private_suffix("sandbox.test") is True


# ---------------------------------------------------------------------------
# _is_reserved_domain
# ---------------------------------------------------------------------------


class TestIsReservedDomain:
    def test_w3_org(self):
        assert _is_reserved_domain("www.w3.org") is True

    def test_microsoft(self):
        assert _is_reserved_domain("schemas.microsoft.com") is True

    def test_not_reserved(self):
        assert _is_reserved_domain("evil.com") is False

    def test_subdomain_of_reserved(self):
        assert _is_reserved_domain("sub.schemas.microsoft.com") is True


# ---------------------------------------------------------------------------
# _is_valid_domain
# ---------------------------------------------------------------------------


class TestIsValidDomain:
    def test_valid_simple(self):
        errors = _is_valid_domain("evil.com")
        assert errors == []

    def test_empty(self):
        errors = _is_valid_domain("")
        assert any("empty" in e for e in errors)

    def test_single_label(self):
        errors = _is_valid_domain("localhost")
        assert any("two labels" in e for e in errors)

    def test_too_long_label(self):
        errors = _is_valid_domain("a" * 64 + ".com")
        assert any("exceeds" in e for e in errors)

    def test_invalid_chars(self):
        errors = _is_valid_domain("evil_domain.com")
        assert any("invalid characters" in e for e in errors)

    def test_hyphen_start(self):
        errors = _is_valid_domain("-evil.com")
        assert any("hyphen" in e for e in errors)

    def test_hyphen_end(self):
        errors = _is_valid_domain("evil-.com")
        assert any("hyphen" in e for e in errors)

    def test_too_long_total(self):
        errors = _is_valid_domain("a" * 200 + "." + "b" * 50 + ".com")
        assert any("253 characters" in e for e in errors)


# ---------------------------------------------------------------------------
# _infer_ioc_type
# ---------------------------------------------------------------------------


class TestInferIOCType:
    def test_ipv4(self):
        assert _infer_ioc_type("8.8.8.8") == IOCType.IP

    def test_ipv6(self):
        assert _infer_ioc_type("2001:db8::1") == IOCType.IP6

    def test_ipv4_cidr(self):
        assert _infer_ioc_type("10.0.0.0/8") == IOCType.IP

    def test_ipv6_cidr(self):
        assert _infer_ioc_type("2001:db8::/32") == IOCType.IP6NET

    def test_domain(self):
        assert _infer_ioc_type("evil.com") == IOCType.DOMAIN

    def test_url_http(self):
        assert _infer_ioc_type("http://evil.com/path") == IOCType.URL

    def test_url_https(self):
        assert _infer_ioc_type("https://evil.com/path?q=1") == IOCType.URL

    def test_invalid_returns_none(self):
        assert _infer_ioc_type("") is None


# ---------------------------------------------------------------------------
# validate_ioc (integration)
# ---------------------------------------------------------------------------


class TestValidateIOC:
    def test_empty_record(self):
        r = AddressRecord(id=1, url="")
        assert validate_ioc(r) is None

    def test_valid_domain(self):
        r = AddressRecord(id=1, url="example-phishing.net", desc="PH", source="US")
        result = validate_ioc(r)
        assert result is not None
        assert result.ioc_type == IOCType.DOMAIN
        assert result.validation_errors == []

    def test_valid_ip(self):
        r = AddressRecord(id=1, url="192.0.2.1", desc="CA", source="RS")
        result = validate_ioc(r)
        assert result is not None
        assert result.ioc_type == IOCType.IP

    def test_valid_url(self):
        r = AddressRecord(id=1, url="https://evil.com/path", desc="MU", source="IH")
        result = validate_ioc(r)
        assert result is not None
        assert result.ioc_type == IOCType.URL

    def test_rfc6761_domain(self):
        r = AddressRecord(id=1, url="localhost")
        result = validate_ioc(r)
        assert result is not None
        assert any("RFC 6761" in e for e in result.validation_errors)

    def test_rfc6761_example_com(self):
        r = AddressRecord(id=1, url="example.com")
        result = validate_ioc(r)
        assert result is not None
        assert any("RFC 6761" in e for e in result.validation_errors)

    def test_private_tld(self):
        r = AddressRecord(id=1, url="myhost.local")
        result = validate_ioc(r)
        assert result is not None
        errs = result.validation_errors
        assert any("private" in e.lower() or "internal" in e.lower() for e in errs)

    def test_reserved_domain(self):
        r = AddressRecord(id=1, url="schemas.microsoft.com")
        result = validate_ioc(r)
        assert result is not None
        errs = result.validation_errors
        assert any("reserved" in e.lower() or "well-known" in e.lower() for e in errs)

    def test_whitespace_trimmed(self):
        r = AddressRecord(id=1, url="  evil.com  ")
        result = validate_ioc(r)
        assert result is not None
        assert result.raw_url == "evil.com"  # stripped by validator

    def test_enum_mapping(self):
        r = AddressRecord(id=1, url="evil.com", desc="PH", source="US", connectiontype="PH")
        result = validate_ioc(r)
        assert result is not None
        assert result.desc.value == "PH"
        assert result.source.value == "US"

    def test_invalid_enum_mapping(self):
        r = AddressRecord(id=1, url="evil.com", desc="INVALID_CODE")
        result = validate_ioc(r)
        assert result is not None
        assert result.desc is None  # invalid code -> None

    def test_valid_ipv6_cidr(self):
        r = AddressRecord(id=1, url="2001:db8::/32", type="ip6net")
        result = validate_ioc(r)
        assert result is not None
        assert result.ioc_type == IOCType.IP6NET

    def test_invalid_ip_address(self):
        r = AddressRecord(id=1, url="999.999.999.999", type="ip")
        result = validate_ioc(r)
        assert result is not None
        assert any("invalid IP" in e for e in result.validation_errors)
