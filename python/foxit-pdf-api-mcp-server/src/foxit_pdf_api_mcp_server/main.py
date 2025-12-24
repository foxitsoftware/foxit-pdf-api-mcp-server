"""Main entry point for Foxit PDF API MCP Server."""

import argparse
import asyncio
import sys

from .server import mcp


def main() -> None:
    """Run the MCP server."""
    parser = argparse.ArgumentParser(
        description="Foxit PDF API MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode: stdio (default) or http (HTTP server)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Port to bind to for HTTP transport (default: 8000)",
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        # Run in stdio mode (default for MCP clients like Claude Desktop)
        asyncio.run(mcp.run())
    elif args.transport == "http":
        # Run in HTTP mode
        print(f"Starting Foxit PDF API MCP Server on http://{args.host}:{args.port}", file=sys.stderr)
        asyncio.run(mcp.run(transport="http", host=args.host, port=args.port))


if __name__ == "__main__":
    main()
