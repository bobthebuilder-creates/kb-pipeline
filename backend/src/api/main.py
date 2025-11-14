from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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


@app.get("/health")
def health():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


def get_app():
    """For ASGI servers if needed."""
    return app


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("APP_PORT", "7777"))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=True)
