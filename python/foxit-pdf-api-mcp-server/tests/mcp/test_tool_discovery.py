"""MCP Protocol Tests – Tool Discovery.

Verify that ``list_tools()`` exposes every registered tool with correct
names, non-empty descriptions, and valid ``inputSchema``.
"""

import pytest

pytestmark = pytest.mark.asyncio


# -------------------------------------------------------------------
# Expected tool catalogue – derived from server.py active imports.
# Update this set when tools are added / removed / commented out.
# -------------------------------------------------------------------
EXPECTED_TOOLS: set[str] = {
    # document lifecycle
    "upload_document",
    "create_share_link",
    "delete_document",
    # pdf creation
    "pdf_from_word",
    "pdf_from_excel",
    "pdf_from_ppt",
    "pdf_from_text",
    "pdf_from_image",
    "pdf_from_html",
    "pdf_from_url",
    # pdf conversion
    "pdf_to_word",
    "pdf_to_excel",
    "pdf_to_ppt",
    "pdf_to_text",
    "pdf_to_html",
    "pdf_to_image",
    # pdf manipulation
    "pdf_merge",
    "pdf_split",
    "pdf_extract_pages",
    "pdf_extract_text",
    "pdf_compress",
    "pdf_flatten",
    "pdf_linearize",
    "pdf_manipulate",
    "pdf_delete_pages",
    "pdf_rotate_pages",
    "pdf_reorder_pages",
    # pdf properties
    "get_pdf_properties",
    # pdf analysis
    "pdf_compare",
    # task status
    "get_task_result",
    # widget
    "show_pdf_viewer",
    "show_pdf_tools",
}


class TestToolDiscovery:
    """list_tools() returns all registered tools with valid metadata."""

    async def test_all_expected_tools_registered(self, mcp_client):
        """Every tool in EXPECTED_TOOLS is returned by list_tools()."""
        tools = await mcp_client.list_tools()
        tool_names = {t.name for t in tools}
        missing = EXPECTED_TOOLS - tool_names
        assert not missing, f"Tools missing from server: {missing}"

    async def test_no_unexpected_tools(self, mcp_client):
        """No surprise tools that are not in the expected set."""
        tools = await mcp_client.list_tools()
        tool_names = {t.name for t in tools}
        extra = tool_names - EXPECTED_TOOLS
        assert not extra, f"Unexpected tools registered: {extra}"

    async def test_tool_count(self, mcp_client):
        """Total tool count matches expectation."""
        tools = await mcp_client.list_tools()
        assert len(tools) == len(EXPECTED_TOOLS)

    async def test_each_tool_has_description(self, mcp_client):
        """Every tool has a non-empty description string."""
        tools = await mcp_client.list_tools()
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' has no description"
            assert len(tool.description.strip()) > 10, (
                f"Tool '{tool.name}' description too short: {tool.description!r}"
            )

    async def test_each_tool_has_input_schema(self, mcp_client):
        """Every tool exposes an inputSchema with type=object."""
        tools = await mcp_client.list_tools()
        for tool in tools:
            schema = tool.inputSchema
            assert schema is not None, f"Tool '{tool.name}' has no inputSchema"
            assert schema.get("type") == "object", (
                f"Tool '{tool.name}' inputSchema type is not 'object': {schema.get('type')}"
            )

    async def test_required_params_in_schema(self, mcp_client):
        """Tools with required params declare them in the schema."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}

        # Tools that require document_id
        tools_needing_document_id = [
            "pdf_to_word", "pdf_to_excel", "pdf_to_ppt",
            "pdf_from_word", "pdf_from_excel",
            "delete_document", "create_share_link",
            "show_pdf_viewer", "get_pdf_properties",
        ]
        for name in tools_needing_document_id:
            tool = tools_by_name[name]
            required = tool.inputSchema.get("required", [])
            assert "document_id" in required, (
                f"Tool '{name}' should require 'document_id', got required={required}"
            )

    async def test_optional_params_not_required(self, mcp_client):
        """Parameters with default values are NOT in the required list."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}

        # pdf_to_word has optional 'password'
        tool = tools_by_name["pdf_to_word"]
        required = tool.inputSchema.get("required", [])
        assert "password" not in required, "password should be optional for pdf_to_word"

        # pdf_to_text has optional 'page_range' and 'password'
        tool = tools_by_name["pdf_to_text"]
        required = tool.inputSchema.get("required", [])
        assert "page_range" not in required
        assert "password" not in required

    async def test_schema_properties_defined(self, mcp_client):
        """Each tool's inputSchema has a 'properties' dict."""
        tools = await mcp_client.list_tools()
        for tool in tools:
            props = tool.inputSchema.get("properties")
            assert isinstance(props, dict), (
                f"Tool '{tool.name}' inputSchema.properties is not a dict"
            )

    async def test_schema_param_types(self, mcp_client):
        """Spot-check parameter type declarations in inputSchema."""
        tools = await mcp_client.list_tools()
        tools_by_name = {t.name: t for t in tools}

        # pdf_to_image: dpi should be integer (or anyOf with integer)
        tool = tools_by_name["pdf_to_image"]
        dpi_prop = tool.inputSchema["properties"].get("dpi", {})
        dpi_types = _collect_types(dpi_prop)
        assert "integer" in dpi_types, f"dpi should be integer type, got {dpi_prop}"

        # pdf_merge: document_ids should be array
        tool = tools_by_name["pdf_merge"]
        ids_prop = tool.inputSchema["properties"].get("document_ids", {})
        assert ids_prop.get("type") == "array", f"document_ids should be array, got {ids_prop}"

        # get_pdf_properties: include_extended_info should be boolean
        tool = tools_by_name["get_pdf_properties"]
        ext_prop = tool.inputSchema["properties"].get("include_extended_info", {})
        ext_types = _collect_types(ext_prop)
        assert "boolean" in ext_types, f"include_extended_info should be boolean, got {ext_prop}"


def _collect_types(prop: dict) -> set[str]:
    """Extract all type strings from a JSON Schema property (handles anyOf)."""
    types = set()
    if "type" in prop:
        types.add(prop["type"])
    for variant in prop.get("anyOf", []):
        if "type" in variant:
            types.add(variant["type"])
    return types
