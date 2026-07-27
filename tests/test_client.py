"""Tests for the async API client: mock HTTP responses, pagination, retry, errors."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from scripts.src.client import APIError, AsyncAPIClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_json_response(
    status_code: int = 200,
    json_data: Any = None,
) -> httpx.Response:
    content = b""
    if json_data is not None:
        import json as _json

        content = _json.dumps(json_data).encode()
    return httpx.Response(
        status_code=status_code,
        content=content,
        request=httpx.Request("GET", "http://test.com"),
    )


# ---------------------------------------------------------------------------
# Construction and configuration
# ---------------------------------------------------------------------------


def test_client_default_config():
    client = AsyncAPIClient()
    assert client.base_url == "https://siberguvenlik.gov.tr"
    assert client.max_retries == 3
    assert client.rate_limit == 10.0
    assert client.timeout == 60.0


def test_client_custom_config():
    client = AsyncAPIClient(
        base_url="http://example.com/",
        max_retries=10,
        rate_limit=5.0,
        timeout=30.0,
    )
    assert client.base_url == "http://example.com"
    assert client.max_retries == 10
    assert client.rate_limit == 5.0
    assert client.timeout == 30.0


def test_client_strips_trailing_slash():
    client = AsyncAPIClient(base_url="http://example.com/")
    assert client.base_url == "http://example.com"


# ---------------------------------------------------------------------------
# Successful requests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_success():
    resp_data = {
        "totalCount": 1,
        "count": 1,
        "models": [{"id": 1, "url": "a.com"}],
        "page": 0,
        "pageCount": 1,
    }
    mock_response = _make_json_response(200, resp_data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await client._request("/api/address/index", params={"page": 0, "per-page": 1})
        assert result["totalCount"] == 1
        assert len(result["models"]) == 1


# ---------------------------------------------------------------------------
# Retry on server errors
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_on_server_error():
    error_resp = _make_json_response(500, {"error": "server error"})
    ok_resp = _make_json_response(
        200,
        {
            "totalCount": 0,
            "count": 0,
            "models": [],
            "page": 0,
            "pageCount": 0,
        },
    )

    call_count = 0

    async def mock_get(*args: Any, **kwargs: Any) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return error_resp
        return ok_resp

    client = AsyncAPIClient(max_retries=3)
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await client._request("/test")
        assert result["totalCount"] == 0
        assert call_count == 2


@pytest.mark.asyncio
async def test_retry_exhausted():
    async def always_fail(*args: Any, **kwargs: Any) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    client = AsyncAPIClient(max_retries=2)
    with (
        patch("httpx.AsyncClient.get", side_effect=always_fail),
        pytest.raises(APIError, match="Failed after"),
    ):
        await client._request("/test")


# ---------------------------------------------------------------------------
# Rate limiting (429)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_limit_retries():
    rate_resp = _make_json_response(429, {})
    ok_resp = _make_json_response(200, {"totalCount": 0, "models": [], "page": 0, "pageCount": 0})

    call_count = 0

    async def mock_get(*args: Any, **kwargs: Any) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return rate_resp
        return ok_resp

    client = AsyncAPIClient(max_retries=3)
    with (
        patch("httpx.AsyncClient.get", side_effect=mock_get),
        patch("scripts.src.client.asyncio.sleep", new_callable=AsyncMock),
    ):
        result = await client._request("/test")
        assert result["totalCount"] == 0


# ---------------------------------------------------------------------------
# Client error (non-retryable, e.g. 400)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_client_error_400_raises_immediately():
    resp = _make_json_response(400, {"error": "bad request"})
    client = AsyncAPIClient(max_retries=3)
    with (
        patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=resp),
        pytest.raises(APIError, match="API error 400"),
    ):
        await client._request("/test")


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_addresses_pagination():
    page0 = {
        "totalCount": 3,
        "count": 2,
        "page": 0,
        "pageCount": 2,
        "models": [
            {
                "id": 1,
                "url": "evil.com",
                "type": "domain",
                "desc": "PH",
                "source": "US",
                "date": "2024-01-01",
                "criticality_level": 3,
                "connectiontype": "PH",
            },
            {
                "id": 2,
                "url": "bad.net",
                "type": "domain",
                "desc": "MC",
                "source": "SO",
                "date": "2024-01-02",
                "criticality_level": 1,
                "connectiontype": "BC",
            },
        ],
    }
    page1 = {
        "totalCount": 3,
        "count": 1,
        "page": 1,
        "pageCount": 2,
        "models": [
            {
                "id": 3,
                "url": "85.214.132.117",
                "type": "ip",
                "desc": "CA",
                "source": "RS",
                "date": "2024-01-03",
                "criticality_level": 2,
                "connectiontype": "AC",
            },
        ],
    }

    call_count = 0

    async def mock_get(*args: Any, **kwargs: Any) -> httpx.Response:
        nonlocal call_count
        params = kwargs.get("params", {})
        page = params.get("page", 0)
        if page == 0:
            return _make_json_response(200, page0)
        return _make_json_response(200, page1)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_addresses(per_page=2, max_pages=2)
        assert len(records) == 3
        assert records[0].id == 1


@pytest.mark.asyncio
async def test_fetch_addresses_empty():
    empty = {"totalCount": 0, "count": 0, "models": [], "page": 0, "pageCount": 0}

    async def mock_get(*args: Any, **kwargs: Any) -> httpx.Response:
        return _make_json_response(200, empty)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_addresses()
        assert records == []


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check_success():
    resp_data = {"totalCount": 483690, "models": [{"id": 1}], "page": 0, "pageCount": 1}
    mock_response = _make_json_response(200, resp_data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        result = await client.health_check()
        assert result is True


@pytest.mark.asyncio
async def test_health_check_failure():
    async def mock_get(*args: Any, **kwargs: Any) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await client.health_check()
        assert result is False


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def test_stats():
    client = AsyncAPIClient()
    s = client.stats
    assert s["base_url"] == "https://siberguvenlik.gov.tr"
    assert s["total_requests"] == 0
    assert s["max_retries"] == 3
