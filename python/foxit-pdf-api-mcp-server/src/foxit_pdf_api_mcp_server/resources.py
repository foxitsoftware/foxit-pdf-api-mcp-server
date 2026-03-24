"""Shared runtime resources (client/mcp + widget HTML resources).

This module exists to break circular imports:
- server.py imports tools to register @mcp.tool()
- tools previously imported server.py to access client/mcp and template URIs

tools MUST import from this module instead of server.py.
This module MUST NOT import any tool modules.
"""

from starlette.responses import Response
from starlette.requests import Request
from pathlib import Path

from fastmcp import FastMCP
from dataclasses import dataclass
from .__version__ import __version__
from .client import FoxitPDFClient
from .config import config
import mcp.types as types
import os
import sys

# Widget template resources
PDF_TOOLS_WIDGET_TEMPLATE_URI = "ui://widget/foxit-pdf-tools.html"
VIEWER_WIDGET_TEMPLATE_URI = "ui://widget/foxit-pdf-viewer.html"
WIDGET_MIME_TYPE = "text/html+skybridge"
WIDGET_DEBUG = os.getenv("FOXIT_WIDGET_DEBUG", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}


def _widget_debug(msg: str) -> None:
    if WIDGET_DEBUG:
        print(f"[foxit:widget] {msg}", file=sys.stderr)

# Create Foxit PDF API client
client = FoxitPDFClient(
    base_url=config.api_base_url,
    client_id=config.client_id,
    client_secret=config.client_secret,
    default_timeout=config.default_timeout,
    poll_interval=config.poll_interval,
    max_retries=config.max_retries,
    debug_http=config.debug_http,
)

# Create FastMCP server
mcp = FastMCP(
    name="Foxit PDF API MCP Server",
    version=__version__,
)


@dataclass(frozen=True)
class Widget:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str


def _load_widget_html(component_name: str) -> str:
    """Load widget HTML from the web/dist directory."""
    current_dir = Path(__file__).resolve().parent
    web_dist_dir = current_dir.parent.parent / "web" / "dist"

    widget_html_path = web_dist_dir / f"{component_name}.html"
    if not widget_html_path.exists():
        raise FileNotFoundError(f"Widget HTML not found at {widget_html_path}")
    html = widget_html_path.read_text(encoding="utf8")
    _widget_debug(
        f"loaded html component={component_name} path={widget_html_path} bytes={len(html.encode('utf-8'))}"
    )
    return html


widgets: list[Widget] = [
    Widget(
        identifier="pdf-tools",
        title="Show PDF Tools",
        template_uri=PDF_TOOLS_WIDGET_TEMPLATE_URI,
        invoking="Using PDF tools",
        invoked="Served PDF tools",
        html=_load_widget_html("index"),
        response_text="Rendered PDF tools!",
    ),
    Widget(
        identifier="pdf-viewer",
        title="Show PDF Viewer",
        template_uri=VIEWER_WIDGET_TEMPLATE_URI,
        invoking="Viewing a PDF document",
        invoked="Displayed a PDF document",
        html=_load_widget_html("viewer"),
        response_text="Rendered a PDF viewer!",
    ),
]


def _tool_meta(widget: Widget) -> dict[str, any]:
    widget_csp = {
        "connect_domains": ["data:", "blob:", "https://*.foxit.com", "https://*.foxitcloud.com"],
        "redirect_domains": ["https://*.foxit.com", "https://*.foxitcloud.com"],
        "resource_domains": [
            "data:",
            "blob:",
            "https://cdn.tailwindcss.com",
            "https://cdn.jsdelivr.net",
            "https://unpkg.com",
            "https://threejs.org",
            "https://*.foxit.com",
            "https://*.foxitcloud.com",
        ],
    }

    return {
        "mcp/outputTemplate": widget.template_uri,
        # Compatibility keys for hosts implementing OpenAI-style widget metadata mapping.
        "openai/outputTemplate": widget.template_uri,
        "mcp/toolInvocation/invoking": widget.invoking,
        "mcp/toolInvocation/invoked": widget.invoked,
        "mcp/widgetAccessible": True,
        "openai/widgetAccessible": True,
        "mcp/widgetDomain": "https://pdfonline.foxit.com",
        "mcp/widgetCSP": widget_csp,
    }


WIDGETS_BY_URI: dict[str, Widget] = {
    widget.template_uri: widget for widget in widgets
}


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    _widget_debug(f"read_resource requested uri={req.params.uri}")
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        _widget_debug(f"read_resource miss uri={req.params.uri}")
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=WIDGET_MIME_TYPE,
            text=widget.html,
            _meta=_tool_meta(widget),
        )
    ]

    _widget_debug(
        f"read_resource hit uri={widget.template_uri} mime={WIDGET_MIME_TYPE} html_bytes={len(widget.html.encode('utf-8'))}"
    )

    return types.ServerResult(types.ReadResourceResult(contents=contents))


mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


@mcp._mcp_server.list_resources()
async def _list_resources() -> list[types.Resource]:
    _widget_debug("list_resources called")
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType=WIDGET_MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> list[types.ResourceTemplate]:
    _widget_debug("list_resource_templates called")
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=f"{widget.title} widget markup",
            mimeType=WIDGET_MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp.custom_route("/.well-known/mcp-challenge", methods=["GET", "OPTIONS"])
async def protected_resource_metadata(request: Request) -> Response:
    _widget_debug(f"mcp_challenge route method={request.method}")
    if request.method == "OPTIONS":
        return Response(status_code=204)
    # Verification token
    secret = os.getenv("VERIFICATION_TOKEN",
                       "REDACTED")
    return Response(content=secret, media_type="text/plain")


_widget_debug(
    "widget registry initialized "
    + ", ".join([f"{w.identifier}:{w.template_uri}" for w in widgets])
)
