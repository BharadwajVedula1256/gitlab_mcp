import requests
import json
from typing import Dict, Union, Optional, List
from ..config import get_gitlab_api, get_gitlab_token, mcp

@mcp.tool()
def approve_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int,
    approval_password: Optional[str] = None,
    sha: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Approve merge request
    Approves the specified merge request using:
        POST /projects/:id/merge_requests/:merge_request_iid/approve

    The currently authenticated user must be an eligible approver. This action 
    creates an approval record for the merge request.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)
        approval_password (Optional[str]): Current user’s password. Required if 
                                           'Require user re-authentication to approve' is 
                                           enabled in project settings.
        sha (Optional[str]): The HEAD commit SHA of the merge request. If provided, 
                             it must match the current HEAD to prevent approving an 
                             outdated version (otherwise returns 409 Conflict).

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the updated merge request 
              object, including the current approval status. Attributes include:
                - id (integer): ID of the merge request.
                - iid (integer): Internal ID of the merge request.
                - title (string): Title of the merge request.
                - state (string): State of the merge request.
                - merge_status (string): Merge status of the merge request.
                - approvals_required (integer): Total approvals required.
                - approvals_left (integer): Approvals remaining.
                - approved_by (array): List of users who have approved the MR.
                - web_url (string): Web URL of the merge request.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx, including 409 Conflict).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approve"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {}

    if approval_password is not None:
        payload['approval_password'] = approval_password
    if sha is not None:
        payload['sha'] = sha

    print(f"\n[APPROVE MR] Attempting to approve merge request !{merge_request_iid} in project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (201 Created)
        print(f"[APPROVE MR] Successfully approved merge request !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[APPROVE MR] Error approving merge request: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[APPROVE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def reset_gitlab_merge_request_approvals(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Reset approvals for a merge request
    Resets all approvals for a specified merge request using:
        PUT /projects/:id/merge_requests/:merge_request_iid/reset_approvals

    This tool deletes all existing approval records for a merge request. This functionality
    is typically restricted to bot users with project or group tokens; human users will
    receive a 401 Unauthorized response.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the updated merge request 
              object, with the 'approved_by' list emptied and 'approvals_left' reset 
              to the required number. Attributes are the same as for the Merge Request API.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx, including 401 Unauthorized).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/reset_approvals"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[RESET MR APPROVALS] Attempting to reset approvals for merge request !{merge_request_iid} in project {project_id}.")
    
    try:
        # 3. Make the PUT request (empty body is fine)
        # Note: PUT is used as specified in the API documentation
        response = requests.put(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content (200 OK)
        print(f"[RESET MR APPROVALS] Successfully reset approvals for merge request !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[RESET MR APPROVALS] Error resetting approvals: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[RESET MR APPROVALS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_approval_configuration(
    project_id: Union[int, str]
) -> Union[Dict, Dict]:
    """
    Retrieve approval configuration for a project
    Retrieves the approval configuration for a project using:
        GET /projects/:id/approvals

    This function fetches the current project-level settings for merge request 
    approvals, including rules for push resets, author/committer approvals, 
    and re-authentication requirements.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the approval configuration. 
              Key attributes include:
                - reset_approvals_on_push (boolean): If true, approvals are reset on push.
                - disable_overriding_approvers_per_merge_request (boolean): If true, prevents MR approver overrides.
                - merge_requests_author_approval (boolean): If true, authors can self-approve.
                - merge_requests_disable_committers_approval (boolean): If true, committers cannot approve.
                - require_reauthentication_to_approve (boolean): If true, requires re-authentication to approve.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approvals"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET APPROVAL CONFIG] Attempting to retrieve approval configuration for project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET APPROVAL CONFIG] Successfully retrieved approval configuration.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET APPROVAL CONFIG] Error retrieving approval configuration: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET APPROVAL CONFIG] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_gitlab_approval_configuration(
    project_id: Union[int, str],
    approvals_before_merge: Optional[int] = None,
    disable_overriding_approvers_per_merge_request: Optional[bool] = None,
    merge_requests_author_approval: Optional[bool] = None,
    merge_requests_disable_committers_approval: Optional[bool] = None,
    require_password_to_approve: Optional[bool] = None,
    require_reauthentication_to_approve: Optional[bool] = None,
    reset_approvals_on_push: Optional[bool] = None,
    selective_code_owner_removals: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Update approval configuration for a project
    Updates the approval configuration for a project using:
        POST /projects/:id/approvals

    The currently authenticated user must be an eligible approver. This function 
    allows modification of project-level merge request approval settings.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        approvals_before_merge (Optional[int]): The number of required approvals. 
                                                (Deprecated in GitLab 12.3; use Approval Rules instead).
        disable_overriding_approvers_per_merge_request (Optional[bool]): If true, prevents 
                                                                        overrides of approvers in an MR.
        merge_requests_author_approval (Optional[bool]): If true, authors can self-approve their MRs.
        merge_requests_disable_committers_approval (Optional[bool]): If true, users who commit 
                                                                     on an MR cannot approve it.
        require_password_to_approve (Optional[bool]): If true, requires password to approve. 
                                                      (Deprecated in GitLab 16.9; use require_reauthentication_to_approve instead).
        require_reauthentication_to_approve (Optional[bool]): If true, requires approver to 
                                                              authenticate before adding approval.
        reset_approvals_on_push (Optional[bool]): If true, approvals are reset on push.
        selective_code_owner_removals (Optional[bool]): If true, resets approvals from 
                                                        Code Owners if their files change. 
                                                        Requires reset_approvals_on_push=False.

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the updated approval configuration.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approvals"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    # Collect all non-None arguments into the payload
    payload = {
        k: v for k, v in locals().items() 
        if k in [
            'approvals_before_merge',
            'disable_overriding_approvers_per_merge_request',
            'merge_requests_author_approval',
            'merge_requests_disable_committers_approval',
            'require_password_to_approve',
            'require_reauthentication_to_approve',
            'reset_approvals_on_push',
            'selective_code_owner_removals'
        ] and v is not None
    }
    
    if not payload:
        return {"warning": "No update parameters provided.", "details": "The API call was skipped because no optional parameters were set."}

    print(f"\n[UPDATE APPROVAL CONFIG] Attempting to update approval configuration for project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[UPDATE APPROVAL CONFIG] Successfully updated approval configuration.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[UPDATE APPROVAL CONFIG] Error updating approval configuration: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[UPDATE APPROVAL CONFIG] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_project_approval_rules(
    project_id: Union[int, str],
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List all approval rules for a project
    Lists all approval rules and any associated details for a specified project using:
        GET /projects/:id/approval_rules

    This tool retrieves the list of configured project-level approval rules, which define 
    the requirements for merging a merge request, including required approver counts, 
    users, and groups.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        per_page (Optional[int]): Number of results per page for pagination.
        page (Optional[int]): Page number of results for pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of approval rule objects (dictionaries). Key attributes include:
                - id (integer): ID of the approval rule.
                - name (string): Name of the rule (e.g., 'security', 'Code-Owner').
                - rule_type (string): Type of rule ('regular', 'report_approver').
                - approvals_required (integer): The number of approvals required for this rule.
                - users (array): List of user objects directly assigned to the rule.
                - groups (array): List of group objects assigned to the rule.
                - protected_branches (array): List of protected branches the rule applies to.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approval_rules"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if per_page is not None:
        params['per_page'] = per_page
    if page is not None:
        params['page'] = page

    print(f"\n[LIST APPROVAL RULES] Attempting to retrieve approval rules for project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST APPROVAL RULES] Successfully retrieved approval rules.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST APPROVAL RULES] Error retrieving approval rules: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[LIST APPROVAL RULES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_project_approval_rule(
    project_id: Union[int, str],
    approval_rule_id: int
) -> Union[Dict, Dict]:
    """
    Retrieve an approval rule for a project
    Retrieves information about a specified approval rule for a project using:
        GET /projects/:id/approval_rules/:approval_rule_id

    This function fetches the detailed configuration for a single, identified 
    project-level approval rule.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        approval_rule_id (int): The ID of a approval rule. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the single approval rule object. 
              Key attributes include:
                - id (integer): ID of the approval rule.
                - name (string): Name of the rule.
                - rule_type (string): Type of rule.
                - approvals_required (integer): The number of approvals required for this rule.
                - users (array): List of user objects directly assigned to the rule.
                - groups (array): List of group objects assigned to the rule.
                - protected_branches (array): List of protected branches the rule applies to.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET APPROVAL RULE] Attempting to retrieve approval rule {approval_rule_id} for project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET APPROVAL RULE] Successfully retrieved approval rule.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET APPROVAL RULE] Error retrieving approval rule: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_project_approval_rule(
    project_id: Union[int, str],
    name: str,
    approvals_required: int,
    applies_to_all_protected_branches: Optional[bool] = None,
    group_ids: Optional[List[int]] = None,
    protected_branch_ids: Optional[List[int]] = None,
    report_type: Optional[str] = None,
    rule_type: Optional[str] = None,
    user_ids: Optional[List[int]] = None,
    usernames: Optional[List[str]] = None
) -> Union[Dict, Dict]:
    """
    Create an approval rule for a project
    Creates an approval rule for a project using:
        POST /projects/:id/approval_rules

    This tool establishes a new rule for merge request approvals, specifying the 
    required number of approvals and the users/groups who can provide them.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        name (str): The name of the approval rule (Limited to 1024 characters). (Required)
        approvals_required (int): The number of required approvals for this rule. (Required)
        applies_to_all_protected_branches (Optional[bool]): If true, applies the rule to 
                                                            all protected branches.
        group_ids (Optional[List[int]]): The IDs of groups as approvers.
        protected_branch_ids (Optional[List[int]]): The IDs of protected branches to scope 
                                                    the rule by.
        report_type (Optional[str]): The report type. Required when rule_type is 'report_approver'. 
                                     Supported: 'license_scanning' (Deprecated) and 'code_coverage'.
        rule_type (Optional[str]): The rule type. Supported: 'any_approver', 'regular'. 
                                   Do not use 'report_approver' when creating. Defaults to 'regular'.
        user_ids (Optional[List[int]]): The IDs of users as approvers.
        usernames (Optional[List[str]]): The usernames of approvers.

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the created approval rule object.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approval_rules"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'name': name,
        'approvals_required': approvals_required,
    }

    # Map Python function argument names to Payload fields and convert bools/lists
    optional_params = {
        'applies_to_all_protected_branches': applies_to_all_protected_branches,
        'group_ids': group_ids,
        'protected_branch_ids': protected_branch_ids,
        'report_type': report_type,
        'rule_type': rule_type,
        'user_ids': user_ids,
        'usernames': usernames,
    }
    
    for key, value in optional_params.items():
        if value is not None:
            # GitLab API usually expects booleans as lowercase strings or true/false JSON values
            if isinstance(value, bool):
                payload[key] = value
            else:
                payload[key] = value

    print(f"\n[CREATE APPROVAL RULE] Attempting to create approval rule '{name}' for project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (201 Created)
        print(f"[CREATE APPROVAL RULE] Successfully created approval rule '{name}'.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[CREATE APPROVAL RULE] Error creating approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[CREATE APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_gitlab_project_approval_rule(
    project_id: Union[int, str],
    approval_rule_id: int,
    name: Optional[str] = None,
    approvals_required: Optional[int] = None,
    applies_to_all_protected_branches: Optional[bool] = None,
    group_ids: Optional[List[int]] = None,
    protected_branch_ids: Optional[List[int]] = None,
    remove_hidden_groups: Optional[bool] = None,
    user_ids: Optional[List[int]] = None,
    usernames: Optional[List[str]] = None
) -> Union[Dict, Dict]:
    """
    Update an approval rule for a project
    Updates a specified approval rule for a project using:
        PUT /projects/:id/approval_rules/:approval_rule_id

    This tool modifies an existing approval rule. Any users or groups not explicitly 
    included in the update parameters are removed from the rule, unless they are 
    "hidden groups" (which are preserved unless remove_hidden_groups is set to true).

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        approval_rule_id (int): The ID of the approval rule to update. (Required)
        name (Optional[str]): The new name of the approval rule (Limited to 1024 characters).
        approvals_required (Optional[int]): The new number of required approvals for this rule.
        applies_to_all_protected_branches (Optional[bool]): If true, applies the rule to 
                                                            all protected branches.
        group_ids (Optional[List[int]]): The IDs of groups as new approvers (overwrites existing list).
        protected_branch_ids (Optional[List[int]]): The IDs of protected branches to scope the rule by (overwrites existing list).
        remove_hidden_groups (Optional[bool]): If true, removes hidden groups from the approval rule.
        user_ids (Optional[List[int]]): The IDs of users as new approvers (overwrites existing list, combined with usernames).
        usernames (Optional[List[str]]): The usernames of new approvers (overwrites existing list, combined with user_ids).

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the updated approval rule object.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    # Collect all non-None arguments into the payload
    payload = {
        k: v for k, v in locals().items() 
        if k in [
            'name',
            'approvals_required',
            'applies_to_all_protected_branches',
            'group_ids',
            'protected_branch_ids',
            'remove_hidden_groups',
            'user_ids',
            'usernames'
        ] and v is not None
    }
    
    if not payload:
        return {"warning": "No update parameters provided.", "details": "The API call was skipped because no optional parameters were set."}

    print(f"\n[UPDATE APPROVAL RULE] Attempting to update approval rule {approval_rule_id} for project {project_id}.")
    
    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (200 OK)
        print(f"[UPDATE APPROVAL RULE] Successfully updated approval rule {approval_rule_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[UPDATE APPROVAL RULE] Error updating approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[UPDATE APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_gitlab_project_approval_rule(
    project_id: Union[int, str],
    approval_rule_id: int
) -> Union[Dict, Dict]:
    """
    Delete an approval rule for a project
    Deletes an approval rule for a specified project using:
        DELETE /projects/:id/approval_rules/:approval_rule_id

    This tool permanently removes a project-level merge request approval rule.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        approval_rule_id (int): The ID of the approval rule to delete. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (204 No Content): A dictionary indicating successful deletion (usually empty dict).
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[DELETE APPROVAL RULE] Attempting to delete approval rule {approval_rule_id} for project {project_id}.")
    
    try:
        # 3. Make the DELETE request
        response = requests.delete(api_url, headers=headers)
        
        # 4. Handle Success (204 No Content) or raise for error
        response.raise_for_status() 
        
        # 5. Return success message or empty dict for 204
        if response.status_code == 204:
            print(f"[DELETE APPROVAL RULE] Successfully deleted approval rule {approval_rule_id}.")
            return {"message": f"Successfully deleted approval rule {approval_rule_id}.", "status_code": 204}
        else:
            # Should not happen if raise_for_status() didn't fail, but good for safety
            return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[DELETE APPROVAL RULE] Error deleting approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[DELETE APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_request_approval_state(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Retrieve approval state for a merge request
    Retrieves the basic approval state for a specified merge request using:
        GET /projects/:id/merge_requests/:merge_request_iid/approvals

    This endpoint provides a high-level summary of the merge request's approval status, 
    including the required and remaining approvals, and a list of all users who 
    have approved it, regardless of specific approval rules.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the MR's approval state, 
              including 'approvals_required', 'approvals_left', and 'approved_by' list.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approvals"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET MR APPROVAL STATE] Attempting to retrieve approval state for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR APPROVAL STATE] Successfully retrieved basic approval state.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR APPROVAL STATE] Error retrieving approval state: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET MR APPROVAL STATE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_request_approval_details(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Retrieve approval details for a merge request
    Retrieves detailed approval status, including rule-specific information, for a specified merge request using:
        GET /projects/:id/merge_requests/:merge_request_iid/approval_state

    This endpoint provides in-depth details about which approval rules apply to the 
    merge request, whether they have been overwritten, and which users have approved 
    *according to the rules*.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the detailed approval state. Key attributes include:
                - approval_rules_overwritten (boolean): If true, indicates the default project rules were modified.
                - rules (array): List of approval rule objects, each showing:
                    - approved (boolean): If true, this specific rule has been satisfied.
                    - approved_by (array): List of users who approved under this specific rule.
                    - eligible_approvers (array): List of users who can approve for this rule.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approval_state"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET MR APPROVAL DETAILS] Attempting to retrieve approval details for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR APPROVAL DETAILS] Successfully retrieved approval details.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR APPROVAL DETAILS] Error retrieving approval details: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET MR APPROVAL DETAILS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_approval_rules(
    project_id: Union[int, str],
    merge_request_iid: int,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List all approval rules for a merge request
    Lists all approval rules and any associated details for a specified merge request using:
        GET /projects/:id/merge_requests/:merge_request_iid/approval_rules

    This tool retrieves the list of approval rules that apply to a *specific* merge request. 
    These rules can be inherited from project settings or specifically overwritten 
    for the individual merge request.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)
        per_page (Optional[int]): Number of results per page for pagination.
        page (Optional[int]): Page number of results for pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of approval rule objects (dictionaries) relevant to the MR. 
              Key attributes include:
                - id (integer): ID of the approval rule.
                - name (string): Name of the rule.
                - rule_type (string): Type of rule.
                - approvals_required (integer): The number of approvals required for this rule.
                - users (array): List of user objects directly assigned to the rule.
                - groups (array): List of group objects assigned to the rule.
                - overridden (boolean): If true, this rule has been modified specifically for the MR.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approval_rules"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if per_page is not None:
        params['per_page'] = per_page
    if page is not None:
        params['page'] = page

    print(f"\n[LIST MR APPROVAL RULES] Attempting to retrieve approval rules for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST MR APPROVAL RULES] Successfully retrieved merge request approval rules.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST MR APPROVAL RULES] Error retrieving MR approval rules: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[LIST MR APPROVAL RULES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

from typing import Optional, Union, Dict, List

@mcp.tool()
def get_gitlab_merge_request_approval_rule(
    project_id: Union[int, str],
    merge_request_iid: int,
    approval_rule_id: int
) -> Union[Dict, Dict]:
    """
    Retrieve an approval rule for a specific merge request
    Retrieves information about an approval rule for a specific merge request using:
        GET /projects/:id/merge_requests/:merge_request_iid/approval_rules/:approval_rule_id

    This tool fetches the detailed configuration for a single, identified approval rule 
    that is scoped to a specific merge request.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)
        approval_rule_id (int): The ID of the approval rule. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the single approval rule object. 
              Key attributes include:
                - id (integer): ID of the approval rule.
                - name (string): Name of the rule.
                - approvals_required (integer): The number of approvals required for this rule.
                - users (array): List of user objects.
                - groups (array): List of group objects.
                - overridden (boolean): If true, indicates the rule was modified for this MR.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET MR APPROVAL RULE] Attempting to retrieve approval rule {approval_rule_id} for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR APPROVAL RULE] Successfully retrieved approval rule.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR APPROVAL RULE] Error retrieving approval rule: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET MR APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_merge_request_approval_rule(
    project_id: Union[int, str],
    merge_request_iid: int,
    name: str,
    approvals_required: int,
    approval_project_rule_id: Optional[int] = None,
    group_ids: Optional[List[int]] = None,
    user_ids: Optional[List[int]] = None,
    usernames: Optional[List[str]] = None
) -> Union[Dict, Dict]:
    """
    Create an approval rule for a merge request
    Creates an approval rule that applies only to the specified merge request using:
        POST /projects/:id/merge_requests/:merge_request_iid/approval_rules

    This tool establishes a new, localized approval rule for a specific merge request. 
    If 'approval_project_rule_id' is provided, it copies the users/groups from the project's 
    rule but uses the specified 'approvals_required'.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)
        name (str): The name of the approval rule (Limited to 1024 characters). (Required)
        approvals_required (int): The number of required approvals for this rule. (Required)
        approval_project_rule_id (Optional[int]): The ID of a project's approval rule to copy from.
        group_ids (Optional[List[int]]): The IDs of groups as approvers (only used if not copying from project rule).
        user_ids (Optional[List[int]]): The IDs of users as approvers (only used if not copying from project rule).
        usernames (Optional[List[str]]): The usernames of approvers (only used if not copying from project rule).

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the created approval rule object.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approval_rules"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'name': name,
        'approvals_required': approvals_required,
    }

    optional_params = {
        'approval_project_rule_id': approval_project_rule_id,
        'group_ids': group_ids,
        'user_ids': user_ids,
        'usernames': usernames,
    }
    
    for key, value in optional_params.items():
        if value is not None:
            payload[key] = value

    print(f"\n[CREATE MR APPROVAL RULE] Attempting to create rule '{name}' for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (201 Created)
        print(f"[CREATE MR APPROVAL RULE] Successfully created approval rule '{name}'.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[CREATE MR APPROVAL RULE] Error creating approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[CREATE MR APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_gitlab_merge_request_approval_rule(
    project_id: Union[int, str],
    merge_request_iid: int,
    approval_rule_id: int,
    name: Optional[str] = None,
    approvals_required: Optional[int] = None,
    group_ids: Optional[List[int]] = None,
    remove_hidden_groups: Optional[bool] = None,
    user_ids: Optional[List[int]] = None,
    usernames: Optional[List[str]] = None
) -> Union[Dict, Dict]:
    """
    Update an approval rule for a merge request
    Updates a specified approval rule for a merge request using:
        PUT /projects/:id/merge_requests/:merge_request_iid/approval_rules/:approval_rule_id

    This tool modifies an existing approval rule that is scoped to a specific merge request. 
    It removes any approvers and groups not explicitly included in the update parameters. 
    Note that system-generated rules like 'report_approver' or 'code_owner' cannot be edited.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)
        approval_rule_id (int): The ID of the approval rule to update. (Required)
        name (Optional[str]): The new name of the approval rule (Limited to 1024 characters).
        approvals_required (Optional[int]): The new number of required approvals for this rule.
        group_ids (Optional[List[int]]): The IDs of groups as new approvers (overwrites existing list).
        remove_hidden_groups (Optional[bool]): If true, removes hidden groups from the approval rule.
        user_ids (Optional[List[int]]): The IDs of users as new approvers (overwrites existing list, combined with usernames).
        usernames (Optional[List[str]]): The usernames of new approvers (overwrites existing list, combined with user_ids).

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the updated approval rule object.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    # Collect all non-None arguments into the payload
    payload = {
        k: v for k, v in locals().items() 
        if k in [
            'name',
            'approvals_required',
            'group_ids',
            'remove_hidden_groups',
            'user_ids',
            'usernames'
        ] and v is not None
    }
    
    if not payload:
        return {"warning": "No update parameters provided.", "details": "The API call was skipped because no optional parameters were set."}

    print(f"\n[UPDATE MR APPROVAL RULE] Attempting to update approval rule {approval_rule_id} for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (200 OK)
        print(f"[UPDATE MR APPROVAL RULE] Successfully updated approval rule {approval_rule_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[UPDATE MR APPROVAL RULE] Error updating approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[UPDATE MR APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_gitlab_merge_request_approval_rule(
    project_id: Union[int, str],
    merge_request_iid: int,
    approval_rule_id: int
) -> Union[Dict, Dict]:
    """
    Delete an approval rule for a merge request
    Deletes an approval rule for a specified merge request using:
        DELETE /projects/:id/merge_requests/:merge_request_iid/approval_rules/:approval_rule_id

    This tool permanently removes an approval rule that is scoped to a specific merge request. 
    Note that system-generated rules like 'report_approver' or 'code_owner' cannot be deleted.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of a project. (Required)
        merge_request_iid (int): The Internal ID (IID) of the merge request. (Required)
        approval_rule_id (int): The ID of the approval rule to delete. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (204 No Content): A dictionary indicating successful deletion.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[DELETE MR APPROVAL RULE] Attempting to delete approval rule {approval_rule_id} for MR !{merge_request_iid} in project {project_id}.")
    
    try:
        # 3. Make the DELETE request
        response = requests.delete(api_url, headers=headers)
        
        # 4. Handle Success (204 No Content) or raise for error
        response.raise_for_status() 
        
        # 5. Return success message or empty dict for 204
        if response.status_code == 204:
            print(f"[DELETE MR APPROVAL RULE] Successfully deleted approval rule {approval_rule_id}.")
            return {"message": f"Successfully deleted approval rule {approval_rule_id}.", "status_code": 204}
        else:
            # Should not happen if raise_for_status() didn't fail
            return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[DELETE MR APPROVAL RULE] Error deleting approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[DELETE MR APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_group_approval_rules(
    group_id: Union[int, str],
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List all approval rules for a group
    Lists all approval rules and any associated details for a specified group using:
        GET /groups/:id/approval_rules

    This tool retrieves the list of configured group-level approval rules, which define 
    the default merge request requirements for all projects within that group. 
    This is typically restricted to group administrators.

    Args:
        group_id (Union[int, str]): The ID or URL-encoded path of a group. (Required)
        per_page (Optional[int]): Number of results per page for pagination.
        page (Optional[int]): Page number of results for pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of group approval rule objects (dictionaries). 
              Key attributes include:
                - id (integer): ID of the approval rule.
                - name (string): Name of the rule.
                - rule_type (string): Type of rule ('any_approver', 'regular', 'report_approver', 'code_owner').
                - approvals_required (integer): The number of approvals required for this rule.
                - users (array): List of user objects directly assigned to the rule.
                - groups (array): List of group objects assigned to the rule.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx), including 403 Forbidden if the user is not a group administrator.
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/groups/{group_id}/approval_rules"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if per_page is not None:
        params['per_page'] = per_page
    if page is not None:
        params['page'] = page

    print(f"\n[LIST GROUP APPROVAL RULES] Attempting to retrieve approval rules for group {group_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST GROUP APPROVAL RULES] Successfully retrieved group approval rules.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST GROUP APPROVAL RULES] Error retrieving group approval rules: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[LIST GROUP APPROVAL RULES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_group_approval_rule(
    group_id: Union[int, str],
    name: str,
    approvals_required: int,
    group_ids: Optional[List[int]] = None,
    rule_type: Optional[str] = None,
    user_ids: Optional[List[int]] = None
) -> Union[Dict, Dict]:
    """
    Create an approval rule for a group
    Creates an approval rule for a group using:
        POST /groups/:id/approval_rules

    This tool establishes a new default approval rule for all projects within the group. 
    This is restricted to group administrators.

    Args:
        group_id (Union[int, str]): The ID or URL-encoded path of a group. (Required)
        name (str): The name of the approval rule (Limited to 1024 characters). (Required)
        approvals_required (int): The number of required approvals for this rule. (Required)
        group_ids (Optional[List[int]]): The IDs of groups as approvers.
        rule_type (Optional[str]): The rule type. Supported values: 'any_approver', 'regular'. 
                                   Do not use 'report_approver'.
        user_ids (Optional[List[int]]): The IDs of users as approvers.

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the created approval rule object.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/groups/{group_id}/approval_rules"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'name': name,
        'approvals_required': approvals_required,
    }

    optional_params = {
        'group_ids': group_ids,
        'rule_type': rule_type,
        'user_ids': user_ids,
    }
    
    for key, value in optional_params.items():
        if value is not None:
            payload[key] = value

    print(f"\n[CREATE GROUP APPROVAL RULE] Attempting to create rule '{name}' for group {group_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (201 Created)
        print(f"[CREATE GROUP APPROVAL RULE] Successfully created approval rule '{name}'.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[CREATE GROUP APPROVAL RULE] Error creating approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[CREATE GROUP APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_gitlab_group_approval_rule(
    group_id: Union[int, str],
    approval_rule_id: int,
    name: Optional[str] = None,
    approvals_required: Optional[int] = None,
    group_ids: Optional[List[int]] = None,
    user_ids: Optional[List[int]] = None
) -> Union[Dict, Dict]:
    """
    Update an approval rule for a group
    Updates an approval rule for a group using:
        PUT /groups/:id/approval_rules/:approval_rule_id

    This tool modifies an existing group-level approval rule, which applies as a default
    to projects within the group. This action is restricted to group administrators.
    This endpoint removes any approvers and groups not explicitly included in the update parameters.
    The rule_type cannot be changed via this endpoint.

    Args:
        group_id (Union[int, str]): The ID or URL-encoded path of a group. (Required)
        approval_rule_id (int): The ID of the approval rule to update. (Required)
        name (Optional[str]): The new name of the approval rule (Limited to 1024 characters).
        approvals_required (Optional[int]): The new number of required approvals for this rule.
        group_ids (Optional[List[int]]): The IDs of groups as new approvers (overwrites existing list).
        user_ids (Optional[List[int]]): The IDs of users as new approvers (overwrites existing list).

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary representing the updated approval rule object.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/groups/{group_id}/approval_rules/{approval_rule_id}"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    # Collect all non-None arguments into the payload
    # Note: rule_type is intentionally excluded as the prompt indicates it shouldn't be used for updating.
    payload = {
        k: v for k, v in locals().items() 
        if k in [
            'name',
            'approvals_required',
            'group_ids',
            'user_ids'
        ] and v is not None
    }
    
    # The API documentation specifies 'approvals_required' as 'string' type in the supported attributes table
    # but the example request shows it as an integer parameter. We'll pass it as an integer, 
    # as is typical for most GitLab API calls, or let the `json` library handle type conversion.
    if 'approvals_required' in payload and isinstance(payload['approvals_required'], int):
        # Convert to string as per documentation note, though usually GitLab prefers JSON ints. 
        # For safety and consistency with typical API standards, we'll keep it as int unless an error occurs.
        # However, the example shows it as a query parameter in the shell, which means the API expects it as a value.
        # We will keep it as an integer in the JSON body, which is the standard practice for POST/PUT/DELETE bodies.
        pass 
    
    if not payload:
        return {"warning": "No update parameters provided.", "details": "The API call was skipped because no optional parameters were set."}

    print(f"\n[UPDATE GROUP APPROVAL RULE] Attempting to update approval rule {approval_rule_id} for group {group_id}.")
    
    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (200 OK)
        print(f"[UPDATE GROUP APPROVAL RULE] Successfully updated approval rule {approval_rule_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[UPDATE GROUP APPROVAL RULE] Error updating approval rule: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[UPDATE GROUP APPROVAL RULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_requests(
    state: Optional[str] = None,
    scope: Optional[str] = None,
    labels: Optional[str] = None,
    milestone: Optional[str] = None,
    author_id: Optional[int] = None,
    author_username: Optional[str] = None,
    assignee_id: Optional[Union[int, str]] = None,
    reviewer_id: Optional[Union[int, str]] = None,
    reviewer_username: Optional[str] = None,
    approved_by_ids: Optional[List[int]] = None,
    approver_ids: Optional[List[int]] = None,
    merge_user_id: Optional[int] = None,
    merge_user_username: Optional[str] = None,
    my_reaction_emoji: Optional[str] = None,
    source_branch: Optional[str] = None,
    target_branch: Optional[str] = None,
    search: Optional[str] = None,
    in_scope: Optional[str] = None,
    order_by: Optional[str] = None,
    sort: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    deployed_after: Optional[str] = None,
    deployed_before: Optional[str] = None,
    environment: Optional[str] = None,
    view: Optional[str] = None,
    render_html: Optional[bool] = None,
    with_labels_details: Optional[bool] = None,
    with_merge_status_recheck: Optional[bool] = None,
    wip: Optional[str] = None,
    not_params: Optional[Dict[str, Union[str, int, List[int]]]] = None,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List merge requests
    Gets all merge requests the authenticated user has access to, with extensive filtering options using:
        GET /merge_requests

    By default, it returns only merge requests created by the current user unless scope='all' is used.
    It supports filtering by state, scope, labels, milestone, authors, assignees, reviewers, approval status, branches, 
    time (created/updated/deployed), and text search.

    Args:
        state (Optional[str]): Returns merge requests with a given state: 'opened', 'closed', 'locked', or 'merged', or 'all'.
        scope (Optional[str]): Returns merge requests for the given scope: 'created_by_me', 'assigned_to_me', 'reviews_for_me', or 'all'. Defaults to 'created_by_me'.
        labels (Optional[str]): Comma-separated list of labels. 'None' for no labels, 'Any' for at least one label.
        milestone (Optional[str]): Returns merge requests for a specific milestone. 'None' for no milestone, 'Any' for any milestone.
        author_id (Optional[int]): Returns merge requests created by the given user ID. Mutually exclusive with author_username.
        author_username (Optional[str]): Returns merge requests created by the given username.
        assignee_id (Optional[Union[int, str]]): Returns merge requests assigned to the given user ID. 'None' for unassigned, 'Any' for any assignee.
        reviewer_id (Optional[Union[int, str]]): Returns merge requests with the user as a reviewer by ID. 'None' for no reviewers, 'Any' for any reviewer.
        reviewer_username (Optional[str]): Returns merge requests with the user as a reviewer by username. Mutually exclusive with reviewer_id.
        approved_by_ids (Optional[List[int]]): Returns merge requests approved by all users with the given IDs (up to 5 users). Premium/Ultimate only.
        approver_ids (Optional[List[int]]): Returns merge requests which have specified all users with the given IDs as individual approvers. Premium/Ultimate only.
        merge_user_id (Optional[int]): Returns merge requests merged by the user with the given user ID. Mutually exclusive with merge_user_username.
        merge_user_username (Optional[str]): Returns merge requests merged by the user with the given username.
        my_reaction_emoji (Optional[str]): Returns merge requests reacted to by the authenticated user by the given emoji. 'None' or 'Any' also supported.
        source_branch (Optional[str]): Returns merge requests with the given source branch.
        target_branch (Optional[str]): Returns merge requests with the given target branch.
        search (Optional[str]): Search merge requests against their title and description.
        in_scope (Optional[str]): Change the scope of the 'search' attribute: 'title', 'description', or a comma-joined string. (Maps to API parameter 'in').
        order_by (Optional[str]): Returns requests ordered by 'created_at', 'title', 'merged_at', or 'updated_at'. Default is 'created_at'.
        sort (Optional[str]): Returns requests sorted in 'asc' or 'desc' order. Default is 'desc'.
        created_after (Optional[str]): Returns merge requests created on or after the given time (ISO 8601 format).
        created_before (Optional[str]): Returns merge requests created on or before the given time (ISO 8601 format).
        updated_after (Optional[str]): Returns merge requests updated on or after the given time (ISO 8601 format).
        updated_before (Optional[str]): Returns merge requests updated on or before the given time (ISO 8601 format).
        deployed_after (Optional[str]): Returns merge requests deployed after the given date/time (ISO 8601 format).
        deployed_before (Optional[str]): Returns merge requests deployed before the given date/time (ISO 8601 format).
        environment (Optional[str]): Returns merge requests deployed to the given environment.
        view (Optional[str]): If 'simple', returns a subset of fields (iid, URL, title, description, state).
        render_html (Optional[bool]): If true, the response includes rendered HTML fields title_html and description_html.
        with_labels_details (Optional[bool]): If true, response returns more details for each label.
        with_merge_status_recheck (Optional[bool]): If true, requests an asynchronous recalculation of the merge_status field.
        wip (Optional[str]): Filter merge requests against their 'wip' (draft) status. Use 'yes' or 'no'.
        not_params (Optional[Dict[str, Union[str, int, List[int]]]]): Returns merge requests that do NOT match the parameters supplied in this dictionary. Keys must be one of: 'labels', 'milestone', 'author_id', 'author_username', 'assignee_id', 'assignee_username', 'reviewer_id', 'reviewer_username', 'my_reaction_emoji'.
        per_page (Optional[int]): Number of results per page for pagination.
        page (Optional[int]): Page number of results for pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of merge request objects (dictionaries). Each object includes:
                - **id** (integer): The unique ID of the merge request.
                - **iid** (integer): The internal ID of the merge request in the project.
                - **project_id** (integer): The ID of the project containing the merge request.
                - **title** (string): The merge request title.
                - **description** (string): Description of the merge request.
                - **state** (string): The current state: 'opened', 'closed', 'merged', or 'locked'.
                - **created_at** (dateTime): Timestamp of when the merge request was created.
                - **updated_at** (dateTime): Timestamp of when the merge request was last updated.
                - **merged_at** (dateTime): Timestamp of when the merge request merged.
                - **closed_at** (dateTime): Timestamp of when the merge request was closed.
                - **author** (object): Information about the user who created the MR.
                - **assignees** (array): Users assigned to the merge request.
                - **reviewers** (array): Reviewers of the merge request.
                - **merge_user** (object): User who merged the merge request, or null.
                - **source_branch** (string): Name of the source branch.
                - **target_branch** (string): Name of the target branch.
                - **source_project_id** (integer): ID of the source project.
                - **target_project_id** (integer): ID of the target project.
                - **sha** (string): SHA of the head commit in the source branch.
                - **merge_commit_sha** (string): SHA of the merge request commit (null until merged).
                - **draft** (boolean): If true, the merge request is marked in a draft state.
                - **has_conflicts** (boolean): If true, the merge request has conflicts.
                - **detailed_merge_status** (string): Detailed merge status information (e.g., 'can_be_merged').
                - **labels** (array): Array of label assigned to the merge request.
                - **milestone** (object): Information about the assigned milestone.
                - **upvotes** (integer): Number of upvotes.
                - **downvotes** (integer): Number of downvotes.
                - **user_notes_count** (integer): Number of user comments.
                - **web_url** (string): Web URL to view the merge request.
                - **references** (object): Object with short, relative, and full references.
                - **time_stats** (object): Time tracking information (estimate and time spent).
                - **task_completion_status** (object): Task list completion count.
                - **squash** (boolean): If true, squash commits when merging.
                - **merge_when_pipeline_succeeds** (boolean): If true, set to auto-merge.
                - **allow_collaboration** (boolean): If true, allows collaboration from members who can merge to the target branch (for forks).
                - *Additional fields (like `closed_by`, `description_html`, etc.) may be included depending on request parameters.*
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/merge_requests"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters)
    # Map Python snake_case parameter names to GitLab API parameter names
    api_params = {
        'state': state,
        'scope': scope,
        'labels': labels,
        'milestone': milestone,
        'author_id': author_id,
        'author_username': author_username,
        'assignee_id': assignee_id,
        'reviewer_id': reviewer_id,
        'reviewer_username': reviewer_username,
        'approved_by_ids': approved_by_ids,
        'approver_ids': approver_ids,
        'merge_user_id': merge_user_id,
        'merge_user_username': merge_user_username,
        'my_reaction_emoji': my_reaction_emoji,
        'source_branch': source_branch,
        'target_branch': target_branch,
        'search': search,
        'in': in_scope,
        'order_by': order_by,
        'sort': sort,
        'created_after': created_after,
        'created_before': created_before,
        'updated_after': updated_after,
        'updated_before': updated_before,
        'deployed_after': deployed_after,
        'deployed_before': deployed_before,
        'environment': environment,
        'view': view,
        'render_html': render_html,
        'with_labels_details': with_labels_details,
        'with_merge_status_recheck': with_merge_status_recheck,
        'wip': wip,
        'per_page': per_page,
        'page': page,
    }
    
    # Filter out None values
    params = {k: v for k, v in api_params.items() if v is not None}
    
    # Handle 'not' parameter hash separately
    if not_params:
        for key, value in not_params.items():
            if value is not None:
                params[f'not[{key}]'] = value

    # Log the attempt
    filter_summary = f"state={state}, scope={scope}" if state or scope else "default scope"
    print(f"\n[LIST MERGE REQUESTS] Attempting to retrieve merge requests with filters: {filter_summary}. Total filters: {len(params)}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST MERGE REQUESTS] Successfully retrieved merge requests.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST MERGE REQUESTS] Error retrieving merge requests: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[LIST MERGE REQUESTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def list_gitlab_project_merge_requests(
    project_id: Union[int, str],
    state: Optional[str] = None,
    scope: Optional[str] = None,
    iids: Optional[List[int]] = None,
    labels: Optional[str] = None,
    milestone: Optional[str] = None,
    author_id: Optional[int] = None,
    author_username: Optional[str] = None,
    assignee_id: Optional[Union[int, str]] = None,
    reviewer_id: Optional[Union[int, str]] = None,
    reviewer_username: Optional[str] = None,
    approved_by_ids: Optional[List[int]] = None,
    approver_ids: Optional[List[int]] = None,
    merge_user_id: Optional[int] = None,
    merge_user_username: Optional[str] = None,
    my_reaction_emoji: Optional[str] = None,
    source_branch: Optional[str] = None,
    target_branch: Optional[str] = None,
    search: Optional[str] = None,
    order_by: Optional[str] = None,
    sort: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    environment: Optional[str] = None,
    view: Optional[str] = None,
    wip: Optional[str] = None,
    with_labels_details: Optional[bool] = None,
    with_merge_status_recheck: Optional[bool] = None,
    not_params: Optional[Dict[str, Union[str, int, List[int]]]] = None,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List project merge requests
    Gets all merge requests for a specified project, with extensive filtering options using:
        GET /projects/:id/merge_requests

    It supports filtering by state, IIDs, labels, milestone, authors, assignees, reviewers, 
    approval status, branches, time (created/updated), and text search.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        state (Optional[str]): Returns merge requests with a given state: 'opened', 'closed', 'locked', or 'merged', or 'all'.
        scope (Optional[str]): Returns merge requests for the given scope: 'created_by_me', 'assigned_to_me', or 'all'.
        iids (Optional[List[int]]): Returns the merge requests having the given Internal IDs (IIDs).
        labels (Optional[str]): Comma-separated list of labels. 'None' for no labels, 'Any' for at least one label.
        milestone (Optional[str]): Returns merge requests for a specific milestone. 'None' or 'Any' also supported.
        author_id (Optional[int]): Returns merge requests created by the given user ID. Mutually exclusive with author_username.
        author_username (Optional[str]): Returns merge requests created by the given username.
        assignee_id (Optional[Union[int, str]]): Returns merge requests assigned to the given user ID. 'None' or 'Any' also supported.
        reviewer_id (Optional[Union[int, str]]): Returns merge requests with the user as a reviewer by ID. 'None' or 'Any' also supported.
        reviewer_username (Optional[str]): Returns merge requests with the user as a reviewer by username. Mutually exclusive with reviewer_id.
        approved_by_ids (Optional[List[int]]): Returns merge requests approved by all users with the given IDs (up to 5 users). Premium/Ultimate only.
        approver_ids (Optional[List[int]]): Returns merge requests which have specified all users with the given IDs as individual approvers. Premium/Ultimate only.
        merge_user_id (Optional[int]): Returns merge requests merged by the user with the given user ID. Mutually exclusive with merge_user_username. (GitLab 17.0+).
        merge_user_username (Optional[str]): Returns merge requests merged by the user with the given username. Mutually exclusive with merge_user_id. (GitLab 17.0+).
        my_reaction_emoji (Optional[str]): Returns merge requests reacted to by the authenticated user by the given emoji. 'None' or 'Any' also supported.
        source_branch (Optional[str]): Returns merge requests with the given source branch.
        target_branch (Optional[str]): Returns merge requests with the given target branch.
        search (Optional[str]): Search merge requests against their title and description.
        order_by (Optional[str]): Returns requests ordered by 'created_at', 'title', or 'updated_at' fields. Default is 'created_at'.
        sort (Optional[str]): Returns requests sorted in 'asc' or 'desc' order. Default is 'desc'.
        created_after (Optional[str]): Returns merge requests created on or after the given time (ISO 8601 format).
        created_before (Optional[str]): Returns merge requests created on or before the given time (ISO 8601 format).
        updated_after (Optional[str]): Returns merge requests updated on or after the given time (ISO 8601 format).
        updated_before (Optional[str]): Returns merge requests updated on or before the given time (ISO 8601 format).
        environment (Optional[str]): Returns merge requests deployed to the given environment.
        view (Optional[str]): If 'simple', returns a subset of fields (iid, URL, title, description, state).
        wip (Optional[str]): Filter merge requests against their 'wip' (draft) status. Use 'yes' or 'no'.
        with_labels_details (Optional[bool]): If true, response returns more details for each label.
        with_merge_status_recheck (Optional[bool]): If true, requests an asynchronous recalculation of the merge_status field.
        not_params (Optional[Dict[str, Union[str, int, List[int]]]]): Returns merge requests that do NOT match the parameters supplied in this dictionary. Accepts keys: 'labels', 'milestone', 'author_id', 'author_username', 'assignee_id', 'assignee_username', 'reviewer_id', 'reviewer_username', 'my_reaction_emoji'.
        per_page (Optional[int]): Number of results per page for pagination.
        page (Optional[int]): Page number of results for pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of merge request objects (dictionaries). Each object includes attributes such as:
                - **id** (integer): ID of the merge request.
                - **iid** (integer): Internal ID of the merge request.
                - **project_id** (integer): ID of the project where the merge request resides.
                - **title** (string): Title of the merge request.
                - **description** (string): Description of the merge request.
                - **state** (string): State of the merge request ('opened', 'closed', 'merged', 'locked').
                - **web_url** (string): Web URL of the merge request.
                - **author** (object): User who created this merge request.
                - **assignee** (object): *Deprecated*. First assignee of the merge request.
                - **assignees** (array): Assignees of the merge request.
                - **reviewers** (array): Reviewers of the merge request.
                - **merge_user** (object): User who merged this merge request, or set it to auto-merge.
                - **merged_at** (datetime): Timestamp of when the merge request was merged.
                - **created_at** (datetime): Timestamp of when the merge request was created.
                - **updated_at** (datetime): Timestamp of when the merge request was updated.
                - **closed_at** (datetime): Timestamp of when the merge request was closed.
                - **closed_by** (object): User who closed this merge request.
                - **source_branch** (string): Source branch of the merge request.
                - **target_branch** (string): Target branch of the merge request.
                - **source_project_id** (integer): ID of the merge request source project (differs from `target_project_id` for forks).
                - **target_project_id** (integer): ID of the merge request target project.
                - **sha** (string): Diff head SHA of the merge request.
                - **merge_commit_sha** (string): SHA of the merge request commit (null until merged).
                - **draft** (boolean): Indicates if the merge request is a draft.
                - **work_in_progress** (boolean): *Deprecated*. Use `draft` instead.
                - **has_conflicts** (boolean): Indicates if the merge request has conflicts.
                - **detailed_merge_status** (string): Detailed merge status.
                - **merge_status** (string): *Deprecated*. Status of the merge request. Use `detailed_merge_status` instead.
                - **labels** (array): Labels of the merge request.
                - **milestone** (object): Milestone of the merge request.
                - **upvotes** (integer): Number of upvotes.
                - **downvotes** (integer): Number of downvotes.
                - **user_notes_count** (integer): User notes count of the merge request.
                - **references** (object): Internal references (short, relative, full).
                - **time_stats** (object): Time tracking stats.
                - **task_completion_status** (object): Completion status of tasks (count and completed_count).
                - **squash** (boolean): If true, squash all commits into a single commit on merge.
                - **squash_on_merge** (boolean): Indicates whether to squash the merge request when merging.
                - **should_remove_source_branch** (boolean): Indicates if the source branch should be deleted after merge.
                - **blocking_discussions_resolved** (boolean): Indicates if all discussions are resolved.
                - **approvals_before_merge** (integer): *Deprecated*. Number of approvals required before merge.
                - **prepared_at** (datetime): Timestamp of when the merge request was prepared.
                - **discussion_locked** (boolean): Indicates if comments are locked to members only.
                - **force_remove_source_branch** (boolean): Indicates if the project settings force branch deletion.
                - **squash_commit_sha** (string): SHA of the squash commit (empty until merged).
                - **merge_when_pipeline_succeeds** (boolean): Indicates if the merge request is set to auto-merge.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters)
    # Map Python snake_case parameter names to GitLab API parameter names
    api_params = {
        'state': state,
        'scope': scope,
        'iids': iids,
        'labels': labels,
        'milestone': milestone,
        'author_id': author_id,
        'author_username': author_username,
        'assignee_id': assignee_id,
        'reviewer_id': reviewer_id,
        'reviewer_username': reviewer_username,
        'approved_by_ids': approved_by_ids,
        'approver_ids': approver_ids,
        'merge_user_id': merge_user_id,
        'merge_user_username': merge_user_username,
        'my_reaction_emoji': my_reaction_emoji,
        'source_branch': source_branch,
        'target_branch': target_branch,
        'search': search,
        'order_by': order_by,
        'sort': sort,
        'created_after': created_after,
        'created_before': created_before,
        'updated_after': updated_after,
        'updated_before': updated_before,
        'environment': environment,
        'view': view,
        'wip': wip,
        'with_labels_details': with_labels_details,
        'with_merge_status_recheck': with_merge_status_recheck,
        'per_page': per_page,
        'page': page,
    }

    # Filter out None values
    params = {}
    for k, v in api_params.items():
        if v is not None:
            # Handle list parameters for correct URL encoding (e.g., iids[]=1&iids[]=2)
            if isinstance(v, list) and k in ('iids', 'approved_by_ids', 'approver_ids'):
                # The 'requests' library handles list values in params by repeating the key with '[]' if it's in the key name, but here we let it handle the list directly.
                params[f'{k}[]'] = v
            else:
                params[k] = v

    # Handle 'not' parameter hash separately
    if not_params:
        for key, value in not_params.items():
            if value is not None:
                params[f'not[{key}]'] = value

    # Log the attempt
    filter_summary = f"state={state}" if state else "all states"
    print(f"\n[LIST PROJECT MERGE REQUESTS] Attempting to retrieve merge requests for project {project_id} with filters: {filter_summary}. Total filters: {len(params)}.")

    try:
        # 4. Make the GET request
        # The 'requests' library automatically handles the list of iids/approved_by_ids when the key is repeated.
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST PROJECT MERGE REQUESTS] Successfully retrieved merge requests for project {project_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST PROJECT MERGE REQUESTS] Error retrieving merge requests: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[LIST PROJECT MERGE REQUESTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

from typing import Optional, Union, Dict, List

@mcp.tool()
def list_gitlab_group_merge_requests(
    group_id: Union[int, str],
    state: Optional[str] = None,
    scope: Optional[str] = None,
    labels: Optional[str] = None,
    milestone: Optional[str] = None,
    author_id: Optional[int] = None,
    author_username: Optional[str] = None,
    assignee_id: Optional[Union[int, str]] = None,
    reviewer_id: Optional[Union[int, str]] = None,
    reviewer_username: Optional[str] = None,
    approved_by_ids: Optional[List[int]] = None,
    approved_by_usernames: Optional[List[str]] = None,
    approver_ids: Optional[List[int]] = None,
    merge_user_id: Optional[int] = None,
    merge_user_username: Optional[str] = None,
    my_reaction_emoji: Optional[str] = None,
    source_branch: Optional[str] = None,
    target_branch: Optional[str] = None,
    search: Optional[str] = None,
    order_by: Optional[str] = None,
    sort: Optional[str] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    non_archived: Optional[bool] = None,
    view: Optional[str] = None,
    with_labels_details: Optional[bool] = None,
    with_merge_status_recheck: Optional[bool] = None,
    not_params: Optional[Dict[str, Union[str, int, List[int]]]] = None,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List group merge requests
    Gets all merge requests for a specified group and its subgroups using:
        GET /groups/:id/merge_requests

    It supports filtering by state, labels, milestone, authors, assignees, reviewers, 
    approval status, branches, time (created/updated), and text search across all projects 
    within the group and its subgroups.

    Args:
        group_id (Union[int, str]): The ID or URL-encoded path of the group. (Required)
        state (Optional[str]): Returns merge requests with a given state: 'opened', 'closed', 'locked', or 'merged', or 'all'.
        scope (Optional[str]): Returns merge requests for the given scope: 'created_by_me', 'assigned_to_me', or 'all'.
        labels (Optional[str]): Comma-separated list of labels. 'None' for no labels, 'Any' for at least one label.
        milestone (Optional[str]): Returns merge requests for a specific milestone. 'None' or 'Any' also supported.
        author_id (Optional[int]): Returns merge requests created by the given user ID. Mutually exclusive with author_username.
        author_username (Optional[str]): Returns merge requests created by the given username.
        assignee_id (Optional[Union[int, str]]): Returns merge requests assigned to the given user ID. 'None' or 'Any' also supported.
        reviewer_id (Optional[Union[int, str]]): Returns merge requests with the user as a reviewer by ID. 'None' or 'Any' also supported.
        reviewer_username (Optional[str]): Returns merge requests with the user as a reviewer by username. Mutually exclusive with reviewer_id.
        approved_by_ids (Optional[List[int]]): Returns merge requests approved by all users with the given IDs (up to 5 users). Premium/Ultimate only.
        approved_by_usernames (Optional[List[str]]): Returns merge requests approved by all users with the given usernames (up to 5 users). Premium/Ultimate only.
        approver_ids (Optional[List[int]]): Returns merge requests which have specified all users with the given IDs as individual approvers. Premium/Ultimate only.
        merge_user_id (Optional[int]): Returns merge requests merged by the user with the given user ID. Mutually exclusive with merge_user_username. (GitLab 17.0+).
        merge_user_username (Optional[str]): Returns merge requests merged by the user with the given username. Mutually exclusive with merge_user_id. (GitLab 17.0+).
        my_reaction_emoji (Optional[str]): Returns merge requests reacted to by the authenticated user by the given emoji. 'None' or 'Any' also supported.
        source_branch (Optional[str]): Returns merge requests with the given source branch.
        target_branch (Optional[str]): Returns merge requests with the given target branch.
        search (Optional[str]): Search merge requests against their title and description.
        order_by (Optional[str]): Returns requests ordered by 'created_at', 'title', or 'updated_at' fields. Default is 'created_at'.
        sort (Optional[str]): Returns requests sorted in 'asc' or 'desc' order. Default is 'desc'.
        created_after (Optional[str]): Returns merge requests created on or after the given time (ISO 8601 format).
        created_before (Optional[str]): Returns merge requests created on or before the given time (ISO 8601 format).
        updated_after (Optional[str]): Returns merge requests updated on or after the given time (ISO 8601 format).
        updated_before (Optional[str]): Returns merge requests updated on or before the given time (ISO 8601 format).
        non_archived (Optional[bool]): Returns merge requests from non-archived projects only. Default is True.
        view (Optional[str]): If 'simple', returns a subset of fields (iid, URL, title, description, state).
        with_labels_details (Optional[bool]): If true, response returns more details for each label.
        with_merge_status_recheck (Optional[bool]): If true, requests an asynchronous recalculation of the merge_status field.
        not_params (Optional[Dict[str, Union[str, int, List[int]]]]): Returns merge requests that do NOT match the parameters supplied in this dictionary. Accepts keys: 'labels', 'milestone', 'author_id', 'author_username', 'assignee_id', 'assignee_username', 'reviewer_id', 'reviewer_username', 'my_reaction_emoji'.
        per_page (Optional[int]): Number of results per page for pagination.
        page (Optional[int]): Page number of results for pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of merge request objects (dictionaries). Each object includes attributes such as:
                - **id** (integer): ID of the merge request.
                - **iid** (integer): Internal ID of the merge request.
                - **project_id** (integer): ID of the project containing the merge request.
                - **title** (string): Title of the merge request.
                - **description** (string): Description of the merge request.
                - **state** (string): State of the merge request ('opened', 'closed', 'merged', 'locked').
                - **web_url** (string): Web URL of the merge request.
                - **author** (object): User who created this merge request.
                - **assignees** (array): Assignees of the merge request.
                - **reviewers** (array): Reviewers of the merge request.
                - **merge_user** (object): User who merged this merge request, or set it to auto-merge.
                - **merged_at** (datetime): Timestamp of when the merge request was merged.
                - **created_at** (datetime): Timestamp of when the merge request was created.
                - **updated_at** (datetime): Timestamp of when the merge request was updated.
                - **closed_at** (datetime): Timestamp of when the merge request was closed.
                - **closed_by** (object): User who closed this merge request.
                - **source_branch** (string): Source branch of the merge request.
                - **target_branch** (string): Target branch of the merge request.
                - **source_project_id** (integer): ID of the merge request source project (differs from `target_project_id` for forks).
                - **target_project_id** (integer): ID of the merge request target project.
                - **sha** (string): Diff head SHA of the merge request.
                - **merge_commit_sha** (string): SHA of the merge request commit (null until merged).
                - **draft** (boolean): Indicates if the merge request is a draft.
                - **has_conflicts** (boolean): Indicates if the merge request has conflicts.
                - **detailed_merge_status** (string): Detailed merge status.
                - **labels** (array): Labels of the merge request.
                - **milestone** (object): Milestone of the merge request.
                - **upvotes** (integer): Number of upvotes.
                - **user_notes_count** (integer): User notes count of the merge request.
                - **references** (object): Internal references (short, relative, full).
                - **time_stats** (object): Time tracking stats.
                - **task_completion_status** (object): Completion status of tasks (count and completed_count).
                - **squash_on_merge** (boolean): Indicates whether to squash the merge request when merging.
                - **should_remove_source_branch** (boolean): Indicates if the source branch should be deleted after merge.
                - **blocking_discussions_resolved** (boolean): Indicates if all discussions are resolved.
                - **merge_when_pipeline_succeeds** (boolean): Indicates if the merge request is set to auto-merge.
                - *Deprecated fields like `assignee`, `merged_by`, `work_in_progress`, and `merge_status` may also be present.*
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/groups/{group_id}/merge_requests"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters)
    # Map Python snake_case parameter names to GitLab API parameter names
    api_params = {
        'state': state,
        'scope': scope,
        'labels': labels,
        'milestone': milestone,
        'author_id': author_id,
        'author_username': author_username,
        'assignee_id': assignee_id,
        'reviewer_id': reviewer_id,
        'reviewer_username': reviewer_username,
        'approved_by_ids': approved_by_ids,
        'approved_by_usernames': approved_by_usernames,
        'approver_ids': approver_ids,
        'merge_user_id': merge_user_id,
        'merge_user_username': merge_user_username,
        'my_reaction_emoji': my_reaction_emoji,
        'source_branch': source_branch,
        'target_branch': target_branch,
        'search': search,
        'order_by': order_by,
        'sort': sort,
        'created_after': created_after,
        'created_before': created_before,
        'updated_after': updated_after,
        'updated_before': updated_before,
        'non_archived': non_archived,
        'view': view,
        'with_labels_details': with_labels_details,
        'with_merge_status_recheck': with_merge_status_recheck,
        'per_page': per_page,
        'page': page,
    }

    # Filter out None values and prepare list parameters for 'requests' library
    params = {}
    for k, v in api_params.items():
        if v is not None:
            # List parameters that need the '[]' suffix for correct URL encoding
            if k in ('approved_by_ids', 'approved_by_usernames', 'approver_ids'):
                if isinstance(v, list):
                    # The 'requests' library handles list values by repeating the key if it includes '[]'
                    params[f'{k}[]'] = v
                else:
                    params[k] = v
            else:
                params[k] = v

    # Handle 'not' parameter hash separately
    if not_params:
        for key, value in not_params.items():
            if value is not None:
                params[f'not[{key}]'] = value

    # Log the attempt
    filter_summary = f"state={state}" if state else "all states"
    print(f"\n[LIST GROUP MERGE REQUESTS] Attempting to retrieve merge requests for group {group_id} with filters: {filter_summary}. Total filters: {len(params)}.")

    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST GROUP MERGE REQUESTS] Successfully retrieved merge requests for group {group_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST GROUP MERGE REQUESTS] Error retrieving merge requests: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[LIST GROUP MERGE REQUESTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_single_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int,
    include_diverged_commits_count: Optional[bool] = None,
    include_rebase_in_progress: Optional[bool] = None,
    render_html: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Get single MR
    Shows detailed information about a single merge request in a project using its Internal ID (IID).

    GET /projects/:id/merge_requests/:merge_request_iid

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        include_diverged_commits_count (Optional[bool]): If true, the response includes the number of commits the source branch is behind the target branch.
        include_rebase_in_progress (Optional[bool]): If true, the response includes whether a rebase operation is currently in progress.
        render_html (Optional[bool]): If true, the response includes rendered HTML for the title and description fields.

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary (object) containing the detailed information for the single merge request.
              The response includes the following attributes (object attributes have nested fields):

                **Core Metadata & State**
                - **id** (integer): The unique ID of the merge request.
                - **iid** (integer): The Internal ID of the merge request.
                - **project_id** (integer): The ID of the project containing the merge request.
                - **title** (string): The merge request title.
                - **description** (string): Description of the merge request (contains Markdown).
                - **state** (string): The current state ('opened', 'closed', 'merged', 'locked').
                - **web_url** (string): Web URL to view the merge request.
                - **references** (object): All internal references (short, relative, full).
                - **reference** (string): *Deprecated*. Use `references` instead.
                - **draft** (boolean): If true, the merge request is marked as a draft.
                - **work_in_progress** (boolean): *Deprecated*. Use `draft` instead.
                - **subscribed** (boolean): If true, the current authenticated user subscribes to this MR.
                - **imported** (boolean): If true, the merge request was imported.
                - **imported_from** (string): Source of import, such as 'Bitbucket'.

                **Personnel & Approvals**
                - **author** (object): Object with information about the user who created the merge request.
                - **assignees** (array): List of users assigned to the merge request.
                - **assignee** (object): *Deprecated*. First assignee of the merge request.
                - **reviewers** (array): List of users assigned as reviewers.
                - **closed_by** (object): User who closed this merge request, or null.
                - **merge_user** (object): The user who merged this merge request, or set it to auto-merge.
                - **merged_by** (object): *Deprecated*. Use `merge_user` instead.
                - **user** (object): Permissions of the user requested for the merge request (e.g., `can_merge`).
                - **approvals_before_merge** (integer): *Deprecated*. Number of approvals required before merge.

                **Branch & Merge Status**
                - **source_branch** (string): Name of the source branch.
                - **target_branch** (string): Name of the target branch.
                - **source_project_id** (integer): ID of the source project.
                - **target_project_id** (integer): ID of the target project.
                - **sha** (string): SHA of the head commit in the source branch.
                - **merge_commit_sha** (string): SHA of the merge request commit (null until merged).
                - **squash_commit_sha** (string): SHA of the squash commit (empty until merged).
                - **has_conflicts** (boolean): If true, the merge request has conflicts.
                - **detailed_merge_status** (string): Detailed status of mergeability.
                - **merge_status** (string): *Deprecated*. Status of the merge request. Use `detailed_merge_status`.
                - **merge_error** (string): Error message shown when a merge fails.
                - **squash** (boolean): If true, squash commits when merging.
                - **squash_on_merge** (boolean): If true, commits are squashed on merge.
                - **should_remove_source_branch** (boolean): If true, source branch is removed after merge.
                - **force_remove_source_branch** (boolean): If true, project settings force branch deletion.
                - **allow_collaboration** (boolean): If true, allows collaboration from members who can merge to the target branch (for forks).
                - **allow_maintainer_to_push** (boolean): *Deprecated*. Use `allow_collaboration` instead.
                - **diff_refs** (object): References of the base, head, and start SHAs.
                - **diverged_commits_count** (integer): Number of commits source branch is behind target branch (if requested).
                - **rebase_in_progress** (boolean): Whether a rebase operation is currently in progress (if requested).

                **Time & Activity**
                - **created_at** (datetime): Timestamp of when the MR was created.
                - **updated_at** (datetime): Timestamp of when the MR was last updated.
                - **merged_at** (datetime): Timestamp of when the MR merged.
                - **closed_at** (datetime): Timestamp of when the MR was closed.
                - **latest_build_started_at** (datetime): Timestamp of when the latest build started.
                - **latest_build_finished_at** (datetime): Timestamp of when the latest build finished.
                - **first_deployed_to_production_at** (datetime): Timestamp of first deployment completion.
                - **merge_after** (datetime): Timestamp after which the MR can be merged (GitLab 17.8+).
                - **prepared_at** (datetime): Timestamp of when the MR was prepared.
                - **upvotes** (integer): Number of upvotes.
                - **downvotes** (integer): Number of downvotes.
                - **user_notes_count** (integer): Number of user comments.
                - **changes_count** (string): The number of changes made (as a string, or "1000+").

                **Workflow & CI/CD**
                - **milestone** (object): Information about the assigned milestone.
                - **labels** (array): Array of labels assigned to the merge request.
                - **pipeline** (object): *Deprecated*. Pipeline running on the branch HEAD. Use `head_pipeline`.
                - **head_pipeline** (object): Pipeline that runs on the HEAD commit of the source branch.
                - **merge_when_pipeline_succeeds** (boolean): If true, the MR is set to auto-merge.
                - **blocking_discussions_resolved** (boolean): If true, all required discussions are resolved.
                - **discussion_locked** (boolean): If true, discussions are locked.
                - **time_stats** (object): Time tracking stats.
                - **task_completion_status** (object): Completion status of tasks (count and completed_count).
                - **first_contribution** (boolean): If true, the author’s first contribution to this project.

            - On failure: A structured error dictionary with details about the error.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters)
    api_params = {
        'include_diverged_commits_count': include_diverged_commits_count,
        'include_rebase_in_progress': include_rebase_in_progress,
        'render_html': render_html,
    }

    # Filter out None values
    params = {k: v for k, v in api_params.items() if v is not None}

    # Log the attempt
    print(f"\n[GET SINGLE MERGE REQUEST] Attempting to retrieve MR !{merge_request_iid} for project {project_id}.")

    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GET SINGLE MERGE REQUEST] Successfully retrieved MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET SINGLE MERGE REQUEST] Error retrieving merge request: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET SINGLE MERGE REQUEST] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_participants(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    Get single merge request participants
    Get a list of all users who have participated in a specific merge request (author, assignees, commenters, etc.).

    GET /projects/:id/merge_requests/:merge_request_iid/participants

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of user objects (dictionaries), where each object contains:
                - **id** (integer): The unique ID of the participant.
                - **name** (string): Display name of the participant.
                - **username** (string): Username of the participant.
                - **state** (string): Current state of the user account (e.g., 'active').
                - **avatar_url** (string): Full URL to the user's avatar image.
                - **web_url** (string): Full URL to the user's profile page.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/participants"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR PARTICIPANTS] Attempting to retrieve participants for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR PARTICIPANTS] Successfully retrieved participants for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR PARTICIPANTS] Error retrieving participants: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR PARTICIPANTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_reviewers(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    Get single merge request reviewers
    Get a list of all users who are explicitly assigned as reviewers for a specific merge request.

    GET /projects/:id/merge_requests/:merge_request_iid/reviewers

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of reviewer objects (dictionaries), where each object contains:
                - **user** (object): The user object for the reviewer (id, name, username, state, etc.).
                - **state** (string): The current state of the review ('unreviewed', 'reviewed', 'requested_changes').
                - **created_at** (datetime): Timestamp of when the reviewer was added.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/reviewers"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR REVIEWERS] Attempting to retrieve reviewers for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR REVIEWERS] Successfully retrieved reviewers for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR REVIEWERS] Error retrieving reviewers: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR REVIEWERS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_commits(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    Get single merge request commits
    Get a list of commits associated with a single merge request.

    GET /projects/:id/merge_requests/:merge_request_iid/commits

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of commit objects (dictionaries), where each object contains:
                - **id** (string): Full SHA ID of the commit.
                - **short_id** (string): Short SHA ID of the commit.
                - **title** (string): Commit title.
                - **message** (string): Full commit message.
                - **author_name** (string): Commit author's name.
                - **author_email** (string): Commit author's email address.
                - **authored_date** (datetime): Commit authored date (identical to `created_at`).
                - **committer_name** (string): Name of the committer.
                - **committer_email** (string): Email address of the committer.
                - **committed_date** (datetime): Commit date.
                - **created_at** (datetime): Identical to the `committed_date` field.
                - **parent_ids** (array): IDs of the parent commits.
                - **trailers** (object): Git trailers parsed for the commit (last value only for duplicates).
                - **extended_trailers** (object): All Git trailers parsed for the commit.
                - **web_url** (string): Web URL of the merge request (commit link).
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/commits"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR COMMITS] Attempting to retrieve commits for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR COMMITS] Successfully retrieved commits for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR COMMITS] Error retrieving commits: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR COMMITS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_dependencies(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    Get merge request dependencies
    Shows information about the merge request dependencies that must be resolved before merging.

    GET /projects/:id/merge_requests/:merge_request_iid/blocks

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of merge request dependency objects (dictionaries), where each object contains:
                - **id** (integer): The ID of the block relationship object.
                - **blocking_merge_request** (object): Full details of the merge request that is blocking the current MR. This field is omitted if the user does not have access to the blocking merge request.
                - **blocked_merge_request** (object): Full details of the merge request being blocked (the MR specified by `merge_request_iid`).
                - **project_id** (integer): ID of the project containing the merge request.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/blocks"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR DEPENDENCIES] Attempting to retrieve dependencies for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR DEPENDENCIES] Successfully retrieved dependencies for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR DEPENDENCIES] Error retrieving dependencies: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR DEPENDENCIES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_gitlab_merge_request_dependency(
    project_id: Union[int, str],
    merge_request_iid: int,
    block_id: int
) -> Union[Dict, None]:
    """
    Delete a merge request dependency
    Deletes a dependency relationship (block) for a merge request.

    DELETE /projects/:id/merge_requests/:merge_request_iid/blocks/:block_id

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project owned by the authenticated user. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request whose dependency is being removed. (Required)
        block_id (int): The ID of the block relationship to delete. This ID is returned by `list_gitlab_merge_request_dependencies`. (Required)

    Returns:
        Union[Dict, None]:
            - On success (204 No Content): Returns None, indicating successful deletion.
            - On failure: A structured error dictionary with details (e.g., 403 Forbidden, 404 Not Found).

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/blocks/{block_id}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[DELETE MR DEPENDENCY] Attempting to delete block ID {block_id} for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the DELETE request
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (204 No Content):
        if response.status_code == 204:
            print(f"[DELETE MR DEPENDENCY] Successfully deleted block ID {block_id} for MR !{merge_request_iid}.")
            return None
        else:
            # Should not happen if raise_for_status() passes, but as a safeguard:
            return {"status": "Success", "message": f"Dependency deleted, received unexpected status code {response.status_code}"}


    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[DELETE MR DEPENDENCY] Error deleting dependency: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[DELETE MR DEPENDENCY] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_merge_request_dependency(
    project_id: Union[int, str],
    merge_request_iid: int,
    blocking_merge_request_id: int
) -> Union[Dict, Dict]:
    """
    Create a merge request dependency
    Sets a merge request (`blocking_merge_request_id`) to block the current merge request (`merge_request_iid`).

    POST /projects/:id/merge_requests/:merge_request_iid/blocks

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project owned by the authenticated user. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request to be blocked. (Required)
        blocking_merge_request_id (int): The internal ID (IID) of the merge request that will block the current one. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the new dependency/block object, which typically includes the full merge request objects for both the blocking and blocked MRs.
            - On failure: A structured error dictionary with details (e.g., 400 Bad Request, 403 Forbidden, 409 Conflict).

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/blocks"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters or Data)
    # Using 'params' for query parameters as shown in the example
    params = {
        'blocking_merge_request_id': blocking_merge_request_id
    }

    # Log the attempt
    print(f"\n[CREATE MR DEPENDENCY] Attempting to set MR !{blocking_merge_request_id} as a blocker for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (201 Created): Return the structured JSON content
        print(f"[CREATE MR DEPENDENCY] Successfully created block relationship: MR !{blocking_merge_request_id} now blocks MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[CREATE MR DEPENDENCY] Error creating dependency: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[CREATE MR DEPENDENCY] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_blockees(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    Get merge request blocked MRs
    Shows information about the merge requests that are blocked by the current merge request.

    GET /projects/:id/merge_requests/:merge_request_iid/blockees

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request that is doing the blocking. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of merge request dependency objects (dictionaries), where each object contains:
                - **id** (integer): The ID of the block relationship object.
                - **blocking_merge_request** (object): Full details of the merge request that is doing the blocking (the MR specified by `merge_request_iid`).
                - **blocked_merge_request** (object): Full details of the merge request being blocked.
                - **project_id** (integer): ID of the project containing the merge request.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/blockees"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR BLOCKEES] Attempting to retrieve merge requests blocked by MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR BLOCKEES] Successfully retrieved blockees for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR BLOCKEES] Error retrieving blockees: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR BLOCKEES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_diffs(
    project_id: Union[int, str],
    merge_request_iid: int,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    unidiff: Optional[bool] = None
) -> Union[List[Dict], Dict]:
    """
    List merge request diffs
    List diffs of the files changed in a merge request, with per-file details. This endpoint is subject to Merge requests diff limits.

    GET /projects/:id/merge_requests/:merge_request_iid/diffs

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        page (Optional[int]): The page of results to return. Defaults to 1.
        per_page (Optional[int]): The number of results per page. Defaults to 20.
        unidiff (Optional[bool]): If true, present diffs in the unified diff format. Default is False. (Introduced in GitLab 16.5)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of diff objects (dictionaries), where each object contains:
                - **old_path** (string): Old path of the file.
                - **new_path** (string): New path of the file.
                - **a_mode** (string): Old file mode.
                - **b_mode** (string): New file mode.
                - **diff** (string): Diff representation of the changes made to the file.
                - **collapsed** (boolean): If true, file diffs are excluded but can be fetched on request.
                - **too_large** (boolean): If true, file diffs are excluded and cannot be retrieved.
                - **new_file** (boolean): If true, file has been added.
                - **renamed_file** (boolean): If true, file has been renamed.
                - **deleted_file** (boolean): If true, file has been removed.
                - **generated_file** (boolean): If true, file is marked as generated.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/diffs"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters)
    api_params = {
        'page': page,
        'per_page': per_page,
        'unidiff': unidiff,
    }

    # Filter out None values
    params = {k: v for k, v in api_params.items() if v is not None}

    # Log the attempt
    print(f"\n[GET MR DIFFS] Attempting to retrieve diffs for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GET MR DIFFS] Successfully retrieved diffs for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR DIFFS] Error retrieving diffs: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR DIFFS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_request_raw_diffs(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[str, Dict]:
    """
    Show merge request raw diffs
    Show the raw diffs of the files changed in a merge request, suitable for programmatic use.

    GET /projects/:id/merge_requests/:merge_request_iid/raw_diffs

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[str, Dict]:
            - On success (200 OK): A raw string containing the unified diff output.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/raw_diffs"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR RAW DIFFS] Attempting to retrieve raw diffs for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the raw text content
        print(f"[GET MR RAW DIFFS] Successfully retrieved raw diffs for MR !{merge_request_iid}.")
        return response.text

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR RAW DIFFS] Error retrieving raw diffs: HTTP Error {e.response.status_code}")
        # Raw diffs endpoint might not return JSON on error, so attempt to return text if JSON decode fails
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR RAW DIFFS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_pipelines(
    project_id: Union[int, str],
    merge_request_iid: int,
    page: Optional[int] = None,
    per_page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List merge request pipelines
    Get a list of pipelines associated with a specific merge request.

    GET /projects/:id/merge_requests/:merge_request_iid/pipelines

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        page (Optional[int]): The page of results to return.
        per_page (Optional[int]): The number of results per page.

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of pipeline objects (dictionaries), where each object typically contains:
                - **id** (integer): The unique ID of the pipeline.
                - **sha** (string): The SHA of the commit the pipeline ran on.
                - **ref** (string): The Git reference (branch/tag) of the pipeline.
                - **status** (string): The current status of the pipeline (e.g., 'success', 'failed', 'running', 'pending').
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/pipelines"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Query Parameters)
    api_params = {
        'page': page,
        'per_page': per_page
    }

    # Filter out None values
    params = {k: v for k, v in api_params.items() if v is not None}

    # Log the attempt
    print(f"\n[LIST MR PIPELINES] Attempting to retrieve pipelines for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[LIST MR PIPELINES] Successfully retrieved pipelines for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST MR PIPELINES] Error retrieving pipelines: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[LIST MR PIPELINES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_merge_request_pipeline(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Create merge request pipeline
    Create a new pipeline for a merge request. This can be a detached merge request pipeline or a merged results pipeline.
    Note: The .gitlab-ci.yml must be configured with 'only: [merge_requests]' for jobs to be created.

    POST /projects/:id/merge_requests/:merge_request_iid/pipelines

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary containing details of the newly created pipeline, including:
                - **id** (integer): Unique ID of the new pipeline.
                - **sha** (string): Commit SHA the pipeline is running on.
                - **status** (string): Current status (e.g., 'pending').
                - **web_url** (string): Web URL to view the pipeline.
                - **detailed_status** (object): Full object detailing the pipeline status.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/pipelines"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[CREATE MR PIPELINE] Attempting to create a new pipeline for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request (no body or params needed as per docs)
        response = requests.post(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (201 Created): Return the structured JSON content
        print(f"[CREATE MR PIPELINE] Successfully created a new pipeline for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[CREATE MR PIPELINE] Error creating pipeline: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[CREATE MR PIPELINE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_merge_request(
    project_id: Union[int, str],
    source_branch: str,
    target_branch: str,
    title: str,
    description: Optional[str] = None,
    target_project_id: Optional[int] = None,
    assignee_ids: Optional[List[int]] = None,
    reviewer_ids: Optional[List[int]] = None,
    labels: Optional[str] = None,
    milestone_id: Optional[int] = None,
    remove_source_branch: Optional[bool] = None,
    squash: Optional[bool] = None,
    allow_collaboration: Optional[bool] = None,
    merge_after: Optional[str] = None,
    approvals_before_merge: Optional[int] = None,
    assignee_id: Optional[int] = None,
    allow_maintainer_to_push: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Create MR
    Creates a new merge request in a project.

    POST /projects/:id/merge_requests

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        source_branch (str): The source branch name. (Required)
        target_branch (str): The target branch name. (Required)
        title (str): Title of the merge request. (Required)
        description (Optional[str]): Description of the merge request (limited to 1,048,576 characters).
        target_project_id (Optional[int]): Numeric ID of the target project (required for cross-project MRs).
        assignee_ids (Optional[List[int]]): The ID of the users to assign the MR to. Set to 0 or empty to unassign all.
        reviewer_ids (Optional[List[int]]): The ID of the users added as a reviewer. Set to 0 or empty to remove reviewers.
        labels (Optional[str]): Labels for the MR, as a comma-separated list (e.g., 'bug,feature'). Creates new labels if they don't exist.
        milestone_id (Optional[int]): The global ID of a milestone to assign.
        remove_source_branch (Optional[bool]): If true, the source branch will be removed when merging.
        squash (Optional[bool]): If true, squash all commits into a single commit on merge. Project settings may override this.
        allow_collaboration (Optional[bool]): Allow commits from members who can merge to the target branch. Alias for `allow_maintainer_to_push`.
        merge_after (Optional[str]): Date after which the merge request can be merged (ISO 8601 format or similar datetime string).
        approvals_before_merge (Optional[int]): *Deprecated in GitLab 16.0*. Number of approvals required before merge.
        assignee_id (Optional[int]): *Deprecated*. Use `assignee_ids` instead.
        allow_maintainer_to_push (Optional[bool]): *Deprecated*. Use `allow_collaboration` instead.

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary (object) containing the detailed information for the newly created merge request, including its `id`, `iid`, `web_url`, and initial status.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Data)
    # Note: GitLab API typically accepts list parameters like assignee_ids as array in JSON body or repeated query params
    # Using JSON body for better structure, as it's a POST request
    data = {
        'source_branch': source_branch,
        'target_branch': target_branch,
        'title': title,
        'description': description,
        'target_project_id': target_project_id,
        'assignee_ids': assignee_ids,
        'reviewer_ids': reviewer_ids,
        'labels': labels,
        'milestone_id': milestone_id,
        'remove_source_branch': remove_source_branch,
        'squash': squash,
        'allow_collaboration': allow_collaboration,
        'merge_after': merge_after,
        'approvals_before_merge': approvals_before_merge,
        # deprecated fields passed only if explicitly provided to avoid unintended effects
        'assignee_id': assignee_id,
        'allow_maintainer_to_push': allow_maintainer_to_push
    }

    # Filter out None values. Note: empty lists/strings should be kept if that's the user's intent (e.g., to unassign).
    # Since None means 'don't send', we filter it.
    payload = {k: v for k, v in data.items() if v is not None}

    # Log the attempt
    print(f"\n[CREATE MR] Attempting to create new MR: '{title}' from '{source_branch}' to '{target_branch}' in project {project_id}.")

    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (201 Created): Return the structured JSON content
        print(f"[CREATE MR] Successfully created MR: {title}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[CREATE MR] Error creating merge request: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[CREATE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    target_branch: Optional[str] = None,
    state_event: Optional[str] = None,
    assignee_ids: Optional[List[int]] = None,
    reviewer_ids: Optional[List[int]] = None,
    add_labels: Optional[str] = None,
    remove_labels: Optional[str] = None,
    labels: Optional[str] = None,
    milestone_id: Optional[int] = None,
    remove_source_branch: Optional[bool] = None,
    squash: Optional[bool] = None,
    discussion_locked: Optional[bool] = None,
    allow_collaboration: Optional[bool] = None,
    merge_after: Optional[str] = None,
    assignee_id: Optional[int] = None,
    allow_maintainer_to_push: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Update MR
    Updates an existing merge request, allowing changes to its target branch, title, description, state (close/reopen), labels, assignees, and more.
    You must include at least one non-required attribute to update.

    PUT /projects/:id/merge_requests/:merge_request_iid

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request to update. (Required)
        title (Optional[str]): New title of the merge request.
        description (Optional[str]): New description of the merge request. Limited to 1,048,576 characters.
        target_branch (Optional[str]): New target branch.
        state_event (Optional[str]): New state event to perform ('close' or 'reopen').
        assignee_ids (Optional[List[int]]): The ID of the users to assign the merge request to. Set to 0 or an empty list to unassign all.
        reviewer_ids (Optional[List[int]]): The ID of the users set as a reviewer. Set to 0 or an empty list to unset all.
        add_labels (Optional[str]): Comma-separated label names to add to a merge request. Creates new labels if they don't exist.
        remove_labels (Optional[str]): Comma-separated label names to remove from a merge request.
        labels (Optional[str]): Comma-separated label names for a merge request. This **replaces** all existing labels. Set to an empty string ('') to unassign all.
        milestone_id (Optional[int]): The global ID of a milestone to assign. Set to 0 to unassign the milestone.
        remove_source_branch (Optional[bool]): Flag indicating if the source branch should be removed when merging.
        squash (Optional[bool]): If true, squash all commits into a single commit on merge.
        discussion_locked (Optional[bool]): Flag indicating if the merge request’s discussion is locked.
        allow_collaboration (Optional[bool]): Allow commits from members who can merge to the target branch.
        merge_after (Optional[str]): Date after which the merge request can be merged (e.g., "YYYY-MM-DDTHH:MM:SSZ").
        assignee_id (Optional[int]): *Deprecated*. Use `assignee_ids` instead.
        allow_maintainer_to_push (Optional[bool]): *Deprecated*. Alias of `allow_collaboration`.

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary (object) containing the updated, detailed information for the merge request.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Data)
    data = {
        'title': title,
        'description': description,
        'target_branch': target_branch,
        'state_event': state_event,
        'assignee_ids': assignee_ids,
        'reviewer_ids': reviewer_ids,
        'add_labels': add_labels,
        'remove_labels': remove_labels,
        'labels': labels,
        'milestone_id': milestone_id,
        'remove_source_branch': remove_source_branch,
        'squash': squash,
        'discussion_locked': discussion_locked,
        'allow_collaboration': allow_collaboration,
        'merge_after': merge_after,
        'assignee_id': assignee_id,
        'allow_maintainer_to_push': allow_maintainer_to_push
    }

    # Filter out None values. Note: empty strings/lists (like labels='') are valid updates and should be kept.
    payload = {k: v for k, v in data.items() if v is not None}

    if not payload:
        return {"error": "Update failed: Must provide at least one field to update (e.g., title, description, state_event)."}

    # Log the attempt
    print(f"\n[UPDATE MR] Attempting to update MR !{merge_request_iid} in project {project_id} with changes: {list(payload.keys())}.")

    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (200 OK): Return the structured JSON content
        print(f"[UPDATE MR] Successfully updated MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[UPDATE MR] Error updating merge request: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[UPDATE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[None, Dict]:
    """
    Delete a merge request
    Deletes the merge request in question. This operation is restricted to administrators and project owners.

    DELETE /projects/:id/merge_requests/:merge_request_iid

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request to delete. (Required)

    Returns:
        Union[None, Dict]:
            - On success (204 No Content): Returns None, indicating successful deletion.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[DELETE MR] Attempting to delete MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the DELETE request
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (204 No Content):
        if response.status_code == 204:
            print(f"[DELETE MR] Successfully deleted MR !{merge_request_iid}.")
            return None
        else:
            # Should not happen if raise_for_status() passes, but as a safeguard:
            return {"status": "Success", "message": f"Merge request deleted, received unexpected status code {response.status_code}"}

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[DELETE MR] Error deleting merge request: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[DELETE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def merge_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int,
    auto_merge: Optional[bool] = None,
    merge_commit_message: Optional[str] = None,
    sha: Optional[str] = None,
    should_remove_source_branch: Optional[bool] = None,
    squash_commit_message: Optional[str] = None,
    squash: Optional[bool] = None,
    merge_when_pipeline_succeeds: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Merge a merge request
    Accept and merge changes submitted with a merge request.

    PUT /projects/:id/merge_requests/:merge_request_iid/merge

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        auto_merge (Optional[bool]): If true, the merge request merges when the pipeline succeeds (replaces `merge_when_pipeline_succeeds`).
        merge_commit_message (Optional[str]): Custom message for the merge commit.
        sha (Optional[str]): If present, this SHA must match the HEAD of the source branch, otherwise the merge fails (e.g., to prevent accidental merges).
        should_remove_source_branch (Optional[bool]): If true, removes the source branch after merging.
        squash_commit_message (Optional[str]): Custom message for the squash commit (only used if `squash` is true).
        squash (Optional[bool]): If true, squashes all commits into a single commit on merge.
        merge_when_pipeline_succeeds (Optional[bool]): *Deprecated in GitLab 17.11*. Use `auto_merge` instead.

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary (object) containing the updated, merged merge request details.
            - On failure: A structured error dictionary with specific details, including common HTTP error codes (401, 405, 409, 422).

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/merge"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Data)
    data = {
        'auto_merge': auto_merge,
        'merge_commit_message': merge_commit_message,
        'sha': sha,
        'should_remove_source_branch': should_remove_source_branch,
        'squash_commit_message': squash_commit_message,
        'squash': squash,
        'merge_when_pipeline_succeeds': merge_when_pipeline_succeeds # Deprecated, but included for compatibility
    }

    # Filter out None values
    payload = {k: v for k, v in data.items() if v is not None}

    # Log the attempt
    print(f"\n[MERGE MR] Attempting to merge MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (200 OK): Return the structured JSON content
        print(f"[MERGE MR] Successfully merged MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[MERGE MR] Error merging merge request: HTTP Error {e.response.status_code}")
        # Note: Merging errors are often returned with specific JSON bodies, check for that
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[MERGE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_request_merge_ref(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Merge to default merge ref path
    Merges the changes between the merge request source and target branches into the special Git ref:
    `refs/merge-requests/:iid/merge` in the target project repository, if possible.
    This action creates a temporary ref representing the result of a merge, without actually merging the MR.
    The response returns the HEAD commit ID of the resulting merge ref.

    GET /projects/:id/merge_requests/:merge_request_iid/merge_ref

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the commit ID of the merge ref:
                - **commit_id** (string): The SHA of the HEAD commit of the `refs/merge-requests/:iid/merge` ref.
            - On failure: A structured error dictionary with details. Specific failures include a 400 status if the MR has conflicts or the merge ref cannot be updated.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/merge_ref"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR MERGE REF] Attempting to retrieve merge ref commit ID for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR MERGE REF] Successfully retrieved merge ref commit ID for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR MERGE REF] Error retrieving merge ref: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR MERGE REF] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def cancel_gitlab_merge_when_pipeline_succeeds(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Cancel merge when pipeline succeeds
    Cancels the automatic merge previously set on a merge request (often referred to as 'Auto Merge' or MWPS).

    POST /projects/:id/merge_requests/:merge_request_iid/cancel_merge_when_pipeline_succeeds

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary (object) containing the updated merge request details. The `merge_when_pipeline_succeeds` field in the response will be `false`.
            - On failure: A structured error dictionary with details. Specific failures include a 406 status if the merge request is closed.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/cancel_merge_when_pipeline_succeeds"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[CANCEL MWPS] Attempting to cancel automatic merge for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (201 Created): Return the structured JSON content
        print(f"[CANCEL MWPS] Successfully cancelled automatic merge for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[CANCEL MWPS] Error cancelling automatic merge: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[CANCEL MWPS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def rebase_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int,
    skip_ci: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Rebase a merge request
    Automatically rebase the source branch of the merge request against its target branch.
    This operation is asynchronous; the response indicates if the rebase was successfully enqueued.

    PUT /projects/:id/merge_requests/:merge_request_iid/rebase

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        skip_ci (Optional[bool]): Set to true to skip creating a CI pipeline for the rebase.

    Returns:
        Union[Dict, Dict]:
            - On successful enqueue (202 Accepted): A dictionary indicating the rebase is in progress:
                - **rebase_in_progress** (bool): Will be `true`.
            - On failure: A structured error dictionary with details. Specific failures include 403 (permission issues or branch protection) and 409 (failed to enqueue).

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/rebase"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Data)
    data = {
        'skip_ci': skip_ci
    }

    # Filter out None values
    payload = {k: v for k, v in data.items() if v is not None}

    # Log the attempt
    print(f"\n[REBASE MR] Attempting to rebase MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (202 Accepted): Return the structured JSON content
        print(f"[REBASE MR] Successfully enqueued rebase for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[REBASE MR] Error rebasing merge request: HTTP Error {e.response.status_code}")
        # Rebase API may return a JSON error even on bad status codes
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[REBASE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_issues_that_close_on_merge(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    List issues that close on merge
    Get a list of all issues that would be automatically closed by merging the provided merge request.
    The response format depends on whether the project uses the internal GitLab issue tracker or an external one (e.g., Jira).

    GET /projects/:id/merge_requests/:merge_request_iid/closes_issues

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of issue objects (dictionaries). For GitLab issues, this includes full issue details. For external trackers (like Jira), this includes simpler objects with 'id' (e.g., 'PROJECT-123') and 'title'.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/closes_issues"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[LIST CLOSING ISSUES] Attempting to retrieve issues that close on merge for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[LIST CLOSING ISSUES] Successfully retrieved list of issues closed by merging MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST CLOSING ISSUES] Error retrieving closing issues: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[LIST CLOSING ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_merge_request_related_issues(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    List issues related to the merge request
    Get a list of all issues that are logically related to the merge request, based on references found in the MR's title, description, commit messages, comments, and discussions.
    The response format depends on whether the project uses the internal GitLab issue tracker or an external one (e.g., Jira).

    GET /projects/:id/merge_requests/:merge_request_iid/related_issues

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of issue objects (dictionaries). For GitLab issues, this includes full issue details. For external trackers (like Jira), this includes simpler objects with 'id' (e.g., 'PROJECT-123') and 'title'.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/related_issues"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[LIST RELATED ISSUES] Attempting to retrieve related issues for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[LIST RELATED ISSUES] Successfully retrieved list of related issues for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST RELATED ISSUES] Error retrieving related issues: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[LIST RELATED ISSUES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def subscribe_to_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Subscribe to a merge request
    Subscribes the authenticated user to a merge request to receive notifications about activity.

    POST /projects/:id/merge_requests/:merge_request_iid/subscribe

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On successful subscription (200 OK): A dictionary (object) containing the full merge request details, with the 'subscribed' field set to true.
            - On already subscribed (304 Not Modified): A dictionary indicating no change was made.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/subscribe"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[SUBSCRIBE MR] Attempting to subscribe to MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        # We don't use raise_for_status() immediately because 304 is a successful, expected response here
        status_code = response.status_code

        # 4. Handle Success (200 or 304)
        if status_code == 200:
            print(f"[SUBSCRIBE MR] Successfully subscribed to MR !{merge_request_iid}.")
            return response.json()
        elif status_code == 304:
            print(f"[SUBSCRIBE MR] User is already subscribed to MR !{merge_request_iid} (HTTP 304 Not Modified).")
            return {"status": "Not Modified", "message": "User is already subscribed to this merge request."}
        else:
            # Re-raise for other bad status codes
            response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[SUBSCRIBE MR] Error subscribing to merge request: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[SUBSCRIBE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def unsubscribe_from_gitlab_merge_request(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Unsubscribe from a merge request
    Unsubscribes the authenticated user from a merge request to stop receiving notifications about its activity.

    POST /projects/:id/merge_requests/:merge_request_iid/unsubscribe

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On successful unsubscription (200 OK): A dictionary (object) containing the full merge request details, with the 'subscribed' field set to false.
            - On already unsubscribed (304 Not Modified): A dictionary indicating no change was made.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/unsubscribe"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[UNSUBSCRIBE MR] Attempting to unsubscribe from MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        # We don't use raise_for_status() immediately because 304 is a successful, expected response here
        status_code = response.status_code

        # 4. Handle Success (200 or 304)
        if status_code == 200:
            print(f"[UNSUBSCRIBE MR] Successfully unsubscribed from MR !{merge_request_iid}.")
            return response.json()
        elif status_code == 304:
            print(f"[UNSUBSCRIBE MR] User is already unsubscribed from MR !{merge_request_iid} (HTTP 304 Not Modified).")
            return {"status": "Not Modified", "message": "User is already unsubscribed from this merge request."}
        else:
            # Re-raise for other bad status codes
            response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[UNSUBSCRIBE MR] Error unsubscribing from merge request: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[UNSUBSCRIBE MR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_merge_request_todo(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Create a to-do item
    Manually creates a to-do item for the authenticated user on a merge request.

    POST /projects/:id/merge_requests/:merge_request_iid/todo

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary (object) containing the details of the newly created to-do item.
            - On item already exists (304 Not Modified): A dictionary indicating that a to-do item for this MR already exists for the user.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx), other than 304.
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/todo"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[CREATE MR TODO] Attempting to create a to-do item for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        status_code = response.status_code

        # 4. Handle Success (201) or Already Exists (304)
        if status_code == 201:
            print(f"[CREATE MR TODO] Successfully created a to-do item for MR !{merge_request_iid}.")
            return response.json()
        elif status_code == 304:
            print(f"[CREATE MR TODO] To-do item already exists for MR !{merge_request_iid} (HTTP 304 Not Modified).")
            # Although the body is usually empty on 304, it might contain information in some cases.
            try:
                return {"status": "Not Modified", "message": "To-do item already exists.", "details": response.json()}
            except json.JSONDecodeError:
                return {"status": "Not Modified", "message": "To-do item already exists."}
        else:
            # Raise for any other status codes (4xx, 5xx)
            response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[CREATE MR TODO] Error creating to-do item: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[CREATE MR TODO] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_request_diff_versions(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[List[Dict], Dict]:
    """
    Get merge request diff versions
    Get a list of all diff versions for a merge request. Each version represents a state of the MR at a specific point in time (usually a new commit to the source branch).

    GET /projects/:id/merge_requests/:merge_request_iid/versions

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success (200 OK): A list of diff version objects (dictionaries), each detailing the commits (head, base, start SHAs) associated with that version.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/versions"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR VERSIONS] Attempting to retrieve diff versions for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR VERSIONS] Successfully retrieved diff versions for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR VERSIONS] Error retrieving diff versions: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR VERSIONS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_single_merge_request_diff_version(
    project_id: Union[int, str],
    merge_request_iid: int,
    version_id: int,
    unidiff: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Get a single merge request diff version
    Retrieves a specific diff version for a merge request, including commit history and file differences for that version.

    GET /projects/:id/merge_requests/:merge_request_iid/versions/:version_id

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        version_id (int): The ID of the specific merge request diff version to retrieve. (Required)
        unidiff (Optional[bool]): If true, presents diffs in the unified diff format. Default is false.

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary (object) containing the details of the specified diff version, including commits and file diffs.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/versions/{version_id}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if unidiff is not None:
        params['unidiff'] = unidiff

    # Log the attempt
    print(f"\n[GET MR DIFF VERSION] Attempting to retrieve diff version {version_id} for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GET MR DIFF VERSION] Successfully retrieved diff version {version_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET MR DIFF VERSION] Error retrieving diff version: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR DIFF VERSION] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def set_gitlab_merge_request_time_estimate(
    project_id: Union[int, str],
    merge_request_iid: int,
    duration: str
) -> Union[Dict, Dict]:
    """
    Set a time estimate for a merge request
    Sets an estimated time of work for this merge request.

    POST /projects/:id/merge_requests/:merge_request_iid/time_estimate

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        duration (str): The estimated duration in human format, such as '3h30m', '1d', '2w'. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the updated time tracking statistics for the MR.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/time_estimate"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Data) - Duration must be passed as a query parameter or form data
    params = {'duration': duration}

    # Log the attempt
    print(f"\n[SET MR TIME ESTIMATE] Attempting to set time estimate of '{duration}' for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the POST request
        # Using data=None and params for query parameters as per the curl example structure
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status()

        # 5. Handle Success: Return the structured JSON content
        print(f"[SET MR TIME ESTIMATE] Successfully set time estimate for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[SET MR TIME ESTIMATE] Error setting time estimate: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[SET MR TIME ESTIMATE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def reset_gitlab_merge_request_time_estimate(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Reset the time estimate for a merge request
    Resets the estimated time for this merge request to 0 seconds.

    POST /projects/:id/merge_requests/:merge_request_iid/reset_time_estimate

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the updated time tracking statistics for the MR, with 'time_estimate' reset to 0.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/reset_time_estimate"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[RESET MR TIME ESTIMATE] Attempting to reset time estimate for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request (no body/params needed)
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()

        # 4. Handle Success: Return the structured JSON content
        print(f"[RESET MR TIME ESTIMATE] Successfully reset time estimate for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[RESET MR TIME ESTIMATE] Error resetting time estimate: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[RESET MR TIME ESTIMATE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def add_gitlab_merge_request_spent_time(
    project_id: Union[int, str],
    merge_request_iid: int,
    duration: str,
    summary: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Add spent time for a merge request
    Adds spent time for this merge request. The time is added to the total_time_spent.

    POST /projects/:id/merge_requests/:merge_request_iid/add_spent_time

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)
        duration (str): The duration in human format, such as '3h30m', '1h', '30m'. (Required)
        summary (Optional[str]): A summary of how the time was spent.

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the updated time tracking statistics for the MR.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/add_spent_time"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (Data)
    params = {'duration': duration}
    if summary is not None:
        params['summary'] = summary

    # Log the attempt
    print(f"\n[ADD MR SPENT TIME] Attempting to add spent time of '{duration}' for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status()

        # 5. Handle Success: Return the structured JSON content
        print(f"[ADD MR SPENT TIME] Successfully added spent time for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[ADD MR SPENT TIME] Error adding spent time: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[ADD MR SPENT TIME] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def reset_gitlab_merge_request_spent_time(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Reset spent time for a merge request
    Resets the total spent time for this merge request to 0 seconds.

    POST /projects/:id/merge_requests/:merge_request_iid/reset_spent_time

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the updated time tracking statistics for the MR, with 'total_time_spent' reset to 0.
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/reset_spent_time"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[RESET MR SPENT TIME] Attempting to reset spent time for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the POST request (no body/params needed)
        response = requests.post(api_url, headers=headers)
        response.raise_for_status()

        # 4. Handle Success: Return the structured JSON content
        print(f"[RESET MR SPENT TIME] Successfully reset spent time for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[RESET MR SPENT TIME] Error resetting spent time: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[RESET MR SPENT TIME] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_request_time_stats(
    project_id: Union[int, str],
    merge_request_iid: int
) -> Union[Dict, Dict]:
    """
    Get time tracking stats
    Retrieves the time tracking statistics (time estimate and total spent time) for a merge request.

    GET /projects/:id/merge_requests/:merge_request_iid/time_stats

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        merge_request_iid (int): The internal ID (IID) of the merge request. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (200 OK): A dictionary containing the time tracking statistics:
                - **human_time_estimate** (str/null)
                - **human_total_time_spent** (str/null)
                - **time_estimate** (integer) - in seconds
                - **total_time_spent** (integer) - in seconds
            - On failure: A structured error dictionary with details.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/merge_requests/{merge_request_iid}/time_stats"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # Log the attempt
    print(f"\n[GET MR TIME STATS] Attempting to retrieve time tracking stats for MR !{merge_request_iid} in project {project_id}.")

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET MR TIME STATS] Successfully retrieved time tracking stats for MR !{merge_request_iid}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[GET MR TIME STATS] Error retrieving time stats: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET MR TIME STATS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}