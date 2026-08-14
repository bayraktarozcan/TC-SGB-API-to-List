"""Cross-type IoC deduplication.

Handles deduplication across domain, URL, IP, IP6, and IP6Net types.
When the same IoC appears multiple times (possibly with different metadata),
the one with the highest quality score is kept, and metadata is merged.
"""

from __future__ import annotations

import logging

from .models import IOCType, ScoredIOC

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_domain_from_url(url: str) -> str | None:
    """Extract the hostname from a URL IoC for cross-type dedup."""
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        host = parsed.hostname
        if host:
            return host.lower().rstrip(".")
    except Exception:  # nosec B110 — intentional fallback for optional DNS resolution
        pass
    return None


def _make_dedup_key(value: str, ioc_type: IOCType) -> str:
    """Create a canonical dedup key."""
    value = value.strip().lower().rstrip(".")
    if ioc_type == IOCType.URL:
        # For URLs, try to extract the domain and add as an alternative key.
        domain = _extract_domain_from_url(value)
        if domain:
            return f"url|{value}|domain|{domain}"
    return f"{ioc_type.value}|{value}"


# ---------------------------------------------------------------------------
# Merge helper
# ---------------------------------------------------------------------------


def _merge_metadata(primary: ScoredIOC, secondary: ScoredIOC) -> ScoredIOC:
    """Merge missing metadata from secondary into primary."""
    if primary.source is None:
        primary.source = secondary.source
    if primary.desc is None:
        primary.desc = secondary.desc
    if primary.connectiontype is None:
        primary.connectiontype = secondary.connectiontype
    return primary


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


class DeduplicationResult:
    """Result of deduplicating a list of scored IoCs."""

    __slots__ = ("kept", "merge_log", "removed_count")

    def __init__(
        self,
        kept: list[ScoredIOC],
        removed_count: int,
        merge_log: list[str],
    ) -> None:
        self.kept = kept
        self.removed_count = removed_count
        self.merge_log = merge_log


def deduplicate(
    scored_iocs: list[ScoredIOC],
    *,
    merge_metadata: bool = True,
) -> DeduplicationResult:
    """Deduplicate a list of scored IoCs.

    Strategy:
    1. Primary dedup: (value, ioc_type) exact match.
    2. Cross-type dedup: domain extracted from URL matches a domain IoC.
    3. When duplicates are found, keep the one with the highest quality_score.
    4. Optionally merge source / desc metadata from all records.

    Parameters
    ----------
    scored_iocs:
        IoCs to deduplicate, already scored.
    merge_metadata:
        If True, merge source, desc, and connectiontype from removed duplicates
        into the kept record's flags for provenance.

    Returns
    -------
    DeduplicationResult with the deduplicated list and statistics.
    """
    # Index by primary key.
    primary: dict[str, ScoredIOC] = {}
    # Secondary index: domain → primary key (for URL-to-domain cross-dedup).
    domain_index: dict[str, str] = {}
    merge_log: list[str] = []

    # Pre-sort so DOMAINs are processed first — ensures domain_index is
    # populated before any URL cross-type check, regardless of input order.
    sorted_iocs = sorted(scored_iocs, key=lambda x: 0 if x.ioc_type == IOCType.DOMAIN else 1)

    for ioc in sorted_iocs:
        # Primary key.
        pkey = _make_dedup_key(ioc.value, ioc.ioc_type)
        if pkey in primary:
            existing = primary[pkey]
            if ioc.quality_score > existing.quality_score:
                merge_log.append(
                    f"Replaced {pkey} "
                    f"(score {existing.quality_score:.3f} → {ioc.quality_score:.3f})"
                )
                if merge_metadata:
                    primary[pkey] = _merge_metadata(ioc, existing)
                else:
                    primary[pkey] = ioc
            else:
                merge_log.append(
                    f"Skipped duplicate {pkey} (kept score {existing.quality_score:.3f})"
                )
                if merge_metadata:
                    primary[pkey] = _merge_metadata(existing, ioc)
            continue

        # Cross-type dedup for URLs: if a URL's domain matches an existing domain IoC.
        if ioc.ioc_type == IOCType.URL:
            domain = _extract_domain_from_url(ioc.value)
            if domain and domain in domain_index:
                existing_key = domain_index[domain]
                domain_existing: ScoredIOC | None = primary.get(existing_key)
                if domain_existing and ioc.quality_score > domain_existing.quality_score:
                    merge_log.append(f"URL {ioc.value} replaced domain {domain} (higher score)")
                    del primary[existing_key]
                    primary[pkey] = ioc
                    domain_index[domain] = pkey
                else:
                    merge_log.append(f"URL {ioc.value} dropped — domain {domain} already present")
                continue

        primary[pkey] = ioc
        if ioc.ioc_type == IOCType.DOMAIN:
            domain_index[ioc.value] = pkey

    kept = list(primary.values())
    removed_count = len(scored_iocs) - len(kept)
    logger.info(
        "Deduplication: %d → %d (removed %d)",
        len(scored_iocs),
        len(kept),
        removed_count,
    )

    return DeduplicationResult(
        kept=kept,
        removed_count=removed_count,
        merge_log=merge_log,
    )
