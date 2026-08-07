const $ = (id) => document.getElementById(id);

async function loadCategories() {
  const data = await fetch('/api/categories').then(r => r.json());
  for (const category of data.categories || []) {
    const option = document.createElement('option');
    option.value = category;
    option.textContent = category;
    $('category').appendChild(option);
  }
}

async function loadProducts() {
  const params = new URLSearchParams({
    category: $('category').value,
    min_discount: $('minDiscount').value,
    ignore_discount: $('ignoreDiscount').checked
  });
  const data = await fetch('/api/products?' + params).then(r => r.json());
  const body = $('products');
  body.innerHTML = '';
  for (const p of data.products || []) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${escapeHtml(p.title)}</td><td>R$ ${Number(p.price).toFixed(2).replace('.', ',')}</td><td>${Number(p.discount_percent || 0).toFixed(0)}%</td><td>${escapeHtml(p.store || '-')}</td><td>${escapeHtml(p.site || '-')}</td><td>${escapeHtml(p.shipping || '-')}</td><td>${p.link ? `<a href="${escapeAttr(p.link)}" target="_blank" rel="noopener">Ver produto</a>` : '-'}</td>`;
    body.appendChild(tr);
  }
  $('status').textContent = `${data.count} produto(s) exibido(s)`;
}

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
$('category').addEventListener('change', loadProducts);
$('minDiscount').addEventListener('change', loadProducts);
$('ignoreDiscount').addEventListener('change', loadProducts);

loadCategories().then(loadProducts).catch(err => $('status').textContent = 'Erro ao carregar: ' + err.message);
