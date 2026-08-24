from typing import Optional

from pydantic import BaseModel, Field, model_validator


class JobCreateRequest(BaseModel):
    payload: dict = Field(default_factory=dict)


class JobFinishRequest(BaseModel):
    result: Optional[str] = None
    error: Optional[str] = None

    @model_validator(mode="after")
    def _exactly_one_of_result_or_error(self):
        if (self.result is None) == (self.error is None):
            raise ValueError("exactly one of 'result' or 'error' must be provided")
        return self


class JobOut(BaseModel):
    id: str
    status: str
    payload: dict
    result: Optional[str] = None
    error: Optional[str] = None
    attempt_count: int
