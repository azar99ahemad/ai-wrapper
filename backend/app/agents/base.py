"""Base AI agent with shared OpenAI interaction logic."""

import json
import logging

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for AI agents with OpenAI API interaction."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> tuple[str, int]:
        """Call OpenAI API and return (response_text, tokens_used)."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0
            return content, tokens
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _call_openai_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> tuple[dict, int]:
        """Call OpenAI API and parse JSON response."""
        content, tokens = await self._call_openai(
            system_prompt, user_prompt, temperature, max_tokens
        )
        # Strip markdown code fences if present
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first line (```json or ```) and last line (```)
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {cleaned[:200]}")
            raise ValueError(f"AI returned invalid JSON: {cleaned[:200]}")
        return parsed, tokens
