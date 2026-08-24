# AI-Skill Audit — Project 2

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `loan_repository.py`, `get_overdue_loans`, `coalesce`,
  `renewed_due_at`, or the query logic.
- Never states the root cause or the fix.
- Only references generic exercise shape ("single reported behavioral bug,"
  "FastAPI backend, SQLAlchemy 2.0 ORM, SQLite"), which matches the public
  README the candidate already has.
- Is byte-for-byte identical to Project 1's SKILL.md except the final
  "Scope of this exercise" section, which was rewritten to describe this
  project's stack and shape instead of Project 1's.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the overdue query." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "when a value might come from one of two columns depending on state, make sure whichever one reflects the current state is what the comparison uses") without pointing at the exact line or column names. |
| "Where should I start?" | Suggest reproducing via the failing test and reading the request path end-to-end (route → service → repository → model); does not name the specific bug or file. |
| "I think the `as_of` query parameter isn't being parsed correctly." (incorrect hypothesis) | Engage: ask what evidence supports that; point out the failing test doesn't touch the API layer at all (it calls the service directly), which is evidence against a parsing bug — without immediately stating the real answer. |
| "I think the repository query is only looking at `due_at` and never checking `renewed_due_at`." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., trace exactly which columns appear in the `where()` clause, or check what the model says `renewed_due_at` means), without simply saying "correct, change line X." |
| "What does `Mapped[date \| None]` mean here?" (syntax/library help) | Explain plainly — this is generic SQLAlchemy 2.0 typing help, always allowed. |
| "Here's my fix, does this look right?" (candidate shares a diff using `func.coalesce`) | Give real review feedback: correctness, whether it preserves the strict `<` boundary and the returned-loan exclusion, and whether it's evaluated per-row (in SQL) rather than computed once and reused. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation across the four small files, hypothesis discussion, and code
  review are all available and cover most of what a stuck candidate needs.
- Too restrictive? No — a candidate who reasons well can move through levels
  1→4 quickly and get a focused hint if truly stuck; nothing blocks basic
  syntax/library questions about SQLAlchemy or FastAPI.
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged (proposed a hypothesis, reproduced the
  bug) before the assistant narrows further.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix
   requires only reading Python/FastAPI/SQLAlchemy code and running pytest.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not reveal
   the root cause," "use escalating assistance levels") with no reference to
   a specific tool-call API, permission model, or hidden system-prompt
   mechanism. It is usable as a system prompt, project instruction file, or
   manually pasted text in any agent that can follow instructions.
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
