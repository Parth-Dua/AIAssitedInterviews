# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: `createOrder` is an `async` Express route handler
   registered directly on the router with no `try/catch` and no wrapper.
   When `warehouseNotifier.notify(order)` rejects (simulating an
   unreachable warehouse), the `await` throws inside the handler, which
   just turns the handler's own returned promise into a rejected promise
   that nothing is listening to. Express never learns the request failed,
   so `next(err)` is never called, `errorHandler.ts` never runs, and no
   response is ever sent for that request.

2. **Why doesn't Express 4 automatically catch a rejected promise from an
   async route handler?**
   Strong answer: Express 4's router just calls the handler function
   (`fn(req, res, next)`) and does not do anything with its return value —
   it has no idea the function is `async` or that it returned a promise at
   all, so it never attaches a `.catch()` to forward a rejection into
   `next(err)`. This is a known, common gap that's specifically why
   wrapper utilities like `asyncHandler`/`catchAsync` exist for Express 4
   apps, and it's exactly the gap Express 5 closes (Express 5 route
   handlers that return a rejected promise are automatically forwarded to
   `next(err)`).

3. **What are the two common idiomatic fixes and their tradeoffs?**
   Strong answer:
   - `try/catch` inside each handler, calling `next(err)` in the `catch` —
     explicit and easy to read locally, but has to be repeated in every
     async handler in the app; easy to forget on a new route later.
   - A small `asyncHandler`/`catchAsync` wrapper applied once at route
     registration (`router.post('/orders', validateOrderCreate,
     asyncHandler(createOrder))`) that does
     `Promise.resolve(fn(...)).catch(next)` — write it once, apply it
     everywhere, much harder to forget; slightly less locally-obvious to a
     reader unfamiliar with the pattern, and requires every route in the
     app to consistently use it.
   Both are correct for this exercise; a candidate who names the tradeoff
   between "explicit but repeated" and "centralized but easy to
   forget-to-apply-somewhere" shows strong judgment either way.

4. **You mentioned the fix alone isn't quite complete — what else did you
   check?**
   Strong answer: once the rejection is caught, it matters *how* it's
   turned into a response. A tempting shortcut is to respond directly in
   the `catch` block (e.g. `res.status(500).send('failed')`) — that stops
   the hang, but bypasses the app's real error contract defined once in
   `errorHandler.ts` (a `502` with `{ error: { code:
   'WAREHOUSE_UNAVAILABLE', message } }` for this specific failure, not a
   generic `500` with plain text). They forwarded the error via `next(err)`
   instead, so `errorHandler.ts` — the single place that decides error
   response shape — is what actually produces the response, and added a
   test asserting the specific status/body. A candidate who didn't think of
   this on their own but arrives at it when asked directly still shows
   reasonable signal; a candidate who found it unprompted is a stronger
   signal.

5. **How would you prevent this class of bug from recurring across every
   route in a larger app?**
   Strong answer: centralize the fix rather than relying on every route
   author remembering a `try/catch` — e.g., a shared `asyncHandler` wrapper
   applied at every route registration (or built into a router-wrapping
   helper so it can't be skipped), a lint rule flagging `async` route
   handlers that aren't wrapped, or migrating to Express 5 (which forwards
   async rejections to `next(err)` automatically, making this whole class
   of bug structurally impossible rather than just easy to avoid). Bonus
   signal: mentioning that whichever approach is chosen, it should be
   applied uniformly — a codebase with some routes wrapped and some not is
   itself a source of exactly this bug reappearing later.

6. **Why does the fix need to distinguish `WarehouseUnavailableError` from
   any other unexpected error, instead of just returning a generic 500 for
   everything caught?**
   Strong answer: the two failures mean different things to a client. A
   `WarehouseUnavailableError` means "the order itself is fine, but a
   downstream system is temporarily unreachable" — a `502`/`503`-style
   response signals that clearly and is potentially retryable. A generic,
   unexpected internal error is a different situation and should surface
   as a `500` with a generic message, not be conflated with a known,
   specific upstream-dependency failure. Collapsing both into the same
   status/body loses information a real client (or on-call engineer
   reading logs) would want.
