"""File Generator Agent - generates individual file contents."""

import json
import logging

from app.agents.base import BaseAgent
from app.schemas.schemas import (
    FileMapEntry,
    GeneratedFile,
    ProjectArchitecture,
    ProjectSpecification,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert full-stack developer. Generate the complete content
for a single file in a Next.js + TailwindCSS project.

Return ONLY valid JSON with this structure:
{
    "path": "the/file/path.tsx",
    "content": "the complete file content as a string",
    "language": "typescript"
}

Requirements:
- Write production-quality, well-structured code
- Use TypeScript for all .ts and .tsx files
- Use TailwindCSS for styling (no custom CSS unless necessary)
- Include proper imports and exports
- Use modern React patterns (hooks, server components where appropriate)
- Make the code complete and functional"""


class FileGeneratorAgent(BaseAgent):
    """Generates individual file contents based on the architecture."""

    async def generate_file(
        self,
        file_entry: FileMapEntry,
        spec: ProjectSpecification,
        arch: ProjectArchitecture,
        existing_files: dict[str, str] | None = None,
    ) -> tuple[GeneratedFile, int]:
        """Generate a single file's content.

        Args:
            file_entry: The file to generate.
            spec: Project specification for context.
            arch: Project architecture for context.
            existing_files: Already generated files for reference.

        Returns:
            Tuple of (GeneratedFile, tokens_used)
        """
        context = {
            "project": spec.model_dump(),
            "file_to_generate": file_entry.model_dump(),
            "all_files": [f.path for f in arch.files],
        }
        if existing_files and file_entry.dependencies:
            context["dependency_contents"] = {
                dep: existing_files[dep]
                for dep in file_entry.dependencies
                if dep in existing_files
            }

        data, tokens = await self._call_openai_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Generate the file content:\n{json.dumps(context, indent=2)}",
            temperature=0.3,
            max_tokens=4096,
        )
        generated = GeneratedFile(**data)
        logger.info(f"Generated file: {generated.path} ({len(generated.content)} chars)")
        return generated, tokens
