"""Shared LLM configuration and client state management.

This module centralizes the active LLM configuration and the optional
client instance so that the API routes, pipeline execution, and other
subsystems can always obtain the latest settings without forcing an
LLM to be present.
"""
from __future__ import annotations

from threading import RLock
from typing import Optional

from loguru import logger

from .client import LLMClient, create_llm_client
from .config import LLMConfig, default_llm_config


class LLMState:
    """Thread-safe holder for the active LLM configuration and client."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._config: LLMConfig = default_llm_config()
        self._client: Optional[LLMClient] = None
        self._client_error: Optional[str] = None

    def get_config(self) -> LLMConfig:
        """Return a deep copy of the active configuration."""
        with self._lock:
            return self._config.copy(deep=True)

    def get_client(self) -> Optional[LLMClient]:
        """Return the currently initialized client (may be ``None``)."""
        with self._lock:
            return self._client

    def get_client_error(self) -> Optional[str]:
        """Return the most recent client initialization error, if any."""
        with self._lock:
            return self._client_error

    def get_status(self) -> dict:
        """Return a serializable snapshot of the LLM state."""
        with self._lock:
            return {
                "mode": self._config.mode.value,
                "base_url": self._config.base_url,
                "model_name": self._config.model_name,
                "client_initialized": self._client is not None,
                "last_error": self._client_error,
            }

    def set_config(self, config: LLMConfig, initialize_client: bool = True) -> bool:
        """Persist a new configuration and optionally initialize the client."""
        with self._lock:
            self._config = config
            self._client = None
            self._client_error = None

        if initialize_client:
            return self.refresh_client()
        return True

    def refresh_client(self) -> bool:
        """Attempt to initialize the client using the current configuration."""
        config = self.get_config()

        try:
            client = create_llm_client(config)
        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.warning(
                "Failed to initialize LLM client (mode=%s, base=%s, model=%s): %s",
                config.mode.value,
                config.base_url,
                config.model_name,
                exc,
            )
            with self._lock:
                self._client = None
                self._client_error = str(exc)
            return False

        with self._lock:
            self._client = client
            self._client_error = None
        logger.info(
            "Initialized LLM client: mode=%s base=%s model=%s",
            config.mode.value,
            config.base_url,
            config.model_name,
        )
        return True


# Module-level singleton ----------------------------------------------------
_llm_state = LLMState()


def get_llm_state() -> LLMState:
    """Return the process-wide LLM state singleton."""
    return _llm_state
