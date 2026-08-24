# Scoring Rubric — Project 12: Feature Flag Rule Engine LLD (100 points)

| Category | Points | Notes |
|---|---|---|
| Public API / interface design | 15 | Implementations depend only on `FeatureFlag.is_enabled` / `FlagRule.decide`; constructors match the given signatures; `rollout_percentage` validated or at least handled sensibly at the boundaries (0 and 100); per-user/per-key state is never leaked as a public attribute. |
| Part 1 correctness (`PercentageRolloutFlag`) | 20 | Deterministic (`hashlib`-based, not `random`/built-in `hash()`) bucketing; same user always gets the same result; 0% disables everyone, 100% enables everyone; different `flag_name`s can diverge for the same user; statistical uniformity holds within the hidden tests' tighter tolerance. |
| Part 2 correctness (`DenyListRule` / `AllowListRule` / `PercentageRolloutRule` / `RuleChain`) | 15 | `DenyListRule` only ever returns `False`/`None`, `AllowListRule` only ever `True`/`None`, `PercentageRolloutRule` never returns `None`; `RuleChain` returns the first non-`None` decision in the order rules were given, falls back to `default` only when every rule defers (including the empty-list case). |
| Extensibility — genuinely polymorphic `RuleChain`, no rewrites | 15 | The core question: does `RuleChain.is_enabled` call `rule.decide(context)` on each rule uniformly and check for `None`, or does it branch on `isinstance(rule, DenyListRule)` / `AllowListRule` / `PercentageRolloutRule`? The isinstance-branching hidden tests (see `bug_design.md`) are the objective check; also confirm `RuleChain` doesn't hardcode a deny-before-allow ordering independent of the list it's given, and check whether the candidate had to go back and change `percentage_rollout.py` for Part 2 to work beyond factoring out a small shared helper (they shouldn't have needed more than that) — ask directly in the debrief if not obvious from the diff/timeline. |
| Code quality / responsibility assignment | 10 | `PercentageRolloutFlag` and `PercentageRolloutRule` share bucketing logic rather than duplicating it; each rule class owns only its own state (its own user-id set, or nothing at all for the rollout wrapper); `RuleChain` owns no rate/rollout state of its own, only the rule list and default; see `bug_design.md` pitfall #2 for the hash-choice quality signal. |
| Tests added | 10 | Candidate added at least one test beyond the given public ones — a boundary case, an additional custom `FlagRule` implementation, a multi-rule ordering scenario, etc. |
| Communication / design explanation | 15 | Can clearly state: why `FlagRule.decide` needs to be able to return `None` rather than a plain `bool`, why the bucketing needs `hashlib` rather than `random` or the built-in `hash()`, why `RuleChain` only depends on the abstract `FlagRule` interface (or, if it doesn't, why they made that tradeoff), and whether/why Part 2 required touching Part 1 code. |

**Passing bar (strong backend signal):** ≥75, all public tests pass, and the
isinstance-branching hidden tests specifically pass (i.e. `RuleChain` is
genuinely polymorphic over `FlagRule`) — a candidate who ships a correct
Part 1 and Part 2 but built `RuleChain` via isinstance-branching should not
clear the Extensibility category and should be capped well below the
passing bar regardless of how clean the rest of the code is, since the
whole point of Part 2 is testing exactly this.

**Red flags:**
- `RuleChain` uses `isinstance()` against `DenyListRule` / `AllowListRule` /
  `PercentageRolloutRule` (or a `type()` check, or a string tag like
  `rule_kind`) instead of calling `decide(context)` polymorphically and
  checking for `None` — fails the design-pitfall hidden tests even if every
  public test passes.
- `RuleChain` internally always evaluates "deny-shaped" rules before
  "allow-shaped" rules regardless of the order it was constructed with,
  instead of simply walking `self._rules` in list order.
- `PercentageRolloutRule` re-implements its own independent hashing/bucketing
  logic instead of reusing `PercentageRolloutFlag`'s (or a shared helper) —
  a latent drift risk even if the two currently happen to agree.
- Candidate uses Python's built-in `hash()` (or `random`, or `uuid4`) to
  decide rollout membership instead of a stable hash like `hashlib.sha256` —
  breaks the "same result forever, across process restarts" requirement even
  though it may pass every test run within a single pytest process (built-in
  `hash()` is stable within one process run unless `PYTHONHASHSEED` varies
  the run itself).
- No real test discipline — candidate's own added tests hardcode specific
  user IDs and percentages without acknowledging the statistical nature of
  rollout, or use an unreasonably tight tolerance likely to flake.
- Candidate cannot explain why `decide` needs a three-valued-ish return
  (`bool | None`) instead of plain `bool`, or treats it as an incidental
  detail rather than the mechanism that makes rule composition work at all.
