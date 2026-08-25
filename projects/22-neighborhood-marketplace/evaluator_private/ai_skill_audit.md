# AI-Skill Audit — Project 22

## Leakage audit

Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:

- Never names `listingService.ts`, `getListings`, `listingsCache.ts`,
  `listingRepository.ts`, `reservedUntil`, "cache," "invalidate," "TTL," or
  any other term that would narrow the search toward the specific
  mechanism.
- Never states the root cause or the fix, including in its rewritten
  "Scope of this exercise" paragraph — that paragraph only describes the
  exercise's *shape* and stack ("Express + TypeScript backend, a minimal
  static HTML/JS frontend served by the same Express app, in-memory
  marketplace listings, an injectable/advanceable clock exposed through a
  debug endpoint, no database") plus a generic note that the reasoning
  will "span more of the backend than a typical debugging exercise" —
  which describes difficulty calibration, not the bug itself, and matches
  what the public README's own difficulty rating and "Your objective"
  section already tell the candidate directly.
- The "Black-box discovery phase" section is copied verbatim from Project
  21 and remains fully generic — it describes a behavioral policy (don't
  name what's wrong before the candidate has explored) rather than
  anything tied to this specific bug, and would read identically dropped
  into either project or any future black-box project with a completely
  different underlying defect.
- Only references generic exercise shape, matching the public README the
  candidate already has; the domain (marketplace listings, reservations,
  purchases) is named only because the README already names it, not
  because the SKILL.md adds any new detail about it.

Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Just tell me what's broken." (before any exploration) | Decline to name or guess at anything; redirect to using the running app first — e.g., "try reserving something, using the testing tools, and tell me what you notice that doesn't look right." |
| "Where should I look?" (before any exploration) | Same redirect as above — do not point at an endpoint, file, or subsystem before the candidate has reported concrete observations from actually using the app. |
| "I reserved a listing, advanced time past the window, and the detail page shows available but the list still shows reserved. What's your take?" (after real exploration) | This satisfies the bar for engaging: may now help the same way as any other exercise — discuss what the observation suggests, help design a tighter/scripted reproduction, ask what else they've ruled out — without stating the root cause outright if they haven't found it yet. |
| "Fix the app for me." | Decline to broadly fix; ask what they've observed and reproduced so far, or offer to help them build a minimal repro first — same as any other project's "just fix it" handling. |
| "Write the patch for the getListings function." (candidate has already identified the right function) | Decline to write the actual fix; may discuss the shape of a fix generically (e.g., "here's how you'd typically bound how long a cached snapshot is trusted," using a made-up unrelated example) without writing the exact lines. |
| "I think the reservation expiry timing is just wrong — maybe an off-by-one." (incorrect hypothesis) | Engage: ask what evidence supports that — e.g., "what did the detail view show immediately after advancing time?" — without stating outright that it's a false lead. |
| "I think the list is cached and doesn't know when a reservation expires on its own, even though it knows when someone explicitly reserves or purchases something." (correct hypothesis, after real exploration) | Confirm the reasoning is sound and suggest how to verify it (e.g., "what would you expect to see if you compared what each of those two read paths actually does?"), without simply saying "correct, change line X." |
| "I shortened the cache lifetime and now I can't reproduce the bug anymore in the browser — am I done?" | Do not confirm completion. Ask how they'd verify that with the app's own deterministic time-control tool rather than casual manual testing, and whether the underlying mechanism (not just how often it's observable) has actually changed — without naming "TTL" or the specific insufficiency outright if the candidate hasn't identified it themselves. |
| "What does `Array.from(...).map(...)` do?" (syntax/library help) | Explain plainly — generic language/library help is always allowed, same as any other project. |
| "Here's my fix, does this look right?" (candidate shares a diff) | Give real review feedback: correctness, whether it uses the app's own injectable clock rather than real wall-clock time, whether it's tested against a scenario with multiple listings (only one expiring), and prompt them to consider whether it holds under deterministic time advances, not just casual manual testing. |

## Judgment check

- Would a compliant assistant remain useful? Yes — once the candidate has
  done any real exploration and reported something concrete, the full
  escalation ladder from the base instructions applies exactly as in every
  other project in this suite (evidence, direction, hypothesis assistance,
  focused hint). The black-box constraint only gates the very first
  exchange, before any observation exists to engage with.
- Too restrictive? No — a candidate who spends even a few minutes actually
  using the app and its debug time-control tool (which the README
  explicitly documents and points to) unlocks the full assistance ladder
  immediately. The gate is on "have you looked yet," not "have you found
  the exact right thing yet."
- Rewards candidate reasoning? Yes, more than Project 21 — the specific
  guidance on the "am I done?" prompt (after a TTL-shortening partial fix)
  is written to push the candidate toward their own deterministic
  verification rather than accepting a symptom-level "I can't reproduce it
  casually anymore" as evidence of correctness, which is precisely the
  reasoning skill this project is built to test.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced, matching the
  rest of the file.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix
   requires only using an Express/vanilla-JS app, reading TypeScript, and
   running `npm test`/`curl` against a local server, including its debug
   time-control endpoint.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md, including the "Black-box discovery phase" section
   carried over unchanged from Project 21, is written as plain behavioral
   constraints with no reference to a specific tool-call API, permission
   model, or hidden system-prompt mechanism. It is usable as a system
   prompt, project instruction file, or manually pasted text in any agent
   that can follow instructions (Claude, Cursor, Copilot, Codex, Gemini, or
   otherwise).
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff,
   tests, and verbal/written explanation only. Nothing references which
   assistant produced a suggestion, and the "verify the candidate's own
   test actually catches the bug" step in `EVALUATOR.md` is a mechanical
   check (revert the fix, run their test, confirm it fails) that any
   evaluator can perform regardless of tooling.
4. **Is any proprietary Claude-specific feature necessary?** No —
   no skills/hooks/MCP/tool-specific mechanics are assumed for running the
   exercise itself. `assessment.yaml`'s `ai.instructions` pointer is
   satisfied by loading a plain text/markdown file into whatever
   system-instruction mechanism the candidate's assistant offers. The
   toolchain (`npm`/`tsc`/`jest`/`ts-jest`/a static file server) is plain
   Node.js tooling, not tied to any AI vendor.
5. **Could a future runner swap providers without changing the problem?**
   Yes — separating `assessment.yaml` (enforcement: what's exposed, what's
   blocked, the time limit) from `SKILL.md` (policy: how the assistant
   should behave) means a runner only needs to (a) mount `candidate_access`
   paths — including `candidate/public/**` for the frontend — into
   whatever agent's workspace, (b) inject `SKILL.md`'s contents as that
   agent's system/project instructions, and (c) keep `blocked_access` paths
   out of reach. None of that is provider-specific, and the pattern is
   reused unchanged from the Node-track template established in Project 16
   and carried through Project 21, with only the domain-specific paragraph
   in SKILL.md's final section differing between the two black-box
   projects.

Verdict: fully agent-independent and portable.
