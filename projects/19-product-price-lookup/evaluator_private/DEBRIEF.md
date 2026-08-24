# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: `PriceService`'s cache key, built by `buildCacheKey`,
   only ever encoded `productId` — the `currency` parameter it accepted
   was never used in the returned string. So a lookup for `(X, USD)` and a
   later lookup for `(X, EUR)` hit the exact same cache entry, and the
   second request silently got back the first request's USD price with
   `source: 'cache'`, without ever calling the pricing provider.

2. **How did you narrow it down, and what did you rule out?**
   Strong answer: ran the failing tests first (one unit-level against
   `PriceService`, one HTTP-level via supertest), confirmed both showed the
   same pattern (`source: 'cache'` and an identical price where `'live'`
   and a different price were expected), then traced the request from the
   route through the controller into the service. Before concluding the
   cache key was the problem, checked two other plausible explanations:
   whether `pricingClient.fetchPrice` itself might be ignoring currency
   (ruled out by calling it directly for two currencies and getting two
   different values), and whether the fallback repository might be
   misfiring and returning a stale value (ruled out by reading its
   interface — already keyed by `(productId, currency)` — and noting the
   bug reproduces even on a request that never touches the fallback path
   at all, since the pricing client isn't failing).

3. **Why does your fix solve it, and could it break anything else?**
   Strong answer: it makes the cache key depend on both `productId` and
   `currency`, so two different currencies of the same product can no
   longer collide. It doesn't touch `priceCache.ts` (the store itself,
   which is correctly currency-agnostic — it just stores whatever key it's
   given), `pricingClient.ts`, or `lastKnownPriceRepository.ts`, so the
   TTL mechanism, the fake provider, and the fallback logic are all
   unaffected. They should mention checking that same-currency repeated
   requests still hit the cache (not accidentally always going live now),
   and that two *different* products in the same currency still get
   independent cache entries.

4. **You mentioned including `currency` in the key — how exactly did you
   combine it with `productId`, and why does that matter?**
   Strong answer: used a delimiter between the two parts (e.g.
   `` `price:${productId}:${currency}` ``) rather than plain concatenation,
   because concatenation without a delimiter isn't guaranteed to produce a
   unique string per `(productId, currency)` pair — two different pairs
   can concatenate to the same string if one pair's component boundary
   lands somewhere the other pair's doesn't (e.g. `productId="P1"` +
   `currency="2EUR"` and `productId="P12"` + `currency="EUR"` both
   concatenate to `"P12EUR"`). A candidate who picked a delimiter without
   being able to articulate *why* it's safe (e.g. "colons can't appear in
   a product id or currency code in this system") is a weaker signal than
   one who reasoned about it explicitly or wrote a test proving it.

5. **What other dimensions might a cache key need to include that aren't
   obvious from a quick read?**
   Strong answer: anything the cached value actually varies by that isn't
   captured elsewhere in how the cache is partitioned — e.g. a region or
   marketplace if prices differ by locale, a customer tier if pricing is
   segmented, a point-in-time version if prices can be scheduled for the
   future, or even the requesting client's API version if the response
   shape itself changes. The general lesson: a cache key must depend on
   every input that can change the correct output, not just the ones that
   happen to be the first parameter in the function signature.

6. **How would you extend this if the pricing client itself needed retries
   with backoff?**
   Strong answer: retries belong around the `pricingClient.fetchPrice`
   call inside the `try` block, not inside the cache or fallback logic —
   e.g. a small retry loop with exponential backoff and a cap, still
   falling through to `lastKnownPriceRepository` only after retries are
   exhausted. They should note that retries change the *latency* of a
   live/cache-miss request but shouldn't change the cache key or the
   fallback semantics, and that a naive retry-forever loop would risk
   blocking the request indefinitely if the provider is down — there
   should still be a bounded number of attempts before falling back.
