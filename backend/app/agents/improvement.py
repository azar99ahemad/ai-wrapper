"""Improvement Agent - updates files based on user prompts."""

import json
import logging

from app.agents.base import BaseAgent
from app.schemas.schemas import EditPlan, GeneratedFile

logger = logging.getLogger(__name__)

PLAN_SYSTEM_PROMPT = """You are an expert software architect. Given a user's edit request
and the current project files, determine which files need to be modified and what changes
are needed.

Return ONLY valid JSON with this structure:
{
    "affected_files": ["src/app/page.tsx", "src/components/Nav.tsx"],
    "changes_description": "Description of the changes to make",
    "new_files": ["src/components/AuthButton.tsx"]
}

Be precise about which files are affected. Include new files if the request requires them."""

EDIT_SYSTEM_PROMPT = """You are an expert full-stack developer. Given a user's edit request,
the current file content, and the edit plan, generate the updated file.

Return ONLY valid JSON with this structure:
{
    "path": "the/file/path.tsx",
    "content": "the complete updated file content",
    "language": "typescript"
}

Make the requested changes while preserving existing functionality.
Return the COMPLETE file content, not just the changes."""


class ImprovementAgent(BaseAgent):
    """Updates project files based on user edit prompts."""

    async def plan_edit(
        self,
        prompt: str,
        file_list: list[str],
        file_contents: dict[str, str] | None = None,
    ) -> tuple[EditPlan, int]:
        """Plan which files need to be edited.

        Returns:
            Tuple of (EditPlan, tokens_used)
        """
        context = {"edit_request": prompt, "project_files": file_list}
        if file_contents:
            # Include a subset of file contents for context
            context["file_snippets"] = {
                k: v[:500] for k, v in file_contents.items()
            }

        data, tokens = await self._call_openai_json(
            system_prompt=PLAN_SYSTEM_PROMPT,
            user_prompt=f"Plan the edit:\n{json.dumps(context, indent=2)}",
            temperature=0.5,
            max_tokens=2048,
        )
        plan = EditPlan(**data)
        logger.info(
            f"Edit plan: {len(plan.affected_files)} files affected, "
            f"{len(plan.new_files)} new files"
        )
        return plan, tokens

    async def edit_file(
        self,
        prompt: str,
        file_path: str,
        current_content: str,
        plan: EditPlan,
    ) -> tuple[GeneratedFile, int]:
        """Edit a single file based on the user's prompt and edit plan.

        Returns:
            Tuple of (GeneratedFile, tokens_used)
        """
        context = {
            "edit_request": prompt,
            "file_path": file_path,
            "current_content": current_content,
            "edit_plan": plan.model_dump(),
        }
        data, tokens = await self._call_openai_json(
            system_prompt=EDIT_SYSTEM_PROMPT,
            user_prompt=f"Edit this file:\n{json.dumps(context, indent=2)}",
            temperature=0.3,
            max_tokens=4096,
        )
        generated = GeneratedFile(**data)
        logger.info(f"Edited file: {generated.path}")
        return generated, tokens
