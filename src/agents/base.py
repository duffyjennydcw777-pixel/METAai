"""
Base agent class — all agents inherit from this.
Handles OpenRouter API calls and response parsing.
"""
import httpx
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import config, AgentModel

logger = logging.getLogger(__name__)


class AgentResponse:
    """Structured response from an agent."""

    def __init__(self, raw: dict, agent_name: str, duration_ms: int):
        self.raw = raw
        self.agent_name = agent_name
        self.duration_ms = duration_ms
        self.content = self._extract_content()
        self.model = raw.get("model", "unknown")
        self.usage = raw.get("usage", {})

    def _extract_content(self) -> str:
        choices = self.raw.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    @property
    def input_tokens(self) -> int:
        return self.usage.get("prompt_tokens", 0)

    @property
    def output_tokens(self) -> int:
        return self.usage.get("completion_tokens", 0)

    @property
    def cost_estimate(self) -> float:
        """Rough cost estimate in USD based on known pricing."""
        # Approximate pricing per 1M tokens
        pricing = {
            "anthropic/claude-3.5-sonnet": (3.0, 15.0),
            "anthropic/claude-3.5-haiku": (0.8, 4.0),
            "openai/gpt-4o-mini": (0.15, 0.6),
            "google/gemini-2.0-flash-001": (0.1, 0.4),
        }
        input_price, output_price = pricing.get(self.model, (1.0, 5.0))
        return (self.input_tokens * input_price + self.output_tokens * output_price) / 1_000_000

    def __str__(self) -> str:
        return (
            f"[{self.agent_name}] "
            f"tokens: {self.input_tokens}→{self.output_tokens} "
            f"cost: ${self.cost_estimate:.4f} "
            f"time: {self.duration_ms}ms"
        )


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(self, model_config: AgentModel):
        self.model_config = model_config
        self.name = model_config.name
        self.system_prompt = ""

    async def call(self, user_prompt: str, system_prompt: Optional[str] = None) -> AgentResponse:
        """Make an API call to OpenRouter."""
        errors = config.validate()
        if errors:
            raise RuntimeError(f"Config errors: {'; '.join(errors)}")

        messages = []
        sys_prompt = system_prompt or self.system_prompt
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model_config.model_id,
            "messages": messages,
            "temperature": self.model_config.temperature,
            "max_tokens": self.model_config.max_tokens,
        }

        start = datetime.now()

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{config.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://metaai.dev",
                    "X-Title": f"METAai-{self.model_config.role}",
                },
                json=payload,
            )
            if response.status_code != 200:
                error_body = response.text[:500]
                logger.error(f"API error {response.status_code}: {error_body}")
                raise RuntimeError(
                    f"OpenRouter API error {response.status_code} "
                    f"(model: {self.model_config.model_id}): {error_body}"
                )
            data = response.json()

        duration_ms = int((datetime.now() - start).total_seconds() * 1000)
        agent_response = AgentResponse(data, self.name, duration_ms)

        logger.info(str(agent_response))
        return agent_response

    async def call_json(self, user_prompt: str, system_prompt: Optional[str] = None) -> dict:
        """Call and parse response as JSON."""
        resp = await self.call(user_prompt, system_prompt)
        content = resp.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first and last lines (```json and ```)
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            parsed = json.loads(content)
            return {"result": parsed, "meta": str(resp)}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from {self.name}: {content[:200]}")
            return {"result": {"raw_text": content}, "meta": str(resp)}

    def save_report(self, content: str, report_type: str, project: str = "general") -> Path:
        """Save agent report to reviews directory."""
        reviews_dir = config.reviews_dir
        reviews_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"{timestamp}_{report_type}_{project}.md"
        filepath = reviews_dir / filename

        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Report saved: {filepath}")
        return filepath
