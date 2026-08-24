from fastapi import APIRouter

from app.api.deps import llm_router_service
from app.models.schemas import CompletionRequest, CompletionResult

router = APIRouter(prefix="/completions", tags=["completions"])


@router.post("", response_model=CompletionResult)
async def create_completion(request: CompletionRequest) -> CompletionResult:
    """Route a chat-completion request to the primary model (with retries),
    falling back to the secondary model if needed, using the router's
    response cache where applicable.
    """
    return await llm_router_service.complete(request.prompt)
