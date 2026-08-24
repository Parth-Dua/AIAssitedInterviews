# AI-Skill Audit — Project 16

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `taskService.ts`, `updateTask`, the hardcoded `status` field,
  or the missing enum-validation gap.
- Never states the root cause or the fix, including in its rewritten
  "Scope of this exercise" paragraph, which only says "a partial-update
  (`PATCH`) request that silently fails to change one of the fields it
  targets" — this matches what the public README's bug report already
  tells the candidate directly, so it adds no information the candidate
  doesn't already have.
- Only references generic exercise shape ("single-repository debugging
  exercise," "Express + TypeScript backend, in-memory task store, no
  database"), matching the public README the candidate already has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the status update issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "make sure every field in a merge follows the same present-or-fallback pattern," using a made-up unrelated example) without pointing at the exact line. |
| "Where should I start?" | Suggest reproducing via the failing tests and tracing the request path from the `PATCH` route through to the service; does not name the specific bug or file. |
| "I think the validation middleware is stripping the status field." (incorrect hypothesis) | Engage: ask what evidence supports that, suggest checking which route the middleware is actually attached to — without stating outright that it's a false lead. |
| "I think the service is hardcoding the status field instead of using the update." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., add a log/print of `updates.status` right before the merge, or read the line character by character), without simply saying "correct, change line X." |
| "My fix makes the failing tests pass now — am I done?" | Encourage further thinking rather than confirming completion: ask what happens if the update contains a value outside the expected set of statuses, without naming the validation gap directly. |
| "What does `Partial<T>` / `??` do in TypeScript?" (syntax/library help) | Explain plainly — this is generic TypeScript/language help, always allowed. |
| "Here's my fix, does this look right?" (candidate shares a diff) | Give real review feedback: correctness, whether it preserves the "PATCH updates exactly the fields provided" invariant, and prompt them to consider input validation as an edge case to double check. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion, and code review are all available and
  cover most of what a stuck candidate needs, including nudging them
  toward the validation-gap follow-up without naming it.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions (TypeScript generics, Express routing,
  Jest/supertest usage).
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged before the assistant narrows further,
  and the "am I done?" handling specifically rewards candidates who keep
  thinking after their tests go green rather than stopping there.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix
   requires only reading TypeScript/Express code and running `npm test`.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not
   reveal the root cause," "use escalating assistance levels") with no
   reference to a specific tool-call API, permission model, or hidden
   system-prompt mechanism. It is usable as a system prompt, project
   instruction file, or manually pasted text in any agent that can follow
   instructions (Claude, Cursor, Copilot, Codex, Gemini, or otherwise).
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff,
   tests, and verbal explanation only. Nothing references which assistant
   produced a suggestion.
4. **Is any proprietary Claude-specific feature necessary?** No — no
   skills/hooks/MCP/tool-specific mechanics are assumed. `assessment.yaml`'s
   `ai.instructions` pointer is satisfied by loading a plain text/markdown
   file into whatever system-instruction mechanism the candidate's
   assistant offers. The toolchain itself (`npm`/`tsc`/`jest`/`ts-jest`) is
   plain Node.js tooling, not tied to any AI vendor.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific,
   and the same pattern is reused unchanged (byte-for-byte, aside from the
   final scope paragraph) from Project 1 through Project 20.

Verdict: fully agent-independent and portable.
