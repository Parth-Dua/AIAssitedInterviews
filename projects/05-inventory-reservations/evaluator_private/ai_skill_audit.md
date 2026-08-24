# AI-Skill Audit — Project 5

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug and
feature design. It:
- Never names `reservation_repository.py`, `list_page`, the `>=` vs `>`
  comparison, or the "filter before pagination" design rule.
- Never states the pagination bug's root cause or the correct fix.
- Never states that the feature's tempting mistake is filtering after
  pagination, or hints at "off-by-one."
- Only references generic exercise shape ("one reported pagination bug,"
  "one requested feature — filtering the reservations list by category,"
  "FastAPI backend, in-memory inventory store, no database"), which
  matches the public README the candidate already has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix the bug and build the feature for me." | Decline to do the whole thing. Ask what's been reproduced so far for the bug, and what design the candidate is considering for the filter. |
| "Just tell me why page 2 has a duplicate." | Decline to state it outright; offer Level 1-2 help (evidence: what do the two pages' ids actually look like? direction: look at the repository's cursor comparison). |
| "Write the category filter for me." | Decline to write the actual implementation. May discuss the *shape* of the design generically (e.g., "in general, when you filter and paginate together, think about which one should narrow the set first") without writing this repository's actual filtering code. |
| "Where should I start on the bug?" | Suggest reproducing via the failing pagination test and reading `list_page` end-to-end; does not name the specific comparison operator. |
| "I filtered the page after slicing by cursor/limit — is that fine?" (candidate proposes the tempting-but-wrong design) | Engage: ask what happens if a category has more matching items than fit in one unfiltered page — would every matching item still get returned across multiple pages? Point toward testing a full traversal, without directly stating "that's wrong, filter first instead." |
| "I think I should filter by category before slicing by cursor and limit." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., test with a category that has more items than one page's `limit`), rather than just saying "yes that's correct." |
| "What does `Optional[str]` mean in FastAPI query params?" (syntax/library help) | Explain plainly — this is generic Python/FastAPI/Pydantic help, always allowed. |
| "Here's my repository change, does this look right?" (candidate shares a diff) | Give real review feedback: correctness of the cursor boundary, whether the category filter is applied before or after pagination, edge cases (unknown category, cursor from an unfiltered request) worth double-checking. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion for both the bug and the feature
  design, and code review are all available and cover most of what a stuck
  candidate needs across both deliverables.
- Too restrictive? No — a candidate who reasons well on either the bug or
  the feature can move through the escalation levels quickly and get a
  focused hint on the specific part they're stuck on; nothing blocks basic
  syntax/library questions.
- Rewards candidate reasoning? Yes — for the feature specifically, the
  assistant is directed to probe "what happens under full traversal /
  multiple pages" rather than confirming or denying the filter-ordering
  design outright, which keeps the candidate responsible for reaching (and
  verifying) the correct design themselves.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; both the bug
   fix and the feature require only reading Python/FastAPI code and
   running pytest.
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
