const listView = document.getElementById('list-view');
const detailView = document.getElementById('detail-view');
const listingsList = document.getElementById('listings-list');
const detailMessage = document.getElementById('detail-message');
const debugStatus = document.getElementById('debug-status');

let currentListingId = null;

async function fetchListings() {
  const res = await fetch('/listings');
  return res.json();
}

function formatPrice(price) {
  return price === 0 ? 'Free' : `$${price}`;
}

function renderListings(listings) {
  listingsList.innerHTML = '';

  listings.forEach((listing) => {
    const li = document.createElement('li');
    li.className = 'listing-row';
    li.dataset.id = listing.id;

    const titleSpan = document.createElement('span');
    titleSpan.className = 'listing-title';
    titleSpan.textContent = listing.title;
    titleSpan.addEventListener('click', () => openDetailView(listing.id));

    const priceSpan = document.createElement('span');
    priceSpan.className = 'listing-price';
    priceSpan.textContent = formatPrice(listing.price);

    const statusSpan = document.createElement('span');
    statusSpan.className = `listing-status status-${listing.status}`;
    statusSpan.textContent = listing.status;

    li.append(titleSpan, priceSpan, statusSpan);
    listingsList.appendChild(li);
  });
}

async function loadList() {
  const listings = await fetchListings();
  renderListings(listings);
}

function setMessage(text, isError) {
  detailMessage.textContent = text;
  detailMessage.classList.toggle('error', Boolean(isError));
}

function renderDetail(listing) {
  document.getElementById('detail-title').textContent = listing.title;
  document.getElementById('detail-price').textContent = formatPrice(listing.price);
  document.getElementById('detail-status').textContent = `Status: ${listing.status}`;

  document.getElementById('reserve-btn').classList.toggle('hidden', listing.status !== 'available');
  document.getElementById('purchase-btn').classList.toggle('hidden', listing.status !== 'reserved');
}

async function openDetailView(id) {
  currentListingId = id;
  const res = await fetch(`/listings/${id}`);
  const listing = await res.json();
  renderDetail(listing);
  setMessage('');

  listView.classList.add('hidden');
  detailView.classList.remove('hidden');
}

document.getElementById('back-btn').addEventListener('click', () => {
  detailView.classList.add('hidden');
  listView.classList.remove('hidden');
  loadList();
});

document.getElementById('reserve-btn').addEventListener('click', async () => {
  const res = await fetch(`/listings/${currentListingId}/reserve`, { method: 'POST' });
  const body = await res.json();

  if (!res.ok) {
    setMessage(body.error || 'Could not reserve this listing.', true);
    return;
  }

  renderDetail(body);
  setMessage('Reserved.');
});

document.getElementById('purchase-btn').addEventListener('click', async () => {
  const res = await fetch(`/listings/${currentListingId}/purchase`, { method: 'POST' });
  const body = await res.json();

  if (!res.ok) {
    setMessage(body.error || 'Could not purchase this listing.', true);
    return;
  }

  renderDetail(body);
  setMessage('Purchased.');
});

document.getElementById('new-listing-btn').addEventListener('click', () => {
  document.getElementById('new-listing-form').classList.toggle('hidden');
});

document.getElementById('cancel-new-listing-btn').addEventListener('click', () => {
  document.getElementById('new-listing-form').classList.add('hidden');
});

document.getElementById('create-listing-btn').addEventListener('click', async () => {
  const title = document.getElementById('new-listing-title').value.trim();
  const priceRaw = document.getElementById('new-listing-price').value;
  const price = priceRaw === '' ? 0 : Number(priceRaw);

  if (!title) {
    return;
  }

  await fetch('/listings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, price }),
  });

  document.getElementById('new-listing-title').value = '';
  document.getElementById('new-listing-price').value = '';
  document.getElementById('new-listing-form').classList.add('hidden');
  loadList();
});

// Testing tools: advance the server's shared clock by a fixed amount
// (comfortably longer than a reservation window) so time-based behavior
// can be explored without waiting in real time, and reset the store back
// to its starting listings.
document.getElementById('advance-time-btn').addEventListener('click', async () => {
  const ADVANCE_MS = 10 * 60 * 1000;

  await fetch('/debug/advance-time', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ advanceByMs: ADVANCE_MS }),
  });

  debugStatus.textContent = `Advanced the server clock by ${ADVANCE_MS / 60000} minutes.`;
});

document.getElementById('reset-btn').addEventListener('click', async () => {
  await fetch('/debug/reset', { method: 'POST' });
  debugStatus.textContent = 'Data reset to the seeded starting listings.';
  detailView.classList.add('hidden');
  listView.classList.remove('hidden');
  currentListingId = null;
  loadList();
});

loadList();
