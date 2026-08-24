from pydantic import BaseModel, Field


class BatchRunRequest(BaseModel):
    batch_id: str
    job_count: int = Field(gt=0)
    num_workers: int = Field(gt=0)


class BatchResult(BaseModel):
    batch_id: str
    remaining: int
    finalize_count: int
