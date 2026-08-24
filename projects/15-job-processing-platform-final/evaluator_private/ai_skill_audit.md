# AI-Skill Audit — Project 15 (Capstone)

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `job_service.py`, `finish_job`, `cancel_job`, or the boolean
  guard condition.
- Never states the root cause, the fix, or that the guard's problem is a
  redundant/implied clause.
- The "Scope of this exercise" paragraph (the only section rewritten from
  Project 1's template) only says: FastAPI backend, one in-memory job
  repository, no database, no real concurrency/threads, fully sequential
  and deterministic, one reported bug plus one requested feature. All of
  this already appears in the public README and is necessary scenario
  framing, not a hint at *where* or *what* the defect is.
Verdict: **no leakage**.

Also re-read every candidate-visible docstring in `app/` with the same
fresh-eyes standard (per the fresh-solver-simulation lesson from earlier
projects in this suite: a docstring that restates a business rule in
language close to the fix mechanism is a spoiler even if the code file
itself is never named):
- `job_service.py`'s `JobService` docstring: "Orchestrates job lifecycle
  transitions on top of JobRepository." — purely structural, states no
  business rule, no valid-transition set, no hint about which method has
  the gap.
- `job_repository.py`'s `JobRepository` docstring: describes it as an
  in-memory store, mentions it would be a database table in production —
  identical in spirit to Project 1's `PricingRepository` docstring, purely
  mechanical.
- `export_worker.py`'s `compute_export_result` docstring: states it's a
  pure function of `payload` and lists what it has none of (I/O,
  randomness, timestamps) — this is necessary for the candidate to be able
  to *rule out* Hypothesis 1 by reading the module, not a spoiler about the
  `finish_job` bug elsewhere; it says nothing about job status transitions
  at all.
- `app/api/routes/jobs.py` docstrings ("Submits a new export job.",
  "Simulates a worker picking up a job.", "Simulates a worker reporting job
  completion or failure.", "Returns the current state of a job."): purely
  mechanical one-liners describing what the endpoint does structurally, no
  mention of guards, transitions, or duplicate-delivery behavior.
- The starting code has **no** `cancel_job` method or route at all, so
  there is no docstring to leak anything about the feature's expected
  guard — the candidate must design the transition rule themselves from
  the README, which is the intended source for business rules in every
  project in this suite.
Verdict: **no leakage** — no candidate-visible docstring states a business
rule, a valid/invalid transition set, or anything that doubles as the
answer. Business rules live only in `README.md`, matching the convention
established across the whole curriculum.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo — the bug and the cancel feature." | Decline to broadly fix both; ask what's been reproduced so far, or offer to help reproduce the bug first before discussing the feature at all. |
| "Just tell me why the duplicate finish isn't rejected." | Decline to state it outright; offer Level 1-2 help (point at the failing test's evidence, or suggest tracing what feeds `finish_job`'s guard) without naming the boolean-logic error. |
| "Write cancel_job for me." | Decline to write the actual implementation. May discuss the *shape* of a status-guard generically (e.g., "a transition method typically checks the current status against the one or more statuses it's valid to transition from, before mutating anything") using a made-up unrelated example, without writing this repository's actual `cancel_job`. |
| "I think the guard is checking the wrong variable, like Project 1's shipping bug." (candidate pattern-matching from experience) | Engage with the analogy on its own terms — ask what specifically about the current guard looks wrong to them, point them at manually evaluating it for a few concrete status values, without confirming or denying the analogy holds here. |
| "I added cancel_job and it passes the tests I can see — am I done?" (candidate who wrote the unconditional-cancel version, unaware of hidden tests) | Do not reveal that hidden tests exist or what they check. Ask what statuses they tested cancelling *from* — did they only test cancelling a freshly created job? — nudging them toward testing their own new code from every relevant state, the same way they're testing the bug fix, without stating the specific gap. |
| "I think the same kind of guard problem might exist in start_job too — should I check?" (candidate on the right track) | Confirm the instinct to check systematically is sound and encourage them to trace through it the same way they did for `finish_job`, without confirming whether `start_job` does or doesn't have a gap before they've looked. |
| "What does `model_validator(mode='after')` do in Pydantic?" (syntax/library help) | Explain plainly — this is generic Pydantic help, always allowed. |
| "Here's my fix to finish_job and my new cancel_job, does this look right?" (candidate shares a diff) | Give real review feedback: correctness of the guard condition, whether `cancel_job`'s guard mirrors the same pattern, edge cases (terminal states, a cancelled job's later start/finish) to double check — genuine code review, not a rubber stamp. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering,
  repo navigation, hypothesis discussion, generic pattern discussion, and
  code review are all available, and this project's core signal
  (recognizing the shared invariant across three methods) is exactly the
  kind of thing a candidate can be nudged toward systematically checking
  without being told the answer.
- Too restrictive? No — a candidate reasoning well moves through the
  escalation levels quickly, and nothing here blocks basic syntax/library
  questions or legitimate code review of work already done.
- Rewards candidate reasoning, especially generalization? Yes — the
  "cancel_job passes what I can see, am I done?" row is deliberately
  designed to redirect the candidate toward testing their own new code
  more thoroughly, without doing that testing for them — this is the
  single highest-leverage moment in the whole audit, since it's exactly
  where the project's central signal (generalizing past the literal report)
  lives.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the
   candidate repo, README, or SKILL.md references Claude or any vendor;
   the fix and feature require only reading Python/FastAPI/dataclass code
   and running pytest.
2. **Do the guarded instructions make sense for any capable coding
   agent?** Yes — SKILL.md is written as plain behavioral constraints ("do
   not reveal the root cause," "use escalating assistance levels") with no
   reference to a specific tool-call API, permission model, or hidden
   system-prompt mechanism. It is usable as a system prompt, project
   instruction file, or manually pasted text in any agent that can follow
   instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff,
   tests, and verbal explanation only. Nothing references which assistant
   produced a suggestion, and the dedicated "generalization" rubric
   category is scored purely from what code the candidate wrote.
4. **Is any proprietary Claude-specific feature necessary?** No — no
   skills/hooks/MCP/tool-specific mechanics are assumed anywhere in the
   candidate-facing materials. `assessment.yaml`'s `ai.instructions`
   pointer is satisfied by loading a plain text/markdown file into
   whatever system-instruction mechanism the candidate's assistant offers.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific.

Verdict: fully agent-independent and portable.
