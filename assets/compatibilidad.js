document.addEventListener('click', function (event) {
  const link = event.target.closest('a[data-compat-event]');
  if (!link) return;
  const body = JSON.stringify({event_type: link.dataset.compatEvent});
  if (navigator.sendBeacon) navigator.sendBeacon('/api/compatibilidad/evento', new Blob([body], {type: 'application/json'}));
});

// Progressive enhancement: the complete table remains usable without JavaScript.
const filter = document.getElementById('compat-filter');
if (filter) {
  const container = filter.closest('.compat-filter');
  const rows = Array.from(container.parentElement.querySelectorAll('.compat-table tbody tr'));
  const status = document.getElementById('compat-filter-status');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const entries = rows.map(row => ({row, text: normalize(row.textContent)}));
  const update = () => {
    const query = normalize(filter.value);
    let visible = 0;
    entries.forEach(entry => {
      entry.row.hidden = query !== '' && !entry.text.includes(query);
      if (!entry.row.hidden) visible += 1;
    });
    status.textContent = visible ? `${visible} de ${rows.length} combinaciones documentadas` : 'Sin coincidencias. Probá otro código o consultá el buscador; esto no demuestra incompatibilidad.';
  };
  container.hidden = false;
  filter.addEventListener('input', update);
  update();
}
