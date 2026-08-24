# Expected Reasoning Path

1. Start the app (`npm run dev`), open `http://localhost:3000`, and use it
   the way the README suggests: look at the note list, open a note to edit
   it, try the quick tag-add control on the list, create a note, click
   Reset. Nothing crashes and everything looks superficially fine on any
   single action taken in isolation.
2. Try combining actions across the two surfaces (the list view's tag
   control and the edit view's save) rather than only testing each in
   isolation — this is the step that actually surfaces the problem, and
   it's the one a candidate who only exercises each endpoint once, alone,
   will miss. A natural way to stumble into it: open a note to edit it,
   get distracted or deliberately go back to the list first, quick-add a
   tag to that same note, then return to the still-open edit form and
   save.
3. Notice: the tag that was just added is gone after the save, and the UI
   never showed any error — it said "Saved." A careful candidate re-checks
   by reloading the list or re-opening the note to confirm this isn't a
   rendering glitch.
4. Turn this into a minimal, deterministic reproduction — ideally scripted
   with `curl` or a quick `supertest`/Jest snippet rather than repeated by
   hand in the browser: `GET /notes/:id` (captures a snapshot) → `POST
   /notes/:id/tags` on the same note → `PUT /notes/:id` using the captured
   snapshot's fields and version. Confirm the tag is present right after
   the `POST` (via a fresh `GET`) and gone right after the `PUT`.
5. Form and test hypotheses before diving into code:
   - "Is the tag-add write itself unreliable?" — checked by `GET`ting
     immediately after the `POST /notes/:id/tags` call: the tag is there
     and the note's version incremented. Ruled out.
   - "Is something serving a stale read?" — checked by reading
     `noteRepository.ts`: a plain `Map`, no caching layer, `getById`
     always returns live state. Ruled out.
   - "The PUT is somehow reverting to old data" — this is where the
     candidate should start reading `noteController.ts` →
     `noteService.ts`.
6. Trace the request path: `routes/notes.ts` → `PUT /notes/:id` →
   `updateNote` controller (thin, validates shape only, passes the payload
   straight through) → `NoteService.updateNote`. Read it line by line:
   `title`, `content`, and `tags` are all taken directly from the payload;
   `version` is bumped by 1. The payload *includes* a `version` field
   (required by the controller's own input validation!) but nothing in the
   function ever reads or compares it.
7. Recognize the significance: `version` is accepted, required, and
   returned on every read — a strong signal it's meant to mean something —
   but on the one endpoint that replaces a note wholesale from a
   client-held snapshot, it's structurally decorative. Compare with
   `addTag`, which never needed to check staleness because it's additive.
8. Fix `updateNote` to compare `payload.version` against
   `existing.version`; reject (409, with none of the payload applied) if
   they differ.
9. Re-run the reproduction: the stale save now returns 409, and the
   quick-added tag survives. A careful candidate then asks: "is tag loss
   the *only* way this manifests, or would a stale save with different
   *content* also silently clobber something?" — and constructs the
   second scenario (two sequential "sessions" loading the same note,
   saving different content changes) to confirm the same fix generalizes:
   the second, now-stale save is rejected too, protecting the first
   session's change.
10. Add regression test(s) that encode what was actually found (the
    GET → quick-add → stale-PUT sequence, and ideally the two-sessions
    lost-update sequence too), verify they fail against the original code
    and pass against the fix, and update the small frontend piece (the
    edit form's save handler should surface a 409 instead of claiming
    success) if the candidate wants the UI itself to behave correctly, not
    just the API.
11. Explain: the version field existed in the contract already but was
    never enforced on the one write path that needed it; the fix restores
    the "your save only succeeds if your view of the note is still
    current" guarantee everywhere `PUT` is used, not just for the specific
    tag-loss case that was first noticed.

A strong candidate reaches step 4 (a minimal, scripted repro) within the
first 20-30 minutes, given the discovery overhead this project deliberately
adds versus a project with a named bug report. They reach step 8 (the
actual fix) within 45-60 minutes, and step 9's generalization (recognizing
and testing the content-loss case, not just the tag-loss case) within the
full 90-minute timebox — ideally without being told to, since noticing it
themselves is the strongest signal this project is designed to surface.
