import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import chardet
import pandas as pd
import pdfplumber
import docx  # from python-docx
from loguru import logger


SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def _detect_encoding(path: str) -> str:
    """
    Best-effort encoding detection for text files.
    """
    with open(path, "rb") as f:
        raw = f.read(4096)
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def _read_txt(path: str) -> str:
    encoding = _detect_encoding(path)
    with open(path, "r", encoding=encoding, errors="ignore") as f:
        return f.read()


def _read_pdf(path: str) -> str:
    text_chunks: List[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


def _read_docx(path: str) -> str:
    document = docx.Document(path)
    return "\n".join(para.text for para in document.paragraphs)


def _read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        return _read_txt(path)
    if ext == ".pdf":
        return _read_pdf(path)
    if ext == ".docx":
        return _read_docx(path)

    raise ValueError(f"Unsupported file extension: {ext}")


def _infer_title_from_filename(path: str) -> str:
    base = os.path.basename(path)
    name, _ext = os.path.splitext(base)
    return name.replace("_", " ").replace("-", " ")


def load_documents(input_dir: str) -> pd.DataFrame:
    """
    Recursively scan input_dir for supported documents and return
    a DataFrame with columns:

      - id: str
      - uri: str (absolute path)
      - title: str
      - text: str
      - creation_date: Optional[datetime]
      - source_type: str ("file")
      - metadata: dict

    This is intentionally simple and local-filesystem focused for v1.
    """
    records: List[Dict[str, Any]] = []

    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory does not exist or is not a directory: {input_dir}")

    logger.info(f"[INGEST] Scanning directory for documents: {input_dir}")

    doc_id = 0
    for root, _dirs, files in os.walk(input_dir):
        for name in files:
            full_path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()

            if ext not in SUPPORTED_EXTENSIONS:
                logger.debug(f"[INGEST] Skipping unsupported file: {full_path}")
                continue

            try:
                text = _read_file(full_path)
            except Exception as e:
                logger.warning(f"[INGEST] Failed to read {full_path}: {e}")
                continue

            if not text.strip():
                logger.debug(f"[INGEST] Empty text in file, skipping: {full_path}")
                continue

            try:
                stat = os.stat(full_path)
                ctime = datetime.fromtimestamp(stat.st_ctime)
            except Exception:
                ctime = None

            doc_id_str = f"doc_{doc_id}"
            doc_id += 1

            record: Dict[str, Any] = {
                "id": doc_id_str,
                "uri": os.path.abspath(full_path),
                "title": _infer_title_from_filename(full_path),
                "text": text,
                "creation_date": ctime,
                "source_type": "file",
                "metadata": {
                    "ext": ext,
                    "size_bytes": os.path.getsize(full_path),
                    "root_dir": input_dir,
                },
            }
            records.append(record)

    if not records:
        logger.warning(f"[INGEST] No supported documents found in: {input_dir}")

    df = pd.DataFrame.from_records(records)
    logger.info(f"[INGEST] Loaded {len(df)} documents from {input_dir}")
    return df

def compose_text_units(
    docs_df: pd.DataFrame,
    max_chars: int = 1200,
) -> pd.DataFrame:
    """
    Naive text unit composer: split each document's text into chunks
    of <= max_chars characters.

    Output columns:
      - id: str
      - document_id: str
      - text: str
      - order: int (chunk index within document)
      - metadata: dict (inherited / derived)
    """
    rows: List[Dict[str, Any]] = []
    tu_id = 0

    logger.info(f"[INGEST] Composing text units with max_chars={max_chars}")

    for _idx, row in docs_df.iterrows():
        doc_id = row["id"]
        text: str = row["text"]
        meta: Dict[str, Any] = {
            "document_uri": row["uri"],
            "document_title": row["title"],
            "source_type": row.get("source_type", "file"),
            "root_dir": row.get("metadata", {}).get("root_dir") if isinstance(row.get("metadata"), dict) else None,
        }

        # chunk by characters (naive; we can upgrade to token-based later)
        start = 0
        order = 0
        while start < len(text):
            chunk = text[start : start + max_chars]
            start += max_chars

            tu_id_str = f"tu_{tu_id}"
            tu_id += 1

            rows.append(
                {
                    "id": tu_id_str,
                    "document_id": doc_id,
                    "text": chunk,
                    "order": order,
                    "metadata": meta,
                }
            )
            order += 1

    tu_df = pd.DataFrame.from_records(rows)
    logger.info(f"[INGEST] Composed {len(tu_df)} text units from {len(docs_df)} documents")
    return tu_df

