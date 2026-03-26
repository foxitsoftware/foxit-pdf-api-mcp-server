"""MCP Protocol Tests – Protocol Routing & Response Format.

Verify that ``call_tool()`` correctly routes to the matching tool function
and wraps the return value in a proper ``CallToolResult``.
All Foxit HTTP calls are mocked (see conftest.py).
"""

import json
import base64

import pytest
from mcp.types import TextContent

from .conftest import MOCK_DOCUMENT_ID, MOCK_TASK_ID

pytestmark = pytest.mark.asyncio


def _parse_text(result) -> dict:
    """Extract and parse the JSON text from a CallToolResult."""
    assert len(result.content) >= 1
    first = result.content[0]
    assert isinstance(first, TextContent)
    assert first.type == "text"
    return json.loads(first.text)


class TestUploadDocumentRouting:
    """call_tool('upload_document', ...) routes correctly."""

    async def test_successful_upload(self, mcp_client):
        b64 = base64.b64encode(b"%PDF-1.4 test content").decode()
        result = await mcp_client.call_tool(
            "upload_document", {"file_content": b64, "file_name": "test.pdf"}
        )
        assert result.is_error is False
        data = _parse_text(result)
        assert data["success"] is True
        assert data["resultDocumentId"] == MOCK_DOCUMENT_ID


class TestCreateShareLinkRouting:
    """call_tool('create_share_link', ...)."""

    async def test_successful_share_link(self, mcp_client):
        result = await mcp_client.call_tool(
            "create_share_link", {"document_id": "doc-1"}
        )
        assert result.is_error is False
        data = _parse_text(result)
        assert data["success"] is True
        assert data["shareUrl"].startswith("https://")


class TestDeleteDocumentRouting:
    """call_tool('delete_document', ...)."""

    async def test_successful_delete(self, mcp_client):
        result = await mcp_client.call_tool(
            "delete_document", {"document_id": "doc-1"}
        )
        assert result.is_error is False
        data = _parse_text(result)
        assert data["success"] is True
        assert "delete" in data["message"].lower()


class TestTaskBasedToolRouting:
    """Task-based tools (pdf_to_*, pdf_from_*, pdf_merge, etc.) return taskId."""

    @pytest.mark.parametrize(
        "tool_name,args",
        [
            ("pdf_to_word", {"document_id": "doc-1"}),
            ("pdf_to_excel", {"document_id": "doc-1"}),
            ("pdf_to_ppt", {"document_id": "doc-1"}),
            ("pdf_to_text", {"document_id": "doc-1"}),
            ("pdf_to_html", {"document_id": "doc-1"}),
            ("pdf_to_image", {"document_id": "doc-1"}),
            ("pdf_from_word", {"document_id": "doc-1"}),
            ("pdf_from_excel", {"document_id": "doc-1"}),
            ("pdf_from_ppt", {"document_id": "doc-1"}),
            ("pdf_from_text", {"document_id": "doc-1"}),
            ("pdf_from_image", {"document_id": "doc-1"}),
            ("pdf_from_html", {"document_id": "doc-1"}),
            ("pdf_merge", {"document_ids": ["doc-1", "doc-2"]}),
            ("pdf_split", {"document_id": "doc-1", "page_count": 1}),
            ("pdf_extract_pages", {"document_id": "doc-1", "page_range": "1"}),
            ("pdf_compress", {"document_id": "doc-1"}),
            ("pdf_flatten", {"document_id": "doc-1"}),
            ("pdf_linearize", {"document_id": "doc-1"}),
            ("pdf_delete_pages", {"document_id": "doc-1", "page_range": "1"}),
            ("pdf_rotate_pages", {"document_id": "doc-1", "page_range": "1", "rotation": 90}),
            ("pdf_reorder_pages", {"document_id": "doc-1", "page_range": "1", "target_position": 2}),
            ("pdf_compare", {"document_id1": "doc-1", "document_id2": "doc-2"}),
        ],
    )
    async def test_task_tool_returns_task_id(self, mcp_client, tool_name, args):
        result = await mcp_client.call_tool(tool_name, args)
        assert result.is_error is False
        data = _parse_text(result)
        assert data["success"] is True
        assert data["taskId"] == MOCK_TASK_ID
        assert "message" in data

    async def test_pdf_from_url(self, mcp_client):
        """pdf_from_url takes url instead of document_id."""
        result = await mcp_client.call_tool(
            "pdf_from_url", {"url": "https://example.com/page"}
        )
        assert result.is_error is False
        data = _parse_text(result)
        assert data["success"] is True
        assert data["taskId"] == MOCK_TASK_ID


class TestGetPdfPropertiesRouting:
    """get_pdf_properties returns properties directly (not a task)."""

    async def test_returns_properties(self, mcp_client):
        result = await mcp_client.call_tool(
            "get_pdf_properties", {"document_id": "doc-1"}
        )
        assert result.is_error is False
        data = _parse_text(result)
        assert data["success"] is True
        assert "properties" in data


class TestResponseFormat:
    """Verify MCP CallToolResult structure for all tool categories."""

    async def test_result_has_content_array(self, mcp_client):
        """CallToolResult.content is a non-empty list of TextContent."""
        result = await mcp_client.call_tool(
            "delete_document", {"document_id": "doc-1"}
        )
        assert isinstance(result.content, list)
        assert len(result.content) >= 1
        assert isinstance(result.content[0], TextContent)

    async def test_content_text_is_valid_json(self, mcp_client):
        """The text payload inside TextContent is parseable JSON."""
        b64 = base64.b64encode(b"%PDF-1.4 test").decode()
        result = await mcp_client.call_tool(
            "upload_document", {"file_content": b64, "file_name": "t.pdf"}
        )
        text = result.content[0].text
        data = json.loads(text)  # should not raise
        assert isinstance(data, dict)

    async def test_is_error_false_on_success(self, mcp_client):
        """Successful tool calls have is_error=False."""
        result = await mcp_client.call_tool(
            "create_share_link", {"document_id": "doc-1"}
        )
        assert result.is_error is False

    async def test_task_response_has_required_keys(self, mcp_client):
        """Task-based responses always include success, taskId, message."""
        result = await mcp_client.call_tool(
            "pdf_to_word", {"document_id": "doc-1"}
        )
        data = _parse_text(result)
        assert "success" in data
        assert "taskId" in data
        assert "message" in data
        # Must NOT contain 'status' (that's only in completed results)
        assert "status" not in data
