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
from src.llm.config import LLMConfig, LLMMode, list_ollama_models
from src.llm.state import get_llm_state

router = APIRouter(prefix="/api/llm", tags=["llm"])

# In a more advanced version, you'd store this in a proper config store.
# For now, we keep a simple in-memory singleton that mirrors main.py.
_current_llm_config: LLMConfig = default_llm_config()
_current_llm_client = None

try:
    _current_llm_client = create_llm_client(_current_llm_config)
except Exception:
    _current_llm_client = None
llm_state = get_llm_state()


class LLMConfigRequest(BaseModel):
    mode: Optional[LLMMode] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    initialize_client: bool = True


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
    """Return the current LLM configuration and client availability."""
    return llm_state.get_status()


@router.post("/config")
async def set_llm_config(req: LLMConfigRequest):
    """
    Update LLM configuration (mode, base_url, model_name) and reinitialize client.
    """Update LLM configuration and optionally reinitialize the client."""
    current = llm_state.get_config()

    Behavior:
      - Fields not provided retain their existing values.
      - Validates that resulting config is usable for the chosen mode.
    """
    global _current_llm_config, _current_llm_client
    new_config = LLMConfig(
        mode=req.mode or current.mode,
        base_url=req.base_url or current.base_url,
        model_name=req.model_name or current.model_name,
    )

    # Start from current config
    mode = req.mode or _current_llm_config.mode
    base_url = req.base_url or _current_llm_config.base_url
    model_name = req.model_name or _current_llm_config.model_name
    initialized = llm_state.set_config(new_config, initialize_client=req.initialize_client)

    new_config = LLMConfig(mode=mode, base_url=base_url, model_name=model_name)
    status = llm_state.get_status()
    status["client_initialized"] = status["client_initialized"] and initialized

    # Try to create client to validate config
    try:
        client = create_llm_client(new_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to initialize LLM client: {e}")
    message = (
        "LLM configuration updated."
        if status["client_initialized"]
        else "LLM configuration saved, client not initialized."
    )
    if status["last_error"]:
        message += f" Reason: {status['last_error']}"

    return {"message": message, "status": status}

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
@router.post("/refresh")
async def refresh_llm_client():
    """Explicitly re-initialize the LLM client using the saved configuration."""
    ok = llm_state.refresh_client()
    status = llm_state.get_status()
    if not ok:
        raise HTTPException(status_code=502, detail=status["last_error"] or "Unknown error")
    return {"message": "LLM client initialized", "status": status}


@router.get("/models")
async def get_ollama_models():
    """
    Return list of available Ollama models for the current base_url.

    Only valid if mode == 'ollama' and base_url is set.
    """
    if _current_llm_config.mode != LLMMode.OLLAMA:
    """Return list of available Ollama models for the current base_url."""
    status = llm_state.get_status()
    if status["mode"] != LLMMode.OLLAMA.value:
        raise HTTPException(status_code=400, detail="LLM mode is not 'ollama'")

    if not _current_llm_config.base_url:
    base_url = status["base_url"]
    if not base_url:
        raise HTTPException(status_code=400, detail="No base_url configured for Ollama")

    try:
        models = await list_ollama_models(_current_llm_config.base_url)
        models = await list_ollama_models(base_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to list Ollama models: {e}")

    return {"models": models}