# Interview Follow-Up Questions (private)

1. **What was the root cause of the pagination bug?**
   Strong answer: the repository's cursor filter compared
   `sequence >= cursor` instead of `sequence > cursor`. Since `cursor` is
   set to the last item's sequence from the previous page, the inclusive
   comparison re-included that same item at the start of the next page.

2. **Why must the category filter be applied *before* pagination rather
   than after?**
   Strong answer: `next_cursor` and page size are both derived from
   whatever `list_page` returns. If pagination happens first (against the
   full unfiltered list) and category filtering happens second, a page can
   come back shorter than `limit` purely because non-matching items were
   trimmed out of the window — and the service then wrongly concludes
   there's nothing more to page through (`next_cursor: null`), silently
   dropping matching items that exist further along in the unfiltered
   list. Filtering first means the cursor/limit slice operates on the
   already-narrowed, still-ordered set, so page size and `next_cursor`
   stay meaningful.

3. **How did you verify the category filter actually worked, beyond
   checking that a single page returned the right category?**
   Strong answer: paged through an entire filtered category (following
   `next_cursor` until null) and confirmed every matching item was
   returned exactly once — a single-page check can't distinguish a correct
   implementation from the filter-after-paginate mistake.

4. **How would this design extend to filtering by multiple fields at
   once (e.g. category *and* status)?**
   Strong answer (design-forward-thinking): the same filter-before-paginate
   principle generalizes — build the filter predicate(s) first, apply all
   of them to narrow the ordered set, then slice by cursor/limit. In a
   real (database-backed) implementation this would become additional
   `WHERE` clauses evaluated before the pagination `LIMIT`/keyset
   condition, not a second pass over an already-paginated result.

5. **What would you change if this needed to scale to millions of
   reservations, where an in-memory list and a Python-level filter/sort
   aren't viable?**
   Strong answer: move to a real datastore with an index on
   `(category, sequence)` (or just `sequence` if category isn't selective
   enough to warrant its own index) so both the filter and the ordered
   cursor scan can be satisfied efficiently by the database rather than by
   scanning and sorting the full table in application code; the query
   shape (filter predicate, then a keyset/cursor condition on the sort
   column, then `LIMIT`) stays conceptually the same.

6. **Is there another valid way to implement the category filter that
   isn't "filter then paginate in one pass"?**
   Strong answer: yes — e.g. precomputing a per-category index (a dict from
   category to its ordered list of items) built once at repository
   construction time, so a filtered request doesn't re-scan and re-filter
   the full list on every call. Any implementation is acceptable as long
   as the *result* is equivalent to filtering before applying the
   cursor/limit boundary.
