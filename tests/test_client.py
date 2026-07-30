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
    assert client.rate_limit == 5.0
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
                "url": "192.0.2.1",
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


# ---------------------------------------------------------------------------
# Close / context manager
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close():
    client = AsyncAPIClient()
    await client._get_client()
    assert client._client is not None
    await client.close()
    assert client._client is None


@pytest.mark.asyncio
async def test_close_when_already_closed():
    client = AsyncAPIClient()
    await client.close()
    assert client._client is None


@pytest.mark.asyncio
async def test_aenter_aexit():
    async with AsyncAPIClient() as client:
        assert client._client is not None
    assert client._client is None or client._client.is_closed


# ---------------------------------------------------------------------------
# Rate limit disabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_limit_disabled():
    ok_resp = _make_json_response(200, {"totalCount": 0, "models": [], "page": 0, "pageCount": 0})
    client = AsyncAPIClient(rate_limit=0)
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=ok_resp):
        result = await client._request("/test")
        assert result["totalCount"] == 0


# ---------------------------------------------------------------------------
# NetworkError retry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_network_error_retries_then_raises():
    async def raise_network(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    client = AsyncAPIClient(max_retries=2)
    with (
        patch("httpx.AsyncClient.get", side_effect=raise_network),
        patch("scripts.src.client.asyncio.sleep", new_callable=AsyncMock),
        pytest.raises(APIError, match="API error 0"),
    ):
        await client._request("/test")


@pytest.mark.asyncio
async def test_network_error_retries_once_then_succeeds():
    call_count = 0

    async def network_then_ok(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ConnectError("connection refused")
        return _make_json_response(200, {"totalCount": 0, "models": [], "page": 0, "pageCount": 0})

    client = AsyncAPIClient(max_retries=3)
    with (
        patch("httpx.AsyncClient.get", side_effect=network_then_ok),
        patch("scripts.src.client.asyncio.sleep", new_callable=AsyncMock),
    ):
        result = await client._request("/test")
        assert result["totalCount"] == 0
        assert call_count == 2


# ---------------------------------------------------------------------------
# Invalid JSON (ValueError) retry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_json_retries_then_raises():
    bad_resp = httpx.Response(
        status_code=200,
        content=b"not json",
        request=httpx.Request("GET", "http://test.com"),
    )

    async def mock_get(*args, **kwargs):
        return bad_resp

    client = AsyncAPIClient(max_retries=2)
    with (
        patch("httpx.AsyncClient.get", side_effect=mock_get),
        patch("scripts.src.client.asyncio.sleep", new_callable=AsyncMock),
        pytest.raises(APIError, match="Invalid JSON"),
    ):
        await client._request("/test")


@pytest.mark.asyncio
async def test_invalid_json_retries_once_then_succeeds():
    call_count = 0

    async def bad_then_ok(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(
                status_code=200,
                content=b"not json",
                request=httpx.Request("GET", "http://test.com"),
            )
        return _make_json_response(200, {"totalCount": 0, "models": [], "page": 0, "pageCount": 0})

    client = AsyncAPIClient(max_retries=3)
    with (
        patch("httpx.AsyncClient.get", side_effect=bad_then_ok),
        patch("scripts.src.client.asyncio.sleep", new_callable=AsyncMock),
    ):
        result = await client._request("/test")
        assert result["totalCount"] == 0


# ---------------------------------------------------------------------------
# Pagination: max_pages, failed record parse, empty models
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_max_pages_limit():
    page_data = {
        "totalCount": 100,
        "count": 2,
        "page": 0,
        "pageCount": 10,
        "models": [
            {
                "id": 1,
                "url": "a.com",
                "type": "domain",
                "desc": "PH",
                "source": "US",
                "date": "2024-01-01",
                "criticality_level": 3,
                "connectiontype": "PH",
            },
            {
                "id": 2,
                "url": "b.com",
                "type": "domain",
                "desc": "MC",
                "source": "SO",
                "date": "2024-01-02",
                "criticality_level": 1,
                "connectiontype": "BC",
            },
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, page_data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_addresses(per_page=2, max_pages=1)
        assert len(records) == 2


@pytest.mark.asyncio
async def test_fetch_empty_page_breaks():
    empty_page = {"totalCount": 0, "count": 0, "page": 0, "pageCount": 5, "models": []}

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, empty_page)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_addresses(per_page=100)
        assert records == []


@pytest.mark.asyncio
async def test_fetch_bad_record_skipped():
    data = {
        "totalCount": 2,
        "count": 2,
        "page": 0,
        "pageCount": 1,
        "models": [
            {"id": 999, "url": None, "type": None},
            {
                "id": 1,
                "url": "good.com",
                "type": "domain",
                "desc": "PH",
                "source": "US",
                "date": "2024-01-01",
                "criticality_level": 3,
                "connectiontype": "PH",
            },
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_addresses()
        assert len(records) == 1


# ---------------------------------------------------------------------------
# Fetch metadata endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_descriptions():
    data = {
        "models": [
            {
                "id": "1",
                "tr_title": "PH",
                "en_title": "Phishing",
                "tr_desc": "Açıklama",
                "en_desc": "Description",
            },
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_descriptions()
        assert len(records) == 1


@pytest.mark.asyncio
async def test_fetch_connection_types():
    data = {
        "models": [
            {"id": "1", "tr_title": "PH", "en_title": "Phishing"},
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_connection_types()
        assert len(records) == 1


@pytest.mark.asyncio
async def test_fetch_sources():
    data = {
        "models": [
            {"id": "1", "tr_title": "USOM", "en_title": "USOM"},
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_sources()
        assert len(records) == 1


@pytest.mark.asyncio
async def test_fetch_incidents():
    data = {
        "models": [
            {"id": 1, "title": "Test incident", "date": "2024-01-01"},
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_incidents()
        assert len(records) == 1


@pytest.mark.asyncio
async def test_fetch_announcements():
    data = {
        "models": [
            {"id": 1, "title": "Test announcement", "date": "2024-01-01"},
        ],
    }

    async def mock_get(*args, **kwargs):
        return _make_json_response(200, data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        records = await client.fetch_announcements()
        assert len(records) == 1


@pytest.mark.asyncio
async def test_fetch_metadata():
    desc_data = {"models": [{"id": "1", "tr_title": "PH", "en_title": "Phishing"}]}
    ct_data = {"models": [{"id": "1", "tr_title": "PH", "en_title": "Phishing"}]}
    src_data = {"models": [{"id": "1", "tr_title": "USOM", "en_title": "USOM"}]}

    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _make_json_response(200, desc_data)
        if call_count == 2:
            return _make_json_response(200, ct_data)
        return _make_json_response(200, src_data)

    client = AsyncAPIClient()
    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await client.fetch_metadata()
        assert "descriptions" in result
        assert "connection_types" in result
        assert "sources" in result
