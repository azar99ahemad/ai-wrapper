"""Architecture Agent - creates project folder structure and file list."""

import json
import logging

from app.agents.base import BaseAgent
from app.schemas.schemas import ProjectArchitecture, ProjectSpecification

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert software architect. Given a project specification,
design the complete file structure for a Next.js + TailwindCSS project.

Return ONLY valid JSON with this structure:
{
    "files": [
        {
            "path": "package.json",
            "description": "Project dependencies and scripts",
            "dependencies": []
        },
        {
            "path": "src/app/page.tsx",
            "description": "Main landing page",
            "dependencies": ["src/components/Header.tsx"]
        }
    ],
    "folder_structure": "A text representation of the folder tree",
    "install_command": "npm install",
    "dev_command": "npm run dev",
    "port": 3000
}

Include all necessary files: package.json, tailwind.config.ts, tsconfig.json,
next.config.js, layout files, page files, component files, API routes, etc.
Order files so dependencies come before dependents."""


class ArchitectAgent(BaseAgent):
    """Creates project folder structure and file list from a specification."""

    async def design(self, spec: ProjectSpecification) -> tuple[ProjectArchitecture, int]:
        """Design the project architecture from a specification.

        Returns:
            Tuple of (ProjectArchitecture, tokens_used)
        """
        data, tokens = await self._call_openai_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Design the file structure for this project:\n{json.dumps(spec.model_dump(), indent=2)}",
            temperature=0.5,
            max_tokens=4096,
        )
        arch = ProjectArchitecture(**data)
        logger.info(f"Designed architecture with {len(arch.files)} files")
        return arch, tokens
