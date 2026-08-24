# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: the shipping-threshold comparison used the post-discount
   subtotal instead of the pre-discount subtotal, coupling two rules that
   should be independent.

2. **How did you narrow it down?**
   Strong answer: ran the failing test first, read the assertion values
   (subtotal/discount correct, shipping wrong), then read the service
   function looking specifically at what feeds the shipping decision.

3. **Why does your fix solve it, and could it break anything else?**
   Strong answer: it restores the invariant "shipping depends only on
   pre-discount subtotal" without touching discount computation; `total`
   still nets out the discount, so totals are unaffected for orders that
   don't cross the threshold. Should note they checked the "always charged
   below threshold" case still works.

4. **What tests would you add, and why?**
   Strong answer: boundary tests at exactly the threshold and one cent below
   it; a case with a large discount confirming discount amount doesn't
   change based on shipping outcome; a case with no discount code and one
   with an invalid discount code.

5. **Is there another valid way to implement this fix?**
   Strong answer: yes — e.g. compute the shipping decision before computing
   the discount at all, or name a dedicated variable for the pre-discount
   subtotal used only for the shipping check. Any implementation preserving
   "shipping depends only on pre-discount subtotal" is acceptable.

6. **If we later wanted free shipping to depend on some discount codes but
   not others, how would you extend this design?**
   Strong answer (design-forward-thinking): don't hardcode the rule in
   `price_order`; consider a small per-code flag/config (e.g., discount
   config carries an `affects_shipping: bool`) surfaced by the repository,
   so `PricingService` stays a thin orchestrator rather than special-casing
   codes by name.
