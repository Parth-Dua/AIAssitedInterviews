# Expected Reasoning Path

1. Run `npm test`; observe that `fetches a live EUR price for a product
   already cached in USD, instead of reusing the USD value` fails in
   `tests/priceService.test.ts`, and `shows the correct live EUR price
   after a USD price was already cached for the same product` fails in
   `tests/pricesApi.test.ts`, while everything else passes.
2. Read the failure output: both expect `source: 'live'` and a EUR price
   different from the USD one, but both actually got `source: 'cache'` and
   the identical USD numeric value.
3. Read the README's customer complaint and confirm it matches exactly:
   switching currency shows the same number, which shouldn't be possible
   since USD and EUR prices are never numerically identical in this system.
4. Trace the request path: `routes/prices.ts` → `GET
   /products/:productId/price` wired only to `getProductPrice` in
   `controllers/priceController.ts`. Read the controller — thin, resolves
   `currency` from the query string (defaulting to `USD`) and passes both
   `productId` and `currency` into `PriceService.getPrice`. Not the bug.
5. Open `services/priceService.ts::getPrice`. It checks the cache first,
   calls the pricing client on a miss, and falls back to the last-known
   price on a provider failure — a fairly standard read-through cache
   pattern. Note the cache key comes from `buildCacheKey(productId,
   currency)`.
6. Read `buildCacheKey`. It takes `currency` as a parameter but its return
   value — `` `price:${productId}` `` — never references it. This is the
   root cause: two requests for the same product in different currencies
   collide on the same cache key.
7. Before concluding, rule out the two plausible alternatives a careful
   candidate should consider:
   - Maybe `pricingClient.fetchPrice` itself ignores `currency` and always
     returns a USD-equivalent price. Check by reading
     `clients/pricingClient.ts` and/or running the public test that calls
     `fetchPrice` directly for `'USD'` and `'EUR'` on the same product —
     it returns two different values. Not the client.
   - Maybe `lastKnownPriceRepository`'s fallback is firing even though the
     live fetch succeeds, and it isn't currency-aware. Check by reading
     `repositories/lastKnownPriceRepository.ts` — `get`/`set` are already
     keyed by `(productId, currency)` — and by noting the first-request
     public test already shows `source: 'live'` on a cache/fallback-free
     path. Not the repository.
8. Read `cache/priceCache.ts` to confirm it's a plain string-keyed
   get/set/TTL store with no currency awareness of its own — it stores and
   returns exactly whatever key it's given. This confirms the defect is
   entirely in what key `getPrice` constructs, not in the cache mechanism.
9. Fix `buildCacheKey` to build a key that depends on both `productId` and
   `currency`, with an unambiguous delimiter between them (e.g.
   `` `price:${productId}:${currency}` ``).
10. Re-run tests. The two originally-failing tests should now pass. A
    careful candidate then asks: "is my new key construction actually safe
    for *any* `productId`/`currency` combination, or could two different
    pairs still collide if I concatenated them without a separator?" —
    and either double-checks their delimiter choice is genuinely
    unambiguous, or writes a quick test proving two inputs that would
    concatenate identically without a delimiter still produce different
    keys with one.
11. Explain: `buildCacheKey` accepted `currency` but silently dropped it,
    so the cache could never distinguish two currencies of the same
    product; the fix restores that dimension, and a delimiter is needed
    between the two parts of the key so that concatenation itself can't
    reintroduce a collision between two different pairs.

A strong candidate reaches step 9 within 20-30 minutes given the failing
tests and README as a starting point (this project runs deeper than a
single hardcoded field — it requires ruling out two other files first), and
reaches step 10's delimiter-safety realization within the full 60-75 minute
timebox, ideally without being told to — noticing it themselves is a strong
signal, and matches the specific thing the hidden test suite checks for.
