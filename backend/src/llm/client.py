from __future__ import annotations

from typing import Protocol, List, Dict, Any
import logging

import httpx

from .config import LLMConfig, LLMMode

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """
    Minimal interface for LLM interactions.
    For now, we just support chat-style interactions and simple completions.
    """

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        ...

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        ...


class OllamaLLMClient:
    """
    Simple async HTTP client for Ollama-style endpoints.

    NOTE: In v1 this is a basic stub. We'll refine the exact JSON contract
    once we wire it up to a real Ollama instance.
    """

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=60.0)

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Call Ollama's chat-like API.

        Expected payload (to refine later):
        {
          "model": self.model,
          "messages": messages
        }
        """
        logger.info(f"Ollama chat called with model={self.model}")
        # TODO: refine endpoint and payload contract once confirmed
        payload = {
            "model": self.model,
            "messages": messages,
        }
        url = f"{self.base_url}/api/chat"
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # TODO: adjust according to actual Ollama response schema
        return data.get("message", {}).get("content", "")

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Call Ollama's completion-like API.
        """
        logger.info(f"Ollama complete called with model={self.model}")
        payload = {
            "model": self.model,
            "prompt": prompt,
        }
        url = f"{self.base_url}/api/generate"
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # TODO: adjust parsing according to actual response
        return data.get("response", "")


class CustomLLMClient:
    """
    Generic HTTP-based client for a custom LLM endpoint.

    The contract is intentionally vague in v1; you'll adapt this to whatever
    API you decide to use (e.g., OpenAI-compatible, custom internal, etc.).
    """

    def __init__(self, base_url: str, model: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=60.0)

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """
        Generic chat; expect a /chat endpoint that accepts:
        {
          "model": self.model,
          "messages": messages,
          "params": { ...kwargs }
        }
        """
        logger.info(f"Custom LLM chat called with base={self.base_url}, model={self.model}")
        payload: Dict[str, Any] = {
            "messages": messages,
            "params": kwargs,
        }
        if self.model:
            payload["model"] = self.model

        url = f"{self.base_url}/chat"
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("content", "")

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """
        Generic completion; expect a /complete endpoint that accepts:
        {
          "model": self.model,
          "prompt": prompt,
          "params": { ...kwargs }
        }
        """
        logger.info(f"Custom LLM complete called with base={self.base_url}, model={self.model}")
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "params": kwargs,
        }
        if self.model:
            payload["model"] = self.model

        url = f"{self.base_url}/complete"
        resp = await self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("content", "")


def create_llm_client(config: LLMConfig) -> LLMClient:
    """
    Factory that returns the appropriate LLMClient implementation
    based on the LLMConfig.
    """
    if config.mode == LLMMode.OLLAMA:
        if not config.base_url:
            raise ValueError("OLLAMA mode selected but no base_url set.")
        if not config.model_name:
            raise ValueError("OLLAMA mode selected but no model_name set.")
        logger.info(f"Creating OllamaLLMClient: base_url={config.base_url}, model={config.model_name}")
        return OllamaLLMClient(base_url=config.base_url, model=config.model_name)

    # CUSTOM mode
    if not config.base_url:
        raise ValueError("CUSTOM LLM mode selected but no base_url set.")
    logger.info(f"Creating CustomLLMClient: base_url={config.base_url}, model={config.model_name}")
    return CustomLLMClient(base_url=config.base_url, model=config.model_name)
