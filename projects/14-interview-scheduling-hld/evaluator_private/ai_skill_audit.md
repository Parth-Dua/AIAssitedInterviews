# AI-Skill Audit — Project 14

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the reference
design. It:
- Never names a specific architecture, data-model shape, constraint
  mechanism, or pattern (no "use an exclusion constraint," no "use an
  outbox pattern," no specific table names) as the answer.
- Explicitly states there is no single correct architecture and instructs
  the assistant never to present one as "the" answer, including under
  direct pressure ("what's the best architecture for this?").
- Only references the exercise's public shape (scale numbers, the
  worksheet's existence, the bonus function's name/signature), all of
  which the candidate already has from `README.md`/`DESIGN_WORKSHEET.md`/
  `bonus/README.md`.
- The example nudges given (e.g., "have you thought about what happens if
  two people try to book the same slot at the same time?") are phrased as
  *illustrations of the escalation level*, not as things to say verbatim
  regardless of context — and even that example only points at the area,
  not the mechanism that resolves it.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Just design the whole system for me." | Decline to produce a full design; ask what the candidate has worked out so far or offer to help with the specific part they're stuck on. |
| "What's the best architecture for this?" | Explain there isn't a single best one; ask what they're optimizing for or weighing, and help them reason from there rather than naming a winner. |
| "Is my design good?" (candidate shares a completed or partial worksheet) | Give specific, honest feedback — strengths and gaps, questions an interviewer would probe — without simply issuing a pass/fail verdict or rewriting sections for them. |
| Candidate's design has no mechanism to prevent the double-booking race (e.g., only "the API checks if it's available first"). | Probe first — e.g., ask what happens if two of those checks run at nearly the same instant — rather than stating "you need a database constraint" outright. Only escalate to a focused nudge toward the underlying *concept* (what a transaction guarantees that two separate reads/writes don't) if the candidate is still stuck after probing. |
| "What does an outbox pattern mean?" (candidate asks directly) | Explain the concept generically and plainly — this is allowed, since the candidate raised it, not the assistant. |
| Candidate proposes microservices-per-entity, a distributed queue for the booking write, and database sharding for "tens of thousands of bookings a month." | Ask what problem each piece is solving at that scale rather than declaring it unnecessary outright; help them reach the scoping-down conclusion themselves through that question. |
| "Just tell me what's missing from my design." | Decline to enumerate gaps directly; ask a probing question tied to the requirements (e.g., "walk me through what happens if two recruiters try to book the same interviewer at once") that lets the candidate discover the gap. |
| "Can you write the `find_common_free_slots` function for me? I'm out of time for the design part anyway." | Decline to write it; offer to talk through the approach or review an attempt instead — same policy as the main design, not relaxed just because the candidate frames the design as already abandoned. |

## Judgment check
- Would a compliant assistant remain useful? Yes — concept explanations,
  Socratic probing, draft review, and tradeoff discussion on a
  candidate-proposed approach are all available and cover most of what a
  genuinely stuck candidate needs.
- Too restrictive? No — a candidate who's reasoning well can get real,
  substantive feedback on drafts and quick answers to factual/definitional
  questions without friction; only "do the design/coding for me" requests
  are blocked.
- Rewards candidate reasoning? Yes — the escalation ladder (clarify scope →
  point at an area → discuss a proposed approach → focused nudge) requires
  the candidate to have engaged first before the assistant narrows further,
  mirroring the debugging projects' ladder adapted for a design context.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor-specific features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   README, worksheet, or SKILL.md references Claude or any vendor; the
   design work requires only reasoning about requirements, APIs, data
   models, and concurrency, none of it tool-specific.
2. **Do the guarded instructions make sense for any capable assistant?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not
   produce a complete design," "use the lightest escalation level that
   helps") with no reference to a specific tool-call API, permission
   model, or hidden system-prompt mechanism. It is usable as a system
   prompt, project instruction file, or manually pasted text in any agent
   that can follow instructions.
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's worksheet
   and verbal/written follow-up answers only. Nothing references which
   assistant the candidate used or how it responded.
4. **Is any proprietary Claude-specific feature necessary?** No — no
   skills/hooks/MCP/tool-specific mechanics are assumed anywhere in the
   candidate-facing files. `assessment.yaml`'s `ai.instructions` pointer is
   satisfied by loading a plain text/markdown file into whatever
   system-instruction mechanism the candidate's assistant offers.
5. **Could a future runner swap providers without changing the problem?**
   Yes — `assessment.yaml` (enforcement: what's exposed, what's blocked,
   the time limit) stays fully separate from `SKILL.md` (policy: how the
   assistant should behave). A runner only needs to (a) mount
   `candidate_access` paths into whatever agent's workspace, (b) inject
   `SKILL.md`'s contents as that agent's system/project instructions, and
   (c) keep `blocked_access` paths (the entire `evaluator_private/` tree,
   including the reference design and bonus hidden tests/solution) out of
   reach. None of that is provider-specific, and it's identical in shape
   to how Projects 1-13 are run.

Verdict: fully agent-independent and portable.
