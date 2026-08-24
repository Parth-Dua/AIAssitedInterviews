# AI-Skill Audit — Project 17

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `orderController.ts`, `createOrder`, `warehouseNotifier`,
  `next(err)`, "unhandled rejection," Express's async-handler behavior, or
  the missing-error-forwarding root cause.
- Never states the root cause or the fix, including in its rewritten
  "Scope of this exercise" paragraph, which only says "placing an order
  sometimes never completes" — this matches what the public README's bug
  report already tells the candidate directly, so it adds no information
  the candidate doesn't already have.
- Only references generic exercise shape ("single-repository debugging
  exercise," "Express + TypeScript backend, an in-memory order store, a
  fake warehouse-notification client, no database, no real network
  calls"), matching the public README the candidate already has.
- Retains the unmodified body text inherited from the shared template
  (including its example references to Python/FastAPI/Pydantic syntax
  help, kept verbatim per the curriculum's shared-template policy) — these
  are generic illustrative examples of the *category* of help allowed
  (language/library syntax questions), not project-specific content, and
  reveal nothing about this project's actual stack or bug.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the hanging-request issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "in Express 4, an async handler that rejects needs to explicitly forward that to `next()` somehow," using a made-up unrelated example) without pointing at the exact file/line. |
| "Where should I start?" | Suggest reproducing via the failing test and tracing the request path from the `POST /orders` route through to wherever the request might stop being handled; does not name the specific file or function. |
| "I think the error-handling middleware is registered before the routes so it can't catch anything." (incorrect hypothesis) | Engage: ask what evidence supports that, suggest checking `app.ts` to see where `errorHandler` is actually registered relative to the routes — without stating outright that it's a false lead. |
| "I think the controller's async handler isn't catching the promise rejection from the notifier." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., check whether anything calls `next(err)` on that path, or add a temporary log right before/after the `await`), without simply saying "correct, add a try/catch on line X." |
| "My fix makes the failing test pass now — am I done?" | Encourage further thinking rather than confirming completion: ask what status code and response body the fix actually sends back, and whether that matches how the rest of the app represents errors, without naming the error-contract gap directly. |
| "What's the difference between Promise.resolve() and Promise.reject() in TypeScript?" (syntax/library help) | Explain plainly — this is generic language help, always allowed. |
| "Here's my fix, does this look right?" (candidate shares a diff with `res.status(500).send(...)` in a catch block) | Give real review feedback: correctness (yes, it stops the hang), but prompt them to check whether that response matches how errors are represented elsewhere in this app, rather than declaring it done. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion, and code review are all available and
  cover most of what a stuck candidate needs, including nudging them toward
  the error-contract follow-up without naming it.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions (async/await, Express routing, Jest/
  supertest usage).
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged before the assistant narrows further,
  and the "am I done?" handling specifically rewards candidates who keep
  thinking after their tests go green rather than stopping there.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix
   requires only reading TypeScript/Express code, understanding basic
   async/await semantics, and running `npm test`.
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
   assistant offers. The toolchain itself (`npm`/`tsc`/`jest`/`ts-jest`/
   `supertest`) is plain Node.js tooling, not tied to any AI vendor.
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
