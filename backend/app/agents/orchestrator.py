"""Pipeline orchestrator - coordinates AI agents for project generation."""

import json
import logging

from app.agents.architect import ArchitectAgent
from app.agents.file_generator import FileGeneratorAgent
from app.agents.improvement import ImprovementAgent
from app.agents.planner import PlannerAgent
from app.schemas.schemas import (
    EditPlan,
    GeneratedFile,
    ProjectArchitecture,
    ProjectSpecification,
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Coordinates the multi-agent pipeline for project generation."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.architect = ArchitectAgent()
        self.file_generator = FileGeneratorAgent()
        self.improvement = ImprovementAgent()

    async def generate_specification(
        self, prompt: str
    ) -> tuple[ProjectSpecification, int]:
        """Step 1: Convert user prompt to project specification."""
        logger.info(f"Generating specification for: {prompt[:100]}...")
        return await self.planner.plan(prompt)

    async def generate_architecture(
        self, spec: ProjectSpecification
    ) -> tuple[ProjectArchitecture, int]:
        """Step 2: Create project architecture from specification."""
        logger.info(f"Generating architecture for: {spec.name}")
        return await self.architect.design(spec)

    async def generate_files(
        self,
        spec: ProjectSpecification,
        arch: ProjectArchitecture,
    ) -> tuple[list[GeneratedFile], int]:
        """Step 3: Generate all project files.

        Returns:
            Tuple of (list of GeneratedFile, total_tokens_used)
        """
        logger.info(f"Generating {len(arch.files)} files...")
        generated_files: list[GeneratedFile] = []
        existing_contents: dict[str, str] = {}
        total_tokens = 0

        for file_entry in arch.files:
            generated, tokens = await self.file_generator.generate_file(
                file_entry=file_entry,
                spec=spec,
                arch=arch,
                existing_files=existing_contents,
            )
            generated_files.append(generated)
            existing_contents[generated.path] = generated.content
            total_tokens += tokens

        logger.info(
            f"Generated {len(generated_files)} files using {total_tokens} tokens"
        )
        return generated_files, total_tokens

    async def generate_project(
        self, prompt: str
    ) -> tuple[ProjectSpecification, ProjectArchitecture, list[GeneratedFile], int]:
        """Run the full generation pipeline.

        Returns:
            Tuple of (spec, architecture, files, total_tokens_used)
        """
        total_tokens = 0

        # Step 1: Specification
        spec, tokens = await self.generate_specification(prompt)
        total_tokens += tokens

        # Step 2: Architecture
        arch, tokens = await self.generate_architecture(spec)
        total_tokens += tokens

        # Step 3: Generate files
        files, tokens = await self.generate_files(spec, arch)
        total_tokens += tokens

        logger.info(
            f"Project generation complete: {spec.name}, "
            f"{len(files)} files, {total_tokens} total tokens"
        )
        return spec, arch, files, total_tokens

    async def plan_edit(
        self,
        prompt: str,
        file_list: list[str],
        file_contents: dict[str, str] | None = None,
    ) -> tuple[EditPlan, int]:
        """Plan which files need editing based on a user prompt."""
        return await self.improvement.plan_edit(prompt, file_list, file_contents)

    async def edit_file(
        self,
        prompt: str,
        file_path: str,
        current_content: str,
        plan: EditPlan,
    ) -> tuple[GeneratedFile, int]:
        """Edit a single file based on a user prompt."""
        return await self.improvement.edit_file(prompt, file_path, current_content, plan)

    def serialize_spec(self, spec: ProjectSpecification) -> str:
        """Serialize a specification to JSON string for storage."""
        return json.dumps(spec.model_dump())

    def serialize_arch(self, arch: ProjectArchitecture) -> str:
        """Serialize an architecture to JSON string for storage."""
        return json.dumps(arch.model_dump())
