# Gitlab Review MCP

A Model Context Protocol (MCP) server for GitLab code review and project management. Provides comprehensive tools for interacting with GitLab projects, merge requests, issues, and code reviews through Claude AI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP->=2.10.6+-green.svg)](https://github.com/jlowin/fastmcp)

## Features

- **GitLab Integration** - Complete GitLab API integration using python-gitlab
- **Code Review Tools** - List projects, MRs, view diffs, and add comments
- **Merge Request Management** - Create, update, and review merge requests
- **Suggestion Support** - View and apply code change suggestions
- **Issue Tracking** - Fetch and manage GitLab issues
- **Line Comments** - Add precise code review comments to specific lines
- **Comment Management** - Update existing comments and reply to discussions
- **Singleton Pattern** - Efficient connection reuse across all tools
- **Type Safety** - Full Pydantic validation with structured models
- **Error Handling** - Comprehensive error reporting and graceful failure modes
- **Logging** - Centralized logging configuration with optional console output

## Installation

### Using uvx (Recommended)

```bash
uvx gitlab-review-mcp
```

### Using uv

```bash
uv add gitlab-review-mcp
uv run gitlab-review-mcp
```

## Configuration

### Environment Variables

Required:
- **`GITLAB_URL`** - GitLab instance URL (default: `https://gitlab.com`)
- **`GITLAB_PRIVATE_TOKEN`** - Your GitLab personal access token

Optional:
- **`GITLAB_REVIEW_MCP_SHOW_LOGS`** - Set to `"true"` to enable detailed logging (default: `false`)

### Getting Your GitLab Token

1. Go to your GitLab instance (e.g., https://gitlab.com)
2. Navigate to **Settings** → **Access Tokens**
3. Create a new token with the following scopes:
   - `api` - Full API access
   - `read_api` - Read API (if you only need read operations)
4. Copy the token and add it to your environment configuration

### Transport Types

1. **`stdio`** (default) - Standard input/output, client launches server automatically
2. **`http`** (recommended for remote) - Modern HTTP transport (aliases: `streamable-http`, `streamable_http`)
3. **`sse`** (legacy) - Server-Sent Events transport (deprecated)

---

## 🚀 Quick Start (uvx)

### Stdio Transport

```json
{
  "mcpServers": {
    "gitlab-review-mcp": {
      "command": "uvx",
      "args": ["--no-progress", "gitlab-review-mcp"],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_PRIVATE_TOKEN": "your-token-here",
        "GITLAB_REVIEW_MCP_SHOW_LOGS": "false"
      }
    }
  }
}
```

### HTTP Transport

**Start server:**
```bash
uvx --no-progress gitlab-review-mcp --transport http --port 8000 --host 0.0.0.0
```

**Client config:**
```json
{
  "mcpServers": {
    "gitlab-review-mcp": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

### SSE Transport

**Start server:**
```bash
uvx --no-progress gitlab-review-mcp --transport sse --port 8000 --host 0.0.0.0
```

**Client config:**
```json
{
  "mcpServers": {
    "gitlab-review-mcp": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

---

## 🔧 Alternative Commands

### Stdio with `uv run --with`

```json
{
  "mcpServers": {
    "gitlab-review-mcp": {
      "command": "uv",
      "args": ["run", "--with", "gitlab-review-mcp", "gitlab-review-mcp"],
      "env": {
"GITLAB_REVIEW_MCP_SHOW_LOGS": "false"
      }
    }
  }
}
```

### Stdio with `uv run --directory` (Local Development)

```json
{
  "mcpServers": {
    "gitlab-review-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/gitlab-review-mcp", "gitlab-review-mcp"],
      "env": {
"GITLAB_REVIEW_MCP_SHOW_LOGS": "true"
      }
    }
  }
}
```

### HTTP/SSE Alternative Commands

All transport types can use these alternative commands:

```bash
# Using uv run --with
uv run --with gitlab-review-mcp gitlab-review-mcp --transport http --port 8000

# Using uv run --directory (local development)
cd /path/to/gitlab-review-mcp
uv run gitlab-review-mcp --transport http --port 8000
```

## Available Tools

### Project Management

#### `list_projects`
List available GitLab projects with optional filtering.
- **Parameters**:
  - `search` (optional) - Filter projects by name
  - `owned` (optional) - Only show owned projects (default: `false`)
  - `membership` (optional) - Only show projects you're a member of (default: `true`)
- **Returns**: Formatted list of projects with ID, name, description, URL, and default branch

### Merge Request Operations

#### `list_merge_requests`
List merge requests for a specific project.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `state` (optional) - Filter by state: `opened`, `closed`, `merged`, `all`
  - `author_id` (optional) - Filter by author user ID
  - `assignee_id` (optional) - Filter by assignee user ID
  - `labels` (optional) - Filter by label names (list)
- **Returns**: Formatted list of MRs with IID, title, state, author, branches, and URLs

#### `get_merge_request`
Fetch detailed merge request information.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID (e.g., !123)
- **Returns**: MR details including title, description, state, branches, author, and timestamps

#### `get_merge_request_diffs`
Get code changes (diffs) for a merge request.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
- **Returns**: Complete diff information including file paths, commit SHAs, and code changes

#### `add_merge_request_comment`
Add a general comment to a merge request.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
  - `comment` (required) - Comment text
- **Returns**: Confirmation with comment ID and details

#### `add_merge_request_line_comment`
Add a line-specific comment to merge request code.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
  - `file_path` (required) - File path in repository
  - `line_number` (required) - Line number in new version
  - `comment` (required) - Comment text
  - `base_sha` (required) - Base commit SHA (from diff)
  - `head_sha` (required) - Head commit SHA (from diff)
  - `start_sha` (required) - Start commit SHA (from diff)
  - `old_line` (optional) - Line number in old version
- **Returns**: Confirmation with discussion ID and comment details

#### `get_merge_request_comments`
Get all comments and discussions from a merge request, including suggestions.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
- **Returns**: All comments with note IDs, discussion IDs, authors, timestamps, and embedded suggestions

#### `get_merge_request_commits`
Get all commits in a merge request.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
- **Returns**: List of commits with SHA, title, message, author, and timestamps

#### `update_merge_request_comment`
Update an existing merge request comment.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
  - `note_id` (required) - Note ID to update
  - `comment` (required) - Updated comment text
- **Returns**: Confirmation with updated comment details

#### `reply_to_merge_request_comment`
Reply to an existing discussion thread.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
  - `discussion_id` (required) - Discussion ID to reply to
  - `comment` (required) - Reply comment text
- **Returns**: Confirmation with reply details

#### `update_merge_request`
Update merge request title and/or description.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `mr_iid` (required) - Merge request IID
  - `title` (optional) - New title
  - `description` (optional) - New description
- **Returns**: Updated MR details

### Suggestion Management

#### `apply_suggestion`
Apply a single code change suggestion.
- **Parameters**:
  - `suggestion_id` (required) - Suggestion ID to apply
- **Returns**: Confirmation with commit ID

#### `apply_suggestions`
Apply multiple code change suggestions in batch.
- **Parameters**:
  - `suggestion_ids` (required) - List of suggestion IDs to apply
- **Returns**: Confirmation with commit ID and applied suggestion IDs

### Issue Management

#### `get_issue`
Fetch detailed issue information.
- **Parameters**:
  - `project_id` (required) - GitLab project ID
  - `issue_iid` (required) - Issue IID (e.g., #123)
- **Returns**: Issue details including title, description, state, assignees, labels, and timestamps


## Testing

The project includes comprehensive tests:

```bash
# Run all tests
make test

# Run with coverage
make test-cov
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/midodimori/gitlab-review-mcp.git
cd gitlab-review-mcp

# Install with development dependencies
make install-dev

# Run tests
make test

# Format and lint code
make format

# Check code style and types
make lint

# Run the server locally
make run

# See all available commands
make help
```

### Project Structure

```
gitlab-review-mcp/
├── .github/
│   └── workflows/
│       ├── publish.yml            # PyPI publishing workflow
│       └── test.yml               # CI tests workflow
├── src/gitlab_review_mcp/
│   ├── __init__.py
│   ├── server.py                  # MCP server implementation
│   ├── config.py                  # Configuration settings
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   └── gitlab_service.py      # GitLab API service
│   ├── tools/                     # MCP tool implementations
│   │   ├── __init__.py
│   │   └── gitlab_tools.py        # GitLab tools (14 tools)
│   └── utils/                     # Utility modules
│       ├── __init__.py
│       └── logging.py             # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_server.py             # Tool function tests with mocks
│   └── test_mcp_integration.py    # MCP integration tests
├── .env.example
├── .gitignore
├── .python-version
├── LICENSE
├── Makefile
├── PUBLISHING.md                  # Publishing guide
├── pyproject.toml                 # Project configuration
├── pytest.ini
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/desktop)

## Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the comprehensive test suite for usage examples