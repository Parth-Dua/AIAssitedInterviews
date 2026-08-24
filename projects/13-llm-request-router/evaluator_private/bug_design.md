# Bug + Feature Design (private — do not expose to candidate)

This project bundles a cache-correctness bug and a response-validation
feature-implementation task that share the same code path
(`LLMRouterService.complete`), so they're documented together.

## Part A — The cache-poisoning-by-fallback bug

### Expected behavior
Only completions produced by the **primary** model are ever written to the
cache. A completion produced by the **fallback** model must never be
cached — it represents a temporary degradation (the primary being down)
and must be freshly re-attempted against the primary on the very next
request for that prompt, no matter how long ago the fallback response was
served.

### Actual (buggy) behavior
`app/services/llm_router_service.py::LLMRouterService.complete` calls
`self._cache.set(prompt, result)` unconditionally after *both* the
primary-success branch and the fallback branch:

```python
text = await self._fallback.complete(prompt)
result = CompletionResult(text=text, model=self._fallback.name, from_cache=False)
self._cache.set(prompt, result)          # writes a fallback-sourced result to the cache
return result
```

Both writes use the exact same cache key (just `prompt` — there is no
per-model or per-source component to the key), so once a fallback response
has been cached, it is indistinguishable from a primary response to the
read path at the top of `complete()`: `cached = self._cache.get(prompt)`
returns it and it is served forever, even after the primary recovers,
until the process restarts or something else evicts that key.

### Root cause
Unconditional cache write: the code that decides *whether* to write to the
cache doesn't consult *which client actually produced the result*. The
cache module itself (`app/cache/response_cache.py`) is correct and
unbugged — a plain `get`/`set`/`delete` dict-backed store with no opinion
about what should be cached. The bug is entirely a policy mistake in the
service layer: it never checks "did this come from the primary?" before
calling `self._cache.set(...)`.

### Violated invariant
"A cache entry is only ever written when the result came from the primary
model; fallback-sourced results are always freshly attempted next time."
(Stated as team policy in the candidate README's bug report section.)

### Relevant execution path
`POST /completions` (`app/api/routes/completions.py`) → `app/api/deps.py`
(wires the singleton primary/fallback clients, cache, and service) →
`LLMRouterService.complete` (`app/services/llm_router_service.py`, the
bug) → `FakeModelClient.complete` (`app/clients/fake_model_client.py`,
correct and given — must be read to understand the `unavailable_prompts`
test hook that simulates a model "going down" and "recovering") →
`ResponseCache.get`/`set` (`app/cache/response_cache.py`, correct — the
bug is in *how* the service calls it, not in the cache implementation
itself).

### Evidence available to the candidate
- The failing public test
  `test_fallback_response_not_served_once_primary_recovers` reproduces the
  exact reported scenario: primary down → fallback serves the prompt →
  primary's `unavailable_prompts` set is cleared (simulating recovery) →
  calling `complete()` again still returns the fallback's answer instead
  of retrying the primary.
- The README states the policy explicitly: "Only primary-model responses
  should ever be cached."
- Reading `complete()` end-to-end shows two `self._cache.set(prompt, ...)`
  call sites, one after the primary-success branch and one after the
  fallback branch, with no conditional distinguishing them.
- Reading `FakeModelClient` shows `unavailable_prompts` is a plain mutable
  set the test can `.discard()` from mid-test to simulate recovery — this
  is the mechanism the reproduction test relies on, and a candidate needs
  to notice it to understand *why* the test's second call is expected to
  route to the primary again.

### Reasonable hypotheses
1. (Correct) The cache write after a successful fallback call is
   unconditional — it should only ever happen after a successful *primary*
   call.
2. (Plausible, wrong) "Maybe the cache needs a TTL (time-to-live) so stale
   entries expire on their own after a while." This is a real, useful
   pattern (see Project 6's notification-preferences-cache exercise, which
   is specifically about that), but it is **not** the actual fix needed
   here: a TTL only bounds *how long* a wrong entry can live, it doesn't
   stop a fallback response from being cached in the first place, and
   there is no time-based staleness signal available anyway — the primary
   could recover one second after the fallback response was cached, and a
   TTL long enough to be useful for a real inference cache (minutes to
   hours) would still serve the stale fallback answer for that whole
   window. The bug report itself makes this explicit: the problem isn't
   that the stale response lived "too long," it's that it should never
   have been cached in the first place. A candidate proposing a TTL should
   be asked: "would a TTL of any length actually satisfy the reported
   complaint, given the primary could come back up moments later?"
3. (Plausible, wrong) "Maybe the cache key needs to include which model
   served it, so primary and fallback responses don't collide." This
   would stop the *symptom* observed in the bug report (a fallback answer
   being returned as if it were the primary's) but is still wrong: it
   would mean a fallback-sourced entry gets cached under its own key and
   then legitimately served *forever* from then on for that prompt,
   satisfied its own cache hit — which directly contradicts "a response
   served by the fallback model ... should never keep being served." The
   fix has to prevent the write, not just relabel it.

### Intended regression tests
`test_fallback_response_not_served_once_primary_recovers` (already present
as a public test) plus the hidden
`test_fallback_response_never_cached_second_scenario`, which exercises the
same class of bug with a different prompt and a different `max_retries`
value to rule out a fix narrowly tailored to the public test's exact
scenario (e.g. hardcoding a specific prompt string, or only fixing one of
the two call sites).

### Acceptable fixes
- Only call `self._cache.set(prompt, result)` in the primary-success
  branch; never call it after the fallback branch.
- Equivalent: keep a single cache-write call site reached from both
  branches, guarded by an explicit condition on which client produced the
  result (e.g. `if result.model == self._primary.name: self._cache.set(...)`),
  as long as the net effect is identical — fallback-sourced results are
  never written to the cache, under any configuration.
- The read path (`self._cache.get(prompt)` at the top of `complete()`) and
  the cache key scheme (still just `prompt`) do not need to change.

### Tempting but incomplete/wrong fix
Overcorrecting by ripping out caching entirely — deleting both
`self._cache.set(...)` calls (or otherwise making `complete()` never write
to the cache at all), on the reasoning that "if nothing is ever cached,
nothing can ever be served stale."

This does fully solve the reported bug's scenario — a repeat call after
recovery now always retries the primary, since nothing was ever cached to
begin with. But it also destroys the legitimate, intended, and
**publicly tested** happy-path behavior: a healthy primary's successful
response **is** supposed to be cached and reused on a repeat identical
prompt (`from_cache=True` on the second call), specifically so repeated
identical prompts don't have to pay the cost of a model call again. That
requirement is exercised directly by the **public** test
`test_repeat_prompt_while_primary_healthy_is_served_from_cache` (unit
level).

**Validated:** applying this exact overcorrected `LLMRouterService`
(caching removed entirely, with the blank-response validation feature
otherwise correctly implemented) to a temporary copy of the candidate
repository, with the hidden tests copied in, and running `pytest -q`,
produced **2 failed, 10 passed**. The two failures were exactly:
- `tests/test_llm_router_service.py::test_repeat_prompt_while_primary_healthy_is_served_from_cache`
  (**public**)
- `tests/test_llm_router_hidden.py::test_primary_fails_once_then_succeeds_is_cached_and_no_fallback`
  (**hidden**)

Every other public and hidden test passed, including the reported-bug
reproduction test itself. This means the overcorrection is caught by the
given **public** test suite already, not only by a hidden test — a
candidate who runs `pytest -q` after this "fix" and reads the output will
see a regression, not a clean pass. The hidden test exists as a second
line of defense: it confirms caching still works correctly even when the
primary needed a retry before succeeding, not just on a first-try success,
ruling out a narrower "fix" that special-cases the exact public-test
sequence.

## Part B — The response-validation feature

### Requested behavior
A response consisting only of whitespace (or empty) is a malformed
completion, not a valid one, and must never be handed back to the caller
as-is:
- For the **primary**: a blank response must count toward the retry loop
  exactly like a `ModelUnavailableError` would — it should NOT be returned
  or cached, and the router should keep retrying (up to `max_retries`)
  before falling back.
- For the **fallback**: its response must ALSO be validated the same way.
  If the fallback's response is also blank after the primary exhausts its
  retries, the router must raise a clear `NoValidCompletionError` (a new
  exception, defined in `llm_router_service.py`) rather than returning a
  blank/invalid `CompletionResult` to the caller.

### Starting (incomplete) state
`FakeModelClient` already supports a `blank_response_prompts` set (a test
hook, exactly parallel to `unavailable_prompts`) that makes `complete()`
return `"   "` for a given prompt — this is given and correct, not
something the candidate needs to add. But `LLMRouterService.complete`
treats *any* string the client returns as a valid completion: there is no
check anywhere for blank/whitespace-only text, so a blank primary response
is cached and returned to the caller exactly as if it were valid.

### Correct design
- Wrap (or otherwise gate) the primary-branch success path with a
  blankness check — e.g. `if not text.strip(): continue` inside the retry
  loop, immediately after `await self._primary.complete(prompt)` succeeds
  without raising — so a blank response falls through to the next retry
  attempt exactly the way a caught `ModelUnavailableError` does.
- After the retry loop is exhausted and the fallback is called, apply the
  same blankness check to the fallback's response. If it's blank, raise
  `NoValidCompletionError(prompt)` instead of constructing and returning a
  `CompletionResult`.
- Neither a blank primary attempt nor a raised
  `NoValidCompletionError` should ever reach `self._cache.set(...)`.

### Tempting but incomplete/wrong implementation
Validating the primary's response but forgetting to validate the
fallback's — i.e., treating a blank *primary* response as a failure
(correctly triggering the retry loop and eventual fallback) but still
returning the fallback's response unconditionally, blank or not. This
passes the public blank-primary test (since that test's fallback client
has no `blank_response_prompts` configured, so the fallback happens to
return a real response) but fails the hidden
`test_both_primary_and_fallback_blank_raises_no_valid_completion` test,
which configures **both** clients to return blank for the same prompt and
asserts `NoValidCompletionError` is raised rather than a blank
`CompletionResult` being returned.

### Acceptable implementations
- The reference `LLMRouterService.complete` above (a small `_is_blank`
  helper, checked at both the primary-retry site and after the fallback
  call).
- Equivalent: inlining the `text.strip()` check at each site instead of a
  shared helper, as long as both the primary and fallback responses are
  validated and a blank result never reaches the cache or the caller.
- Not acceptable: validating only one of the two clients' responses, or
  validating but still caching/returning the blank result anyway.

## Why this is interview-appropriate
Retry/fallback/cache orchestration for an unreliable upstream dependency —
"retry N times, fall back to a secondary provider, cache the good answer,
never cache the degraded one, and validate the response before trusting
it" — is an extremely common real backend interview and production topic.
An AI-inference gateway sitting in front of two model providers is simply
one current example of "a service that calls a flaky, rate-limited,
occasionally-malformed upstream and needs to be reliable anyway"; the same
shape shows up verbatim for payment processors, third-party APIs, or
internal microservices with no ML involved at all. No ML knowledge is
required or tested — everything about "which model" is just a label on a
deterministic string, and the actual skills exercised are async control
flow, cache-write policy correctness, and input/output validation.
