# Interview Follow-Up Questions (private)

1. **What was the root cause of the caching bug?**
   Strong answer: `complete()` writes to the cache after *both* the
   primary-success branch and the fallback branch, using the same key,
   with no check on which client actually produced the result. The fix
   scopes the cache write to only happen after a primary success.

2. **Why should fallback responses never be cached, in general terms
   beyond this specific scenario?**
   Strong answer: a fallback response exists to paper over a *temporary*
   degradation in the primary — it's explicitly a lower-quality or
   lower-confidence substitute for what the primary would have returned.
   Caching it treats a degraded, time-bound condition as if it were a
   stable, cacheable fact, which means the system keeps serving the worse
   answer long after the condition that caused it has resolved. The
   general principle: only cache a result when the source that produced it
   is the one you'd be equally happy to serve again unconditionally: a
   fallback's job is to be tried again next time, not memorized.

3. **How would you extend this if the router needed to support a THIRD
   tier of fallback model?**
   Strong answer (design-forward-thinking): generalize the two-model
   special case into a list/chain of clients tried in order (e.g.
   `self._models = [primary, secondary, tertiary]`), with the caching rule
   generalizing to "only cache a result produced by `self._models[0]`" (or
   more precisely, by whichever tier is considered the non-degraded,
   canonical source) — everything downstream of that first tier is a
   degradation and should never be cached. Retry budget could either apply
   per-tier or be shared across the whole chain; a strong candidate should
   at least flag that as a design decision to make explicit, not something
   to leave ambiguous.

4. **What would change if two concurrent requests for the same
   never-before-seen prompt arrived at the same time?**
   Discussion only, not required to implement here (a nod to Project 10's
   concurrency theme, not a new concurrency requirement for this
   exercise). Strong answer: as written, both requests would miss the
   cache, both would call the primary independently, and both would
   attempt to write the same cache key — a classic cache stampede /
   duplicate-work scenario. A production fix might use a per-key async
   lock or an in-flight-request map so the second caller awaits the
   first's in-progress call instead of issuing a duplicate one, or accept
   the duplicate work as a deliberate tradeoff for simplicity at low
   concurrency. There's no single "correct" answer expected here — the
   signal is whether the candidate can identify the race and reason about
   at least one mitigation and its tradeoffs.

5. **How did you verify the validation feature was actually complete, not
   just "the primary case works"?**
   Strong answer: configured *both* the primary and fallback fake clients
   to return blank responses for the same prompt and confirmed a clear
   exception (`NoValidCompletionError`) was raised rather than a blank
   `CompletionResult` being silently returned — this is the case that
   distinguishes "validated the primary" from "validated both models,"
   and it's easy to miss if you stop testing once the public blank-primary
   test passes.

6. **Is there another valid way to implement the cache-write fix?**
   Strong answer: yes — instead of simply deleting the fallback branch's
   `self._cache.set(...)` call, an equally valid implementation keeps a
   single cache-write call site reached from both branches, guarded by an
   explicit `if result.model == self._primary.name:` (or equivalent)
   check. Any implementation preserving "a fallback-sourced result is
   never written to the cache, under any prompt or retry configuration" is
   acceptable — the exact code shape doesn't matter.
