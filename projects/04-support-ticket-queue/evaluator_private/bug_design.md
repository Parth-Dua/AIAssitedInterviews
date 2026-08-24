# Bug Design (private — do not expose to candidate)

## Expected behavior
Each ticket's `watchers` list is independent. Creating a ticket without
explicit watchers gives it its own fresh list containing (at most) the
auto-watch email. Creating a ticket with explicit watchers gives it a fresh
list containing those watchers plus the auto-watch email. Adding a watcher
to one ticket via `add_watcher` must only ever change that ticket's list.

## Actual (buggy) behavior
`app/services/ticket_service.py::TicketService.create_ticket` is declared as:

```python
def create_ticket(self, subject: str, watchers: list[str] = []) -> Ticket:
    if self._auto_watch_email:
        watchers.append(self._auto_watch_email)
    ticket = Ticket(id=self._next_id, subject=subject, status="open", watchers=watchers)
    ...
```

`app/api/routes/tickets.py` calls `_service.create_ticket(request.subject,
request.watchers)` when the request has explicit watchers, but calls
`_service.create_ticket(request.subject)` — omitting the argument entirely —
whenever the request's `watchers` field is empty/omitted. `TicketService` is
constructed with `auto_watch_email="support-lead@company.example"`, so the
auto-watch branch always fires.

Because every ticket created via the omitted-argument path receives the
*exact same* list object (Python's `[]` default is evaluated once, at
function-definition time, not once per call), and the auto-watch branch
mutates that object in place with `.append(...)`, every such ticket's
`watchers` attribute is actually a reference to one shared list that keeps
growing:

- Ticket N created without explicit watchers gets a watcher list that
  already contains one auto-watch entry per *prior* ticket created the same
  way, plus its own.
- Because it's literally the same object, any later mutation to one such
  ticket's `watchers` (e.g. via `add_watcher`, which does
  `ticket.watchers.append(email)`) is instantly visible on every other
  ticket that shares that object — including ones that appeared to have
  their own independent list at the time they were returned to the caller.

## Root cause
A **mutable default argument** (`watchers: list[str] = []`) combined with
**in-place mutation** of that default (`watchers.append(...)`) inside
`create_ticket`. Python binds the default value once, when the function
object is created (at class-body/module-import time) — not fresh on every
call — so every call that omits `watchers` receives and mutates the same
list object, for the lifetime of the process.

## Violated invariant
"Each ticket's `watchers` list is independent; creating or modifying one
ticket's watcher list must never affect any other ticket's watcher list."

## Relevant execution path
`POST /tickets` (`app/api/routes/tickets.py::create_ticket`) decides whether
to pass `request.watchers` explicitly or omit it →
`TicketService.create_ticket` (`app/services/ticket_service.py`, where the
bug lives) → `Ticket` domain object (`app/domain/ticket.py`, just a
dataclass, holds whatever list reference it's given) →
`TicketRepository.save` (`app/repositories/ticket_repository.py`, stores the
`Ticket` object as-is: `self._tickets[ticket.id] = ticket`, no copy). The
repository is worth reading closely precisely *because* it has no defensive
copy — that's normal, correct behavior for a simple in-memory store, and a
candidate should confirm it isn't itself the bug (it just faithfully stores
and returns whatever object it's handed, which is exactly why the aliasing
bug's effects are directly observable through it). The actual bug is
entirely inside `ticket_service.py::create_ticket`.

## Evidence available to the candidate
- Two failing public tests reproduce both angles of the bug report:
  - `test_adding_watcher_to_one_ticket_does_not_affect_another` — adding a
    watcher to one ticket leaks onto a second, unrelated ticket.
  - `test_successive_tickets_without_watchers_have_stable_watcher_count` —
    each successive ticket created without explicit watchers ends up with a
    growing watcher count instead of a stable count of 1.
- The README states the bug report in the support desk's own words.
- Reading `ticket_service.py::create_ticket` end-to-end reveals the mutable
  default argument and the in-place `.append`.
- Printing `id(ticket_a.watchers)` vs `id(ticket_b.watchers)` for two
  tickets created without explicit watchers shows they're the same object.

## Reasonable hypotheses
1. (Correct) `create_ticket`'s default `watchers` argument is a mutable
   list, evaluated once, and the auto-watch append mutates it in place, so
   every ticket created without explicit watchers shares (and keeps
   growing) the same underlying list.
2. (Plausible, wrong) The repository is returning the same `Ticket` object
   reference on every `get()`/`save()` call, so all tickets end up pointing
   at the same underlying data. Ruled out by reading
   `ticket_repository.py`: it's a plain `dict` keyed by ticket id, storing
   and returning distinct `Ticket` objects per id — `get(1)` and `get(2)`
   return different objects with different `id`/`subject` fields; only
   their `watchers` *list* attribute happens to be the same shared object
   when the ticket was created via the buggy default-argument path. A
   candidate who checks `ticket_a is ticket_b` (false) but doesn't check
   `ticket_a.watchers is ticket_b.watchers` (true) could get stuck here
   briefly before narrowing further.
3. (Plausible, wrong) The `Ticket` dataclass itself has a shared mutable
   default for `watchers`. Ruled out by reading `app/domain/ticket.py`: it
   has no default at all — `watchers` is a required field, always supplied
   explicitly by the caller (`Ticket(..., watchers=watchers)`), so the
   dataclass definition itself isn't where the sharing originates.

## Intended regression tests
The two failing public tests above, plus hidden tests covering: the
service must not mutate a caller-supplied `watchers` list in place; two
tickets created without explicit watchers must get independent list
objects (`is not`); interleaved explicit/default-path creation stays
isolated; the auto-watch email is present regardless of path. See
`hidden_tests/test_ticket_hidden.py`.

## Acceptable fixes
- Change the default to `watchers: list[str] | None = None` and, inside the
  function, build a **new** list when the caller didn't supply one (e.g.
  `watchers = list(watchers) if watchers is not None else []`) *before*
  appending the auto-watch email — this also avoids mutating a
  caller-supplied list. This is the reference solution.
- Equivalent: keep the `None` default, but construct the returned list with
  something like `ticket_watchers = [*(watchers or []), self._auto_watch_email]`
  instead of appending in place.
- Any variant that (a) never reuses the same list object across calls that
  omit `watchers`, and (b) never mutates a list object the caller passed in,
  is acceptable.

## Tempting but incomplete/wrong fix
Changing the signature to `watchers: list[str] | None = None` with
`if watchers is None: watchers = []` inside the function, but leaving
`watchers.append(self._auto_watch_email)` as an in-place append on whatever
`watchers` now refers to. This **does** fix both originally-failing public
tests — the shared-default aliasing is gone, since every omitted-argument
call now gets a brand-new `[]`. But it introduces a subtler bug: when a
caller passes an **explicit** watchers list (e.g. from
`request.watchers`), `watchers` inside the function is no longer a fresh
object — it's the literal object the caller passed in — and appending to it
mutates that caller-owned list as a side effect. If any code elsewhere
holds a reference to that same list (logs it, returns it verbatim, or a
test constructed it and later asserts on it), it will unexpectedly observe
the auto-watch email added to a list it never modified itself.

This is caught by
`hidden_tests/test_ticket_hidden.py::test_create_ticket_does_not_mutate_caller_supplied_watchers_list`,
which constructs a `watchers` list variable, passes it into
`create_ticket`, and then asserts the *original* variable is unchanged.
Verified empirically: this half-fix passes all 8 public tests and 3 of 4
hidden tests, and fails exactly that one hidden test.

## Why this is interview-appropriate
Python's mutable-default-argument gotcha, compounded by in-place mutation
of shared state, is one of the most classic real-world Python interview and
code-review themes — genuinely common in production code, well-documented,
but easy to miss when reading quickly. Diagnosing it requires recognizing a
specific language behavior (not just following a business-logic thread),
tracing object identity across two small files, and — for a strong
candidate — noticing that the *first* fix that comes to mind (the `None`
sentinel) is necessary but not sufficient. No specialist knowledge beyond
core Python semantics is required; fully discoverable from the code, the
two failing tests, and the README.
