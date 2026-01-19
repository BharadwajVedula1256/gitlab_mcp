"""
GitLab API Configuration

This module provides the FastMCP instance and HTTP client for GitLab API calls.
Supports both environment variables and runtime configuration via MCP tools.
"""

import os
import httpx
from fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("gitlab-server")

# GitLab API Configuration - can be set via env vars or runtime
_config = {
    "api_url": os.getenv("GITLAB_API", ""),
    "token": os.getenv("GITLAB_TOKEN", ""),
}

def get_gitlab_api():
    """Get the configured GitLab API URL."""
    return _config["api_url"]

def get_gitlab_token():
    """Get the configured GitLab token."""
    return _config["token"]

def set_gitlab_config(api_url: str = None, token: str = None):
    """Set GitLab configuration at runtime."""
    if api_url:
        _config["api_url"] = api_url
    if token:
        _config["token"] = token

def get_headers():
    """Get HTTP headers for GitLab API requests."""
    headers = {"Accept": "application/json"}
    if _config["token"]:
        headers["PRIVATE-TOKEN"] = _config["token"]
    return headers

def get_client():
    """Get an HTTP client with current configuration."""
    return httpx.AsyncClient(headers=get_headers(), timeout=30.0)

def is_configured():
    """Check if GitLab is properly configured."""
    return bool(_config["api_url"] and _config["token"])

# For backwards compatibility
GITLAB_API = property(lambda self: get_gitlab_api())
GITLAB_TOKEN = property(lambda self: get_gitlab_token())

# Register a configuration tool
@mcp.tool()
def configure_gitlab(
    api_url: str = "https://gitlab.com/api/v4",
    token: str = None
) -> dict:
    """
    Configure GitLab API credentials at runtime.
    
    Use this tool to set your GitLab credentials before using other GitLab tools.
    This allows you to provide your own GitLab token without requiring environment variables.
    
    Parameters:
    - api_url (string): GitLab API base URL. Default: "https://gitlab.com/api/v4"
    - token (string): Your GitLab Personal Access Token
    
    Returns:
    - A confirmation message with configuration status
    """
    if not token:
        return {
            "error": "Token is required",
            "message": "Please provide your GitLab Personal Access Token. "
                      "Create one at: https://gitlab.com/-/user_settings/personal_access_tokens"
        }
    
    set_gitlab_config(api_url=api_url, token=token)
    
    return {
        "status": "configured",
        "api_url": api_url,
        "message": "GitLab credentials configured successfully. You can now use GitLab tools."
    }

@mcp.tool()
def check_gitlab_config() -> dict:
    """
    Check the current GitLab configuration status.
    
    Returns:
    - Configuration status including whether API URL and token are set
    """
    return {
        "configured": is_configured(),
        "api_url": _config["api_url"] or "(not set)",
        "token_set": bool(_config["token"]),
        "message": "Ready to use GitLab tools." if is_configured() else 
                   "Please run configure_gitlab with your token first."
    }
