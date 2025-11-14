# Dynamic Specification (DS)
Authoritative Docs → Graph-Based Knowledge System for RAG
Local Ollama + Manual Endpoint Override + GraphDB + Qdrant + React/Vite UI @ 0.0.0.0:7777

## 0. Scope & Intent
Build a Dockerized service that:
1. Accepts a user-selected folder path of authoritative documents.
2. Processes those docs into structured data: documents, text_units, entities, relationships, claims, communities, community_reports.
3. Stores structured data in a graph database and Qdrant vector store.
4. Supports local Ollama or a custom LLM endpoint.
5. Exposes React/Vite UI on port 7777.

## 1. Key Requirements
### Functional
- LLM backend: Local Ollama (auto-detected) or custom endpoint.
- Manual LLM endpoint override always available.
- Document ingestion and indexing pipeline.
- Graph-based KB creation.
- RAG retrieval API (global, local, hybrid).
- Web UI to configure LLM endpoint, model, and input path.
### Non-Functional
- Fully Dockerized environment.
- Free/open-source infra.
- No authentication in v1.
- In-depth, stage-by-stage pipeline tracking in UI.

## 2. Architecture Overview
### Components
- Backend (FastAPI)
- Ingestion & Indexing Pipeline
- GraphDB (Neo4j/FalkorDB)
- Qdrant vector store
- RAG retrieval layer
- React/Vite UI

## 3. Data Model (Schemas)
Documents, TextUnits, Entities, Relationships, Claims, Communities, CommunityReports.

## 4. Storage & Infra
- Neo4j Community Edition
- Qdrant
- Parquet/SQL optional for backup and export

## 5. LLM and Endpoint Selection
### LLM Modes
1. Ollama Mode (auto-discovered or manually forced)
2. Custom Endpoint Mode (manual URL)

### Auto Discovery of Ollama
- Checks OLLAMA_HOST
- Scans common systemd locations (e.g., /etc/systemd/system/ollama.service)
- Parses host binding
- Tries http://127.0.0.1:11434 and http://localhost:11434
- Validates via /api/version

### Manual Override
User specifies base URL in UI.
If set, manual override takes precedence over auto-detected Ollama.

## 6. Indexing & Pipeline
Pipeline executes ingestion → text unit composition → entity/relationship extraction → claims (optional) → community detection → community report generation → embeddings → persistence.

## 7. Web API & UI
Backend endpoints:
- GET /api/llm/status
- POST /api/llm/config
- GET /api/ollama/models
- POST /api/pipeline/run
- GET /api/pipeline/status/{id}
- POST /api/rag/query

React/Vite UI Panels:
- LLM Config (select Ollama/custom, model list, test endpoint)
- Input Path (choose any path under /data/input)
- Pipeline Run Panel
- Live Tracking Panel (stage, progress, timestamps)
- KB Overview Panel

## 8. Dockerization
Services included:
- kb-backend
- qdrant
- neo4j
Volume mounts:
- ./input_docs → /data/input
- ./output_data → /data/output

## 9. Documentation Requirements
A README must include:
- Overview
- System requirements (hardware + software)
- Setup steps
- Running in Docker and dev mode
- Using the UI
- Troubleshooting (Ollama, Neo4j, Qdrant issues)
