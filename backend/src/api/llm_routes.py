from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.llm.config import (
    LLMConfig,
    LLMMode,
    default_llm_config,
    list_ollama_models,
)
from src.llm.client import create_llm_client

router = APIRouter(prefix="/api/llm", tags=["llm"])

# In a more advanced version, you'd store this in a proper config store.
# For now, we keep a simple in-memory singleton that mirrors main.py.
_current_llm_config: LLMConfig = default_llm_config()
_current_llm_client = None

try:
    _current_llm_client = create_llm_client(_current_llm_config)
except Exception:
    _current_llm_client = None


class LLMConfigRequest(BaseModel):
    mode: Optional[LLMMode] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None


@router.get("/status")
async def get_llm_status():
    """
    Return the current LLM configuration and whether a client is initialized.
    """
    return {
        "mode": _current_llm_config.mode.value,
        "base_url": _current_llm_config.base_url,
        "model_name": _current_llm_config.model_name,
        "client_initialized": _current_llm_client is not None,
    }


@router.post("/config")
async def set_llm_config(req: LLMConfigRequest):
    """
    Update LLM configuration (mode, base_url, model_name) and reinitialize client.

    Behavior:
      - Fields not provided retain their existing values.
      - Validates that resulting config is usable for the chosen mode.
    """
    global _current_llm_config, _current_llm_client

    # Start from current config
    mode = req.mode or _current_llm_config.mode
    base_url = req.base_url or _current_llm_config.base_url
    model_name = req.model_name or _current_llm_config.model_name

    new_config = LLMConfig(mode=mode, base_url=base_url, model_name=model_name)

    # Try to create client to validate config
    try:
        client = create_llm_client(new_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize LLM client: {e}")

    _current_llm_config = new_config
    _current_llm_client = client

    return {
        "message": "LLM configuration updated",
        "config": {
            "mode": _current_llm_config.mode.value,
            "base_url": _current_llm_config.base_url,
            "model_name": _current_llm_config.model_name,
        },
    }


@router.get("/models")
async def get_ollama_models():
    """
    Return list of available Ollama models for the current base_url.

    Only valid if mode == 'ollama' and base_url is set.
    """
    if _current_llm_config.mode != LLMMode.OLLAMA:
        raise HTTPException(status_code=400, detail="LLM mode is not 'ollama'")

    if not _current_llm_config.base_url:
        raise HTTPException(status_code=400, detail="No base_url configured for Ollama")

    try:
        models = await list_ollama_models(_current_llm_config.base_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list Ollama models: {e}")

    return {"models": models}
