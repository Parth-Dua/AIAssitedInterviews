from app.cache.response_cache import ResponseCache
from app.clients.fake_model_client import FakeModelClient
from app.services.llm_router_service import LLMRouterService


def make_router(
    unavailable_prompts=None,
    blank_response_prompts=None,
    fallback_blank_response_prompts=None,
    max_retries=3,
):
    primary = FakeModelClient(
        name="primary-model",
        unavailable_prompts=unavailable_prompts,
        blank_response_prompts=blank_response_prompts,
    )
    fallback = FakeModelClient(
        name="fallback-model",
        blank_response_prompts=fallback_blank_response_prompts,
    )
    cache = ResponseCache()
    service = LLMRouterService(primary, fallback, cache, max_retries=max_retries)
    return service, primary, fallback, cache


async def test_primary_success_returns_primary_response():
    service, primary, fallback, cache = make_router()
    result = await service.complete("hello")
    assert result.model == primary.name
    assert result.from_cache is False
    assert result.text  # non-blank


async def test_repeat_prompt_while_primary_healthy_is_served_from_cache():
    """A repeat identical prompt, while the primary is healthy, should be
    served from the cache rather than re-invoking the primary model.
    """
    service, primary, fallback, cache = make_router()

    first = await service.complete("hello")
    second = await service.complete("hello")

    assert first.from_cache is False
    assert second.from_cache is True
    assert second.text == first.text
    assert second.model == first.model


async def test_primary_always_unavailable_falls_back():
    prompt = "outage-prompt"
    service, primary, fallback, cache = make_router(unavailable_prompts={prompt})

    result = await service.complete(prompt)

    assert result.model == fallback.name
    assert result.from_cache is False


async def test_fallback_response_not_served_once_primary_recovers():
    """Bug report: a brief primary outage caused some prompts to be served
    by the fallback model. Long after the primary recovered, those same
    prompts kept getting the stale cached fallback answer instead of
    trying the (now healthy) primary again.
    """
    prompt = "flaky-prompt"
    service, primary, fallback, cache = make_router(unavailable_prompts={prompt})

    first = await service.complete(prompt)
    assert first.model == fallback.name  # served by fallback while primary is down

    # Primary recovers for this prompt.
    primary._unavailable_prompts.discard(prompt)

    second = await service.complete(prompt)
    assert second.model == primary.name, (
        "the primary has recovered, so this prompt should be routed to the "
        "primary again rather than served from a stale cached fallback "
        "response"
    )
    assert second.from_cache is False


async def test_blank_primary_response_is_not_returned_as_valid():
    """A whitespace-only response from the primary is a malformed
    completion, not a valid one, and must never be handed back to the
    caller as-is — it should be treated like a failure and trigger the
    same retry/fallback path as ModelUnavailableError.
    """
    prompt = "malformed-response-prompt"
    service, primary, fallback, cache = make_router(blank_response_prompts={prompt})

    result = await service.complete(prompt)

    assert result.text.strip() != "", (
        "a blank/whitespace-only model response must never be returned as "
        "a valid completion"
    )
    assert result.model == fallback.name
