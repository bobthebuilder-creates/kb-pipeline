from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from src.llm.config import default_llm_config
from src.llm.client import create_llm_client
from src.api import llm_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KB Pipeline Backend",
    description="Backend service for the graph-based KB + RAG pipeline",
    version="0.1.0",
)

# CORS – allow frontend on dev (Vite default is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global LLM config/client at startup (for /health).
# The LLM API route maintains its own mutable config instance too.
LLM_CONFIG = default_llm_config()
try:
    LLM_CLIENT = create_llm_client(LLM_CONFIG)
    logger.info(f"Initialized LLM client with config: {LLM_CONFIG}")
except Exception as e:
    LLM_CLIENT = None
    logger.warning(f"Failed to initialize LLM client at startup: {e}")

# Routers
app.include_router(llm_routes.router)


@app.get("/health")
def health():
    """
    Simple health check endpoint.
    """
    return {
        "status": "ok",
        "llm_mode": LLM_CONFIG.mode.value,
        "llm_base_url": LLM_CONFIG.base_url,
        "llm_model": LLM_CONFIG.model_name,
        "llm_client_initialized": LLM_CLIENT is not None,
    }


def get_app():
    """For ASGI servers if needed."""
    return app


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("APP_PORT", "7777"))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=True)
