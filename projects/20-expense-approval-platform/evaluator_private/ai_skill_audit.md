# AI-Skill Audit — Project 20

## Leakage audit

Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `expenseReportService.ts`, `approveReport`, `rejectReport`,
  the unused `actingUserId` parameter, or the `delegatedApproverId` gap.
- Never states the root cause or the fix, including in its rewritten
  "Scope of this exercise" paragraph, which only says "one reported
  authorization bug to find and fix, and one requested delegation feature
  to implement" — this matches what the public README's bug report and
  feature request already tell the candidate directly, so it adds no
  information the candidate doesn't already have.
- Only references generic exercise shape ("single-repository
  debugging-plus-feature exercise," "Express + TypeScript backend,
  in-memory expense-report and user stores, no database, no real
  authentication system"), matching the public README the candidate
  already has.

Read every comment in `candidate/src/` fresh, checking for anything that
states a business rule, a design rationale, or a "why this matters"
justification that doubles as the answer to what the candidate must figure
out:
- `types.ts`: comments state what each interface/field IS ("Shape accepted
  by POST /expense-reports") — no comment says why `assignedManagerId` vs.
  `delegatedApproverId` matters for authorization.
- `middleware/attachUser.ts`, `middleware/requireRole.ts`: comments state
  what the function does mechanically (reads a header, looks up a user,
  gates on role) — neither comment says or implies that the role check
  alone is insufficient for a per-record operation; that reasoning is only
  ever stated in `bug_design.md` and `expected_reasoning.md`, both private.
- `services/expenseReportService.ts`, `controllers/expenseReportController.ts`,
  `repositories/*.ts`: comments are structural ("in-memory store, keyed by
  report id," "thin controller," "business logic... sits between
  controllers and the repository") — none state or hint that
  `approveReport`/`rejectReport` are missing a check, and the unused
  `actingUserId` parameter carries no comment at all (the parameter shape
  itself is the only tell, exactly as the build brief specified — no prose
  points at it).
- `README.md`: states the bug report and feature request in plain language
  (matching a real PM/support-ticket voice) and the deliverables framing
  ("why your fix generalizes... including once delegation exists") — this
  is scope/deliverable framing, not a hint at the specific missing line,
  consistent with how Project 15's README frames its own generalization
  deliverable.

Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo and add the delegation feature." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce the reported bug first. |
| "Just tell me why the wrong manager can approve reports." | Decline to state it outright; offer Level 1-2 help (evidence / direction) — e.g. suggest checking whether `requireRole` and the service layer are answering the same question. |
| "Write the authorization check for approveReport." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "a resource-level check usually compares the acting user's id against a field on the record itself, separate from any role check," using a made-up unrelated example) without pointing at `assignedManagerId`/`delegatedApproverId` by name. |
| "Where should I start?" | Suggest reproducing via the failing tests and tracing the request path from the route through `attachUser`/`requireRole` into the service; does not name the specific missing check. |
| "I think requireRole is letting non-managers through." (incorrect hypothesis) | Engage: ask what evidence supports that, suggest checking whether the "plain employee gets 403" test currently passes — without stating outright that it's a false lead. |
| "I think the service never checks who the report is actually assigned to." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., look at every place `actingUserId`/`assignedManagerId` appear in the function and see which ones are actually compared), without simply saying "correct, add the check on line X." |
| "My delegate endpoint returns 200 and sets the field — am I done?" | Encourage further thinking rather than confirming completion: ask what happens when the delegate themselves tries to approve or reject the report, without naming the gap directly. |
| "Here's my approveReport fix, does this look right?" (candidate shares a diff) | Give real review feedback: correctness, whether `rejectReport` needs the identical change, and prompt them to consider what happens once delegation exists as an edge case to double check. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion, and code review are all available and
  cover most of what a stuck candidate needs, including nudging them toward
  the delegation-consistency follow-up without naming it.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions (TypeScript generics, Express routing,
  Jest/supertest usage).
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged before the assistant narrows further,
  and the "am I done?" handling specifically rewards candidates who keep
  thinking after their delegate endpoint returns 200 rather than stopping
  there.
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
