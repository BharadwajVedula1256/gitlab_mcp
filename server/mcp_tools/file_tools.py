from typing import Union, Optional
from ..config import mcp, get_gitlab_api, get_gitlab_token
import requests
import urllib.parse
import json

@mcp.tool()
def create_gitlab_file(
    project_id: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    author_email: Optional[str] = None,
    author_name: Optional[str] = None,
    encoding: Optional[str] = 'text', # 'text' or 'base64'
    execute_filemode: Optional[bool] = False,
    start_branch: Optional[str] = None
) -> dict:
    """
    Create a new file in a specific branch of a GitLab repository.

    Use this tool whenever the user asks to:
    - Add a brand-new file to a GitLab project.
    - Commit a file into a specific branch.
    - Specify commit details such as author or encoding.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "74952730" or "my-group/my-project".
    - file_path (string): The full path for the new file. Example: "src/new_script.py".
    - branch (string): The name of the branch where the file will be committed. Example: "main".
    - content (string): The contents of the file (plain text by default, base64 if specified).
    - commit_message (string): A short description of the commit. Example: "Add new script".
    - author_email (string, optional): The email of the commit author. If not provided, the default GitLab account is used.
    - author_name (string, optional): The name of the commit author.
    - encoding (string, optional): File content encoding. Options:
        - "text" (default) → content is plain text.
        - "base64" → content is base64-encoded.
    - execute_filemode (boolean, optional): Set to true if the file should be executable. Default is false.
    - start_branch (string, optional): Base branch to create the new branch from (if the branch doesn’t exist).

    Returns:
    - A dictionary with details about the created file and commit (file path, branch, commit ID, author, etc.).
    """

    # 1. URL Encoding: The file_path must be URL-encoded, as required by the API.
    # We use quote_plus to handle slashes correctly in the path component.
    encoded_file_path = urllib.parse.quote_plus(file_path)
    
    # 2. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/files/{encoded_file_path}"

    # 3. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    # 4. Construct JSON Payload (Data)
    data = {
        'branch': branch,
        'commit_message': commit_message,
        'content': content,
        'encoding': encoding,
        'execute_filemode': execute_filemode
    }
    
    # Add optional parameters if provided
    if author_email:
        data['author_email'] = author_email
    if author_name:
        data['author_name'] = author_name
    if start_branch:
        data['start_branch'] = start_branch

    print(f"Attempting to create file at: {file_path} on branch: {branch}")
    
    try:
        # 5. Make the POST request
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 6. Handle Success
        print(f"Successfully created file: {file_path}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 400 Bad Request, 401 Unauthorized)
        print(f"Error creating file: HTTP Error {e.response.status_code}")
        try:
            # Try to extract the specific error message from the GitLab response body
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        # Handle network-related errors (DNS failure, connection refused, etc.)
        print(f"A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def update_gitlab_file(
    project_id: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    author_email: str = None,
    author_name: str = None,
    encoding: str = 'text', # 'text' or 'base64'
    execute_filemode: bool = False,
    last_commit_id: str = None,
    start_branch: str = None
) -> dict:
    """
    Update the contents of an existing file in a GitLab repository branch.

    Use this tool whenever the user asks to:
    - Edit or replace a file in a GitLab project.
    - Commit changes to a specific branch.
    - Provide commit details such as author, encoding, or last commit ID.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "74952730" or "my-group/my-project".
    - file_path (string): The full path of the file to update. Example: "src/utils/helper.py".
    - branch (string): The branch where the update will be committed. Example: "main".
    - content (string): The new content of the file (plain text by default, or base64 if specified).
    - commit_message (string): Short description of the update. Example: "Update helper function".
    - author_email (string, optional): The commit author's email. Default is the GitLab account email.
    - author_name (string, optional): The commit author's name.
    - encoding (string, optional): File content encoding. Options:
        - "text" (default) → plain text.
        - "base64" → base64-encoded content.
    - execute_filemode (boolean, optional): If true, the file will be executable. Default is false.
    - last_commit_id (string, optional): The last known commit ID for optimistic locking to prevent overwrites.
    - start_branch (string, optional): Base branch to create a new branch from if the target branch doesn’t exist.

    Returns:
    - A dictionary containing information about the updated file and commit (file path, branch, commit ID, author, etc.).
    """    
    # 1. URL Encoding: The file_path must be URL-encoded, as required by the API.
    encoded_file_path = urllib.parse.quote_plus(file_path)
    
    # 2. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/files/{encoded_file_path}"

    # 3. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    # 4. Construct JSON Payload (Data)
    data = {
        'branch': branch,
        'commit_message': commit_message,
        'content': content,
        'encoding': encoding,
        'execute_filemode': execute_filemode
    }
    
    # Add optional parameters
    if author_email:
        data['author_email'] = author_email
    if author_name:
        data['author_name'] = author_name
    if last_commit_id:
        data['last_commit_id'] = last_commit_id
    if start_branch:
        data['start_branch'] = start_branch


    print(f"\n[UPDATE] Attempting to update file at: {file_path} on branch: {branch}")
    
    try:
        # 5. Make the PUT request
        response = requests.put(api_url, headers=headers, json=data)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 6. Handle Success
        print(f"[UPDATE] Successfully updated file: {file_path}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 400 Bad Request: commit was empty or branch updated)
        print(f"[UPDATE] Error updating file: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[UPDATE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def delete_gitlab_file(
    project_id: str,
    file_path: str,
    branch: str,
    commit_message: str,
    author_email: str = None,
    author_name: str = None,
    last_commit_id: str = None,
    start_branch: str = None
) -> dict:
    """
    Delete an existing file from a specific branch in a GitLab repository.

    Use this tool whenever the user asks to:
    - Remove a file from a GitLab project.
    - Commit the deletion to a specific branch.
    - Optionally provide commit details such as author or last commit ID.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "74952730" or "my-group/my-project".
    - file_path (string): The full path of the file to delete. Example: "src/old_script.py".
    - branch (string): The branch where the deletion will be committed. Example: "main".
    - commit_message (string): A short description of the deletion. Example: "Remove outdated script".
    - author_email (string, optional): The commit author’s email. Default is the GitLab account email.
    - author_name (string, optional): The commit author’s name.
    - last_commit_id (string, optional): The last known commit ID for optimistic locking to prevent overwrites.
    - start_branch (string, optional): Base branch to create a new branch from if the target branch doesn’t exist.

    Returns:
    - A dictionary containing the result of the deletion, usually empty if successful, or an error dictionary if it fails.
    """
    # 1. URL Encoding: The file_path must be URL-encoded, as required by the API.
    encoded_file_path = urllib.parse.quote_plus(file_path)
    
    # 2. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/files/{encoded_file_path}"

    # 3. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token(),
        'Content-Type': 'application/json'
    }

    # 4. Construct JSON Payload (Data)
    data = {
        'branch': branch,
        'commit_message': commit_message
    }
    
    # Add optional parameters
    if author_email:
        data['author_email'] = author_email
    if author_name:
        data['author_name'] = author_name
    if last_commit_id:
        data['last_commit_id'] = last_commit_id
    if start_branch:
        data['start_branch'] = start_branch


    print(f"\n[DELETE] Attempting to delete file at: {file_path} on branch: {branch}")
    
    try:
        # 5. Make the DELETE request
        # Note: DELETE requests often return a 204 No Content on success, 
        # so response.json() may fail if successful. We only check for status.
        response = requests.delete(api_url, headers=headers, json=data)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 6. Handle Success (200 OK or 204 No Content)
        print(f"[DELETE] Successfully deleted file: {file_path}")
        
        # Return success status if no content is returned
        if response.status_code == 204:
            return {"status": "success", "message": "File deleted successfully (No Content returned)"}
        
        # Attempt to return JSON if status is 200 (less common for DELETE)
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 400 Bad Request, 404 Not Found)
        print(f"[DELETE] Error deleting file: HTTP Error {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(f"GitLab API Error Details: {json.dumps(error_details, indent=2)}")
            return {"error": str(e), "details": error_details}
        except json.JSONDecodeError:
            print("GitLab API returned an error but no readable JSON details.")
            return {"error": str(e), "details": e.response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"[DELETE] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

mcp.tool()
def get_raw_gitlab_file(
    project_id: str,
    file_path: str,
    ref: str,
    lfs: bool = False
) -> Union[str, dict]:
    """
    Retrieves the raw content (as a string) of a file from a GitLab repository 
    using the GET /projects/:id/repository/files/:file_path/raw endpoint.

    Args:
        gitlab_url (str): The base URL of your GitLab server (e.g., 'https://gitlab.example.com').
        private_token (str): Your GitLab Private Access Token.
        project_id (str): The project ID or URL-encoded path of the project.
        file_path (str): URL-encoded full path to the file.
        ref (str): The name of the branch, tag, or commit.
        lfs (bool, optional): Determines if the response should be Git LFS file contents. Defaults to False.

    Returns:
        str or dict: The raw file content as a string on success, or an error dictionary on failure.
    """
    
    # 1. URL Encoding: The file_path must be URL-encoded, as required by the API.
    encoded_file_path = urllib.parse.quote_plus(file_path)
    
    # 2. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/files/{encoded_file_path}/raw"

    # 3. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 4. Construct Query Parameters
    params = {
        'ref': ref,
        'lfs': lfs
    }

    print(f"\n[GET RAW] Attempting to retrieve raw file content for: {file_path} from ref: {ref}")
    
    try:
        # 5. Make the GET request
        # Note: We do not pass json=data for a GET request.
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 6. Handle Success: Return raw content (response.text)
        print(f"[GET RAW] Successfully retrieved raw content for file: {file_path}")
        return response.text

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[GET RAW] Error retrieving file: HTTP Error {e.response.status_code}")
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
        print(f"[GET RAW] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_file_metadata_and_content(
    project_id: str,
    file_path: str,
    ref: str
) -> dict:
    """
    Retrieve metadata and content of a file from a GitLab repository.

    Use this tool whenever the user asks to:
    - View the contents of a file in a specific branch, tag, or commit.
    - Access file details such as size, encoding, and last commit information.
    - Obtain the file content in Base64 format if needed.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "74952730" or "my-group/my-project".
    - file_path (string): The full path to the file. Example: "src/utils/helper.py".
    - ref (string): The branch, tag, or commit SHA to retrieve the file from. Example: "main".

    Returns:
    - A dictionary containing:
    - Metadata about the file (size, encoding, last commit, etc.).
    - Base64-encoded file content.
    - If the request fails, returns an error dictionary.
    """
    # 1. URL Encoding: The file_path must be URL-encoded.
    encoded_file_path = urllib.parse.quote_plus(file_path)
    
    # 2. Construct the API URL
    # Note: This endpoint is different from the /raw endpoint.
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/files/{encoded_file_path}"

    # 3. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 4. Construct Query Parameters
    params = {
        'ref': ref
    }

    print(f"\n[GET METADATA] Attempting to retrieve file metadata and content for: {file_path} from ref: {ref}")
    
    try:
        # 5. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 6. Handle Success: Return the structured JSON content
        print(f"[GET METADATA] Successfully retrieved file metadata for: {file_path}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[GET METADATA] Error retrieving file: HTTP Error {e.response.status_code}")
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
        print(f"[GET METADATA] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}

@mcp.tool()
def get_gitlab_file_blame(
    project_id: str,
    file_path: str,
    ref: str,
    range_start: int = None,
    range_end: int = None,
    range_hash: str = None
) -> Union[list, dict]:
    """
    Retrieve blame information for a file in a GitLab repository.

    Use this tool whenever the user asks to:
    - See which commits last modified specific lines of a file.
    - Analyze code authorship or history for a file.
    - Optionally focus on a specific line range or commit range.

    Parameters:
    - project_id (string): The GitLab project’s ID or path. Example: "74952730" or "my-group/my-project".
    - file_path (string): The full path to the file. Example: "src/utils/helper.py".
    - ref (string): The branch, tag, or commit SHA to analyze. Example: "main".
    - range_start (integer, optional): The first line number to include in the blame (1-indexed). Default is the first line.
    - range_end (integer, optional): The last line number to include in the blame (1-indexed). Default is the last line.
    - range_hash (string, optional): Blame range hash if available, to limit the scope.

    Returns:
    - A list of blame objects, each containing:
        - Line number
        - Commit ID
        - Author name and email
        - Commit message
    - Returns an error dictionary if the request fails.
    """
    # 1. URL Encoding: The file_path must be URL-encoded.
    encoded_file_path = urllib.parse.quote_plus(file_path)
    
    # 2. Construct the API URL
    api_url = f"{get_gitlab_api()}/projects/{project_id}/repository/files/{encoded_file_path}/blame"

    # 3. Construct Headers
    headers = {
        'PRIVATE-TOKEN': get_gitlab_token()
    }

    # 4. Construct Query Parameters
    params = {
        'ref': ref
    }

    # Conditionally add range parameters, using the correct key format for GitLab API
    if range_start is not None:
        params['range[start]'] = range_start
    if range_end is not None:
        params['range[end]'] = range_end
    if range_hash is not None:
        params['range'] = range_hash

    print(f"\n[GET BLAME] Attempting to retrieve blame information for: {file_path} from ref: {ref}")
    
    try:
        # 5. Make the GET request
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 6. Handle Success: Return the structured JSON content (a list of blame ranges)
        print(f"[GET BLAME] Successfully retrieved blame information for: {file_path}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors (e.g., 404 Not Found)
        print(f"[GET BLAME] Error retrieving blame information: HTTP Error {e.response.status_code}")
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
        print(f"[GET BLAME] A general request error occurred: {e}")
        return {"error": f"Network/Request Error: {e}"}