# Team Task Board API — Update Endpoint Bug (Interview Exercise)

**Format:** AI-Assisted Debugging Assessment
**Timebox:** 45–60 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 6/10 — calibrated to Amazon-style SWE repo-debugging online
assessments (repo-based, unfamiliar code, one reported bug, public + hidden
tests). This project does not assume you've attempted any other project in
this curriculum.

## Scenario

You've just joined the internal tools team supporting a lightweight
team task board (think a stripped-down Trello). Each task belongs to a
board, has a title, a status (`todo` / `in_progress` / `done`), a priority
(`low` / `medium` / `high`), and an optional assignee. It's a small internal
service — you haven't seen this code before today.

Support has escalated a user complaint:

> "Users report that when they try to move a task from 'todo' to
> 'in_progress' using the task update feature, the request succeeds (they
> get back a 200 with the task) but the status shown afterward is still
> 'todo'. Updating the title or priority on the same task works fine."

## Your task

1. Reproduce the reported bug.
2. Find the root cause.
3. Fix it so a `PATCH` request updates every field it includes in the body —
   not just some of them.
4. Add or strengthen tests so this can't silently regress.
5. Make sure you haven't broken any other existing behavior.

You do **not** need to add any new features — this is a bug fix only.

## Repository layout

```
src/
  app.ts                              Express app setup (middleware, routes)
  server.ts                           Entrypoint — imports app, calls .listen()
  routes/tasks.ts                     Router for /boards/:boardId/tasks and /tasks/:id
  middleware/validateTaskCreate.ts    Validation for task creation
  controllers/taskController.ts       Request/response handling
  services/taskService.ts             Task business logic
  repositories/taskRepository.ts      In-memory task store (seeded with sample data)
  types.ts                            Task interface and request/response shapes
tests/
  taskService.test.ts                 Unit tests against the service directly
  tasksApi.test.ts                    HTTP-level tests against the Express app (supertest)
```

## Setup

```bash
npm install
```

## Running tests

```bash
npm test
```

Two tests currently fail (one unit-level, one HTTP-level) — both encode the
same reported bug. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to fixing this bug (plus any tests you add). Don't
  refactor unrelated code.
- Preserve the existing API request/response shapes (`GET
  /boards/:boardId/tasks`, `POST /boards/:boardId/tasks`, `PATCH
  /tasks/:id`).

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, and verify anything it
suggests before you rely on it.

## Deliverables

- Your code fix.
- Any tests you added or changed.
- Be ready to explain: what the root cause was, how you found it, why your
  fix is correct, and what else you checked to make sure nothing else
  broke.
