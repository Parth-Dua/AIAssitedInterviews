"""Reference solution for app/services/llm_router_service.py.

Fixes the cache-poisoning-by-fallback bug (fallback-sourced results are
never written to the cache) and implements the missing response-validation
feature (a blank/whitespace-only model response is treated the same as
ModelUnavailableError for retry/fallback purposes; if the fallback also
returns blank, NoValidCompletionError is raised instead of a blank result).
"""

from app.cache.response_cache import ResponseCache
from app.clients.fake_model_client import FakeModelClient, ModelUnavailableError
from app.models.schemas import CompletionResult

DEFAULT_MAX_RETRIES = 3


class NoValidCompletionError(Exception):
    """Raised when neither the primary nor the fallback model could produce
    a usable (non-blank) completion for a prompt.
    """

    def __init__(self, prompt: str):
        self.prompt = prompt
        super().__init__(f"no valid completion available for prompt {prompt!r}")


def _is_blank(text: str) -> bool:
    """A response consisting only of whitespace (or empty) is malformed
    and must be treated the same as an upstream failure.
    """
    return not text.strip()


class LLMRouterService:
    """Routes a chat-completion request to a primary model, retrying it a
    bounded number of times, and falling back to a secondary model if the
    primary can't serve the request. A response cache sits in front of
    both models so repeated identical prompts don't re-invoke a model
    client unnecessarily.

    Only completions produced by the primary model are ever cached. A
    response served by the fallback model represents a temporary
    degradation (the primary being down or malfunctioning) and must never
    be cached — it must never keep being served once the primary is
    healthy again.
    """

    def __init__(
        self,
        primary: FakeModelClient,
        fallback: FakeModelClient,
        cache: ResponseCache,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self._primary = primary
        self._fallback = fallback
        self._cache = cache
        self._max_retries = max_retries

    async def complete(self, prompt: str) -> CompletionResult:
        cached = self._cache.get(prompt)
        if cached is not None:
            return CompletionResult(text=cached.text, model=cached.model, from_cache=True)

        for _ in range(self._max_retries):
            try:
                text = await self._primary.complete(prompt)
            except ModelUnavailableError:
                continue

            if _is_blank(text):
                # A blank response is a malformed completion, not a valid
                # one — treat it like a failure and retry against the
                # primary just as we would for ModelUnavailableError.
                continue

            result = CompletionResult(text=text, model=self._primary.name, from_cache=False)
            self._cache.set(prompt, result)
            return result

        text = await self._fallback.complete(prompt)
        if _is_blank(text):
            raise NoValidCompletionError(prompt)

        # Deliberately not cached: a fallback-sourced result must always be
        # freshly attempted against the primary next time, never served
        # from a stale cache entry.
        return CompletionResult(text=text, model=self._fallback.name, from_cache=False)
