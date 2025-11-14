import uuid
import time
from enum import Enum
from typing import Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from src.llm.config import default_llm_config
from src.llm.client import create_llm_client
from src.pipeline.core import build_knowledge_base

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


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


# Simple in-memory job store for now.
# Later we can move this to a DB or Redis if needed.
_PIPELINE_JOBS: Dict[str, PipelineStatus] = {}


def _run_pipeline_job(job_id: str, input_path: str, indexing_method: str) -> None:
    """
    Background task that runs the pipeline.
    This is a blocking, sync function by design for now.
    """
    job = _PIPELINE_JOBS[job_id]
    job.status = PipelineStatusEnum.RUNNING
    job.stage = "initializing"
    job.message = f"Starting pipeline for input_path={input_path}"
    job.progress = 0.01
    _PIPELINE_JOBS[job_id] = job

    try:
        # Prepare LLM config + client
        job.stage = "llm_init"
        job.message = "Initializing LLM client"
        _PIPELINE_JOBS[job_id] = job

        llm_config = default_llm_config()
        llm_client = create_llm_client(llm_config)

        # Call the core pipeline (stub for now)
        job.stage = "running_pipeline"
        job.message = "Running build_knowledge_base (stub)"
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

        # Mark as complete
        job = _PIPELINE_JOBS[job_id]
        job.status = PipelineStatusEnum.COMPLETED
        job.stage = "completed"
        job.progress = 1.0
        job.message = "Pipeline completed successfully"
        job.finished_at = time.time()
        _PIPELINE_JOBS[job_id] = job

    except Exception as e:
        job = _PIPELINE_JOBS[job_id]
        job.status = PipelineStatusEnum.FAILED
        job.stage = "error"
        job.message = f"Pipeline failed: {e}"
        job.finished_at = time.time()
        _PIPELINE_JOBS[job_id] = job


def _update_job_status(job_id: str, stage: str, progress: float, message: str) -> None:
    """
    Helper used by the pipeline to push stage-level updates.
    """
    if job_id not in _PIPELINE_JOBS:
        return
    job = _PIPELINE_JOBS[job_id]
    job.stage = stage
    job.progress = progress
    job.message = message
    _PIPELINE_JOBS[job_id] = job


@router.post("/run", response_model=PipelineStatus)
async def run_pipeline(req: RunPipelineRequest, background_tasks: BackgroundTasks):
    """
    Start a new pipeline job for the specified input_path.
    """
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

    # Kick off background job
    background_tasks.add_task(
        _run_pipeline_job, job_id, req.input_path, req.indexing_method or "standard"
    )

    return status


@router.get("/status/{job_id}", response_model=PipelineStatus)
async def get_pipeline_status(job_id: str):
    """
    Get the current status of a pipeline job.
    """
    if job_id not in _PIPELINE_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return _PIPELINE_JOBS[job_id]
