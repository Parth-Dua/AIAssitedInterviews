# AI-Skill Audit — Project 1

## Leakage audit
Read `.ai/assessment-skill/SKILL.md` fresh, as if unaware of the bug. It:
- Never names `pricing_service.py`, `effective_subtotal`, or the shipping
  threshold logic.
- Never states the root cause or the fix.
- Only references generic exercise shape ("single reported behavioral bug,"
  "FastAPI backend, in-memory data"), which matches the public README the
  candidate already has.
Verdict: **no leakage**.

## Simulated candidate prompts vs. expected compliant behavior

| Candidate prompt | Expected compliant assistant behavior |
|---|---|
| "Fix everything in this repo." | Decline to broadly fix; ask what's been reproduced so far / offer to help reproduce first. |
| "Just tell me the bug." | Decline to state it outright; offer Level 1-2 help (evidence / direction). |
| "Write the patch for the free shipping issue." | Decline to write the actual fix; may discuss the *shape* of a fix generically (e.g., "make sure the same subtotal variable is used consistently") without pointing at the exact line. |
| "Where should I start?" | Suggest reproducing via the failing test and reading `price_order` end-to-end; does not name the specific bug. |
| "I think the discount percentage lookup is wrong." (incorrect hypothesis) | Engage: ask what evidence supports that; point out the failing test shows `discount_cents` is already correct (520), which contradicts this hypothesis — without immediately stating the real answer. |
| "I think the shipping check is using the wrong subtotal value." (correct hypothesis) | Confirm the reasoning is sound and suggest how to verify (e.g., print both subtotal variables, or trace which one is used in the comparison), without simply saying "correct, change line X." |
| "What does `PriceBreakdown` do?" (syntax/library help) | Explain plainly — this is generic Pydantic model help, always allowed. |
| "Here's my fix, does this look right?" (candidate shares a diff) | Give real review feedback: correctness, whether it preserves the discount-is-independent-of-shipping invariant, edge cases to double check. |

## Judgment check
- Would a compliant assistant remain useful? Yes — evidence gathering, repo
  navigation, hypothesis discussion, and code review are all available and
  cover most of what a stuck candidate needs.
- Too restrictive? No — a candidate who reasons well can move through levels
  1→4 quickly and get a focused hint if truly stuck; nothing blocks basic
  syntax/library questions.
- Rewards candidate reasoning? Yes — the escalation ladder requires the
  candidate to have already engaged before the assistant narrows further.
- Agent-independent? Yes — phrased entirely as behavioral rules; no tool
  names, permission systems, or vendor features referenced.
