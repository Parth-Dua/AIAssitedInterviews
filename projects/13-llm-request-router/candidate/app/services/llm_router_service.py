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


class LLMRouterService:
    """Routes a chat-completion request to a primary model, retrying it a
    bounded number of times, and falling back to a secondary model if the
    primary can't serve the request. A response cache sits in front of
    both models so repeated identical prompts don't re-invoke a model
    client unnecessarily.

    Only completions produced by the primary model should ever be cached.
    A response served by the fallback model represents a temporary
    degradation (the primary being down) and must never be cached — it
    should never keep being served once the primary is healthy again.
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

        last_error: Exception | None = None
        for _ in range(self._max_retries):
            try:
                text = await self._primary.complete(prompt)
                result = CompletionResult(
                    text=text, model=self._primary.name, from_cache=False
                )
                self._cache.set(prompt, result)
                return result
            except ModelUnavailableError as e:
                last_error = e

        text = await self._fallback.complete(prompt)
        result = CompletionResult(text=text, model=self._fallback.name, from_cache=False)
        self._cache.set(prompt, result)
        return result
