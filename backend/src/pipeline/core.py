from typing import Callable

from loguru import logger
import pandas as pd

from src.llm.config import LLMConfig
from src.pipeline.ingest import load_documents, compose_text_units

StatusCallback = Callable[[str, float, str], None]


def build_knowledge_base(
    input_dir: str,
    llm_config: LLMConfig,
    indexing_method: str,
    status_callback: StatusCallback | None = None,
) -> None:
    """
    Main pipeline entrypoint (v1).

    Currently implements:
      - Real document loading
      - Real text unit composition
    and stubs out later stages.
    """

    def update(stage: str, progress: float, message: str) -> None:
        logger.info(f"[PIPELINE] {stage} {progress*100:.1f}% - {message}")
        if status_callback:
            status_callback(stage, progress, message)

    # 1. Load documents
    update("load_documents", 0.1, f"Loading documents from {input_dir}")
    docs_df: pd.DataFrame = load_documents(input_dir)

    if docs_df.empty:
        update("load_documents", 0.15, "No documents found; pipeline will complete with empty KB.")
        # We still continue through the motions; you might choose to early-exit instead.
    else:
        update("load_documents", 0.2, f"Loaded {len(docs_df)} documents")

    # 2. Compose text units
    update("compose_text_units", 0.25, "Composing text units")
    tu_df: pd.DataFrame = compose_text_units(docs_df, max_chars=1200)
    update("compose_text_units", 0.35, f"Composed {len(tu_df)} text units")

    # 3. Graph extraction (stub)
    update("extract_graph", 0.5, f"Extracting entities/relationships (method={indexing_method})")
    # TODO: implement real graph extraction using LLM client

    # 4. Community detection (stub)
    update("detect_communities", 0.7, "Detecting communities")
    # TODO: implement community detection

    # 5. Community reports (stub)
    update("summarize_communities", 0.85, "Generating community reports")
    # TODO: implement summary generation using LLM

    # 6. Embeddings + storage (stub)
    update("embed_and_store", 0.95, "Generating embeddings and storing in vector/graph DB")
    # TODO: implement embedding + Qdrant/Neo4j writes

    update("finalizing", 0.99, "Finalizing pipeline")
