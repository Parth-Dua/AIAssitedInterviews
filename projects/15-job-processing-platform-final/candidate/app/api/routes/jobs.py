from fastapi import APIRouter, HTTPException

from app.models.schemas import JobCreateRequest, JobFinishRequest, JobOut
from app.repositories.job_repository import JobNotFoundError, JobRepository
from app.services.job_service import InvalidJobStateError, JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])

_repository = JobRepository()
_service = JobService(_repository)


def _to_out(job) -> JobOut:
    return JobOut(
        id=job.id,
        status=job.status,
        payload=job.payload,
        result=job.result,
        error=job.error,
        attempt_count=job.attempt_count,
    )


@router.post("", response_model=JobOut)
def create_job(request: JobCreateRequest) -> JobOut:
    """Submits a new export job."""
    job = _service.create_job(request.payload)
    return _to_out(job)


@router.post("/{job_id}/start", response_model=JobOut)
def start_job(job_id: str) -> JobOut:
    """Simulates a worker picking up a job."""
    try:
        job = _service.start_job(job_id)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_out(job)


@router.post("/{job_id}/finish", response_model=JobOut)
def finish_job(job_id: str, request: JobFinishRequest) -> JobOut:
    """Simulates a worker reporting job completion or failure."""
    try:
        job = _service.finish_job(job_id, result=request.result, error=request.error)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_out(job)


@router.post("/{job_id}/cancel", response_model=JobOut)
def cancel_job(job_id: str) -> JobOut:
    """Cancels a job that is still waiting in the queue."""
    try:
        job = _service.cancel_job(job_id)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _to_out(job)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str) -> JobOut:
    """Returns the current state of a job."""
    try:
        job = _service.get_job(job_id)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_out(job)
