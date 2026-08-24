import uuid

from app.domain.job import Job
from app.repositories.job_repository import JobRepository


class InvalidJobStateError(Exception):
    def __init__(self, job_id: str, current_status: str):
        self.job_id = job_id
        self.current_status = current_status
        super().__init__(
            f"job {job_id} cannot perform this transition from status {current_status!r}"
        )


class JobService:
    """Orchestrates job lifecycle transitions on top of JobRepository.

    Legal transitions are centralized here as a table of
    action -> {statuses a job must currently be in for that action to be
    allowed}, rather than as separate ad-hoc boolean guards repeated in
    each method. Any status not listed for an action is rejected. This
    keeps "which transitions are legal" auditable in one place and makes
    it structurally impossible to add a new mutating method that forgets
    to check the job's current status.
    """

    _ALLOWED_SOURCE_STATUSES: dict[str, set[str]] = {
        "start": {"queued"},
        "finish": {"running"},
        "cancel": {"queued"},
    }

    def __init__(self, repository: JobRepository):
        self._repository = repository

    def create_job(self, payload: dict) -> Job:
        job = Job(id=str(uuid.uuid4()), payload=payload)
        self._repository.create(job)
        return job

    def get_job(self, job_id: str) -> Job:
        return self._repository.get(job_id)

    def _require_status(self, job: Job, action: str) -> None:
        if job.status not in self._ALLOWED_SOURCE_STATUSES[action]:
            raise InvalidJobStateError(job.id, job.status)

    def start_job(self, job_id: str) -> Job:
        job = self._repository.get(job_id)
        self._require_status(job, "start")
        job.status = "running"
        job.attempt_count += 1
        self._repository.save(job)
        return job

    def finish_job(self, job_id: str, result: str | None, error: str | None) -> Job:
        job = self._repository.get(job_id)
        self._require_status(job, "finish")
        job.status = "completed" if result is not None else "failed"
        job.result = result
        job.error = error
        self._repository.save(job)
        return job

    def cancel_job(self, job_id: str) -> Job:
        job = self._repository.get(job_id)
        self._require_status(job, "cancel")
        job.status = "cancelled"
        self._repository.save(job)
        return job
