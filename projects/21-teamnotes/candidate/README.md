# TeamNotes (Black-Box Full-App Debugging Assessment)

**Format:** Black-Box Full-App Debugging Assessment
**Timebox:** 90 minutes
**Level:** Backend / Full-Stack, New Grad+ to Mid-level
**Difficulty:** 8.5/10 — deliberately above typical intern/new-grad OA
difficulty, calibrated for skill-building rather than a quick screen. This
project does not assume you've attempted any other project in this
curriculum.

## Scenario

TeamNotes is a small shared notes tool for a team — think a lightweight
internal wiki. A note has a title, freeform content, and a set of tags.

From the app, a user can:

- See the list of all notes, with each note's title and tags.
- Create a new note.
- Open a note to edit its title, content, and tags all at once, and save
  those changes.
- Quickly add a single tag to a note directly from the list, without opening
  the full edit view — handy for tagging something on the fly.

It's a small internal service — you haven't seen this code before today.

## Setup

```bash
cd candidate
npm install
npm run dev
```

This starts a single server (default `http://localhost:3000`, or whatever
port `PORT` is set to) that serves both the API and the frontend. Open it in
a browser and use the app the way a real user would.

If you want to start over during a session with a clean slate, either click
the **Reset** button in the UI, or:

```bash
curl -X POST http://localhost:3000/debug/reset
```

This restores the seeded starting notes and discards anything you've added
or changed. It's a testing utility, not part of the "real" product.

## Your objective

Explore the running application. Something about it doesn't behave the way
it should. Find it, reproduce it reliably, understand why it happens, and
fix it.

There's no failing test to point you at it — this is meant to simulate
encountering an unfamiliar app for the first time and needing to figure out,
through actual use, that something is wrong before you can even start
debugging it.

## Running the test suite

```bash
npm test
```

This should currently pass. That's expected, not a bug in the exercise
itself — the existing tests cover ordinary usage of the app and don't happen
to exercise the specific problem you're looking for. Once you understand
what's wrong, you're expected to add your own regression test(s) that would
have caught it.

## Constraints

- The substantive fix belongs in the backend. If your backend fix requires
  the frontend to participate correctly in a corrected contract, a small,
  necessary change there is fine — but the frontend isn't where the real
  engineering decision lives.
- Keep your changes scoped to what you actually find and fix. This isn't an
  invitation to refactor the app, add new features, or rewrite things "to be
  safe."
- Preserve the existing API request/response shapes and the general
  behavior of endpoints you aren't touching.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not a
specific product. It also governs a black-box discovery phase: until you've
described what you actually observed by using the app, don't expect it to
name or point you at what's wrong.

Using an assistant well is part of what's being evaluated — treat it like a
knowledgeable but junior pair programmer, not an oracle. You're expected to
do the exploration yourself, form your own hypotheses, and verify anything
it suggests before you rely on it.

## Deliverables

- Your fix.
- Your regression test(s).
- Be ready to explain:
  - What you observed while using the app, and how you turned that into a
    reliable, repeatable reproduction.
  - What the root cause turned out to be.
  - Why your fix is correct.
  - If you went down a path that fixed part of what you noticed before
    realizing it wasn't the whole story — what you initially tried, why it
    looked right, and why it turned out to be insufficient.
