"""Gitlab Review MCP MCP server."""

import argparse

from fastmcp import FastMCP

from gitlab_review_mcp.config import get_settings
from gitlab_review_mcp.tools import gitlab_tools
from gitlab_review_mcp.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

# Initialize MCP server
mcp: FastMCP = FastMCP("Gitlab Review MCP")

# Register GitLab tools
mcp.tool()(gitlab_tools.list_projects)
mcp.tool()(gitlab_tools.list_merge_requests)
mcp.tool()(gitlab_tools.get_merge_request)
mcp.tool()(gitlab_tools.get_merge_request_diffs)
mcp.tool()(gitlab_tools.get_merge_request_comments)
mcp.tool()(gitlab_tools.get_merge_request_commits)
mcp.tool()(gitlab_tools.add_merge_request_comment)
mcp.tool()(gitlab_tools.update_merge_request_comment)
mcp.tool()(gitlab_tools.reply_to_merge_request_comment)
mcp.tool()(gitlab_tools.add_merge_request_line_comment)
mcp.tool()(gitlab_tools.get_issue)
mcp.tool()(gitlab_tools.update_merge_request)
mcp.tool()(gitlab_tools.apply_suggestion)
mcp.tool()(gitlab_tools.apply_suggestions)


def main() -> None:
    """Main entry point for the MCP server."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level, include_console=settings.show_logs)

    parser = argparse.ArgumentParser(
        description="Gitlab Review MCP with multiple transport support"
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "http", "streamable-http", "streamable_http"],
        default="stdio",
        help="Transport type: stdio (default), sse (legacy), http/streamable-http/streamable_http (modern)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE or Streamable HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host for SSE or Streamable HTTP transport (default: 0.0.0.0)",
    )

    args, _ = parser.parse_known_args()

    logger.info("Starting Gitlab Review MCP...")

    logger.info(f"Transport: {args.transport}")

    if args.transport == "stdio":
        mcp.run(show_banner=False)
    elif args.transport == "sse":
        logger.info(f"Starting SSE server on http://{args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port, show_banner=False)
    elif args.transport in ("http", "streamable-http", "streamable_http"):
        logger.info(f"Starting HTTP server on http://{args.host}:{args.port}")
        mcp.run(transport="http", host=args.host, port=args.port, show_banner=False)


if __name__ == "__main__":
    main()
