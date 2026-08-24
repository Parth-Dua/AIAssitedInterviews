# AI-Skill Audit — Project 6

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug and
feature design. It:
- Never names `notification_prefs_service.py`, `update_preferences`,
  `cache.delete`, `cache.set`, or any specific method/line.
- Never states the stale-cache bug's root cause or the correct fix.
- Never states the TTL feature's implementation (no mention of
  `expires_at`, the `>=` boundary convention, or the injectable-clock
  parameter name).
- Never hints at the "cache the request body instead of the persisted
  value" trap.
- Only references generic exercise shape ("one reported stale-cache bug,"
  "one requested feature — adding a TTL to the cache," "FastAPI backend,
  an in-memory repository standing in for a database, a small in-memory
  cache module standing in for a Redis-like cache, no real database or
  Redis server," "tests must not rely on real sleeping"), which matches
  the public README the candidate already has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix the bug and build the TTL feature for me." | Decline to do the whole thing. Ask what's been reproduced so far for the bug, and what design the candidate is considering for TTL. |
| "Just tell me why the settings page shows the old value." | Decline to state it outright; offer Level 1-2 help (evidence: what does the failing test show about the sequence of GET/PUT/GET? direction: look at both handlers in the service and compare what each one does with the cache). |
| "Write the cache invalidation call for me." | Decline to write the actual line. May discuss the *shape* of the fix generically (e.g., "in general, a write path needs to either clear or refresh whatever a read path might have cached") without writing this repository's actual fix. |
| "Where should I start on the bug?" | Suggest reproducing via the failing PUT-then-GET test and reading both `get_preferences` and `update_preferences` side by side; does not name the missing call. |
| "I'll just overwrite the cache with the request body when I get a PUT, that's simpler than deleting." (candidate proposes the tempting-but-wrong design) | Engage: ask whether the value written to the repository is always guaranteed to be identical to the raw request body, and how they'd find out — without directly stating "that's wrong, cache what was persisted instead." |
| "I think I should invalidate/delete the cache entry on write, or cache exactly what the repository save() call returns." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., a test that exercises a case where the server changes the value before persisting it), rather than just saying "yes that's correct." |
| "How do I write a test that advances time without actually sleeping?" (syntax/technique help) | Explain plainly — this is generic testing/dependency-injection technique help, always allowed, and squarely inside what the exercise asks for. |
| "Here's my Cache class with TTL, does this look right?" (candidate shares a diff) | Give real review feedback: whether `set`/`get` handle the TTL consistently, whether the boundary convention is applied uniformly, whether the clock is used via `self._now()` everywhere rather than calling `time.monotonic()` directly somewhere, edge cases (no TTL given, TTL of 0) worth double-checking. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering,
  repo navigation, hypothesis discussion for both the bug and the TTL
  design, and code review are all available and cover most of what a
  stuck candidate needs across both deliverables.
- Too restrictive? No — a candidate who reasons well on either the bug or
  the feature can move through the escalation levels quickly and get a
  focused hint on the specific part they're stuck on; nothing blocks
  basic syntax/library/testing-technique questions.
- Rewards candidate reasoning? Yes — for the bug specifically, the
  assistant is directed to probe "is the request body always identical to
  what gets persisted?" rather than confirming or denying the
  cache-the-request design outright, which keeps the candidate
  responsible for reaching (and verifying) the correct design themselves.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the
   candidate repo, README, or SKILL.md references Claude or any vendor;
   both the bug fix and the TTL feature require only reading Python/
   FastAPI code and running pytest.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not
   reveal the root cause," "use escalating assistance levels") with no
   reference to a specific tool-call API, permission model, or hidden
   system-prompt mechanism. It is usable as a system prompt, project
   instruction file, or manually pasted text in any agent that can follow
   instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff,
   tests, and verbal explanation only. Nothing references which assistant
   produced a suggestion.
4. **Is any proprietary Claude-specific feature necessary?** No — no
   skills/hooks/MCP/tool-specific mechanics are assumed. `assessment.yaml`'s
   `ai.instructions` pointer is satisfied by loading a plain text/markdown
   file into whatever system-instruction mechanism the candidate's
   assistant offers.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific.

Verdict: fully agent-independent and portable.
