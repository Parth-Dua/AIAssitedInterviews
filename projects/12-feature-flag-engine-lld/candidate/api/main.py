"""Optional thin FastAPI wrapper around the `flagengine` library.

This exists only for realism (so the library could plausibly sit behind an
internal feature-flag service endpoint). It contains no graded logic of its
own — it just constructs a `PercentageRolloutFlag` and calls `is_enabled`.
You do not need to read or run this to complete the exercise; everything
that's graded lives in `flagengine/`.

Requires the optional `api` extra: `pip install -e ".[api]"`.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from flagengine import PercentageRolloutFlag

app = FastAPI(title="Feature Flag Service (demo)")

# A single demo flag shared across requests, purely for demo purposes.
_flag = PercentageRolloutFlag(flag_name="new-checkout-flow", rollout_percentage=25.0)


class CheckRequest(BaseModel):
    user_id: str


class CheckResponse(BaseModel):
    enabled: bool


@app.post("/flags/new-checkout-flow/check", response_model=CheckResponse)
def check(request: CheckRequest) -> CheckResponse:
    enabled = _flag.is_enabled({"user_id": request.user_id})
    return CheckResponse(enabled=enabled)


@app.get("/flags/new-checkout-flow/check", response_model=CheckResponse)
def check_get(user_id: str) -> CheckResponse:
    enabled = _flag.is_enabled({"user_id": user_id})
    return CheckResponse(enabled=enabled)
