# Expected Reasoning Path

## Part A — the caching bug

1. Run `pytest -q`; observe `test_fallback_response_not_served_once_primary_recovers`
   fails while most other tests pass.
2. Read the test: primary is put into `unavailable_prompts` for a prompt,
   `complete()` is called (fallback serves it, as expected), then the
   prompt is removed from `unavailable_prompts` (primary "recovers"), and
   `complete()` is called again — the assertion expects the second call's
   `model` to be the primary's name, but it's still the fallback's.
3. Open `app/services/llm_router_service.py`; read `complete()` end to
   end. Notice the cache read at the top (`self._cache.get(prompt)`), the
   cache write after the primary-success branch, and a *second* cache
   write after the fallback branch — using the exact same key.
4. Cross-check against the README's stated policy: "Only primary-model
   responses should ever be cached... a response served by the fallback
   model must never be cached."
5. Recognize that the second `self._cache.set(...)` call (after the
   fallback branch) is the root cause — it should not exist, or should be
   conditioned on the result having come from the primary.
6. Read `app/clients/fake_model_client.py` to understand that
   `unavailable_prompts` is a plain mutable set the reproduction test
   mutates mid-test to simulate "the primary recovers" — this is what
   makes the second `complete()` call in the failing test meaningful.
7. Remove (or condition) the fallback-branch cache write. Re-run the
   failing test; it should now pass. Also re-run
   `test_repeat_prompt_while_primary_healthy_is_served_from_cache` to
   confirm the *legitimate* primary-caching behavior still works — this
   guards against the overcorrection of removing caching entirely (see
   `bug_design.md`).
8. Explain: a fallback response represents a temporary degradation and
   must never poison the cache for a prompt the primary can serve once
   healthy; the fix scopes the cache write to "only after a primary
   success," not "after any successful completion."

## Part B — the response-validation feature

1. Read the README's feature request: "some responses come back
   malformed/empty and should never be handed back to the caller."
2. Notice the failing public test
   `test_blank_primary_response_is_not_returned_as_valid`: it configures
   the primary's `blank_response_prompts` for a prompt and asserts the
   returned `text` is non-blank and the response was actually served by
   the fallback.
3. Read `FakeModelClient.complete` to see that a prompt in
   `blank_response_prompts` returns `"   "` (whitespace) without raising —
   this is a *different* failure mode than `ModelUnavailableError`, and
   `complete()` currently has no code path that treats a returned string
   as anything but valid.
4. Design the fix: inside the retry loop, after a successful (non-raising)
   call to the primary, check whether the text is blank
   (`not text.strip()`); if so, treat it like a caught
   `ModelUnavailableError` and continue the loop rather than returning or
   caching it.
5. Apply the same check to the fallback's response after the retry loop is
   exhausted. If the fallback's response is also blank, raise a new
   `NoValidCompletionError` (defined near the top of
   `llm_router_service.py`, matching the style of `ModelUnavailableError`)
   instead of returning a blank `CompletionResult`.
6. Re-run the full suite; both the previously-failing bug test and the
   previously-failing feature test should now pass, along with everything
   that was already passing.
7. Write (or recognize the value of) an additional test where *both* the
   primary and fallback are configured to return blank, confirming
   `NoValidCompletionError` is raised rather than a blank result being
   silently returned — this is exactly what distinguishes a complete
   validation implementation from one that only checks the primary.
8. Explain: a blank/whitespace response is a malformed completion, not
   a "successful but empty" one, so it must be treated the same as an
   outright failure for retry/fallback purposes — and once the router has
   truly exhausted both models without a usable answer, the caller needs a
   clear, distinct signal (`NoValidCompletionError`) rather than being
   handed unusable text.

A strong candidate reaches a correct root-cause diagnosis for Part A within
20-25 minutes given the failing test as a starting point, and a correct
design for Part B within another 25-35 minutes, leaving time to add tests
and verify nothing else broke.
