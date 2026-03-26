"""Shared fixtures for MCP protocol tests.

These tests verify the MCP protocol layer (tool discovery, routing, schema
validation, response format, error handling) WITHOUT making real HTTP calls
to the Foxit API.  Every FoxitPDFClient method is mocked.
"""

import inspect
import json
import pytest
from unittest.mock import AsyncMock, patch

from fastmcp import Client
from foxit_pdf_api_mcp_server.server import mcp
from foxit_pdf_api_mcp_server import resources
from foxit_pdf_api_mcp_server.client.foxit_client import FoxitPDFClient


# ---------------------------------------------------------------------------
# Mock return values matching the TypedDict contracts in types/api.py
# ---------------------------------------------------------------------------
MOCK_DOCUMENT_ID = "mock-doc-id-123"
MOCK_TASK_ID = "mock-task-id-456"

MOCK_UPLOAD_RESPONSE = {"documentId": MOCK_DOCUMENT_ID}
MOCK_OPERATION_RESPONSE = {"taskId": MOCK_TASK_ID}
MOCK_SHARE_LINK_RESPONSE = {
    "shareUrl": "https://example.com/share/abc",
    "token": "mock-token",
    "expiresAt": "2026-12-31T23:59:59Z",
}
MOCK_PROPERTIES_RESPONSE = {
    "docInfo": {"pageCount": 3, "title": "Mock PDF", "author": "Test"},
}
MOCK_TASK_STATUS_RESPONSE = {
    "taskId": MOCK_TASK_ID,
    "status": "COMPLETED",
    "progress": 100,
    "resultDocumentId": "mock-result-doc-id",
}

# Methods that need specific mock return values (not the default taskId response).
_SPECIAL_MOCKS: dict[str, object] = {
    "upload_document": MOCK_UPLOAD_RESPONSE,
    "create_share_link": MOCK_SHARE_LINK_RESPONSE,
    "delete_document": None,
    "get_pdf_properties": MOCK_PROPERTIES_RESPONSE,
    "get_task_status": MOCK_TASK_STATUS_RESPONSE,
    "download_document": b"mock pdf bytes",
    "download_document_partial": b"mock partial bytes",
    "close": None,
}


@pytest.fixture(autouse=True)
def mock_foxit_client():
    """Patch every public async method on the shared FoxitPDFClient instance.

    Methods listed in ``_SPECIAL_MOCKS`` get their specific return values.
    All other public async methods (task-based operations) automatically
    return ``MOCK_OPERATION_RESPONSE`` (``{"taskId": "..."}``).

    This auto-discovers methods via introspection so you never need to
    update a hardcoded list when adding a new tool / client method.
    """
    client = resources.client
    patchers = []

    for name, method in inspect.getmembers(FoxitPDFClient, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        if not inspect.iscoroutinefunction(method):
            continue

        return_value = _SPECIAL_MOCKS.get(name, MOCK_OPERATION_RESPONSE)
        p = patch.object(client, name, new_callable=AsyncMock, return_value=return_value)
        patchers.append(p)

    # Start all patches
    for p in patchers:
        p.start()

    yield

    # Stop all patches
    for p in patchers:
        p.stop()


@pytest.fixture
async def mcp_client():
    """Create and connect a FastMCP Client via in-memory transport."""
    async with Client(mcp) as c:
        yield c
