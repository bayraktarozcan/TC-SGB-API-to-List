"""TC-SGB threat intelligence pipeline — fetch, validate, normalize, score, dedup, export."""

from .client import AsyncAPIClient
from .deduplicator import deduplicate
from .models import (
    AddressRecord,
    ConnectionType,
    DescriptionCategory,
    IOCType,
    NormalizedIOC,
    PipelineStats,
    ScoredIOC,
    Source,
    ValidatedIOC,
)
from .normalizer import normalize_ioc
from .outputs import FORMAT_REGISTRY, generate_all
from .pipeline import Pipeline, run_pipeline_sync
from .quality import DEFAULT_QUALITY_THRESHOLD, filter_false_positives, score_ioc
from .validator import validate_ioc, validate_records_batch

__all__ = [
    "DEFAULT_QUALITY_THRESHOLD",
    "FORMAT_REGISTRY",
    "AddressRecord",
    "AsyncAPIClient",
    "ConnectionType",
    "DescriptionCategory",
    "IOCType",
    "NormalizedIOC",
    "Pipeline",
    "PipelineStats",
    "ScoredIOC",
    "Source",
    "ValidatedIOC",
    "deduplicate",
    "filter_false_positives",
    "generate_all",
    "normalize_ioc",
    "run_pipeline_sync",
    "score_ioc",
    "validate_ioc",
    "validate_records_batch",
]
