# Interview Follow-Up Questions (private)

1. **How did you first notice something was wrong?**
   Strong answer: describes actually using the app (or replaying its HTTP
   calls) across more than one surface — specifically, combining the
   list view's tag control with the edit view's save, rather than testing
   each endpoint once in isolation. A weaker but still creditable answer
   describes stumbling into it while poking around without a specific plan,
   as long as they can now describe the exact sequence precisely. A
   candidate who can't describe any concrete sequence of actions — only "I
   read the code and it looked suspicious" — should be probed on whether
   they actually ran the reproduction before writing a fix.

2. **What was the root cause, precisely?**
   Strong answer: `NoteService.updateNote` accepts a `version` field in its
   payload (in fact requires it, per the controller's input validation) but
   never compares it against the note's actual current version before
   applying the rest of the payload. Every field — `title`, `content`,
   `tags` — is taken from the client's payload unconditionally, so any
   write that happened between when the client's edit form loaded its data
   and when it saved is silently discarded.

3. **What invariant does your fix enforce, in one sentence?**
   Strong answer along the lines of: "A full-edit save should only succeed
   if the client's view of the note (its version) is still the note's
   current version — if the note changed since the client loaded it, the
   save must be rejected instead of silently overwriting the newer state."

4. **Why would a fix that only merges tags be insufficient?**
   Strong answer: merging tags additively happens to make the specific
   symptom that's easiest to notice (a quick-added tag disappearing) go
   away, because a union operation can't remove something that's already
   there. But it does nothing about `title` or `content` — a stale save
   still silently overwrites those with no check and no error, which is
   the same underlying problem (no staleness detection at all), just less
   visible because there's no separate "quick edit content" control to
   collide with. The real fix has to check *whether the snapshot is
   current* as a precondition for accepting the whole write, not
   special-case one field.

5. **What would you need to add if this had real concurrent multi-user
   editing instead of a single stale in-browser snapshot?**
   Strong answer touches on: the version-check mechanism (optimistic
   concurrency control) generalizes directly to true multi-user
   concurrency — it doesn't need to change. What *would* need attention:
   surfacing the conflict usefully to a real second user (e.g., offering a
   merge/diff view instead of just "reload and redo your edit"), handling
   the UX of a save failing after a user has been typing for a while
   (don't just discard their draft), and possibly a way to see who else is
   currently editing. A candidate who says "nothing changes" without
   qualifying "for the correctness mechanism specifically" is missing the
   UX half of the question; a candidate who redesigns the whole system for
   this is overengineering for what was actually asked.

6. **Your fix makes the stale save return 409 instead of silently
   succeeding — did you check what happens to a user who's mid-edit when
   that happens? Should it?**
   Strong answer: notices that the starting frontend's save handler didn't
   check the response status at all before their change, so without a
   frontend update, a rejected save would still tell the user "Saved."
   incorrectly, which is arguably worse than before (previously the data
   was silently wrong; now it's silently wrong *and* the UI actively lies
   about it) unless they also added the frontend status check. A candidate
   who made only the backend change should be asked directly whether they
   considered this; one who already added the frontend piece should
   explain why they judged it in-scope as "the client needs to participate
   correctly in the corrected contract" rather than a new feature.
