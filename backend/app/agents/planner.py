"""Planner Agent - converts user prompt into structured project specification."""

import logging

from app.agents.base import BaseAgent
from app.schemas.schemas import ProjectSpecification

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert software architect. \
Given a user's description of a web application,
generate a detailed project specification in JSON format.

Return ONLY valid JSON with this structure:
{
    "name": "project-name-kebab-case",
    "description": "Brief project description",
    "features": ["feature1", "feature2"],
    "tech_stack": {"frontend": "Next.js", "styling": "TailwindCSS", ...},
    "pages": ["page1", "page2"],
    "api_endpoints": ["GET /api/items", "POST /api/items"]
}

Always use Next.js with TailwindCSS for the frontend.
Be practical and detailed but focused."""


class PlannerAgent(BaseAgent):
    """Converts a user prompt into a structured project specification."""

    async def plan(self, prompt: str) -> tuple[ProjectSpecification, int]:
        """Generate a project specification from a user prompt.

        Returns:
            Tuple of (ProjectSpecification, tokens_used)
        """
        data, tokens = await self._call_openai_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Create a project specification for: {prompt}",
            temperature=0.7,
            max_tokens=2048,
        )
        spec = ProjectSpecification(**data)
        logger.info(f"Planned project: {spec.name} with {len(spec.features)} features")
        return spec, tokens
