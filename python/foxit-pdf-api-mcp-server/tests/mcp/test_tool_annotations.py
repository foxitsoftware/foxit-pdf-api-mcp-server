"""MCP Protocol Tests – Tool Annotations.

Verify that every tool exposes the correct ``readOnlyHint`` and
``destructiveHint`` annotations through the MCP protocol.
"""

import pytest

pytestmark = pytest.mark.asyncio


# Annotation classification from the source code
WRITE_TOOLS: set[str] = {
    "upload_document", "create_share_link",
    "pdf_from_word", "pdf_from_excel", "pdf_from_ppt", "pdf_from_text",
    "pdf_from_image", "pdf_from_html", "pdf_from_url",
    "pdf_to_word", "pdf_to_excel", "pdf_to_ppt", "pdf_to_text",
    "pdf_to_html", "pdf_to_image",
    "pdf_merge", "pdf_split", "pdf_extract_pages", "pdf_extract_text",
    "pdf_compress", "pdf_flatten", "pdf_linearize", "pdf_manipulate",
    "pdf_delete_pages", "pdf_rotate_pages", "pdf_reorder_pages",
    "pdf_compare",
}

READ_ONLY_TOOLS: set[str] = {
    "get_pdf_properties",
    "show_pdf_viewer",
    "show_pdf_tools",
}

DESTRUCTIVE_TOOLS: set[str] = {
    "delete_document",
}

# get_task_result has no annotations (bare @mcp.tool())
NO_ANNOTATION_TOOLS: set[str] = {
    "get_task_result",
}


class TestToolAnnotations:
    """Verify MCP tool annotations match the intended access patterns."""

    async def test_write_tools_not_read_only(self, mcp_client):
        """WRITE tools have readOnlyHint=False, destructiveHint=False."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}
        for name in WRITE_TOOLS:
            tool = tools_by_name[name]
            ann = tool.annotations
            assert ann is not None, f"Tool '{name}' has no annotations"
            assert ann.readOnlyHint is False, (
                f"Tool '{name}' readOnlyHint should be False, got {ann.readOnlyHint}"
            )
            assert ann.destructiveHint is False, (
                f"Tool '{name}' destructiveHint should be False, got {ann.destructiveHint}"
            )

    async def test_read_only_tools(self, mcp_client):
        """READ_ONLY tools have readOnlyHint=True, destructiveHint=False."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}
        for name in READ_ONLY_TOOLS:
            tool = tools_by_name[name]
            ann = tool.annotations
            assert ann is not None, f"Tool '{name}' has no annotations"
            assert ann.readOnlyHint is True, (
                f"Tool '{name}' readOnlyHint should be True, got {ann.readOnlyHint}"
            )
            assert ann.destructiveHint is False, (
                f"Tool '{name}' destructiveHint should be False, got {ann.destructiveHint}"
            )

    async def test_destructive_tools(self, mcp_client):
        """DESTRUCTIVE tools have destructiveHint=True."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}
        for name in DESTRUCTIVE_TOOLS:
            tool = tools_by_name[name]
            ann = tool.annotations
            assert ann is not None, f"Tool '{name}' has no annotations"
            assert ann.destructiveHint is True, (
                f"Tool '{name}' destructiveHint should be True, got {ann.destructiveHint}"
            )

    async def test_no_annotation_tools(self, mcp_client):
        """Tools registered without annotations have annotations=None."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}
        for name in NO_ANNOTATION_TOOLS:
            tool = tools_by_name[name]
            assert tool.annotations is None, (
                f"Tool '{name}' should have no annotations, got {tool.annotations}"
            )

    async def test_all_tools_classified(self, mcp_client):
        """Every registered tool is in exactly one annotation category."""
        tools = await mcp_client.list_tools()
        all_classified = WRITE_TOOLS | READ_ONLY_TOOLS | DESTRUCTIVE_TOOLS | NO_ANNOTATION_TOOLS
        tool_names = {t.name for t in tools}
        unclassified = tool_names - all_classified
        assert not unclassified, f"Tools not classified in annotation tests: {unclassified}"
