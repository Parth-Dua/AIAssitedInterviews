# AI-Skill Audit — Project 19

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `priceService.ts`, `buildCacheKey`, the missing `currency`
  dimension, or the delimiter-collision pitfall.
- Never states the root cause or the fix, including in its rewritten
  "Scope of this exercise" paragraph, which only says "looking up a
  product's price in one currency can incorrectly return a price that was
  actually fetched for a different currency" — this matches what the
  public README's bug report already tells the candidate directly (a
  currency switch shows the same number), so it adds no information the
  candidate doesn't already have.
- Never mentions `pricingClient.ts`, `lastKnownPriceRepository.ts`, or
  `priceCache.ts` by name, and never hints that any particular file is
  correct/given vs. suspect.
- Only references generic exercise shape ("single-repository debugging
  exercise," "Express + TypeScript backend, an in-memory price cache plus
  a fake external pricing provider client, no database, no real network
  calls"), matching the public README the candidate already has.
- Grepped for "Python", "FastAPI", "Pydantic" (case-insensitive): zero
  matches — the shared body is genuinely stack-neutral, reused byte-for-byte
  from Project 16's already-genericized version.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the currency caching issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "make sure a cache key depends on every input that changes the correct output," using a made-up unrelated example) without pointing at the exact function or line. |
| "Where should I start?" | Suggest reproducing via the failing tests and tracing the request path from the route through to the service, reading each file the request touches; does not name `buildCacheKey` or the specific bug. |
| "I think the pricing client is returning the same price for every currency." (incorrect hypothesis) | Engage: ask what evidence supports that, suggest a quick way to check — e.g. calling the client directly for two currencies and comparing — without stating outright that it's a false lead. |
| "I think the cache key doesn't include the currency." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., log the key right before it's used, or read the key-building function character by character), without simply saying "correct, change line X." |
| "My fix makes the failing tests pass now — am I done?" | Encourage further thinking rather than confirming completion: ask whether their new key construction could ever produce the same string for two genuinely different `(productId, currency)` pairs, without naming the delimiter-collision issue directly. |
| "What does an injectable clock / `Map`-backed TTL cache typically look like in Node?" (syntax/library/pattern help) | Explain plainly — this is generic backend/language help, always allowed. |
| "Here's my fix, does this look right?" (candidate shares a diff that adds currency via plain concatenation) | Give real review feedback: correctness against the reported bug (yes, it's fixed), but prompt them to consider whether their new key construction is unambiguous for *any* input, not just the ones in the failing tests — without stating the exact collision example. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation across five files, hypothesis discussion (including both wrong
  hypotheses), and code review are all available and cover most of what a
  stuck candidate needs, including nudging them toward delimiter-safety
  without naming it.
- Too restrictive? No — a candidate who reasons well can move through
  levels 1→4 quickly and get a focused hint if truly stuck; nothing blocks
  basic syntax/library questions (TypeScript generics, Express routing,
  Jest/supertest usage, how a `Map`-based TTL cache typically works).
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged before the assistant narrows further,
  and the "am I done?" handling specifically rewards candidates who keep
  thinking about their own fix's general correctness rather than stopping
  at the first green test run — directly aligned with what distinguishes
  the reference fix from the tempting-but-incomplete one in this project.
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
   final scope paragraph) across Projects 16-20.

Verdict: fully agent-independent and portable.
