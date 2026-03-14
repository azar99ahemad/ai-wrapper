"""Pydantic schemas for API request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.models import DeploymentProvider, DeploymentStatus, PlanType, ProjectStatus


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    plan: PlanType
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Project ---
class ProjectCreate(BaseModel):
    prompt: str = Field(min_length=10, max_length=5000)
    name: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    prompt: str
    status: ProjectStatus
    preview_url: str | None
    git_repo_url: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetailResponse(ProjectResponse):
    specification: str | None
    architecture: str | None
    files: list["ProjectFileResponse"] = []


# --- Project Files ---
class ProjectFileResponse(BaseModel):
    id: uuid.UUID
    path: str
    content: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FileEditRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=2000)


class FileEditResponse(BaseModel):
    file: ProjectFileResponse
    changes_description: str


# --- AI Generation ---
class GenerationResponse(BaseModel):
    id: uuid.UUID
    agent_name: str
    prompt: str
    response: str
    tokens_used: int
    cost: float
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Deployment ---
class DeployRequest(BaseModel):
    provider: DeploymentProvider


class DeploymentResponse(BaseModel):
    id: uuid.UUID
    provider: DeploymentProvider
    status: DeploymentStatus
    url: str | None
    build_log: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Usage ---
class UsageLimitResponse(BaseModel):
    month: str
    generation_count: int
    limit: int

    model_config = {"from_attributes": True}


# --- AI Agent Internal Schemas ---
class ProjectSpecification(BaseModel):
    """Output of the Planner Agent."""

    name: str
    description: str
    features: list[str]
    tech_stack: dict[str, str]
    pages: list[str]
    api_endpoints: list[str] | None = None


class FileMapEntry(BaseModel):
    """Single file in the architecture."""

    path: str
    description: str
    dependencies: list[str] = []


class ProjectArchitecture(BaseModel):
    """Output of the Architecture Agent."""

    files: list[FileMapEntry]
    folder_structure: str
    install_command: str = "npm install"
    dev_command: str = "npm run dev"
    port: int = 3000


class GeneratedFile(BaseModel):
    """Output of the File Generator Agent."""

    path: str
    content: str
    language: str


class DebugResult(BaseModel):
    """Output of the Debug Agent."""

    fixed_files: list[GeneratedFile]
    errors_found: list[str]
    errors_fixed: list[str]


class EditPlan(BaseModel):
    """Output of the Improvement Agent planning step."""

    affected_files: list[str]
    changes_description: str
    new_files: list[str] = []
