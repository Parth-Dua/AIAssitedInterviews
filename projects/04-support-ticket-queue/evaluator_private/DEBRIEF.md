# Interview Follow-Up Questions (private)

1. **What was the root cause?**
   Strong answer: `create_ticket`'s `watchers` parameter had a mutable
   default argument (`= []`), which Python evaluates once at
   function-definition time rather than fresh on every call. Because the
   function also mutated that default in place (`.append(...)`), every
   ticket created without an explicit `watchers` argument ended up sharing
   — and progressively growing — the exact same list object.

2. **How did you narrow it down?**
   Strong answer: ran the failing tests first, noticed both only involved
   tickets created *without* explicit watchers, then read `create_ticket`
   looking specifically at the `watchers` parameter and what happens to it
   when omitted vs. supplied. Ideally confirmed the shared-object theory
   directly (e.g. `id()` comparison or `is`) rather than just guessing.

3. **Why does Python behave this way with default arguments, and what's
   the general rule for avoiding this class of bug?**
   Strong answer: default argument values are evaluated exactly once, when
   the `def` statement executes, and the resulting object is reused on
   every call where that argument is omitted. For immutable defaults
   (numbers, strings, `None`, tuples of immutables) this is harmless since
   they can't be mutated. For mutable defaults (lists, dicts, sets) it's
   dangerous specifically when the function body mutates the parameter in
   place. General rule: never use a mutable object as a default argument
   value; use `None` as a sentinel and construct a fresh mutable object
   inside the function body when the argument wasn't supplied — and even
   then, don't mutate whatever object *was* supplied by the caller unless
   that's an explicitly documented and intended side effect.

4. **Why does your fix solve it, and could it break anything else?**
   Strong answer: it ensures every call path — whether `watchers` is
   omitted or supplied — produces a brand-new list for that ticket, so no
   two tickets ever share a watcher-list object, and the caller's own list
   (if they passed one) is never mutated. Should note they checked the
   "explicit watchers passed" case still includes both the explicit
   watchers and the auto-watch email, and that a caller's own list
   variable is unaffected after the call.

5. **What tests would you add, and why?**
   Strong answer: an object-identity check (`is not`) between two tickets'
   watcher lists created without explicit watchers; a test asserting the
   service doesn't mutate a caller-supplied watchers list; an interleaved
   create/watch scenario mixing explicit and default paths; confirming the
   auto-watch email is present on every path.

6. **How would you make `Ticket`'s watcher-list handling robust against
   this class of mistake even if someone adds a similar bug elsewhere
   later?** (design-forward)
   Strong answer (several acceptable angles): centralize "watcher list
   construction" in one small helper/factory so there's only one place
   that can get the defaulting logic wrong; consider making `Ticket`
   itself defensively copy or normalize the list it's given in
   `__post_init__`; add a lint rule or code-review checklist item flagging
   mutable default arguments (many linters, e.g. `flake8-bugbear`'s `B006`,
   catch this automatically); write the identity/mutation-safety tests
   described above as a standing regression suite rather than one-off
   checks, so any future function with the same shape gets caught quickly.
