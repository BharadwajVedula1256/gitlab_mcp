import requests
import json
from typing import Dict, Union, List
from ..config import get_gitlab_api, get_gitlab_token, mcp

@mcp.tool()
def gitlab_global_search(
    scope: str,
    search_query: str,
    confidential: bool = None,
    order_by: str = None,
    sort: str = None,
    state: str = None
) -> Union[List[Dict], Dict]:
    """
    Search across a GitLab instance globally within a specified scope.

    Use this tool whenever the user asks to:
    - Find projects, issues, merge requests, commits, or blobs matching a query.
    - Optionally filter results by confidentiality, state, or order.

    Parameters:
    - scope (string): Scope to search in. Options: "projects", "issues", "merge_requests", "blobs", "commits". Example: "issues".
    - search_query (string): The search query string. Example: "bug fix".
    - confidential (boolean, optional): Filter by confidentiality (only for 'issues'). Example: True.
    - order_by (string, optional): Field to order results by. Currently only "created_at" is supported.
    - sort (string, optional): Order direction: "asc" or "desc".
    - state (string, optional): Filter by state (only for 'issues' or 'merge_requests'). Example: "opened".

    Returns:
    - A list of dictionaries representing the search results on success.
    - Returns an error dictionary if the search fails.
    """
    # 1. Construct the API URL for global search
    api_url = f"{get_gitlab_api()}/search"
    print(f"\n[GITLAB SEARCH] Performing global search for scope '{scope}'.")

    # 2. Construct Headers (Authentication is required for search API)
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 3. Construct Query Parameters
    params = {
        'scope': scope,
        'search': search_query,
    }

    # Add optional parameters
    # confidential is only relevant for 'issues' scope
    if confidential is not None:
        params['confidential'] = confidential
    if order_by:
        params['order_by'] = order_by
    if sort:
        params['sort'] = sort
    # state is only relevant for 'issues' and 'merge_requests' scopes
    if state:
        params['state'] = state

    print(f"Search Query: '{search_query}'")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the list of search results
        print("[GITLAB SEARCH] Search completed successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 401 Unauthorized, 403 Forbidden)
        print(f"[GITLAB SEARCH] Error performing search: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB SEARCH] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def gitlab_search_within_group(
    group_id: Union[int, str],
    scope: str,
    search_query: str,
    confidential: bool = None,
    order_by: str = None,
    sort: str = None,
    state: str = None
) -> Union[List[Dict], Dict]:
    """
    Search within a specific GitLab group in a specified scope.

    Use this tool whenever the user asks to:
    - Find projects, issues, merge requests, commits, or blobs within a specific group.
    - Optionally filter results by confidentiality, state, or order.

    Parameters:
    - group_id (int or string): The GitLab group’s ID or path. Example: "74952730" or "my-group/my-project".
    - scope (string): Scope to search in. Options: "issues", "merge_requests", "projects", "blobs", "commits". Example: "issues".
    - search_query (string): The search query string. Example: "login bug".
    - confidential (boolean, optional): Filter by confidentiality (only for 'issues'). Example: True.
    - order_by (string, optional): Field to order results by. Currently only "created_at" is supported.
    - sort (string, optional): Order direction: "asc" or "desc".
    - state (string, optional): Filter by state (only for 'issues' or 'merge_requests'). Example: "opened".

    Returns:
    - A list of dictionaries representing the search results on success.
    - Returns an error dictionary if the search fails.
    """
    # 1. Construct the API URL for group search
    api_url = f"{get_gitlab_api()}/groups/{group_id}/search"
    print(f"\n[GITLAB GROUP SEARCH] Performing search in group {group_id} for scope '{scope}'.")

    # 2. Construct Headers (Authentication is required)
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 3. Construct Query Parameters
    params = {
        'scope': scope,
        'search': search_query,
    }

    # Add optional parameters
    if confidential is not None:
        params['confidential'] = confidential
    if order_by:
        params['order_by'] = order_by
    if sort:
        params['sort'] = sort
    if state:
        params['state'] = state

    print(f"Search Query: '{search_query}'")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the list of search results
        print("[GITLAB GROUP SEARCH] Search completed successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found if group is private and user isn't a member)
        print(f"[GITLAB GROUP SEARCH] Error performing search: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB GROUP SEARCH] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def gitlab_search_within_project(
    project_id: Union[int, str],
    scope: str,
    search_query: str,
    confidential: bool = None,
    ref: str = None,
    order_by: str = None,
    sort: str = None,
    state: str = None
) -> Union[List[Dict], Dict]:
    """
    Search within a specific GitLab project in a specified scope.

    Use this tool whenever the user asks to:
    - Find blobs, commits, issues, merge requests, milestones, notes, wiki blobs, or users within a project.
    - Optionally filter results by branch/tag, confidentiality, state, or order.

    Parameters:
    - project_id (int or string): The GitLab project’s ID or path. Example: "74952730" or "my-group/my-project".
    - scope (string): Scope to search in. Options: "blobs", "commits", "issues", "merge_requests", "milestones", "notes", "users", "wiki_blobs". Example: "issues".
    - search_query (string): The search query string. Example: "login bug".
    - confidential (boolean, optional): Filter by confidentiality (only for 'issues'). Example: True.
    - ref (string, optional): Branch or tag to search on (only for 'blobs', 'commits', 'wiki_blobs'). Example: "develop".
    - order_by (string, optional): Field to order results by. Currently only "created_at" is supported.
    - sort (string, optional): Order direction: "asc" or "desc".
    - state (string, optional): Filter by state (only for 'issues' or 'merge_requests'). Example: "opened".

    Returns:
    - A list of dictionaries representing the search results on success.
    - Returns an error dictionary if the search fails.
    """
    # 1. Construct the API URL for project search
    api_url = f"{get_gitlab_api()}/projects/{project_id}/search"
    print(f"\n[GITLAB PROJECT SEARCH] Performing search in project {project_id} for scope '{scope}'.")

    # 2. Construct Headers (Authentication is required)
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 3. Construct Query Parameters
    params = {
        'scope': scope,
        'search': search_query,
    }

    # Add optional parameters
    if confidential is not None:
        params['confidential'] = confidential
    if ref:
        params['ref'] = ref
    if order_by:
        params['order_by'] = order_by
    if sort:
        params['sort'] = sort
    if state:
        params['state'] = state

    print(f"Search Query: '{search_query}'")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the list of search results
        print("[GITLAB PROJECT SEARCH] Search completed successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found if project is private and user isn't a member)
        print(f"[GITLAB PROJECT SEARCH] Error performing search: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB PROJECT SEARCH] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}