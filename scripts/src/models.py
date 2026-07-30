"""Pydantic models for T.C. Siber Güvenlik Başkanlığı API responses and internal data."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IOCType(str, Enum):
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"


class DescriptionCategory(str, Enum):
    PHISHING = "PH"
    FINANCIAL_PHISHING = "BP"
    MALWARE_DIST_DOMAIN = "MD"
    MALWARE_DIST_IP = "MI"
    MALWARE_DIST_URL = "MU"
    MALWARE_CMD_CENTER = "MC"
    CYBER_ATTACK = "CA"


class Source(str, Enum):
    USOM = "US"
    SOME = "SO"
    RSA = "RS"
    IHBAR = "IH"
    SGB = "SB"


class ConnectionType(str, Enum):
    APT_CNC = "AC"
    BOTNET_CNC = "BC"
    EXPLOIT_KIT = "EK"
    MOBILE_CNC = "MC"
    MALWARE_DOWNLOAD = "MF"
    MINING_MALWARE = "MM"
    OTHER = "OT"
    PHISHING = "PH"


# ---------------------------------------------------------------------------
# API response wrappers — matching real SGB API field names
# ---------------------------------------------------------------------------

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response from the SGB API.

    Real API fields: totalCount, count, models, page, pageCount
    """

    models: list[T] = Field(default_factory=list)
    totalCount: int = 0
    count: int = 0
    page: int = 0
    pageCount: int = 0


class AddressRecord(BaseModel):
    """Single IoC record from /api/address/index.

    Real API fields: id, url, type, desc, source, date, criticality_level, connectiontype
    """

    id: int
    url: str = ""
    type: str = ""
    desc: str = ""
    source: str = ""
    date: str = ""
    criticality_level: int = Field(default=10)
    connectiontype: str = ""


class DescriptionRecord(BaseModel):
    """Record from /api/address-description/index.

    Real API fields: id, tr_title, en_title, tr_desc, en_desc
    """

    id: str
    tr_title: str = ""
    en_title: str = ""
    tr_desc: str = ""
    en_desc: str = ""


class ConnectionTypeRecord(BaseModel):
    """Record from /api/address-connection-type/index.

    Real API fields: id, tr_title, en_title
    """

    id: str
    tr_title: str = ""
    en_title: str = ""


class SourceRecord(BaseModel):
    """Record from /api/address-source/index.

    Real API fields: id, tr_title, en_title
    """

    id: str
    tr_title: str = ""
    en_title: str = ""


class IncidentRecord(BaseModel):
    """Record from /api/incident/index."""

    id: int
    title: str = ""
    desc: str = ""
    date: str = ""
    active: bool = True
    slug: str = ""
    language: str = ""


class AnnouncementRecord(BaseModel):
    """Record from /api/announcement/index."""

    id: int
    title: str = ""
    desc: str = ""
    date: str = ""
    active: bool = True
    slug: str = ""
    language: str = ""


# ---------------------------------------------------------------------------
# Internal / pipeline models
# ---------------------------------------------------------------------------


class ValidatedIOC(BaseModel):
    """An IoC that has passed validation."""

    raw_url: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    validation_errors: list[str] = Field(default_factory=list)


class NormalizedIOC(BaseModel):
    """An IoC that has been normalised (lowercase, trimmed, IDN resolved, etc.)."""

    value: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    normalization_notes: list[str] = Field(default_factory=list)


class ScoredIOC(BaseModel):
    """An IoC with a quality / confidence score."""

    value: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    quality_score: float = 0.0
    false_positive_risk: str = "low"
    flags: list[str] = Field(default_factory=list)


class PipelineStats(BaseModel):
    """Statistics collected during a pipeline run."""

    total_fetched: int = 0
    after_validation: int = 0
    after_normalization: int = 0
    after_dedup: int = 0
    after_quality: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    by_desc: dict[str, int] = Field(default_factory=dict)
    by_criticality: dict[int, int] = Field(default_factory=dict)
    validation_rejected: int = 0
    quality_rejected: int = 0
    duplicates_removed: int = 0
    fetch_duration_seconds: float = 0.0
    pipeline_duration_seconds: float = 0.0
    errors: list[str] = Field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=== Pipeline Statistics ===",
            f"  Fetched:          {self.total_fetched}",
            f"  After validation: {self.after_validation} ({self.validation_rejected} rejected)",
            f"  After normaliz.:  {self.after_normalization}",
            f"  After dedup:      {self.after_dedup} ({self.duplicates_removed} removed)",
            f"  After quality:    {self.after_quality} ({self.quality_rejected} rejected)",
            f"  By type:          {self.by_type}",
            f"  By source:        {self.by_source}",
            f"  Fetch time:       {self.fetch_duration_seconds:.1f}s",
            f"  Total time:       {self.pipeline_duration_seconds:.1f}s",
        ]
        if self.errors:
            lines.append(f"  Errors:           {len(self.errors)}")
            for err in self.errors[:5]:
                lines.append(f"    - {err}")
        return "\n".join(lines)
