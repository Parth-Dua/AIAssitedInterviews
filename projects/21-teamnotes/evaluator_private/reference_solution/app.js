/**
 * Reference solution for the small, mechanical frontend change: the edit
 * form already sends `version` in its PUT body (that part of the contract
 * was never the bug). What's missing in the starting `public/app.js` is
 * that the submit handler never looks at the response status — it treats
 * every response as a success. Once the backend starts rejecting stale
 * saves with 409, the UI needs to surface that instead of claiming
 * "Saved." regardless. This file shows only the changed submit handler;
 * everything else in candidate/public/app.js is unchanged.
 */
document.getElementById('edit-form').addEventListener('submit', async (event) => {
  event.preventDefault();

  const id = document.getElementById('edit-id').value;
  const version = Number(document.getElementById('edit-version').value);
  const title = document.getElementById('edit-title').value;
  const content = document.getElementById('edit-content').value;
  const tags = document
    .getElementById('edit-tags')
    .value.split(',')
    .map((t) => t.trim())
    .filter(Boolean);

  const res = await fetch(`/notes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, tags, version }),
  });
  const body = await res.json();

  if (res.status === 409) {
    setMessage(
      body.error || 'This note changed since you opened it — reload to see the latest version.',
      true
    );
    return;
  }

  if (!res.ok) {
    setMessage(body.error || 'Could not save note.', true);
    return;
  }

  setMessage('Saved.');
  document.getElementById('edit-version').value = body.version;
});
