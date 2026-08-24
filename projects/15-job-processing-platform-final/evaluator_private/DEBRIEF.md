# Interview Follow-Up Questions (private)

The candidate README explicitly lists being ready to answer follow-up
questions as part of the deliverable — these are the private, detailed
version of that ask. Pick 3-5 depending on time remaining.

1. **What was the root cause, precisely, in terms of the boolean logic?**
   Strong answer: the guard `job.status != "running" and job.status ==
   "queued"` only ever evaluates `True` when `job.status == "queued"`,
   because that clause already implies the first one — so `(A and B)`
   collapses to just `B`. For every other status, including `"completed"`
   and `"failed"`, the second clause is `False` and short-circuits the
   whole condition to `False`, so the guard silently does nothing. The fix
   is to check the one thing that actually needs checking:
   `job.status != "running"`.

2. **Why does your fix need to apply to `cancel_job` too, not just
   `finish_job`?**
   Strong answer: the underlying invariant isn't "the finish endpoint has
   a bug," it's "every lifecycle transition must be guarded against being
   called from a status it isn't valid from." That invariant applies
   identically to `start` (only from `"queued"`), `finish` (only from
   `"running"`), and `cancel` (only from `"queued"`). Writing `cancel_job`
   without a guard reproduces the exact same mistake in a new place, and a
   candidate who only fixes the literally-reported bug without applying
   the lesson to the code they're about to write hasn't actually
   internalized the root cause.

3. **Is there a more robust way to express valid state transitions than
   ad-hoc boolean guards in each method, and would you recommend it here?**
   Strong answer: yes in principle — e.g. a small table mapping each
   transition to its set of valid source statuses, consulted by a single
   shared helper, so a future new transition can't forget the check the
   way this one did. Whether to recommend it *for this exercise* is a
   judgment call worth discussing: it's a reasonable stretch improvement
   for a small, stable set of transitions like this one, but the candidate
   should recognize it's not strictly necessary to solve the problem
   correctly, and over-engineering a generic state-machine framework for a
   three-transition lifecycle in a 75-90 minute exercise would be scope
   creep. A candidate who mentions this as a "if this were expected to
   grow" observation, without necessarily building it, shows good judgment.

4. **What would you need to change if a job needed to support being
   cancelled WHILE running?**
   Strong answer (design-forward-thinking): this system currently has no
   notion of interrupting in-progress work — `running` is a stable state
   until a worker calls back. Supporting mid-flight cancellation would
   require at minimum: a new intermediate status (e.g.
   `"cancel_requested"`) that a worker can observe and act on, some way
   for the worker to actually stop or ignore its result, and a decision
   about what happens if `finish` arrives *after* a cancellation was
   requested but before the worker noticed (a race the current fully
   sequential exercise doesn't have to deal with, but a real distributed
   version would). Bonus if the candidate connects this to the at-least-
   once delivery background already established in the README.

5. **How did you verify your fix didn't just patch the one reported
   scenario?**
   Strong answer: ran the full test suite (not just the one failing test)
   after each change; added a test for the `"failed"`-terminal case in
   addition to the given `"completed"`-terminal case, to make sure the fix
   wasn't narrowly tailored to one status; explicitly tested cancelling a
   job from every non-`"queued"` status, not just the one obvious "cancel
   right after creating it" happy path; tested that a cancelled job can't
   later be started or finished.

6. **Is there a difference in how "seriously" you'd treat the `start_job`
   gap versus the `finish_job` bug, given that one has a failing public
   test and the other doesn't?**
   Strong answer: no — both are the same class of missing/incomplete
   guard, and a thorough candidate treats "no test currently catches this"
   as a reason to *add* a test, not a reason to leave it unfixed. The
   `finish_job` bug got a public test because it had a concrete, reported,
   customer-visible symptom (a changed result); `start_job`'s gap doesn't
   have an equally dramatic visible symptom in this exercise (re-`start`ing
   an already-`running` job doesn't visibly corrupt anything), but
   re-`start`ing an already-*completed* job — flipping a finished job back
   to `"running"` — is a real, if less immediately obvious, correctness
   problem worth fixing on the same reasoning that motivated the
   `finish_job` fix.
