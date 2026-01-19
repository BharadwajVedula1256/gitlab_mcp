# GitLab FastMCP Server

A [FastMCP](https://github.com/jlowin/fastmcp) server providing GitLab API tools for AI assistants.

## Features

**60+ tools** across 8 categories: Repository, Files, Commits, Branches, Issues, Merge Requests, Projects, and Search.

**Runtime Configuration**: Users provide their GitLab token when they start using the server - no hardcoded credentials needed!

## Usage

### First, configure your GitLab credentials:

When you start using the server, call the `configure_gitlab` tool:

```
configure_gitlab(
    api_url="https://gitlab.com/api/v4",
    token="your-gitlab-token"
)
```

This allows each user to use their own GitLab token without any environment variables.

### Check configuration status:
```
check_gitlab_config()
```

## Deployment to FastMCP

1. Push to GitHub
2. Go to [fastmcp.app](https://fastmcp.app) and deploy
3. Users configure their own token at runtime using `configure_gitlab`

## Project Structure

```
gitlab_fastmcp/
├── server.py              ← Entry point
├── server/
│   ├── __init__.py
│   ├── config.py          ← Runtime config + configure_gitlab tool
│   ├── gitlab_server.py
│   ├── schema.py
│   └── mcp_tools/         ← 8 tool files (60+ tools)
├── pyproject.toml
├── README.md
└── LICENSE
```

## Alternative: Environment Variables

You can also pre-configure via environment variables:

| Variable | Description |
|----------|-------------|
| `GITLAB_API` | GitLab API URL (default: `https://gitlab.com/api/v4`) |
| `GITLAB_TOKEN` | Your GitLab Personal Access Token |

## License

MIT License
