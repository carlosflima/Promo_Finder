const $ = (id) => document.getElementById(id);
let visibleProducts = [];
let activeList = null;

async function loadCategories() {
  const data = await fetch('/api/categories').then(r => r.json());
  for (const category of data.categories || []) {
    const option = document.createElement('option');
    option.value = category;
    option.textContent = category;
    $('category').appendChild(option);
  }
}

function money(value) {
  return `R$ ${Number(value || 0).toFixed(2).replace('.', ',')}`;
}

async function loadProducts() {
  const params = new URLSearchParams({
    category: $('category').value,
    min_discount: $('minDiscount').value,
    ignore_discount: $('ignoreDiscount').checked
  });
  const data = await fetch('/api/products?' + params).then(r => r.json());
  visibleProducts = data.products || [];
  const body = $('products');
  body.innerHTML = '';
  const selection = $('purchaseSelection');
  selection.innerHTML = '';
  for (const p of visibleProducts) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><input class="offer-check" type="checkbox" data-id="${escapeAttr(p.id)}"></td><td>${escapeHtml(p.title)}</td><td>${money(p.price)}</td><td>${Number(p.discount_percent || 0).toFixed(0)}%</td><td>${escapeHtml(p.store || '-')}</td><td>${escapeHtml(p.site || '-')}</td><td>${escapeHtml(p.shipping || '-')}</td><td>${escapeHtml(p.seller || p.seller_id || '-')}</td><td>${p.link ? `<a href="${escapeAttr(p.link)}" target="_blank" rel="noopener">Ver produto</a>` : '-'}</td>`;
    body.appendChild(tr);

    const row = document.createElement('tr');
    row.innerHTML = `<td><input class="selection-check" type="checkbox" data-id="${escapeAttr(p.id)}"></td><td>${escapeHtml(p.title)}</td><td><input class="qty" data-id="${escapeAttr(p.id)}" type="number" min="1" value="1"></td><td>${money(p.price)}</td><td>${escapeHtml(p.shipping || '-')}</td><td>${escapeHtml(p.store || p.site || '-')}</td><td>${escapeHtml(p.seller || p.seller_id || '-')}</td>`;
    selection.appendChild(row);
  }
  document.querySelectorAll('.offer-check').forEach((el) => el.addEventListener('change', () => syncSelection(el.dataset.id, el.checked)));
  document.querySelectorAll('.selection-check').forEach((el) => el.addEventListener('change', () => syncSelection(el.dataset.id, el.checked)));
  document.querySelectorAll('.qty').forEach((el) => el.addEventListener('change', updateSelectedTotal));
  $('status').textContent = `${data.count} produto(s) exibido(s)`;
  updateSelectedTotal();
}

function syncSelection(id, checked) {
  document.querySelectorAll(`[data-id="${CSS.escape(id)}"]`).forEach((el) => {
    if (el.classList.contains('offer-check') || el.classList.contains('selection-check')) el.checked = checked;
  });
  updateSelectedTotal();
}

function selectedItems() {
  const ids = new Set([...document.querySelectorAll('.selection-check:checked')].map(el => el.dataset.id));
  return visibleProducts.filter(p => ids.has(String(p.id))).map(p => {
    const qtyEl = document.querySelector(`.qty[data-id="${CSS.escape(String(p.id))}"]`);
    return {...p, quantity: Math.max(1, Number(qtyEl?.value || 1)), total_price: Number(p.price || 0), shipping_cost: Number(p.shipping_cost || 0)};
  });
}

function updateSelectedTotal() {
  const total = selectedItems().reduce((sum, p) => sum + (p.total_price + p.shipping_cost) * p.quantity, 0);
  $('selectedTotal').textContent = `Total selecionado: ${money(total)}`;
  const enabled = Boolean(activeList) && selectedItems().length > 0;
  $('saveList').disabled = !enabled;
  $('generateList').disabled = !activeList;
}

async function loadLists() {
  const data = await fetch('/api/purchase-lists').then(r => r.json());
  const select = $('savedLists');
  select.innerHTML = '<option value="">Selecionar lista salva...</option>';
  for (const list of data.lists || []) {
    const option = document.createElement('option');
    option.value = list.id;
    option.textContent = list.name;
    select.appendChild(option);
  }
}

async function createList() {
  const name = $('listName').value.trim();
  if (!name) return setListStatus('Informe o nome da lista.');
  const response = await fetch('/api/purchase-lists', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name})});
  const data = await response.json();
  if (!response.ok) return setListStatus(data.error || 'Não foi possível criar a lista.');
  activeList = data.list;
  $('listName').value = '';
  setListStatus(`Lista ativa: ${activeList.name}`);
  $('deleteList').disabled = false;
  updateSelectedTotal();
  await loadLists();
  $('savedLists').value = activeList.id;
}

async function loadList(id) {
  if (!id) { activeList = null; $('deleteList').disabled = true; updateSelectedTotal(); return; }
  const response = await fetch(`/api/purchase-lists/${encodeURIComponent(id)}`);
  if (!response.ok) return setListStatus('Não foi possível recuperar a lista.');
  activeList = await response.json();
  setListStatus(`Lista ativa: ${activeList.name} (${activeList.items.length} item(ns))`);
  $('deleteList').disabled = false;
  const ids = new Set(activeList.items.map(item => String(item.id)));
  document.querySelectorAll('.selection-check').forEach(el => el.checked = ids.has(String(el.dataset.id)));
  document.querySelectorAll('.offer-check').forEach(el => el.checked = ids.has(String(el.dataset.id)));
  activeList.items.forEach(item => { const q = document.querySelector(`.qty[data-id="${CSS.escape(String(item.id))}"]`); if (q) q.value = item.quantity || 1; });
  updateSelectedTotal();
}

async function saveList() {
  if (!activeList) return;
  const items = selectedItems();
  const response = await fetch(`/api/purchase-lists/${encodeURIComponent(activeList.id)}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({items})});
  const data = await response.json();
  if (!response.ok) return setListStatus(data.error || 'Falha ao salvar.');
  activeList = data.list;
  setListStatus(`Lista salva: ${activeList.name} — ${items.length} item(ns).`);
  await loadLists();
  $('savedLists').value = activeList.id;
}

async function deleteList() {
  if (!activeList || !confirm(`Excluir a lista "${activeList.name}"?`)) return;
  await fetch(`/api/purchase-lists/${encodeURIComponent(activeList.id)}`, {method:'DELETE'});
  activeList = null;
  $('savedLists').value = '';
  $('deleteList').disabled = true;
  setListStatus('Lista excluída.');
  updateSelectedTotal();
  await loadLists();
}

async function generateGroups() {
  if (!activeList) return;
  await saveList();
  const response = await fetch(`/api/purchase-lists/${encodeURIComponent(activeList.id)}/generate`, {method:'POST'});
  const data = await response.json();
  if (!response.ok) return setListStatus(data.error || 'Falha ao gerar grupos.');
  $('purchaseGroups').innerHTML = (data.groups || []).map(group => `<article class="purchase-group"><strong>${escapeHtml(group.store)}${group.seller ? ` — vendedor: ${escapeHtml(group.seller)}` : ''}</strong><span>${group.items.length} produto(s) · ${money(group.total)}</span></article>`).join('');
}

function setListStatus(text) { $('listStatus').textContent = text; }
function escapeHtml(value) { const d = document.createElement('div'); d.textContent = value ?? ''; return d.innerHTML; }
function escapeAttr(value) { return String(value ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;'); }

$('refresh').addEventListener('click', async () => {
  $('status').textContent = 'Pesquisando...';
  await fetch('/api/refresh', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({min_discount: Number($('minDiscount').value), ignore_discount: $('ignoreDiscount').checked}) });
  await loadProducts();
});
$('export').addEventListener('click', async () => {
  const data = await fetch('/api/export-pdf', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}).then(r => r.json());
  if (data.ok) window.open(data.url, '_blank'); else alert(data.error || 'Não foi possível exportar.');
});
$('createList').addEventListener('click', createList);
$('savedLists').addEventListener('change', (e) => loadList(e.target.value));
$('saveList').addEventListener('click', saveList);
$('deleteList').addEventListener('click', deleteList);
$('generateList').addEventListener('click', generateGroups);
$('category').addEventListener('change', loadProducts);
$('minDiscount').addEventListener('change', loadProducts);
$('ignoreDiscount').addEventListener('change', loadProducts);

loadCategories().then(loadProducts).then(loadLists).catch(err => $('status').textContent = 'Erro ao carregar: ' + err.message);
