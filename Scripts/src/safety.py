"""Publication safety policy for blocklist generation.

Syntax validation answers "is this a well-formed rule?". This module answers
a different question: "is it safe to publish a rule that blocks this host?".
It is shared by the external-feed path and the main IoC pipeline so both
production lines enforce the same guarantees.

Matching is exact-host only, never substring: ``evil-google.com``,
``google.js.cn`` and ``google.com.evil.example.com`` share text with
``google.com`` but are different registrable domains, so none of them is
affected by the ``google.com`` rule. Only an exact entry blocks or holds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Decision(str, Enum):
    """Publication verdict for one indicator."""

    ACCEPT = "accept"
    REJECT = "reject"
    REVIEW = "review"


@dataclass(frozen=True)
class SafetyRecord:
    """One auditable policy decision."""

    source: str
    indicator: str
    decision: Decision
    reason: str
    rule: str | None = None


BLOCKED_EXACT: frozenset[str] = frozenset(
    {
        "google.com",
        "www.google.com",
        "www.linkedin.com",
        "gemini.google.com",
        "aistudio.google.com",
        "accounts.google.com",
        "myaccount.google.com",
        "ogs.google.com",
        "alkalimakersuite-pa.clients6.google.com",
        "ogads-pa.clients6.google.com",
        "youtube.com",
        "www.youtube.com",
        "googlevideo.com",
        "ytimg.com",
    }
)

SHARED_APEX: frozenset[str] = frozenset(
    {
        "docs.google.com",
        "sites.google.com",
        "drive.usercontent.google.com",
        "storage.googleapis.com",
        "firebasestorage.googleapis.com",
    }
)

REASON_BLOCKED = "blocked exact high-impact host"
REASON_SHARED_APEX = "shared user-content infrastructure apex needs review"
REASON_ACCEPTED = "no policy rule matched"
REASON_UNENCODABLE = "unencodable hostname"


def decide_host(host: str, *, source: str) -> SafetyRecord:
    """Decide whether blocking *host* wholesale is safe to publish."""
    text = host.strip().lower().rstrip(".")
    try:
        ascii_host = text.encode("idna").decode("ascii")
    except UnicodeError:
        return SafetyRecord(
            source=source, indicator=host, decision=Decision.REJECT, reason=REASON_UNENCODABLE
        )
    if ascii_host in BLOCKED_EXACT:
        return SafetyRecord(
            source=source, indicator=ascii_host, decision=Decision.REJECT, reason=REASON_BLOCKED
        )
    if ascii_host in SHARED_APEX:
        return SafetyRecord(
            source=source,
            indicator=ascii_host,
            decision=Decision.REVIEW,
            reason=REASON_SHARED_APEX,
        )
    return SafetyRecord(
        source=source, indicator=ascii_host, decision=Decision.ACCEPT, reason=REASON_ACCEPTED
    )


@dataclass
class SafetySummary:
    """Aggregate counts plus the non-accepted records for audit."""

    accepted: int = 0
    rejected: int = 0
    review: int = 0
    records: list[SafetyRecord] = field(default_factory=list)
