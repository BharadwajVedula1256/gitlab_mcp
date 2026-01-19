import requests
import json
from typing import Dict, Union, List, Optional
from ..config import get_gitlab_api, get_gitlab_token, mcp

@mcp.tool()
def list_gitlab_repository_commits(
    project_id: Union[int, str],
    all_commits: Optional[bool] = None,
    author: Optional[str] = None,
    first_parent: Optional[bool] = None,
    order: Optional[str] = None,
    path: Optional[str] = None,
    ref_name: Optional[str] = None,
    since: Optional[str] = None,
    trailers: Optional[bool] = None,
    until: Optional[str] = None,
    with_stats: Optional[bool] = None,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List, Dict]:
    """
    List repository commits
    Retrieve the list of commits in a GitLab repository using:
        GET /projects/:id/repository/commits

    This function provides a list of commits, which can be filtered by branch,
    tag, date range, author, and file path.

    Args:
        project_id (str): Project ID or URL-encoded path of the repository. (Required)
        all_commits (bool, optional): If true, retrieve every commit from the repository,
                                       ignoring `ref_name`.
        author (str, optional): Search commits by commit author (name or email).
        first_parent (bool, optional): If true, follows only the first parent commit 
                                       upon seeing a merge commit.
        order (str, optional): List commits in order. Possible values: 'default' 
                               (reverse chronological) or 'topo'.
        path (str, optional): The file path to filter commits affecting only that file.
        ref_name (str, optional): The name of a repository branch, tag, or revision range.
                                  Defaults to the default branch.
        since (str, optional): Only commits after or on this date (ISO 8601: YYYY-MM-DDTHH:MM:SSZ).
        trailers (bool, optional): If true, parses and includes Git trailers for every commit.
        until (str, optional): Only commits before or on this date (ISO 8601: YYYY-MM-DDTHH:MM:SSZ).
        with_stats (bool, optional): If true, retrieve stats (additions, deletions) about each commit.
        per_page (int, optional): Number of results per page for traditional pagination. Default is 20.
        page (int, optional): Page number of results for traditional pagination.

    Returns:
        Union[List, Dict]: 
            - On success: A list of commit objects (dictionaries). Each object includes:
                - id (string): SHA of the commit.
                - short_id (string): Short SHA of the commit.
                - title (string): Title of the commit message.
                - author_name (string): Name of the commit author.
                - author_email (string): Email address of the commit author.
                - authored_date (string): Date when the commit was authored.
                - committer_name (string): Name of the commit committer.
                - committer_email (string): Email address of the commit committer.
                - committed_date (string): Date when the commit was committed.
                - created_at (string): Date when the commit was created (identical to committed_date).
                - message (string): Full commit message.
                - parent_ids (array): Array of parent commit SHAs.
                - web_url (string): Web URL of the commit.
                - trailers (object): Git trailers parsed from the commit message.
                - extended_trailers (object): Extended Git trailers with all values.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits"

    # 2. Construct Headers (using private token from config)
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}

    # List of parameters to check and include in the request
    api_params_map = {
        'all_commits': 'all', 'author': 'author', 'first_parent': 'first_parent', 
        'order': 'order', 'path': 'path', 'ref_name': 'ref_name', 
        'since': 'since', 'trailers': 'trailers', 'until': 'until', 
        'with_stats': 'with_stats', 'per_page': 'per_page', 'page': 'page'
    }

    local_vars = locals()
    for py_name, api_name in api_params_map.items():
        value = local_vars.get(py_name)
        if value is not None:
            # Convert boolean values to lowercase strings for the GitLab API
            if isinstance(value, bool):
                params[api_name] = str(value).lower()
            else:
                params[api_name] = value

    print(f"\n[LIST COMMITS] Attempting to list commits for project {project_id} (Ref: {ref_name or 'default branch'}).")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the list of commit objects
        print(f"[LIST COMMITS] Successfully retrieved commit list.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[LIST COMMITS] Error retrieving commits: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[LIST COMMITS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def create_gitlab_commit(
    project_id: Union[int, str],
    branch: str,
    commit_message: str,
    actions: List[Dict],
    author_email: Optional[str] = None,
    author_name: Optional[str] = None,
    force: Optional[bool] = None,
    start_branch: Optional[str] = None,
    start_project: Optional[Union[int, str]] = None,
    start_sha: Optional[str] = None,
    stats: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Create a commit with multiple files and actions
    Create a commit by posting a JSON payload using:
        POST /projects/:id/repository/commits

    This tool creates a single commit containing one or more file actions
    (create, update, delete, move, chmod) on a specified branch. It is the
    primary method for programmatic modification of repository content.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        branch (str): Name of the branch to commit into. (Required)
        commit_message (str): Commit message. (Required)
        actions (List[Dict]): An array of action hashes to commit as a batch. (Required)
                              Each dictionary must contain 'action' and 'file_path'.
                              For 'create'/'update'/'move', include 'content'.
                              For 'move', include 'previous_path'.
                              For 'chmod', include 'execute_filemode'.
        author_email (str, optional): Specify the commit author’s email address.
        author_name (str, optional): Specify the commit author’s name.
        force (bool, optional): If true, overwrites the target branch.
        start_branch (str, optional): Name of the branch to start the new branch from.
        start_project (Union[int, str], optional): Project ID/path to start the new branch from.
        start_sha (str, optional): SHA of the commit to start the new branch from.
        stats (bool, optional): Include commit stats in the response. Default is true in API.

    Returns:
        Union[Dict, Dict]:
            - On success: A dictionary representing the created commit object. Attributes include:
                - id (string): SHA of the created commit.
                - short_id (string): Short SHA of the created commit.
                - title (string): Title of the commit message.
                - author_name (string): Name of the commit author.
                - author_email (string): Email address of the commit author.
                - authored_date (string): Date when the commit was authored.
                - committer_name (string): Name of the commit committer.
                - committer_email (string): Email address of the commit committer.
                - committed_date (string): Date when the commit was committed.
                - created_at (string): Date when the commit was created.
                - message (string): Full commit message.
                - parent_ids (array): Array of parent commit SHAs.
                - stats (object): Statistics about the commit (additions, deletions, total).
                - status (string): Status of the commit.
                - web_url (string): Web URL of the commit.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'branch': branch,
        'commit_message': commit_message,
        'actions': actions,
    }

    # Map Python function argument names to Payload fields
    optional_params = {
        'author_email': author_email,
        'author_name': author_name,
        'force': force,
        'start_branch': start_branch,
        'start_project': start_project,
        'start_sha': start_sha,
        'stats': stats,
    }
    
    # Add optional parameters, filtering out None values
    for py_name, value in optional_params.items():
        if value is not None:
            # Convert boolean values to lowercase strings for the GitLab API if needed
            if isinstance(value, bool):
                payload[py_name] = str(value).lower()
            else:
                payload[py_name] = value

    print(f"\n[CREATE COMMIT] Attempting to create commit on branch '{branch}' in project {project_id} with {len(actions)} action(s).")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[CREATE COMMIT] Successfully created commit.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[CREATE COMMIT] Error creating commit: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[CREATE COMMIT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_single_commit(
    project_id: Union[int, str],
    sha: str,
    stats: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Get a single commit
    Get a specific commit identified by the commit hash or name of a branch or tag using:
        GET /projects/:id/repository/commits/:sha

    This function retrieves the complete details for a single commit, branch, or tag 
    in a GitLab repository.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash or name of a repository branch or tag. (Required)
        stats (Optional[bool]): Include commit stats (additions, deletions, total) in the response.

    Returns:
        Union[Dict, Dict]:
            - On success: A dictionary representing the commit object. Attributes include:
                - id (string): SHA of the commit.
                - short_id (string): Short SHA of the commit.
                - title (string): Title of the commit message.
                - author_name (string): Name of the commit author.
                - author_email (string): Email address of the commit author.
                - authored_date (string): Date when the commit was authored.
                - committer_name (string): Name of the commit committer.
                - committer_email (string): Email address of the commit committer.
                - committed_date (string): Date when the commit was committed.
                - created_at (string): Date when the commit was created.
                - message (string): Full commit message.
                - parent_ids (array): Array of parent commit SHAs.
                - last_pipeline (object): Information about the last pipeline for this commit.
                - stats (object): Statistics about the commit (additions, deletions, total).
                - status (string): Status of the commit.
                - web_url (string): Web URL of the commit.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}"

    # 2. Construct Headers and Query Parameters
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    params = {}
    if stats is not None:
        # GitLab API expects boolean query parameters as lowercase strings
        params['stats'] = str(stats).lower()

    print(f"\n[GET SINGLE COMMIT] Attempting to retrieve commit details for SHA/Ref '{sha}' in project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET SINGLE COMMIT] Successfully retrieved commit details.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET SINGLE COMMIT] Error retrieving commit: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET SINGLE COMMIT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_commit_references(
    project_id: Union[int, str],
    sha: str,
    type: Optional[str] = None,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List, Dict]:
    """
    Get references a commit is pushed to
    Get all references (from branches or tags) a commit is pushed to using:
        GET /projects/:id/repository/commits/:sha/refs

    This function retrieves all branches and/or tags that point to the given commit SHA.
    The list can be filtered by reference type and paginated.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash. (Required)
        type (Optional[str]): The scope of references. Possible values: 'branch', 'tag', 'all'.
                              Default is 'all'.
        per_page (Optional[int]): Number of results per page for traditional pagination.
        page (Optional[int]): Page number of results for traditional pagination.

    Returns:
        Union[List, Dict]:
            - On success: A list of reference objects (dictionaries). Each object includes:
                - name (string): Name of the branch or tag.
                - type (string): Type of reference ('branch' or 'tag').
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/refs"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}

    # Map Python function argument names to Payload fields
    optional_params = {
        'type': type,
        'per_page': per_page,
        'page': page,
    }
    
    # Add optional parameters, filtering out None values
    for py_name, value in optional_params.items():
        if value is not None:
            params[py_name] = value

    print(f"\n[GET COMMIT REFS] Attempting to retrieve references for commit SHA '{sha}' in project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT REFS] Successfully retrieved commit references.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT REFS] Error retrieving commit references: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT REFS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_commit_sequence(
    project_id: Union[int, str],
    sha: str,
    first_parent: Optional[bool] = None
) -> Union[Dict, Dict]:
    """
    Get commit sequence
    Get the sequence number of a commit in a project by following the parent links from the given commit using:
        GET /projects/:id/repository/commits/:sha/sequence

    This API provides essentially the same features as the `git rev-list --count` command for a given commit SHA.
    It counts the total number of commits reachable from the specified commit.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash. (Required)
        first_parent (Optional[bool]): If true, follows only the first parent commit upon seeing a merge commit.

    Returns:
        Union[Dict, Dict]:
            - On success: A dictionary representing the commit sequence count. Attributes include:
                - count (integer): Sequence number of the commit (total reachable commits).
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/sequence"

    # 2. Construct Headers and Query Parameters
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    params = {}
    if first_parent is not None:
        # GitLab API expects boolean query parameters as lowercase strings
        params['first_parent'] = str(first_parent).lower()

    print(f"\n[GET COMMIT SEQUENCE] Attempting to retrieve sequence count for SHA '{sha}' in project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT SEQUENCE] Successfully retrieved commit sequence count.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT SEQUENCE] Error retrieving sequence count: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT SEQUENCE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def cherry_pick_gitlab_commit(
    project_id: Union[int, str],
    sha: str,
    branch: str,
    dry_run: Optional[bool] = None,
    message: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Cherry-pick a commit
    Cherry-picks a commit to a given branch using:
        POST /projects/:id/repository/commits/:sha/cherry_pick

    This tool applies the changes from a specified commit (identified by SHA) onto 
    a target branch, creating a new commit. It supports a dry-run mode to check 
    for conflicts before applying.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash to cherry-pick. (Required)
        branch (str): The name of the branch to cherry-pick the commit into. (Required)
        dry_run (Optional[bool]): If true, the cherry-pick is attempted but no changes are
                                  committed. Default is false.
        message (Optional[str]): A custom commit message to use for the new commit.

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the new cherry-picked commit object. Attributes include:
                - id (string): SHA of the cherry-picked commit.
                - short_id (string): Short SHA of the cherry-picked commit.
                - title (string): Title of the commit message.
                - author_name (string): Name of the original commit author.
                - author_email (string): Email address of the original commit author.
                - authored_date (string): Date when the original commit was authored.
                - committer_name (string): Name of the cherry-pick committer.
                - committer_email (string): Email address of the cherry-pick committer.
                - committed_date (string): Date when the cherry-picked commit was committed.
                - created_at (string): Date when the cherry-picked commit was created.
                - message (string): Full commit message.
                - parent_ids (array): Array of parent commit SHAs.
                - web_url (string): Web URL of the cherry-picked commit.
            - On dry-run success (200 OK): A dictionary with `{"dry_run": "success"}`.
            - On failure: A structured error dictionary containing `message` and `error_code` ('empty' or 'conflict').

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/cherry_pick"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'branch': branch,
    }

    # Add optional parameters, filtering out None values
    if dry_run is not None:
        # GitLab API often expects boolean values as strings or needs them handled explicitly
        payload['dry_run'] = str(dry_run).lower()
    if message is not None:
        payload['message'] = message

    print(f"\n[CHERRY-PICK] Attempting to cherry-pick commit '{sha}' to branch '{branch}' in project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        
        # 5. Handle responses (201 Created for success, 200 OK for dry-run success, others for failure)
        
        if response.status_code == 201:
            # Successful commit created
            print(f"[CHERRY-PICK] Successfully created cherry-pick commit.")
            return response.json()
        
        if response.status_code == 200 and dry_run:
            # Successful dry run
            print(f"[CHERRY-PICK] Dry run successful: cherry-pick can be applied cleanly.")
            return response.json()

        # Check for non-2xx status codes (failure)
        response.raise_for_status()
        
        # Fallback for unexpected success status (shouldn't happen based on API doc)
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle known failure responses (400 Bad Request for conflict/empty)
        print(f"[CHERRY-PICK] Error during cherry-pick: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            # This handles the specific failure format: {"message": "...", "error_code": "..."}
            if 'error_code' in error_details or 'message' in error_details:
                return {"error": error_details.get("message", str(e)), "error_code": error_details.get("error_code", "unknown_api_error")}
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[CHERRY-PICK] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def revert_gitlab_commit(
    project_id: Union[int, str],
    sha: str,
    branch: str,
    dry_run: Optional[bool] = None,
) -> Union[Dict, Dict]:
    """
    Revert a commit
    Reverts a commit in a given branch using:
        POST /projects/:id/repository/commits/:sha/revert

    This tool creates a new commit that undoes the changes introduced by the specified 
    commit (identified by SHA) onto a target branch. It supports a dry-run mode to 
    check for conflicts before applying.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): Commit SHA to revert. (Required)
        branch (str): Target branch name. (Required)
        dry_run (Optional[bool]): If true, the revert is attempted but no changes are
                                  committed. Default is false.

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the new revert commit object. Attributes include:
                - id (string): SHA of the revert commit.
                - short_id (string): Short SHA of the revert commit.
                - title (string): Title of the revert commit message.
                - author_name (string): Name of the revert commit author.
                - author_email (string): Email address of the revert commit author.
                - authored_date (string): Date when the revert commit was authored.
                - committer_name (string): Name of the revert commit committer.
                - committer_email (string): Email address of the revert commit committer.
                - committed_date (string): Date when the revert commit was committed.
                - created_at (string): Date when the revert commit was created.
                - message (string): Full revert commit message.
                - parent_ids (array): Array of parent commit SHAs.
                - web_url (string): Web URL of the revert commit.
            - On dry-run success (200 OK): A dictionary with `{"dry_run": "success"}`.
            - On failure: A structured error dictionary containing `message` and `error_code` ('conflict' or 'empty').

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/revert"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'branch': branch,
    }

    # Add optional dry_run parameter, converting boolean to lowercase string
    if dry_run is not None:
        payload['dry_run'] = str(dry_run).lower()

    print(f"\n[REVERT COMMIT] Attempting to revert commit '{sha}' to branch '{branch}' in project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        
        # 5. Handle responses (201 Created for success, 200 OK for dry-run success, others for failure)
        
        if response.status_code == 201:
            # Successful commit created
            print(f"[REVERT COMMIT] Successfully created revert commit.")
            return response.json()
        
        if response.status_code == 200 and dry_run:
            # Successful dry run
            print(f"[REVERT COMMIT] Dry run successful: revert can be applied cleanly.")
            return response.json()

        # Check for non-2xx status codes (failure)
        response.raise_for_status()
        
        # Fallback for unexpected success status
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle known failure responses (400 Bad Request for conflict/empty)
        print(f"[REVERT COMMIT] Error during revert: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            # This handles the specific failure format: {"message": "...", "error_code": "..."}
            if 'error_code' in error_details or 'message' in error_details:
                return {"error": error_details.get("message", str(e)), "error_code": error_details.get("error_code", "unknown_api_error")}
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[REVERT COMMIT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

from typing import Optional, Union, Dict, List

@mcp.tool()
def get_gitlab_commit_diff(
    project_id: Union[int, str],
    sha: str,
    unidiff: Optional[bool] = None
) -> Union[List[Dict], Dict]:
    """
    Get commit diff
    Get the diff of a commit in a project using:
        GET /projects/:id/repository/commits/:sha/diff

    This function retrieves the differences (diff) for all files modified by a 
    specific commit, branch, or tag.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash or name of a repository branch or tag. (Required)
        unidiff (Optional[bool]): If true, presents diffs in the unified diff format.

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of file diff objects (dictionaries). Each object includes:
                - diff (string): The diff content.
                - old_path (string): Old path of the file.
                - new_path (string): New path of the file.
                - a_mode (string): Old file mode of the file.
                - b_mode (string): New file mode of the file.
                - new_file (boolean): If true, this is a new file.
                - renamed_file (boolean): If true, the file was renamed.
                - deleted_file (boolean): If true, the file was deleted.
                - collapsed (boolean): File diffs are excluded but can be fetched on request.
                - too_large (boolean): File diffs are excluded and cannot be retrieved (due to limits).
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/diff"

    # 2. Construct Headers and Query Parameters
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    params = {}
    if unidiff is not None:
        # GitLab API expects boolean query parameters as lowercase strings
        params['unidiff'] = str(unidiff).lower()

    print(f"\n[GET COMMIT DIFF] Attempting to retrieve diff for SHA/Ref '{sha}' in project {project_id}.")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT DIFF] Successfully retrieved commit diff.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT DIFF] Error retrieving commit diff: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT DIFF] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_commit_comments(
    project_id: Union[int, str],
    sha: str
) -> Union[List[Dict], Dict]:
    """
    Get commit comments
    Get the comments of a commit in a project using:
        GET /projects/:id/repository/commits/:sha/comments

    This function retrieves all comments (notes) associated with a specific commit 
    identified by its hash, branch name, or tag name.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash or name of a repository branch or tag. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of comment objects (dictionaries). Each object includes:
                - note (string): The comment text.
                - author (object): Information about the comment author (id, username, email, etc.).
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/comments"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET COMMIT COMMENTS] Attempting to retrieve comments for SHA/Ref '{sha}' in project {project_id}.")
    
    try:
        # 3. Make the GET request (no payload or optional params needed)
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT COMMENTS] Successfully retrieved commit comments.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT COMMENTS] Error retrieving commit comments: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT COMMENTS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def post_gitlab_commit_comment(
    project_id: Union[int, str],
    sha: str,
    note: str,
    path: Optional[str] = None,
    line: Optional[int] = None,
    line_type: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Post comment to commit
    Adds a comment to a commit using:
        POST /projects/:id/repository/commits/:sha/comments

    This tool adds a comment (note) to a specified commit. It supports adding a
    general commit comment or a specific line comment by providing the file path, 
    line number, and line type ('new' or 'old').

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit SHA or name of a repository branch or tag. (Required)
        note (str): The text of the comment. (Required)
        path (Optional[str]): The file path relative to the repository for a line comment.
        line (Optional[int]): The line number where the comment should be placed for a line comment.
        line_type (Optional[str]): The line type. Takes 'new' or 'old' as arguments for a line comment.

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the created comment object. Attributes include:
                - note (string): The comment text.
                - author (object): Information about the comment author.
                - created_at (string): Date when the comment was created.
                - path (string): File path relative to the repository (null if general comment).
                - line (integer): Line number where the comment is placed (null if general comment).
                - line_type (string): Type of line the comment is on (null if general comment).
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/comments"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'note': note,
    }

    # Add optional line-specific parameters
    if path is not None:
        payload['path'] = path
    if line is not None:
        payload['line'] = line
    if line_type is not None:
        payload['line_type'] = line_type

    print(f"\n[POST COMMIT COMMENT] Attempting to post comment to SHA/Ref '{sha}' in project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[POST COMMIT COMMENT] Successfully posted comment.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[POST COMMIT COMMENT] Error posting comment: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[POST COMMIT COMMENT] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

from typing import Optional, Union, Dict, List

@mcp.tool()
def get_gitlab_commit_discussions(
    project_id: Union[int, str],
    sha: str
) -> Union[List[Dict], Dict]:
    """
    Get commit discussions
    Get the discussions of a commit in a project using:
        GET /projects/:id/repository/commits/:sha/discussions

    This function retrieves all discussion threads (which may contain multiple notes/comments) 
    associated with a specific commit identified by its hash, branch name, or tag name.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash or name of a repository branch or tag. (Required)

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of discussion objects (dictionaries). Each object includes:
                - id (string): ID of the discussion.
                - individual_note (boolean): If true, the discussion is an individual note.
                - notes (array): Array of note/comment objects in the discussion.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/discussions"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET COMMIT DISCUSSIONS] Attempting to retrieve discussions for SHA/Ref '{sha}' in project {project_id}.")
    
    try:
        # 3. Make the GET request (no payload or optional params needed)
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT DISCUSSIONS] Successfully retrieved commit discussions.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT DISCUSSIONS] Error retrieving commit discussions: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT DISCUSSIONS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_commit_statuses(
    project_id: Union[int, str],
    sha: str,
    all: Optional[bool] = None,
    name: Optional[str] = None,
    order_by: Optional[str] = None,
    pipeline_id: Optional[int] = None,
    ref: Optional[str] = None,
    sort: Optional[str] = None,
    stage: Optional[str] = None,
    per_page: Optional[int] = None,
    page: Optional[int] = None
) -> Union[List[Dict], Dict]:
    """
    List commit statuses
    List the statuses of a commit in a project using:
        GET /projects/:id/repository/commits/:sha/statuses

    This function retrieves all CI/CD statuses (e.g., pending, running, success, failed) 
    associated with a specific commit, branch, or tag.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): Hash of the commit. (Required)
        all (Optional[bool]): If true, include all statuses instead of latest only. Default is false.
        name (Optional[str]): Filter statuses by job name (e.g., 'bundler:audit').
        order_by (Optional[str]): Values for sorting statuses. Valid values are 'id' and 'pipeline_id'. Default is 'id'.
        pipeline_id (Optional[int]): Filter statuses by pipeline ID.
        ref (Optional[str]): Name of the branch or tag. Default is the default branch.
        sort (Optional[str]): Sort statuses in ascending or descending order. Valid values are 'asc' and 'desc'. Default is 'asc'.
        stage (Optional[str]): Filter statuses by build stage (e.g., 'test').
        per_page (Optional[int]): Number of results per page for traditional pagination.
        page (Optional[int]): Page number of results for traditional pagination.

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of status objects (dictionaries). Each object includes:
                - id (integer): ID of the status.
                - status (string): Status of the commit (e.g., 'success', 'failed').
                - name (string): Name of the status.
                - ref (string): Reference (branch or tag) of the commit.
                - sha (string): SHA of the commit.
                - author (object): Information about the status author.
                - created_at (string): Date when the status was created.
                - started_at (string): Date when the status was started.
                - finished_at (string): Date when the status was finished.
                - description (string): Description of the status.
                - target_url (string): Target URL associated with the status.
                - allow_failure (boolean): If true, the status allows failure.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/statuses"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}

    # Map Python function argument names to Payload fields
    optional_params = {
        'all': all,
        'name': name,
        'order_by': order_by,
        'pipeline_id': pipeline_id,
        'ref': ref,
        'sort': sort,
        'stage': stage,
        'per_page': per_page,
        'page': page,
    }
    
    # Add optional parameters, filtering out None values
    for py_name, value in optional_params.items():
        if value is not None:
            # Handle boolean parameters which must be lowercase strings for GitLab API
            if isinstance(value, bool):
                params[py_name] = str(value).lower()
            else:
                params[py_name] = value

    print(f"\n[GET COMMIT STATUSES] Attempting to retrieve statuses for SHA '{sha}' in project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT STATUSES] Successfully retrieved commit statuses.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT STATUSES] Error retrieving commit statuses: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT STATUSES] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def set_gitlab_commit_pipeline_status(
    project_id: Union[int, str],
    sha: str,
    state: str,
    coverage: Optional[float] = None,
    description: Optional[str] = None,
    name: Optional[str] = None,
    context: Optional[str] = None,
    pipeline_id: Optional[int] = None,
    ref: Optional[str] = None,
    target_url: Optional[str] = None
) -> Union[Dict, Dict]:
    """
    Set commit pipeline status
    Add or update the pipeline status of a commit using:
        POST /projects/:id/statuses/:sha

    This tool is used to post a status (e.g., pending, success, failed) to a 
    specific commit, typically used by external CI/CD systems to integrate 
    pipeline results into GitLab.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit SHA. (Required)
        state (str): The state of the status. Can be one of: 'pending', 'running', 
                     'success', 'failed', 'canceled', 'skipped'. (Required)
        coverage (Optional[float]): The total code coverage percentage.
        description (Optional[str]): The short description of the status (255 chars or fewer).
        name (Optional[str]): The label to differentiate this status from the status of other systems.
                              Default value is 'default'. Use this or 'context'.
        context (Optional[str]): Alternative name for the label/context (same as 'name').
        pipeline_id (Optional[int]): The ID of the pipeline to set status for (useful for multiple pipelines on the same SHA).
        ref (Optional[str]): The ref (branch or tag) to which the status refers (255 chars or fewer).
        target_url (Optional[str]): The target URL to associate with this status (255 chars or fewer).

    Returns:
        Union[Dict, Dict]:
            - On success (201 Created): A dictionary representing the created status object. Attributes include:
                - id (integer): ID of the status.
                - status (string): State of the commit ('success', 'failed', etc.).
                - name (string): Name/context of the status.
                - sha (string): SHA of the commit.
                - author (object): Information about the status author.
                - created_at (string): Date when the status was created.
                - finished_at (string): Date when the status was finished.
                - coverage (float): Code coverage percentage.
                - description (string): Description of the status.
                - target_url (string): Target URL associated with the status.
                - ref (string): Reference of the commit.
                - allow_failure (boolean): If true, the status allows failure.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx, 5xx, or 422).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/statuses/{sha}"

    # 2. Construct Headers
    headers = {
        'Content-Type': 'application/json' 
    }
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Payload (JSON Body)
    payload = {
        'state': state,
    }

    # Map Python function argument names to Payload fields
    optional_params = {
        'coverage': coverage,
        'description': description,
        'pipeline_id': pipeline_id,
        'ref': ref,
        'target_url': target_url,
    }
    
    # Handle 'name' or 'context' which are aliases
    if name is not None:
        payload['name'] = name
    elif context is not None:
        payload['context'] = context

    # Add other optional parameters, filtering out None values
    for py_name, value in optional_params.items():
        if value is not None:
            payload[py_name] = value

    print(f"\n[SET COMMIT STATUS] Attempting to set status '{state}' for SHA '{sha}' in project {project_id}.")
    
    try:
        # 4. Make the POST request
        response = requests.post(api_url, headers=headers, json=payload)
        
        # 5. Check for 201 Created (Success)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Handle Success: Return the structured JSON content
        print(f"[SET COMMIT STATUS] Successfully set commit status to '{state}'.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (including 422 Unprocessable Entity)
        print(f"[SET COMMIT STATUS] Error setting commit status: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[SET COMMIT STATUS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def list_gitlab_commit_merge_requests(
    project_id: Union[int, str],
    sha: str,
    state: Optional[str] = None
) -> Union[List[Dict], Dict]:
    """
    List merge requests associated with a commit
    Returns information about the merge request that originally introduced a specific commit using:
        GET /projects/:id/repository/commits/:sha/merge_requests

    This function retrieves a list of merge requests that include the specified commit.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit SHA. (Required)
        state (Optional[str]): Returns merge requests with the specified state.
                               Possible values: 'opened', 'closed', 'locked', or 'merged'.
                               Omit this parameter to get all merge requests regardless of state.

    Returns:
        Union[List[Dict], Dict]:
            - On success: A list of merge request objects (dictionaries). Each object includes:
                - id (integer): ID of the merge request.
                - iid (integer): Internal ID of the merge request.
                - project_id (integer): ID of the project.
                - title (string): Title of the merge request.
                - description (string): Description of the merge request.
                - state (string): State of the merge request ('opened', 'merged', etc.).
                - created_at (string): Date when the merge request was created.
                - updated_at (string): Date when the merge request was last updated.
                - source_branch (string): Source branch of the merge request.
                - target_branch (string): Target branch of the merge request.
                - author (object): Information about the merge request author.
                - assignee (object): Information about the merge request assignee.
                - labels (array): Labels associated with the merge request.
                - milestone (object): Milestone associated with the merge request.
                - sha (string): SHA of the merge request.
                - merge_commit_sha (string): SHA of the merge commit.
                - squash_commit_sha (string): SHA of the squash commit.
                - merge_status (string): Merge status of the merge request.
                - merge_when_pipeline_succeeds (boolean): If true, merges when pipeline succeeds.
                - draft (boolean): If true, the merge request is a draft.
                - work_in_progress (boolean): If true, the merge request is set as work in progress.
                - upvotes (integer): Number of upvotes.
                - downvotes (integer): Number of downvotes.
                - user_notes_count (integer): Number of user notes.
                - discussion_locked (boolean): If true, discussions are locked.
                - should_remove_source_branch (boolean): If true, removes source branch after merge.
                - force_remove_source_branch (boolean): If true, forces source branch removal.
                - web_url (string): Web URL of the merge request.
                - time_stats (object): Time tracking statistics.
                - source_project_id (integer): ID of the source project.
                - target_project_id (integer): ID of the target project.
            - On failure: A structured error dictionary.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/merge_requests"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if state is not None:
        params['state'] = state

    print(f"\n[GET COMMIT MRs] Attempting to retrieve merge requests for SHA '{sha}' in project {project_id}.")

    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT MRs] Successfully retrieved associated merge requests.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GET COMMIT MRs] Error retrieving merge requests: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}

    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT MRs] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_commit_signature(
    project_id: Union[int, str],
    sha: str
) -> Union[Dict, Dict]:
    """
    Get commit signature
    Get the signature from a commit, if it is signed, using:
        GET /projects/:id/repository/commits/:sha/signature

    This tool retrieves the signature details (PGP, SSH, or X.509) and verification 
    status for a specific commit. For unsigned commits, this endpoint returns a 404 
    Not Found error.

    Args:
        project_id (Union[int, str]): The ID or URL-encoded path of the project. (Required)
        sha (str): The commit hash or name of a repository branch or tag. (Required)

    Returns:
        Union[Dict, Dict]:
            - On success (Signed Commit): A dictionary representing the signature details. Attributes include:
                - signature_type (string): Type of signature ('PGP', 'SSH', or 'X509').
                - verification_status (string): Verification status of the signature.
                - commit_source (string): Source of the commit (e.g., 'gitaly').
                - gpg_key_id (integer): ID of the GPG key (if PGP signed).
                - gpg_key_primary_keyid (string): Primary key ID of the GPG key (if PGP signed).
                - gpg_key_user_name (string): User name associated with the GPG key (if PGP signed).
                - gpg_key_user_email (string): Email address associated with the GPG key (if PGP signed).
                - key (object): SSH key information (if SSH signed).
                - x509_certificate (object): X.509 certificate information (if X.509 signed).
            - On failure (Unsigned or Error): A structured error dictionary. For unsigned commits, the API
              typically returns a 404 with a specific message.

    Raises:
        requests.exceptions.HTTPError: If the GitLab API request returns a bad status code (4xx or 5xx).
        requests.exceptions.RequestException: For network-related errors during the API call.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/commits/{sha}/signature"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET COMMIT SIGNATURE] Attempting to retrieve signature for SHA/Ref '{sha}' in project {project_id}.")
    
    try:
        # 3. Make the GET request (no payload or optional params needed)
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET COMMIT SIGNATURE] Successfully retrieved commit signature.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        status_code = e.response.status_code
        print(f"[GET COMMIT SIGNATURE] Error retrieving commit signature: HTTP Error {status_code}")
        
        try:
            error_details = e.response.json()
            # Special case for unsigned commit (404)
            if status_code == 404 and error_details.get('message', '').lower() == '404 gpg signature not found':
                 return {"error": "Commit signature not found (Commit is likely unsigned).", "details": error_details}
            
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET COMMIT SIGNATURE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}