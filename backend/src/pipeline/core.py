from typing import Callable

from loguru import logger

from src.llm.config import LLMConfig

StatusCallback = Callable[[str, float, str], None]


def build_knowledge_base(
    input_dir: str,
    llm_config: LLMConfig,
    indexing_method: str,
    status_callback: StatusCallback | None = None,
) -> None:
    """
    Stub for the main pipeline.

    In v1 this just logs fake stages so the job lifecycle works end-to-end.
    We'll replace each stage with real logic in later steps.
    """
    def update(stage: str, progress: float, message: str) -> None:
        logger.info(f"[PIPELINE] {stage} {progress*100:.1f}% - {message}")
        if status_callback:
            status_callback(stage, progress, message)

    update("load_documents", 0.2, f"Loading documents from {input_dir}")
    # TODO: implement real load_documents()

    update("compose_text_units", 0.3, "Composing text units")
    # TODO: implement real compose_text_units()

    update("extract_graph", 0.5, f"Extracting entities/relationships (method={indexing_method})")
    # TODO: implement real graph extraction

    update("detect_communities", 0.7, "Detecting communities")
    # TODO: implement real community detection

    update("summarize_communities", 0.85, "Generating community reports")
    # TODO: implement real community summary generation

    update("embed_and_store", 0.95, "Generating embeddings and storing in vector/graph DB")
    # TODO: implement real embedding + storage logic

    update("finalizing", 0.99, "Finalizing pipeline")
