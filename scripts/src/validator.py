"""IOC validation: checks for empty fields, invalid domains, RFC6761,
private TLDs, reserved domains, unicode issues, IP/URL correctness."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from .models import AddressRecord, IOCType, ValidatedIOC

# ---------------------------------------------------------------------------
# RFC 6761 reserved / special-use domains and TLDs
# ---------------------------------------------------------------------------

RFC6761_DOMAINS: set[str] = {
    "localhost",
    "localhost.localdomain",
    "invalid",
    "example",
    "example.com",
    "example.net",
    "example.org",
    "example.invalid",
    "test",
    "test.com",
    "local",
}

PRIVATE_SUFFIXES: tuple[str, ...] = (
    ".local",
    ".localdomain",
    ".lan",
    ".home",
    ".internal",
    ".corp",
    ".intranet",
    ".private",
    ".test",
    ".invalid",
)

RESERVED_DOMAINS: set[str] = {
    "schemas.microsoft.com",
    "schemas.openxmlformats.org",
    "www.w3.org",
    "schemas.android.com",
    "www.oracle.com",
    "docs.oasis-open.org",
    "xml.org",
}

# Maximum domain label length (RFC 952 / 1035)
MAX_LABEL_LEN = 63
MAX_DOMAIN_LEN = 253

_DOMAIN_RE = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*\.[A-Za-z]{2,}$"
)


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _is_valid_ip_network(value: str) -> bool:
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False


def _is_rfc6761(domain: str) -> bool:
    lower = domain.lower()
    if lower in RFC6761_DOMAINS:
        return True
    parts = lower.split(".")
    for i in range(len(parts)):
        if ".".join(parts[i:]) in RFC6761_DOMAINS:
            return True
    return False


def _has_private_suffix(domain: str) -> bool:
    lower = domain.lower()
    return any(lower.endswith(s) for s in PRIVATE_SUFFIXES)


def _is_reserved_domain(domain: str) -> bool:
    lower = domain.lower()
    return lower in RESERVED_DOMAINS or any(lower.endswith(f".{r}") for r in RESERVED_DOMAINS)


def _is_valid_domain(domain: str) -> list[str]:
    errors: list[str] = []
    lower = domain.lower().rstrip(".")
    if len(lower) == 0:
        errors.append("empty domain")
        return errors
    if len(lower) > MAX_DOMAIN_LEN:
        errors.append(f"domain exceeds {MAX_DOMAIN_LEN} characters")
    labels = lower.split(".")
    for label in labels:
        if len(label) == 0:
            errors.append("empty label in domain")
            break
        if len(label) > MAX_LABEL_LEN:
            errors.append(f"label '{label}' exceeds {MAX_LABEL_LEN} characters")
        if not re.match(r"^[A-Za-z0-9-]+$", label):
            errors.append(f"label '{label}' contains invalid characters")
            break
        if label.startswith("-") or label.endswith("-"):
            errors.append(f"label '{label}' starts or ends with hyphen")
            break
    if len(labels) < 2:
        errors.append("domain must have at least two labels")
    if not _DOMAIN_RE.match(lower):
        errors.append("domain does not match expected pattern")
    return errors


def _infer_ioc_type(value: str) -> IOCType | None:
    """Infer IOC type from the value when API type field is not available."""
    value = value.strip()
    if not value:
        return None
    if _is_valid_ip(value):
        addr = ipaddress.ip_address(value)
        return IOCType.IP6 if addr.version == 6 else IOCType.IP
    if "/" in value:
        if _is_valid_ip_network(value):
            network = ipaddress.ip_network(value, strict=False)
            return IOCType.IP6NET if network.version == 6 else IOCType.IP
    # Only treat as URL if it already has an explicit scheme
    if "://" in value:
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https") and parsed.hostname:
            return IOCType.URL
    if "." in value and " " not in value:
        return IOCType.DOMAIN
    return None


def validate_ioc(record: AddressRecord) -> ValidatedIOC | None:
    """Validate a single AddressRecord and return a ValidatedIOC or None if invalid."""
    errors: list[str] = []
    value = record.url.strip()

    if not value:
        return None

    # Use API's type field first, fall back to inference
    api_type = record.type.strip().lower() if record.type else ""
    ioc_type: IOCType | None = None
    if api_type:
        try:
            ioc_type = IOCType(api_type)
        except ValueError:
            ioc_type = _infer_ioc_type(value)
    else:
        ioc_type = _infer_ioc_type(value)
    if ioc_type is None:
        ioc_type = IOCType.DOMAIN

    # Map string fields to enums
    from .models import ConnectionType, DescriptionCategory, Source

    desc_cat: DescriptionCategory | None = None
    if record.desc:
        try:
            desc_cat = DescriptionCategory(record.desc)
        except ValueError:
            pass

    source_enum: Source | None = None
    if record.source:
        try:
            source_enum = Source(record.source)
        except ValueError:
            pass

    conn_type: ConnectionType | None = None
    if record.connectiontype:
        try:
            conn_type = ConnectionType(record.connectiontype)
        except ValueError:
            pass

    if ioc_type in (IOCType.DOMAIN, IOCType.URL):
        # Extract hostname for domain checks
        hostname = value
        if ioc_type == IOCType.URL:
            parsed = urlparse(value if "://" in value else f"https://{value}")
            hostname = parsed.hostname or value

        hostname = hostname.lower().rstrip(".")
        errors.extend(_is_valid_domain(hostname))

        if _is_rfc6761(hostname):
            errors.append(f"RFC 6761 reserved domain: {hostname}")
        if _has_private_suffix(hostname):
            errors.append(f"private/internal TLD: {hostname}")
        if _is_reserved_domain(hostname):
            errors.append(f"reserved/well-known domain: {hostname}")

    if ioc_type in (IOCType.IP, IOCType.IP6, IOCType.IP6NET):
        clean = value.split("/")[0] if "/" in value else value
        if not _is_valid_ip(clean):
            # Might be an IP in URL form
            parsed = urlparse(value if "://" in value else f"https://{value}")
            if parsed.hostname and _is_valid_ip(parsed.hostname):
                pass
            else:
                errors.append(f"invalid IP address: {value}")

    # Parse date string to datetime
    parsed_date = None
    if record.date:
        try:
            from datetime import datetime
            # Handle ISO format dates like "2024-01-15T10:30:00"
            date_str = record.date.replace("Z", "+00:00")
            parsed_date = datetime.fromisoformat(date_str)
        except (ValueError, AttributeError):
            pass

    if errors:
        return ValidatedIOC(
            raw_url=value,
            ioc_type=ioc_type,
            desc=desc_cat,
            source=source_enum,
            date=parsed_date,
            criticality_level=record.criticality_level,
            connectiontype=conn_type,
            original_id=record.id,
            validation_errors=errors,
        )

    return ValidatedIOC(
        raw_url=value,
        ioc_type=ioc_type,
        desc=desc_cat,
        source=source_enum,
        date=parsed_date,
        criticality_level=record.criticality_level,
        connectiontype=conn_type,
        original_id=record.id,
    )


def validate_records_batch(
    records: list[AddressRecord],
) -> tuple[list[ValidatedIOC], list[tuple[AddressRecord, list[str]]]]:
    """Validate a batch of API records.

    Returns (valid, rejected) where rejected is a list of (record, errors).
    """
    valid: list[ValidatedIOC] = []
    rejected: list[tuple[AddressRecord, list[str]]] = []

    for rec in records:
        result = validate_ioc(rec)
        if result is None:
            rejected.append((rec, ["empty or unparseable IOC value"]))
        elif result.validation_errors:
            rejected.append((rec, result.validation_errors))
        else:
            valid.append(result)

    return valid, rejected
