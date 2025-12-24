"""Foxit PDF API MCP Server setup."""

from fastmcp import FastMCP

from .__version__ import __version__
from .client import FoxitPDFClient
from .config import config

# Create Foxit PDF API client
client = FoxitPDFClient(
    base_url=config.api_base_url,
    client_id=config.client_id,
    client_secret=config.client_secret,
    default_timeout=config.default_timeout,
    poll_interval=config.poll_interval,
    max_retries=config.max_retries,
)

# Create FastMCP server
mcp = FastMCP(
    name="Foxit PDF API MCP Server",
    version=__version__,
)

# Import tools to register them (tools use @mcp.tool() decorator)
# Document lifecycle tools
from .tools import document_lifecycle  # noqa: E402, F401

# PDF creation tools
from .tools import pdf_creation  # noqa: E402, F401

# PDF conversion tools
from .tools import pdf_conversion  # noqa: E402, F401

# PDF manipulation tools
from .tools import pdf_manipulation  # noqa: E402, F401

# PDF security tools
from .tools import pdf_security  # noqa: E402, F401

# PDF properties tools
from .tools import pdf_properties  # noqa: E402, F401

# PDF analysis tools
from .tools import pdf_analysis  # noqa: E402, F401

# PDF forms tools
from .tools import pdf_forms  # noqa: E402, F401
