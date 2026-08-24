from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    prompt: str = Field(min_length=1)


class CompletionResult(BaseModel):
    text: str
    model: str
    from_cache: bool
