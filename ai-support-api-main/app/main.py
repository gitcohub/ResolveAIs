from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from openai import APIConnectionError, APIStatusError, APITimeoutError
from app.config import Settings, get_settings
from app.jobs import create_job, get_job, process_support_job
from app.schemas import (
    JobAcceptedResponse,
    JobStatusResponse,
    SupportRequest,
    SupportResponse,
)
from app.services.ai_service import create_openai_response
from app.security import verify_api_key
app = FastAPI(
    title="AI Support API",
    description=(
        "A FastAPI backend demo for validating, classifying, "
        "and responding to customer support requests."
    ),
    version="0.2.0",
)
@app.get("/health", tags=["System"])
async def health_check(
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    return {
        "status": "ok",
        "ai_mode": "mock" if settings.use_mock_ai else "openai",
    }
@app.post(
    "/support/analyze",
    response_model=SupportResponse,
    tags=["Support"],
)
async def analyze_support_request(
    request: SupportRequest,
    settings: Settings = Depends(get_settings),
    _: str = Depends(verify_api_key),
) -> SupportResponse:
    try:
        return await create_openai_response(request, settings)
    except APITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="The AI provider timed out.",
        ) from exc
    except APIConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to the AI provider.",
        ) from exc
    except APIStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"The AI provider returned status {exc.status_code}.",
        ) from exc
@app.post(
    "/support/jobs",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Background Jobs"],
)
async def submit_support_job(
    request: SupportRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    _: str = Depends(verify_api_key),
) -> JobAcceptedResponse:
    job = create_job()
    background_tasks.add_task(
        process_support_job,
        job.job_id,
        request,
        settings,
    )
    return job
@app.get(
    "/support/jobs/{job_id}",
    response_model=JobStatusResponse,
    tags=["Background Jobs"],
)
async def read_support_job(
    job_id: str,
    _: str = Depends(verify_api_key),
) -> JobStatusResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )
    return job
