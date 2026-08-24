# Expected Reasoning Path

1. Run `pytest -q`; observe two failures:
   `test_adding_watcher_to_one_ticket_does_not_affect_another` and
   `test_successive_tickets_without_watchers_have_stable_watcher_count`,
   while everything else (including the "with explicit watchers" and
   "single ticket without watchers" cases) passes.
2. Read both failure messages closely. The first shows a watcher added to
   ticket 1 appearing on ticket 2's list. The second shows watcher *counts*
   growing across successively created tickets (e.g. 8 entries instead of
   1) — and, on inspection, largely duplicate entries of the same
   auto-watch email.
3. Notice both failing tests create tickets **without** passing an explicit
   `watchers` argument, while the passing tests either create a single
   ticket or always pass watchers explicitly. This narrows attention to
   what happens specifically when `watchers` is omitted.
4. Open `app/api/routes/tickets.py`; see that the route omits the
   `watchers` argument entirely (rather than passing `[]`) when the
   request has no explicit watchers.
5. Open `app/services/ticket_service.py::create_ticket`; notice the
   parameter is declared `watchers: list[str] = []` and that the function
   body does `watchers.append(self._auto_watch_email)` — an in-place
   mutation of whatever `watchers` refers to.
6. Recognize (or look up) that a mutable default argument value in Python
   is created once, at function-definition time, and is the same object on
   every call that doesn't override it — so every call that omits
   `watchers` mutates and shares one persistent list.
7. Confirm by inspection or a quick experiment (e.g. checking
   `id(ticket_a.watchers) == id(ticket_b.watchers)` for two tickets created
   without explicit watchers) that this is exactly what's happening.
8. Rule out the repository as the cause by reading
   `ticket_repository.py` — it stores/returns distinct `Ticket` objects per
   id in a plain dict; only their shared `watchers` list attribute (when
   created via the buggy path) is aliased.
9. Fix `create_ticket` so that (a) it never reuses the same list object
   across calls that omit `watchers`, and (b) it never mutates a
   caller-supplied list in place — e.g. default to `None` and build a new
   list (via `list(watchers)` or `[*watchers]`) before appending the
   auto-watch email.
10. Re-run tests; all pass. A strong candidate goes further and manually
    checks (or adds a test for) the case where an explicit watchers list is
    passed in and the caller still holds a reference to it afterward —
    recognizing that a naive `if watchers is None: watchers = []` fix,
    without copying, still mutates caller-supplied lists.
11. Explain: the shared-default aliasing was compounded by in-place
    mutation; the fix must address both the "shared across omitted-argument
    calls" issue and the "mutates whatever list it's given" issue
    independently — fixing only the first is a common, easy-to-miss partial
    fix.

A strong candidate reaches step 9 within 20-25 minutes given the two
failing tests as a starting point, and independently arrives at (or
recognizes when prompted) the caller-list-mutation subtlety in step 10-11.
