import requests
import json
from typing import Dict, Union, List
from ..config import get_gitlab_api, get_gitlab_token, mcp

@mcp.tool()
def gitlab_list_branches(
    project_id: Union[int, str],
    regex: str = None,
    search: str = None
) -> Union[List[Dict], Dict]:
    """
    Retrieve the list of branches in a GitLab repository using:
        GET /projects/:id/repository/branches

    This function provides branch metadata sorted alphabetically by name. 
    Supports both regular expression (regex) filtering and simple search 
    queries for branch discovery.

    Args:
        project_id (Union[int, str]): Project ID or URL-encoded path of the repository. (Required)
        regex (str, optional): Filter branches whose names match a RE2-compatible 
                               regular expression. Cannot be combined with `search`.
        search (str, optional): Filter branches containing the given string. Supports 
                                `^term` (starts with) and `term$` (ends with).

    Returns:
        Union[List[Dict], Dict]: 
            - On success: A list of branch objects with metadata (name, commit info, etc.).
            - On failure: A structured error dictionary.

    Raises:
        httpx.HTTPError: If the GitLab API request fails.
    """
    
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/branches"
    print(f"\n[GITLAB LIST BRANCHES] Listing branches for project {project_id}.")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 3. Construct Query Parameters
    params = {}
    
    # Only one of regex or search can be used
    if regex:
        params['regex'] = regex
        print(f"Filtering by regex: '{regex}'")
    elif search:
        params['search'] = search
        print(f"Filtering by search string: '{search}'")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success
        print("[GITLAB LIST BRANCHES] Branches retrieved successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST BRANCHES] Error retrieving branches: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST BRANCHES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def gitlab_get_single_branch(
    project_id: Union[int, str],
    branch: str
) -> Union[Dict, Dict]:
    """
    Retrieve details of a single branch in a GitLab repository using:
        GET /projects/:id/repository/branches/:branch

    This function returns metadata about a branch, including its commit info, 
    protection status, and merge availability.

    Args:
        gitlab_url (str): Base URL of the GitLab server (e.g., 'https://gitlab.com'). (Required)
        private_token (str): Personal or project access token with repository read permissions. (Required)
        project_id (Union[int, str]): Numeric project ID or URL-encoded project path. (Required)
        branch (str): URL-encoded branch name to fetch (e.g., 'main' or 'feature%2Fapi-refactor'). (Required)

    Returns:
        Dict:
            - On success: A dictionary describing the branch (fields: name, merged, protected, 
              default, developers_can_push, developers_can_merge, commit metadata, etc.).
            - On failure: A structured error dictionary.

    Raises:
        httpx.HTTPError: If the GitLab API request fails.
    """
    
    # 1. Construct the API URL (the branch name is a path parameter)
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/branches/{branch}"
    print(f"\n[GITLAB GET SINGLE BRANCH] Retrieving branch '{branch}' for project {project_id}.")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # No query parameters needed for this endpoint

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success
        print("[GITLAB GET SINGLE BRANCH] Branch details retrieved successfully.")
        # The API returns a single dictionary object for a single branch
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project/branch doesn't exist or permissions issue)
        print(f"[GITLAB GET SINGLE BRANCH] Error retrieving branch: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB GET SINGLE BRANCH] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def gitlab_create_branch(
    project_id: Union[int, str],
    branch_name: str,
    ref_source: str
) -> Union[Dict, Dict]:
    """
    Create a new branch in a GitLab project repository.

    API Endpoint:
        POST /projects/:id/repository/branches

    Description:
        Creates a new branch from a given source reference. The source reference can be
        another branch or a specific commit SHA. On success, returns details of the newly
        created branch.

    Args:
        project_id (int | str): The ID or URL-encoded path of the GitLab project.
        branch_name (str): The name of the new branch to create.
        ref_source (str): The source branch name or commit SHA to branch from.

    Returns:
        dict: On success (HTTP 201), returns the branch details including name, commit, 
            and protection status.
        dict: On failure, returns an error object with 'error' and 'message' keys.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/branches"
    print(f"\n[GITLAB CREATE BRANCH] Creating new branch '{branch_name}' from ref '{ref_source}' in project {project_id}.")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 3. Construct Query Parameters (GitLab API often accepts parameters via query string for this POST endpoint)
    params = {
        'branch': branch_name,
        'ref': ref_source
    }

    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (201 Created)
        print("[GITLAB CREATE BRANCH] Branch created successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 400 Bad Request if branch already exists or name is invalid, 404/403 for permissions)
        print(f"[GITLAB CREATE BRANCH] Error creating branch: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB CREATE BRANCH] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def gitlab_delete_branch(
    project_id: Union[int, str],
    branch_name: str
) -> Union[Dict, str]:
    """
    Delete a branch from a GitLab project repository.

    Description:
        Permanently removes a branch from the repository. The default branch and 
        protected branches cannot be deleted. On success, the API returns an 
        HTTP 204 (No Content) response.

    Args:
        project_id (int | str): The ID or URL-encoded path of the GitLab project.
        branch_name (str): The name of the branch to delete (must be URL-encoded).

    Returns:
        str: On success (HTTP 204), returns a confirmation message such as 
            "Branch deleted successfully."
        dict: On failure, returns an error object containing details like 
            {'error': '...', 'message': '...'}.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/branches/{branch_name}"
    print(f"\n[GITLAB DELETE BRANCH] Attempting to delete branch '{branch_name}' from project {project_id}.")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    try:
        # 3. Make the DELETE request
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (204 No Content)
        if response.status_code == 204:
            success_message = f"[GITLAB DELETE BRANCH] Branch '{branch_name}' deleted successfully (HTTP 204 No Content)."
            print(success_message)
            return success_message
        
        # Fallback for unexpected success codes, although 204 is expected
        return {"warning": f"Branch deletion returned unexpected status code {response.status_code}.", "text": response.text}

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 400 if protected/default, 404 if branch/project not found)
        print(f"[GITLAB DELETE BRANCH] Error deleting branch: HTTP Error {e.response.status_code}")
        try:
            # Attempt to parse JSON error details
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Handle cases where the response is plain text (e.g., often with 400 errors)
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB DELETE BRANCH] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}