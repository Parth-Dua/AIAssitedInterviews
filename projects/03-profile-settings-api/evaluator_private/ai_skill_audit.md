# AI-Skill Audit — Project 3

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `profile_service.py`, `model_dump`, `exclude_unset`,
  `exclude_none`, or any specific field.
- Never states the root cause or the fix.
- Only references generic exercise shape ("single reported behavioral bug
  involving a PATCH partial-update endpoint," "FastAPI backend, in-memory
  data, no database"), which matches the public README the candidate
  already has and does not name the mechanism (omitted-vs-null) at all.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the PATCH endpoint issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "partial-update endpoints usually need to distinguish 'field not sent' from 'field sent as empty'") without pointing at the exact line or naming `exclude_unset`. |
| "Where should I start?" | Suggest reproducing via the failing test and reading `update_profile` and the request schema end-to-end; does not name the specific bug. |
| "What's the difference between exclude_unset and exclude_none in Pydantic?" (generic library question) | Explain plainly and generically (this is standard Pydantic library knowledge, always allowed) without saying which one this repository's fix needs or pointing at the specific file/line. |
| "I think the repository's save() is overwriting fields wrong." (incorrect hypothesis) | Engage: ask what evidence supports that; point out that `save()` is a simple dict assignment, so the candidate should check what's being passed *into* it, without immediately supplying the real answer. |
| "I think the merge logic doesn't know which fields were actually sent by the caller." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., print `request.model_dump()` vs. `request.model_fields_set` for a partial request), without simply saying "correct, use exclude_unset on line X." |
| "Here's my fix using exclude_none=True, does this look right?" (candidate shares the tempting-but-wrong fix) | Give real review feedback: note it passes the reported case, but ask what happens if a caller explicitly wants to *clear* a nullable field with `null` — prompt the candidate to test that case themselves, without simply naming `exclude_unset` as the correct answer. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion, generic Pydantic/library explanations,
  and code review are all available and cover most of what a stuck
  candidate needs.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions, including generic `exclude_unset` vs.
  `exclude_none` explanations (just not "which one to use here").
- Rewards candidate reasoning? Yes — the escalation ladder, plus the
  requirement that even a correct hypothesis only gets confirmation-and-
  verification-help rather than a direct "yes," means the candidate must
  still independently connect the generic library concept to this
  repository's specific merge code and think through the null-clearing
  edge case themselves.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix
   requires only reading Python/FastAPI/Pydantic code and running pytest.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not
   reveal the root cause," "use escalating assistance levels") with no
   reference to a specific tool-call API, permission model, or hidden
   system-prompt mechanism. It is usable as a system prompt, project
   instruction file, or manually pasted text in any agent that can follow
   instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff, tests,
   and verbal explanation only. Nothing references which assistant produced
   a suggestion.
4. **Is any proprietary Claude-specific feature necessary?** No — no
   skills/hooks/MCP/tool-specific mechanics are assumed. `assessment.yaml`'s
   `ai.instructions` pointer is satisfied by loading a plain text/markdown
   file into whatever system-instruction mechanism the candidate's assistant
   offers.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific.

Verdict: fully agent-independent and portable.
