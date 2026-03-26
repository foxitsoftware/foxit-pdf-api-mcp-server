"""E2E test fixtures — NO mocking. Uses the real Foxit Cloud API."""

import base64
from pathlib import Path

import httpx
import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture(scope="module")
async def refresh_http_client():
    """Recreate the httpx.AsyncClient so it binds to the current event loop."""
    from foxit_pdf_api_mcp_server.resources import client

    try:
        await client._client.aclose()
    except Exception:
        pass
    client._client = httpx.AsyncClient(
        timeout=httpx.Timeout(client.default_timeout), follow_redirects=True
    )
    yield client
