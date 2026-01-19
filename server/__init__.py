"""
GitLab MCP Server Package
"""

from .gitlab_server import mcp
from .config import GITLAB_API, GITLAB_TOKEN, client

__all__ = ["mcp", "GITLAB_API", "GITLAB_TOKEN", "client"]
