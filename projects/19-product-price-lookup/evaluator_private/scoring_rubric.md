# Scoring Rubric — Project 19 (100 points)

| Category | Points | Notes |
|---|---|---|
| Repository comprehension | 10 | Understood the route → controller → service → cache flow, and correctly identified `priceCache.ts`, `pricingClient.ts`, and `lastKnownPriceRepository.ts` as given/correct supporting files rather than assuming the bug could be anywhere. |
| Debugging process | 15 | Reproduced the bug via the failing tests (or an equivalent manual repro: USD lookup, then EUR lookup, same product) before making changes; didn't shotgun-edit multiple files. |
| Root-cause reasoning | 20 | Correctly identifies that `buildCacheKey` in `priceService.ts` accepts `currency` but never uses it, so the cache key only depends on `productId`; can articulate the violated invariant ("a cached price is only valid for the exact `(productId, currency)` pair it was fetched for") and ruled out at least one of the two plausible-wrong hypotheses (pricing client ignoring currency; fallback repository misfiring) by reading the relevant file or test, not just by assumption. |
| Correctness of fix | 25 | Public tests pass; hidden tests pass — including the delimiter-collision test (catches the "just concatenate `productId` and `currency` with no separator" incomplete fix) and the cross-product isolation test (catches an over-eager fix that collapses to a single global cache entry); the cache/fallback/TTL happy paths still work; per-currency TTL expiry still works independently for USD and EUR. |
| Tests added/improved | 10 | Added at least one regression test beyond the given failing ones (e.g., a same-product-different-currency test, a delimiter-collision test on their own key construction), or meaningfully strengthened existing coverage. |
| Scope discipline | 5 | Did not modify unrelated files/behavior (`priceCache.ts`, `pricingClient.ts`, `lastKnownPriceRepository.ts` internals, the `GET` route shape, seed data) without justification. |
| Communication / explanation | 15 | Can clearly state expected vs. actual behavior, root cause, why the fix is correct (including why a delimiter is needed, not just that `currency` is now included), and what else they checked to rule out the two plausible-wrong hypotheses. |

**Passing bar (strong mid-level signal):** ≥75, hidden tests pass, and
candidate can explain root cause — including the delimiter-safety point —
without prompting.

**Red flags:**
- Fix passes the two originally-failing tests but fails
  `buildCacheKey — composite key collision safety` or its behavioral
  counterpart (the "concatenate with no delimiter" incomplete fix — see
  `bug_design.md`).
- Fix makes the cache key depend only on `currency` (dropping `productId`),
  or introduces a single global cache shared across all products — fails
  the cross-product isolation hidden test and the existing public
  different-product coverage.
- Candidate cannot explain *why* concatenation without a delimiter is
  unsafe in general, only that adding `currency` to the key made the
  reported test pass.
- Candidate rewrites `priceCache.ts`, `pricingClient.ts`, or
  `lastKnownPriceRepository.ts` "to be safe" instead of fixing the one
  function that's actually wrong.
- Candidate never directly tests `pricingClient.fetchPrice` or reads
  `lastKnownPriceRepository.ts`, and instead assumes the bug is in one of
  those without checking — or worse, "fixes" one of them despite them
  being correct.
