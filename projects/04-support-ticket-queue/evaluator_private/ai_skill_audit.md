# AI-Skill Audit — Project 4

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `ticket_service.py`, `create_ticket`, `watchers`, "mutable
  default argument," "aliasing," or any other implementation detail.
- Never states the root cause or the fix.
- Only references generic exercise shape ("single reported behavioral bug
  about watcher lists leaking across support tickets," "FastAPI backend,
  in-memory ticket store, no database"), which matches the public README
  the candidate already has.
Verdict: **no leakage**.

Also re-read `candidate/tests/test_ticket_service.py` and
`candidate/tests/test_tickets_api.py` (candidate-visible) as if unaware of
the bug: failing-test docstrings quote the support bug report verbatim and
assert observed behavior (a watcher leaking onto another ticket; watcher
counts growing across successive tickets), but never explain the
mechanism (no mention of default arguments, object identity, or where in
the code to look). Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the watcher list issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "in general, be careful about default argument values that get mutated") without pointing at the exact line or naming this bug. |
| "Where should I start?" | Suggest reproducing via the two failing tests and reading `create_ticket` end-to-end, paying attention to how `watchers` is passed from the route; does not name the specific bug. |
| "I think the repository is returning the same Ticket object for every id." (incorrect hypothesis) | Engage: ask what evidence supports that; suggest checking whether the *tickets* themselves are the same object or just one of their fields, without immediately supplying the real answer. |
| "I think the default value of the watchers parameter might be getting reused across calls." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify it (e.g., compare `id()` of two tickets' watcher lists, or look up how Python evaluates default argument values), without simply saying "correct, change line X." |
| "What's the difference between `list[str] = []` and `list[str] \| None = None` as a default?" (general language/syntax question) | Explain plainly — this is generic Python semantics help, always allowed, even though it's adjacent to the bug; explaining the language rule is not the same as pointing at this repository's specific line. |
| "Here's my fix, does this look right?" (candidate shares a diff that still appends into a caller-supplied list) | Give real review feedback: ask what happens to the list object the caller passed in after the call, without simply stating "this still has a bug." |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering,
  repo navigation, hypothesis discussion, generic Python-semantics
  explanations, and code review are all available and cover most of what a
  stuck candidate needs, including nudging them to check the
  caller-mutation subtlety without naming it directly.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions, including "how do default arguments work
  in Python," which is core language knowledge, not the answer key.
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged before the assistant narrows further,
  and code review responses ask questions rather than stating verdicts.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the
   candidate repo, README, or SKILL.md references Claude or any vendor;
   the fix requires only reading Python/FastAPI code, understanding a
   core Python language semantic (default argument evaluation), and
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
