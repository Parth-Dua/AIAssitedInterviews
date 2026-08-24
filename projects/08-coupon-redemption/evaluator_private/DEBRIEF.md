# Interview Follow-Up Questions (private)

1. **What was the root cause of the reported bug?**
   Strong answer: `redeem()` mutated `coupon.status` to `"exhausted"`
   *after* it had already called `self._repository.save(coupon)`.
   Because `save()` makes a defensive copy of the object it's given, that
   final mutation only ever touched a local object no longer connected to
   what's actually stored — so the persisted coupon's status silently
   stayed `"active"` forever, even once `redemption_count` had reached or
   passed the limit.

2. **Why did the bug only show up on a fresh read (a separate `GET`) and
   not in the redeem call's own response?**
   Strong answer: the object `redeem()` returns to its caller is the same
   local `Coupon` instance that gets mutated after the `save()` call — so
   from the caller's point of view, that one response correctly shows
   `status="exhausted"`. The mutation is real, it's just applied to an
   object nobody re-reads from storage afterward. Only a subsequent,
   independent fetch (a new `GET /coupons/{code}` or `get_by_code()` call)
   goes back to the repository's actual stored copy and reveals that the
   mutation never landed there. This is exactly why testing a mutation by
   inspecting only the mutating call's own return value is insufficient —
   you have to verify persisted state independently.

3. **What does the repository's defensive-copy behavior protect against,
   and why is respecting that convention the service's responsibility
   rather than something to remove?**
   Strong answer: it protects the repository's stored state from being
   silently changed by code outside the repository that happens to be
   holding a reference to a `Coupon` object — without the defensive copy,
   any caller who kept mutating an object after calling `save()` (or after
   calling `get_by_code()`) would be directly corrupting what's "in the
   database" without ever calling `save()` again, which is exactly the
   kind of action-at-a-distance bug repositories are meant to prevent.
   That means callers (the service layer) must treat every `Coupon`
   object as a disposable snapshot the instant it's handed to `save()` —
   any further change requires composing a new mutation and calling
   `save()` again. Removing the defensive copy to "fix" this bug would
   silence this one symptom while reopening the exact class of problem
   the copy exists to prevent.

4. **Your first fix attempt could have been to implement `fixed_amount` as
   a plain subtraction. Why is that wrong, and how did you catch it (or
   would you catch it) if you'd gone down that path?**
   Strong answer: it produces a negative total whenever the fixed
   discount exceeds the order subtotal — which the feature request
   explicitly calls out ("we don't want a negative total") but which
   every "obvious" manual test case (a modest discount against a normal
   order) never exercises. Catching it means actually testing the
   boundary condition the request describes, not just the typical case —
   either by writing a test for "discount larger than subtotal" or by
   re-reading the request's own wording carefully enough to notice it
   names the edge case directly.

5. **How did you verify the redemption-limit fix was correct at the exact
   boundary (not off by one in either direction)?**
   Strong answer: explicitly checked that the `(max_redemptions - 1)`-th
   redemption still leaves the coupon `active`, the `max_redemptions`-th
   redemption is the one that flips it to `exhausted`, and the
   `(max_redemptions + 1)`-th redemption is rejected — rather than just
   confirming "eventually it stops working," which could hide a fix that
   exhausts one redemption too early or too late.

6. **How would you extend this to a third discount type, e.g.
   buy-one-get-one?**
   Strong answer (design-forward-thinking): the current
   `apply_discount` dispatches on a string `discount_type` with an
   `if`/`elif` chain, which will keep growing awkwardly as more types are
   added. A cleaner extension point would be a small strategy registry —
   a mapping from `discount_type` to a pricing function/class, each
   independently testable — so adding "buy-one-get-one" (which needs unit
   quantities/line items, not just a subtotal in cents) is a matter of
   defining a new strategy and registering it, rather than growing a
   single method's branching logic and widening its signature for every
   future discount shape.
