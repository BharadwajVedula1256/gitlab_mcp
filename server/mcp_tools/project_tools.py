from typing import Optional, List, Union, Dict, Iterable
import requests
import json
from ..config import mcp, get_gitlab_api, get_gitlab_token
import httpx

@mcp.tool
def get_single_project(
    project_id: Union[int, str],
    license: Optional[bool] = False,
    statistics: Optional[bool] = False,
    with_custom_attributes: Optional[bool] = False
) -> Union[Dict, Dict]:
    """
    Retrieves detailed information about a specific GitLab project, including metadata, license, 
    statistics, and custom attributes (depending on permissions and visibility).

    This function leverages the `GET /projects/:id` API endpoint.  
    Public projects can be accessed without authentication, while private ones require 
    a valid access token.

    Args:
        project_id (Union[int, str]): The unique project identifier or its URL-encoded path. (Required)
        license (Optional[bool]): If True, includes project license information. Defaults to False.
        statistics (Optional[bool]): If True, includes repository and storage statistics. 
                                    Requires at least the Reporter role. Defaults to False.
        with_custom_attributes (Optional[bool]): If True, includes any admin-defined custom attributes. Defaults to False.

    Returns:
        Union[Dict, Dict]: 
            - On success: A dictionary containing the project’s metadata, configuration, and statistics.  
            - On failure: A dictionary describing the error response.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}"
    print(f"\n[GITLAB GET SINGLE PROJECT] Retrieving project {project_id}.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {}
    if license:
        params['license'] = license
    if statistics:
        params['statistics'] = statistics
    if with_custom_attributes:
        params['with_custom_attributes'] = with_custom_attributes
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB GET SINGLE PROJECT] Project {project_id} retrieved successfully.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB GET SINGLE PROJECT] Error retrieving project: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB GET SINGLE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool
def list_projects(
    user_id: Union[int, str] = None,
    archived: bool = None,
    id_after: int = None,
    id_before: int = None,
    imported: bool = None,
    include_hidden: bool = None,
    include_pending_delete: bool = None,
    last_activity_after: str = None,
    last_activity_before: str = None,
    membership: bool = None,
    min_access_level: int = None,
    order_by: str = None,
    owned: bool = None,
    repository_checksum_failed: bool = None,
    repository_storage: str = None,
    search: str = None,
    search_namespaces: bool = None,
    simple: bool = None,
    starred: bool = None,
    statistics: bool = None,
    topic: str = None,
    topic_id: int = None,
    updated_after: str = None,
    updated_before: str = None,
    visibility: str = None,
    wiki_checksum_failed: bool = None,
    with_custom_attributes: bool = None,
    with_issues_enabled: bool = None,
    with_merge_requests_enabled: bool = None,
    with_programming_language: str = None,
    marked_for_deletion_on: str = None,
    active: bool = None
) -> Union[List[Dict], Dict]:
    """
    Retrieves a comprehensive list of GitLab projects visible to the authenticated user.  
    This endpoint supports extensive filtering, sorting, and access control options, enabling fine-grained 
    queries across all projects the user can access. When accessed anonymously, only public projects 
    (with limited fields) are returned.

    Leverages the `GET /projects` API endpoint.

    Args:
        user_id (Union[int, str]): If provided, lists projects owned by the specified user ID or username.
        archived (Optional[bool]): Filter projects by archived status.  
        id_after (Optional[int]): Return only projects with IDs greater than this value.  
        id_before (Optional[int]): Return only projects with IDs smaller than this value.  
        imported (Optional[bool]): Include only projects imported from external systems by the current user.  
        include_hidden (Optional[bool]): Include hidden projects (admin-only).  
        include_pending_delete (Optional[bool]): Include projects pending deletion (admin-only).  
        last_activity_after (Optional[str]): Include projects active after a given timestamp (ISO 8601).  
        last_activity_before (Optional[str]): Include projects active before a given timestamp (ISO 8601).  
        membership (Optional[bool]): Limit to projects where the current user is a member.  
        min_access_level (Optional[int]): Filter by minimum required access level.  
        order_by (Optional[str]): Field to order results by (e.g., `"created_at"`, `"updated_at"`, `"star_count"`).  
        owned (Optional[bool]): Return only projects owned by the authenticated user.  
        repository_checksum_failed (Optional[bool]): Filter by projects with repository checksum failures (Premium/Ultimate).  
        repository_storage (Optional[str]): Limit results to projects stored in a specific repository storage (admin-only).  
        search (Optional[str]): Search by project name, path, or description (case-insensitive substring match).  
        search_namespaces (Optional[bool]): Include ancestor namespaces in the search match. Defaults to `False`.  
        simple (Optional[bool]): Return simplified project representations (applies automatically to unauthenticated requests).  
        starred (Optional[bool]): Filter by projects starred by the user.  
        statistics (Optional[bool]): Include project-level statistics (requires Reporter access).  
        topic (Optional[str]): Comma-separated list of topic names to match.  
        topic_id (Optional[int]): Filter projects by a specific topic ID.  
        updated_after (Optional[str]): Include projects updated after the given timestamp (ISO 8601).  
        updated_before (Optional[str]): Include projects updated before the given timestamp (ISO 8601).  
        visibility (Optional[str]): Filter by project visibility — one of `"public"`, `"internal"`, `"private"`.  
        wiki_checksum_failed (Optional[bool]): Filter projects with wiki checksum failures (Premium/Ultimate).  
        with_custom_attributes (Optional[bool]): Include administrator-defined custom attributes (admin-only).  
        with_issues_enabled (Optional[bool]): Filter projects that have issues enabled.  
        with_merge_requests_enabled (Optional[bool]): Filter projects that have merge requests enabled.  
        with_programming_language (Optional[str]): Filter by projects written in a specific programming language.  
        marked_for_deletion_on (Optional[str]): Filter by projects marked for deletion on a given date (GitLab 17.1+).  
        active (Optional[bool]): Limit to active projects (not archived or pending deletion).  

    Returns:
        Union[List[Dict], Dict]:  
            - On success: A list of project metadata dictionaries matching the query filters.  
            - On failure: A dictionary describing the error (status code, message, etc.).
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/users/{user_id}/projects"
    print(f"\n[GITLAB LIST PROJECTS] Listing projects with specified filters.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {}
    
    # Add all parameters that have non-None values
    if archived is not None:
        params['archived'] = archived
    if id_after is not None:
        params['id_after'] = id_after
    if id_before is not None:
        params['id_before'] = id_before
    if imported is not None:
        params['imported'] = imported
    if include_hidden is not None:
        params['include_hidden'] = include_hidden
    if include_pending_delete is not None:
        params['include_pending_delete'] = include_pending_delete
    if last_activity_after is not None:
        params['last_activity_after'] = last_activity_after
    if last_activity_before is not None:
        params['last_activity_before'] = last_activity_before
    if membership is not None:
        params['membership'] = membership
    if min_access_level is not None:
        params['min_access_level'] = min_access_level
    if order_by is not None:
        params['order_by'] = order_by
    if owned is not None:
        params['owned'] = owned
    if repository_checksum_failed is not None:
        params['repository_checksum_failed'] = repository_checksum_failed
    if repository_storage is not None:
        params['repository_storage'] = repository_storage
    if search is not None:
        params['search'] = search
    if search_namespaces is not None:
        params['search_namespaces'] = search_namespaces
    if simple is not None:
        params['simple'] = simple
    if starred is not None:
        params['starred'] = starred
    if statistics is not None:
        params['statistics'] = statistics
    if topic is not None:
        params['topic'] = topic
    if topic_id is not None:
        params['topic_id'] = topic_id
    if updated_after is not None:
        params['updated_after'] = updated_after
    if updated_before is not None:
        params['updated_before'] = updated_before
    if visibility is not None:
        params['visibility'] = visibility
    if wiki_checksum_failed is not None:
        params['wiki_checksum_failed'] = wiki_checksum_failed
    if with_custom_attributes is not None:
        params['with_custom_attributes'] = with_custom_attributes
    if with_issues_enabled is not None:
        params['with_issues_enabled'] = with_issues_enabled
    if with_merge_requests_enabled is not None:
        params['with_merge_requests_enabled'] = with_merge_requests_enabled
    if with_programming_language is not None:
        params['with_programming_language'] = with_programming_language
    if marked_for_deletion_on is not None:
        params['marked_for_deletion_on'] = marked_for_deletion_on
    if active is not None:
        params['active'] = active
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST PROJECTS] Projects retrieved successfully.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST PROJECTS] Error retrieving projects: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST PROJECTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_user_contributed_projects(
    user_id: Union[int, str],
    order_by: Optional[str] = None,
    simple: Optional[bool] = None,
    sort: Optional[str] = None
) -> Union[List[Dict], Dict]:
    """
    Retrieves a list of GitLab projects that a specific user has contributed to within the past year.  
    A “contribution” includes actions such as commits, merge requests, or issues created by the user.  
    This endpoint is particularly useful for analyzing user activity or generating contribution reports.

    Leverages the `GET /users/:user_id/contributed_projects` API endpoint.

    Args:
        user_id (Union[int, str]):  
            The unique ID or username of the user whose contributed projects should be listed. (Required)
        order_by (Optional[str]):  
            The field used to order results. Options include `"id"`, `"name"`, `"path"`, `"created_at"`,  
            `"updated_at"`, `"star_count"`, and `"last_activity_at"`. Defaults to `"created_at"`.
        simple (Optional[bool]):  
            If `True`, returns only limited fields for each project.  
            Note: Without authentication, this flag has no effect — only simple fields are returned by default.
        sort (Optional[str]):  
            Sort order for results — either `"asc"` (ascending) or `"desc"` (descending).  
            Defaults to `"desc"`.

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of project dictionaries where the user has made contributions.  
            - On failure: A dictionary containing error details such as message and status code.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/users/{user_id}/contributed_projects"
    print(f"\n[GITLAB LIST USER CONTRIBUTED PROJECTS] Requesting URL: {api_url}")
    print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Params: {order_by=}, {simple=}, {sort=}")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }
    print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Headers: {headers}")
    
    # 3. Construct Query Parameters
    params = {}
    
    # Add all parameters that have non-None values
    if order_by is not None:
        params['order_by'] = order_by
    if simple is not None:
        params['simple'] = simple
    if sort is not None:
        params['sort'] = sort
    
    try:
        # 4. Make the GET request
        print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Making GET request to {api_url}")
        response = requests.get(api_url, headers=headers, params=params)
        print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Response status: {response.status_code}")
        
        # Check if response is empty
        if response.content == b'':
            print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Empty response received from API")
            return []
            
        # Check for successful response
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Projects contributed to by user {user_id} retrieved successfully.")
        
        # Try to parse JSON response
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Found {len(data)} contributed projects")
                return data
            else:
                print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Unexpected response format: {type(data)}")
                return {"error": "Unexpected response format", "response": data}
        except json.JSONDecodeError:
            print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Failed to parse JSON response")
            return {"error": "Failed to parse JSON response", "raw_response": response.text}
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if user doesn't exist or permissions issue)
        print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] Error retrieving contributed projects for user {user_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST USER CONTRIBUTED PROJECTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def search_projects_by_name(
    search: str,
    order_by: Optional[str] = None,
    sort: Optional[str] = None
) -> Union[List[Dict], Dict]:
    """
    Performs a semantic search for GitLab projects by name that are visible to the authenticated user.  
    When called without authentication, it returns only publicly accessible projects.  
    Ideal for discovery, auto-complete, or LLM-based project retrieval tasks where name-based matching is needed.

    Leverages the `GET /projects` endpoint with the `search` parameter.

    Args:
        search (str):  
            The substring or keyword to match against project names. (Required)  
            For example, `"mcp"` will return all projects containing “mcp” in their names.
        order_by (Optional[str]):  
            Defines the sorting field.  
            Valid values: `"id"`, `"name"`, `"created_at"`, `"star_count"`, `"last_activity_at"`.  
            Defaults to `"created_at"`.
        sort (Optional[str]):  
            Sort direction for the results — `"asc"` (ascending) or `"desc"` (descending).  
            Defaults to `"desc"`.

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of matching project dictionaries, each containing metadata like `id`, `name`, `path`, and `visibility`.  
            - On failure: An error dictionary containing details like `message` and `status_code`.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects"
    print(f"\n[GITLAB SEARCH PROJECTS BY NAME] Searching for projects with name containing '{search}'.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {
        'search': search
    }
    
    # Add optional parameters if they are provided
    if order_by is not None:
        params['order_by'] = order_by
    if sort is not None:
        params['sort'] = sort
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB SEARCH PROJECTS BY NAME] Found {len(response.json())} projects matching '{search}'.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB SEARCH PROJECTS BY NAME] Error searching for projects: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB SEARCH PROJECTS BY NAME] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_project_users(
    project_id: Union[int, str],
    search: Optional[str] = None,
    skip_users: Optional[List[int]] = None
) -> Union[List[Dict], Dict]:
    """
    Retrieves the list of users who have access to a specific GitLab project.  
    This includes users with any level of membership or access rights.  
    Supports filtering and exclusion to refine results, making it suitable for  
    permission management, access audits, or contextual LLM reasoning over project collaborators.

    Uses the `GET /projects/:id/users` endpoint.

    Args:
        project_id (Union[int, str]):  
            The unique ID or URL-encoded path of the GitLab project. (Required)  
            Example: `12345` or `'my-namespace%2Fexample-project'`.
        search (Optional[str]):  
            Filters users by a partial match on their username, name, or email.  
            Useful for narrowing results when searching for a specific contributor.
        skip_users (Optional[List[int]]):  
            A list of user IDs to exclude from the results.  
            Helps avoid redundant or system-level accounts in automated pipelines.

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of user objects (each containing details like `id`, `username`, `name`, `state`, and `access_level`).  
            - On failure: An error dictionary describing the issue (`message`, `status_code`, etc.).
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/users"
    print(f"\n[GITLAB LIST PROJECT USERS] Retrieving users for project {project_id} with specified filters.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {}
    
    # Add optional parameters if they are provided
    if search is not None:
        params['search'] = search
    if skip_users is not None:
        # Convert list of IDs to comma-separated string
        params['skip_users'] = ','.join(map(str, skip_users))
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST PROJECT USERS] Users retrieved successfully for project {project_id}.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST PROJECT USERS] Error retrieving users for project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST PROJECT USERS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_project_groups(
    project_id: Union[int, str],
    search: Optional[str] = None,
    shared_min_access_level: Optional[int] = None,
    shared_visible_only: Optional[bool] = None,
    skip_groups: Optional[List[int]] = None,
    with_shared: Optional[bool] = None
) -> Union[List[Dict], Dict]:
    """
    Get a list of ancestor groups for this project.
    
    GET /projects/:id/groups
    
    Args:
        project_id (int or str): The ID or URL-encoded path of the project.
        search (str, optional): Search for specific groups.
        shared_min_access_level (int, optional): Limit to shared groups with at least this role (access_level).
        shared_visible_only (bool, optional): Limit to shared groups user has access to.
        skip_groups (List[int], optional): Skip the group IDs passed.
        with_shared (bool, optional): Include projects shared with this group. Default is false.
    
    Returns:
        List[Dict]: A list of group dictionaries.
        Dict: Error information if the request failed.
    """
    
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/groups"
    print(f"\n[GITLAB LIST PROJECT GROUPS] Retrieving groups for project {project_id} with specified filters.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {}
    
    # Add optional parameters if they are provided
    if search is not None:
        params['search'] = search
    if shared_min_access_level is not None:
        params['shared_min_access_level'] = shared_min_access_level
    if shared_visible_only is not None:
        params['shared_visible_only'] = shared_visible_only
    if skip_groups is not None:
        # Convert list of IDs to comma-separated string
        params['skip_groups'] = ','.join(map(str, skip_groups))
    if with_shared is not None:
        params['with_shared'] = with_shared
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST PROJECT GROUPS] Groups retrieved successfully for project {project_id}.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST PROJECT GROUPS] Error retrieving groups for project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST PROJECT GROUPS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_project_shareable_groups(
    project_id: Union[int, str],
    search: Optional[str] = None
) -> Union[List[Dict], Dict]:
    """
    Retrieves all GitLab groups that are eligible to be shared with a given project.  
    This helps identify potential collaboration groups that can be granted access  
    to the specified project based on existing permissions and visibility rules.  
    Useful for automating project-sharing workflows or recommending group access  
    within LLM-driven DevOps or CI/CD management assistants.

    Uses the `GET /projects/:id/share_locations` endpoint.

    Args:
        project_id (Union[int, str]):  
            The unique ID or URL-encoded path of the GitLab project. (Required)  
            Example: `12345` or `'research-team%2Fvision-project'`.
        search (Optional[str]):  
            A keyword to filter shareable groups by name or path.  
            Example: `'ml'` returns only groups whose names or paths contain "ml".

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of shareable group objects, each containing fields like `id`, `name`, `path`, and `visibility_level`.  
            - On failure: An error dictionary describing the issue (e.g., unauthorized access, invalid project ID).
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/share_locations"
    print(f"\n[GITLAB LIST PROJECT SHAREABLE GROUPS] Retrieving shareable groups for project {project_id} with specified filters.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {}
    
    # Add optional parameters if they are provided
    if search is not None:
        params['search'] = search
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST PROJECT SHAREABLE GROUPS] Shareable groups retrieved successfully for project {project_id}.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST PROJECT SHAREABLE GROUPS] Error retrieving shareable groups for project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST PROJECT SHAREABLE GROUPS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def list_project_invited_groups(
    project_id: Union[int, str],
    search: Optional[str] = None,
    min_access_level: Optional[int] = None,
    relation: Optional[List[str]] = None,
    with_custom_attributes: Optional[bool] = None
) -> Union[List[Dict], Dict]:
    """
    Retrieves all groups that have been invited to a specific GitLab project,  
    including both directly invited and inherited (via parent group) associations.  
    Useful for auditing project access, managing permissions, or recommending group-level  
    collaborations in automated DevOps workflows or LLM-based project management tools.

    Uses the `GET /projects/:id/invited_groups` endpoint.  
    Results are paginated, with 20 entries returned per page by default.

    Args:
        project_id (Union[int, str]):  
            The unique ID or URL-encoded path of the GitLab project. (Required)  
            Example: `12345` or `'ai-team%2Fvision-models'`.
        search (Optional[str]):  
            A search query to filter groups by name or path.  
            Example: `'cv'` returns groups with names containing "cv".
        min_access_level (Optional[int]):  
            Filters groups to include only those where the user has at least  
            the specified access level (e.g., `30` for Developer, `40` for Maintainer).
        relation (Optional[List[str]]):  
            Specifies which groups to return — `'direct'`, `'inherited'`, or both.  
            Example: `['direct']` returns only directly invited groups.
        with_custom_attributes (Optional[bool]):  
            Whether to include custom attributes for each group (admin only).

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of invited group objects containing fields such as  
            `id`, `name`, `access_level`, and `shared_from_group`.  
            - On failure: A dictionary containing error details (e.g., invalid project ID,  
            insufficient permissions).
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/invited_groups"
    print(f"\n[GITLAB LIST PROJECT INVITED GROUPS] Retrieving invited groups for project {project_id} with specified filters.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. Construct Query Parameters
    params = {}
    
    # Add optional parameters if they are provided
    if search is not None:
        params['search'] = search
    if min_access_level is not None:
        params['min_access_level'] = min_access_level
    if relation is not None:
        # Convert list to comma-separated string
        params['relation'] = ','.join(relation)
    if with_custom_attributes is not None:
        params['with_custom_attributes'] = with_custom_attributes
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST PROJECT INVITED GROUPS] Invited groups retrieved successfully for project {project_id}.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST PROJECT INVITED GROUPS] Error retrieving invited groups for project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST PROJECT INVITED GROUPS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_project_languages(
    project_id: Union[int, str]
) -> Union[Dict, Dict]:
    """
    Retrieves the programming languages used in a GitLab project along with their respective  
    usage percentages. Useful for understanding code composition, automating tech stack reports,  
    or feeding language statistics into analytics dashboards and LLM-driven project insights.

    Uses the `GET /projects/:id/languages` endpoint.

    Args:
        project_id (Union[int, str]):  
            The unique ID or URL-encoded path of the GitLab project. (Required)  
            Example: `12345` or `'ai-team%2Fvision-models'`.

    Returns:
        Union[Dict, Dict]:
            - On success: A dictionary where each key is a programming language name (e.g., `'Python'`, `'C++'`)  
            and the value is the percentage of the codebase written in that language.  
            Example: `{'Python': 72.5, 'C++': 27.5}`.
            - On failure: A dictionary containing error details (e.g., project not found, insufficient permissions).
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/languages"
    print(f"\n[GITLAB LIST PROJECT LANGUAGES] Retrieving programming languages for project {project_id}.")
    
    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }
    
    # 3. No parameters needed for this endpoint
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        # 5. Handle Success
        print(f"[GITLAB LIST PROJECT LANGUAGES] Programming languages retrieved successfully for project {project_id}.")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 if project doesn't exist or permissions issue)
        print(f"[GITLAB LIST PROJECT LANGUAGES] Error retrieving programming languages for project {project_id}: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB LIST PROJECT LANGUAGES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_project(
    # --- Required/Core Attributes (Name, Path, Location) ---
    name: Optional[str] = None,
    path: Optional[str] = None,
    namespace_id: Optional[Union[int, str]] = None,
    description: Optional[str] = None,
    visibility: str = 'public', # public, internal, private
    
    # --- Repository Initialization & Configuration ---
    initialize_with_readme: bool = False,
    default_branch: Optional[str] = None,
    import_url: Optional[str] = None,
    lfs_enabled: Optional[bool] = None,
    merge_method: Optional[str] = None, # merge, rebase_merge, ff
    remove_source_branch_after_merge: Optional[bool] = None,
    repository_object_format: Optional[str] = None,
    repository_storage: Optional[str] = None, # Administrator only
    squash_option: Optional[str] = None, # never, always, default_on, default_off
    
    # --- CI/CD Configuration ---
    auto_cancel_pending_pipelines: Optional[str] = None,
    auto_devops_deploy_strategy: Optional[str] = None, # continuous, manual, timed_incremental
    auto_devops_enabled: Optional[bool] = None,
    build_git_strategy: Optional[str] = None, # fetch, clone
    build_timeout: Optional[int] = None,
    ci_config_path: Optional[str] = None,
    group_runners_enabled: Optional[bool] = None,
    merge_pipelines_enabled: Optional[bool] = None,
    merge_trains_enabled: Optional[bool] = None,
    merge_trains_skip_train_allowed: Optional[bool] = None,
    mirror: Optional[bool] = None,
    mirror_trigger_builds: Optional[bool] = None,
    only_allow_merge_if_pipeline_succeeds: Optional[bool] = None,
    public_jobs: Optional[bool] = None,
    shared_runners_enabled: Optional[bool] = None,
    
    # --- Merge Request/Issue/Wiki Settings ---
    approvals_before_merge: Optional[int] = None, # Deprecated in 16.0
    autoclose_referenced_issues: Optional[bool] = None,
    only_allow_merge_if_all_discussions_are_resolved: Optional[bool] = None,
    only_allow_merge_if_all_status_checks_passed: Optional[bool] = None, # Ultimate only
    printing_merge_request_link_enabled: Optional[bool] = None,
    resolve_outdated_diff_discussions: Optional[bool] = None,
    
    # --- Metadata, Security & Templates ---
    emails_enabled: Optional[bool] = None,
    external_authorization_classification_label: Optional[str] = None, # Premium/Ultimate only
    group_with_project_templates_id: Optional[Union[int, str]] = None,
    request_access_enabled: Optional[bool] = None,
    show_default_award_emojis: Optional[bool] = None,
    template_name: Optional[str] = None,
    template_project_id: Optional[Union[int, str]] = None,
    topics: Optional[List[str]] = None,
    use_custom_template: Optional[bool] = None, # Premium/Ultimate only
    warn_about_potentially_unwanted_characters: Optional[bool] = None,
    
    # --- Project Feature Visibility Settings (Access Levels: disabled, private, enabled, public) ---
    analytics_access_level: Optional[str] = None,
    builds_access_level: Optional[str] = None, # (Deprecated) Use pipelines
    container_registry_access_level: Optional[str] = None,
    environments_access_level: Optional[str] = None,
    feature_flags_access_level: Optional[str] = None,
    forking_access_level: Optional[str] = None,
    infrastructure_access_level: Optional[str] = None,
    issues_access_level: Optional[str] = None,
    merge_requests_access_level: Optional[str] = None,
    model_experiments_access_level: Optional[str] = None,
    model_registry_access_level: Optional[str] = None,
    monitor_access_level: Optional[str] = None,
    pages_access_level: Optional[str] = None,
    package_registry_access_level: Optional[str] = None,
    releases_access_level: Optional[str] = None,
    repository_access_level: Optional[str] = None,
    requirements_access_level: Optional[str] = None,
    security_and_compliance_access_level: Optional[str] = None,
    snippets_access_level: Optional[str] = None,
    wiki_access_level: Optional[str] = None,
    
    # --- Deprecated/Legacy/Other Simple Booleans/Ints ---
    emails_disabled: Optional[bool] = None,
    issues_enabled: Optional[bool] = None,
    jobs_enabled: Optional[bool] = None,
    merge_requests_enabled: Optional[bool] = None,
    packages_enabled: Optional[bool] = None,
    public_builds: Optional[bool] = None,
    snippets_enabled: Optional[bool] = None,
    wiki_enabled: Optional[bool] = None,
    tag_list: Optional[List[str]] = None, # Deprecated in 14.0
    
) -> Union[Dict, Dict]:
    """
    Creates a new GitLab project either for the authenticated user or within a specified namespace/group.  
    Supports full configuration of repository settings, CI/CD options, merge request rules, feature visibility, 
    security, templates, and other advanced attributes.

    Uses the `POST /projects` endpoint.

    Args:
        # --- Required/Core Attributes ---
        name (str, optional): Project name. Required if `path` is not provided.
        path (str, optional): Repository path. Required if `name` is not provided.
        namespace_id (int or str, optional): ID or URL-encoded path of the namespace/group for the project.
        description (str, optional): Project description.
        visibility (str, optional): Project visibility ('private', 'internal', 'public'). Default is 'private'.

        # --- Repository Initialization & Configuration ---
        initialize_with_readme (bool, optional): Initialize repository with a README. Default False.
        default_branch (str, optional): Name of the default branch.
        import_url (str, optional): URL to import an existing repository.
        lfs_enabled (bool, optional): Enable Git LFS.
        merge_method (str, optional): Merge strategy: 'merge', 'rebase_merge', 'ff'.
        remove_source_branch_after_merge (bool, optional): Remove source branch after merge.
        repository_object_format (str, optional): Format for repository objects.
        repository_storage (str, optional): Storage location for repository (admin only).
        squash_option (str, optional): Squash commit strategy: 'never', 'always', 'default_on', 'default_off'.

        # --- CI/CD Configuration ---
        auto_cancel_pending_pipelines (str, optional): Auto-cancel pending pipelines configuration.
        auto_devops_deploy_strategy (str, optional): Auto DevOps deploy strategy: 'continuous', 'manual', 'timed_incremental'.
        auto_devops_enabled (bool, optional): Enable Auto DevOps.
        build_git_strategy (str, optional): Git strategy for builds: 'fetch', 'clone'.
        build_timeout (int, optional): Build timeout in seconds.
        ci_config_path (str, optional): Custom CI/CD configuration path.
        group_runners_enabled (bool, optional): Enable group runners.
        merge_pipelines_enabled (bool, optional): Enable merge pipelines.
        merge_trains_enabled (bool, optional): Enable merge trains.
        merge_trains_skip_train_allowed (bool, optional): Allow skipping merge trains.
        mirror (bool, optional): Enable repository mirroring.
        mirror_trigger_builds (bool, optional): Trigger builds for mirrored repositories.
        only_allow_merge_if_pipeline_succeeds (bool, optional): Only allow merge if pipeline succeeds.
        public_jobs (bool, optional): Enable public jobs.
        shared_runners_enabled (bool, optional): Enable shared runners.

        # --- Merge Request/Issue/Wiki Settings ---
        approvals_before_merge (int, optional): Deprecated in 16.0; number of approvals required.
        autoclose_referenced_issues (bool, optional): Auto-close referenced issues.
        only_allow_merge_if_all_discussions_are_resolved (bool, optional): Only allow merge if all discussions are resolved.
        only_allow_merge_if_all_status_checks_passed (bool, optional): Only allow merge if all status checks passed (Ultimate only).
        printing_merge_request_link_enabled (bool, optional): Enable printing MR link.
        resolve_outdated_diff_discussions (bool, optional): Automatically resolve outdated diff discussions.

        # --- Metadata, Security & Templates ---
        emails_enabled (bool, optional): Enable project emails.
        external_authorization_classification_label (str, optional): Premium/Ultimate only; external authorization label.
        group_with_project_templates_id (int or str, optional): Group ID for project templates.
        request_access_enabled (bool, optional): Allow users to request access.
        show_default_award_emojis (bool, optional): Show default award emojis.
        template_name (str, optional): Name of the project template.
        template_project_id (int or str, optional): Project ID of the template.
        topics (List[str], optional): List of project topics.
        use_custom_template (bool, optional): Premium/Ultimate only; use custom template.
        warn_about_potentially_unwanted_characters (bool, optional): Warn about unwanted characters in project name/path.

        # --- Project Feature Visibility Settings ---
        analytics_access_level (str, optional): Feature visibility: 'disabled', 'private', 'enabled', 'public'.
        builds_access_level (str, optional): Deprecated; use pipelines.
        container_registry_access_level (str, optional): Visibility for container registry.
        environments_access_level (str, optional): Visibility for environments.
        feature_flags_access_level (str, optional): Visibility for feature flags.
        forking_access_level (str, optional): Visibility for forking.
        infrastructure_access_level (str, optional): Visibility for infrastructure.
        issues_access_level (str, optional): Visibility for issues.
        merge_requests_access_level (str, optional): Visibility for merge requests.
        model_experiments_access_level (str, optional): Visibility for model experiments.
        model_registry_access_level (str, optional): Visibility for model registry.
        monitor_access_level (str, optional): Visibility for monitor.
        pages_access_level (str, optional): Visibility for pages.
        package_registry_access_level (str, optional): Visibility for package registry.
        releases_access_level (str, optional): Visibility for releases.
        repository_access_level (str, optional): Visibility for repository.
        requirements_access_level (str, optional): Visibility for requirements.
        security_and_compliance_access_level (str, optional): Visibility for security & compliance.
        snippets_access_level (str, optional): Visibility for snippets.
        wiki_access_level (str, optional): Visibility for wiki.

        # --- Deprecated/Legacy/Other Simple Booleans/Ints ---
        emails_disabled (bool, optional): Disable emails.
        issues_enabled (bool, optional): Enable issues.
        jobs_enabled (bool, optional): Enable jobs.
        merge_requests_enabled (bool, optional): Enable merge requests.
        packages_enabled (bool, optional): Enable packages.
        public_builds (bool, optional): Enable public builds.
        snippets_enabled (bool, optional): Enable snippets.
        wiki_enabled (bool, optional): Enable wiki.
        tag_list (List[str], optional): Deprecated in 14.0; tags for the project.

    Returns:
        Union[Dict, Dict]:
            - On success: Dictionary representing the newly created project.
            - On failure: Dictionary containing error details (e.g., validation errors, permission denied).
    """


    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects"
    print(f"\n[GITLAB CREATE PROJECT] Attempting to create project: '{name or path}'")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    # 3. Construct Payload from all explicit arguments
    payload = {
        'name': name,
        'path': path,
        'namespace_id': namespace_id,
        'description': description,
        'visibility': visibility,
        'initialize_with_readme': initialize_with_readme,
        'default_branch': default_branch,
        'import_url': import_url,
        'lfs_enabled': lfs_enabled,
        'merge_method': merge_method,
        'remove_source_branch_after_merge': remove_source_branch_after_merge,
        'repository_object_format': repository_object_format,
        'repository_storage': repository_storage,
        'squash_option': squash_option,
        'auto_cancel_pending_pipelines': auto_cancel_pending_pipelines,
        'auto_devops_deploy_strategy': auto_devops_deploy_strategy,
        'auto_devops_enabled': auto_devops_enabled,
        'build_git_strategy': build_git_strategy,
        'build_timeout': build_timeout,
        'ci_config_path': ci_config_path,
        'group_runners_enabled': group_runners_enabled,
        'merge_pipelines_enabled': merge_pipelines_enabled,
        'merge_trains_enabled': merge_trains_enabled,
        'merge_trains_skip_train_allowed': merge_trains_skip_train_allowed,
        'mirror': mirror,
        'mirror_trigger_builds': mirror_trigger_builds,
        'only_allow_merge_if_pipeline_succeeds': only_allow_merge_if_pipeline_succeeds,
        'public_jobs': public_jobs,
        'shared_runners_enabled': shared_runners_enabled,
        'approvals_before_merge': approvals_before_merge,
        'autoclose_referenced_issues': autoclose_referenced_issues,
        'only_allow_merge_if_all_discussions_are_resolved': only_allow_merge_if_all_discussions_are_resolved,
        'only_allow_merge_if_all_status_checks_passed': only_allow_merge_if_all_status_checks_passed,
        'printing_merge_request_link_enabled': printing_merge_request_link_enabled,
        'resolve_outdated_diff_discussions': resolve_outdated_diff_discussions,
        'emails_enabled': emails_enabled,
        'external_authorization_classification_label': external_authorization_classification_label,
        'group_with_project_templates_id': group_with_project_templates_id,
        'request_access_enabled': request_access_enabled,
        'show_default_award_emojis': show_default_award_emojis,
        'template_name': template_name,
        'template_project_id': template_project_id,
        'topics': topics,
        'use_custom_template': use_custom_template,
        'warn_about_potentially_unwanted_characters': warn_about_potentially_unwanted_characters,
        'analytics_access_level': analytics_access_level,
        'builds_access_level': builds_access_level,
        'container_registry_access_level': container_registry_access_level,
        'environments_access_level': environments_access_level,
        'feature_flags_access_level': feature_flags_access_level,
        'forking_access_level': forking_access_level,
        'infrastructure_access_level': infrastructure_access_level,
        'issues_access_level': issues_access_level,
        'merge_requests_access_level': merge_requests_access_level,
        'model_experiments_access_level': model_experiments_access_level,
        'model_registry_access_level': model_registry_access_level,
        'monitor_access_level': monitor_access_level,
        'pages_access_level': pages_access_level,
        'package_registry_access_level': package_registry_access_level,
        'releases_access_level': releases_access_level,
        'repository_access_level': repository_access_level,
        'requirements_access_level': requirements_access_level,
        'security_and_compliance_access_level': security_and_compliance_access_level,
        'snippets_access_level': snippets_access_level,
        'wiki_access_level': wiki_access_level,
        'emails_disabled': emails_disabled,
        'issues_enabled': issues_enabled,
        'jobs_enabled': jobs_enabled,
        'merge_requests_enabled': merge_requests_enabled,
        'packages_enabled': packages_enabled,
        'public_builds': public_builds,
        'snippets_enabled': snippets_enabled,
        'wiki_enabled': wiki_enabled,
        'tag_list': tag_list,
        # Note: 'avatar' (file upload) and 'container_expiration_policy_attributes' (nested hash)
        # are omitted as they require complex input types not easily supported by simple function arguments.
    }
    
    # Filter out None values to ensure a clean request body
    payload = {k: v for k, v in payload.items() if v is not None}

    # Validation: Ensure at least name or path is provided
    if 'name' not in payload and 'path' not in payload:
        return {"error": "Validation Error", "details": "Either 'name' or 'path' must be provided to create a project."}

    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (201 Created)
        print("[GITLAB CREATE PROJECT] Project created successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 400 Bad Request for validation failure, 403 for permissions)
        print(f"[GITLAB CREATE PROJECT] Error creating project: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB CREATE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_project_for_user(
    user_id: Union[int, str],
    
    # --- Required/Core Attributes (Name, Path, Location) ---
    name: str, # REQUIRED for this endpoint
    path: Optional[str] = None,
    namespace_id: Optional[Union[int, str]] = None,
    description: Optional[str] = None,
    visibility: str = 'private', # public, internal, private
    
    # --- Repository Initialization & Configuration ---
    initialize_with_readme: bool = False,
    default_branch: Optional[str] = None,
    import_url: Optional[str] = None,
    lfs_enabled: Optional[bool] = None,
    merge_method: Optional[str] = None, # merge, rebase_merge, ff
    remove_source_branch_after_merge: Optional[bool] = None,
    repository_object_format: Optional[str] = None,
    repository_storage: Optional[str] = None, # Administrator only
    squash_option: Optional[str] = None, # never, always, default_on, default_off
    issue_branch_template: Optional[str] = None,
    
    # --- CI/CD Configuration ---
    auto_cancel_pending_pipelines: Optional[str] = None,
    auto_devops_deploy_strategy: Optional[str] = None, # continuous, manual, timed_incremental
    auto_devops_enabled: Optional[bool] = None,
    build_git_strategy: Optional[str] = None, # fetch, clone
    build_timeout: Optional[int] = None,
    ci_config_path: Optional[str] = None,
    group_runners_enabled: Optional[bool] = None,
    merge_pipelines_enabled: Optional[bool] = None,
    # NOTE: Merge trains not listed in documentation for this endpoint, omitted for strict adherence.
    mirror: Optional[bool] = None,
    mirror_trigger_builds: Optional[bool] = None,
    only_allow_merge_if_pipeline_succeeds: Optional[bool] = None,
    public_jobs: Optional[bool] = None,
    shared_runners_enabled: Optional[bool] = None,
    
    # --- Merge Request/Issue/Wiki Settings ---
    approvals_before_merge: Optional[int] = None, # Deprecated in 16.0
    autoclose_referenced_issues: Optional[bool] = None,
    only_allow_merge_if_all_discussions_are_resolved: Optional[bool] = None,
    only_allow_merge_if_all_status_checks_passed: Optional[bool] = None, # Ultimate only
    printing_merge_request_link_enabled: Optional[bool] = None,
    resolve_outdated_diff_discussions: Optional[bool] = None,
    merge_commit_template: Optional[str] = None,
    squash_commit_template: Optional[str] = None,
    suggestion_commit_message: Optional[str] = None,
    
    # --- Metadata, Security & Templates ---
    emails_enabled: Optional[bool] = None,
    enforce_auth_checks_on_uploads: Optional[bool] = None,
    external_authorization_classification_label: Optional[str] = None, # Premium/Ultimate only
    group_with_project_templates_id: Optional[Union[int, str]] = None,
    request_access_enabled: Optional[bool] = None,
    show_default_award_emojis: Optional[bool] = None,
    template_name: Optional[str] = None,
    topics: Optional[List[str]] = None,
    use_custom_template: Optional[bool] = None, # Premium/Ultimate only
    warn_about_potentially_unwanted_characters: Optional[bool] = None,
    
    # --- Project Feature Visibility Settings (Access Levels: disabled, private, enabled, public) ---
    analytics_access_level: Optional[str] = None,
    builds_access_level: Optional[str] = None, # (Deprecated) Use pipelines
    container_registry_access_level: Optional[str] = None,
    environments_access_level: Optional[str] = None,
    feature_flags_access_level: Optional[str] = None,
    forking_access_level: Optional[str] = None,
    infrastructure_access_level: Optional[str] = None,
    issues_access_level: Optional[str] = None,
    merge_requests_access_level: Optional[str] = None,
    model_experiments_access_level: Optional[str] = None,
    model_registry_access_level: Optional[str] = None,
    monitor_access_level: Optional[str] = None,
    pages_access_level: Optional[str] = None,
    package_registry_access_level: Optional[str] = None,
    releases_access_level: Optional[str] = None,
    repository_access_level: Optional[str] = None,
    requirements_access_level: Optional[str] = None,
    security_and_compliance_access_level: Optional[str] = None,
    snippets_access_level: Optional[str] = None,
    wiki_access_level: Optional[str] = None,
    
    # --- Deprecated/Legacy/Other Simple Booleans/Ints ---
    emails_disabled: Optional[bool] = None,
    issues_enabled: Optional[bool] = None,
    jobs_enabled: Optional[bool] = None,
    merge_requests_enabled: Optional[bool] = None,
    packages_enabled: Optional[bool] = None,
    public_builds: Optional[bool] = None,
    snippets_enabled: Optional[bool] = None,
    wiki_enabled: Optional[bool] = None,
    tag_list: Optional[List[str]] = None, # Deprecated in 14.0
    
) -> Union[Dict, Dict]:
    """
    Creates a new project for a specified user in GitLab. Requires Administrator privileges.

    Endpoint: POST /projects/user/:user_id

    Args:
        user_id (Union[int, str]): ID of the user who will own the project. (Required)
        
        # --- Required/Core Attributes ---
        name (str): Name of the new project. (Required)
        path (str, optional): Repository path for the new project. Defaults to `name`.
        namespace_id (Union[int, str], optional): Namespace/group ID for the project.
        description (str, optional): Project description.
        visibility (str, optional): Visibility level ('private', 'internal', 'public'). Default: 'private'.
        
        # --- Repository Initialization & Configuration ---
        initialize_with_readme (bool, optional): Initialize repository with README. Default: False.
        default_branch (str, optional): Default branch name.
        import_url (str, optional): URL to import project from.
        lfs_enabled (bool, optional): Enable Git LFS.
        merge_method (str, optional): Merge strategy ('merge', 'rebase_merge', 'ff').
        remove_source_branch_after_merge (bool, optional): Remove source branch after merge.
        repository_object_format (str, optional): Repository object format.
        repository_storage (str, optional): Storage location for repository (Admin only).
        squash_option (str, optional): Squash commits option ('never', 'always', 'default_on', 'default_off').
        issue_branch_template (str, optional): Template for new branches from issues.
        
        # --- CI/CD Configuration ---
        auto_cancel_pending_pipelines (str, optional): Auto-cancel pipelines setting.
        auto_devops_deploy_strategy (str, optional): Auto DevOps deploy strategy ('continuous', 'manual', 'timed_incremental').
        auto_devops_enabled (bool, optional): Enable Auto DevOps.
        build_git_strategy (str, optional): Git clone strategy ('fetch', 'clone').
        build_timeout (int, optional): Build timeout in seconds.
        ci_config_path (str, optional): Path to CI configuration file.
        group_runners_enabled (bool, optional): Enable group runners.
        merge_pipelines_enabled (bool, optional): Enable merge pipelines.
        mirror (bool, optional): Enable repository mirroring.
        mirror_trigger_builds (bool, optional): Trigger builds on mirror update.
        only_allow_merge_if_pipeline_succeeds (bool, optional): Restrict merge if pipeline fails.
        public_jobs (bool, optional): Make jobs public.
        shared_runners_enabled (bool, optional): Enable shared runners.
        
        # --- Merge Request / Issue / Wiki Settings ---
        approvals_before_merge (int, optional): Number of approvals before merge (deprecated in GitLab 16.0).
        autoclose_referenced_issues (bool, optional): Automatically close referenced issues.
        only_allow_merge_if_all_discussions_are_resolved (bool, optional): Restrict merge until all discussions resolved.
        only_allow_merge_if_all_status_checks_passed (bool, optional): Restrict merge until status checks pass (Ultimate only).
        printing_merge_request_link_enabled (bool, optional): Enable merge request link in commit messages.
        resolve_outdated_diff_discussions (bool, optional): Resolve outdated diff discussions automatically.
        merge_commit_template (str, optional): Template for merge commits.
        squash_commit_template (str, optional): Template for squash commits.
        suggestion_commit_message (str, optional): Template for suggestion commits.
        
        # --- Metadata, Security & Templates ---
        emails_enabled (bool, optional): Enable project emails.
        enforce_auth_checks_on_uploads (bool, optional): Enforce authentication for uploads.
        external_authorization_classification_label (str, optional): Security label (Premium/Ultimate only).
        group_with_project_templates_id (Union[int, str], optional): Group ID for project templates.
        request_access_enabled (bool, optional): Enable request access button.
        show_default_award_emojis (bool, optional): Show default award emojis.
        template_name (str, optional): Project template name.
        topics (List[str], optional): List of project topics.
        use_custom_template (bool, optional): Enable custom template (Premium/Ultimate only).
        warn_about_potentially_unwanted_characters (bool, optional): Warn about unwanted characters.
        
        # --- Project Feature Visibility Settings ---
        analytics_access_level (str, optional): Access level for analytics.
        builds_access_level (str, optional): Access level for builds (deprecated; use pipelines).
        container_registry_access_level (str, optional): Access level for container registry.
        environments_access_level (str, optional): Access level for environments.
        feature_flags_access_level (str, optional): Access level for feature flags.
        forking_access_level (str, optional): Access level for forking.
        infrastructure_access_level (str, optional): Access level for infrastructure.
        issues_access_level (str, optional): Access level for issues.
        merge_requests_access_level (str, optional): Access level for merge requests.
        model_experiments_access_level (str, optional): Access level for model experiments.
        model_registry_access_level (str, optional): Access level for model registry.
        monitor_access_level (str, optional): Access level for monitor.
        pages_access_level (str, optional): Access level for Pages.
        package_registry_access_level (str, optional): Access level for package registry.
        releases_access_level (str, optional): Access level for releases.
        repository_access_level (str, optional): Access level for repository.
        requirements_access_level (str, optional): Access level for requirements.
        security_and_compliance_access_level (str, optional): Access level for security & compliance.
        snippets_access_level (str, optional): Access level for snippets.
        wiki_access_level (str, optional): Access level for wiki.
        
        # --- Deprecated / Legacy / Other Booleans / Ints ---
        emails_disabled (bool, optional): Disable project emails.
        issues_enabled (bool, optional): Enable issues.
        jobs_enabled (bool, optional): Enable jobs.
        merge_requests_enabled (bool, optional): Enable merge requests.
        packages_enabled (bool, optional): Enable packages.
        public_builds (bool, optional): Enable public builds.
        snippets_enabled (bool, optional): Enable snippets.
        wiki_enabled (bool, optional): Enable wiki.
        tag_list (List[str], optional): List of tags (deprecated in GitLab 14.0).

    Returns:
        Union[Dict, Dict]: Project object dictionary on success (HTTP 201), or an error dictionary on failure.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/user/{user_id}"
    print(f"\n[GITLAB CREATE PROJECT FOR USER] Attempting to create project '{name}' for user ID {user_id}")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_api(),
        'Content-Type': 'application/json'
    }

    # 3. Construct Payload from all explicit arguments
    payload = {
        'name': name,
        'path': path,
        'namespace_id': namespace_id,
        'description': description,
        'visibility': visibility,
        'initialize_with_readme': initialize_with_readme,
        'default_branch': default_branch,
        'import_url': import_url,
        'lfs_enabled': lfs_enabled,
        'merge_method': merge_method,
        'remove_source_branch_after_merge': remove_source_branch_after_merge,
        'repository_object_format': repository_object_format,
        'repository_storage': repository_storage,
        'squash_option': squash_option,
        'issue_branch_template': issue_branch_template,
        'auto_cancel_pending_pipelines': auto_cancel_pending_pipelines,
        'auto_devops_deploy_strategy': auto_devops_deploy_strategy,
        'auto_devops_enabled': auto_devops_enabled,
        'build_git_strategy': build_git_strategy,
        'build_timeout': build_timeout,
        'ci_config_path': ci_config_path,
        'group_runners_enabled': group_runners_enabled,
        'merge_pipelines_enabled': merge_pipelines_enabled,
        'mirror': mirror,
        'mirror_trigger_builds': mirror_trigger_builds,
        'only_allow_merge_if_pipeline_succeeds': only_allow_merge_if_pipeline_succeeds,
        'public_jobs': public_jobs,
        'shared_runners_enabled': shared_runners_enabled,
        'approvals_before_merge': approvals_before_merge,
        'autoclose_referenced_issues': autoclose_referenced_issues,
        'only_allow_merge_if_all_discussions_are_resolved': only_allow_merge_if_all_discussions_are_resolved,
        'only_allow_merge_if_all_status_checks_passed': only_allow_merge_if_all_status_checks_passed,
        'printing_merge_request_link_enabled': printing_merge_request_link_enabled,
        'resolve_outdated_diff_discussions': resolve_outdated_diff_discussions,
        'merge_commit_template': merge_commit_template,
        'squash_commit_template': squash_commit_template,
        'suggestion_commit_message': suggestion_commit_message,
        'emails_enabled': emails_enabled,
        'enforce_auth_checks_on_uploads': enforce_auth_checks_on_uploads,
        'external_authorization_classification_label': external_authorization_classification_label,
        'group_with_project_templates_id': group_with_project_templates_id,
        'request_access_enabled': request_access_enabled,
        'show_default_award_emojis': show_default_award_emojis,
        'template_name': template_name,
        'topics': topics,
        'use_custom_template': use_custom_template,
        'warn_about_potentially_unwanted_characters': warn_about_potentially_unwanted_characters,
        'analytics_access_level': analytics_access_level,
        'builds_access_level': builds_access_level,
        'container_registry_access_level': container_registry_access_level,
        'environments_access_level': environments_access_level,
        'feature_flags_access_level': feature_flags_access_level,
        'forking_access_level': forking_access_level,
        'infrastructure_access_level': infrastructure_access_level,
        'issues_access_level': issues_access_level,
        'merge_requests_access_level': merge_requests_access_level,
        'model_experiments_access_level': model_experiments_access_level,
        'model_registry_access_level': model_registry_access_level,
        'monitor_access_level': monitor_access_level,
        'pages_access_level': pages_access_level,
        'package_registry_access_level': package_registry_access_level,
        'releases_access_level': releases_access_level,
        'repository_access_level': repository_access_level,
        'requirements_access_level': requirements_access_level,
        'security_and_compliance_access_level': security_and_compliance_access_level,
        'snippets_access_level': snippets_access_level,
        'wiki_access_level': wiki_access_level,
        'emails_disabled': emails_disabled,
        'issues_enabled': issues_enabled,
        'jobs_enabled': jobs_enabled,
        'merge_requests_enabled': merge_requests_enabled,
        'packages_enabled': packages_enabled,
        'public_builds': public_builds,
        'snippets_enabled': snippets_enabled,
        'wiki_enabled': wiki_enabled,
        'tag_list': tag_list,
    }
    
    # Filter out None values to ensure a clean request body
    payload = {k: v for k, v in payload.items() if v is not None}

    # Validation: Ensure name is provided (as path is auto-generated if omitted)
    if 'name' not in payload or not payload['name']:
        return {"error": "Validation Error", "details": "'name' is required to create a project for a user."}

    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (201 Created)
        print(f"[GITLAB CREATE PROJECT FOR USER] Project '{name}' created successfully for user {user_id}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 400 Bad Request for validation failure, 403 for permissions/admin status)
        print(f"[GITLAB CREATE PROJECT FOR USER] Error creating project: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB CREATE PROJECT FOR USER] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def edit_project(
    project_id: Union[int, str], # ID or URL-encoded path of the project to edit
    
    # --- Required/Core Attributes (Name, Path, Location) ---
    name: Optional[str] = None,
    path: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[str] = None, # public, internal, private
    
    # --- Repository Initialization & Configuration ---
    default_branch: Optional[str] = None,
    import_url: Optional[str] = None,
    lfs_enabled: Optional[bool] = None,
    merge_method: Optional[str] = None, # merge, rebase_merge, ff
    remove_source_branch_after_merge: Optional[bool] = None,
    repository_storage: Optional[str] = None, # Administrator only
    squash_option: Optional[str] = None, # never, always, default_on, default_off
    issue_branch_template: Optional[str] = None,
    
    # --- CI/CD Configuration ---
    allow_merge_on_skipped_pipeline: Optional[bool] = None,
    allow_pipeline_trigger_approve_deployment: Optional[bool] = None, # Premium/Ultimate only
    auto_cancel_pending_pipelines: Optional[str] = None,
    auto_devops_deploy_strategy: Optional[str] = None, # continuous, manual, timed_incremental
    auto_devops_enabled: Optional[bool] = None,
    build_git_strategy: Optional[str] = None, # fetch, clone
    build_timeout: Optional[int] = None,
    ci_config_path: Optional[str] = None,
    ci_default_git_depth: Optional[int] = None,
    ci_delete_pipelines_in_seconds: Optional[int] = None,
    ci_forward_deployment_enabled: Optional[bool] = None,
    ci_forward_deployment_rollback_allowed: Optional[bool] = None,
    ci_allow_fork_pipelines_to_run_in_parent_project: Optional[bool] = None,
    ci_id_token_sub_claim_components: Optional[List[str]] = None,
    ci_separated_caches: Optional[bool] = None,
    ci_restrict_pipeline_cancellation_role: Optional[str] = None, # Premium/Ultimate only
    ci_pipeline_variables_minimum_override_role: Optional[str] = None,
    ci_push_repository_for_job_token_allowed: Optional[bool] = None,
    group_runners_enabled: Optional[bool] = None,
    merge_pipelines_enabled: Optional[bool] = None,
    merge_trains_enabled: Optional[bool] = None,
    merge_trains_skip_train_allowed: Optional[bool] = None,
    mirror: Optional[bool] = None, # Premium/Ultimate only
    mirror_overwrites_diverged_branches: Optional[bool] = None, # Premium/Ultimate only
    mirror_trigger_builds: Optional[bool] = None, # Premium/Ultimate only
    mirror_user_id: Optional[int] = None, # Admin only, Premium/Ultimate
    only_allow_merge_if_pipeline_succeeds: Optional[bool] = None,
    only_mirror_protected_branches: Optional[bool] = None, # Premium/Ultimate only
    public_jobs: Optional[bool] = None,
    shared_runners_enabled: Optional[bool] = None,
    
    # --- Merge Request/Issue/Wiki Settings ---
    approvals_before_merge: Optional[int] = None, # Deprecated in 16.0
    auto_duo_code_review_enabled: Optional[bool] = None, # Ultimate only
    autoclose_referenced_issues: Optional[bool] = None,
    issues_template: Optional[str] = None, # Premium/Ultimate only
    merge_commit_template: Optional[str] = None,
    mr_default_target_self: Optional[bool] = None,
    only_allow_merge_if_all_discussions_are_resolved: Optional[bool] = None,
    only_allow_merge_if_all_status_checks_passed: Optional[bool] = None, # Ultimate only
    prevent_merge_without_jira_issue: Optional[bool] = None, # Ultimate only
    printing_merge_request_link_enabled: Optional[bool] = None,
    resolve_outdated_diff_discussions: Optional[bool] = None,
    squash_commit_template: Optional[str] = None,
    suggestion_commit_message: Optional[str] = None,
    
    # --- Metadata, Security & Templates ---
    container_expiration_policy_attributes: Optional[Dict] = None, # Nested hash
    duo_remote_flows_enabled: Optional[bool] = None,
    emails_enabled: Optional[bool] = None,
    enforce_auth_checks_on_uploads: Optional[bool] = None,
    external_authorization_classification_label: Optional[str] = None, # Premium/Ultimate only
    group_with_project_templates_id: Optional[Union[int, str]] = None,
    keep_latest_artifact: Optional[bool] = None,
    max_artifacts_size: Optional[int] = None,
    request_access_enabled: Optional[bool] = None,
    restrict_user_defined_variables: Optional[bool] = None, # Deprecated
    service_desk_enabled: Optional[bool] = None,
    show_default_award_emojis: Optional[bool] = None,
    spp_repository_pipeline_access: Optional[bool] = None, # Ultimate only
    template_name: Optional[str] = None,
    topics: Optional[List[str]] = None,
    use_custom_template: Optional[bool] = None, # Premium/Ultimate only
    warn_about_potentially_unwanted_characters: Optional[bool] = None,
    web_based_commit_signing_enabled: Optional[bool] = None, # GitLab SaaS only
    
    # --- Project Feature Visibility Settings (Access Levels: disabled, private, enabled, public) ---
    analytics_access_level: Optional[str] = None,
    builds_access_level: Optional[str] = None, # (Deprecated) Use pipelines
    container_registry_access_level: Optional[str] = None,
    environments_access_level: Optional[str] = None,
    feature_flags_access_level: Optional[str] = None,
    forking_access_level: Optional[str] = None,
    infrastructure_access_level: Optional[str] = None,
    issues_access_level: Optional[str] = None,
    merge_requests_access_level: Optional[str] = None,
    model_experiments_access_level: Optional[str] = None,
    model_registry_access_level: Optional[str] = None,
    monitor_access_level: Optional[str] = None,
    pages_access_level: Optional[str] = None,
    package_registry_access_level: Optional[str] = None,
    releases_access_level: Optional[str] = None,
    repository_access_level: Optional[str] = None,
    requirements_access_level: Optional[str] = None,
    security_and_compliance_access_level: Optional[str] = None,
    snippets_access_level: Optional[str] = None,
    wiki_access_level: Optional[str] = None,
    
    # --- Deprecated/Legacy/Other Simple Booleans/Ints ---
    container_registry_enabled: Optional[bool] = None, # Deprecated
    emails_disabled: Optional[bool] = None, # Deprecated
    issues_enabled: Optional[bool] = None, # Deprecated
    jobs_enabled: Optional[bool] = None, # Deprecated
    merge_requests_enabled: Optional[bool] = None, # Deprecated
    packages_enabled: Optional[bool] = None, # Deprecated
    public_builds: Optional[bool] = None, # Deprecated
    snippets_enabled: Optional[bool] = None, # Deprecated
    wiki_enabled: Optional[bool] = None, # Deprecated
    tag_list: Optional[List[str]] = None, # Deprecated
    
) -> Union[Dict, Dict]:
    """
    Updates an existing GitLab project with new settings and configurations.

    Endpoint: PUT /projects/:id

    Args:
        project_id (Union[int, str]): ID or URL-encoded path of the project to update. (Required)
        
        # --- Required/Core Attributes ---
        name (str, optional): New project name.
        path (str, optional): New repository path.
        description (str, optional): Updated project description.
        visibility (str, optional): Visibility level ('private', 'internal', 'public').
        
        # --- Repository Initialization & Configuration ---
        default_branch (str, optional): New default branch name.
        import_url (str, optional): URL to import project from.
        lfs_enabled (bool, optional): Enable Git LFS.
        merge_method (str, optional): Merge strategy ('merge', 'rebase_merge', 'ff').
        remove_source_branch_after_merge (bool, optional): Remove source branch after merge.
        repository_storage (str, optional): Storage location (Admin only).
        squash_option (str, optional): Squash commits option ('never', 'always', 'default_on', 'default_off').
        issue_branch_template (str, optional): Template for new branches from issues.
        
        # --- CI/CD Configuration ---
        allow_merge_on_skipped_pipeline (bool, optional): Allow merge on skipped pipeline.
        allow_pipeline_trigger_approve_deployment (bool, optional): Premium/Ultimate only.
        auto_cancel_pending_pipelines (str, optional): Auto-cancel pipelines setting.
        auto_devops_deploy_strategy (str, optional): DevOps deploy strategy ('continuous', 'manual', 'timed_incremental').
        auto_devops_enabled (bool, optional): Enable Auto DevOps.
        build_git_strategy (str, optional): Git clone strategy ('fetch', 'clone').
        build_timeout (int, optional): Build timeout in seconds.
        ci_config_path (str, optional): Path to CI config file.
        ci_default_git_depth (int, optional): Default git depth for CI.
        ci_delete_pipelines_in_seconds (int, optional): Seconds to delete old pipelines.
        ci_forward_deployment_enabled (bool, optional): Enable forward deployment.
        ci_forward_deployment_rollback_allowed (bool, optional): Allow rollback for forward deployments.
        ci_allow_fork_pipelines_to_run_in_parent_project (bool, optional): Allow fork pipelines.
        ci_id_token_sub_claim_components (List[str], optional): ID token claim components.
        ci_separated_caches (bool, optional): Enable separated caches.
        ci_restrict_pipeline_cancellation_role (str, optional): Premium/Ultimate only.
        ci_pipeline_variables_minimum_override_role (str, optional): Minimum role to override pipeline variables.
        ci_push_repository_for_job_token_allowed (bool, optional): Allow repository push for job token.
        group_runners_enabled (bool, optional): Enable group runners.
        merge_pipelines_enabled (bool, optional): Enable merge pipelines.
        merge_trains_enabled (bool, optional): Enable merge trains.
        merge_trains_skip_train_allowed (bool, optional): Allow skipping merge train.
        mirror (bool, optional): Enable repository mirroring (Premium/Ultimate only).
        mirror_overwrites_diverged_branches (bool, optional): Mirror overwrite option (Premium/Ultimate only).
        mirror_trigger_builds (bool, optional): Trigger builds on mirror update (Premium/Ultimate only).
        mirror_user_id (int, optional): Admin only, Premium/Ultimate.
        only_allow_merge_if_pipeline_succeeds (bool, optional): Restrict merge until pipeline succeeds.
        only_mirror_protected_branches (bool, optional): Premium/Ultimate only.
        public_jobs (bool, optional): Make jobs public.
        shared_runners_enabled (bool, optional): Enable shared runners.
        
        # --- Merge Request / Issue / Wiki Settings ---
        approvals_before_merge (int, optional): Deprecated in GitLab 16.0.
        auto_duo_code_review_enabled (bool, optional): Ultimate only.
        autoclose_referenced_issues (bool, optional): Auto-close referenced issues.
        issues_template (str, optional): Premium/Ultimate only.
        merge_commit_template (str, optional): Template for merge commits.
        mr_default_target_self (bool, optional): Default merge request target.
        only_allow_merge_if_all_discussions_are_resolved (bool, optional): Restrict merge until discussions resolved.
        only_allow_merge_if_all_status_checks_passed (bool, optional): Ultimate only.
        prevent_merge_without_jira_issue (bool, optional): Ultimate only.
        printing_merge_request_link_enabled (bool, optional): Enable MR link in commits.
        resolve_outdated_diff_discussions (bool, optional): Resolve outdated diffs automatically.
        squash_commit_template (str, optional): Template for squash commits.
        suggestion_commit_message (str, optional): Template for suggestion commits.
        
        # --- Metadata, Security & Templates ---
        container_expiration_policy_attributes (Dict, optional): Nested hash for container expiration policy.
        duo_remote_flows_enabled (bool, optional): Ultimate only.
        emails_enabled (bool, optional): Enable emails.
        enforce_auth_checks_on_uploads (bool, optional): Enforce authentication for uploads.
        external_authorization_classification_label (str, optional): Premium/Ultimate only.
        group_with_project_templates_id (Union[int, str], optional): Group ID for project templates.
        keep_latest_artifact (bool, optional): Keep latest artifact.
        max_artifacts_size (int, optional): Max artifact size in MB.
        request_access_enabled (bool, optional): Enable request access button.
        restrict_user_defined_variables (bool, optional): Deprecated.
        service_desk_enabled (bool, optional): Enable service desk.
        show_default_award_emojis (bool, optional): Show default award emojis.
        spp_repository_pipeline_access (bool, optional): Ultimate only.
        template_name (str, optional): Project template name.
        topics (List[str], optional): List of project topics.
        use_custom_template (bool, optional): Premium/Ultimate only.
        warn_about_potentially_unwanted_characters (bool, optional): Warn about unwanted characters.
        web_based_commit_signing_enabled (bool, optional): GitLab SaaS only.
        
        # --- Project Feature Visibility Settings ---
        analytics_access_level (str, optional): Access level for analytics.
        builds_access_level (str, optional): Access level for builds (deprecated; use pipelines).
        container_registry_access_level (str, optional): Access level for container registry.
        environments_access_level (str, optional): Access level for environments.
        feature_flags_access_level (str, optional): Access level for feature flags.
        forking_access_level (str, optional): Access level for forking.
        infrastructure_access_level (str, optional): Access level for infrastructure.
        issues_access_level (str, optional): Access level for issues.
        merge_requests_access_level (str, optional): Access level for merge requests.
        model_experiments_access_level (str, optional): Access level for model experiments.
        model_registry_access_level (str, optional): Access level for model registry.
        monitor_access_level (str, optional): Access level for monitor.
        pages_access_level (str, optional): Access level for Pages.
        package_registry_access_level (str, optional): Access level for package registry.
        releases_access_level (str, optional): Access level for releases.
        repository_access_level (str, optional): Access level for repository.
        requirements_access_level (str, optional): Access level for requirements.
        security_and_compliance_access_level (str, optional): Access level for security & compliance.
        snippets_access_level (str, optional): Access level for snippets.
        wiki_access_level (str, optional): Access level for wiki.
        
        # --- Deprecated / Legacy / Other Booleans / Ints ---
        container_registry_enabled (bool, optional): Deprecated.
        emails_disabled (bool, optional): Deprecated.
        issues_enabled (bool, optional): Deprecated.
        jobs_enabled (bool, optional): Deprecated.
        merge_requests_enabled (bool, optional): Deprecated.
        packages_enabled (bool, optional): Deprecated.
        public_builds (bool, optional): Deprecated.
        snippets_enabled (bool, optional): Deprecated.
        wiki_enabled (bool, optional): Deprecated.
        tag_list (List[str], optional): Deprecated.
        
    Returns:
        Union[Dict, Dict]: Updated project object on success (HTTP 200) or error dictionary on failure.
    """

    # 1. Construct the API URL
    # project_id must be URL-encoded if it's a path, but requests handles simple encoding
    api_url = f"{get_gitlab_api()}/projects/{project_id}"
    print(f"\n[GITLAB EDIT PROJECT] Attempting to update project: '{project_id}'")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    # 3. Construct Payload from all explicit arguments
    payload = {
        'name': name,
        'path': path,
        'description': description,
        'visibility': visibility,
        'default_branch': default_branch,
        'import_url': import_url,
        'lfs_enabled': lfs_enabled,
        'merge_method': merge_method,
        'remove_source_branch_after_merge': remove_source_branch_after_merge,
        'repository_storage': repository_storage,
        'squash_option': squash_option,
        'issue_branch_template': issue_branch_template,
        'allow_merge_on_skipped_pipeline': allow_merge_on_skipped_pipeline,
        'allow_pipeline_trigger_approve_deployment': allow_pipeline_trigger_approve_deployment,
        'auto_cancel_pending_pipelines': auto_cancel_pending_pipelines,
        'auto_devops_deploy_strategy': auto_devops_deploy_strategy,
        'auto_devops_enabled': auto_devops_enabled,
        'build_git_strategy': build_git_strategy,
        'build_timeout': build_timeout,
        'ci_config_path': ci_config_path,
        'ci_default_git_depth': ci_default_git_depth,
        'ci_delete_pipelines_in_seconds': ci_delete_pipelines_in_seconds,
        'ci_forward_deployment_enabled': ci_forward_deployment_enabled,
        'ci_forward_deployment_rollback_allowed': ci_forward_deployment_rollback_allowed,
        'ci_allow_fork_pipelines_to_run_in_parent_project': ci_allow_fork_pipelines_to_run_in_parent_project,
        'ci_id_token_sub_claim_components': ci_id_token_sub_claim_components,
        'ci_separated_caches': ci_separated_caches,
        'ci_restrict_pipeline_cancellation_role': ci_restrict_pipeline_cancellation_role,
        'ci_pipeline_variables_minimum_override_role': ci_pipeline_variables_minimum_override_role,
        'ci_push_repository_for_job_token_allowed': ci_push_repository_for_job_token_allowed,
        'group_runners_enabled': group_runners_enabled,
        'merge_pipelines_enabled': merge_pipelines_enabled,
        'merge_trains_enabled': merge_trains_enabled,
        'merge_trains_skip_train_allowed': merge_trains_skip_train_allowed,
        'mirror': mirror,
        'mirror_overwrites_diverged_branches': mirror_overwrites_diverged_branches,
        'mirror_trigger_builds': mirror_trigger_builds,
        'mirror_user_id': mirror_user_id,
        'only_allow_merge_if_pipeline_succeeds': only_allow_merge_if_pipeline_succeeds,
        'only_mirror_protected_branches': only_mirror_protected_branches,
        'public_jobs': public_jobs,
        'shared_runners_enabled': shared_runners_enabled,
        'approvals_before_merge': approvals_before_merge,
        'auto_duo_code_review_enabled': auto_duo_code_review_enabled,
        'autoclose_referenced_issues': autoclose_referenced_issues,
        'issues_template': issues_template,
        'merge_commit_template': merge_commit_template,
        'mr_default_target_self': mr_default_target_self,
        'only_allow_merge_if_all_discussions_are_resolved': only_allow_merge_if_all_discussions_are_resolved,
        'only_allow_merge_if_all_status_checks_passed': only_allow_merge_if_all_status_checks_passed,
        'prevent_merge_without_jira_issue': prevent_merge_without_jira_issue,
        'printing_merge_request_link_enabled': printing_merge_request_link_enabled,
        'resolve_outdated_diff_discussions': resolve_outdated_diff_discussions,
        'squash_commit_template': squash_commit_template,
        'suggestion_commit_message': suggestion_commit_message,
        'container_expiration_policy_attributes': container_expiration_policy_attributes,
        'duo_remote_flows_enabled': duo_remote_flows_enabled,
        'emails_enabled': emails_enabled,
        'enforce_auth_checks_on_uploads': enforce_auth_checks_on_uploads,
        'external_authorization_classification_label': external_authorization_classification_label,
        'group_with_project_templates_id': group_with_project_templates_id,
        'keep_latest_artifact': keep_latest_artifact,
        'max_artifacts_size': max_artifacts_size,
        'request_access_enabled': request_access_enabled,
        'restrict_user_defined_variables': restrict_user_defined_variables,
        'service_desk_enabled': service_desk_enabled,
        'show_default_award_emojis': show_default_award_emojis,
        'spp_repository_pipeline_access': spp_repository_pipeline_access,
        'template_name': template_name,
        'topics': topics,
        'use_custom_template': use_custom_template,
        'warn_about_potentially_unwanted_characters': warn_about_potentially_unwanted_characters,
        'web_based_commit_signing_enabled': web_based_commit_signing_enabled,
        'analytics_access_level': analytics_access_level,
        'builds_access_level': builds_access_level,
        'container_registry_access_level': container_registry_access_level,
        'environments_access_level': environments_access_level,
        'feature_flags_access_level': feature_flags_access_level,
        'forking_access_level': forking_access_level,
        'infrastructure_access_level': infrastructure_access_level,
        'issues_access_level': issues_access_level,
        'merge_requests_access_level': merge_requests_access_level,
        'model_experiments_access_level': model_experiments_access_level,
        'model_registry_access_level': model_registry_access_level,
        'monitor_access_level': monitor_access_level,
        'pages_access_level': pages_access_level,
        'package_registry_access_level': package_registry_access_level,
        'releases_access_level': releases_access_level,
        'repository_access_level': repository_access_level,
        'requirements_access_level': requirements_access_level,
        'security_and_compliance_access_level': security_and_compliance_access_level,
        'snippets_access_level': snippets_access_level,
        'wiki_access_level': wiki_access_level,
        'container_registry_enabled': container_registry_enabled,
        'emails_disabled': emails_disabled,
        'issues_enabled': issues_enabled,
        'jobs_enabled': jobs_enabled,
        'merge_requests_enabled': merge_requests_enabled,
        'packages_enabled': packages_enabled,
        'public_builds': public_builds,
        'snippets_enabled': snippets_enabled,
        'wiki_enabled': wiki_enabled,
        'tag_list': tag_list,
        # Note: 'avatar' is omitted as it requires complex input types.
    }
    
    # Filter out None values to ensure a clean request body
    payload = {k: v for k, v in payload.items() if v is not None}

    # Validation: Ensure payload is not empty (no updates to perform)
    if not payload:
        print("[GITLAB EDIT PROJECT] Warning: No parameters provided for update.")
        return {"warning": "No fields provided for update. The API was not called."}

    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success (200 OK)
        print("[GITLAB EDIT PROJECT] Project updated successfully.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 400 Bad Request for validation failure, 403 for permissions)
        print(f"[GITLAB EDIT PROJECT] Error updating project: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB EDIT PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def import_project_members(
    target_project_id: Union[int, str], # The ID or URL-encoded path of the project to receive the members.
    source_project_id: Union[int, str] # The ID or URL-encoded path of the project to import members from.
) -> Dict:
    """
    Imports members from one project (source) into another (target).
    
    This function calls the GitLab API: POST /projects/:id/import_project_members/:project_id.
    
    Note: Members with the Owner role in the source project are imported 
    with the Maintainer role if the target project's current user is Maintainer,
    or with the Owner role if the current user is Owner.

    Args:
        target_project_id (Union[int, str]): The ID or URL-encoded path of the project to receive members. (Required)
        source_project_id (Union[int, str]): The ID or URL-encoded path of the project to import members from. (Required)

    Returns:
        Dict: A dictionary containing the status and messages (if any errors occurred during import) 
              on success (200), or an error dictionary on network/API failure (4xx, 5xx).
    """

    # 1. Construct the API URL. IDs must be URL-encoded if they are paths.
    api_url = (
        f"{get_gitlab_api()}/projects/{target_project_id}"
        f"/import_project_members/{source_project_id}"
    )
    print(f"\n[GITLAB IMPORT MEMBERS] Attempting to import members from '{source_project_id}' into '{target_project_id}'")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (200 OK)
        result = response.json()
        status = result.get('status', 'N/A')
        
        if status == 'ok':
            print(f"[GITLAB IMPORT MEMBERS] Members imported successfully.")
        elif status == 'error':
            total = result.get('total_members_count', 'unknown')
            print(f"[GITLAB IMPORT MEMBERS] Import completed with errors. Total members attempted: {total}")
            # The message key contains per-member errors
            print(f"Individual Member Errors: {json.dumps(result.get('message', {}), indent=2)}")
        
        return result

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 Project Not Found, 422 Unprocessable Entity)
        print(f"[GITLAB IMPORT MEMBERS] Error importing members: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details from the response
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB IMPORT MEMBERS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def archive_project(
    project_id: Union[int, str] # The ID or URL-encoded path of the project.
) -> Dict:
    """
    Archives a specified project in GitLab.

    Calls the GitLab API endpoint: POST /projects/:id/archive.

    Prerequisites:
    - The calling user must be an **Administrator** or have the **Owner** role on the project.
    - The operation is **idempotent** (safe to call multiple times).

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project to archive.

    Returns:
        Dict: The updated project object, with the 'archived' field set to true (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """

    # 1. Construct the API URL. The project_id must be URL-encoded if it's a path.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/archive"
    print(f"\n[GITLAB ARCHIVE PROJECT] Attempting to archive project: '{project_id}'")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (200 OK)
        result = response.json()
        print(f"[GITLAB ARCHIVE PROJECT] Project '{project_id}' successfully archived.")
        return result

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 Project Not Found, 403 Forbidden)
        print(f"[GITLAB ARCHIVE PROJECT] Error archiving project: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details from the response
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB ARCHIVE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def unarchive_project(
    project_id: Union[int, str] # The ID or URL-encoded path of the project.
) -> Dict:
    """
    Unarchives a specified project in GitLab, making it visible and accessible again.

    Calls the GitLab API endpoint: POST /projects/:id/unarchive.

    Prerequisites:
    - The calling user must be an **Administrator** or have the **Owner** role on the project.
    - The operation is **idempotent** (safe to call multiple times). Unarchiving an unarchived project has no effect.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project to unarchive.

    Returns:
        Dict: The updated project object, with the 'archived' field set to false (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """

    # 1. Construct the API URL. The project_id must be URL-encoded if it's a path.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/unarchive"
    print(f"\n[GITLAB UNARCHIVE PROJECT] Attempting to unarchive project: '{project_id}'")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (200 OK)
        result = response.json()
        print(f"[GITLAB UNARCHIVE PROJECT] Project '{project_id}' successfully unarchived.")
        return result

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 Project Not Found, 403 Forbidden)
        print(f"[GITLAB UNARCHIVE PROJECT] Error unarchiving project: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details from the response
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB UNARCHIVE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def delete_project(
    project_id: Union[int, str],
    full_path: Optional[str] = None,
    permanently_remove: Optional[Union[bool, str]] = None,
) -> Union[Dict, str]:
    """
    Deletes a GitLab project, including all associated resources like issues and merge requests.

    Calls the GitLab API endpoint: DELETE /projects/:id.

    By default, this marks the project for **delayed deletion** (retention period depends on instance settings).
    Use `permanently_remove` (if available on your instance) to delete immediately if the project is 
    already marked for deletion.

    Prerequisites:
    - The calling user must be an **Administrator** or have the **Owner** role on the project.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project to delete.
        full_path (str, optional): Full path of the project (e.g., 'group/project') to use with 
                                   `permanently_remove`. Introduced in GitLab 15.11.
        permanently_remove (Union[bool, str], optional): **DEPRECATED in GitLab 18.4.** If set, immediately deletes a project if it 
                                                        is marked for deletion. Use caution.

    Returns:
        str: On success (HTTP 202 - Accepted/Queued, or 204 - No Content/Immediate), returns a confirmation message.
        Dict: On failure, returns an error object.
    """
    # 1. Construct the API URL.
    api_url = f"{get_gitlab_api()}/projects/{project_id}"
    print(f"\n[GITLAB DELETE PROJECT] Attempting to delete project: '{project_id}'")

    # 2. Construct Headers
    headers = {'PRIVATE-TOKEN': get_gitlab_token()}
    
    # 3. Construct Query Parameters (for optional fields)
    params = {}
    if full_path is not None:
        params['full_path'] = full_path
    if permanently_remove is not None:
        # Note: The API accepts boolean or string for this, we allow both.
        params['permanently_remove'] = permanently_remove 

    try:
        # 4. Make the DELETE request
        response = requests.delete(api_url, headers=headers, params=params)
        
        # 5. Handle Success (HTTP 202 Accepted/Queued or 204 No Content/Immediate)
        if response.status_code in [202, 204]:
            status_desc = "immediately deleted" if response.status_code == 204 else "queued for deletion"
            msg = f"Project '{project_id}' successfully {status_desc} (HTTP {response.status_code})."
            print(f"[GITLAB DELETE PROJECT] {msg}")
            return msg

        # Raise exception for any other unexpected status code (4xx or 5xx)
        response.raise_for_status() 

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 403 Forbidden, 404 Not Found)
        print(f"[GITLAB DELETE PROJECT] Error deleting project: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB DELETE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def restore_project(
    project_id: Union[int, str] # The ID or URL-encoded path of the project.
) -> Dict:
    """
    Restores a project that has been marked for delayed deletion.

    Calls the GitLab API endpoint: POST /projects/:id/restore.

    Prerequisites:
    - The calling user must be an **Administrator** or have the **Owner** role on the project.
    - The project must currently be marked for deletion.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project to restore.

    Returns:
        Dict: The restored project object on success (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """

    # 1. Construct the API URL. The project_id must be URL-encoded.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/restore"
    print(f"\n[GITLAB RESTORE PROJECT] Attempting to restore project: '{project_id}'")

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    try:
        # 3. Make the POST request
        response = requests.post(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (200 OK)
        result = response.json()
        print(f"[GITLAB RESTORE PROJECT] Project '{project_id}' successfully restored.")
        return result

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 Project Not Found, 403 Forbidden)
        print(f"[GITLAB RESTORE PROJECT] Error restoring project: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details from the response
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB RESTORE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def transfer_project(
    project_id: Union[int, str], # The ID or URL-encoded path of the project.
    namespace: Union[int, str] # The ID or path of the namespace (user or group) to transfer to.
) -> Dict:
    """
    Transfers a project to a new namespace (user or group).

    Calls the GitLab API endpoint: PUT /projects/:id/transfer.

    Prerequisites for transfer must be met (e.g., user must be Owner, target namespace must exist,
    etc.). Refer to GitLab documentation for details on transfer prerequisites.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project to transfer.
        namespace (Union[int, str]): The ID or path of the target namespace.

    Returns:
        Dict: The updated project object, now in the new namespace (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """

    # 1. Construct the API URL.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/transfer"
    print(f"\n[GITLAB TRANSFER PROJECT] Attempting to transfer project '{project_id}' to namespace '{namespace}'")

    # 2. Construct Headers and Payload
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }
    payload = {
        'namespace': namespace
    }

    try:
        # 3. Make the PUT request
        response = requests.put(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (200 OK)
        result = response.json()
        print(f"[GITLAB TRANSFER PROJECT] Project '{project_id}' successfully transferred to namespace '{namespace}'.")
        return result

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 400 Bad Request, 403 Forbidden, 422 Unprocessable Entity for failed transfer rules)
        print(f"[GITLAB TRANSFER PROJECT] Error transferring project: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details from the response
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            # For 422 errors, the message usually contains the transfer reason.
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB TRANSFER PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_transfer_locations(
    project_id: Union[int, str], # The ID or URL-encoded path of the project.
    search: Optional[str] = None, # Optional string to filter groups by name.
) -> Union[List[Dict], Dict]:
    """
    Retrieves a list of groups to which the authenticated user can transfer a project.

    Calls the GitLab API endpoint: GET /projects/:id/transfer_locations.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project 
                                      whose transfer locations are being checked.
        search (str, optional): A group name search term to filter the results.

    Returns:
        List[Dict]: A list of group dictionaries available for transfer (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """

    # 1. Construct the API URL. The project_id must be URL-encoded.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/transfer_locations"
    print(f"\n[GITLAB TRANSFER LOCATIONS] Attempting to list groups available for transfer of project: '{project_id}'")

    # 2. Construct Headers and Parameters
    headers = {'PRIVATE-TOKEN': get_gitlab_token()}
    params = {}
    
    if search:
        params['search'] = search

    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success (200 OK)
        result = response.json()
        print(f"[GITLAB TRANSFER LOCATIONS] Found {len(result)} eligible transfer locations.")
        return result

    except requests.exceptions.HTTPError as e:
        # Handle errors (e.g., 404 Project Not Found, 403 Forbidden)
        print(f"[GITLAB TRANSFER LOCATIONS] Error listing transfer locations: HTTP Error {e.response.status_code}")
        try:
            # Attempt to extract JSON error details
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback for non-JSON error responses
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB TRANSFER LOCATIONS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def upload_project_avatar(
    project_id: Union[int, str],
    avatar_file_path: str, # Local path to the image file (e.g., 'dk.png')
) -> Dict:
    """
    Uploads an avatar image file to the specified GitLab project.

    Calls the GitLab API endpoint: PUT /projects/:id. This requires multipart/form-data.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        avatar_file_path (str): The local file path to the image to upload.

    Returns:
        Dict: The updated project details on success, including the new 'avatar_url' (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}"
    print(f"\n[GITLAB UPLOAD AVATAR] Attempting to upload avatar for project: '{project_id}' from '{avatar_file_path}'")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}

    try:
        # Open the file in binary mode for upload (required for multipart/form-data)
        with open(avatar_file_path, 'rb') as avatar_file:
            # The 'files' dictionary structures the multipart data:
            # {'field_name': ('filename_for_server', file_handle)}
            files = {'avatar': (avatar_file_path, avatar_file)}
            
            # Use the files parameter for multipart/form-data PUT request
            response = requests.put(api_url, headers=headers, files=files)
        
        response.raise_for_status()

        result = response.json()
        print(f"[GITLAB UPLOAD AVATAR] Avatar successfully uploaded. New URL: {result.get('avatar_url')}")
        return result

    except FileNotFoundError:
        print(f"[GITLAB UPLOAD AVATAR] Error: File not found at '{avatar_file_path}'")
        return {"error": "File Not Found", "details": f"The avatar file path '{avatar_file_path}' does not exist."}
    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB UPLOAD AVATAR] Error uploading avatar: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB UPLOAD AVATAR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def download_project_avatar(
    project_id: Union[int, str],
    save_path: Optional[str] = None # Optional local path (with filename) to save the downloaded image.
) -> Union[bytes, str, Dict]:
    """
    Downloads the project's avatar image.

    Calls the GitLab API endpoint: GET /projects/:id/avatar.
    No authentication is required if the project is publicly accessible.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        save_path (str, optional): Local path (including filename and extension) to save the avatar.

    Returns:
        Union[bytes, str, Dict]: The raw image bytes if save_path is None, the save path string on successful save, 
                                 or an error dictionary on failure.
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/avatar"
    print(f"\n[GITLAB DOWNLOAD AVATAR] Attempting to download avatar for project: '{project_id}'")

    # Only include token if provided/needed
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()
        
    try:
        # Use stream=True to handle the binary response efficiently
        response = requests.get(api_url, headers=headers, stream=True)
        response.raise_for_status()

        # Get raw image content
        image_bytes = response.content

        if save_path:
            # Save the raw bytes to the specified local path
            with open(save_path, 'wb') as f:
                f.write(image_bytes)
            print(f"[GITLAB DOWNLOAD AVATAR] Avatar successfully downloaded and saved to: {save_path}")
            return f"Avatar successfully saved to {save_path}"

        print(f"[GITLAB DOWNLOAD AVATAR] Avatar successfully downloaded ({len(image_bytes)} bytes).")
        return image_bytes

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB DOWNLOAD AVATAR] Error downloading avatar: HTTP Error {e.response.status_code}")
        # Avatar endpoints often do not return JSON on error
        error_text = e.response.text
        print(f"GitLab API Error Details: {error_text}")
        return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB DOWNLOAD AVATAR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    except IOError as e:
        print(f"[GITLAB DOWNLOAD AVATAR] Error writing file to '{save_path}': {e}")
        return {"error": "File Write Error", "details": str(e)}

@mcp.tool()
def remove_project_avatar(
    project_id: Union[int, str],
) -> Dict:
    """
    Removes the current avatar image from the specified GitLab project.

    Calls the GitLab API endpoint: PUT /projects/:id with the 'avatar' parameter set to a blank value.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.

    Returns:
        Dict: The updated project details on success, with 'avatar_url' set to null (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}"
    print(f"\n[GITLAB REMOVE AVATAR] Attempting to remove avatar for project: '{project_id}'")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}
    # Setting 'avatar' to an empty string in the data payload tells GitLab to remove the existing avatar.
    data = {'avatar': ''}

    try:
        # Use data=data for application/x-www-form-urlencoded PUT request
        response = requests.put(api_url, headers=headers, data=data)
        response.raise_for_status()

        result = response.json()
        print(f"[GITLAB REMOVE AVATAR] Avatar successfully removed. Avatar URL is now: {result.get('avatar_url')}")
        return result

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB REMOVE AVATAR] Error removing avatar: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB REMOVE AVATAR] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def share_project_with_group(
    project_id: Union[int, str],
    group_id: int,
    group_access: int,
    expires_at: Optional[str] = None,
) -> Dict:
    """
    Shares a project with a specified group, granting a specific access level.

    Calls the GitLab API endpoint: POST /projects/:id/share.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        group_id (int): The ID of the group to share with.
        group_access (int): The access role to grant (e.g., 10=Guest, 20=Reporter, 30=Developer).
        expires_at (str, optional): Share expiration date in ISO 8601 format (e.g., '2025-12-31').

    Returns:
        Dict: The shared group object on success (HTTP 201).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/share"
    print(f"\n[GITLAB SHARE PROJECT] Attempting to share project '{project_id}' with group '{group_id}'")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}
    data = {
        'group_id': group_id,
        'group_access': group_access,
    }
    if expires_at:
        data['expires_at'] = expires_at

    try:
        response = requests.post(api_url, headers=headers, data=data)
        response.raise_for_status()

        result = response.json()
        print(f"[GITLAB SHARE PROJECT] Project successfully shared with group {group_id}.")
        return result

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB SHARE PROJECT] Error sharing project: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB SHARE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def unshare_project_from_group(
    project_id: Union[int, str],
    group_id: int,
) -> Dict:
    """
    Removes a project's sharing link with a group.

    Calls the GitLab API endpoint: DELETE /projects/:id/share/:group_id.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        group_id (int): The ID of the group to unshare from.

    Returns:
        Dict: Success message on no content (HTTP 204).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/share/{group_id}"
    print(f"\n[GITLAB UNSHARE PROJECT] Attempting to unshare project '{project_id}' from group '{group_id}'")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}

    try:
        response = requests.delete(api_url, headers=headers)
        response.raise_for_status()

        if response.status_code == 204:
            print(f"[GITLAB UNSHARE PROJECT] Project successfully unshared from group {group_id}.")
            return {"success": f"Project {project_id} unshared from group {group_id}."}
        
        # Should not be reached if raise_for_status() passed and it's not 204
        return {"warning": f"Unshare request completed with status code {response.status_code}."}

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB UNSHARE PROJECT] Error unsharing project: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB UNSHARE PROJECT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def start_project_housekeeping(
    project_id: Union[int, str],
    task: Optional[str] = None,
) -> Dict:
    """
    Starts the housekeeping task for a project.

    Calls the GitLab API endpoint: POST /projects/:id/housekeeping.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        task (str, optional): 'prune' to trigger manual prune or 'eager' to trigger eager housekeeping.

    Returns:
        Dict: Empty response body on success (HTTP 202 Accepted).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/housekeeping"
    print(f"\n[GITLAB HOUSEKEEPING] Starting housekeeping for project '{project_id}' (Task: {task if task else 'default'})")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}
    data = {}
    if task:
        data['task'] = task

    try:
        response = requests.post(api_url, headers=headers, data=data)
        response.raise_for_status()

        if response.status_code == 202:
            print(f"[GITLAB HOUSEKEEPING] Housekeeping task started successfully (HTTP 202 Accepted).")
            return {"success": "Housekeeping task initiated."}
        
        # In case GitLab changes response to something else on success
        return {"success": "Housekeeping task initiated.", "response": response.json() if response.content else {}}

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB HOUSEKEEPING] Error starting housekeeping: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB HOUSEKEEPING] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def sast_real_time_scan(
    project_id: Union[int, str],
    file_path: str,
    content: str,
) -> Dict:
    """
    Performs a Real-time SAST (Static Application Security Testing) scan on a single file's content.
    This feature is Tier: Ultimate and Status: Experiment.

    Calls the GitLab API endpoint: POST /projects/:id/security_scans/sast/scan.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        file_path (str): The path/name of the file being scanned (e.g., 'src/main.c').
        content (str): The actual content of the file to be scanned.

    Returns:
        Dict: SAST scan results, including a list of 'vulnerabilities' (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/security_scans/sast/scan"
    print(f"\n[GITLAB SAST SCAN] Starting real-time SAST scan for file '{file_path}' in project '{project_id}'")

    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }
    payload = {
        'file_path': file_path,
        'content': content
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        print(f"[GITLAB SAST SCAN] Scan completed. Found {len(result.get('vulnerabilities', []))} vulnerabilities.")
        return result

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB SAST SCAN] Error performing SAST scan: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB SAST SCAN] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def download_repository_snapshot(
    project_id: Union[int, str],
    save_path: str,
    wiki: bool = False,
) -> Dict:
    """
    Downloads a snapshot (tar archive) of the project's Git repository (or wiki).
    This endpoint may only be accessed by an administrative user.

    Calls the GitLab API endpoint: GET /projects/:id/snapshot.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.
        save_path (str): Local path (including filename and '.tar' extension) to save the snapshot.
        wiki (bool, optional): If True, downloads the wiki repository snapshot instead of the project repository.

    Returns:
        Dict: Success message on successful file save.
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    repo_type = "wiki" if wiki else "project"
    api_url = f"{get_gitlab_api()}/projects/{project_id}/snapshot"
    print(f"\n[GITLAB REPO SNAPSHOT] Attempting to download {repo_type} repository snapshot for project '{project_id}' to '{save_path}'")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}
    params = {'wiki': str(wiki).lower()} # 'true' or 'false'

    try:
        # Use stream=True for handling large binary file download
        response = requests.get(api_url, headers=headers, params=params, stream=True)
        response.raise_for_status()

        # Save the raw bytes to the specified local path
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        
        print(f"[GITLAB REPO SNAPSHOT] Snapshot successfully downloaded and saved to: {save_path}")
        return {"success": f"Repository snapshot for {repo_type} successfully saved to {save_path}"}

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB REPO SNAPSHOT] Error downloading snapshot: HTTP Error {e.response.status_code}")
        # Snapshot endpoints often do not return JSON on error
        error_text = e.response.text
        print(f"GitLab API Error Details: {error_text}")
        return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB REPO SNAPSHOT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    except IOError as e:
        print(f"[GITLAB REPO SNAPSHOT] Error writing file to '{save_path}': {e}")
        return {"error": "File Write Error", "details": str(e)}

@mcp.tool()
def get_repository_storage_path(
    project_id: Union[int, str],
) -> Dict:
    """
    Gets the path to repository storage for the specified project.
    Available for administrators only.

    Calls the GitLab API endpoint: GET /projects/:id/storage.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project.

    Returns:
        Dict: Repository storage information (HTTP 200).
        Dict: An error dictionary on network/API failure (HTTP 4xx/5xx).
    """
    api_url = f"{get_gitlab_api()}/projects/{project_id}/storage"
    print(f"\n[GITLAB REPO STORAGE] Attempting to get repository storage path for project '{project_id}'")

    headers = {'PRIVATE-TOKEN': get_gitlab_token()}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        result = response.json()
        print(f"[GITLAB REPO STORAGE] Storage path retrieved for project {project_id}.")
        return result

    except requests.exceptions.HTTPError as e:
        print(f"[GITLAB REPO STORAGE] Error retrieving storage path: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            error_text = e.response.text
            print(f"GitLab API Error Details: {error_text}")
            return {"error": str(e), "details": error_text}
    except requests.exceptions.RequestException as e:
        print(f"[GITLAB REPO STORAGE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}