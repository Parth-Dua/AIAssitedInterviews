# Scoring Rubric — Project 13 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → service → client/cache flow; read `FakeModelClient` closely enough to know what `unavailable_prompts` and `blank_response_prompts` do and why they're plain mutable sets, before editing. |
| Debugging process | 10 | Reproduced the caching bug via the failing test (or an equivalent manual repro: mark a prompt unavailable, call `complete()`, clear the unavailable marker, call again) before making changes; didn't shotgun-edit across files. |
| Root-cause reasoning | 15 | Correctly identifies that the cache write after the fallback branch is unconditional and shouldn't exist (or must be conditioned on the result's source); can articulate the general invariant ("only primary-sourced results are cached") and why a TTL alone would not actually fix the reported complaint. |
| Bug-fix correctness | 15 | Public `test_fallback_response_not_served_once_primary_recovers` passes; hidden `test_fallback_response_never_cached_second_scenario` passes (fix isn't narrowly scoped to one prompt/config); the legitimate primary-caching happy path (`test_repeat_prompt_while_primary_healthy_is_served_from_cache`) still passes — i.e. caching wasn't removed wholesale. |
| Feature/validation implementation quality | 20 | Blank/whitespace responses from the primary correctly trigger the same retry path as `ModelUnavailableError`; the fallback's response is also validated; `NoValidCompletionError` is raised (not a blank `CompletionResult` returned) when both are blank; a blank response is never written to the cache; retry-then-succeed still returns the primary's response and still caches it correctly (not just first-try success). |
| Tests added | 10 | Added at least one regression test beyond the given failing ones — ideally one exercising "both primary and fallback blank" (the case that most distinguishes a complete validation implementation from a primary-only one) and/or a second cache-poisoning scenario with a different prompt/`max_retries`. |
| Scope discipline | 5 | Did not modify `FakeModelClient`, `ResponseCache`, the response schema, or unrelated endpoints; changes stayed within `llm_router_service.py` (plus imports/exception definitions there). |
| Communication | 15 | Can clearly state: the caching bug's root cause and why the fix is correct; why a TTL would not have actually solved the reported complaint; why both models' responses need independent blank-response validation, not just the primary's; what they checked to confirm both the fix and the feature work together without breaking the happy-path caching behavior. |

**Passing bar (strong intern/new-grad signal):** ≥75, all hidden tests
pass, and the candidate can explain both the cache-poisoning root cause
and the primary-vs-fallback validation distinction without prompting.

**Red flags:**
- Fix passes the reported-bug test but fails
  `test_repeat_prompt_while_primary_healthy_is_served_from_cache` (public)
  or `test_primary_fails_once_then_succeeds_is_cached_and_no_fallback`
  (hidden) — the "remove caching entirely" overcorrection. See
  `bug_design.md`.
- Candidate validates the primary's response for blankness but not the
  fallback's, so `test_both_primary_and_fallback_blank_raises_no_valid_completion`
  (hidden) fails and a blank `CompletionResult` can still reach the
  caller.
- Candidate proposes a cache TTL as "the fix" for Part A and cannot
  explain, when pressed, why a TTL doesn't actually address the reported
  scenario (the primary could recover moments after the fallback response
  was cached).
- Candidate cannot explain *why* either the fix or the validation design
  is correct, only that changing X made a test pass.
- Candidate treats this as an ML/prompt-engineering exercise (e.g. tries
  to "improve" the fake model's output text, or asks about real model
  behavior) rather than recognizing it as an async orchestration and cache
  correctness problem with fake, deterministic clients.
