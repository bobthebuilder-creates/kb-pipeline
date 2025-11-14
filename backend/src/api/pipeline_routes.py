import time
import uuid
from enum import Enum
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.llm.state import get_llm_state
from src.pipeline.core import build_knowledge_base

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])
llm_state = get_llm_state()


class PipelineStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class RunPipelineRequest(BaseModel):
    input_path: str
    indexing_method: Optional[str] = "standard"


class PipelineStatus(BaseModel):
    job_id: str
    status: PipelineStatusEnum
    stage: Optional[str] = None
    progress: float = 0.0
    message: Optional[str] = None
    started_at: float
    finished_at: Optional[float] = None


_PIPELINE_JOBS: Dict[str, PipelineStatus] = {}


def _run_pipeline_job(job_id: str, input_path: str, indexing_method: str) -> None:
    """Background task that runs the pipeline for a queued job."""
    job = _PIPELINE_JOBS[job_id]
    job.status = PipelineStatusEnum.RUNNING
    job.stage = "initializing"
    job.message = f"Starting pipeline for input_path={input_path}"
    job.progress = 0.01
    _PIPELINE_JOBS[job_id] = job

    try:
        job.stage = "llm_config"
        job.message = "Fetching active LLM configuration"
        _PIPELINE_JOBS[job_id] = job

        llm_config = llm_state.get_config()
        logger.info("[PIPELINE] Using LLM config: %s", llm_config.dict())

        job.stage = "running_pipeline"
        job.message = "Running build_knowledge_base"
        job.progress = 0.1
        _PIPELINE_JOBS[job_id] = job

        build_knowledge_base(
            input_dir=input_path,
            llm_config=llm_config,
            indexing_method=indexing_method,
            status_callback=lambda stage, progress, msg: _update_job_status(
                job_id, stage, progress, msg
            ),
        )

        job = _PIPELINE_JOBS[job_id]
        job.status = PipelineStatusEnum.COMPLETED
        job.stage = "completed"
        job.progress = 1.0
        job.message = "Pipeline completed successfully"
        job.finished_at = time.time()
        _PIPELINE_JOBS[job_id] = job
    except Exception as exc:  # pragma: no cover - defensive logging path
        job = _PIPELINE_JOBS[job_id]
        job.status = PipelineStatusEnum.FAILED
        job.stage = "error"
        job.message = f"Pipeline failed: {exc}"
        job.finished_at = time.time()
        _PIPELINE_JOBS[job_id] = job
        logger.exception("[PIPELINE] Job %s failed", job_id)


def _update_job_status(job_id: str, stage: str, progress: float, message: str) -> None:
    if job_id not in _PIPELINE_JOBS:
        return
    job = _PIPELINE_JOBS[job_id]
    job.stage = stage
    job.progress = progress
    job.message = message
    _PIPELINE_JOBS[job_id] = job


@router.post("/run", response_model=PipelineStatus)
async def run_pipeline(req: RunPipelineRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    now = time.time()

    status = PipelineStatus(
        job_id=job_id,
        status=PipelineStatusEnum.PENDING,
        stage="queued",
        progress=0.0,
        message="Job queued",
        started_at=now,
        finished_at=None,
    )
    _PIPELINE_JOBS[job_id] = status

    background_tasks.add_task(
        _run_pipeline_job, job_id, req.input_path, req.indexing_method or "standard"
    )

    return status


@router.get("/status/{job_id}", response_model=PipelineStatus)
async def get_pipeline_status(job_id: str):
    if job_id not in _PIPELINE_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return _PIPELINE_JOBS[job_id]
