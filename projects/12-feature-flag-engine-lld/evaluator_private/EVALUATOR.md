# Evaluator Guide — Project 12: Feature Flag Rule Engine LLD

## Format & target
Low-Level Design + Implementation. Backend SWE, mid-level and up. ~60-90 min.
Difficulty 8/10.

## How to grade

1. Confirm both parts are implemented: `candidate/flagengine/percentage_rollout.py`,
   `rules.py`, and `rule_chain.py` no longer raise `NotImplementedError`.
2. Copy `hidden_tests/test_flagengine_hidden.py` into `candidate/tests/` and
   run `pytest -q` from `candidate/`. All public + hidden tests should pass
   for a fully correct, well-designed solution.
3. Specifically check the four `RuleChain`-polymorphism hidden tests
   (`test_chain_honors_a_custom_rule_that_is_the_only_rule`,
   `test_chain_custom_rule_decision_beats_default_when_placed_after_known_rules`,
   `test_chain_falls_through_a_deferring_custom_rule_to_the_next_rule`,
   `test_chain_mixes_a_custom_rule_with_built_in_rules_in_the_middle`) —
   these are the objective check for the isinstance-branching pitfall (see
   `bug_design.md`). If these fail while everything else passes, the
   candidate's `RuleChain` is very likely branching on concrete rule types
   instead of calling `rule.decide(context)` polymorphically; open
   `rule_chain.py` and confirm.
4. Also check `test_rule_chain_respects_whatever_order_it_is_given` — a
   `RuleChain` that internally always checks "deny-like" rules before
   "allow-like" rules (rather than walking `self._rules` in the order it was
   given) will fail this even if it isn't literally isinstance-branching.
5. Review whether Part 2 required modifying Part 1 code
   (`percentage_rollout.py`). Check the candidate's diff/commit history if
   available, or ask directly in the debrief. **This is itself a design
   signal, not just a pass/fail gate** — a candidate whose Part 1 needed no
   changes to support Part 2 (beyond factoring out a small shared helper,
   which is expected and fine) demonstrated that their original design
   anticipated the kind of change a follow-up requirement introduces, which
   is the actual thing this exercise is testing.
6. Confirm `PercentageRolloutRule` reuses the Part 1 bucketing logic rather
   than re-deriving it — `test_percentage_rollout_rule_agrees_with_percentage_rollout_flag`
   is the objective check, but it's also worth glancing at `rules.py` to see
   *how* it's reused (composing a `PercentageRolloutFlag`, or calling a
   shared module-level helper, are both fine; two independent hashing
   implementations that happen to agree today are a quality flag even if
   the test currently passes).
7. Compare the candidate's class design against
   `reference_solution/flagengine/` and `expected_reasoning.md` — several
   internal designs are fine (dataclass vs. plain int for bucket storage,
   how the shared hashing helper is exposed, etc.); only the
   externally-observable behavior and the polymorphism requirement are hard
   constraints.
8. Score with `scoring_rubric.md`.
9. Ask 2-3 questions from `DEBRIEF.md`.

## Interview-realism audit (private)

1. **Format simulated:** LLD/OOD coding round — implement a small library
   from two interfaces and a requirements doc, with a follow-up requirement
   revealed mid-exercise. Feature flags / experimentation is one of the
   most common "gradual rollout" system-design and OOD prompts asked at
   backend-heavy interview loops, distinct in mechanism from Project 11's
   clock-based rate limiter (deterministic hashing + rule-chain-with-
   deferral, vs. token-bucket state + simple tiered dispatch).
2. **Role level:** Mid-level backend SWE and up; also reasonable for a
   strong new grad in a system-design-adjacent loop, though the
   `bool | None` deferral semantics push this slightly above Project 11's
   difficulty.
3. **Why feasible in 60-90 min:** Part 1 is a self-contained, well-scoped
   deterministic-hashing rollout (a very common real-world mechanism many
   candidates have implemented or read about) with a given class skeleton
   and given public tests describing exact expected behavior. Part 2 reuses
   the same context-dict convention and the same abstraction style
   established in Part 1, so it's mostly new surface area (the chain-of-
   rules-with-deferral idea), not entirely new concepts. A candidate who
   paces well should finish core implementation in 45-60 minutes, leaving
   time to add tests and articulate reasoning.
4. **Signal obtained:** Whether the candidate can (a) implement a
   deterministic, hash-based decision function correctly against a given
   interface and statistical-uniformity requirement, and (b) design a rule
   chain that depends only on an abstraction (including a three-valued-ish
   `bool | None` return, i.e. "decide or defer") rather than quietly
   coupling to concrete rule types — a very common real LLD-interview
   failure mode whenever a "list of pluggable rules evaluated in order"
   requirement shows up (also seen in real systems like middleware chains,
   validation pipelines, and permission-check cascades).
5. **Coding vs. reasoning split:** ~55% coding (four classes, real logic in
   each), ~45% design reasoning/verification (why `decide` needs to be able
   to return `None`, why `hashlib` over the built-in `hash()`, what
   `RuleChain` should and shouldn't know about its rules).
6. **Would a top company use a close variant:** Yes — "design a feature
   flag / experimentation rollout system" and "design a rule-based
   decision engine that a team can keep extending" are both recurring LLD
   interview prompts at companies running experimentation platforms, and
   the deterministic-bucketing-by-hash technique described here is the same
   one production feature-flag systems actually use.
7. **Anything included for production education rather than signal?** No —
   the determinism requirement (hash-based, not random) is included purely
   because it's the only way to make "does the same user always get the
   same result" testable and correct at all, not as a lesson in itself. The
   FastAPI wrapper in `api/` is explicitly optional/non-graded and exists
   only for scenario realism.

## AI-trivialization check

Tested prompt: "Implement PercentageRolloutFlag, DenyListRule, AllowListRule,
PercentageRolloutRule, and RuleChain per the README, make all tests pass." A
capable general-purpose coding agent with full repo access (not bound by the
assessment SKILL.md) can plausibly produce a fully correct, properly
polymorphic solution in one or two shots — deterministic bucket hashing and
"chain of rules, first non-None answer wins" are both well-represented
patterns in training data, and the explicit Part 2 wording ("without having
to rewrite the code that chains rules together") strongly primes a capable
model toward pure delegation over isinstance-branching, the same way
Project 11's wording does for its dispatcher.

This is expected and acceptable for a *Level 1-2 (fundamentals)* LLD
project — same posture as Project 11. The interview signal is not "can the
AI produce a correct design" but "can the candidate drive that design
themselves, explain their own class boundaries, and recognize (with or
without AI help) why the deferral/polymorphism requirement matters." Under
the assessment SKILL.md, the assistant is constrained to discuss design
tradeoffs and review code rather than write the implementation outright,
which restores the intended signal: the candidate still has to make and
defend the actual design decisions. See `ai_skill_audit.md`.

## Agent independence
No part of grading references which AI product the candidate used. Grade
the candidate's implementation, added tests, and design explanation only.

## Fresh solver simulation (validation record)

Run per rule 34: an isolated agent received only `candidate/README.md`,
`candidate/.ai/assessment-skill/SKILL.md`, and repo access — no design
brief, hidden tests, reference solution, or evaluator notes. Result: it
implemented all classes correctly (all public tests passed), produced a
genuinely polymorphic `RuleChain` (proved it by dropping in a novel custom
rule type it wrote itself), correctly used `hashlib` over `hash()` for
cross-process determinism, and refactored the bucketing logic into a
shared helper so `PercentageRolloutFlag` and `PercentageRolloutRule` agree
— in an estimated 45-70 minutes, inside the 60-90 minute timebox.

**Finding that caused a revision:** it flagged two README passages as
over-explicit, the same pattern already caught on Project 11: (1) "think
about how to share that logic between the two without duplicating it" —
handing the candidate the refactor decision rather than letting the
duplication smell prompt it; (2) the closing prompt asking whether
`RuleChain` would work "without changing a single line of `RuleChain`
itself" for a new rule type — very close to stating the intended
polymorphic design outright. It also separately noted the given `bool |
None` interface itself is a significant scaffold (it pre-supplies the
"defer" concept), but judged that appropriate for this difficulty/duration
rather than a defect, so no change was made there. **Fix applied:** the
first passage was reworded to state only the behavioral requirement
(`PercentageRolloutRule` must *agree* with `PercentageRolloutFlag` for the
same inputs — testable, doesn't prescribe the implementation approach);
the closing prompt was reworded to ask the candidate to explain their
design and how they'd expect it to behave with a future rule type, without
presupposing the answer is "zero changes." Public test pass/fail split
re-verified unchanged (all 10 fail with `NotImplementedError`) — README-only
change, no code touched.

It confirmed it never accessed anything outside `candidate/`. (Its
implementation and added test edits were reverted after the simulation,
then the README fix was applied and re-validated, restoring the original
unimplemented starting state.)
