"""Tests for server implementation."""

from unittest.mock import patch

import pytest

from gitlab_review_mcp.server import mcp


class TestListProjects:
    """Tests for list_projects tool."""

    @pytest.mark.asyncio
    async def test_list_projects_success(self):
        """Test that list_projects returns formatted project list."""
        tool_func = mcp._tool_manager._tools["list_projects"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.list_projects"
        ) as mock_list:
            mock_list.return_value = [
                {
                    "id": 1,
                    "name": "Test Project",
                    "path": "test-project",
                    "path_with_namespace": "group/test-project",
                    "description": "A test project",
                    "web_url": "https://gitlab.com/group/test-project",
                    "default_branch": "main",
                }
            ]

            result = await tool_func()
            assert isinstance(result, str)
            assert "Test Project" in result
            assert "group/test-project" in result

    @pytest.mark.asyncio
    async def test_list_projects_empty(self):
        """Test that list_projects handles no projects."""
        tool_func = mcp._tool_manager._tools["list_projects"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.list_projects"
        ) as mock_list:
            mock_list.return_value = []
            result = await tool_func()
            assert "No projects found" in result


class TestListMergeRequests:
    """Tests for list_merge_requests tool."""

    @pytest.mark.asyncio
    async def test_list_merge_requests_success(self):
        """Test that list_merge_requests returns formatted MR list."""
        tool_func = mcp._tool_manager._tools["list_merge_requests"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.list_merge_requests"
        ) as mock_list:
            mock_list.return_value = [
                {
                    "id": 100,
                    "iid": 1,
                    "title": "Test MR",
                    "state": "opened",
                    "merged": False,
                    "web_url": "https://gitlab.com/group/project/-/merge_requests/1",
                    "source_branch": "feature",
                    "target_branch": "main",
                    "author": "testuser",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-02T00:00:00Z",
                }
            ]

            result = await tool_func(project_id=1)
            assert isinstance(result, str)
            assert "Test MR" in result
            assert "!1" in result

    @pytest.mark.asyncio
    async def test_list_merge_requests_empty(self):
        """Test that list_merge_requests handles no MRs."""
        tool_func = mcp._tool_manager._tools["list_merge_requests"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.list_merge_requests"
        ) as mock_list:
            mock_list.return_value = []
            result = await tool_func(project_id=1)
            assert "No merge requests found" in result


class TestGetMergeRequest:
    """Tests for get_merge_request tool."""

    @pytest.mark.asyncio
    async def test_get_merge_request_success(self):
        """Test that get_merge_request returns MR details."""
        tool_func = mcp._tool_manager._tools["get_merge_request"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request"
        ) as mock_get:
            mock_get.return_value = {
                "id": 100,
                "iid": 1,
                "title": "Test MR",
                "description": "Test description",
                "state": "opened",
                "merged": False,
                "web_url": "https://gitlab.com/group/project/-/merge_requests/1",
                "source_branch": "feature",
                "target_branch": "main",
                "author": "testuser",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "comments": [],
            }

            result = await tool_func(project_id=1, mr_iid=1)
            assert isinstance(result, str)
            assert "Test MR" in result
            assert "Test description" in result


class TestGetMergeRequestDiffs:
    """Tests for get_merge_request_diffs tool."""

    @pytest.mark.asyncio
    async def test_get_merge_request_diffs_success(self):
        """Test that get_merge_request_diffs returns diff information."""
        tool_func = mcp._tool_manager._tools["get_merge_request_diffs"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_diffs"
        ) as mock_get:
            mock_get.return_value = [
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
            ]

            result = await tool_func(project_id=1, mr_iid=1)
            assert isinstance(result, str)
            assert "test.py" in result


class TestAddMergeRequestComment:
    """Tests for add_merge_request_comment tool."""

    @pytest.mark.asyncio
    async def test_add_merge_request_comment_success(self):
        """Test that add_merge_request_comment adds comment."""
        tool_func = mcp._tool_manager._tools["add_merge_request_comment"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.add_merge_request_comment"
        ) as mock_add:
            mock_add.return_value = {
                "id": 123,
                "body": "Test comment",
                "author": "testuser",
                "created_at": "2025-01-01T00:00:00Z",
            }

            result = await tool_func(project_id=1, mr_iid=1, comment="Test comment")
            assert isinstance(result, str)
            assert "Comment added successfully" in result
            assert "Test comment" in result


class TestAddMergeRequestLineComment:
    """Tests for add_merge_request_line_comment tool."""

    @pytest.mark.asyncio
    async def test_add_merge_request_line_comment_success(self):
        """Test that add_merge_request_line_comment adds line comment."""
        tool_func = mcp._tool_manager._tools["add_merge_request_line_comment"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.add_merge_request_line_comment"
        ) as mock_add:
            mock_add.return_value = {
                "id": "disc123",
                "body": "Line comment",
                "position": {
                    "base_sha": "base123",
                    "start_sha": "start123",
                    "head_sha": "head123",
                    "position_type": "text",
                    "new_path": "test.py",
                    "old_path": "test.py",
                    "new_line": 10,
                },
            }

            result = await tool_func(
                project_id=1,
                mr_iid=1,
                file_path="test.py",
                line_number=10,
                comment="Line comment",
                base_sha="base123",
                head_sha="head123",
                start_sha="start123",
            )
            assert isinstance(result, str)
            assert "Line comment added successfully" in result
            assert "test.py" in result


class TestGetMergeRequestComments:
    """Tests for get_merge_request_comments tool."""

    @pytest.mark.asyncio
    async def test_get_merge_request_comments_success(self):
        """Test that get_merge_request_comments returns comments with suggestions."""
        tool_func = mcp._tool_manager._tools["get_merge_request_comments"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_comments"
        ) as mock_get:
            mock_get.return_value = [
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
            ]

            result = await tool_func(project_id=1, mr_iid=1)
            assert isinstance(result, str)
            assert "Test comment with suggestion" in result
            assert "456" in result
            assert "APPLICABLE" in result

    @pytest.mark.asyncio
    async def test_get_merge_request_comments_empty(self):
        """Test that get_merge_request_comments handles no comments."""
        tool_func = mcp._tool_manager._tools["get_merge_request_comments"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_comments"
        ) as mock_get:
            mock_get.return_value = []
            result = await tool_func(project_id=1, mr_iid=1)
            assert "No comments found" in result


class TestGetMergeRequestCommits:
    """Tests for get_merge_request_commits tool."""

    @pytest.mark.asyncio
    async def test_get_merge_request_commits_success(self):
        """Test that get_merge_request_commits returns commit list."""
        tool_func = mcp._tool_manager._tools["get_merge_request_commits"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_commits"
        ) as mock_get:
            mock_get.return_value = [
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
            ]

            result = await tool_func(project_id=1, mr_iid=1)
            assert isinstance(result, str)
            assert "Test commit" in result
            assert "abc123" in result

    @pytest.mark.asyncio
    async def test_get_merge_request_commits_empty(self):
        """Test that get_merge_request_commits handles no commits."""
        tool_func = mcp._tool_manager._tools["get_merge_request_commits"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_merge_request_commits"
        ) as mock_get:
            mock_get.return_value = []
            result = await tool_func(project_id=1, mr_iid=1)
            assert "No commits found" in result


class TestUpdateMergeRequestComment:
    """Tests for update_merge_request_comment tool."""

    @pytest.mark.asyncio
    async def test_update_merge_request_comment_success(self):
        """Test that update_merge_request_comment updates a comment."""
        tool_func = mcp._tool_manager._tools["update_merge_request_comment"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.update_merge_request_comment"
        ) as mock_update:
            mock_update.return_value = {
                "id": 123,
                "body": "Updated comment",
                "author": "testuser",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
            }

            result = await tool_func(
                project_id=1, mr_iid=1, note_id=123, comment="Updated comment"
            )
            assert isinstance(result, str)
            assert "Comment updated successfully" in result
            assert "Updated comment" in result


class TestReplyToMergeRequestComment:
    """Tests for reply_to_merge_request_comment tool."""

    @pytest.mark.asyncio
    async def test_reply_to_merge_request_comment_success(self):
        """Test that reply_to_merge_request_comment adds a reply."""
        tool_func = mcp._tool_manager._tools["reply_to_merge_request_comment"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.reply_to_merge_request_comment"
        ) as mock_reply:
            mock_reply.return_value = {
                "id": 456,
                "body": "Reply comment",
                "discussion_id": "abc123",
                "created_at": "2025-01-01T00:00:00Z",
            }

            result = await tool_func(
                project_id=1, mr_iid=1, discussion_id="abc123", comment="Reply comment"
            )
            assert isinstance(result, str)
            assert "Reply added successfully" in result
            assert "Reply comment" in result


class TestGetIssue:
    """Tests for get_issue tool."""

    @pytest.mark.asyncio
    async def test_get_issue_success(self):
        """Test that get_issue returns issue details."""
        tool_func = mcp._tool_manager._tools["get_issue"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.get_issue"
        ) as mock_get:
            mock_get.return_value = {
                "id": 100,
                "iid": 1,
                "title": "Test Issue",
                "description": "Test description",
                "state": "opened",
                "web_url": "https://gitlab.com/group/project/-/issues/1",
                "author": "testuser",
                "assignees": ["assignee1"],
                "labels": ["bug"],
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "closed_at": None,
            }

            result = await tool_func(project_id=1, issue_iid=1)
            assert isinstance(result, str)
            assert "Test Issue" in result
            assert "Test description" in result


class TestUpdateMergeRequest:
    """Tests for update_merge_request tool."""

    @pytest.mark.asyncio
    async def test_update_merge_request_success(self):
        """Test that update_merge_request updates MR."""
        tool_func = mcp._tool_manager._tools["update_merge_request"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.update_merge_request"
        ) as mock_update:
            mock_update.return_value = {
                "id": 100,
                "iid": 1,
                "title": "Updated Title",
                "description": "Updated description",
                "state": "opened",
                "web_url": "https://gitlab.com/group/project/-/merge_requests/1",
                "updated_at": "2025-01-02T00:00:00Z",
            }

            result = await tool_func(project_id=1, mr_iid=1, title="Updated Title")
            assert isinstance(result, str)
            assert "Merge request updated successfully" in result
            assert "Updated Title" in result

    @pytest.mark.asyncio
    async def test_update_merge_request_no_params(self):
        """Test that update_merge_request requires at least one parameter."""
        tool_func = mcp._tool_manager._tools["update_merge_request"].fn

        result = await tool_func(project_id=1, mr_iid=1)
        assert "Error" in result
        assert "title or description must be provided" in result


class TestApplySuggestion:
    """Tests for apply_suggestion tool."""

    @pytest.mark.asyncio
    async def test_apply_suggestion_success(self):
        """Test that apply_suggestion applies a suggestion."""
        tool_func = mcp._tool_manager._tools["apply_suggestion"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.apply_suggestion"
        ) as mock_apply:
            mock_apply.return_value = {
                "id": 123,
                "applied": True,
                "commit_id": "abc123def456",
            }

            result = await tool_func(suggestion_id=123)
            assert isinstance(result, str)
            assert "Suggestion applied successfully" in result
            assert "123" in result
            assert "abc123def456" in result


class TestApplySuggestions:
    """Tests for apply_suggestions tool."""

    @pytest.mark.asyncio
    async def test_apply_suggestions_success(self):
        """Test that apply_suggestions applies multiple suggestions."""
        tool_func = mcp._tool_manager._tools["apply_suggestions"].fn

        with patch(
            "gitlab_review_mcp.tools.gitlab_tools._service.apply_suggestions"
        ) as mock_apply:
            mock_apply.return_value = {
                "count": 3,
                "applied": True,
                "commit_id": "abc123def456",
                "suggestion_ids": [123, 456, 789],
            }

            result = await tool_func(suggestion_ids=[123, 456, 789])
            assert isinstance(result, str)
            assert "Suggestions applied successfully" in result
            assert "3" in result
            assert "abc123def456" in result
            assert "123" in result
