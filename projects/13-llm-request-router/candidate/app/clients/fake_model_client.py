"""A fully fake, deterministic stand-in for a real LLM inference client.

There is no network call, no real model, and no randomness anywhere in this
module. Given the same prompt, `FakeModelClient.complete` always returns the
same string (or always raises, or always returns a blank string) for the
lifetime of a given configuration. This exists purely so the router's async
control flow (retries, fallback, caching, validation) can be exercised and
tested deterministically, without depending on any real model provider.
"""

import asyncio
import hashlib


class ModelUnavailableError(Exception):
    """Raised when a model client cannot serve a completion right now.

    Stands in for the kind of transient upstream failure a real inference
    provider would surface (rate limiting, an outage, a timeout, ...).
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        super().__init__(f"{model_name} is unavailable")


class FakeModelClient:
    """A deterministic fake "model" identified by `name`.

    `unavailable_prompts` and `blank_response_prompts` are plain mutable
    sets. Tests (and this module's callers) can add prompts to or remove
    prompts from these sets between calls to simulate a model "going down"
    for a specific prompt and later "recovering" — there is no timer or
    real state machine involved, just set membership checked at call time.

    - A prompt in `unavailable_prompts` makes `complete()` raise
      `ModelUnavailableError` for that prompt.
    - A prompt in `blank_response_prompts` makes `complete()` return a
      whitespace-only string for that prompt, simulating a malformed/empty
      completion from the upstream model (as opposed to an outright error).
    - Any other prompt returns a deterministic, unique-per-prompt string
      derived from the prompt's SHA-256 hash, prefixed with this client's
      name so tests can tell which model actually served a given response.
    """

    def __init__(
        self,
        name: str,
        unavailable_prompts: set[str] | None = None,
        blank_response_prompts: set[str] | None = None,
    ):
        self.name = name
        self._unavailable_prompts = unavailable_prompts or set()
        self._blank_response_prompts = blank_response_prompts or set()

    async def complete(self, prompt: str) -> str:
        await asyncio.sleep(0)  # simulates async I/O without real delay/nondeterminism
        if prompt in self._unavailable_prompts:
            raise ModelUnavailableError(self.name)
        if prompt in self._blank_response_prompts:
            return "   "  # simulates a malformed/empty completion from the model
        return f"{self.name}:{hashlib.sha256(prompt.encode()).hexdigest()[:10]}"
