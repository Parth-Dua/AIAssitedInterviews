# Bug Design (private — do not expose to candidate)

## Expected behavior
`POST /orders` always results in a response being sent back to the client:
`201` with the created order when the warehouse system is reachable, or a
correctly-shaped error response (per `middleware/errorHandler.ts`'s
contract) when it isn't. Invariant: "every request that reaches the
`createOrder` handler eventually gets a response — success or a well-formed
error — no matter what an awaited dependency does."

## Actual (buggy) behavior
`controllers/orderController.ts::createOrder` is an `async` Express route
handler registered directly (`router.post('/orders', validateOrderCreate,
createOrder)`, no wrapping):

```ts
export async function createOrder(req: Request, res: Response) {
  const order = orderService.createOrder(req.body);
  await warehouseNotifier.notify(order);
  res.status(201).json(order);
}
```

When `warehouseNotifier.notify(order)` rejects (simulating the warehouse
system being unreachable for a specific `warehouseId`), the `await` throws
inside the async function, which turns the function's own returned promise
into a rejected promise — but nothing is holding onto that promise. Express
4 has no special-casing for async route handlers: it calls `createOrder(req,
res)` and moves on: it does not attach a `.catch()` to the returned promise,
so a rejection there never reaches `next(err)` and never reaches
`errorHandler.ts`. `res.status(201).json(order)` is simply never reached,
and no other code path sends a response either. The client's connection is
left open until it times out on its own — exactly the "the request never
completes" behavior in the support report.

## Root cause
Missing rejection-to-`next(err)` forwarding on an async Express 4 route
handler. Express 4 does not automatically catch a rejected promise returned
by an `async` handler and translate it into a call to its error-handling
middleware (this specific behavior changed in Express 5, which is why this
project deliberately pins `"express": "^4.19.2"`). Any `await` inside such a
handler that rejects without an enclosing `try/catch` (or an equivalent
wrapper that attaches `.catch(next)`) produces a silently swallowed
rejection and a request that never gets a response.

## Violated invariant
"Every request that reaches a route handler eventually gets a response."
Implied by basic HTTP semantics and by the support report's framing (the
client "just waits and eventually times out" — i.e., nothing on the server
side ever decided to respond, successfully or with an error).

## Relevant execution path
`POST /orders` (`src/routes/orders.ts`) → `validateOrderCreate`
(`src/middleware/validateOrderCreate.ts`, correct — synchronous, calls
`next(err)` for a malformed body, never touches `warehouseId`/notification
concerns) → `createOrder` controller (`src/controllers/orderController.ts`,
**the bug**) → `OrderService.createOrder` (`src/services/orderService.ts`,
correct, synchronous, cannot itself hang or reject in a way relevant here)
→ `warehouseNotifier.notify` (`src/services/warehouseNotifier.ts`, correct
— a fake external-HTTP-client stand-in that resolves or rejects on the next
microtask, no timers, no real I/O). The candidate must also read `app.ts` to
confirm `errorHandler` is correctly registered last, and read
`errorHandler.ts` itself to understand the error contract it defines — both
needed to rule out hypothesis 1 below and to recognize the tempting-fix trap.

## Evidence available to the candidate
- The failing public test in `tests/ordersApi.test.ts` (`eventually sends a
  response instead of leaving the request hanging`) races the request
  against a short timer and shows no response arrives — reproducing the
  support report concretely and fast, without a real hang in CI.
- `tests/orderController.test.ts` shows `warehouseNotifier.notify()`
  resolves/rejects promptly when called directly, in isolation from
  Express — evidence ruling out "the notifier itself hangs."
- The README states the support report verbatim: reachable-warehouse orders
  work fine; unreachable-warehouse orders never complete.
- Reading `orderController.ts::createOrder` end-to-end shows a bare `await`
  with no `try/catch` and no wrapping at the route-registration site.

## Reasonable hypotheses
1. (Plausible, wrong) The error-handling middleware is registered in the
   wrong place (e.g., before the routes), so it can never catch anything —
   ruled out by reading `app.ts`, which shows `app.use(errorHandler)` is
   correctly the very last `app.use()` call, after `ordersRouter`.
2. (Plausible, wrong) `warehouseNotifier.notify()` itself never
   resolves/rejects — hangs internally — for an offline warehouse id. Ruled
   out by a direct unit test of `notify()` in isolation (no Express, no
   HTTP) in `tests/orderController.test.ts`, which shows it rejects
   promptly with a `WarehouseUnavailableError`.
3. (Correct) `createOrder` doesn't catch or forward the rejection from
   `warehouseNotifier.notify()`. Because it's an `async` handler registered
   directly (no `try/catch`, no wrapper), the rejection becomes an
   unhandled promise rejection from Express's point of view — it never
   reaches `errorHandler.ts`, so no response is ever sent for that request.

## Intended regression tests
The one already-failing public test (`tests/ordersApi.test.ts`, HTTP-level,
bounded race) plus the hidden tests in
`hidden_tests/orderHidden.test.ts`: the error-contract test (catches the
tempting bypass fix), the second-offline-warehouse-id generalization test,
and the sequential-request test (a failed order doesn't leave the service
unable to handle the next one).

## Acceptable fixes
- Wrap the handler body in `try/catch` and forward to `next(err)`:
  ```ts
  export async function createOrder(req: Request, res: Response, next: NextFunction) {
    try {
      const order = orderService.createOrder(req.body);
      await warehouseNotifier.notify(order);
      res.status(201).json(order);
    } catch (err) {
      next(err);
    }
  }
  ```
  See `reference_solution/orderController.ts`.
- Equivalent phrasing: an `asyncHandler`/`catchAsync` wrapper utility
  applied once at route registration —
  `router.post('/orders', validateOrderCreate, asyncHandler(createOrder))`
  where `asyncHandler(fn) = (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next)` — leaving `createOrder`'s
  body exactly as originally written. Both are correct and idiomatic;
  neither is preferred over the other for grading purposes. A candidate who
  applies the wrapper approach to only the `/orders` route (rather than
  building it generically) has still fixed the reported bug correctly, even
  though a generic wrapper is the better long-term practice (see
  `DEBRIEF.md`, question 5).
- The fix must route the error through `errorHandler.ts` — i.e., the
  response for an unreachable warehouse must be whatever
  `errorHandler.ts` produces for a `WarehouseUnavailableError` (in the
  given code: `502` with `{ error: { code: 'WAREHOUSE_UNAVAILABLE',
  message: string } }`) — not an ad-hoc response constructed elsewhere.

## Tempting but incomplete/wrong fix
Wrapping the handler in `try/catch` but responding **directly** instead of
calling `next(err)`:
```ts
export async function createOrder(req: Request, res: Response) {
  try {
    const order = orderService.createOrder(req.body);
    await warehouseNotifier.notify(order);
    res.status(201).json(order);
  } catch (err) {
    res.status(500).send('failed');
  }
}
```
This "fixes" the hang — a response is now sent for every request — so it
passes the originally-failing public test. But it bypasses
`errorHandler.ts` entirely: it hardcodes a generic `500` instead of the more
appropriate `502`/`503` ("upstream dependency unavailable") the app's real
error contract would produce, and sends a plain-text body instead of the
established `{ error: { code, message } }` JSON shape every other error
response in this app uses. It also loses the distinction between "the
warehouse is unreachable" and "something else went wrong internally" — both
land on the same generic message. `hidden_tests/orderHidden.test.ts`'s
"responds with the app's real error contract, not an ad-hoc bypass
response" test catches exactly this: it asserts `502` and the
`WAREHOUSE_UNAVAILABLE` JSON shape, which fails against the bypass (gets
`500` and a plain-text body) and passes against a fix that forwards to
`next(err)` by any mechanism. Verified directly: under the bypass fix, all
8 originally-present tests pass but all 3 hidden tests fail on exactly this
mismatch (`Expected: 502, Received: 500`).

## Why this is interview-appropriate for an Amazon-style OA
"An async Express route handler doesn't forward a rejected promise to
`next(err)`, so a downstream failure leaves the client hanging" is one of
the single most common real-world Express interview/code-review findings —
it's the textbook reason `asyncHandler` wrapper utilities and (later)
Express 5's native promise-catching exist at all. The multi-file reasoning
chain here (route → validation middleware → controller → service →
notifier → app-level middleware registration → error handler) forces a
candidate to actually trace where a request's control flow can silently
drop, rather than guessing. The tempting bypass fix additionally rewards
candidates who think about *what the fix should actually look like* — not
just "does a response go out now" — which is exactly the differentiator
real Express code review looks for in this class of bug.
