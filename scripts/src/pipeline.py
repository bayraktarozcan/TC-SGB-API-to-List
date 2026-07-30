"""Pipeline orchestrator for IoC ingestion, validation, dedup, and quality scoring."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from .client import AsyncAPIClient
from .deduplicator import deduplicate
from .models import (
    AddressRecord,
    IOCType,
    NormalizedIOC,
    PipelineStats,
    ScoredIOC,
    ValidatedIOC,
)
from .normalizer import normalize_ioc
from .quality import DEFAULT_QUALITY_THRESHOLD, score_ioc
from .validator import validate_ioc

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline orchestrator.

    Stages:
    1. Fetch   — paginated retrieval of all IoCs from SGB API
    2. Validate — syntax + semantic checks, reject invalid entries
    3. Normalize — lowercase, trim, IDN normalization
    4. Quality — confidence scoring and false-positive risk estimation
    5. Dedup   — cross-type deduplication (keeps highest-scored duplicate)
    """

    def __init__(
        self,
        client: AsyncAPIClient | None = None,
        min_quality_score: float | None = None,
        max_criticality: int | None = None,
        per_page: int = 9999,
        max_pages: int = 0,
        skip_validation: bool = False,
        skip_dedup: bool = False,
    ):
        self.client = client or AsyncAPIClient()
        self.min_quality_score = (
            min_quality_score if min_quality_score is not None else DEFAULT_QUALITY_THRESHOLD
        )
        self.max_criticality = max_criticality
        self.per_page = per_page
        self.max_pages = max_pages
        self.skip_validation = skip_validation
        self.skip_dedup = skip_dedup
        self.stats = PipelineStats()

    async def run(self) -> tuple[list[ScoredIOC], PipelineStats]:
        """Execute the full pipeline."""
        start_time = time.monotonic()
        self.stats = PipelineStats()

        # Stage 1: Fetch
        raw_records, fetch_duration = await self._stage_fetch()
        self.stats.fetch_duration_seconds = fetch_duration

        # Stage 2: Validate
        validated, rejected_count = self._stage_validate(raw_records)
        self.stats.validation_rejected = rejected_count
        self.stats.after_validation = len(validated)

        # Stage 3: Normalize
        normalized = self._stage_normalize(validated)
        self.stats.after_normalization = len(normalized)

        # Stage 4: Quality score
        scored, quality_rejected = self._stage_quality(normalized)
        self.stats.quality_rejected = quality_rejected
        self.stats.after_quality = len(scored)

        # Stage 5: Dedup (cross-type, uses quality_score)
        deduped, dup_count = self._stage_dedup(scored)
        self.stats.duplicates_removed = dup_count
        self.stats.after_dedup = len(deduped)

        # Compute stats
        self._compute_stats(deduped)
        self.stats.pipeline_duration_seconds = time.monotonic() - start_time

        logger.info(self.stats.summary())
        return deduped, self.stats

    async def __aenter__(self) -> Pipeline:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.client.close()

    async def _stage_fetch(self) -> tuple[list[AddressRecord], float]:
        """Stage 1: Fetch all IoCs from the API."""
        logger.info("Stage 1/5: Fetching IoCs...")
        start = time.monotonic()
        records = await self.client.fetch_addresses(
            per_page=self.per_page,
            max_pages=self.max_pages,
        )
        self.stats.total_fetched = len(records)
        duration = time.monotonic() - start
        logger.info(f"Fetched {len(records)} IoCs in {duration:.1f}s")
        return records, duration

    def _stage_validate(self, records: list[AddressRecord]) -> tuple[list[ValidatedIOC], int]:
        """Stage 2: Validate each IoC."""
        if self.skip_validation:
            logger.info("Stage 2/5: Validation skipped (--skip-validation)")
            validated = [
                ValidatedIOC(raw_url=r.url, ioc_type=IOCType.DOMAIN, original_id=r.id)
                for r in records
            ]
            return validated, 0

        logger.info("Stage 2/5: Validating IoCs...")
        validated: list[ValidatedIOC] = []
        rejected = 0

        for record in records:
            try:
                result = validate_ioc(record)
                if result is None or result.validation_errors:
                    rejected += 1
                else:
                    validated.append(result)
            except Exception as e:
                logger.debug(f"Validation error for record {record.id}: {e}")
                rejected += 1

        logger.info(f"Validated {len(validated)}, rejected {rejected}")
        return validated, rejected

    def _stage_normalize(self, validated: list[ValidatedIOC]) -> list[NormalizedIOC]:
        """Stage 3: Normalize each validated IoC."""
        logger.info("Stage 3/5: Normalizing IoCs...")
        normalized: list[NormalizedIOC] = []

        for v in validated:
            try:
                n = normalize_ioc(v)
                if n is not None:
                    normalized.append(n)
            except Exception as e:
                logger.debug(f"Normalization error: {e}")

        logger.info(f"Normalized {len(normalized)} IoCs")
        return normalized

    def _stage_dedup(self, scored: list[ScoredIOC]) -> tuple[list[ScoredIOC], int]:
        """Stage 5: Cross-type deduplication using deduplicator module.

        Uses quality_score to keep the highest-scored duplicate when the same
        IoC appears with different metadata or across types (domain vs URL).
        """
        if self.skip_dedup:
            logger.info("Stage 5/5: Deduplication skipped (--skip-dedup)")
            return scored, 0

        logger.info("Stage 5/5: Cross-type deduplicating...")
        result = deduplicate(scored)
        return result.kept, result.removed_count

    def _stage_quality(self, normalized: list[NormalizedIOC]) -> tuple[list[ScoredIOC], int]:
        """Stage 4: Score quality and filter."""
        logger.info("Stage 4/5: Quality scoring...")
        scored: list[ScoredIOC] = []
        rejected = 0

        for n in normalized:
            try:
                s = score_ioc(n)
                if s.quality_score < self.min_quality_score:
                    rejected += 1
                    continue
                if self.max_criticality is not None and s.criticality_level > self.max_criticality:
                    rejected += 1
                    continue
                scored.append(s)
            except Exception as e:
                logger.debug(f"Quality scoring error: {e}")
                rejected += 1

        logger.info(f"Scored {len(scored)}, rejected {rejected}")
        return scored, rejected

    def _compute_stats(self, scored: list[ScoredIOC]) -> None:
        """Compute aggregate statistics from scored IoCs."""
        for s in scored:
            # By type
            type_key = s.ioc_type.value if hasattr(s.ioc_type, "value") else str(s.ioc_type)
            self.stats.by_type[type_key] = self.stats.by_type.get(type_key, 0) + 1

            # By source
            if s.source:
                src_key = s.source.value if hasattr(s.source, "value") else str(s.source)
                self.stats.by_source[src_key] = self.stats.by_source.get(src_key, 0) + 1

            # By description
            if s.desc:
                desc_key = s.desc.value if hasattr(s.desc, "value") else str(s.desc)
                self.stats.by_desc[desc_key] = self.stats.by_desc.get(desc_key, 0) + 1

            # By criticality
            self.stats.by_criticality[s.criticality_level] = (
                self.stats.by_criticality.get(s.criticality_level, 0) + 1
            )


def run_pipeline_sync(
    client: AsyncAPIClient | None = None,
    **kwargs: Any,
) -> tuple[list[ScoredIOC], PipelineStats]:
    """Synchronous wrapper around the async Pipeline.run()."""

    async def _run() -> tuple[list[ScoredIOC], PipelineStats]:
        async with Pipeline(client=client, **kwargs) as pipeline:
            return await pipeline.run()

    return asyncio.run(_run())
