# Design Brief (private — do not expose to candidate)

*(Filename kept as `bug_design.md` for structural consistency with the rest
of the curriculum's evaluator_private layout. This project has no injected
bug — its content is the private design brief for an LLD/implement-from-
requirements exercise.)*

## Full requirements (candidate-facing, restated here for evaluator reference)

**Given, fully implemented:** `FeatureFlag` ABC (`is_enabled(context) ->
bool`) and `FlagRule` ABC (`decide(context) -> bool | None`, where `None`
means "no opinion, defer to the next rule").

**Part 1 — `PercentageRolloutFlag`:** deterministic percentage rollout.
`rollout_percentage` is 0-100. The same `context["user_id"]` must always get
the same result for a given flag, forever — computed fresh each call from a
stable hash of `flag_name` + `user_id`, no randomness, no stored per-user
state. Roughly `rollout_percentage`% of a large population of distinct
`user_id`s should end up enabled (approximate uniformity, statistical not
exact). Different `flag_name`s must be free to diverge for the same
`user_id` (bucketing is per-flag).

**Part 2 — `DenyListRule` / `AllowListRule` / `PercentageRolloutRule`
(`rules.py`) + `RuleChain` (`rule_chain.py`):** `DenyListRule` returns
`False` if the user is in its set, else `None` (never `True`).
`AllowListRule` returns `True` if the user is in its set, else `None`
(never `False`). `PercentageRolloutRule` always decides (never `None`),
reusing Part 1's bucketing rather than duplicating it. `RuleChain` takes an
ordered `list[FlagRule]` and a `default: bool`; evaluates rules in order,
returns the first non-`None` decision, falls back to `default` if every
rule (including zero rules) defers. Deny beats allow beats rollout *only
because that's the order the candidate is told to construct the chain in*
— `RuleChain` itself must not hardcode that priority; it must respect
whatever order it's given.

## Why this is interview-appropriate

Feature flags / gradual rollout systems are a very common real-world
backend building block and a recurring LLD/OOD interview prompt,
particularly at companies running any kind of experimentation or staged-
rollout infrastructure. The two-part structure — implement a first
mechanism, then reveal a second requirement (explicit overrides via a rule
chain) that tests whether the first design anticipated change — mirrors how
these interviews are actually run in practice, the same shape used in
Project 11 but applied to a genuinely different underlying mechanism:
deterministic hashing instead of clock-based token/window state, and a
chain-of-rules-with-deferral instead of a single-dispatch tiered lookup. No
named design pattern (e.g. "Chain of Responsibility" or "Strategy") is
suggested to the candidate anywhere in the README, the SKILL.md, or any
candidate-facing file — the interfaces (`FeatureFlag` with one method,
`FlagRule` with one method that can abstain) make the appropriate shape
discoverable through the requirements themselves, without pre-labeling it.
A candidate who has independently learned this pattern will recognize it; a
candidate who hasn't can still arrive at a correct design by directly
satisfying the stated requirements ("RuleChain must keep working when a new
kind of rule is added, without rewriting the code that chains rules
together").

## Design pitfall #1 (hidden-test-enforced): isinstance-branching in
`RuleChain`

**The temptation:** a candidate implements `RuleChain.is_enabled` as
something like:

```python
def is_enabled(self, context):
    for rule in self._rules:
        if isinstance(rule, DenyListRule):
            result = rule.decide(context)
            if result is not None:
                return result
        elif isinstance(rule, AllowListRule):
            result = rule.decide(context)
            if result is not None:
                return result
        elif isinstance(rule, PercentageRolloutRule):
            return rule.decide(context)
        # else: silently skipped, or raises TypeError
    return self._default
```

This *works* for every public test and most hidden tests, because the
exercise only ever hands `RuleChain` the three concrete rule types it was
written against, in the priority order the README suggests. It violates the
entire point of depending on the `FlagRule` interface: adding a fourth rule
type later (the README's own example — a future "business hours only"
rule) would require going back and modifying `RuleChain` again, which is
exactly the coupling the Part 2 requirement ("without having to rewrite the
code that chains rules together") was written to rule out. A subtler
variant of the same mistake hardcodes deny-before-allow-before-rollout
priority directly in `RuleChain`'s logic (e.g. always checking for a
`DenyListRule` instance first regardless of list order) rather than simply
walking `self._rules` in whatever order the caller constructed it with.

**Exactly which hidden tests catch it:**
`hidden_tests/test_flagengine_hidden.py` defines small custom `FlagRule`
subclasses inline (`AlwaysOnRule`, `AlwaysOffRule`, `BusinessHoursRule`) —
each just a few lines implementing `decide` directly, with zero knowledge
of `DenyListRule`/`AllowListRule`/`PercentageRolloutRule` and vice versa —
and uses them inside `RuleChain` in:

- `test_chain_honors_a_custom_rule_that_is_the_only_rule`
- `test_chain_custom_rule_decision_beats_default_when_placed_after_known_rules`
- `test_chain_falls_through_a_deferring_custom_rule_to_the_next_rule`
- `test_chain_mixes_a_custom_rule_with_built_in_rules_in_the_middle`

plus a fifth test targeting the hardcoded-priority variant specifically:

- `test_rule_chain_respects_whatever_order_it_is_given`

A correct, purely-polymorphic `RuleChain` (i.e. `for rule in self._rules:
result = rule.decide(context); if result is not None: return result` then
`return self._default`) passes all five trivially. An isinstance-branching
implementation fails the first four — either by raising on the
unrecognized custom type, or by silently skipping it and falling through to
`default`/the next known rule, which each test is specifically constructed
so that fallback produces the *wrong* answer rather than accidentally
matching the correct one. A hardcoded-priority implementation fails the
fifth even if it does dispatch every rule polymorphically. This is the
intended, precise signal: the flawed versions are "correct" by every test
that only exercises the three known rule types in their suggested order,
and wrong only on the tests built to catch exactly these shortcuts.

## Design pitfall #2 (rubric/DEBRIEF signal only, not hidden-test-enforced):
`hash()` vs. `hashlib`

**The temptation:** a candidate reaches for Python's built-in `hash()` on
the combined `flag_name`/`user_id` string, since it's shorter to write and
"just works" for the entire duration of a test session:

```python
bucket = hash(f"{flag_name}:{user_id}") % 100
```

This passes every test that runs within a single `pytest` process, because
`hash()` is stable *within* one process run. It silently breaks the single
hardest stated requirement — "the same user_id must always get the same
result, forever," explicitly including across process restarts — because
Python randomizes `str`/`bytes` hashing per-process via `PYTHONHASHSEED`
(enabled by default since Python 3.3, specifically as a hash-flooding DoS
mitigation) unless a fixed seed is set in the environment. In a real
feature-flag service that gets redeployed regularly, this bug would
manifest as users randomly flipping in and out of a rollout on every
deploy — a genuinely nasty, hard-to-diagnose production incident, not a
theoretical concern.

**Why this is documented here rather than hidden-test-enforced:** reliably
proving this in a single pytest run requires spawning a subprocess with a
different `PYTHONHASHSEED` and comparing bucket assignments across the two
processes. That's implementable, but it adds real complexity and a
non-trivial flakiness/portability surface (subprocess spawning, environment
variable propagation, interpreter startup cost) to the hidden test suite
for a pitfall that a careful code read of `percentage_rollout.py` catches
immediately and unambiguously — `hash(` or `hashlib.sha256(` is a one-line,
zero-ambiguity thing to look for. Evaluators should read
`percentage_rollout.py` (and, if it re-derives the bucket independently
instead of reusing it, `rules.py`) directly and flag any use of the
built-in `hash()`, `random`, or `uuid` for bucketing as an automatic fail
on Part 1 correctness, regardless of what the test suite shows, and it's
called out explicitly in `scoring_rubric.md` and as a `DEBRIEF.md`
discussion point.

## Relevant files
- `candidate/flagengine/base.py` — given, correct, not graded directly.
- `candidate/flagengine/percentage_rollout.py`, `rules.py`, `rule_chain.py`
  — the four graded classes.
- `evaluator_private/reference_solution/flagengine/` — full working
  reference implementation of all four classes, including the shared
  `_bucket_for` helper.
- `evaluator_private/hidden_tests/test_flagengine_hidden.py` — hidden tests
  described above.
