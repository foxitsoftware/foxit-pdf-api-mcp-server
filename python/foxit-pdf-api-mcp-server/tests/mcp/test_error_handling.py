"""MCP Protocol Tests – Error Handling.

Verify MCP-level error behaviour: unknown tools, missing / extra parameters,
wrong argument types, and internal tool failures.
"""

import json

import pytest
from unittest.mock import AsyncMock, patch
from fastmcp.exceptions import ToolError

from foxit_pdf_api_mcp_server import resources

pytestmark = pytest.mark.asyncio


class TestUnknownTool:
    """Calling a tool that does not exist raises ToolError."""

    async def test_nonexistent_tool(self, mcp_client):
        with pytest.raises(ToolError, match="Unknown tool"):
            await mcp_client.call_tool("nonexistent_tool", {"arg": "val"})

    async def test_similar_name_typo(self, mcp_client):
        """A slight typo in the tool name is still rejected."""
        with pytest.raises(ToolError):
            await mcp_client.call_tool("pdf_to_words", {"document_id": "x"})


class TestMissingRequiredParams:
    """Omitting required parameters raises ToolError (Pydantic validation)."""

    async def test_pdf_to_word_no_document_id(self, mcp_client):
        with pytest.raises(ToolError, match="document_id"):
            await mcp_client.call_tool("pdf_to_word", {})

    async def test_delete_document_no_document_id(self, mcp_client):
        with pytest.raises(ToolError, match="document_id"):
            await mcp_client.call_tool("delete_document", {})

    async def test_pdf_split_missing_page_count(self, mcp_client):
        with pytest.raises(ToolError, match="page_count"):
            await mcp_client.call_tool("pdf_split", {"document_id": "doc-1"})

    async def test_pdf_merge_missing_document_ids(self, mcp_client):
        with pytest.raises(ToolError, match="document_ids"):
            await mcp_client.call_tool("pdf_merge", {})

    async def test_pdf_compare_missing_both_ids(self, mcp_client):
        with pytest.raises(ToolError, match="document_id1"):
            await mcp_client.call_tool("pdf_compare", {})

    async def test_get_task_result_missing_task_id(self, mcp_client):
        with pytest.raises(ToolError, match="task_id"):
            await mcp_client.call_tool("get_task_result", {})

    async def test_show_pdf_tools_missing_user_intent(self, mcp_client):
        with pytest.raises(ToolError, match="user_intent"):
            await mcp_client.call_tool("show_pdf_tools", {})


class TestUnexpectedParams:
    """Passing parameters not in the tool schema raises ToolError."""

    async def test_extra_param_on_delete(self, mcp_client):
        with pytest.raises(ToolError, match="Unexpected keyword argument"):
            await mcp_client.call_tool(
                "delete_document", {"document_id": "x", "bogus": 123}
            )

    async def test_extra_param_on_conversion(self, mcp_client):
        with pytest.raises(ToolError, match="Unexpected keyword argument"):
            await mcp_client.call_tool(
                "pdf_to_word", {"document_id": "x", "quality": "high"}
            )


class TestToolInternalErrors:
    """When a tool catches an exception it returns success=False JSON
    (not a protocol-level error) so callers get actionable messages."""

    async def test_upload_document_no_file_content(self, mcp_client):
        """upload_document with no file_content returns error JSON."""
        result = await mcp_client.call_tool(
            "upload_document", {"file_content": None, "file_name": "test.pdf"}
        )
        # Tool catches ValueError internally and returns error JSON
        assert result.is_error is False  # MCP protocol level is OK
        data = json.loads(result.content[0].text)
        assert data["success"] is False
        assert "error" in data

    async def test_client_api_error_propagated(self, mcp_client):
        """When FoxitPDFClient raises, the tool returns error JSON."""
        from foxit_pdf_api_mcp_server.client.foxit_client import FoxitAPIError

        with patch.object(
            resources.client,
            "pdf_to_word",
            new_callable=AsyncMock,
            side_effect=FoxitAPIError("Authentication failed", code="AUTH_ERROR", status_code=401),
        ):
            result = await mcp_client.call_tool(
                "pdf_to_word", {"document_id": "doc-1"}
            )
            assert result.is_error is False
            data = json.loads(result.content[0].text)
            assert data["success"] is False
            assert "Authentication failed" in data["error"]
            assert data["code"] == "AUTH_ERROR"
            assert data["statusCode"] == 401

    async def test_unexpected_exception_propagated(self, mcp_client):
        """A generic RuntimeError inside a tool is also caught gracefully."""
        with patch.object(
            resources.client,
            "delete_document",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Network timeout"),
        ):
            result = await mcp_client.call_tool(
                "delete_document", {"document_id": "doc-1"}
            )
            assert result.is_error is False
            data = json.loads(result.content[0].text)
            assert data["success"] is False
            assert "Network timeout" in data["error"]
