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

    Valid transitions:
      queued  -> running    (start)
      queued  -> cancelled  (cancel)
      running -> completed  (finish, result given)
      running -> failed     (finish, error given)
    completed / failed / cancelled are terminal: no further start, finish,
    or cancel is accepted from any of them.
    """

    def __init__(self, repository: JobRepository):
        self._repository = repository

    def create_job(self, payload: dict) -> Job:
        job = Job(id=str(uuid.uuid4()), payload=payload)
        self._repository.create(job)
        return job

    def get_job(self, job_id: str) -> Job:
        return self._repository.get(job_id)

    def start_job(self, job_id: str) -> Job:
        job = self._repository.get(job_id)
        if job.status != "queued":
            raise InvalidJobStateError(job_id, job.status)
        job.status = "running"
        job.attempt_count += 1
        self._repository.save(job)
        return job

    def finish_job(self, job_id: str, result: str | None, error: str | None) -> Job:
        job = self._repository.get(job_id)
        if job.status != "running":
            raise InvalidJobStateError(job_id, job.status)
        job.status = "completed" if result is not None else "failed"
        job.result = result
        job.error = error
        self._repository.save(job)
        return job

    def cancel_job(self, job_id: str) -> Job:
        job = self._repository.get(job_id)
        if job.status != "queued":
            raise InvalidJobStateError(job_id, job.status)
        job.status = "cancelled"
        self._repository.save(job)
        return job
