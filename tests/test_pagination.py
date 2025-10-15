"""Tests for pagination in tools."""

from unittest.mock import patch

import pytest

from gitlab_review_mcp.server import mcp


class TestCommentsPagination:
    """Tests for get_merge_request_comments pagination."""

    @pytest.mark.asyncio
    async def test_get_merge_request_comments_with_pagination(self):
        """Test that get_merge_request_comments returns comments with pagination."""
        tool_func = mcp._tool_manager._tools["get_merge_request_comments"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_comments"
        ) as mock_get:
            mock_get.return_value = {
                "comments": [
                    {
                        "note_id": 123,
                        "discussion_id": "abc123",
                        "author": "testuser",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z",
                        "body": "Test comment with suggestion",
                        "system": False,
                        "resolvable": True,
                        "resolved": False,
                        "file_path": "test.py",
                        "suggestions": [
                            {
                                "id": 456,
                                "from_line": 10,
                                "to_line": 12,
                                "from_content": "old code",
                                "to_content": "new code",
                                "applicable": True,
                                "applied": False,
                                "appliable": True,
                            }
                        ],
                    }
                ],
                "total": 45,
                "page": 1,
                "per_page": 20,
                "total_pages": 3,
            }

            result = await tool_func(project_id=1, mr_iid=1, page=1)
            assert isinstance(result, str)
            assert "Test comment with suggestion" in result
            assert "page 1 of 3" in result
            assert "Use page=2 to see next page" in result


class TestCommitsPagination:
    """Tests for get_merge_request_commits pagination."""

    @pytest.mark.asyncio
    async def test_get_merge_request_commits_with_pagination(self):
        """Test that get_merge_request_commits returns commits with pagination."""
        tool_func = mcp._tool_manager._tools["get_merge_request_commits"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_commits"
        ) as mock_get:
            mock_get.return_value = {
                "commits": [
                    {
                        "id": "abc123def456",
                        "short_id": "abc123",
                        "title": "Test commit",
                        "message": "Test commit message",
                        "author_name": "Test User",
                        "author_email": "test@example.com",
                        "authored_date": "2025-01-01T00:00:00Z",
                        "committer_name": "Test User",
                        "committer_email": "test@example.com",
                        "committed_date": "2025-01-01T00:00:00Z",
                        "web_url": "https://gitlab.com/group/project/-/commit/abc123def456",
                    }
                ],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "total_pages": 5,
            }

            result = await tool_func(project_id=1, mr_iid=1, page=1)
            assert isinstance(result, str)
            assert "Test commit" in result
            assert "page 1 of 5" in result
            assert "Use page=2 to see next page" in result


class TestDiffsPagination:
    """Tests for get_merge_request_diffs pagination."""

    @pytest.mark.asyncio
    async def test_get_merge_request_diffs_with_pagination(self):
        """Test that get_merge_request_diffs returns diffs with pagination."""
        tool_func = mcp._tool_manager._tools["get_merge_request_diffs"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_diffs"
        ) as mock_get:
            mock_get.return_value = {
                "diffs": [
                    {
                        "id": "abc123",
                        "base_commit_sha": "base123",
                        "head_commit_sha": "head123",
                        "start_commit_sha": "start123",
                        "created_at": "2025-01-01T00:00:00Z",
                        "state": "collected",
                        "diffs": [
                            {
                                "old_path": "test.py",
                                "new_path": "test.py",
                                "a_mode": "100644",
                                "b_mode": "100644",
                                "new_file": False,
                                "renamed_file": False,
                                "deleted_file": False,
                                "diff": "@@ -1 +1 @@\n-old\n+new",
                            }
                        ],
                    }
                ],
                "total": 25,
                "page": 1,
                "per_page": 20,
                "total_pages": 2,
            }

            result = await tool_func(project_id=1, mr_iid=1, page=1)
            assert isinstance(result, str)
            assert "test.py" in result
            assert "page 1 of 2" in result
            assert "Use page=2 to see next page" in result
