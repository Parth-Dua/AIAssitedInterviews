# Interview Follow-Up Questions (private)

1. **Why can't `FlagRule.decide` just return a plain `bool` — what would
   break?**
   Strong answer: a single rule frequently has no opinion at all about a
   given context (a deny-list rule has nothing to say about a user who
   isn't on its list). If `decide` were forced to return `True`/`False`
   only, every rule would have to fabricate an answer it doesn't actually
   hold, which makes "evaluate rules in priority order, first one with a
   real opinion wins" impossible to express cleanly — you'd need some other
   out-of-band signal (a sentinel value, an extra return field, an
   exception) to represent "doesn't apply here." `None` is the natural
   third state, and it's exactly what lets `RuleChain` be a simple
   "first-non-None-wins" loop.

2. **Why is Python's built-in `hash()` unsafe for this use case?**
   Strong answer: `hash()` on strings is deliberately randomized per
   process (seeded by `PYTHONHASHSEED`, on by default since Python 3.3, as
   a hash-flooding DoS mitigation for dict/set). That means the same
   `(flag_name, user_id)` pair can map to a different bucket every time the
   process restarts, which directly violates "the same user always gets the
   same result, forever." A stable hash like `hashlib.sha256` doesn't have
   this problem — same input, same digest, on any machine, in any process,
   forever. If the candidate used `hash()`, ask them to predict what would
   happen to a specific user's rollout status across two separate
   deployments of the same service — a strong candidate should immediately
   recognize the failure mode once asked, even if they missed it while
   coding.

3. **How would you extend this to support percentage rollouts that are
   correlated across MULTIPLE flags for the same user (e.g. an experiment
   framework where a user's "bucket" for one experiment should be
   consistent with — or deliberately independent of — their bucket in
   another experiment), without duplicating the bucketing logic?**
   Strong answer: the current design already keys the hash on `flag_name +
   user_id`, so two *different* flags naturally get independent buckets for
   the same user (that's the Part 1 requirement). For **correlated**
   buckets across flags (e.g. all experiments in one "layer" should
   co-vary), you'd introduce a separate `layer_key` (or `experiment_key`)
   that's shared by every flag/experiment that should correlate, and hash
   on `layer_key + user_id` instead of `flag_name + user_id` for those —
   letting the caller choose the correlation key rather than baking
   "correlated" or "independent" into the hashing function itself. Bonus:
   recognizing this is a strong argument for keeping the bucketing helper
   (`_bucket_for` or equivalent) as a small, reusable, string-keyed
   function that any future flag/rule/experiment abstraction can call with
   whatever key it needs, rather than hardcoding `flag_name` as the only
   possible correlation axis inside `PercentageRolloutFlag` itself.

4. **Walk me through what happens, step by step, for a single call to
   `RuleChain.is_enabled` when none of the rules have an opinion.**
   Strong answer: iterate the rule list in order; call `.decide(context)`
   on each; every one returns `None`; the loop finishes without returning;
   fall back to and return `self._default`. `RuleChain` itself never
   computes an allow/deny decision — it only routes to whichever rule
   decides, or to the configured default if nobody does.

5. **Why did (or didn't) your Part 1 design need to change when you read
   the Part 2 requirements?**
   Strong answer: `PercentageRolloutFlag` itself didn't need behavioral
   changes — at most, its bucketing math needed to be pulled into a small
   shared helper (or exposed via composition) so `PercentageRolloutRule`
   could reuse it instead of re-deriving it. If the candidate *did* have to
   rewrite more than that, ask specifically what had to change and why — a
   common honest answer is "I'd hardcoded the hashing inline in
   `is_enabled` with no way to call it from outside," which is itself
   useful signal about what to probe further (was the class designed with
   any reuse in mind, or only to satisfy Part 1's tests?).

6. **Suppose two candidate rules in a chain would both make the same
   correct decision for a user, but the platform team later wants to log
   *which rule* actually decided. How would you change the design to
   support that without breaking `FlagRule.decide`'s existing contract?**
   Strong answer (design-forward, discussion only): a few reasonable
   directions — have `RuleChain` track and expose which rule (by identity
   or a name attribute) produced the winning decision as a side channel
   (e.g. a `last_decided_by` attribute, or a richer return type from a new
   method alongside `is_enabled` rather than changing `decide`'s contract
   for every existing caller); or have `decide` optionally accept/return
   more structured information in a way that still allows `None` to mean
   "no opinion." The key thing to listen for: the candidate should
   recognize this shouldn't require breaking the existing `bool | None`
   contract that every current rule (and any future third-party rule) was
   built against — a good answer treats interface stability as a real
   constraint, not something to casually redesign around.
