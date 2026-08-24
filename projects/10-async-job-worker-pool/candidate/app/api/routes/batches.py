from fastapi import APIRouter

from app.models.schemas import BatchResult, BatchRunRequest
from app.services.job_service import JobService

router = APIRouter(prefix="/batches", tags=["batches"])

_service = JobService()


@router.post("/run", response_model=BatchResult)
async def run_batch(request: BatchRunRequest) -> BatchResult:
    """Run a batch of jobs across a pool of workers and report how it ended.

    Awaits the batch to full completion before responding — there is no
    background processing or polling involved from the client's
    perspective.
    """
    return await _service.run_batch(
        request.batch_id, request.job_count, request.num_workers
    )
