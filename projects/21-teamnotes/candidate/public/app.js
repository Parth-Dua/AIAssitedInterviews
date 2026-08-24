const listView = document.getElementById('list-view');
const editView = document.getElementById('edit-view');
const notesList = document.getElementById('notes-list');
const editMessage = document.getElementById('edit-message');

async function fetchNotes() {
  const res = await fetch('/notes');
  return res.json();
}

function renderNotes(notes) {
  notesList.innerHTML = '';

  notes.forEach((note) => {
    const li = document.createElement('li');
    li.className = 'note-row';
    li.dataset.id = note.id;

    const titleSpan = document.createElement('span');
    titleSpan.className = 'note-title';
    titleSpan.textContent = note.title;
    titleSpan.addEventListener('click', () => openEditView(note.id));

    const tagsSpan = document.createElement('span');
    tagsSpan.className = 'note-tags';
    tagsSpan.textContent = note.tags.join(', ');

    const versionSpan = document.createElement('span');
    versionSpan.className = 'note-version';
    versionSpan.textContent = `v${note.version}`;

    const tagInput = document.createElement('input');
    tagInput.className = 'quick-tag-input';
    tagInput.placeholder = 'tag';

    const tagBtn = document.createElement('button');
    tagBtn.className = 'quick-tag-btn';
    tagBtn.textContent = '+ tag';
    tagBtn.addEventListener('click', () => quickAddTag(note.id, tagInput, li));

    li.append(titleSpan, tagsSpan, versionSpan, tagInput, tagBtn);
    notesList.appendChild(li);
  });
}

async function loadList() {
  const notes = await fetchNotes();
  renderNotes(notes);
}

// Quick-add-tag: a small per-row control on the list view. Posts directly
// to the tags endpoint and updates just this row.
async function quickAddTag(id, inputEl, rowEl) {
  const tag = inputEl.value.trim();
  if (!tag) {
    return;
  }

  const res = await fetch(`/notes/${id}/tags`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tag }),
  });

  if (!res.ok) {
    alert('Could not add tag.');
    return;
  }

  const updated = await res.json();
  rowEl.querySelector('.note-tags').textContent = updated.tags.join(', ');
  rowEl.querySelector('.note-version').textContent = `v${updated.version}`;
  inputEl.value = '';
}

// Edit view: loads the note when opened and populates the form fields.
async function openEditView(id) {
  const res = await fetch(`/notes/${id}`);
  const note = await res.json();

  document.getElementById('edit-id').value = note.id;
  document.getElementById('edit-version').value = note.version;
  document.getElementById('edit-title').value = note.title;
  document.getElementById('edit-content').value = note.content;
  document.getElementById('edit-tags').value = note.tags.join(', ');
  setMessage('');

  listView.classList.add('hidden');
  editView.classList.remove('hidden');
}

function setMessage(text, isError) {
  editMessage.textContent = text;
  editMessage.classList.toggle('error', Boolean(isError));
}

document.getElementById('back-btn').addEventListener('click', () => {
  editView.classList.add('hidden');
  listView.classList.remove('hidden');
  loadList();
});

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
  const updated = await res.json();

  setMessage('Saved.');
  document.getElementById('edit-version').value = updated.version;
});

document.getElementById('new-note-btn').addEventListener('click', () => {
  document.getElementById('new-note-form').classList.toggle('hidden');
});

document.getElementById('cancel-new-note-btn').addEventListener('click', () => {
  document.getElementById('new-note-form').classList.add('hidden');
});

document.getElementById('create-note-btn').addEventListener('click', async () => {
  const title = document.getElementById('new-note-title').value.trim();
  const content = document.getElementById('new-note-content').value;
  if (!title) {
    return;
  }

  await fetch('/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, tags: [] }),
  });

  document.getElementById('new-note-title').value = '';
  document.getElementById('new-note-content').value = '';
  document.getElementById('new-note-form').classList.add('hidden');
  loadList();
});

document.getElementById('reset-btn').addEventListener('click', async () => {
  await fetch('/debug/reset', { method: 'POST' });
  editView.classList.add('hidden');
  listView.classList.remove('hidden');
  loadList();
});

loadList();
