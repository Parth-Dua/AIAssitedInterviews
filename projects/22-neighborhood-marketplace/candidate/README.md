# Neighborhood Marketplace (Black-Box Full-App Debugging Assessment, Final)

**Format:** Black-Box Full-App Debugging Assessment
**Timebox:** 105 minutes
**Level:** Backend / Full-Stack, New Grad+ to Mid-level
**Difficulty:** 9/10 — the hardest project in this curriculum, deliberately
above typical intern/new-grad OA difficulty, calibrated for skill-building
rather than a quick screen. This project does not assume you've attempted
any other project in this curriculum.

## Scenario

Neighborhood Marketplace is a small app for neighbors to list items they
want to sell or give away — a bookshelf, a bike, a box of gardening tools,
whatever's cluttering the garage.

From the app, a user can:

- See the list of all listings, with each listing's title, price, and
  status.
- Open a listing to see its details.
- Reserve a listing that's currently available, putting a soft hold on it
  while the buyer arranges pickup. A reservation automatically lapses on
  its own after a while if nobody follows through, making the listing
  available again for someone else.
- Purchase a listing that's currently reserved, finalizing the sale.
- Create a new listing.

It's a small local tool — you haven't seen this code before today.

## Setup

```bash
cd candidate
npm install
npm run dev
```

This starts a single server (default `http://localhost:3000`, or whatever
port `PORT` is set to) that serves both the API and the frontend. Open it in
a browser and use the app the way a real user would.

## Testing tools

The app includes a small "Testing tools" panel, plus two endpoints behind
it, purely to make this app easier to explore and test — they are not part
of the "real" product:

```bash
# Restore the seeded starting listings and discard anything you've added
# or changed.
curl -X POST http://localhost:3000/debug/reset

# Move the app's internal clock forward by the given number of
# milliseconds, so you can explore time-based behavior (like a reservation
# lapsing) without actually waiting.
curl -X POST http://localhost:3000/debug/advance-time \
  -H 'Content-Type: application/json' \
  -d '{"advanceByMs": 600000}'
```

Both are also available as buttons in the UI itself.

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
  - Why your fix is correct and complete — including why a fix that only
    narrows the window in which the problem is observable, without
    addressing why it happens at all, would be insufficient.
  - If you went down a path that resolved part of what you noticed before
    realizing it wasn't the whole story — what you initially tried, why it
    looked right, and why it turned out to be incomplete.
