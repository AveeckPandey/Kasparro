"""Configuration management for candidate screening system."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Project directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    INPUT_DIR: Path = Field(default=Path("./resumes"))
    OUTPUT_FILE: Path = Field(default=Path("./output/results.json"))

    # GitHub API
    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub PAT for public API rate limits")
    GITHUB_CACHE_FILE: Path = Field(default=Path("./output/.github_cache.json"))

    # LLM Settings
    LLM_PROVIDER: str = Field(default="auto", description="auto, openai, gemini, or heuristic")
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1")

    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")

    # Concurrency & Performance
    CONCURRENCY_LIMIT: int = Field(default=5, description="Max concurrent worker tasks")
    REQUEST_TIMEOUT: float = Field(default=15.0, description="Network timeout in seconds")

    # Scoring Weights (Total: 100)
    WEIGHT_AI_PROJECT_DEPTH: int = 40
    WEIGHT_PYTHON_BACKEND: int = 30
    WEIGHT_CLOUD_FULLSTACK: int = 15
    WEIGHT_GITHUB: int = 10
    WEIGHT_ENGINEERING_DEPTH: int = 5

    # Penalties
    PENALTY_SHALLOW_WRAPPER_MIN: int = 5
    PENALTY_SHALLOW_WRAPPER_MAX: int = 15
    PENALTY_TUTORIAL_PROJECT: int = 8

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
