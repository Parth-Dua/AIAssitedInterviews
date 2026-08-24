"""Optional thin FastAPI wrapper around the `ratelimiter` library.

This exists only for realism (so the library could plausibly sit behind an
API gateway endpoint). It contains no graded logic of its own — it just
constructs a `TokenBucketRateLimiter` and calls `allow_request`. You do not
need to read or run this to complete the exercise; everything that's graded
lives in `ratelimiter/`.

Requires the optional `api` extra: `pip install -e ".[api]"`.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from ratelimiter import TokenBucketRateLimiter

app = FastAPI(title="Rate Limiter Gateway (demo)")

# A single default limiter shared across requests, purely for demo purposes.
_limiter = TokenBucketRateLimiter(capacity=10, refill_rate_per_second=1.0)


class CheckRequest(BaseModel):
    client_key: str


class CheckResponse(BaseModel):
    allowed: bool


@app.post("/check", response_model=CheckResponse)
def check(request: CheckRequest) -> CheckResponse:
    allowed = _limiter.allow_request(request.client_key)
    return CheckResponse(allowed=allowed)
