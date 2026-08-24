from app.domain.job import Job


class JobNotFoundError(Exception):
    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"job not found: {job_id}")


class JobRepository:
    """In-memory store of Job records, keyed by id.

    In production this would be backed by a database table; here it's a
    plain dict so the exercise has no external dependencies.
    """

    def __init__(self):
        self._jobs: dict[str, Job] = {}

    def create(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job:
        job = self._jobs.get(job_id)
        if job is None:
            raise JobNotFoundError(job_id)
        return job

    def save(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job
