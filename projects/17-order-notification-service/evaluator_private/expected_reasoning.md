# Expected Reasoning Path

1. Run `npm test`; observe that `POST /orders — warehouse unreachable (bug
   report reproduction) › eventually sends a response instead of leaving
   the request hanging` fails in `tests/ordersApi.test.ts`, while every
   other test — including the direct, in-isolation tests of
   `warehouseNotifier.notify()` in `tests/orderController.test.ts` — passes.
2. Read the failure output: it's not a wrong-value assertion, it's a
   promise that never settled within the test's short bounded window — plus
   (visible in the console output) a raw `WarehouseUnavailableError`
   surfacing as an uncaught rejection with a full stack trace through
   Express's layer/route dispatch machinery, bottoming out at
   `orderController.ts` and `warehouseNotifier.ts`.
3. Read the README's support report and confirm it matches: reachable
   warehouses work fine; unreachable ones just hang until the client times
   out.
4. Trace the request path: `routes/orders.ts` wires `POST /orders` through
   `validateOrderCreate` (synchronous, unrelated to timing/notification)
   into `createOrder` in `controllers/orderController.ts`.
5. Consider hypothesis 1: is `errorHandler.ts` registered in the wrong
   place, so it can never fire? Read `app.ts` — `app.use(errorHandler)` is
   correctly the last middleware, after `ordersRouter`. Ruled out.
6. Consider hypothesis 2: does `warehouseNotifier.notify()` itself hang for
   an offline warehouse id? Read `warehouseNotifier.ts` — it's synchronous
   logic returning `Promise.resolve()`/`Promise.reject()` immediately, no
   timers. Confirm with the existing direct unit tests in
   `tests/orderController.test.ts`, which call `notify()` with no Express
   involved and show it rejects promptly. Ruled out.
7. Read `orderController.ts::createOrder` character by character:
   ```ts
   export async function createOrder(req: Request, res: Response) {
     const order = orderService.createOrder(req.body);
     await warehouseNotifier.notify(order);
     res.status(201).json(order);
   }
   ```
   Notice: it's `async`, it's registered directly at the route
   (`router.post('/orders', validateOrderCreate, createOrder)`) with no
   `try/catch` around the `await` and no wrapper at the registration site.
8. Recognize the mechanism: Express 4 does not automatically catch a
   promise rejected by an async route handler. When `notify()` rejects, the
   `await` throws inside `createOrder`, which becomes an unhandled
   rejection of the handler's own returned (and un-awaited-by-Express)
   promise. `res.status(201).json(order)` is never reached, and nothing
   else ever calls `res.send`/`res.json`/`next(err)` for that request — so
   no response goes out at all. This exactly explains why reachable
   warehouses work (the `await` never throws) and unreachable ones hang
   (the `await` throws into the void).
9. Fix it — wrap the body in `try/catch` and call `next(err)` on failure
   (or, equivalently, apply a small `asyncHandler`/`catchAsync` wrapper at
   route registration that does the same thing once, for every route).
10. Re-run tests. The originally-failing test now passes. A careful
    candidate asks: "now that a response is sent, is it the *right*
    response?" — checks what `errorHandler.ts` is supposed to produce for
    this kind of failure (a typed `WarehouseUnavailableError` → `502` with
    a `{ error: { code, message } }` body) and confirms their fix actually
    routes the error through `next(err)` into `errorHandler.ts`, rather
    than constructing an ad-hoc response (e.g. `res.status(500).send(...)`)
    inside the `catch` block that happens to "work" but discards the app's
    established error contract.
11. Explain: the handler never forwarded a rejected promise to Express's
    error-handling machinery, so a downstream failure (the warehouse being
    unreachable) silently swallowed the response entirely; the complete fix
    both stops the hang *and* preserves the app's real error contract
    rather than inventing a new one in the catch block.

A strong candidate reaches step 8 within 15-20 minutes given the failing
test, the isolated notifier tests, and the README as starting points, and
reaches step 10's realization (the error-contract check) within the full
45-60 minute timebox, ideally without being told to — noticing it
themselves is a strong signal.
