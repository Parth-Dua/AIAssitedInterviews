# AI-Skill Audit — Project 11

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the design
brief. It:
- Never names any of the three concrete pitfalls in `bug_design.md`
  (isinstance-branching, leaking internal bucket state).
- Never names a formal software design pattern (e.g. "Strategy") anywhere —
  confirmed by a direct text search of the file for "strategy pattern" and
  related pattern names; none appear.
- Never states or implies what the correct `TieredRateLimiter` internals
  should look like, beyond restating the same "without any calling code
  needing to know which strategy is in use" language already present in the
  public README.
- The Part 2/follow-up structure and the general shape ("framework-
  independent library," "two-part requirement revealed after Part 1")
  match only what's already visible in the public README the candidate has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Just design the classes for me." | Decline to hand over a full design. Ask what the candidate has sketched so far, or what state they think each class needs to own, and build from there. |
| "Should I use inheritance or composition here?" | Generic conceptual help is fine — discuss the tradeoffs of inheritance vs. composition in the abstract (e.g. with a made-up unrelated example), and help the candidate reason about which fits *their* stated requirements, without telling them what `TieredRateLimiter` should specifically do. |
| "Write the body of `allow_request` for the token bucket." | Decline to write it. May explain the general algorithm concept (refill based on elapsed time, cap at capacity, consume one token) since that's public, well-known CS material already implied by the README — but not working code for this file. |
| "Is my `TieredRateLimiter` going to work when they add a third strategy later?" | Don't just answer yes/no. Ask what `TieredRateLimiter.allow_request` currently does with the limiter it looks up — does it call the interface, or does it check the limiter's concrete type? Help them reason toward the answer themselves, the same way you'd help evaluate a debugging hypothesis. |
| "What's a token bucket rate limiter, conceptually?" (general CS knowledge) | Explain plainly — this is generic algorithm/library knowledge, always allowed, same tier as explaining what idempotency means in a debugging project. |
| "Here's my `TokenBucketRateLimiter`, does this look right?" (candidate shares code) | Give real review feedback: correctness against the stated refill/consume order, whether the clock is genuinely injected everywhere, edge cases (fractional refill, key not seen before) worth double-checking. |
| "Why did my Part 1 tests break after I added `TieredRateLimiter`?" | Help them debug it like any other failing test — what's the assertion, what's actually returned, where does `TieredRateLimiter` route this key — without directly stating "you're branching on isinstance, stop doing that" as the first move; guide them to notice it themselves if that's the cause. |
| "Just tell me if I should use a dict or a dataclass for the per-key bucket state." | This is a small, generic implementation-detail question with no bearing on the graded design test — fine to discuss tradeoffs plainly (a dataclass is more readable and extensible; a bare tuple is more compact) without it counting as "writing the implementation." |

## Judgment check
- Would a compliant assistant remain useful? Yes — general algorithm
  explanation, design-tradeoff discussion, code review, and debugging help
  are all available, which covers most of what a stuck candidate needs for
  a design-and-implement exercise.
- Too restrictive? No — nothing blocks the candidate from getting real
  design-reasoning help; only the actual authorship of the implementation
  and the direct verdict on whether their design "will work" are withheld,
  mirroring how a debugging project withholds the root cause but not the
  reasoning process.
- Rewards candidate reasoning? Yes — a candidate who's already reasoned
  toward a correct polymorphic design gets confirmation and refinement
  quickly; a candidate who hasn't is redirected to think about it rather
  than handed the answer.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the exercise
   requires only plain Python and pytest, and is fully solvable with any
   capable coding agent or with no AI assistance at all.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not write
   the body of a method for the candidate," "discuss design tradeoffs
   generically") with no reference to a specific tool-call API, permission
   model, or hidden system-prompt mechanism. Usable as a system prompt,
   project instruction file, or manually pasted text in any agent that can
   follow instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's
   implementation, added tests, and design explanation only. Nothing
   references which assistant produced a suggestion, and the hidden tests
   that catch the isinstance-branching pitfall run as plain pytest against
   plain Python classes.
4. **Is any proprietary Claude-specific feature necessary?** No —
   `ratelimiter/` has zero framework dependencies (not even FastAPI or
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
   pytest to run.

Verdict: fully agent-independent and portable.
