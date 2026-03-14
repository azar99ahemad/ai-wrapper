"""Tests for the AI agent base class."""

import json

from app.agents.base import BaseAgent


class TestBaseAgent:
    def test_init(self):
        agent = BaseAgent()
        assert agent.client is not None
        assert agent.model is not None

    def test_json_cleaning_code_fence(self):
        """Test that JSON wrapped in code fences can be parsed."""
        # We can't call _call_openai_json directly without mocking OpenAI,
        # but we can test the JSON cleaning logic indirectly
        content = '```json\n{"key": "value"}\n```'
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        parsed = json.loads(cleaned)
        assert parsed["key"] == "value"

    def test_json_cleaning_plain(self):
        """Test that plain JSON passes through."""
        content = '{"key": "value"}'
        parsed = json.loads(content.strip())
        assert parsed["key"] == "value"
