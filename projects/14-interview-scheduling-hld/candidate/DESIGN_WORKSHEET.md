# Design Worksheet — Interview Scheduling Service

This is a scaffold, not a fill-in-the-blank quiz. There isn't one right
answer per section. Use headings as prompts for what to think through; feel
free to revise earlier sections as later ones change your mind — that's
normal design work, not a sign you did something wrong earlier. Point-form
notes, short prose, or ASCII sketches are all fine — this is a working
document, not a polished writeup.

If a section feels premature to answer in depth, a one-line placeholder
("assuming X for now, would revisit if Y") is a legitimate answer.

---

## 1. Clarifying Questions & Assumptions

What would you ask an interviewer/PM before committing to a design? For
anything you didn't get to ask, what assumption are you making instead, and
why is it reasonable?

## 2. Functional Requirements

What must the system do? Consider the core flows named in the prompt
(publishing availability, finding common free slots, booking, notifying,
rescheduling, cancelling) and anything else you think belongs in scope.

## 3. Non-Functional Requirements

What properties matter here beyond "it works"? Think about correctness,
latency/responsiveness expectations, durability, and anything specific to
this domain (e.g., what happens under concurrent access).

## 4. API Design

Sketch the main endpoints/operations a client (recruiter-facing UI, or an
internal scheduling tool) would call. Method + path + rough request/response
shape is enough — you don't need to fully specify every field.

## 5. Data Model

What are the core entities, and how do they relate? Call out anything in
the schema that's doing real work to enforce a system invariant (not just
storing data).

## 6. Component Diagram

What are the main pieces of the system and how do they talk to each other?
ASCII art, a boxes-and-arrows description in prose, or a bullet list of
components with their responsibilities are all fine — no drawing tool is
expected or required.

## 7. Request Flow

Walk through the **book-a-slot happy path** end to end, from a recruiter
asking "when is this panel free?" through a confirmed, notified booking.

Then walk through the **double-booking race**: two people try to book the
same interviewer for an overlapping time at nearly the same moment. What
actually happens in your system, step by step, and why can't both succeed?

## 8. Scaling Notes

Where is load concentrated (reads vs. writes, which entities, which
operations)? What, if anything, in your design needs to change as the
company grows toward (but not wildly past) the scale described in the
prompt? It's fine — often correct — to conclude that a given piece doesn't
need to change.

## 9. Caching Strategy

Where does caching help? Where would caching be actively dangerous for this
system, and how do you avoid that?

## 10. Reliability & Failure Handling

Pick the one or two failure modes you think matter most here (the prompt
hints at a couple) and describe what happens when they occur, and how the
system recovers or degrades gracefully.

## 11. Key Tradeoffs

Name the two or three biggest decisions in your design where you chose one
approach over a plausible alternative. What did you give up, and why was
that the right call *for this system, at this scale* — not in general?

## 12. Open Questions / What I'd Explore With More Time

What are you least sure about? What would you want to prototype, load-test,
or get more requirements clarity on before actually building this?
