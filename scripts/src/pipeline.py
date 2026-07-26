"""Pipeline orchestrator for IOC ingestion, validation, dedup, and quality scoring."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from .client import AsyncAPIClient
from .models import (
    AddressRecord,
    NormalizedIOC,
    PipelineStats,
    ScoredIOC,
    ValidatedIOC,
)
from .normalizer import normalize_ioc
from .quality import score_ioc
from .validator import validate_ioc

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline orchestrator.

    Stages:
    1. Fetch   — paginated retrieval of all IOCs from SGB API
    2. Validate — syntax + semantic checks, reject invalid entries
    3. Normalize — lowercase, trim, IDN, remove duplicates
    4. Dedup   — exact + fuzzy deduplication
    5. Quality — confidence scoring and false-positive risk estimation
    """

    def __init__(
        self,
        client: AsyncAPIClient | None = None,
        min_quality_score: float = 0.0,
        max_criticality: int = 10,
        per_page: int = 9999,
        max_pages: int = 0,
        skip_validation: bool = False,
        skip_dedup: bool = False,
    ):
        self.client = client or AsyncAPIClient()
        self.min_quality_score = min_quality_score
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

        # Stage 4: Dedup
        deduped, dup_count = self._stage_dedup(normalized)
        self.stats.duplicates_removed = dup_count
        self.stats.after_dedup = len(deduped)

        # Stage 5: Quality score
        scored, quality_rejected = self._stage_quality(deduped)
        self.stats.quality_rejected = quality_rejected
        self.stats.after_quality = len(scored)

        # Compute stats
        self._compute_stats(scored)
        self.stats.pipeline_duration_seconds = time.monotonic() - start_time

        logger.info(self.stats.summary())
        return scored, self.stats

    async def __aenter__(self) -> Pipeline:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.client.close()

    async def _stage_fetch(self) -> tuple[list[AddressRecord], float]:
        """Stage 1: Fetch all IOCs from the API."""
        logger.info("Stage 1/5: Fetching IOCs...")
        start = time.monotonic()
        records = await self.client.fetch_addresses(
            per_page=self.per_page,
            max_pages=self.max_pages,
        )
        self.stats.total_fetched = len(records)
        duration = time.monotonic() - start
        logger.info(f"Fetched {len(records)} IOCs in {duration:.1f}s")
        return records, duration

    def _stage_validate(self, records: list[AddressRecord]) -> tuple[list[ValidatedIOC], int]:
        """Stage 2: Validate each IOC."""
        logger.info("Stage 2/5: Validating IOCs...")
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
        """Stage 3: Normalize each validated IOC."""
        logger.info("Stage 3/5: Normalizing IOCs...")
        normalized: list[NormalizedIOC] = []

        for v in validated:
            try:
                n = normalize_ioc(v)
                if n is not None:
                    normalized.append(n)
            except Exception as e:
                logger.debug(f"Normalization error: {e}")

        logger.info(f"Normalized {len(normalized)} IOCs")
        return normalized

    def _stage_dedup(
        self, normalized: list[NormalizedIOC]
    ) -> tuple[list[NormalizedIOC], int]:
        """Stage 4: Remove duplicates.

        Note: deduplicate() expects ScoredIOC, but we're passing NormalizedIOC.
        For now, we do simple exact-match dedup on NormalizedIOC before scoring.
        """
        logger.info("Stage 4/5: Deduplicating...")
        seen: set[str] = set()
        unique: list[NormalizedIOC] = []
        for n in normalized:
            key = f"{n.ioc_type.value}|{n.value}"
            if key not in seen:
                seen.add(key)
                unique.append(n)
        removed = len(normalized) - len(unique)
        logger.info(f"Dedup: {len(unique)} unique (removed {removed} duplicates)")
        return unique, removed

    def _stage_quality(
        self, deduped: list[NormalizedIOC]
    ) -> tuple[list[ScoredIOC], int]:
        """Stage 5: Score quality and filter."""
        logger.info("Stage 5/5: Quality scoring...")
        scored: list[ScoredIOC] = []
        rejected = 0

        for n in deduped:
            try:
                s = score_ioc(n)
                if s.quality_score >= self.min_quality_score:
                    scored.append(s)
                else:
                    rejected += 1
            except Exception as e:
                logger.debug(f"Quality scoring error: {e}")
                rejected += 1

        logger.info(f"Scored {len(scored)}, rejected {rejected}")
        return scored, rejected

    def _compute_stats(self, scored: list[ScoredIOC]) -> None:
        """Compute aggregate statistics from scored IOCs."""
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
