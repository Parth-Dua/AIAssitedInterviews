# Feature Flag Rule Engine (Interview Exercise)

**Format:** Low-Level Design + Implementation
**Timebox:** 60–90 minutes
**Level:** Backend / SWE — Difficulty 8/10

## Scenario

You're building a feature-flag evaluation library for a backend platform
team. Product and eng teams need to roll new behavior out gradually to a
percentage of users, and later layer explicit per-user overrides on top —
all evaluated the same way everywhere the flag is checked.

Two interfaces you're building against are already given to you, fully
implemented, in `flagengine/base.py`:

```python
class FeatureFlag(ABC):
    @abstractmethod
    def is_enabled(self, context: dict) -> bool:
        """Return whether the flag is on for this context (e.g.
        context["user_id"])."""

class FlagRule(ABC):
    @abstractmethod
    def decide(self, context: dict) -> bool | None:
        """Return True or False if this rule has a definitive opinion for
        this context, or None if this rule doesn't apply here and
        evaluation should defer to the next rule."""
```

Everything you write should work in terms of these interfaces.

## Part 1 — Percentage Rollout

Implement `PercentageRolloutFlag` in `flagengine/percentage_rollout.py`. The
class shape is already stubbed out:

```python
class PercentageRolloutFlag(FeatureFlag):
    def __init__(self, flag_name: str, rollout_percentage: float):
        ...

    def is_enabled(self, context: dict) -> bool:
        ...
```

Requirements:

- `rollout_percentage` is a value from 0 to 100.
- The same `context["user_id"]` must **always** get the same enabled/disabled
  result for a given flag, on every call, forever. This must be true even
  across separate process runs — it needs to be computed fresh each time
  from a stable hash of `flag_name` and `user_id`, not from any randomness
  or stored per-user state.
- Roughly `rollout_percentage`% of a large population of distinct
  `user_id`s should end up enabled. This is a statistical property, not an
  exact one — don't expect precisely `rollout_percentage`% on a small
  sample.
- Different `flag_name`s must be free to produce different results for the
  same `user_id` — the bucketing is per-flag, not just per-user (otherwise
  every flag in the system would turn on for the exact same subset of
  users).

Run `pytest -q tests/test_percentage_rollout.py` until it's green before
moving on to Part 2.

## Part 2 — Follow-up

**Read this section only after Part 1 is implemented and its tests pass.**
In a real interview, requirements often get extended after your initial
design is in place — this section is exactly that.

> We want to layer explicit per-user overrides on top of percentage
> rollout: certain users should always be OFF (e.g. accounts under
> investigation) regardless of rollout percentage, and certain users should
> always be ON (e.g. internal QA accounts) regardless of rollout
> percentage. Deny beats allow beats rollout, in that priority order. And
> the platform team wants to keep adding new kinds of rules over time (e.g.
> a future "business hours only" rule) without having to rewrite the code
> that chains rules together.

Implement three more classes, already stubbed out for you:

### `DenyListRule`, `AllowListRule`, `PercentageRolloutRule` (`flagengine/rules.py`)

```python
class DenyListRule(FlagRule):
    def __init__(self, user_ids: set[str]):
        ...
    def decide(self, context: dict) -> bool | None:
        ...

class AllowListRule(FlagRule):
    def __init__(self, user_ids: set[str]):
        ...
    def decide(self, context: dict) -> bool | None:
        ...

class PercentageRolloutRule(FlagRule):
    def __init__(self, flag_name: str, rollout_percentage: float):
        ...
    def decide(self, context: dict) -> bool | None:
        ...
```

`DenyListRule` returns `False` if `context["user_id"]` is in its set, else
`None` (it defers — it never has an opinion that isn't "deny"). `AllowListRule`
is the mirror image: `True` if the user is in its set, else `None` — it
never returns `False`. `PercentageRolloutRule` always has an opinion (it
never returns `None`), and for a given `flag_name`/`rollout_percentage`
must agree with `PercentageRolloutFlag` on the same `user_id` — the two
are evaluating the same rollout, just through different interfaces.

### `RuleChain` (`flagengine/rule_chain.py`)

```python
class RuleChain(FeatureFlag):
    def __init__(self, rules: list[FlagRule], default: bool):
        ...
    def is_enabled(self, context: dict) -> bool:
        ...
```

Evaluates `rules` in order, asking each one to `decide(context)`, and
returns the first non-`None` answer it gets. If every rule in the list
defers (returns `None` for every rule, including the empty-list case),
returns `default`.

Run `pytest -q tests/test_rules_and_chain.py` until it's green.

When you're done, be ready to explain your `RuleChain` design: whether
finishing Part 2 required changing anything in `percentage_rollout.py`,
and how you'd expect it to behave if the platform team added a new kind of
rule later.

## Repository layout

```
flagengine/
  base.py                 FeatureFlag / FlagRule interfaces (given, do not modify)
  percentage_rollout.py    PercentageRolloutFlag — Part 1, implement this
  rules.py                 DenyListRule / AllowListRule / PercentageRolloutRule — Part 2, implement this
  rule_chain.py             RuleChain — Part 2, implement this
api/
  main.py                  Optional thin FastAPI wrapper — not required reading,
                            contains no graded logic
tests/
  test_percentage_rollout.py     Part 1 public tests
  test_rules_and_chain.py        Part 2 public tests
```

## Setup

```bash
pip install -e ".[dev]"
```

The `flagengine` package itself has **zero dependencies** — everything you
need to implement is plain Python (only `hashlib`, from the standard
library, plus whatever data structures you choose). (The optional `api`
extra pulls in FastAPI/Pydantic only if you want to poke at the demo wrapper
in `api/`; it is not required for this exercise.)

## Running tests

```bash
pytest -q
```

All tests currently fail with `NotImplementedError` — that's expected,
nothing is implemented yet. Part 1 and Part 2 tests are in separate files so
you can run just the section you're working on, e.g.:

```bash
pytest -q tests/test_percentage_rollout.py
```

## Constraints

- Implement against the given `FeatureFlag` / `FlagRule` interfaces in
  `base.py` — don't change them.
- Rollout decisions must be **deterministic**: no real randomness (no
  `random`, no `uuid4`, nothing seeded per-process) — derive the decision
  from a stable hash of inputs every time, so the same inputs always
  produce the same output, including across separate process runs.
- Beyond the given class shapes and the two interfaces, the internal design
  is yours: you may add private helper methods, private module-level
  functions, private state, or small internal data structures freely.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. It can help you
reason through your class design and talk through tradeoffs, but the actual
implementation and the design decisions behind it need to be yours.

## Deliverables

- Your implementation of all four classes.
- Any tests you added.
- Be ready to explain: your rule-chain design, what invariants each class
  maintains, and whether Part 2 did or didn't require changing your Part 1
  code.
