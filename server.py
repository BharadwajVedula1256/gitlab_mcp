"""
GitLab FastMCP Server - Entry Point

This is the main entry point for the FastMCP server.
Run with: python server.py
"""

from server.gitlab_server import mcp

if __name__ == "__main__":
    mcp.run()
