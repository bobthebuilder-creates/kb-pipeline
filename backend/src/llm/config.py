from enum import Enum
from typing import Optional
from pydantic import BaseModel
import os
import logging
import httpx

logger = logging.getLogger(__name__)


class LLMMode(str, Enum):
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMConfig(BaseModel):
    """
    Configuration for LLM access.

    mode:
        - "ollama": use local Ollama HTTP endpoint
        - "custom": use a user-provided HTTP endpoint
    base_url:
        - e.g. "http://127.0.0.1:11434"
        - for Ollama, this will be the discovered or overridden URL
        - for custom, this is whatever the user provides
    model_name:
        - required in Ollama mode (e.g., "llama3")
        - optional for custom mode (depends on custom API)
    """

    mode: LLMMode = LLMMode.OLLAMA
    base_url: Optional[str] = None
    model_name: Optional[str] = None


def discover_ollama_endpoint() -> Optional[str]:
    """
    Attempt to discover a working Ollama endpoint.

    Strategy (per DS, not fully implemented yet):
      1. Check OLLAMA_HOST env var; if present, assume http://<host>:11434.
      2. In the future:
         - Inspect common systemd service files:
             /etc/systemd/system/ollama.service
             /lib/systemd/system/ollama.service
             ~/.config/systemd/user/ollama.service
           Parse Environment/ExecStart lines for host/bind address.
      3. Try standard candidates:
         - http://127.0.0.1:11434
         - http://localhost:11434

    For now, this is a stub that only checks OLLAMA_HOST and simple defaults.
    Later we'll add real HTTP probing and service file parsing.
    """
    # 1. Check env var
    host = os.getenv("OLLAMA_HOST")
    if host:
        # allow user to pass full URL or just host
        if host.startswith("http://") or host.startswith("https://"):
            logger.info(f"Using OLLAMA_HOST as full URL: {host}")
            return host
        candidate = f"http://{host}:11434"
        logger.info(f"Using OLLAMA_HOST as host, built URL: {candidate}")
        return candidate

    # 2. Fall back to common defaults
    default_candidates = [
        "http://127.0.0.1:11434",
        "http://localhost:11434",
    ]

    # TODO: add real HTTP checks (e.g., GET /api/version) to verify.
    # For now, return the first candidate and trust the user to ensure it's running.
    logger.info("No OLLAMA_HOST set; falling back to default Ollama candidates.")
    return default_candidates[0]


def default_llm_config() -> LLMConfig:
    """
    Construct a default LLMConfig based on environment variables and
    simple discovery logic.

    Environment variables (optional):
      LLM_MODE: "ollama" or "custom"
      LLM_BASE_URL: explicit base URL (takes precedence over discovery)
      LLM_MODEL_NAME: model name for the LLM
    """
    mode_str = os.getenv("LLM_MODE", "ollama").lower()
    mode = LLMMode(mode_str) if mode_str in LLMMode._value2member_map_ else LLMMode.OLLAMA

    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_NAME")

    if mode == LLMMode.OLLAMA:
        if not base_url:
            base_url = discover_ollama_endpoint()
            logger.info(f"Discovered Ollama base URL: {base_url}")
    else:
        # custom mode: require LLM_BASE_URL to be set later via API or env
        logger.info("Using CUSTOM LLM mode; base_url must be provided by user or env.")

    return LLMConfig(mode=mode, base_url=base_url, model_name=model_name)

async def list_ollama_models(base_url: str) -> list[str]:
    """
    Query Ollama for installed models.

    This assumes Ollama exposes a /api/tags endpoint that returns:
      { "models": [ { "name": "llama3" }, ... ] }

    For now we keep it simple; we'll refine once we hook to a real instance.
    """
    url = base_url.rstrip("/") + "/api/tags"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    models = []
    for item in data.get("models", []):
        name = item.get("name")
        if name:
            models.append(name)
    return models