import logging
import os
from enum import Enum
from typing import Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMMode(str, Enum):
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMConfig(BaseModel):
    """Configuration for LLM access."""

    mode: LLMMode = LLMMode.OLLAMA
    base_url: Optional[str] = None
    model_name: Optional[str] = None


def discover_ollama_endpoint() -> Optional[str]:
    """Attempt to discover a working Ollama endpoint."""
    host = os.getenv("OLLAMA_HOST")
    if host:
        if host.startswith("http://") or host.startswith("https://"):
            logger.info("Using OLLAMA_HOST as full URL: %s", host)
            return host
        candidate = f"http://{host}:11434"
        logger.info("Using OLLAMA_HOST as host, built URL: %s", candidate)
        return candidate

    default_candidates = [
        "http://127.0.0.1:11434",
        "http://localhost:11434",
    ]
    logger.info("No OLLAMA_HOST set; falling back to default Ollama candidates.")
    return default_candidates[0]


def default_llm_config() -> LLMConfig:
    """Construct the default LLM configuration using env vars and discovery."""
    mode_str = os.getenv("LLM_MODE", "ollama").lower()
    mode = LLMMode(mode_str) if mode_str in LLMMode._value2member_map_ else LLMMode.OLLAMA

    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_NAME")

    if mode == LLMMode.OLLAMA:
        if not base_url:
            base_url = discover_ollama_endpoint()
            logger.info("Discovered Ollama base URL: %s", base_url)
    else:
        logger.info("Using CUSTOM LLM mode; base_url must be provided by user or env.")

    return LLMConfig(mode=mode, base_url=base_url, model_name=model_name)


async def list_ollama_models(base_url: str) -> list[str]:
    """Query Ollama for installed models."""
    url = base_url.rstrip("/") + "/api/tags"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    models: list[str] = []
    for item in data.get("models", []):
        name = item.get("name")
        if name:
            models.append(name)
    return models
