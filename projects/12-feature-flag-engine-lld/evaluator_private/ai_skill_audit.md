# AI-Skill Audit — Project 12

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the design
brief. It:
- Never names either of the two concrete pitfalls in `bug_design.md`
  (isinstance-branching in `RuleChain`, `hash()` vs. `hashlib`).
- Never states or implies the correct `RuleChain` internals beyond restating
  the same "without having to rewrite the code that chains rules together"
  language already present in the public README.
- Never names a formal software design pattern (e.g. "Chain of
  Responsibility," "Strategy") anywhere — confirmed by a direct text search
  of the file for pattern names; none appear.
- The Part 2/follow-up structure and the general shape ("framework-
  independent library," "two-part requirement revealed after Part 1")
  match only what's already visible in the public README the candidate has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Just design the classes for me." | Decline to hand over a full design. Ask what the candidate has sketched so far, or what state they think each class needs to own, and build from there. |
| "Should `decide` return a bool or something else?" | Generic conceptual help is fine — discuss, in the abstract, what a "rule that might not apply" needs to be able to express, and help the candidate reason about what the given `bool \| None` signature already implies, without writing their `decide` method bodies for them. |
| "Write the body of `is_enabled` for the percentage rollout flag." | Decline to write it. May explain the general concept (deterministic hash of an identifier mapped into a fixed range, compared against a threshold) since that's public, well-known material already implied by the README — but not working code for this file. |
| "Is my `RuleChain` going to work when they add a fourth rule type later?" | Don't just answer yes/no. Ask what `RuleChain.is_enabled` currently does with each rule it iterates — does it call `.decide(context)` uniformly, or does it check the rule's concrete type first? Help them reason toward the answer themselves, the same way you'd help evaluate a debugging hypothesis. |
| "What's a deterministic hash-based rollout, conceptually?" (general CS/backend knowledge) | Explain plainly — this is generic algorithm/systems knowledge, always allowed, same tier as explaining what a token bucket is in Project 11. |
| "Here's my `PercentageRolloutFlag`, does this look right?" (candidate shares code) | Give real review feedback: correctness against the stated determinism/uniformity requirements, whether they used a stable hash or something process-randomized, edge cases (0%, 100%, boundary bucket values) worth double-checking. |
| "Why did my Part 1 tests break after I added `PercentageRolloutRule`?" | Help them debug it like any other failing test — what's the assertion, what's actually returned, is the rule reusing the flag's logic or reimplementing it — without directly stating "you duplicated the hashing and it drifted, stop doing that" as the first move; guide them to notice it themselves if that's the cause. |
| "Just tell me if I should store the deny-list as a `set` or a `list`." | This is a small, generic implementation-detail question with no bearing on the graded design test — fine to discuss tradeoffs plainly (a `set` gives O(1) membership checks and matches the given constructor's `set[str]` type) without it counting as "writing the implementation." |

## Judgment check
- Would a compliant assistant remain useful? Yes — general algorithm
  explanation, design-tradeoff discussion, code review, and debugging help
  are all available, which covers most of what a stuck candidate needs for
  a design-and-implement exercise.
- Too restrictive? No — nothing blocks the candidate from getting real
  design-reasoning help; only the actual authorship of the implementation
  and the direct verdict on whether their design "will work" are withheld,
  mirroring how Project 11's assistant behaves for the same shape of
  extensibility question.
- Rewards candidate reasoning? Yes — a candidate who's already reasoned
  toward a correct, deferral-respecting, polymorphic design gets
  confirmation and refinement quickly; a candidate who hasn't is redirected
  to think about it rather than handed the answer.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the exercise
   requires only plain Python and pytest, and is fully solvable with any
   capable coding agent or with no AI assistance at all.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not write
   the body of `decide` or `is_enabled` for the candidate," "discuss design
   tradeoffs generically") with no reference to a specific tool-call API,
   permission model, or hidden system-prompt mechanism. Usable as a system
   prompt, project instruction file, or manually pasted text in any agent
   that can follow instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's
   implementation, added tests, and design explanation only. Nothing
   references which assistant produced a suggestion, and the hidden tests
   that catch the isinstance-branching and hardcoded-priority pitfalls run
   as plain pytest against plain Python classes.
4. **Is any proprietary Claude-specific feature necessary?** No —
   `flagengine/` has zero framework dependencies (not even FastAPI or
   Pydantic — those are confined to the fully optional `api/` wrapper), no
   skills/hooks/MCP/tool-specific mechanics are assumed, and
   `assessment.yaml`'s `ai.instructions` pointer is satisfied by loading a
   plain text/markdown file into whatever system-instruction mechanism the
   candidate's assistant offers.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific,
   and the core exercise needs nothing beyond a Python interpreter and
   pytest (specifically, only the standard-library `hashlib` module beyond
   pytest itself) to run.

Verdict: fully agent-independent and portable.
