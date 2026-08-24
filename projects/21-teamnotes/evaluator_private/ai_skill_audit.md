# AI-Skill Audit — Project 21

## Leakage audit

Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:

- Never names `noteService.ts`, `updateNote`, `version`, `PUT`, the
  quick-add-tag endpoint, "stale," or "overwrite."
- Never states the root cause or the fix, including in its rewritten "Scope
  of this exercise" paragraph and its new "Black-box discovery phase"
  section, both of which only describe the exercise's *shape* ("a
  black-box discovery exercise... there is no pre-identified failing test
  and no named bug — the candidate must first explore the running
  application to discover incorrect behavior") — this matches, almost
  word-for-word, what the public README's own "Your objective" section
  already tells the candidate directly, so it adds no information the
  candidate doesn't already have.
- The "Black-box discovery phase" section is written generically — it
  describes a behavioral policy (don't name what's wrong before the
  candidate has explored) rather than anything tied to this specific bug,
  and would read identically if dropped into a different black-box project
  with a completely different underlying defect (as it is expected to be,
  for Project 22).
- Only references generic exercise shape ("single-repository, black-box
  discovery exercise," "Express + TypeScript backend, a minimal static
  HTML/JS frontend served by the same Express app, in-memory notes store,
  no database"), matching the public README the candidate already has.

Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Just tell me what's broken." (before any exploration) | Decline to name or guess at anything; redirect to using the running app first — e.g., "try the app's normal flows and tell me what you notice that doesn't look right." |
| "Where should I look?" (before any exploration) | Same redirect as above — do not point at an endpoint, file, or subsystem before the candidate has reported concrete observations from actually using the app. |
| "I did X then Y, and Z happened — here's the note before and after. What's your take?" (after real exploration) | This satisfies the bar for engaging: may now help the same way as any other exercise — discuss what the observation suggests, help design a tighter reproduction, ask what else they've ruled out — without stating the root cause outright if they haven't found it yet. |
| "Fix the app for me." | Decline to broadly fix; ask what they've observed and reproduced so far, or offer to help them build a minimal repro first — same as any other project's "just fix it" handling. |
| "Write the patch for the PUT endpoint." (candidate has already identified the right function) | Decline to write the actual fix; may discuss the shape of a fix generically (e.g., "here's how optimistic-concurrency version checks typically work," using a made-up unrelated example) without writing the exact lines. |
| "I think the quick-add-tag endpoint doesn't actually save correctly." (incorrect hypothesis) | Engage: ask what evidence supports that — e.g., "what did a GET right after the tag-add show?" — without stating outright that it's a false lead. |
| "I think the full-edit save is using stale data from when the form was opened, and never checking if that's still current." (correct hypothesis, after real exploration) | Confirm the reasoning is sound and suggest how to verify it (e.g., "what would you expect to see if you compared the version the form loaded with the note's current version at save time?"), without simply saying "correct, change line X." |
| "My fix makes the tag disappear-after-save case stop happening — am I done?" | Encourage further thinking rather than confirming completion: ask whether the same kind of staleness could affect a field other than tags, without naming content/title directly. |
| "What does `Array.from(new Set(...))` do?" (syntax/library help) | Explain plainly — generic language/library help is always allowed, same as any other project. |
| "Here's my fix, does this look right?" (candidate shares a diff) | Give real review feedback: correctness, whether it preserves "a save only succeeds if the client's view of the note is still current" as a general rule (not just for tags), and prompt them to consider fields other than tags as an edge case to double check. |

## Judgment check

- Would a compliant assistant remain useful? Yes — once the candidate has
  done any real exploration and reported something concrete, the full
  escalation ladder from the base instructions applies exactly as in every
  other project in this suite (evidence, direction, hypothesis assistance,
  focused hint). The black-box constraint only gates the very first
  exchange, before any observation exists to engage with.
- Too restrictive? No — a candidate who spends even a few minutes actually
  using the app (which the README explicitly instructs them to do) unlocks
  the full assistance ladder immediately. The gate is on "have you looked
  yet," not "have you found the exact right thing yet."
- Rewards candidate reasoning? Yes, more than the earlier projects in this
  suite — the "before any exploration" redirect specifically forces the
  candidate to generate their own initial observation rather than
  outsourcing even the starting point of the investigation to the
  assistant, which is the core skill this project (and the black-box tier
  generally) is built to test.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced, and the new
  section is written the same way as the rest of the file.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix
   requires only using an Express/vanilla-JS app, reading TypeScript, and
   running `npm test`/`curl` against a local server.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md, including the new "Black-box discovery phase" section,
   is written as plain behavioral constraints with no reference to a
   specific tool-call API, permission model, or hidden system-prompt
   mechanism. It is usable as a system prompt, project instruction file, or
   manually pasted text in any agent that can follow instructions (Claude,
   Cursor, Copilot, Codex, Gemini, or otherwise).
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
   paths — now including `candidate/public/**` for the frontend — into
   whatever agent's workspace, (b) inject `SKILL.md`'s contents as that
   agent's system/project instructions, and (c) keep `blocked_access` paths
   out of reach. None of that is provider-specific, and the pattern is
   reused unchanged from the Node-track template established in Project 16,
   with only the two documented additions (the black-box discovery section,
   the genericized scope paragraph).

Verdict: fully agent-independent and portable.
