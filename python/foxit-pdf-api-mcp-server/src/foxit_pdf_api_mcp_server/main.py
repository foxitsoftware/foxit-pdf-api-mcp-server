"""Main entry point for Foxit PDF API MCP Server."""

import argparse
import os
import sys

from .server import mcp

#HTTP mode is not yet available. We are currently implementing it
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
        default="0.0.0.0",
        help="Host to bind to for HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.getenv("SERVER_PORT", "8080")),
        help="Port to bind to for HTTP transport (default: $SERVER_PORT or 8080)",
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        # Run in stdio mode (the default transport for MCP clients).
        # FastMCP.run() is synchronous and manages its own event loop, so it must
        # not be wrapped in asyncio.run() (that raises TypeError on fastmcp>=3).
        mcp.run()
    elif args.transport == "http":
        # Run in HTTP mode
        print(f"Starting Foxit PDF API MCP Server on http://{args.host}:{args.port}", file=sys.stderr)
        mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
