# Expected Design Reasoning — Project 12

*(Describes what a good class design looks like and why, for an LLD project
built from a requirements doc rather than a root-cause debugging path.)*

## What each class should own

- **`PercentageRolloutFlag`** owns exactly two immutable values: `flag_name`
  and `rollout_percentage`. It owns *no* per-user state at all — the whole
  point of deterministic hashing is that nothing needs to be remembered
  between calls. A clean implementation derives the bucket fresh every call
  from `flag_name` and `context["user_id"]`.

- **`DenyListRule` / `AllowListRule`** each own exactly one thing: a set of
  user IDs. Neither needs to know about rollout percentages, hashing, or any
  other rule. `DenyListRule` must never return `True`; `AllowListRule` must
  never return `False` — each is a one-sided opinion, and "not my user"
  always means defer (`None`), not "the opposite answer."

- **`PercentageRolloutRule`** owns no independent logic — it should compose
  (or otherwise directly reuse) `PercentageRolloutFlag`'s bucketing, because
  a `FlagRule` that decides based on rollout percentage and a `FeatureFlag`
  that decides based on rollout percentage are the same decision wearing two
  different interfaces. Re-deriving the hash math a second time here is a
  duplication smell, not just a style nit — two independently-written
  bucketing implementations could silently drift (e.g. one dev fixes an
  off-by-one in the flag class and forgets the rule class exists).

- **`RuleChain`** owns no rollout/allow/deny logic of its own at all — it
  owns exactly two things: an ordered `list[FlagRule]` and a `default: bool`.
  Its only job is: walk the list, in the order given, call `.decide(context)`
  on each, return the first answer that isn't `None`, and fall back to
  `default` if it runs out of rules. This is the crux of the exercise: the
  moment `RuleChain` needs to know anything about *how* a specific rule
  decides, or needs to know the rule's concrete type at all, a responsibility
  that belongs entirely inside each rule has leaked into the chain.

## Why `FlagRule.decide` returns `bool | None` instead of plain `bool`

A single rule frequently has *no opinion* about a given context — a
deny-list rule has nothing useful to say about a user who isn't on its list;
a "business hours only" rule (the kind of future rule the README gestures
at) has nothing to say once you're inside business hours if its job is only
to gate the *outside*-hours case. If `decide` could only return `True` or
`False`, every rule would be forced to fabricate an opinion it doesn't
actually hold, which destroys the ability to chain rules by priority at all
— you'd need some other out-of-band signal (an extra return value, an
exception, a special sentinel *value* rather than the type system helping
express "no opinion" directly) to represent "this rule doesn't apply here."
`None` as the third state is the natural, minimal way to express "abstain"
in a `bool`-shaped world, and it's exactly what lets `RuleChain` be as
simple as "first non-`None` wins."

## Why `hashlib` (not the built-in `hash()`) for bucketing

Python's built-in `hash()` on strings is deliberately randomized per
process, seeded by `PYTHONHASHSEED`, specifically to prevent
hash-flooding denial-of-service attacks against dict-based data structures.
That's a good property for `dict`/`set` internals and a fatal one for this
use case: it means `hash("checkout-v2:user-42")` can (and typically will)
return a *different* value every time the process restarts. A feature flag
that silently reassigns users to different buckets on every deploy violates
the single hardest requirement in the spec — "the same `context["user_id"]`
must always get the same result, forever" — even though it would look
perfectly stable within a single pytest run or a single long-lived process,
which is exactly what makes it a realistic, easy-to-miss trap rather than an
obviously broken idea. `hashlib.sha256` (or any other standard cryptographic
or well-specified non-cryptographic hash with no process-level seed) doesn't
have this problem: the same input string always produces the same digest,
on any machine, in any process, forever.

## Why `RuleChain` should only depend on the abstract `FlagRule` interface

The Part 2 requirement is explicit: "the platform team wants to keep adding
new kinds of rules over time ... without having to rewrite the code that
chains rules together." This is a direct, practical restatement of
depending on an abstraction rather than a concretion — the same shape as
Project 11's `TieredRateLimiter` requirement, applied to a chain-of-rules
instead of a single dispatch. A candidate does not need to know the name of
any formal software design pattern to arrive at the right shape here — they
only need to take the requirement at face value: `RuleChain` receives
objects typed as `FlagRule` and should therefore only ever call `FlagRule`'s
one method on them. The moment a candidate writes
`isinstance(rule, DenyListRule)` inside `RuleChain`, they've silently added
a hidden coupling: `RuleChain` can now only be used with a fixed, closed set
of rule classes it recognizes by name, which is precisely the situation the
requirement was written to rule out (a platform team that wants to add a
"business hours only" rule, or any other future rule, later without
touching existing code).

## Expected implementation path

1. Read `base.py` — two one-method ABCs: `FeatureFlag.is_enabled` and
   `FlagRule.decide` (the latter returning `bool | None`).
2. Implement `PercentageRolloutFlag`: derive a stable 0-99 bucket from
   `hashlib.sha256(f"{flag_name}:{user_id}")`, compare against
   `rollout_percentage`.
3. Run `pytest -q tests/test_percentage_rollout.py`, get it green, including
   the statistical-uniformity and per-flag-divergence tests.
4. Read the Part 2 section. Implement `DenyListRule` and `AllowListRule` as
   simple set-membership checks that defer (`None`) on a miss.
5. Implement `PercentageRolloutRule` by composing a `PercentageRolloutFlag`
   internally (or extracting the bucketing helper both can call) — not by
   re-deriving the hash math.
6. Implement `RuleChain` as a pure walk-the-list dispatcher: iterate
   `self._rules` in order, call `.decide(context)`, return the first
   non-`None` result, fall back to `default`. No type inspection of any
   rule.
7. Run `pytest -q tests/test_rules_and_chain.py`, get it green.
8. Reflect (unprompted, or when asked in the debrief): Part 1's
   `PercentageRolloutFlag` required no behavioral changes to support Part 2
   — at most, extracting its bucketing math into a small shared helper so
   `PercentageRolloutRule` could reuse it — because `RuleChain` only ever
   calls the interface it was written against.

A strong candidate reaches a fully passing, polymorphic implementation of
all four classes within 45-60 minutes, with 15-30 minutes left to add tests
and articulate the design reasoning above.
