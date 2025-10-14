"""GitLab MCP tools implementation."""

from typing import Optional

from gitlab_review_mcp.services.gitlab_service import GitLabService
from gitlab_review_mcp.utils.logging import get_logger

logger = get_logger(__name__)

_service = GitLabService()


async def list_projects(
    search: Optional[str] = None,
    owned: bool = False,
    membership: bool = True,
) -> str:
    """
    List available GitLab projects.

    Args:
        search: Optional search string to filter projects by name
        owned: Only return projects owned by the authenticated user
        membership: Only return projects the user is a member of (default: True)

    Returns:
        Formatted string with project list
    """
    try:
        logger.info(
            f"Listing projects - search: {search}, owned: {owned}, membership: {membership}"
        )
        projects = await _service.list_projects(
            search=search, owned=owned, membership=membership
        )

        if not projects:
            return "No projects found."

        result = [f"Found {len(projects)} projects:\n"]
        for project in projects:
            result.append(f"- [{project['id']}] {project['path_with_namespace']}")
            result.append(f"  Name: {project['name']}")
            if project["description"]:
                result.append(f"  Description: {project['description']}")
            result.append(f"  URL: {project['web_url']}")
            if project["default_branch"]:
                result.append(f"  Default branch: {project['default_branch']}")
            result.append("")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return f"Error listing projects: {str(e)}"


async def list_merge_requests(
    project_id: int,
    state: Optional[str] = None,
    author_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    labels: Optional[str] = None,
) -> str:
    """
    List merge requests for a specific project.

    Args:
        project_id: GitLab project ID
        state: Filter by state ('opened', 'closed', 'merged', 'all')
        author_id: Filter by author user ID
        assignee_id: Filter by assignee user ID
        labels: Comma-separated label names (e.g., "bug,urgent")

    Returns:
        Formatted string with merge request list
    """
    try:
        logger.info(f"Listing merge requests for project {project_id}")
        mrs = await _service.list_merge_requests(
            project_id=project_id,
            state=state,
            author_id=author_id,
            assignee_id=assignee_id,
            labels=labels,
        )

        if not mrs:
            return "No merge requests found."

        result = [f"Found {len(mrs)} merge requests:\n"]
        for mr in mrs:
            merged_str = " (merged)" if mr["merged"] else ""
            result.append(f"- !{mr['iid']}: {mr['title']}")
            result.append(f"  State: {mr['state']}{merged_str}")
            result.append(f"  Author: {mr['author']}")
            result.append(f"  Branches: {mr['source_branch']} → {mr['target_branch']}")
            result.append(f"  URL: {mr['web_url']}")
            result.append(f"  Updated: {mr['updated_at']}")
            result.append("")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error listing merge requests: {e}")
        return f"Error listing merge requests: {str(e)}"


async def get_merge_request(project_id: int, mr_iid: int) -> str:
    """
    Fetch merge request details.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID (internal ID shown in GitLab UI as !123)

    Returns:
        Formatted string with MR details
    """
    try:
        logger.info(f"Getting merge request !{mr_iid} from project {project_id}")
        mr = await _service.get_merge_request(project_id, mr_iid)

        result = [
            f"Merge Request !{mr['iid']}: {mr['title']}",
            f"State: {mr['state']}" + (" (merged)" if mr["merged"] else ""),
            f"Author: {mr['author']}",
            f"Source: {mr['source_branch']} → Target: {mr['target_branch']}",
            f"URL: {mr['web_url']}",
            f"Created: {mr['created_at']}",
            f"Updated: {mr['updated_at']}",
            "",
            "Description:",
            mr["description"] if mr["description"] else "(No description)",
        ]

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error getting merge request: {e}")
        return f"Error getting merge request: {str(e)}"


async def get_merge_request_diffs(project_id: int, mr_iid: int) -> str:
    """
    Get merge request diffs showing code changes.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID

    Returns:
        Formatted string with diff information
    """
    try:
        logger.info(f"Getting diffs for MR !{mr_iid} from project {project_id}")
        diffs = await _service.get_merge_request_diffs(project_id, mr_iid)

        if not diffs:
            return "No diffs found."

        result = [f"Diffs for Merge Request !{mr_iid}:\n"]

        for diff_version in diffs:
            result.append(f"Diff ID: {diff_version['id']}")
            result.append(f"Base: {diff_version['base_commit_sha'][:8]}")
            result.append(f"Head: {diff_version['head_commit_sha'][:8]}")
            result.append(f"State: {diff_version['state']}")
            result.append("")

            if diff_version["diffs"]:
                result.append(f"Files changed ({len(diff_version['diffs'])}):")
                for file_diff in diff_version["diffs"]:
                    status = []
                    if file_diff["new_file"]:
                        status.append("NEW")
                    if file_diff["deleted_file"]:
                        status.append("DELETED")
                    if file_diff["renamed_file"]:
                        status.append("RENAMED")

                    status_str = f" [{', '.join(status)}]" if status else ""
                    result.append(f"\n- {file_diff['new_path']}{status_str}")

                    if file_diff["old_path"] != file_diff["new_path"]:
                        result.append(f"  (renamed from {file_diff['old_path']})")

                    if file_diff["diff"]:
                        result.append("  Diff:")
                        result.append(file_diff["diff"])
            result.append("")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error getting merge request diffs: {e}")
        return f"Error getting merge request diffs: {str(e)}"


async def update_merge_request_comment(
    project_id: int, mr_iid: int, note_id: int, comment: str
) -> str:
    """
    Update an existing merge request comment.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID
        note_id: Note ID to update
        comment: Updated comment text

    Returns:
        Confirmation message with updated comment details
    """
    try:
        logger.info(f"Updating comment {note_id} in MR !{mr_iid}")
        result = await _service.update_merge_request_comment(
            project_id, mr_iid, note_id, comment
        )

        return (
            f"Comment updated successfully!\n"
            f"ID: {result['id']}\n"
            f"Author: {result['author']}\n"
            f"Updated: {result['updated_at']}\n"
            f"Body: {result['body']}"
        )

    except Exception as e:
        logger.error(f"Error updating merge request comment: {e}")
        return f"Error updating merge request comment: {str(e)}"


async def reply_to_merge_request_comment(
    project_id: int, mr_iid: int, discussion_id: str, comment: str
) -> str:
    """
    Reply to an existing merge request discussion/comment.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID
        discussion_id: Discussion ID to reply to
        comment: Reply comment text

    Returns:
        Confirmation message with reply details
    """
    try:
        logger.info(f"Replying to discussion {discussion_id} in MR !{mr_iid}")
        result = await _service.reply_to_merge_request_comment(
            project_id, mr_iid, discussion_id, comment
        )

        return (
            f"Reply added successfully!\n"
            f"Note ID: {result['id']}\n"
            f"Discussion ID: {result['discussion_id']}\n"
            f"Created: {result['created_at']}\n"
            f"Body: {result['body']}"
        )

    except Exception as e:
        logger.error(f"Error replying to comment: {e}")
        return f"Error replying to comment: {str(e)}"


async def add_merge_request_comment(project_id: int, mr_iid: int, comment: str) -> str:
    """
    Add a general comment to a merge request.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID
        comment: Comment text to add

    Returns:
        Confirmation message with comment details
    """
    try:
        logger.info(f"Adding comment to MR !{mr_iid} in project {project_id}")
        result = await _service.add_merge_request_comment(project_id, mr_iid, comment)

        return (
            f"Comment added successfully!\n"
            f"ID: {result['id']}\n"
            f"Author: {result['author']}\n"
            f"Created: {result['created_at']}\n"
            f"Body: {result['body']}"
        )

    except Exception as e:
        logger.error(f"Error adding merge request comment: {e}")
        return f"Error adding merge request comment: {str(e)}"


async def add_merge_request_line_comment(
    project_id: int,
    mr_iid: int,
    file_path: str,
    line_number: int,
    comment: str,
    base_sha: str,
    head_sha: str,
    start_sha: str,
    old_line: Optional[int] = None,
) -> str:
    """
    Add a line-specific comment to a merge request diff.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID
        file_path: Path to the file in the repository
        line_number: Line number in the new version of the file
        comment: Comment text to add
        base_sha: Base commit SHA (from diff)
        head_sha: Head commit SHA (from diff)
        start_sha: Start commit SHA (from diff)
        old_line: Line number in the old version (optional, for modified lines)

    Returns:
        Confirmation message with comment details
    """
    try:
        logger.info(f"Adding line comment to MR !{mr_iid} at {file_path}:{line_number}")
        result = await _service.add_merge_request_line_comment(
            project_id=project_id,
            mr_iid=mr_iid,
            file_path=file_path,
            line_number=line_number,
            comment=comment,
            base_sha=base_sha,
            head_sha=head_sha,
            start_sha=start_sha,
            old_line=old_line,
        )

        return (
            f"Line comment added successfully!\n"
            f"Discussion ID: {result['id']}\n"
            f"File: {file_path}\n"
            f"Line: {line_number}\n"
            f"Comment: {result['body']}"
        )

    except Exception as e:
        logger.error(f"Error adding line comment: {e}")
        return f"Error adding line comment: {str(e)}"


async def get_issue(project_id: int, issue_iid: int) -> str:
    """
    Fetch issue details.

    Args:
        project_id: GitLab project ID
        issue_iid: Issue IID (internal ID shown in GitLab UI as #123)

    Returns:
        Formatted string with issue details
    """
    try:
        logger.info(f"Getting issue #{issue_iid} from project {project_id}")
        issue = await _service.get_issue(project_id, issue_iid)

        result = [
            f"Issue #{issue['iid']}: {issue['title']}",
            f"State: {issue['state']}",
            f"Author: {issue['author']}",
            f"URL: {issue['web_url']}",
            f"Created: {issue['created_at']}",
            f"Updated: {issue['updated_at']}",
        ]

        if issue["closed_at"]:
            result.append(f"Closed: {issue['closed_at']}")

        if issue["assignees"]:
            result.append(f"Assignees: {', '.join(issue['assignees'])}")

        if issue["labels"]:
            result.append(f"Labels: {', '.join(issue['labels'])}")

        result.append("")
        result.append("Description:")
        result.append(
            issue["description"] if issue["description"] else "(No description)"
        )

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error getting issue: {e}")
        return f"Error getting issue: {str(e)}"


async def update_merge_request(
    project_id: int,
    mr_iid: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """
    Update merge request title and/or description.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID
        title: New title (optional)
        description: New description (optional)

    Returns:
        Confirmation message with updated MR details
    """
    try:
        if title is None and description is None:
            return "Error: At least one of title or description must be provided."

        logger.info(f"Updating MR !{mr_iid} in project {project_id}")
        result = await _service.update_merge_request(
            project_id=project_id, mr_iid=mr_iid, title=title, description=description
        )

        return (
            f"Merge request updated successfully!\n"
            f"MR !{result['iid']}: {result['title']}\n"
            f"State: {result['state']}\n"
            f"URL: {result['web_url']}\n"
            f"Updated: {result['updated_at']}\n"
            f"\nDescription:\n{result['description']}"
        )

    except Exception as e:
        logger.error(f"Error updating merge request: {e}")
        return f"Error updating merge request: {str(e)}"


async def get_merge_request_comments(project_id: int, mr_iid: int) -> str:
    """
    Get all comments/discussions from a merge request, including suggestions.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID

    Returns:
        Formatted string with all comments, including note_id, discussion_id, and suggestions
    """
    try:
        logger.info(f"Getting comments for MR !{mr_iid} from project {project_id}")
        comments = await _service.get_merge_request_comments(project_id, mr_iid)

        if not comments:
            return "No comments found."

        result = [
            f"Comments in Merge Request !{mr_iid}:\n",
            f"Total comments: {len(comments)}\n",
        ]

        for comment in comments:
            if not comment["system"]:
                status = ""
                if comment["resolvable"]:
                    status = " [RESOLVED]" if comment["resolved"] else " [UNRESOLVED]"

                result.append(f"- Note ID: {comment['note_id']}")
                result.append(f"  Discussion ID: {comment['discussion_id']}")
                result.append(f"  Author: {comment['author']}")
                result.append(f"  Created: {comment['created_at']}")
                if (
                    comment.get("updated_at")
                    and comment["updated_at"] != comment["created_at"]
                ):
                    result.append(f"  Updated: {comment['updated_at']}")
                if comment.get("file_path"):
                    result.append(f"  File: {comment['file_path']}")
                result.append(f"  Status:{status}")
                result.append(f"  Body: {comment['body']}")

                if comment.get("suggestions"):
                    result.append(f"  Suggestions ({len(comment['suggestions'])}):")
                    for suggestion in comment["suggestions"]:
                        applied_status = (
                            "APPLIED"
                            if suggestion["applied"]
                            else (
                                "APPLICABLE"
                                if suggestion["applicable"]
                                else "NOT APPLICABLE"
                            )
                        )
                        result.append(
                            f"    - Suggestion ID: {suggestion['id']} [{applied_status}]"
                        )
                        result.append(
                            f"      Lines: {suggestion['from_line']} - {suggestion['to_line']}"
                        )
                        if suggestion.get("to_content"):
                            result.append(
                                f"      Proposed change:\n{suggestion['to_content']}"
                            )

                result.append("")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error getting merge request comments: {e}")
        return f"Error getting merge request comments: {str(e)}"


async def get_merge_request_commits(project_id: int, mr_iid: int) -> str:
    """
    Get commits in a merge request.

    Args:
        project_id: GitLab project ID
        mr_iid: Merge request IID

    Returns:
        Formatted string with commit list
    """
    try:
        logger.info(f"Getting commits for MR !{mr_iid} from project {project_id}")
        commits = await _service.get_merge_request_commits(project_id, mr_iid)

        if not commits:
            return "No commits found."

        result = [
            f"Commits in Merge Request !{mr_iid}:\n",
            f"Total commits: {len(commits)}\n",
        ]

        for commit in commits:
            result.append(f"- {commit['short_id']}: {commit['title']}")
            result.append(
                f"  Author: {commit['author_name']} <{commit['author_email']}>"
            )
            result.append(f"  Date: {commit['authored_date']}")
            if commit["web_url"]:
                result.append(f"  URL: {commit['web_url']}")
            if commit["message"] != commit["title"]:
                result.append(f"  Message: {commit['message']}")
            result.append("")

        return "\n".join(result)

    except Exception as e:
        logger.error(f"Error getting merge request commits: {e}")
        return f"Error getting merge request commits: {str(e)}"


async def apply_suggestion(suggestion_id: int) -> str:
    """
    Apply a single suggestion to the merge request.

    Args:
        suggestion_id: Suggestion ID to apply

    Returns:
        Confirmation message with apply details
    """
    try:
        logger.info(f"Applying suggestion {suggestion_id}")
        result = await _service.apply_suggestion(suggestion_id)

        return (
            f"Suggestion applied successfully!\n"
            f"Suggestion ID: {result['id']}\n"
            f"Commit ID: {result['commit_id']}\n"
            f"Status: Applied"
        )

    except Exception as e:
        logger.error(f"Error applying suggestion: {e}")
        return f"Error applying suggestion: {str(e)}"


async def apply_suggestions(suggestion_ids: list[int]) -> str:
    """
    Apply multiple suggestions in batch to the merge request.

    Args:
        suggestion_ids: List of suggestion IDs to apply

    Returns:
        Confirmation message with batch apply details
    """
    try:
        logger.info(f"Applying {len(suggestion_ids)} suggestions in batch")
        result = await _service.apply_suggestions(suggestion_ids)

        return (
            f"Suggestions applied successfully!\n"
            f"Count: {result['count']}\n"
            f"Commit ID: {result['commit_id']}\n"
            f"Suggestion IDs: {', '.join(map(str, result['suggestion_ids']))}"
        )

    except Exception as e:
        logger.error(f"Error applying suggestions: {e}")
        return f"Error applying suggestions: {str(e)}"
