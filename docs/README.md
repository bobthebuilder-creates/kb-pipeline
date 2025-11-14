# KB Pipeline

This project builds a Dockerized system that:

- Ingests authoritative documents
- Builds a graph-based knowledge base (Neo4j + Qdrant)
- Uses local or custom LLM endpoints (Ollama supported)
- Exposes a FastAPI backend and React/Vite UI on port 7777

The design is defined in `docs/dynamic_spec.md` and updated as the implementation evolves.
