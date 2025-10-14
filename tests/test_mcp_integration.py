"""Integration tests for MCP server."""

import os
from unittest.mock import patch

import pytest

from gitlab_review_mcp.server import mcp


class TestMCPIntegration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that the MCP server can be initialized."""
        assert mcp is not None
        assert mcp.name == "Gitlab Review MCP"

    def test_all_tools_registered(self):
        """Test that all expected tools are registered with the MCP server."""
        expected_tools = {
            "list_projects",
            "list_merge_requests",
            "get_merge_request",
            "get_merge_request_diffs",
            "get_merge_request_comments",
            "get_merge_request_commits",
            "add_merge_request_comment",
            "update_merge_request_comment",
            "reply_to_merge_request_comment",
            "add_merge_request_line_comment",
            "get_issue",
            "update_merge_request",
            "apply_suggestion",
            "apply_suggestions",
        }

        registered_tools = set(mcp._tool_manager._tools.keys())

        missing_tools = expected_tools - registered_tools
        extra_tools = registered_tools - expected_tools

        assert not missing_tools, f"Missing tools: {missing_tools}"
        assert not extra_tools, f"Unexpected tools: {extra_tools}"
        assert registered_tools == expected_tools

    def test_tool_docstrings(self):
        """Test that all tools have proper docstrings."""
        import inspect

        for tool_name, tool in mcp._tool_manager._tools.items():
            func = tool.fn
            assert func.__doc__ is not None, f"Tool {tool_name} missing docstring"
            assert (
                len(func.__doc__.strip()) > 0
            ), f"Tool {tool_name} has empty docstring"

            docstring = func.__doc__
            assert "Returns:" in docstring, f"Tool {tool_name} missing Returns section"

            sig = inspect.signature(func)
            if len(sig.parameters) > 0:
                assert (
                    "Args:" in docstring
                ), f"Tool {tool_name} takes parameters but missing Args section"

    def test_tool_type_hints(self):
        """Test that all tools have proper type hints."""
        import inspect

        for tool_name, tool in mcp._tool_manager._tools.items():
            func = tool.fn
            sig = inspect.signature(func)

            for param_name, param in sig.parameters.items():
                assert (
                    param.annotation != inspect.Parameter.empty
                ), f"Tool {tool_name} parameter {param_name} missing type hint"

            assert (
                sig.return_annotation != inspect.Signature.empty
            ), f"Tool {tool_name} missing return type hint"

    @patch.dict(os.environ, {"GITLAB_REVIEW_MCP_SHOW_LOGS": "false"}, clear=False)
    @patch("gitlab_review_mcp.server.mcp.run")
    @patch("gitlab_review_mcp.server.logger")
    def test_main_stdio_transport(self, mock_logger, mock_run):
        """Test main function with stdio transport (default)."""
        from gitlab_review_mcp.server import main

        with patch("sys.argv", ["gitlab-review-mcp"]):
            main()

        mock_logger.info.assert_any_call("Transport: stdio")
        mock_run.assert_called_once_with(show_banner=False)

    @patch.dict(os.environ, {"GITLAB_REVIEW_MCP_SHOW_LOGS": "false"}, clear=False)
    @patch("gitlab_review_mcp.server.mcp.run")
    @patch("gitlab_review_mcp.server.logger")
    def test_main_http_transport(self, mock_logger, mock_run):
        """Test main function with HTTP transport."""
        from gitlab_review_mcp.server import main

        with patch("sys.argv", ["gitlab-review-mcp", "--transport", "http"]):
            main()

        mock_logger.info.assert_any_call("Transport: http")
        mock_logger.info.assert_any_call("Starting HTTP server on http://0.0.0.0:8000")
        mock_run.assert_called_once_with(
            transport="http", host="0.0.0.0", port=8000, show_banner=False
        )
