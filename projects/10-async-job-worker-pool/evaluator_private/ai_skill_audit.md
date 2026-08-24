# AI-Skill Audit — Project 10

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `job_batch_tracker.py`, `mark_job_done`, `_remaining`, or the
  `await`-between-read-and-write mechanism.
- Never states the root cause, the fix, or the tempting-but-wrong
  per-call-lock trap.
- Only references generic exercise shape ("single reported behavioral
  bug," "FastAPI backend, in-memory state, `asyncio` throughout," "no
  database, no real threads or processes, no real network I/O"), all of
  which matches the public README the candidate already has. The one
  reassurance it adds beyond Project 1's text — that this is real
  `asyncio` concurrency, not multi-threading/multi-processing, and
  requires no distributed-systems expertise — is a scope clarification,
  not a hint about where the bug lives.
- Candidate-facing code (`app/**`) contains no comments or docstrings that
  narrate the bug's location or mechanism. `JobBatchTracker`'s class
  docstring states only the intended contract ("finalized exactly once,
  at the moment the last job finishes") — the same style as Project 1's
  pricing-rules docstring, which states the rule the buggy code violates
  without describing the violation itself.

Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the batch-completion issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "in general, if you read a shared value, do something async, then write it back, two callers can interleave around that — you'd either avoid awaiting in between or protect the section with something shared") using a made-up unrelated example, without pointing at the exact line or file. |
| "Where should I start?" | Suggest reproducing via the failing test and reading the execution path (`route → JobService → worker_loop → JobBatchTracker`) end-to-end; does not name the specific bug. |
| "I think the worker loop is calling mark_job_done too few times." (incorrect hypothesis) | Engage: ask what evidence supports that; point out the passing `test_mark_job_done_called_exactly_job_count_times` test already shows the call count is exactly right, which contradicts this hypothesis — without immediately stating the real answer. |
| "I think there's an await between reading and writing the remaining counter, so two workers can race." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., add a print/log of `remaining` on each read and write, or trace which line resumes when), without simply saying "correct, remove the await on line X." |
| "I added `asyncio.Lock()` inside `mark_job_done` and it still fails — why?" (candidate has landed on the tempting-wrong fix) | Do not immediately reveal "the lock has to be shared." Ask the candidate what specifically the lock is supposed to be preventing two calls from doing, and whether two different calls to `mark_job_done` could ever end up holding *different* Lock objects — nudge them toward inspecting where the `Lock()` is constructed, without stating the fix outright. This is Level 3-4 hypothesis/focused-hint territory, not a free answer. |
| "What does `asyncio.Queue.get()` do if the queue is empty vs. non-empty?" (syntax/library help) | Explain plainly — this is generic asyncio/library help, always allowed, and is exactly the kind of question that helps a candidate correctly rule out `JobQueue` as the cause. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering,
  repo navigation, hypothesis discussion (including for the specific
  "I added a lock, why doesn't it work" dead end), and code review are all
  available and cover most of what a stuck candidate needs.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions about `asyncio` primitives.
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged (including having tried and observed
  the failure of their own fix attempt) before the assistant narrows
  further, which is especially important for the per-call-lock trap: the
  assistant must not just say "that lock doesn't work because X," it must
  make the candidate examine why.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the
   candidate repo, README, or SKILL.md references Claude or any vendor;
   the fix requires only reading Python/`asyncio`/FastAPI code and running
   `pytest`.
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
   produced a suggestion, and the empirical determinism checks (5+ runs,
   byte-identical) are properties of CPython's `asyncio` event loop, not
   of any AI model.
4. **Is any proprietary Claude-specific feature necessary?** No —
   no skills/hooks/MCP/tool-specific mechanics are assumed.
   `assessment.yaml`'s `ai.instructions` pointer is satisfied by loading a
   plain text/markdown file into whatever system-instruction mechanism the
   candidate's assistant offers.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths into whatever agent's workspace, (b) inject `SKILL.md`'s contents
   as that agent's system/project instructions, and (c) keep
   `blocked_access` paths out of reach. None of that is provider-specific,
   and none of it depends on any particular Python version's `asyncio`
   internals beyond what's already pinned by `requires-python` in
   `pyproject.toml`.

Verdict: fully agent-independent and portable.
