"""Domain/IP normalization: lowercase, trim, trailing dot removal,
IDN/punycode conversion, dedup preparation, invalid domain removal."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import IOCType, NormalizedIOC, ValidatedIOC


def _normalize_domain(value: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    original = value

    # Trim whitespace
    value = value.strip()
    if value != original:
        notes.append("trimmed whitespace")

    # Lowercase
    lower = value.lower()
    if lower != value:
        notes.append("lowercased")
    value = lower

    # Remove trailing dot
    if value.endswith("."):
        value = value[:-1]
        notes.append("removed trailing dot")

    # Remove leading dot
    if value.startswith("."):
        value = value[1:]
        notes.append("removed leading dot")

    # IDN / Punycode conversion
    try:
        encoded = value.encode("idna").decode("ascii")
        if encoded != value:
            notes.append(f"IDN→punycode: {value} → {encoded}")
            value = encoded
    except (UnicodeError, UnicodeDecodeError):
        notes.append(f"IDN encoding failed for {value}")

    # Remove consecutive dots
    if ".." in value:
        value = re.sub(r"\.{2,}", ".", value)
        notes.append("removed consecutive dots")

    return value, notes


def _normalize_url(value: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    original = value

    value = value.strip()
    if value != original:
        notes.append("trimmed whitespace")

    # Ensure scheme
    if not re.match(r"^https?://", value, re.IGNORECASE):
        value = f"https://{value}"
        notes.append("added https scheme")

    parsed = urlparse(value)

    if parsed.hostname:
        norm_host, host_notes = _normalize_domain(parsed.hostname)
        notes.extend(host_notes)
        if norm_host != parsed.hostname:
            # Reconstruct URL
            port_part = ""
            if parsed.port and parsed.port not in (80, 443):
                port_part = f":{parsed.port}"
            path_part = parsed.path or ""
            query_part = f"?{parsed.query}" if parsed.query else ""
            fragment_part = f"#{parsed.fragment}" if parsed.fragment else ""
            scheme = parsed.scheme or "https"
            value = f"{scheme}://{norm_host}{port_part}{path_part}{query_part}{fragment_part}"
            notes.append("normalized hostname in URL")

    return value, notes


def _normalize_ip(value: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    original = value
    value = value.strip()
    if value != original:
        notes.append("trimmed whitespace")
    value = value.lower()
    return value, notes


def normalize_ioc(validated: ValidatedIOC) -> NormalizedIOC | None:
    """Normalize a ValidatedIOC. Returns None only if normalization is impossible."""
    value = validated.raw_url.strip()
    if not value:
        return None

    notes: list[str] = []

    if validated.ioc_type == IOCType.DOMAIN:
        value, dom_notes = _normalize_domain(value)
        notes.extend(dom_notes)
    elif validated.ioc_type == IOCType.URL:
        value, url_notes = _normalize_url(value)
        notes.extend(url_notes)
    elif validated.ioc_type in (IOCType.IP, IOCType.IP6, IOCType.IP6NET):
        value, ip_notes = _normalize_ip(value)
        notes.extend(ip_notes)

    # After normalization, reject obviously invalid values
    if not value or value == "." or value == "-":
        notes.append("rejected empty/invalid after normalization")
        return None

    return NormalizedIOC(
        value=value,
        ioc_type=validated.ioc_type,
        desc=validated.desc,
        source=validated.source,
        date=validated.date,
        criticality_level=validated.criticality_level,
        connectiontype=validated.connectiontype,
        original_id=validated.original_id,
        normalization_notes=notes,
    )


def normalize_batch(validated_list: list[ValidatedIOC]) -> list[NormalizedIOC]:
    """Normalize a batch of validated IOCs, filtering out invalid ones."""
    results: list[NormalizedIOC] = []
    for v in validated_list:
        normalized = normalize_ioc(v)
        if normalized is not None:
            results.append(normalized)
    return results
