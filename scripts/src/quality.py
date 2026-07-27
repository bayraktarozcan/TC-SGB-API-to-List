"""Quality scoring and false-positive risk detection for IOCs."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from .models import (
    IOCType,
    NormalizedIOC,
    ScoredIOC,
)

# Benign / whitelisted domains that should never appear in threat lists
BENIGN_DOMAINS: set[str] = {
    "google.com",
    "googleapis.com",
    "gstatic.com",
    "github.com",
    "github.io",
    "githubusercontent.com",
    "microsoft.com",
    "windows.com",
    "windowsupdate.com",
    "office.com",
    "office365.com",
    "outlook.com",
    "live.com",
    "azure.com",
    "amazon.com",
    "amazonaws.com",
    "cloudflare.com",
    "cloudfront.net",
    "akamai.com",
    "akamaized.net",
    "apple.com",
    "icloud.com",
    "facebook.com",
    "fbcdn.net",
    "twitter.com",
    "x.com",
    "youtube.com",
    "ytimg.com",
    "mozilla.org",
    "mozilla.com",
    "firefox.com",
    "cloudflare-dns.com",
    "opendns.com",
    "quad9.net",
    "akamai.net",
    "verisign.com",
    "verisign.net",
    "iana.org",
    "rfc-editor.org",
    "w3.org",
}

BENIGN_IPS: set[str] = {
    "1.1.1.1",
    "8.8.8.8",
    "8.8.4.4",
    "9.9.9.9",
    "208.67.222.222",
    "208.67.220.220",
}


def _extract_domain(value: str) -> str | None:
    if "://" in value:
        parsed = urlparse(value)
        return parsed.hostname
    return value.lower().rstrip(".")


def _is_benign_domain(domain: str) -> bool:
    lower = domain.lower()
    if lower in BENIGN_DOMAINS:
        return True
    parts = lower.split(".")
    for i in range(len(parts)):
        candidate = ".".join(parts[i:])
        if candidate in BENIGN_DOMAINS:
            return True
    return False


def _is_benign_ip(ip_str: str) -> bool:
    return ip_str in BENIGN_IPS


def _is_private_ip(ip_str: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip_str)
        return addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local
    except ValueError:
        return False


def _has_suspicious_patterns(domain: str) -> list[str]:
    flags: list[str] = []
    if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        flags.append("ip_in_domain")
    if len(domain) > 50:
        flags.append("long_domain")
    if domain.count("-") > 5:
        flags.append("many_hyphens")
    # Very short random-looking domains
    parts = domain.split(".")
    if parts and len(parts[0]) <= 3 and domain.count(".") == 1:
        flags.append("very_short_domain")
    # Numeric-heavy domains (e.g., 12345abc.example.com)
    if re.search(r"^[0-9]+$", parts[0]) if parts else False:
        flags.append("numeric_subdomain")
    return flags


def score_ioc(ioc: NormalizedIOC) -> ScoredIOC:
    """Compute quality score and false-positive risk for an IOC."""
    score = 100.0
    fp_risk = "low"
    flags: list[str] = []

    domain = _extract_domain(ioc.value)

    # Benign domain check
    if domain and _is_benign_domain(domain):
        score -= 80
        flags.append("benign_domain")
        fp_risk = "high"

    # Benign IP check
    if ioc.ioc_type in (IOCType.IP, IOCType.IP6) and _is_benign_ip(ioc.value):
        score -= 80
        flags.append("benign_ip")
        fp_risk = "high"

    # Private IP check
    if ioc.ioc_type in (IOCType.IP, IOCType.IP6) and _is_private_ip(ioc.value):
        score -= 70
        flags.append("private_ip")
        fp_risk = "high"

    # Suspicious patterns (informational – don't reject, just flag)
    if domain:
        pattern_flags = _has_suspicious_patterns(domain)
        flags.extend(pattern_flags)
        score -= len(pattern_flags) * 5

    # Source confidence
    if ioc.source is not None:
        score += 5
    else:
        score -= 10
        flags.append("no_source")

    # Has description category
    if ioc.desc is not None:
        score += 5

    # Criticality adjustment
    if ioc.criticality_level <= 3:
        score += 10
    elif ioc.criticality_level >= 8:
        score -= 5

    # Has date
    if ioc.date is not None:
        score += 3

    # Clamp
    score = max(0.0, min(100.0, score))

    # Determine risk from score — only elevate risk, never downgrade
    # pattern-based fp_risk (set by checks above) takes precedence
    if score < 20:
        fp_risk = "high"
    elif score < 50:
        if fp_risk == "low":
            fp_risk = "medium"
    # score >= 50: keep whatever fp_risk was set by pattern checks

    return ScoredIOC(
        value=ioc.value,
        ioc_type=ioc.ioc_type,
        desc=ioc.desc,
        source=ioc.source,
        date=ioc.date,
        criticality_level=ioc.criticality_level,
        connectiontype=ioc.connectiontype,
        original_id=ioc.original_id,
        quality_score=score,
        false_positive_risk=fp_risk,
        flags=flags,
    )


DEFAULT_QUALITY_THRESHOLD: float = 20.0


def filter_false_positives(
    scored: list[ScoredIOC], min_score: float = 20.0
) -> tuple[list[ScoredIOC], int]:
    """Filter out IOCs with quality scores below the threshold."""
    accepted: list[ScoredIOC] = []
    rejected = 0
    for ioc in scored:
        if ioc.quality_score >= min_score:
            accepted.append(ioc)
        else:
            rejected += 1
    return accepted, rejected


def score_iocs(
    iocs: list[NormalizedIOC],
    threshold: float = DEFAULT_QUALITY_THRESHOLD,
) -> list[ScoredIOC]:
    """Score a batch of IOCs, filtering out those below the threshold."""
    scored: list[ScoredIOC] = []
    for ioc in iocs:
        s = score_ioc(ioc)
        if s.quality_score >= threshold:
            scored.append(s)
    return scored
