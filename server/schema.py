from typing import Optional
from pydantic import BaseModel, Field

# Pydantic models for the tool inputs and outputs
class CreateRepositoryOptions(BaseModel):
    """Options for creating a GitLab repository"""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    visibility: Optional[str] = Field("private", description="Visibility level: private, internal, or public")
    initialize_with_readme: Optional[bool] = Field(False, description="Initialize with README")

class GitLabRepository(BaseModel):
    """GitLab repository model"""
    id: int
    name: str
    path: str
    description: str
    visibility: str
    readme_url: Optional[str] = None

class GitLabCreateUpdateFileResponse(BaseModel):
    file_path: str
    content: str
    encoding: str
    commit_id: str
    last_commit_id: str
    web_url: Optional[str] = None