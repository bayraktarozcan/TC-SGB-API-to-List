"""T.C. Siber Güvenlik Başkanlığı API client with pagination, retries, and rate limiting."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from .models import (
    AddressRecord,
    AnnouncementRecord,
    ConnectionTypeRecord,
    DescriptionRecord,
    IncidentRecord,
    SourceRecord,
)

logger = logging.getLogger(__name__)

# Real API base URL (verified from OpenAPI spec and live calls)
BASE_URL = "https://siberguvenlik.gov.tr"


class APIError(Exception):
    """Raised when the SGB API returns a non-2xx response."""

    def __init__(self, status_code: int, detail: str, url: str):
        self.status_code = status_code
        self.detail = detail
        self.url = url
        super().__init__(f"API error {status_code} at {url}: {detail}")


class AsyncAPIClient:
    """Async HTTP client for the T.C. Siber Güvenlik Başkanlığı API.

    No authentication required. Conservative rate limiting (10 req/s).
    Exponential backoff on transient errors.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        max_retries: int = 3,
        rate_limit: float = 10.0,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.rate_limit = rate_limit
        self.timeout = timeout
        self._last_request_time: float = 0.0
        self._request_count: int = 0
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create a persistent httpx.AsyncClient."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncAPIClient:
        await self._get_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def _rate_limit_wait(self) -> None:
        """Enforce rate limiting between requests."""
        if self.rate_limit <= 0:
            return
        min_interval = 1.0 / self.rate_limit
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        self._last_request_time = time.monotonic()

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a single HTTP GET request with retries and exponential backoff."""
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        last_response: httpx.Response | None = None

        for attempt in range(self.max_retries):
            await self._rate_limit_wait()
            try:
                client = await self._get_client()
                response = await client.get(url, params=params)
                self._request_count += 1

                if response.status_code == 200:
                    return response.json()  # type: ignore[no-any-return]
                if response.status_code == 429:
                    last_response = response
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"Rate limited (429). Waiting {wait}s before retry...")
                    await asyncio.sleep(wait)
                    continue
                if response.status_code >= 500:
                    last_response = response
                    wait = 2**attempt
                    logger.warning(
                        "Server error %s. Waiting %ss (attempt %d/%d)",
                        response.status_code,
                        wait,
                        attempt + 1,
                        self.max_retries,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise APIError(
                    status_code=response.status_code,
                    detail=response.text[:500],
                    url=url,
                )
            except httpx.TimeoutException:
                wait = 2**attempt
                logger.warning(
                    "Timeout on %s. Waiting %ss (attempt %d/%d)",
                    endpoint,
                    wait,
                    attempt + 1,
                    self.max_retries,
                )
                await asyncio.sleep(wait)
            except httpx.NetworkError as e:
                logger.error(f"Network error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                else:
                    raise
            except ValueError as e:
                logger.error(f"Invalid JSON response from {endpoint}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                else:
                    raise APIError(
                        status_code=0,
                        detail=f"Invalid JSON response: {e}",
                        url=url,
                    )

        # All retries exhausted on 429/5xx — preserve the last HTTP status.
        status = last_response.status_code if last_response else 0
        detail = (
            last_response.text[:500]
            if last_response
            else f"Failed after {self.max_retries} attempts"
        )
        raise APIError(status_code=status, detail=detail, url=url)

    async def _fetch_paginated(
        self,
        endpoint: str,
        model_class: Any,
        per_page: int = 9999,
        max_pages: int = 0,
    ) -> list[Any]:
        """Fetch all pages from a paginated endpoint.

        Args:
            endpoint: API endpoint path (e.g., "/api/address/index")
            model_class: Pydantic model class for each record
            per_page: Records per page (max 9999)
            max_pages: Maximum pages to fetch (0 = all)

        Returns:
            List of all records across all pages
        """
        all_records = []
        page = 0

        while True:
            params = {
                "page": page,
                "per-page": per_page,
            }

            data = await self._request(endpoint, params)

            # Parse the paginated response
            # Real API returns: {totalCount, count, models, page, pageCount}
            models_list = data.get("models", [])
            total_count = data.get("totalCount", 0)
            page_count = data.get("pageCount", 1)

            # Convert to Pydantic models
            for item in models_list:
                try:
                    record = model_class.model_validate(item)
                    all_records.append(record)
                except Exception as e:
                    logger.warning(f"Failed to parse record: {e}")
                    continue

            logger.info(
                f"Page {page}: fetched {len(models_list)} records "
                f"(total so far: {len(all_records)}/{total_count})"
            )

            # Check if we've fetched all pages
            page += 1
            if page >= page_count:
                break

            if max_pages > 0 and page >= max_pages:
                logger.info(f"Reached max_pages limit ({max_pages})")
                break

            # If count is 0, we're done
            if len(models_list) == 0:
                break

        return all_records

    async def fetch_addresses(
        self,
        per_page: int = 9999,
        max_pages: int = 0,
    ) -> list[AddressRecord]:
        """Fetch all IOC addresses (domains, IPs, URLs)."""
        logger.info("Fetching all addresses from SGB API...")
        records = await self._fetch_paginated(
            endpoint="/api/address/index",
            model_class=AddressRecord,
            per_page=per_page,
            max_pages=max_pages,
        )
        logger.info(f"Fetched {len(records)} address records total")
        return records

    async def fetch_descriptions(self) -> list[DescriptionRecord]:
        """Fetch address description categories."""
        data = await self._request("/api/address-description/index")
        models_list = data.get("models", [])
        records = [DescriptionRecord.model_validate(item) for item in models_list]
        logger.info(f"Fetched {len(records)} description records")
        return records

    async def fetch_connection_types(self) -> list[ConnectionTypeRecord]:
        """Fetch address connection types."""
        data = await self._request("/api/address-connection-type/index")
        models_list = data.get("models", [])
        records = [ConnectionTypeRecord.model_validate(item) for item in models_list]
        logger.info(f"Fetched {len(records)} connection type records")
        return records

    async def fetch_sources(self) -> list[SourceRecord]:
        """Fetch address sources."""
        data = await self._request("/api/address-source/index")
        models_list = data.get("models", [])
        records = [SourceRecord.model_validate(item) for item in models_list]
        logger.info(f"Fetched {len(records)} source records")
        return records

    async def fetch_incidents(self) -> list[IncidentRecord]:
        """Fetch recent incidents/advisories."""
        data = await self._request("/api/incident/index")
        models_list = data.get("models", [])
        records = [IncidentRecord.model_validate(item) for item in models_list]
        logger.info(f"Fetched {len(records)} incident records")
        return records

    async def fetch_announcements(self) -> list[AnnouncementRecord]:
        """Fetch recent announcements."""
        data = await self._request("/api/announcement/index")
        models_list = data.get("models", [])
        records = [AnnouncementRecord.model_validate(item) for item in models_list]
        logger.info(f"Fetched {len(records)} announcement records")
        return records

    async def fetch_metadata(self) -> dict[str, Any]:
        """Fetch all metadata (descriptions, connection types, sources)."""
        descriptions, connection_types, sources = await asyncio.gather(
            self.fetch_descriptions(),
            self.fetch_connection_types(),
            self.fetch_sources(),
        )
        return {
            "descriptions": {d.id: d for d in descriptions},
            "connection_types": {ct.id: ct for ct in connection_types},
            "sources": {s.id: s for s in sources},
        }

    async def health_check(self) -> bool:
        """Verify API is reachable."""
        try:
            data = await self._request(
                "/api/address/index",
                params={"page": 0, "per-page": 1},
            )
            return "totalCount" in data
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    @property
    def stats(self) -> dict[str, Any]:
        """Return client usage statistics."""
        return {
            "base_url": self.base_url,
            "total_requests": self._request_count,
            "max_retries": self.max_retries,
            "rate_limit": self.rate_limit,
        }
