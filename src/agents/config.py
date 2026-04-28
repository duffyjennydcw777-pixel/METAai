"""
METAai Agent Configuration.
Loads settings from .env and provides defaults.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional, can use system env vars


@dataclass
class AgentModel:
    """Model configuration for a specific agent role."""
    name: str
    role: str
    model_id: str
    temperature: float = 0.1
    max_tokens: int = 4096


@dataclass
class Config:
    """Global configuration for the agent system."""

    # OpenRouter
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))

    # Agent models
    architect: AgentModel = field(default_factory=lambda: AgentModel(
        name="Architect",
        role="architect",
        model_id=os.getenv("AGENT_MODEL_ARCHITECT", "anthropic/claude-3.5-sonnet"),
        temperature=0.2,
        max_tokens=8192,
    ))
    reviewer: AgentModel = field(default_factory=lambda: AgentModel(
        name="Reviewer",
        role="review",
        model_id=os.getenv("AGENT_MODEL_REVIEW", "anthropic/claude-3.5-haiku-20241022"),
        temperature=0.1,
        max_tokens=4096,
    ))
    security: AgentModel = field(default_factory=lambda: AgentModel(
        name="Security Auditor",
        role="security",
        model_id=os.getenv("AGENT_MODEL_SECURITY", "anthropic/claude-3.5-sonnet"),
        temperature=0.1,
        max_tokens=4096,
    ))
    test_gen: AgentModel = field(default_factory=lambda: AgentModel(
        name="Test Generator",
        role="test",
        model_id=os.getenv("AGENT_MODEL_TEST", "openai/gpt-4o-mini"),
        temperature=0.3,
        max_tokens=8192,
    ))
    preflight: AgentModel = field(default_factory=lambda: AgentModel(
        name="Deploy Guardian",
        role="preflight",
        model_id=os.getenv("AGENT_MODEL_PREFLIGHT", "google/gemini-2.0-flash-001"),
        temperature=0.0,
        max_tokens=2048,
    ))

    # Paths
    reviews_dir: Path = field(default_factory=lambda: Path("reviews"))
    patterns_file: Path = field(default_factory=lambda: Path("SOLUTION_PATTERNS.md"))
    decisions_file: Path = field(default_factory=lambda: Path("DECISIONS.md"))

    def validate(self) -> list[str]:
        """Check configuration, return list of errors."""
        errors = []
        if not self.api_key:
            errors.append("OPENROUTER_API_KEY not set. Add it to .env")
        return errors


# Singleton
config = Config()
