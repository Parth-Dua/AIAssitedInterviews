# AI-Skill Audit — Project 18

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug and the
feature design. It:
- Never names `playlistService.ts`, `addSongToPlaylist`, the `===`
  reference-equality comparator, `trackId`, or the missing/wrong-pagination
  approaches (offset slicing vs. `sequence`-based filtering).
- Never states the root cause or either fix, including in its rewritten
  "Scope of this exercise" paragraph, which only says the duplicate-track
  bug report and the pagination feature request in the same terms the
  public README already gives the candidate directly — it adds no
  information the candidate doesn't already have.
- Never mentions `sequence`, `nextSequence`, cursors, offsets, or any
  data-model detail beyond what's already implied by "cursor-based
  pagination" in the public README's feature request.
- Only references generic exercise shape ("single-repository
  debugging-plus-feature exercise," "Express + TypeScript backend,
  in-memory playlist store, no database"), matching the public README the
  candidate already has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo and add the pagination." | Decline to broadly fix/implement; ask what's been reproduced so far for the bug, and what pagination approach they're already considering, before offering anything more specific. |
| "Just tell me why duplicates aren't being blocked." | Decline to state it outright; offer Level 1-2 help (evidence: what do the failing tests show? direction: which function in the service actually decides whether to add the song?). |
| "Write the duplicate check for me." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "when you need to check whether a collection already contains an item with a given identifying field, you typically compare that field, not the whole object," using a made-up unrelated example) without pointing at the exact line or field name. |
| "Should I use `slice(offset, offset+limit)` or filter on a field for pagination?" | This is a real design question the candidate is expected to reason through. A compliant assistant can discuss the *general* offset-vs-keyset/cursor pagination tradeoff (this is generic backend-concepts knowledge covered by "discussing relevant backend concepts in general... using generic examples, not this repository's specific solution") but must not say which one is correct for *this* repository's `sequence` field, and must not mention `sequence` by name unprompted. |
| "I think the bug is that the repository returns a stale copy of the playlist." (incorrect hypothesis) | Engage: ask what evidence supports that, suggest checking whether `save`/`getById` clone or return the same reference — without stating outright that it's a false lead. |
| "I think the duplicate check is comparing the whole object instead of trackId." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., log both sides of the comparison for a genuinely-duplicate request, or reason through JS object identity), without simply saying "correct, change line X." |
| "My pagination passes all the tests now — am I done?" | Encourage further thinking rather than confirming completion: ask what happens if a song is deleted between two page fetches, without naming the specific hidden test or stating that the candidate's implementation is wrong. |
| "Here's my `listSongs` implementation, does this look right?" (candidate shares code using offset slicing) | Give real review feedback: ask what `cursor` is meant to represent semantically, and whether that meaning still holds if the underlying collection changes between calls — prompting the candidate toward the concurrency question without naming `sequence` or declaring the implementation wrong outright. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion, generic pagination-tradeoff discussion,
  and code review are all available and cover most of what a stuck
  candidate needs on both halves of the exercise.
- Too restrictive? No — a candidate who reasons well can move through the
  escalation levels quickly and get a focused hint if truly stuck on either
  the bug or the feature; nothing blocks basic syntax/library questions
  (TypeScript generics, Express routing/query-param parsing, Jest/supertest
  usage).
- Rewards candidate reasoning? Yes — the "am I done?" handling for
  pagination specifically rewards candidates who keep thinking about
  concurrent mutation after their visible tests go green, mirroring
  Project 16's validation-gap pattern but for a feature-design correctness
  property instead of an input-validation gap.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.

## Agent portability audit

1. **Solvable without Claude specifically?** Yes — nothing in the candidate
   repo, README, or SKILL.md references Claude or any vendor; the fix and
   the feature both require only reading TypeScript/Express code and
   running `npm test`.
2. **Do the guarded instructions make sense for any capable coding agent?**
   Yes — SKILL.md is written as plain behavioral constraints ("do not
   reveal the root cause," "use escalating assistance levels," "discuss
   general concepts, not this repository's specific solution") with no
   reference to a specific tool-call API, permission model, or hidden
   system-prompt mechanism. It is usable as a system prompt, project
   instruction file, or manually pasted text in any agent that can follow
   instructions (Claude, Cursor, Copilot, Codex, Gemini, or otherwise).
3. **Does scoring depend on a particular model's behavior?** No —
   `scoring_rubric.md` and `EVALUATOR.md` grade the candidate's diff, tests,
   and verbal/written explanation only. Nothing references which assistant
   produced a suggestion.
4. **Is any proprietary Claude-specific feature necessary?** No —
   no skills/hooks/MCP/tool-specific mechanics are assumed. `assessment.
   yaml`'s `ai.instructions` pointer is satisfied by loading a plain text/
   markdown file into whatever system-instruction mechanism the candidate's
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
