# LLM Request Router — Cache Poisoning by Fallback Responses (Interview Exercise)

**Format:** Debugging + Feature Implementation
**Timebox:** 75–90 minutes
**Level:** SWE Intern / New Grad / Backend
**Difficulty:** 8/10

## Before you start: what this exercise is (and isn't)

This project is about backend orchestration, not machine learning. The
"models" in this repository are entirely fake and deterministic — plain
Python functions that hash their input and return a string, with no real
network call, no API key, no ML model, and no randomness anywhere. You do
not need any prompt-engineering or ML background to do this exercise. What
you're actually being assessed on is asyncio control flow, retry/fallback
correctness, cache correctness, and input/output validation — the same
skills a "read this pricing function" or "fix this webhook handler"
exercise would test, just in an AI-inference-flavored setting.

## Scenario

You've just joined the platform team responsible for an internal service
that routes chat-completion requests to one of two LLM providers: a
primary model and a fallback model. It's a small internal service — you
haven't seen this code before today. A response cache sits in front of
both models so repeated identical prompts don't have to hit a model
provider again (real model calls are expensive and slow — the cache exists
to avoid paying that cost twice for the same input).

Support has escalated a customer complaint, and the platform team has a
follow-up feature request.

### 1. A bug report

> "We had a brief outage on our primary model. During that window, some
> prompts got served by the fallback model instead — expected behavior.
> But we noticed that even long after the primary model recovered and was
> healthy again, those same prompts kept getting the fallback model's
> (lower quality) cached answer instead of trying the primary again."

The team's stated policy is:

> Only primary-model responses should ever be cached. A response served by
> the fallback model represents a temporary degradation and should never
> keep being served once the primary model is healthy again.

### 2. A feature request

> "Some responses come back malformed/empty (just whitespace) and should
> never be handed back to the caller. If the primary gives us a blank
> response, that should count as a failure just like an outright error
> would — retry it, and fall back if it keeps happening. And if the
> fallback *also* comes back blank, don't just hand the caller garbage —
> fail clearly instead."

## Your task

1. Reproduce the reported bug, find its root cause, and fix it.
2. Implement the response-validation feature described above: a blank (or
   whitespace-only) model response must never be treated as a valid
   completion, for either the primary or the fallback model.
3. Add or strengthen tests so neither the bug nor an incomplete validation
   implementation can silently regress.
4. Make sure you haven't broken any other existing behavior.

This exercise has **two deliverables**, not one: the bug fix and the
feature. Budget your time for both.

## Repository layout

```
app/
  main.py                                FastAPI app entrypoint
  api/deps.py                            Wires up the clients/cache/service singletons
  api/routes/completions.py              POST /completions
  models/schemas.py                      Request/response Pydantic models
  services/llm_router_service.py         Routing, retry, fallback, and cache orchestration
  clients/fake_model_client.py           Fake, deterministic model client (no real network/ML)
  cache/response_cache.py                Small in-memory cache
tests/
  test_llm_router_service.py             Unit tests for the router service
  test_completions_api.py                API-level tests
```

## Setup

```bash
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
```

Some tests currently fail — they encode the reported bug and the missing
validation feature. The rest pass and describe behavior you must **not**
break.

## Constraints

- Keep changes scoped to the bug fix and the requested feature (plus any
  tests you add). Don't refactor unrelated code.
- Preserve the existing service and API shapes: `LLMRouterService.complete`
  still takes a single `prompt` string and returns a `CompletionResult`;
  `POST /completions` still takes `{"prompt": ...}` and returns the same
  response shape.
- The fake model clients (`app/clients/fake_model_client.py`) are correct
  and given — don't modify their behavior. Read them carefully to
  understand how `unavailable_prompts` and `blank_response_prompts` work;
  your own tests will likely need to use them.
- No real sleeping and no real network calls anywhere, including in any
  tests you add — everything in this exercise is deterministic and offline
  by design.

## AI tool policy

You may use an AI coding assistant. If you'd like it to behave the way a
real interview/OA proctor would configure it, load
`.ai/assessment-skill/SKILL.md` into your assistant as a system/project
instruction. It's written to work with any capable coding assistant, not
a specific product.

Using an assistant well is part of what's being evaluated — treat it like
a knowledgeable but junior pair programmer, not an oracle. You're expected
to reproduce the bug, form your own hypotheses, design the feature, and
verify anything the assistant suggests before you rely on it.

## Deliverables

- Your bug fix.
- Your response-validation implementation.
- Any tests you added or changed.
- Be ready to explain: what the caching bug's root cause was, how you
  found it, why your fix is correct, how you designed the validation
  feature, and what else you checked to make sure nothing else broke.
