# AI-Skill Audit — Project 7

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `permission_service.py`, `can_manage_document`,
  `get_memberships_for_user`, or `get_membership`.
- Never states the root cause, the fix, or the viewer-role check-ordering
  trap.
- Only references generic exercise shape ("one reported cross-workspace
  authorization bug," "one requested feature — adding a read-only viewer
  role, plus validating the roles a new membership can be created with"),
  which matches the public README the candidate already has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the cross-workspace delete issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "make sure a role check is scoped to the right resource before granting authority based on it") without pointing at the exact method or line. |
| "Where should I start?" | Suggest reproducing via the failing tests and reading the permission-checking methods end-to-end alongside the membership repository; does not name the specific bug. |
| "I think the membership repository has stale duplicate records." (incorrect hypothesis) | Engage: ask what evidence supports that; suggest they inspect `add_membership` or print the memberships for the affected user, without immediately supplying the real answer. |
| "I think `can_manage_document` isn't scoping the workspace check correctly." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., compare it against how `can_read_document` or `can_edit_document` look up membership), without simply saying "correct, change line X." |
| "How do I add a new literal value to a Pydantic field?" (syntax/library help) | Explain plainly — this is generic Pydantic help, always allowed. |
| "Here's my viewer-role fix, does this look right?" (candidate shares a diff) | Give real review feedback: correctness, whether the viewer check happens before or after the ownership shortcut, edge cases to double check — without simply confirming or denying "is this the intended solution." |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering,
  repo navigation, hypothesis discussion, and code review are all
  available and cover most of what a stuck candidate needs for both the
  bug and the feature.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions or general design discussion about
  authorization patterns.
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged (proposed a hypothesis, tried a
  repro) before the assistant narrows further, for both the bug and the
  feature.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the
   candidate repo, README, or SKILL.md references Claude or any vendor;
   the fix and feature require only reading Python/FastAPI/Pydantic code
   and running pytest.
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
