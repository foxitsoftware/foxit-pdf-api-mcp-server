"""Foxit PDF API MCP Server setup.

This module imports tools to register @mcp.tool() decorated functions.
To avoid circular imports (server -> tools -> server), shared runtime objects
(client/mcp and widget resources) live in resources.py and are re-exported here.
"""

# Re-export shared objects/constants from resources.py for backward compatibility.
from .resources import *


# Import tools to register them (tools use @mcp.tool() decorator)
# Document lifecycle tools
from .tools import document_lifecycle  # noqa: E402, F401

# PDF creation tools
from .tools import pdf_creation  # noqa: E402, F401

# PDF conversion tools
from .tools import pdf_conversion  # noqa: E402, F401

# # PDF manipulation tools
from .tools import pdf_manipulation  # noqa: E402, F401

# # PDF security tools
# from .tools import pdf_security  # noqa: E402, F401

# # PDF properties tools
from .tools import pdf_properties  # noqa: E402, F401

# # PDF analysis tools
from .tools import pdf_analysis  # noqa: E402, F401

# PDF security tools
from .tools import pdf_security  # noqa: E402, F401

# PDF forms tools
# from .tools import pdf_forms  # noqa: E402, F401

# Task status tool (async task polling)
from .tools import task_status  # noqa: E402, F401

from .tools import pdf_widget  # noqa: E402, F401
