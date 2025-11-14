import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api import llm_routes, pipeline_routes
from src.llm.state import get_llm_state

app = FastAPI(
    title="KB Pipeline Backend",
    description="Backend service for the graph-based KB + RAG pipeline",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_routes.router)
app.include_router(pipeline_routes.router)

llm_state = get_llm_state()


@app.get("/health")
def health():
    """Simple health check endpoint."""
    status = llm_state.get_status()
    logger.debug("Health check requested: %s", status)
    return {"status": "ok", "llm": status}


def get_app():
    """Return the ASGI application instance."""
    return app


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("APP_PORT", "7777"))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=True)
