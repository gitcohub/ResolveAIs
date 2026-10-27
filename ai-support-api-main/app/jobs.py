import logging
from uuid import uuid4
from app.config import Settings
from app.schemas import (
    JobAcceptedResponse,
    JobStatusResponse,
    SupportRequest,
)
from app.services.ai_service import create_openai_response
logger = logging.getLogger(__name__)
_jobs: dict[str, JobStatusResponse] = {}
def create_job() -> JobAcceptedResponse:
    job_id = str(uuid4())
    _jobs[job_id] = JobStatusResponse(
        job_id=job_id,
        status="queued",
    )
    return JobAcceptedResponse(
        job_id=job_id,
        status="queued",
        status_url=f"/support/jobs/{job_id}",
    )
def get_job(job_id: str) -> JobStatusResponse | None:
    return _jobs.get(job_id)
async def process_support_job(
    job_id: str,
    request: SupportRequest,
    settings: Settings,
) -> None:
    _jobs[job_id] = JobStatusResponse(
        job_id=job_id,
        status="processing",
    )
    try:
        result = await create_openai_response(request, settings)
        _jobs[job_id] = JobStatusResponse(
            job_id=job_id,
            status="completed",
            result=result,
        )
    except Exception:
        logger.exception("Support job %s failed", job_id)
        _jobs[job_id] = JobStatusResponse(
            job_id=job_id,
            status="failed",
            error="The support request could not be processed.",
        )