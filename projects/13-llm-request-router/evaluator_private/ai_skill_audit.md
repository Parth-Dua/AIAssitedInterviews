# AI-Skill Audit — Project 13

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `llm_router_service.py`, `self._cache.set`, the two cache-
  write call sites, `NoValidCompletionError`, or any other implementation
  detail.
- Never states the root cause or the fix for either the bug or the
  feature.
- Only references the generic exercise shape ("debugging-plus-feature
  exercise," "fully fake, deterministic, offline model clients," "one
  reported response-caching correctness bug," "one requested [validation]
  feature"), which matches the public README the candidate already has.
- Explicitly reassures the candidate that no real ML/API keys/network
  calls are involved — this is scope-setting information the candidate
  already has from the README, not a hint about the bug.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce the failing tests first. |
| "Just tell me why the cache is stale." | Decline to state the root cause outright; offer Level 1-2 help (evidence: what does the failing test show / direction: which method actually writes to the cache). |
| "Write the patch for the fallback-caching bug." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "a cache write is usually conditioned on which source produced the value being written") without pointing at the exact line(s) to change. |
| "Should I just add a TTL to the cache to fix this?" (plausible-but-wrong hypothesis) | Engage honestly: ask what the candidate expects a TTL to change here, and point out (without stating the final answer) that the bug report describes the primary recovering arbitrarily soon after the outage — invite the candidate to reason about whether a TTL of any length would reliably satisfy that. Do not confirm or deny the hypothesis outright. |
| "I think the cache write after the fallback call shouldn't be there." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify it (e.g., "what test would confirm that, once removed, the legitimate primary-caching case still works?") rather than just saying "yes, delete it." |
| "How do I make the retry loop also treat a blank response as a failure?" (asking about mechanism, not the specific fix) | Explain the general pattern (checking a returned value against a validity condition and treating an invalid result like a caught exception for control-flow purposes) using a generic, unrelated example, without writing the actual conditional for this repository's retry loop. |
| "Here's my fix, does this look right?" (candidate shares a diff) | Give real review feedback: does it stop caching fallback results in *all* configurations, not just the reported prompt; does it validate the fallback's response too, or only the primary's; does a blank result ever reach `self._cache.set` or the caller. |
| "What does `FakeModelClient.complete` do?" (reading unfamiliar given code) | Explain plainly — this is generic code-reading help about a file that's explicitly correct and given, always allowed, and encourages the candidate to actually read it rather than skip it. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering,
  repo navigation, hypothesis discussion (including pushing back on the
  TTL red herring without just supplying the real answer), and code review
  are all available and cover most of what a stuck candidate needs for
  both the bug and the feature.
- Too restrictive? No — a candidate who reasons well moves through the
  escalation ladder quickly and gets a focused hint if truly stuck on
  either half; nothing blocks basic syntax/library questions or reading
  the given, correct `FakeModelClient` code.
- Rewards candidate reasoning? Yes — the TTL hypothesis specifically
  requires the candidate to articulate *why* it doesn't work, not just
  accept or reject it on the assistant's say-so.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced anywhere.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the
   candidate repo, README, or SKILL.md references Claude or any vendor;
   the fix requires only reading Python/asyncio/FastAPI code and running
   pytest. No real model provider, API key, or network access is involved
   anywhere in the exercise.
2. **Do the guarded instructions make sense for any capable coding
   agent?** Yes — SKILL.md is written as plain behavioral constraints
   ("do not reveal the root cause," "use escalating assistance levels")
   with no reference to a specific tool-call API, permission model, or
   hidden system-prompt mechanism. It is usable as a system prompt,
   project instruction file, or manually pasted text in any agent capable
   of following instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff,
   tests, and verbal explanation only. Nothing references which assistant
   produced a suggestion.
4. **Is any proprietary Claude-specific feature necessary?** No — no
   skills/hooks/MCP/tool-specific mechanics are assumed. `assessment.yaml`'s
   `ai.instructions` pointer is satisfied by loading a plain text/markdown
   file into whatever system-instruction mechanism the candidate's
   assistant offers. The "fake model client" domain itself requires no
   provider-specific SDK or API — it's pure standard-library Python
   (`asyncio`, `hashlib`).
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific,
   and the exercise's fake/deterministic/offline design means no runner
   ever needs to provision or pay for a real model API to run this
   project.

Verdict: fully agent-independent and portable.
