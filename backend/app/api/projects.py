"""Project management API routes."""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.orchestrator import PipelineOrchestrator
from app.core.database import get_db
from app.models.models import (
    AIGeneration,
    Deployment,
    DeploymentStatus,
    Project,
    ProjectFile,
    ProjectStatus,
)
from app.schemas.schemas import (
    DeploymentResponse,
    DeployRequest,
    FileEditRequest,
    FileEditResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectFileResponse,
    ProjectResponse,
)
from app.services.deployment import DeploymentService
from app.services.sandbox import SandboxService

router = APIRouter(prefix="/projects", tags=["projects"])

# Service instances
orchestrator = PipelineOrchestrator()
sandbox = SandboxService()
deployment_service = DeploymentService()


@router.post("/generate", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def generate_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    # user: User = Depends(get_current_user),  # Enable when auth is wired
):
    """Generate a new project from a natural language prompt.

    This endpoint triggers the full AI pipeline:
    1. Planner Agent → project specification
    2. Architecture Agent → file map
    3. File Generator Agent → generate all files
    """
    # Create project record
    project = Project(
        # user_id=user.id,  # Enable when auth is wired
        user_id=uuid.uuid4(),  # Placeholder
        name=data.name or "untitled-project",
        prompt=data.prompt,
        status=ProjectStatus.GENERATING,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    try:
        # Run the AI pipeline
        spec, arch, files, total_tokens = await orchestrator.generate_project(data.prompt)

        # Update project with spec and architecture
        project.name = spec.name
        project.description = spec.description
        project.specification = orchestrator.serialize_spec(spec)
        project.architecture = orchestrator.serialize_arch(arch)
        project.status = ProjectStatus.READY

        # Store generated files
        for f in files:
            project_file = ProjectFile(
                project_id=project.id,
                path=f.path,
                content=f.content,
            )
            db.add(project_file)

        # Log the generation
        generation = AIGeneration(
            project_id=project.id,
            agent_name="pipeline",
            prompt=data.prompt,
            response=json.dumps({"files_generated": len(files)}),
            tokens_used=total_tokens,
            cost=total_tokens * 0.00003,  # Approximate cost
        )
        db.add(generation)

        await db.commit()
        await db.refresh(project)

        # Start sandbox container
        try:
            file_dict = {f.path: f.content for f in files}
            project_dir = await sandbox.create_project_directory(
                str(project.id), file_dict
            )
            container_id, preview_url = await sandbox.start_container(
                str(project.id),
                project_dir,
                install_command=arch.install_command,
                dev_command=arch.dev_command,
                port=arch.port,
            )
            project.container_id = container_id
            project.preview_url = preview_url
            await db.commit()
            await db.refresh(project)
        except Exception as e:
            # Sandbox failure is non-fatal - project is still generated
            project.preview_url = f"Sandbox error: {e}"
            await db.commit()

    except Exception as e:
        project.status = ProjectStatus.ERROR
        project.description = str(e)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Project generation failed: {e}",
        )

    return project


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get project details including files."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.files))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/files", response_model=list[ProjectFileResponse])
async def get_project_files(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all files for a project."""
    result = await db.execute(
        select(ProjectFile).where(ProjectFile.project_id == project_id)
    )
    return result.scalars().all()


@router.post("/{project_id}/files/{file_id}/edit", response_model=FileEditResponse)
async def edit_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    data: FileEditRequest,
    db: AsyncSession = Depends(get_db),
):
    """Edit a project file using a natural language prompt."""
    # Get the file
    result = await db.execute(
        select(ProjectFile).where(
            ProjectFile.id == file_id,
            ProjectFile.project_id == project_id,
        )
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Get all project files for context
    all_files_result = await db.execute(
        select(ProjectFile).where(ProjectFile.project_id == project_id)
    )
    all_files = all_files_result.scalars().all()
    file_list = [f.path for f in all_files]
    file_contents = {f.path: f.content for f in all_files}

    # Plan the edit
    plan, plan_tokens = await orchestrator.plan_edit(data.prompt, file_list, file_contents)

    # Edit the file
    generated, edit_tokens = await orchestrator.edit_file(
        data.prompt, file.path, file.content, plan
    )

    # Update the file
    file.content = generated.content
    file.version += 1

    # Log the generation
    generation = AIGeneration(
        project_id=project_id,
        agent_name="improvement",
        prompt=data.prompt,
        response=json.dumps({"file": file.path, "changes": plan.changes_description}),
        tokens_used=plan_tokens + edit_tokens,
        cost=(plan_tokens + edit_tokens) * 0.00003,
    )
    db.add(generation)

    await db.commit()
    await db.refresh(file)

    return FileEditResponse(
        file=ProjectFileResponse.model_validate(file),
        changes_description=plan.changes_description,
    )


@router.post("/{project_id}/deploy", response_model=DeploymentResponse)
async def deploy_project(
    project_id: uuid.UUID,
    data: DeployRequest,
    db: AsyncSession = Depends(get_db),
):
    """Deploy a project to a cloud provider."""
    # Get project and files
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.files))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != ProjectStatus.READY:
        raise HTTPException(
            status_code=400, detail="Project is not ready for deployment"
        )

    # Create deployment record
    deployment = Deployment(
        project_id=project.id,
        provider=data.provider,
        status=DeploymentStatus.BUILDING,
    )
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)

    try:
        file_dict = {f.path: f.content for f in project.files}
        url, build_log = await deployment_service.deploy(
            data.provider, project.name, file_dict
        )
        deployment.url = url
        deployment.build_log = build_log
        deployment.status = DeploymentStatus.DEPLOYED
        project.status = ProjectStatus.DEPLOYED
    except Exception as e:
        deployment.build_log = str(e)
        deployment.status = DeploymentStatus.FAILED

    await db.commit()
    await db.refresh(deployment)
    return deployment


@router.get("/{project_id}/preview-url")
async def get_preview_url(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get the preview URL for a running project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "preview_url": project.preview_url,
        "status": project.status,
        "container_id": project.container_id,
    }
