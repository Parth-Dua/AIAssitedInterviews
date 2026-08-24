# Bug Design (private — do not expose to candidate)

## Expected behavior
`GET /products/:productId/price?currency=...` looks up the current price of
a product in the requested currency, caching successful lookups briefly to
avoid redundant provider calls. Invariant: "a cached price is only a valid
answer for the exact `(productId, currency)` pair it was fetched for."
Looking up a product's price in one currency must never return a price that
was actually fetched for a different currency of the same product.

## Actual (buggy) behavior
`PriceService.getPrice` (`src/services/priceService.ts`) builds the cache
key via `buildCacheKey(productId, currency)`, which returns `` `price:${productId}` ``
— it accepts a `currency` parameter but never reads it. A request for
`(productId=X, currency=USD)` populates the cache under `price:X`. A
*subsequent* request for `(productId=X, currency=EUR)` looks up the same
key, gets a cache hit, and incorrectly returns the previously-fetched USD
numeric value with `source: 'cache'` — even though a EUR price was never
actually fetched. The external pricing client is never called for that EUR
request at all.

## Root cause
Composite-key construction that omits one of the two dimensions the key
must depend on. `buildCacheKey` is a small, already-isolated, already-wired
helper — the bug is not that key construction is scattered or hard to find;
it's that the one function responsible for it silently drops `currency`
while still accepting it as a parameter (a plausible "forgot to use an
argument" defect, not a missing-function defect). `priceCache.ts` itself is
correct and currency-agnostic by design — it is a dumb string-keyed
get/set/TTL store with no opinion about what a key should encode; the
mistake is entirely in what string `getPrice` asks it to store under.

## Violated invariant
"A cached price is only a valid answer for the exact `(productId, currency)`
pair it was fetched for." (Implied by the general semantics of caching a
value that varies along more than one dimension; directly evidenced by the
customer-facing bug report.)

## Relevant execution path
`GET /products/:productId/price` (`src/routes/prices.ts`) → `getProductPrice`
controller (`src/controllers/priceController.ts`, thin — resolves the
`currency` query param, defaulting to `USD`, and passes both to the service;
maps `PriceUnavailableError` to 503) → `PriceService.getPrice`
(`src/services/priceService.ts`, **the bug**, via `buildCacheKey`) →
`PriceCache.get`/`.set` (`src/cache/priceCache.ts`, correct, given — a plain
TTL-expiring `Map` with an injectable clock; must be read to confirm it has
no currency awareness of its own, so the defect can only be in how the
service constructs the key it hands the cache) → on a cache miss,
`PricingClient.fetchPrice` (`src/clients/pricingClient.ts`, correct, given
— a fake external provider, deterministic per `(productId, currency)`, no
real network/timers) → on a provider failure,
`LastKnownPriceRepository.get` (`src/repositories/lastKnownPriceRepository.ts`,
correct, given — already keyed by `(productId, currency)` internally).

## Evidence available to the candidate
- The README states the customer complaint verbatim: switching currency
  shows the exact same number, which shouldn't be possible.
- The failing public tests (`fetches a live EUR price for a product already
  cached in USD...` at the service layer, and `shows the correct live EUR
  price after a USD price was already cached...` at the HTTP layer)
  reproduce the exact reported scenario: a USD lookup followed by a EUR
  lookup for the same product returns `source: 'cache'` and the identical
  price instead of `source: 'live'` with a different one.
- Reading `priceService.ts::getPrice` end-to-end shows `buildCacheKey`
  accepts `currency` as a parameter but its return value never references
  it.

## Reasonable hypotheses
1. (Plausible, wrong) `pricingClient.fetchPrice` ignores the `currency`
   argument and always returns a USD-equivalent price, so of course the
   "EUR" price looks like the USD one. Ruled out by the public test
   `PricingClient.fetchPrice (direct) — returns different prices for the
   same product in different currencies`: calling `fetchPrice` directly, in
   isolation from the service and cache entirely, with `'USD'` and `'EUR'`
   for the same `productId` returns two different numeric values. The fake
   provider is doing its job correctly.
2. (Plausible, wrong) `lastKnownPriceRepository`'s fallback is incorrectly
   triggering even when the live fetch succeeds, and it isn't
   currency-aware, so it's silently serving a stale USD value. Ruled out by
   reading `lastKnownPriceRepository.ts`'s interface (`get`/`set` both take
   `(productId, currency)` and key on both internally) and by the public
   test `PriceService.getPrice — fetches a product price live on the first
   request`, which shows a first-time lookup returns `source: 'live'` — the
   fallback path is never even entered on the reported scenario, since the
   pricing client isn't failing.
3. (Correct) `buildCacheKey` in `priceService.ts` omits `currency` from the
   key it returns, so any two requests for the same `productId` — regardless
   of `currency` — collide on the same cache entry.

## Intended regression tests
The two already-failing public tests (one at the service layer, one at the
HTTP layer) reproducing the currency-blind cache bug, plus the hidden tests
in `hidden_tests/priceHidden.test.ts`: a direct unit test of `buildCacheKey`
proving it doesn't collide on inputs that would concatenate to the same raw
string without a delimiter; a black-box behavioral variant of the same
check via `getPrice` (robust to a fix that inlines the key construction
instead of keeping `buildCacheKey`); a cross-product sanity check that the
fix doesn't overcorrect into a single global cache entry; a per-currency TTL
expiry check using the cache's injectable clock; and a fallback-path
currency-correctness check.

## Acceptable fixes
- Change `buildCacheKey` to include both dimensions with an unambiguous
  delimiter, e.g. `` `price:${productId}:${currency}` `` (the reference
  solution's approach).
- Equivalent phrasings: a delimiter-safe composite built any other way (an
  array joined with a separator, a small object hashed/serialized safely,
  etc.), as long as two distinct `(productId, currency)` pairs can never
  produce the same key string. `:` is safe here because neither
  `productId` nor `currency` values in this system are expected to contain
  a literal colon — a candidate who reasons about *why* their chosen
  delimiter is safe (not just picks one) is showing the stronger signal.
- The fix does not need to preserve the exact name `buildCacheKey`, but
  since it already exists as a small, already-wired, already-exported
  helper in the starting code, the natural minimal fix is to edit its
  return statement in place rather than delete or inline it — consistent
  with the "keep changes scoped" constraint. (The hidden test suite
  includes both a direct import of `buildCacheKey` *and* a black-box
  behavioral equivalent that doesn't depend on the function's name, so a
  candidate who reasonably inlines the fix instead is still caught/covered
  correctly — see `ai_skill_audit.md`'s portability note is not relevant
  here, but graders should note: if `buildCacheKey` is gone, verify
  collision-safety via the behavioral hidden test's result, not the direct
  one, before concluding a fix is incomplete.)
- The fix must **not** key the cache only on `currency` (which would
  collide across different products) — the existing public test suite's
  cross-product coverage plus the hidden cross-product test both catch
  this if a candidate over-corrects in the wrong direction.

## Tempting but incomplete/wrong fix
Changing `buildCacheKey` to include `currency`, but via naive string
concatenation with no delimiter:

```ts
export function buildCacheKey(productId: string, currency: string): string {
  return `price:${productId}${currency}`;
}
```

This fix genuinely fixes the *reported* bug: `buildCacheKey('X', 'USD')` and
`buildCacheKey('X', 'EUR')` now produce different strings
(`'price:XUSD'` vs `'price:XEUR'`), so the two originally-failing public
tests (and all other public tests) pass. It is still wrong in general,
because concatenation without a delimiter is not injective over the pair —
two *different* `(productId, currency)` pairs can produce the *same*
string whenever one pair's boundary falls in a different place than the
other's. Concretely: `buildCacheKey('P1', '2EUR')` and
`buildCacheKey('P12', 'EUR')` both produce `'price:P12EUR'`. `'2EUR'` is
used here purely as a test string to exercise the key-builder's
collision-safety in isolation — the assertion is about the key-building
function's behavior on two distinct input pairs, not a claim that `'2EUR'`
is a real ISO currency code; this is exactly the kind of narrow,
implementation-level unit test a real engineer would write to prove a
composite-key scheme is collision-safe.

Validated directly: against this delimiter-less fix, all 12 public tests
pass (the currency-blind bug is gone) and 15/17 tests total pass — only the
two hidden collision tests (`buildCacheKey — composite key collision
safety` and its black-box behavioral counterpart,
`getPrice — end-to-end collision safety for concatenation-alike inputs`)
fail, exactly as designed. The other three hidden tests (cross-product
isolation, per-currency TTL expiry, currency-correct fallback) all still
pass under this fix, confirming the two failing tests are a narrow,
well-targeted regression net rather than a broad correctness check that
would fail for unrelated reasons.

See `evaluator_private/reference_solution/priceService.ts` for the
delimiter-safe fix isolated from the delimiter-less one (the only line that
differs between the two is `buildCacheKey`'s return statement).

## Why this is interview-appropriate for an Amazon-style OA
Cache-key construction that silently omits a dimension a value actually
varies along, and composite-key delimiter safety once you *do* include all
the right dimensions, are both extremely common real backend interview and
production topics — multi-dimensional cache keys, idempotency keys, and
partition/shard keys all have the exact same "did you include every
dimension, and can two distinct tuples ever collide once you concatenate
them" failure shape. Tracing `route → controller → service (the bug) →
cache (correct, but must be read to rule it out) → pricing client (correct,
must be tested in isolation to rule out hypothesis 1) → last-known-price
repository (correct, must be read to rule out hypothesis 2)` across five
files to isolate a one-line defect in a function that already looks
suspiciously unused is exactly the "read an unfamiliar multi-layer service,
rule out plausible red herrings by actually reading the code, then fix a
narrow, precisely-explainable defect" shape Amazon-style repo-based
debugging OAs test. The tempting-but-incomplete fix additionally rewards
candidates who think past "the reported bug's test is green now" to "is my
new key construction actually safe in general," rather than stopping at the
first green test run — a common differentiator in OA rubrics for this
format.
