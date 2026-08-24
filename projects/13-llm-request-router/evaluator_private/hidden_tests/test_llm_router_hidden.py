"""Hidden tests. Copy this file into candidate/tests/ (it is not present in
the candidate repo) and run `pytest` from candidate/ after applying a
candidate's fix, or after applying
reference_solution/llm_router_service.py to validate the answer key.
"""

import pytest

from app.cache.response_cache import ResponseCache
from app.clients.fake_model_client import FakeModelClient, ModelUnavailableError
from app.services.llm_router_service import LLMRouterService, NoValidCompletionError


class CallCountingClient:
    """Wraps a FakeModelClient and counts calls to `complete()`, without
    altering its behavior at all — every call is forwarded unchanged. Used
    to assert exactly how many times the router actually invoked the
    primary during its retry loop, non-invasively (FakeModelClient itself
    is not modified).
    """

    def __init__(self, wrapped: FakeModelClient):
        self._wrapped = wrapped
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._wrapped.name

    async def complete(self, prompt: str) -> str:
        self.call_count += 1
        return await self._wrapped.complete(prompt)


class FailNTimesThenDelegateClient:
    """Wraps a FakeModelClient so the first `fail_times` calls raise
    ModelUnavailableError unconditionally, then subsequent calls delegate
    to the wrapped client normally. Simulates "the primary recovers partway
    through a single retry loop" — something FakeModelClient's static
    `unavailable_prompts` membership can't express on its own, since that
    would fail *every* call for a given prompt, not just the first N.
    """

    def __init__(self, wrapped: FakeModelClient, fail_times: int):
        self._wrapped = wrapped
        self._remaining_failures = fail_times
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._wrapped.name

    async def complete(self, prompt: str) -> str:
        self.call_count += 1
        if self._remaining_failures > 0:
            self._remaining_failures -= 1
            raise ModelUnavailableError(self._wrapped.name)
        return await self._wrapped.complete(prompt)


async def test_primary_fails_once_then_succeeds_is_cached_and_no_fallback():
    """Retry-then-succeed must still cache correctly — this is not covered
    by the public first-try-success test, and guards against a fix that
    only caches when the primary succeeds on its very first attempt.
    """
    raw_primary = FakeModelClient("primary-model")
    primary = FailNTimesThenDelegateClient(raw_primary, fail_times=1)
    fallback = FakeModelClient("fallback-model")
    cache = ResponseCache()
    service = LLMRouterService(primary, fallback, cache, max_retries=3)

    result = await service.complete("retry-then-succeed")

    assert result.model == "primary-model"
    assert result.from_cache is False
    assert primary.call_count == 2  # one failure, then a success — no fallback needed

    second = await service.complete("retry-then-succeed")
    assert second.from_cache is True
    assert second.model == "primary-model"


async def test_both_primary_and_fallback_blank_raises_no_valid_completion():
    prompt = "double-malformed"
    primary = FakeModelClient("primary-model", blank_response_prompts={prompt})
    fallback = FakeModelClient("fallback-model", blank_response_prompts={prompt})
    cache = ResponseCache()
    service = LLMRouterService(primary, fallback, cache, max_retries=2)

    with pytest.raises(NoValidCompletionError):
        await service.complete(prompt)

    assert cache.get(prompt) is None, (
        "a failed attempt (no valid completion from either model) must not "
        "populate the cache"
    )


async def test_primary_call_count_matches_max_retries_when_always_unavailable():
    prompt = "always-down"
    raw_primary = FakeModelClient("primary-model", unavailable_prompts={prompt})
    primary = CallCountingClient(raw_primary)
    fallback = FakeModelClient("fallback-model")
    cache = ResponseCache()
    max_retries = 4
    service = LLMRouterService(primary, fallback, cache, max_retries=max_retries)

    result = await service.complete(prompt)

    assert result.model == fallback.name
    assert primary.call_count == max_retries, (
        "the primary should be attempted exactly max_retries times before "
        "falling back — no more, no fewer"
    )


async def test_fallback_response_never_cached_second_scenario():
    """Same class of bug as the reported one (fallback-sourced responses
    must never be cached), with a different prompt and a different
    max_retries value than the public test, to rule out a fix narrowly
    special-cased to the public test's exact scenario.
    """
    prompt = "second-outage-prompt"
    primary = FakeModelClient("primary-model", unavailable_prompts={prompt})
    fallback = FakeModelClient("fallback-model")
    cache = ResponseCache()
    service = LLMRouterService(primary, fallback, cache, max_retries=1)

    await service.complete(prompt)
    assert cache.get(prompt) is None, (
        "a fallback-sourced result must never be written to the cache, "
        "under any configuration"
    )

    primary._unavailable_prompts.discard(prompt)
    result = await service.complete(prompt)
    assert result.model == primary.name
    assert result.from_cache is False
