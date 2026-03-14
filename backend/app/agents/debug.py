"""Debug Agent - automatically fixes compile/build errors."""

import json
import logging

from app.agents.base import BaseAgent
from app.schemas.schemas import DebugResult, GeneratedFile

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert debugger for Next.js + TailwindCSS projects.
Given build/compile errors and the relevant source files, fix the errors.

Return ONLY valid JSON with this structure:
{
    "fixed_files": [
        {
            "path": "src/app/page.tsx",
            "content": "complete fixed file content",
            "language": "typescript"
        }
    ],
    "errors_found": ["description of error 1", "description of error 2"],
    "errors_fixed": ["how error 1 was fixed", "how error 2 was fixed"]
}

Fix all errors while preserving the intended functionality.
Only include files that actually needed changes."""


class DebugAgent(BaseAgent):
    """Automatically fixes compile/build errors in generated code."""

    async def fix(
        self,
        error_output: str,
        files: dict[str, str],
    ) -> tuple[DebugResult, int]:
        """Analyze build errors and fix the relevant files.

        Args:
            error_output: The build/compile error output.
            files: Dict mapping file paths to their content.

        Returns:
            Tuple of (DebugResult, tokens_used)
        """
        context = {
            "errors": error_output,
            "files": files,
        }
        data, tokens = await self._call_openai_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Fix these build errors:\n{json.dumps(context, indent=2)}",
            temperature=0.2,
            max_tokens=4096,
        )
        # Parse fixed files
        fixed_files = [GeneratedFile(**f) for f in data.get("fixed_files", [])]
        result = DebugResult(
            fixed_files=fixed_files,
            errors_found=data.get("errors_found", []),
            errors_fixed=data.get("errors_fixed", []),
        )
        logger.info(
            f"Debug agent fixed {len(result.errors_fixed)} of {len(result.errors_found)} errors"
        )
        return result, tokens
