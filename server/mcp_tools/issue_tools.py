import requests
import json
from typing import Dict, Union, List, Optional
from ..config import get_gitlab_api, get_gitlab_token, mcp

@mcp.tool()
def list_issues(
    assignee_id: Optional[int] = None,
    assignee_username: Optional[str] = None,
    author_id: Optional[int] = None,
    author_username: Optional[str] = None,
    confidential: Optional[bool] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    due_date: Optional[str] = None,
    iids: Optional[List[int]] = None,
    in_field: Optional[str] = None,
    issue_type: Optional[str] = None,
    labels: Optional[List[str]] = None,
    milestone: Optional[str] = None,
    my_reaction_emoji: Optional[str] = None,
    order_by: Optional[str] = None,
    scope: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    state: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    with_labels_details: Optional[bool] = None
) -> Union[List[Dict], Dict]:
    """
    Get all issues the authenticated user has access to.

    Use this tool whenever the user asks to:
    - List or find issues with specific attributes.
    - Filter issues by assignee, author, labels, milestone, status, or other criteria.

    Parameters:
    - assignee_id (integer, optional): Return issues assigned to the given user ID.
    - assignee_username (string, optional): Return issues assigned to the given username.
    - author_id (integer, optional): Return issues created by the given user ID.
    - author_username (string, optional): Return issues created by the given username.
    - confidential (boolean, optional): Filter for confidential or public issues.
    - created_after (string, optional): Return issues created on or after the given time (ISO 8601 format).
    - created_before (string, optional): Return issues created on or before the given time (ISO 8601 format).
    - due_date (string, optional): Filter by due date ('0', 'any', 'today', 'overdue', etc.).
    - iids (list of integers, optional): Return only issues with the given IIDs.
    - in_field (string, optional): Scope for the search attribute ('title', 'description').
    - issue_type (string, optional): Filter by issue type ('issue', 'incident', 'test_case', 'task').
    - labels (list of strings, optional): Comma-separated list of label names.
    - milestone (string, optional): The milestone title.
    - my_reaction_emoji (string, optional): Filter by emoji reaction from the authenticated user.
    - order_by (string, optional): Order results by a specific field (e.g., 'created_at', 'updated_at').
    - scope (string, optional): Scope of issues to return ('created_by_me', 'assigned_to_me', 'all').
    - search (string, optional): Search for issues by title and description.
    - sort (string, optional): Sort order ('asc' or 'desc').
    - state (string, optional): Filter by state ('opened', 'closed').
    - updated_after (string, optional): Return issues updated on or after the given time (ISO 8601 format).
    - updated_before (string, optional): Return issues updated on or before the given time (ISO 8601 format).
    - with_labels_details (boolean, optional): If true, returns more details for each label.

    Returns:
    - A list of dictionaries representing the issues on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/issues"
    print(f"\n[GITLAB ISSUES] Listing issues.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    params = {}
    if assignee_id is not None:
        params['assignee_id'] = assignee_id
    if assignee_username is not None:
        params['assignee_username'] = assignee_username
    if author_id is not None:
        params['author_id'] = author_id
    if author_username is not None:
        params['author_username'] = author_username
    if confidential is not None:
        params['confidential'] = confidential
    if created_after:
        params['created_after'] = created_after
    if created_before:
        params['created_before'] = created_before
    if due_date:
        params['due_date'] = due_date
    if iids:
        params['iids[]'] = iids
    if in_field:
        params['in'] = in_field
    if issue_type:
        params['issue_type'] = issue_type
    if labels:
        params['labels'] = ','.join(labels)
    if milestone:
        params['milestone'] = milestone
    if my_reaction_emoji:
        params['my_reaction_emoji'] = my_reaction_emoji
    if order_by:
        params['order_by'] = order_by
    if scope:
        params['scope'] = scope
    if search:
        params['search'] = search
    if sort:
        params['sort'] = sort
    if state:
        params['state'] = state
    if updated_after:
        params['updated_after'] = updated_after
    if updated_before:
        params['updated_before'] = updated_before
    if with_labels_details:
        params['with_labels_details'] = with_labels_details

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()

        print("[GITLAB ISSUES] Successfully retrieved issues.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error listing issues: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_project_issues(
    project_id: Union[int, str],
    assignee_id: Optional[int] = None,
    assignee_username: Optional[List[str]] = None,
    author_id: Optional[int] = None,
    author_username: Optional[str] = None,
    confidential: Optional[bool] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    due_date: Optional[str] = None,
    iids: Optional[List[int]] = None,
    issue_type: Optional[str] = None,
    labels: Optional[List[str]] = None,
    milestone: Optional[str] = None,
    my_reaction_emoji: Optional[str] = None,
    order_by: Optional[str] = None,
    scope: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    state: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    with_labels_details: Optional[bool] = None,
    cursor: Optional[str] = None
) -> Union[List[Dict], Dict]:
    """
    Get a list of a project’s issues.

    Use this tool whenever the user asks to:
    - List or find issues within a specific project.
    - Filter project issues by assignee, author, labels, milestone, status, or other criteria.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - assignee_id (integer, optional): Return issues assigned to the given user ID.
    - assignee_username (list of strings, optional): Return issues assigned to the given usernames.
    - author_id (integer, optional): Return issues created by the given user ID.
    - author_username (string, optional): Return issues created by the given username.
    - confidential (boolean, optional): Filter for confidential or public issues.
    - created_after (string, optional): Return issues created on or after the given time (ISO 8601 format).
    - created_before (string, optional): Return issues created on or before the given time (ISO 8601 format).
    - due_date (string, optional): Filter by due date ('0', 'any', 'today', 'overdue', etc.).
    - iids (list of integers, optional): Return only issues with the given IIDs.
    - issue_type (string, optional): Filter by issue type ('issue', 'incident', 'test_case', 'task').
    - labels (list of strings, optional): Comma-separated list of label names.
    - milestone (string, optional): The milestone title.
    - my_reaction_emoji (string, optional): Filter by emoji reaction from the authenticated user.
    - order_by (string, optional): Order results by a specific field (e.g., 'created_at', 'updated_at').
    - scope (string, optional): Scope of issues to return ('created_by_me', 'assigned_to_me', 'all').
    - search (string, optional): Search for issues by title and description.
    - sort (string, optional): Sort order ('asc' or 'desc').
    - state (string, optional): Filter by state ('opened', 'closed').
    - updated_after (string, optional): Return issues updated on or after the given time (ISO 8601 format).
    - updated_before (string, optional): Return issues updated on or before the given time (ISO 8601 format).
    - with_labels_details (boolean, optional): If true, returns more details for each label.
    - cursor (string, optional): The pagination cursor.

    Returns:
    - A list of dictionaries representing the project's issues on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues"
    print(f"\n[GITLAB PROJECT ISSUES] Listing issues for project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    params = {}
    if assignee_id is not None:
        params['assignee_id'] = assignee_id
    if assignee_username:
        params['assignee_username[]'] = assignee_username
    if author_id is not None:
        params['author_id'] = author_id
    if author_username:
        params['author_username'] = author_username
    if confidential is not None:
        params['confidential'] = confidential
    if created_after:
        params['created_after'] = created_after
    if created_before:
        params['created_before'] = created_before
    if due_date:
        params['due_date'] = due_date
    if iids:
        params['iids[]'] = iids
    if issue_type:
        params['issue_type'] = issue_type
    if labels:
        params['labels'] = ','.join(labels)
    if milestone:
        params['milestone'] = milestone
    if my_reaction_emoji:
        params['my_reaction_emoji'] = my_reaction_emoji
    if order_by:
        params['order_by'] = order_by
    if scope:
        params['scope'] = scope
    if search:
        params['search'] = search
    if sort:
        params['sort'] = sort
    if state:
        params['state'] = state
    if updated_after:
        params['updated_after'] = updated_after
    if updated_before:
        params['updated_before'] = updated_before
    if with_labels_details:
        params['with_labels_details'] = with_labels_details
    if cursor:
        params['cursor'] = cursor
        
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()

        print(f"[GITLAB PROJECT ISSUES] Successfully retrieved issues for project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB PROJECT ISSUES] Error listing issues for project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB PROJECT ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_single_issue(issue_id: int) -> Union[Dict, Dict]:
    """
    Get a single issue. Note: This is only for administrators.

    Use this tool whenever the user asks to:
    - Get a single issue by its ID.
    - View the details of a specific issue.

    Parameters:
    - issue_id (integer): The ID of the issue to retrieve.

    Returns:
    - A dictionary representing the issue on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/issues/{issue_id}"
    print(f"\n[GITLAB ISSUES] Retrieving issue with ID {issue_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved issue {issue_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error retrieving issue {issue_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_new_issue(
    project_id: Union[int, str],
    title: str,
    assignee_id: Optional[int] = None,
    assignee_ids: Optional[List[int]] = None,
    confidential: Optional[bool] = None,
    created_at: Optional[str] = None,
    description: Optional[str] = None,
    discussion_to_resolve: Optional[str] = None,
    due_date: Optional[str] = None,
    epic_id: Optional[int] = None,
    iid: Optional[Union[int, str]] = None,
    issue_type: Optional[str] = None,
    labels: Optional[List[str]] = None,
    merge_request_to_resolve_discussions_of: Optional[int] = None,
    milestone_id: Optional[int] = None,
    weight: Optional[int] = None
) -> Union[Dict, Dict]:
    """
    Creates a new project issue.

    Use this tool whenever the user asks to:
    - Create a new issue in a project.
    - Open a bug report, feature request, or task.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - title (string): The title of the issue.
    - assignee_id (integer, optional): The ID of the user to assign the issue to.
    - assignee_ids (list of integers, optional): The IDs of users to assign the issue to.
    - confidential (boolean, optional): Set the issue to be confidential.
    - created_at (string, optional): The creation date of the issue (ISO 8601 format). Requires admin/owner rights.
    - description (string, optional): The description of the issue.
    - discussion_to_resolve (string, optional): The ID of a discussion to resolve.
    - due_date (string, optional): The due date in 'YYYY-MM-DD' format.
    - epic_id (integer, optional): ID of the epic to add the issue to.
    - iid (integer or string, optional): The internal ID of the issue. Requires admin/owner rights.
    - issue_type (string, optional): The type of issue ('issue', 'incident', 'test_case', 'task').
    - labels (list of strings, optional): List of label names to assign to the issue.
    - merge_request_to_resolve_discussions_of (integer, optional): The IID of a merge request to resolve discussions in.
    - milestone_id (integer, optional): The global ID of a milestone to assign to the issue.
    - weight (integer, optional): The weight of the issue.

    Returns:
    - A dictionary representing the newly created issue on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues"
    print(f"\n[GITLAB ISSUES Creating a new issue in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    data = {
        'title': title
    }

    if assignee_id is not None:
        data['assignee_id'] = assignee_id
    if assignee_ids:
        data['assignee_ids'] = assignee_ids
    if confidential is not None:
        data['confidential'] = confidential
    if created_at:
        data['created_at'] = created_at
    if description:
        data['description'] = description
    if discussion_to_resolve:
        data['discussion_to_resolve'] = discussion_to_resolve
    if due_date:
        data['due_date'] = due_date
    if epic_id is not None:
        data['epic_id'] = epic_id
    if iid is not None:
        data['iid'] = iid
    if issue_type:
        data['issue_type'] = issue_type
    if labels:
        data['labels'] = ','.join(labels)
    if merge_request_to_resolve_discussions_of is not None:
        data['merge_request_to_resolve_discussions_of'] = merge_request_to_resolve_discussions_of
    if milestone_id is not None:
        data['milestone_id'] = milestone_id
    if weight is not None:
        data['weight'] = weight

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        print(f"[GITLAB ISSUES Successfully created issue in project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error creating issue in project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def edit_issue(
    project_id: Union[int, str],
    issue_iid: int,
    add_labels: Optional[str] = None,
    assignee_ids: Optional[List[int]] = None,
    confidential: Optional[bool] = None,
    description: Optional[str] = None,
    discussion_locked: Optional[bool] = None,
    due_date: Optional[str] = None,
    epic_id: Optional[int] = None,
    issue_type: Optional[str] = None,
    labels: Optional[str] = None,
    milestone_id: Optional[int] = None,
    remove_labels: Optional[str] = None,
    state_event: Optional[str] = None,
    title: Optional[str] = None,
    updated_at: Optional[str] = None,
    weight: Optional[int] = None
) -> Union[Dict, Dict]:
    """
    Updates an existing project issue. This can be used to edit, close, or reopen an issue.

    Use this tool whenever the user asks to:
    - Update or modify an existing issue in a project.
    - Close or reopen an issue.
    - Change an issue's labels, assignee, milestone, or other attributes.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.
    - add_labels (string, optional): Comma-separated label names to add to the issue.
    - assignee_ids (list of integers, optional): The IDs of users to assign the issue to. Set to [] or [0] to unassign.
    - confidential (boolean, optional): Updates the confidentiality of the issue.
    - description (string, optional): The new description of the issue.
    - discussion_locked (boolean, optional): Lock or unlock the issue's discussion.
    - due_date (string, optional): The new due date in 'YYYY-MM-DD' format.
    - epic_id (integer, optional): The ID of the epic to associate the issue with.
    - issue_type (string, optional): Updates the type of issue ('issue', 'incident', 'test_case', 'task').
    - labels (string, optional): Comma-separated list of label names to set for the issue.
    - milestone_id (integer, optional): The global ID of the milestone to assign. Set to 0 to unassign.
    - remove_labels (string, optional): Comma-separated label names to remove from the issue.
    - state_event (string, optional): Event to change the issue state ('close' or 'reopen').
    - title (string, optional): The new title of the issue.
    - updated_at (string, optional): Sets the update time (ISO 8601 format). Requires admin/owner rights.
    - weight (integer, optional): The new weight of the issue.

    Returns:
    - A dictionary representing the updated issue on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}"
    print(f"\n[GITLAB ISSUES] Editing issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    data = {}
    if add_labels is not None:
        data['add_labels'] = add_labels
    if assignee_ids is not None:
        data['assignee_ids'] = assignee_ids
    if confidential is not None:
        data['confidential'] = confidential
    if description is not None:
        data['description'] = description
    if discussion_locked is not None:
        data['discussion_locked'] = discussion_locked
    if due_date is not None:
        data['due_date'] = due_date
    if epic_id is not None:
        data['epic_id'] = epic_id
    if issue_type is not None:
        data['issue_type'] = issue_type
    if labels is not None:
        data['labels'] = labels
    if milestone_id is not None:
        data['milestone_id'] = milestone_id
    if remove_labels is not None:
        data['remove_labels'] = remove_labels
    if state_event is not None:
        data['state_event'] = state_event
    if title is not None:
        data['title'] = title
    if updated_at is not None:
        data['updated_at'] = updated_at
    if weight is not None:
        data['weight'] = weight

    if not data:
        return {"error": "At least one parameter to update is required."}

    try:
        response = requests.put(api_url, headers=headers, json=data)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully edited issue {issue_iid} in project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error editing issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Optional[Dict]:
    """
    Deletes an issue. Note: This is only for administrators and project owners.

    Use this tool whenever the user asks to:
    - Delete or remove an issue from a project.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A success dictionary if the deletion is successful.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}"
    print(f"\n[GITLAB ISSUES] Deleting issue {issue_iid} from project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status()

        # A 204 No Content response indicates success
        print(f"[GITLAB ISSUES] Successfully deleted issue {issue_iid} from project {project_id}.")
        return {"status": "success", "message": f"Issue {issue_iid} deleted successfully."}

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error deleting issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Handle cases where there's no JSON body, like 404 Not Found
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def reorder_issue(
    project_id: Union[int, str],
    issue_iid: int,
    move_after_id: Optional[int] = None,
    move_before_id: Optional[int] = None
) -> Union[Dict, Dict]:
    """
    Reorders an issue in a project's manual sort order.

    Use this tool whenever the user asks to:
    - Change the manual order of an issue within a project.
    - Move an issue before or after another issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue to be reordered.
    - move_after_id (integer, optional): The global ID of the issue to move this issue after.
    - move_before_id (integer, optional): The global ID of the issue to move this issue before.

    Returns:
    - A dictionary representing the updated issue on success.
    - An error dictionary if the request fails.
    """
    if move_after_id is None and move_before_id is None:
        return {"error": "At least one of 'move_after_id' or 'move_before_id' is required."}

    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/reorder"
    print(f"\n[GITLAB ISSUES] Reordering issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    params = {}
    if move_after_id is not None:
        params['move_after_id'] = move_after_id
    if move_before_id is not None:
        params['move_before_id'] = move_before_id

    try:
        response = requests.put(api_url, headers=headers, params=params)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully reordered issue {issue_iid} in project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error reordering issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def move_issue(
    project_id: Union[int, str],
    issue_iid: int,
    to_project_id: int
) -> Union[Dict, Dict]:
    """
    Moves an issue to a different project.

    Use this tool whenever the user asks to:
    - Move an issue from one project to another.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the source project.
    - issue_iid (integer): The internal ID of the issue to move.
    - to_project_id (integer): The ID of the project to move the issue to.

    Returns:
    - A dictionary representing the moved issue in its new project on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/move"
    print(f"\n[GITLAB ISSUES] Moving issue {issue_iid} from project {project_id} to project {to_project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # This endpoint expects form data, not a JSON payload
    data = {
        'to_project_id': to_project_id
    }

    try:
        response = requests.post(api_url, headers=headers, data=data)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully moved issue {issue_iid} to project {to_project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error moving issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def clone_issue(
    project_id: Union[int, str],
    issue_iid: int,
    to_project_id: int,
    with_notes: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Clones an issue to a different project.

    Use this tool whenever the user asks to:
    - Clone or copy an issue to another project.
    - Duplicate an issue, optionally including its notes.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the source project.
    - issue_iid (integer): The internal ID of the issue to clone.
    - to_project_id (integer): The ID of the project to clone the issue to.
    - with_notes (boolean, optional): If true, clones the issue with its notes. Defaults to false.

    Returns:
    - A dictionary representing the newly cloned issue on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/clone"
    print(f"\n[GITLAB ISSUES] Cloning issue {issue_iid} from project {project_id} to project {to_project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # This endpoint expects parameters in the URL query string for a POST request
    params = {
        'to_project_id': to_project_id
    }
    if with_notes is not None:
        params['with_notes'] = with_notes

    try:
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully cloned issue {issue_iid} to project {to_project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error cloning issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def subscribe_to_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Subscribes the authenticated user to an issue to receive notifications.

    Use this tool whenever the user asks to:
    - Subscribe to an issue.
    - Start receiving notifications for an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary representing the issue on successful subscription.
    - A specific message if already subscribed.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/subscribe"
    print(f"\n[GITLAB ISSUES Subscribing to issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.post(api_url, headers=headers)
        
        # A 304 Not Modified response means the user is already subscribed
        if response.status_code == 304:
            print(f"[GITLAB ISSUES] Already subscribed to issue {issue_iid}.")
            return {"status": "not_modified", "message": f"Already subscribed to issue {issue_iid}."}
        
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully subscribed to issue {issue_iid} in project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error subscribing to issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def unsubscribe_from_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Unsubscribes the authenticated user from an issue.

    Use this tool whenever the user asks to:
    - Unsubscribe from an issue.
    - Stop receiving notifications for an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary representing the issue on successful unsubscription.
    - A specific message if not subscribed.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/unsubscribe"
    print(f"\n[GITLAB ISSUES] Unsubscribing from issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.post(api_url, headers=headers)

        # A 304 Not Modified response means the user was not subscribed
        if response.status_code == 304:
            print(f"[GITLAB ISSUES] Not subscribed to issue {issue_iid}.")
            return {"status": "not_modified", "message": f"You were not subscribed to issue {issue_iid}."}
        
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully unsubscribed from issue {issue_iid} in project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error unsubscribing from issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_todo_on_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Manually creates a to-do item for the current user on an issue.

    Use this tool whenever the user asks to:
    - Add an issue to their to-do list.
    - Create a to-do item for a specific issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary representing the newly created to-do item on success.
    - A specific message if a to-do item already exists.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/todo"
    print(f"\n[GITLAB ISSUES] Creating a to-do item for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.post(api_url, headers=headers)

        # A 304 Not Modified response means a to-do item already exists
        if response.status_code == 304:
            print(f"[GITLAB ISSUES] To-do item already exists for issue {issue_iid}.")
            return {"status": "not_modified", "message": f"A to-do item already exists for you on issue {issue_iid}."}
        
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully created to-do item for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error creating to-do item for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def promote_issue_to_epic(
    project_id: Union[int, str],
    issue_iid: int,
    comment: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Promotes an issue to an epic (Premium/Ultimate feature).

    Use this tool whenever the user asks to:
    - Promote an issue to an epic.
    - Convert an issue into an epic.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.
    - comment (string, optional): A comment to add to the issue along with the promotion. If not provided, the issue is promoted without an accompanying comment.

    Returns:
    - A dictionary representing the note created during the promotion on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/notes"
    print(f"\n[GITLAB ISSUES] Promoting issue {issue_iid} in project {project_id} to an epic.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # Construct the note body with the /promote quick action
    if comment:
        note_body = f"{comment}\n\n/promote"
    else:
        note_body = "/promote"

    params = {
        'body': note_body
    }

    try:
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully promoted issue {issue_iid} to an epic.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error promoting issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            # Check for specific error message if the feature is unavailable
            if "not available" in str(error_details).lower():
                 print("This feature may not be available for your GitLab tier (Requires Premium/Ultimate).")
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def set_issue_time_estimate(
    project_id: Union[int, str],
    issue_iid: int,
    duration: str
) -> Union[Dict, Dict]:
    """
    Sets an estimated time of work for an issue.

    Use this tool whenever the user asks to:
    - Set or update the time estimate for an issue.
    - Add an estimated time of work to an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.
    - duration (string): The duration in human-readable format (e.g., '3h30m').

    Returns:
    - A dictionary containing the updated time tracking statistics on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/time_estimate"
    print(f"\n[GITLAB ISSUES] Setting time estimate for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    params = {
        'duration': duration
    }

    try:
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully set time estimate for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error setting time estimate for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def reset_issue_time_estimate(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Resets the estimated time for an issue to 0.

    Use this tool whenever the user asks to:
    - Reset or clear the time estimate for an issue.
    - Remove the estimated time of work from an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary containing the updated time tracking statistics on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/reset_time_estimate"
    print(f"\n[GITLAB ISSUES] Resetting time estimate for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully reset time estimate for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error resetting time estimate for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def add_spent_time_for_issue(
    project_id: Union[int, str],
    issue_iid: int,
    duration: str,
    summary: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Adds spent time for an issue.

    Use this tool whenever the user asks to:
    - Add or log spent time for an issue.
    - Record time worked on a specific issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.
    - duration (string): The duration in human-readable format (e.g., '3h30m').
    - summary (string, optional): A summary of how the time was spent.

    Returns:
    - A dictionary containing the updated time tracking statistics on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/add_spent_time"
    print(f"\n[GITLAB ISSUES] Adding spent time for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    params = {
        'duration': duration
    }
    if summary:
        params['summary'] = summary

    try:
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully added spent time for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error adding spent time for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def reset_spent_time_for_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Resets the total spent time for an issue to 0.

    Use this tool whenever the user asks to:
    - Reset or clear the spent time for an issue.
    - Remove the logged time from an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary containing the updated time tracking statistics on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/reset_spent_time"
    print(f"\n[GITLAB ISSUES] Resetting spent time for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully reset spent time for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error resetting spent time for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_issue_time_tracking_stats(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Gets time tracking stats for an issue.

    Use this tool whenever the user asks to:
    - Get the time tracking statistics for an issue.
    - See the estimated and spent time on an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary containing the time tracking statistics on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/time_stats"
    print(f"\n[GITLAB ISSUES] Getting time tracking stats for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved time tracking stats for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error getting time tracking stats for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_related_merge_requests_for_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[List[Dict], Dict]:
    """
    Gets all the merge requests that are related to an issue.

    Use this tool whenever the user asks to:
    - List all merge requests linked to a specific issue.
    - Find merge requests that close or mention an issue.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A list of dictionaries representing the related merge requests on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/related_merge_requests"
    print(f"\n[GITLAB ISSUES] Listing merge requests related to issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved merge requests related to issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error listing related merge requests for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_merge_requests_closing_issue(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[List[Dict], Dict]:
    """
    Gets all merge requests that close a particular issue when merged.

    Use this tool whenever the user asks to:
    - List merge requests that will close a specific issue.
    - Find the merge requests that are set to resolve an issue upon merging.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A list of dictionaries representing the merge requests on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/closed_by"
    print(f"\n[GITLAB ISSUES] Listing MRs that close issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved MRs that close issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error listing MRs closing issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_issue_participants(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[List[Dict], Dict]:
    """
    Lists users that are participants in an issue.

    Use this tool whenever the user asks to:
    - List the participants of an issue.
    - See who is involved in an issue's discussion.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A list of dictionaries representing the issue participants on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/participants"
    print(f"\n[GITLAB ISSUES Listing participants for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved participants for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error listing participants for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_issue_user_agent_details(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[Dict, Dict]:
    """
    Gets the user agent and IP details of the issue creator. Note: This is only for administrators.

    Use this tool whenever the user asks to:
    - Get user agent and IP details for an issue's author.
    - Track the origin of an issue for spam prevention.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A dictionary containing the user agent details on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/user_agent_detail"
    print(f"\n[GITLAB ISSUES Getting user agent details for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved user agent details for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error getting user agent details for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_issue_state_events(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[List[Dict], Dict]:
    """
    Lists all state changes for a given issue.

    Use this tool whenever the user asks to:
    - Track the state history of an issue.
    - See who changed an issue's state and when.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the project's issue.

    Returns:
    - A list of dictionaries representing the state events on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/resource_state_events"
    print(f"\n[GITLAB ISSUES] Listing state events for issue {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB ISSUES] Successfully retrieved state events for issue {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB ISSUES] Error listing state events for issue {issue_iid}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def upload_incident_metric_image(
    project_id: Union[int, str],
    issue_iid: int,
    file_path: str,
    url: Optional[str] = None,
    url_text: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Uploads a metric image to an incident.

    Use this tool whenever the user asks to:
    - Upload a metric image or screenshot to an incident.
    - Add a chart to an incident's Metrics tab.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the incident.
    - file_path (string): The local path to the image file to be uploaded.
    - url (string, optional): A URL to associate with the image.
    - url_text (string, optional): A description for the image or URL.

    Returns:
    - A dictionary representing the uploaded metric image on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/metric_images"
    print(f"\n[GITLAB INCIDENTS Uploading metric image to incident {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    data = {}
    if url:
        data['url'] = url
    if url_text:
        data['url_text'] = url_text

    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(api_url, headers=headers, data=data, files=files)
            response.raise_for_status()

        print(f"[GITLAB INCIDENTS] Successfully uploaded metric image to incident {issue_iid}.")
        return response.json()
        
    except FileNotFoundError:
        print(f"[GITLAB INCIDENTS] Error: File not found at path: {file_path}")
        return {"error": f"File not found at path: {file_path}"}
    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB INCIDENTS] Error uploading metric image: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB INCIDENTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_incident_metric_images(
    project_id: Union[int, str],
    issue_iid: int
) -> Union[List[Dict], Dict]:
    """
    Lists all metric images for an incident.

    Use this tool whenever the user asks to:
    - List or view all metric images associated with an incident.
    - See the charts in an incident's Metrics tab.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the incident.

    Returns:
    - A list of dictionaries representing the metric images on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/metric_images"
    print(f"\n[GITLAB INCIDENTS] Listing metric images for incident {issue_iid} in project {project_id}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB INCIDENTS] Successfully retrieved metric images for incident {issue_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB INCIDENTS] Error listing metric images: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB INCIDENTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_incident_metric_image(
    project_id: Union[int, str],
    issue_iid: int,
    image_id: int,
    url: Optional[str] = None,
    url_text: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Updates the attributes of a metric image for an incident.

    Use this tool whenever the user asks to:
    - Edit or update the details of a metric image in an incident.
    - Change the URL or description of an incident's metric image.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the incident.
    - image_id (integer): The ID of the metric image to update.
    - url (string, optional): The new URL to associate with the image.
    - url_text (string, optional): The new description for the image or URL.

    Returns:
    - A dictionary representing the updated metric image on success.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/metric_images/{image_id}"
    print(f"\n[GITLAB INCIDENTS] Updating metric image {image_id} for incident {issue_iid}.")

    if url is None and url_text is None:
        return {"error": "At least one of 'url' or 'url_text' is required to update."}

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    data = {}
    if url:
        data['url'] = url
    if url_text:
        data['url_text'] = url_text

    try:
        response = requests.put(api_url, headers=headers, data=data)
        response.raise_for_status()

        print(f"[GITLAB INCIDENTS] Successfully updated metric image {image_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB INCIDENTS] Error updating metric image {image_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB INCIDENTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_incident_metric_image(
    project_id: Union[int, str],
    issue_iid: int,
    image_id: int
) -> Optional[Dict]:
    """
    Deletes a metric image from an incident.

    Use this tool whenever the user asks to:
    - Delete or remove a metric image from an incident.
    - Remove a chart from an incident's Metrics tab.

    Parameters:
    - project_id (int or string): The ID or URL-encoded path of the project.
    - issue_iid (integer): The internal ID of the incident.
    - image_id (integer): The ID of the metric image to delete.

    Returns:
    - A success dictionary if the deletion is successful.
    - An error dictionary if the request fails.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/issues/{issue_iid}/metric_images/{image_id}"
    print(f"\n[GITLAB INCIDENTS Deleting metric image {image_id} from incident {issue_iid}.")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status()

        print(f"[GITLAB INCIDENTS] Successfully deleted metric image {image_id}.")
        return {"status": "success", "message": f"Metric image {image_id} deleted successfully."}

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB INCIDENTS] Error deleting metric image {image_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB INCIDENTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}