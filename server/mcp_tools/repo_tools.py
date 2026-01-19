"""
MCP Tools for GitLab Server
"""
from typing import Optional, List, Union, Dict, Iterable
import requests
import json
from ..config import mcp, get_gitlab_api, get_gitlab_token
import httpx
from ..schema import GitLabRepository

# Modified create_repository function from server/mcp_tools/repo_tools.py
@mcp.tool()
def list_gitlab_repository_tree(
    project_id: str,
    ref: str = None,
    path: str = None,
    recursive: bool = False,
    per_page: int = None,
    page_token: str = None,
    pagination: str = None
) -> Union[List, Dict]:
    """
    List the contents (files and directories) of a GitLab repository.

    Use this tool whenever the user asks to:
    - Browse files and folders in a repository.
    - Explore the structure of a branch, tag, or commit.
    - Optionally retrieve the contents recursively or paginate results.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - ref (string, optional): Branch, tag, or commit to list. Defaults to the repository’s default branch.
    - path (string, optional): Path inside the repository to list. Example: "src/components".
    - recursive (boolean, optional): If true, list all files and folders recursively. Default is False.
    - per_page (integer, optional): Number of results per page for traditional pagination. Default is 20.
    - page_token (string, optional): Token for keyset pagination to fetch the next page.
    - pagination (string, optional): Use 'keyset' for keyset-based pagination instead of page/per_page.

    Returns:
    - A list of tree objects (files/folders), each containing:
        - name
        - type (file or directory)
        - path
        - size
    - Returns an error dictionary if the request fails.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/tree"

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 3. Construct Query Parameters
    params = {}
    
    if ref:
        params['ref'] = ref
    if path:
        # While the API documentation suggests the path itself is not strictly URL-encoded,
        # encoding it here ensures robustness for paths containing special characters.
        params['path'] = path 
    if recursive:
        params['recursive'] = 'true'
    
    # Pagination parameters
    if per_page is not None:
        params['per_page'] = per_page
    if page_token:
        params['page_token'] = page_token
    if pagination:
        params['pagination'] = pagination

    print(f"\n[LIST TREE] Attempting to list contents for project {project_id} at path '{path}' on ref '{ref}'")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the list of tree objects
        print(f"[LIST TREE] Successfully retrieved repository tree.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[LIST TREE] Error retrieving repository tree: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[LIST TREE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}


@mcp.tool()
def get_gitlab_blob(
    project_id: str,
    sha: str
) -> Dict:
    """
    Retrieve information and content of a blob in a GitLab repository.

    Use this tool whenever the user asks to:
    - Access the contents of a specific blob by its SHA.
    - Inspect metadata such as size and encoding for the blob.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - sha (string): The SHA hash of the blob to retrieve. Example: "a1b2c3d4e5f6...".

    Returns:
    - A dictionary containing:
        - Metadata about the blob (size, encoding, etc.)
        - Base64-encoded content of the blob
    - Returns an error dictionary if the request fails.
    """    
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/blobs/{sha}"

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    print(f"\n[GET BLOB] Attempting to retrieve blob with SHA: {sha} for project {project_id}")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the structured JSON content
        print(f"[GET BLOB] Successfully retrieved blob: {sha}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[GET BLOB] Error retrieving blob: HTTP Error {e.response.status_code}")
        try:
            # Try to parse error details if the response body is JSON
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback if error body is not JSON or is empty
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET BLOB] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_raw_gitlab_blob(
    project_id: str,
    sha: str
) -> Union[str, Dict]:
    """
    Retrieve the raw contents of a blob in a GitLab repository.

    Use this tool whenever the user asks to:
    - Get the raw text of a file or blob by its SHA.
    - Access the file content without metadata or Base64 encoding.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - sha (string): The SHA hash of the blob to retrieve. Example: "a1b2c3d4e5f6...".

    Returns:
    - The raw content of the blob as a string.
    - If the request fails, returns an error dictionary.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/blobs/{sha}/raw"

    # 2. Construct Headers (only include token if provided/needed)
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    print(f"\n[GET RAW BLOB] Attempting to retrieve raw content for blob with SHA: {sha} for project {project_id}")
    
    try:
        # 3. Make the GET request
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Handle Success: Return the raw content as a string
        print(f"[GET RAW BLOB] Successfully retrieved raw content for blob: {sha}")
        return response.text

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[GET RAW BLOB] Error retrieving blob raw content: HTTP Error {e.response.status_code}")
        try:
            # Try to parse error details if the response body is JSON
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback if error body is not JSON or is empty
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET RAW BLOB] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_file_archive(
    project_id: str,
    sha: str = None,
    path: str = None,
    format_suffix: str = 'tar.gz'
) -> Union[bytes, Dict]:
    """
    Download a compressed archive of a GitLab repository or a specific subpath.

    Use this tool whenever the user asks to:
    - Get a snapshot of a repository at a specific branch, tag, or commit.
    - Download the repository or a subdirectory as a compressed archive.
    - Choose the archive format (zip, tar.gz, bz2).

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - sha (string, optional): Branch, tag, or commit to download. Defaults to the repository’s default branch. Example: "main".
    - path (string, optional): Subpath inside the repository to download. Defaults to the entire repository. Example: "src/components".
    - format_suffix (string, optional): Archive format. Options: "zip", "tar.gz" (default), "bz2".

    Returns:
    - The raw binary content of the archive as bytes.
    - Returns an error dictionary if the request fails.
    """
    # 1. Construct the API URL with the format suffix
    # The format must be appended directly to the URL before query params.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/archive.{format_suffix}"

    # 2. Construct Headers
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if sha:
        params['sha'] = sha
    if path:
        # requests.get will handle URL-encoding for query parameters like path
        params['path'] = path

    print(f"\n[GET ARCHIVE] Attempting to retrieve repository archive for project {project_id} (Ref: {sha or 'default'}, Path: {path or 'root'}, Format: {format_suffix})")
    
    try:
        # 4. Make the GET request
        # response.content returns bytes, which is appropriate for binary archives.
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the raw binary content
        print(f"[GET ARCHIVE] Successfully retrieved repository archive in {format_suffix} format.")
        return response.content

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[GET ARCHIVE] Error retrieving archive: HTTP Error {e.response.status_code}")
        try:
            # Try to parse error details if the response body is JSON
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback if error body is not JSON or is empty
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET ARCHIVE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def compare_gitlab_refs(
    project_id: str,
    from_ref: str,
    to_ref: str,
    from_project_id: Union[int, str] = None,
    straight: bool = False
) -> Dict:
    """
    Compare two branches, tags, or commits in a GitLab repository.

    Use this tool whenever the user asks to:
    - See the differences between two refs (branches, tags, or commits).
    - Get commits, file changes, and diffs between two points in the repository.
    - Optionally compare across projects or use a direct vs merge-base comparison.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - from_ref (string): Starting commit SHA, branch, or tag. Example: "main".
    - to_ref (string): Ending commit SHA, branch, or tag. Example: "feature-branch".
    - from_project_id (string or int, optional): Project ID to compare 'from' if it differs from `project_id`.
    - straight (boolean, optional): Comparison method:
        - True → direct comparison (`from..to`)
        - False → comparison using merge base (`from...to`, default)

    Returns:
    - A dictionary containing:
        - Commits between the refs
        - Diffs for each changed file
        - Summary of additions, deletions, and changes
    - Returns an error dictionary if the request fails.
    """  
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/compare"

    # 2. Construct Headers (only include token if provided/needed)
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {
        'from': from_ref,
        'to': to_ref,
        'straight': straight
    }

    if from_project_id is not None:
        params['from_project_id'] = from_project_id

    print(f"\n[COMPARE REFS] Attempting to compare refs for project {project_id}: {from_ref} -> {to_ref} (Straight: {straight})")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[COMPARE REFS] Successfully retrieved comparison results.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[COMPARE REFS] Error comparing refs: HTTP Error {e.response.status_code}")
        try:
            # Try to parse error details if the response body is JSON
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback if error body is not JSON or is empty
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[COMPARE REFS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def get_gitlab_contributors(
    project_id: str,
    order_by: str = None,
    sort: str = None
) -> Union[List, Dict]:
    """
    Retrieve the list of contributors for a GitLab repository.

    Use this tool whenever the user asks to:
    - See who has contributed to a project and how many commits they made.
    - Optionally order or sort contributors by name, email, or commit count.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - order_by (string, optional): Field to order contributors by. Options:
        - "name" → order alphabetically by contributor name
        - "email" → order by email
        - "commits" → order by number of commits (default)
    - sort (string, optional): Sorting direction. Options:
        - "asc" → ascending order (default)
        - "desc" → descending order

    Returns:
    - A list of contributor objects, each containing:
        - name
        - email
        - number of commits
    - Returns an error dictionary if the request fails.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/contributors"

    # 2. Construct Headers (only include token if provided/needed)
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {}
    if order_by:
        # Validate and set order_by, ensuring it is lowercased for consistency
        valid_orders = ['name', 'email', 'commits']
        if order_by.lower() not in valid_orders:
            print(f"[GET CONTRIBUTORS] Warning: Invalid 'order_by' value '{order_by}'. Must be one of {valid_orders}. Using default.")
        else:
            params['order_by'] = order_by.lower()
        
    if sort:
        # Validate and set sort, ensuring it is lowercased
        valid_sorts = ['asc', 'desc']
        if sort.lower() not in valid_sorts:
            print(f"[GET CONTRIBUTORS] Warning: Invalid 'sort' value '{sort}'. Must be one of {valid_sorts}. Using default.")
        else:
            params['sort'] = sort.lower()

    print(f"\n[GET CONTRIBUTORS] Attempting to retrieve contributors list for project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content (a list of contributors)
        print(f"[GET CONTRIBUTORS] Successfully retrieved contributors list.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found, 401 Unauthorized)
        print(f"[GET CONTRIBUTORS] Error retrieving contributors: HTTP Error {e.response.status_code}")
        try:
            # Try to parse error details if the response body is JSON
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback if error body is not JSON or is empty
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET CONTRIBUTORS] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_merge_base(
    project_id: str,
    refs: Iterable[str]
) -> Dict:
    """
    Find the common ancestor (merge base) of two or more branches, tags, or commits in a GitLab repository.

    Use this tool whenever the user asks to:
    - Determine the shared commit ancestor for multiple refs.
    - Analyze differences or prepare for merges between branches/tags/commits.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - refs (list of strings): Two or more commit SHAs, branch names, or tags to find the common ancestor of. Example: ["main", "feature/login"].

    Returns:
    - A commit object representing the merge base, including:
        - commit SHA
        - author name and email
        - commit message
        - timestamp
    - Returns an error dictionary if the request fails.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/merge_base"

    # 2. Construct Headers (only include token if provided/needed)
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    # The API expects 'refs[]' repeated for each reference, which requests.get handles
    # automatically when passing a list/tuple to a parameter.
    params = {'refs': list(refs)}
    
    # Basic validation
    if len(refs) < 2:
        return {"error": "Invalid Input", "details": "The 'refs' list must contain at least two references (SHA, branch, or tag) to find a common merge base."}

    print(f"\n[GET MERGE BASE] Attempting to find merge base for refs: {', '.join(refs)} in project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the commit object for the merge base
        print(f"[GET MERGE BASE] Successfully retrieved merge base.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found, 400 Bad Request)
        print(f"[GET MERGE BASE] Error retrieving merge base: HTTP Error {e.response.status_code}")
        try:
            # Try to parse error details if the response body is JSON
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            # Fallback if error body is not JSON or is empty
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GET MERGE BASE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def add_gitlab_changelog_data(
    project_id: str,
    version: str,
    branch: str = None,
    config_file: str = None,
    date: str = None,
    file: str = None,
    from_ref: str = None,
    message: str = None,
    to_ref: str = None,
    trailer: str = None
) -> Dict:
    """
    Add changelog data to a GitLab repository based on commits.

    Use this tool whenever the user asks to:
    - Create or update a changelog file for a specific version.
    - Include commits from a branch or commit range.
    - Optionally specify commit messages, changelog file, release date, or configuration.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - version (string): Semantic version for the changelog. Example: "1.0.0".
    - branch (string, optional): Branch to commit changelog changes. Defaults to the repository’s default branch.
    - config_file (string, optional): Path to changelog config file. Defaults to ".gitlab/changelog_config.yml".
    - date (string, optional): Release date (ISO 8601 format). Defaults to current date/time.
    - file (string, optional): Changelog file to update. Defaults to "CHANGELOG.md".
    - from_ref (string, optional): Start commit SHA for the changelog (exclusive).
    - to_ref (string, optional): End commit SHA for the changelog (inclusive). Defaults to `branch`.
    - message (string, optional): Commit message. Defaults to "Add changelog for version X".
    - trailer (string, optional): Git trailer to filter commits. Defaults to "Changelog".

    Returns:
    - A dictionary with the GitLab API response on success.
    - Returns an error dictionary if the request fails.
    """
    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/changelog"

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/x-www-form-urlencoded' # Using form-urlencoded for simple key/value data
    }

    # 3. Construct Payload (Data)
    data = {
        'version': version
    }

    # Add optional parameters
    if branch:
        data['branch'] = branch
    if config_file:
        data['config_file'] = config_file
    if date:
        data['date'] = date
    if file:
        data['file'] = file
    if from_ref:
        data['from'] = from_ref
    if message:
        data['message'] = message
    if to_ref:
        data['to'] = to_ref
    if trailer:
        data['trailer'] = trailer

    print(f"\n[ADD CHANGELOG] Attempting to generate and commit changelog for version: {version} in project {project_id}.")
    
    try:
        # 4. Make the POST request
        # Note: requests uses 'data=data' for application/x-www-form-urlencoded
        response = requests.post(api_url, headers=headers, data=data)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[ADD CHANGELOG] Successfully generated and committed changelog for version {version}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 400 Bad Request: missing 'from' or invalid version)
        print(f"[ADD CHANGELOG] Error adding changelog data: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[ADD CHANGELOG] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def generate_gitlab_changelog_data(
    project_id: str,
    version: str,
    config_file: str = None,
    date: str = None,
    from_ref: str = None,
    to_ref: str = None,
    trailer: str = None
) -> Dict:
    """
    Generate changelog data from a GitLab repository without committing it to a file.

    Use this tool whenever the user asks to:
    - Preview the changelog for a specific version.
    - Get commit notes or release notes in JSON format.
    - Optionally filter by commit range, date, or Git trailer.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - version (string): Semantic version to generate the changelog for. Example: "1.0.0".
    - config_file (string, optional): Path to changelog configuration file. Defaults to ".gitlab/changelog_config.yml".
    - date (string, optional): Release date (ISO 8601 format). Defaults to current date/time.
    - from_ref (string, optional): Start commit SHA for the changelog (exclusive).
    - to_ref (string, optional): End commit SHA for the changelog (inclusive).
    - trailer (string, optional): Git trailer to filter commits. Defaults to "Changelog".

    Returns:
    - A dictionary containing the structured changelog data, typically including a 'notes' field.
    - Returns an error dictionary if the request fails.
    """

    # 1. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/changelog"

    # 2. Construct Headers (include token if provided)
    headers = {}
    if get_gitlab_token():
        headers['PRIVATE-TOKEN'] = get_gitlab_token()

    # 3. Construct Query Parameters
    params = {
        'version': version
    }

    # Add optional parameters
    if config_file:
        params['config_file'] = config_file
    if date:
        params['date'] = date
    if from_ref:
        params['from'] = from_ref
    if to_ref:
        params['to'] = to_ref
    if trailer:
        params['trailer'] = trailer

    print(f"\n[GENERATE CHANGELOG] Attempting to generate changelog data for version: {version} in project {project_id}.")
    
    try:
        # 4. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the structured JSON content
        print(f"[GENERATE CHANGELOG] Successfully generated changelog data for version {version}.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[GENERATE CHANGELOG] Error generating changelog data: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[GENERATE CHANGELOG] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}
    
@mcp.tool()
def update_gitlab_submodule_reference(
    project_id: str,
    submodule_path: str,
    branch: str,
    commit_sha: str,
    commit_message: str = None
) -> Dict:
    """
    Update an existing Git submodule reference in a GitLab repository.

    Use this tool whenever the user asks to:
    - Point a submodule to a specific commit SHA.
    - Commit the submodule update to a branch, optionally with a custom message.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "my-group/my-project".
    - submodule_path (string): Full path to the submodule. Example: "lib/modules/example".
    - branch (string): Branch to commit the submodule update to. Example: "main".
    - commit_sha (string): Commit SHA to set the submodule to. Example: "a1b2c3d4e5f6".
    - commit_message (string, optional): Custom commit message. Defaults to GitLab’s automatic message if not provided.

    Returns:
    - A dictionary representing the commit object created by the submodule update.
    - Returns an error dictionary if the request fails.
    """
    # 1. Construct the API URL (Note: submodule_path must be URL-encoded)
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/submodules/{submodule_path}"

    # 2. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # 3. Construct Payload (Data)
    data = {
        'branch': branch,
        'commit_sha': commit_sha,
    }

    if commit_message:
        data['commit_message'] = commit_message
    
    print(f"\n[UPDATE SUBMODULE] Attempting to update submodule '{submodule_path}' to SHA '{commit_sha}' on branch '{branch}'.")
    
    try:
        # 4. Make the PUT request
        response = requests.put(api_url, headers=headers, data=data)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 5. Handle Success: Return the commit object
        print(f"[UPDATE SUBMODULE] Successfully updated submodule reference.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        print(f"[UPDATE SUBMODULE] Error updating submodule: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[UPDATE SUBMODULE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
async def create_repository(
    name: str,
    description: Optional[str] = None,
    visibility: Optional[str] = "private", 
    initialize_with_readme: Optional[bool] = False
) -> GitLabRepository:
    """
    Create a new GitLab project (repository).

    Use this tool whenever the user asks to:
    - Create a new project or repository in GitLab.
    - Set up a project with a specific name, description, or visibility.
    - Optionally initialize the project with a README file.

    Parameters:
    - name (string): The name of the project. Example: "my-awesome-project".
    - description (string, optional): A short description of the project. Example: "A demo repository for testing MCP".
    - visibility (string, optional): Who can see the project. Options:
        - "private" (default): Only project members can access.
        - "internal": Any logged-in user can access.
        - "public": Visible to everyone.
    - initialize_with_readme (boolean, optional): If true, create the project with an initial README.md file. Default is false.

    Returns:
    - A dictionary with details of the created project (project ID, name, description, visibility, URLs, etc.).
    """
    try:
        # Validate parameters before making API call
        if not name:
            raise ValueError("Repository name is required")
            
        if visibility and visibility not in ['private', 'internal', 'public']:
            raise ValueError("Visibility must be 'private', 'internal', or 'public'")
        
        # Prepare request payload
        payload = {
            "name": name,
            "description": description,
            "visibility": visibility,
            "initialize_with_readme": initialize_with_readme
        }
        
        # Filter out None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Make POST request to GitLab API
        response = await client.post(
            f"{get_gitlab_api()}/projects",
            json=payload
        )
        
        # Enhanced error handling for better debugging
        if response.status_code == 400:
            error_detail = response.json()
            if isinstance(error_detail, dict) and 'message' in error_detail:
                raise Exception(f"Bad Request - {error_detail['message']}")
            else:
                raise Exception("Bad Request - invalid parameters provided")
        elif response.status_code == 401:
            raise Exception("Authentication Failed - Please check that get_gitlab_token() environment variable is set correctly")
        elif response.status_code == 403:
            raise Exception("Access Denied - Your GitLab account doesn't have permission to create projects")
        elif response.status_code == 409:
            raise Exception("Conflict - A repository with this name already exists")
        
        response.raise_for_status()
        
        # Parse and return the response
        data = response.json()
        return GitLabRepository(
            id=data["id"],
            name=data["name"],
            path=data["path"],
            description=data.get("description", ""),
            visibility=data["visibility"],
            readme_url=data.get("readme_url")
        )
        
    except httpx.HTTPError as e:
        # Improved error reporting with status codes
        if e.response:
            raise Exception(f"GitLab API error {e.response.status_code}: {e.response.reason_phrase}") from e
        else:
            raise Exception(f"Network error connecting to GitLab API: {e}") from e
    except ValueError as e:
        raise Exception(f"Parameter validation error: {e}") from e
    except KeyError as e:
        raise Exception(f"Missing expected field in GitLab response: {e}") from e
    except Exception as e:
        # Catch-all for unexpected errors
        raise Exception(f"Unexpected error during repository creation: {e}") from e
    
# Search repositories tool
@mcp.tool()
async def search_repositories(
    search: str,
    page: Optional[int] = 1,
    per_page: Optional[int] = 20
) -> list:
    """
    Search for GitLab projects (repositories) by keyword.

    Use this tool whenever the user asks to:
    - Find an existing project or repository in GitLab.
    - Look up projects by name, keyword, or description.
    - Browse available projects matching a search term.

    Parameters:
    - search (string): The keyword or phrase to search for. Example: "fastmcp".
    - page (integer, optional): Page number of results for pagination. Default is 1 (first page).
    - per_page (integer, optional): How many results to return per page. Default is 20.

    Returns:
    - A list of repositories matching the search query. Each item includes details such as:
    - project ID
    - name
    - path
    - description
    - visibility (private/internal/public)
    - URLs and metadata
    """
    try:
        # Make GET request to GitLab API for project search
        params = {
            "search": search,
            "page": page,
            "per_page": per_page
        }
        
        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = await client.get(
            f"{get_gitlab_api()}/projects",
            params=params
        )
        
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Return raw dictionary data instead of Pydantic models
        repositories = []
        for item in data:
            repositories.append({
                "id": item["id"],
                "name": item["name"], 
                "path": item["path"],
                "description": item.get("description", ""),
                "visibility": item["visibility"],
                "readme_url": item.get("readme_url")
            })
        
        return repositories
        
    except httpx.HTTPError as e:
        raise Exception(f"GitLab API error: {e.response.reason_phrase}") from e
    except KeyError as e:
        raise Exception(f"Missing expected field in GitLab response: {e}") from e