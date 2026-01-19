"""
GitLab MCP Server

This module defines the FastMCP server and imports all tools.
The mcp instance is exported for use by the entry point.
"""

from .config import mcp
from .mcp_tools.repo_tools import *
from .mcp_tools.file_tools import *
from .mcp_tools.search_tools import *
from .mcp_tools.branch_tools import *
from .mcp_tools.project_tools import *
from .mcp_tools.commit_tools import *
from .mcp_tools.merge_request_tools import *
from .mcp_tools.issue_tools import *

# Export mcp for the entry point
__all__ = ["mcp"]