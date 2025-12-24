"""Foxit PDF API MCP Server."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("foxit-pdf-api-mcp-server")
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0-dev"
