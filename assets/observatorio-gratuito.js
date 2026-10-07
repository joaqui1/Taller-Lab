/* Progressive enhancement: los modelos, enlaces e historial funcionan sin JS. */
(async () => {
  'use strict';
  // El dominio principal puede seguir usando su hosting actual. Los datos y
  // las descargas se actualizan desde Pages, sin ejecutar cron de Vercel.
  const mirror = ['www.tallerlab.com.ar','tallerlab.com.ar'].includes(location.hostname);
  const remoteRoot = 'https://joaqui1.github.io/Taller-Lab';
  // Aplicar la caducidad antes de cualquier espera de red.
  function expireSavedPrices() {
    for (const item of document.querySelectorAll('.product[data-observed],.model-current[data-observed]')) {
      const at = Date.parse(item.dataset.observed);
      if (item.dataset.state !== 'error' && item.dataset.observed &&
          (!Number.isFinite(at) || at > Date.now() || Date.now()-at > 48*3600000)) {
        item.dataset.state = 'vencido';
        item.querySelector('.current-price').textContent = '—';
        const badge = item.querySelector('.badge'); badge.className = 'badge vencido'; badge.textContent = 'Dato vencido';
        const change = item.querySelector('.change'); if (change) change.textContent = '—';
        const changeNote = item.querySelector('.product-change small'); if (changeNote) changeNote.textContent = 'Sin comparación vigente';
        const caption = item.querySelector('.price-caption'); if (caption) caption.textContent = 'Dato vencido';
        if (item.matches('.model-current')) {
          const verdict = document.querySelector('.verdict');
          if (verdict) {
            verdict.className = 'verdict unknown';
            verdict.querySelector('p').textContent = 'La captura venció: no hay un precio vigente para calificar. El historial sigue disponible abajo.';
          }
        }
      }
    }
    for (const item of document.querySelectorAll('.moves li[data-observed]')) {
      const at = Date.parse(item.dataset.observed);
      if (!Number.isFinite(at) || at > Date.now() || Date.now()-at > 48*3600000) item.hidden = true;
    }
    const moves = document.querySelector('.moves');
    if (moves && !moves.querySelector('li:not([hidden])')) moves.hidden = true;
  }
  expireSavedPrices(); setInterval(expireSavedPrices, 60000);
  // Refrescar también ficha, estadísticas, contexto y destacados desde una misma
  // publicación. El HTML local sigue siendo usable si Pages no responde.
  if (mirror) {
    try {
      const response = await fetch(remoteRoot + location.pathname, {cache:'no-store', credentials:'omit', signal:AbortSignal.timeout(8000)});
      if (!response.ok) throw new Error('Publicación no disponible');
      const remote = new DOMParser().parseFromString(await response.text(), 'text/html');
      const next = remote.querySelector('main[data-publication]');
      const currentMain = document.querySelector('main[data-publication]');
      const canonical = remote.querySelector('link[rel="canonical"]')?.href;
      const at = Date.parse(next?.dataset.publication);
      if (next && currentMain && canonical === 'https://www.tallerlab.com.ar' + location.pathname &&
          Number.isFinite(at) && at <= Date.now() && at >= Date.parse(currentMain.dataset.publication)) {
        // Las rutas de Pages llevan un prefijo; las páginas quedan en el dominio principal.
        for (const link of next.querySelectorAll('a[href^="/Taller-Lab/"]')) {
          link.setAttribute('href', link.getAttribute('href').slice('/Taller-Lab'.length));
        }
        currentMain.replaceWith(document.importNode(next, true));
      }
    } catch { /* La vigencia se valida igualmente sobre la copia local. */ }
  }
  expireSavedPrices();

  function classifyChange(previous, current) {
    const before = Number(previous.price_ars), after = Number(current.price_ars);
    const oldRef = Number(previous.reference_ars), newRef = Number(current.reference_ars);
    const oldOffer = oldRef > before, newOffer = newRef > after;
    if (before === after) return 'Sin cambio';
    if (oldOffer && !newOffer && after === oldRef) return 'Fin de oferta';
    if (newOffer && !oldOffer && before === newRef) return 'Inicio de oferta';
    if (oldOffer || newOffer) return 'Cambio de oferta';
    return 'Cambio de precio';
  }
  if (mirror) {
    for (const link of document.querySelectorAll('a[href]')) {
      const target = new URL(link.href);
      if (target.origin === location.origin && (target.pathname.endsWith('/historial.csv') || target.pathname.endsWith('/descargar-csv') || target.pathname.endsWith('/precios-observatorio-publico.json'))) {
        link.href = remoteRoot + target.pathname;
      }
    }
  }
  const list = document.getElementById('products');
  if (!list) return;
  const rows = [...list.querySelectorAll('.product')];
  const search = document.getElementById('search');
  const stock = document.getElementById('stock');
  const sort = document.getElementById('sort');
  const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es');
  const original = new Map(rows.map((r,i) => [r,i]));
  function refresh() {
    expireSavedPrices();
    let available = 0, unavailable = 0, unverified = 0;
    for (const row of rows) {
      if(row.dataset.state === 'disponible') available++;
      else if(row.dataset.state === 'agotado') unavailable++;
      else unverified++;
    }
    document.getElementById('available-count').textContent = String(available).padStart(2,'0');
    document.getElementById('unavailable-count').textContent = String(unavailable).padStart(2,'0');
    document.getElementById('freshness-warning').hidden = unverified === 0;
    filter();
  }
  function filter() {
    const query = norm(search.value.trim());
    const visible = rows.filter(row => {
      const match = norm(row.dataset.search).includes(query);
      const state = row.dataset.state;
      const status = stock.value === 'all' || state === stock.value || (stock.value === 'unverified' && !['disponible','agotado'].includes(state));
      row.hidden = !(match && status);
      return !row.hidden;
    });
    const sorted = [...rows].sort((a,b) => {
      if(sort.value === 'default') return original.get(a)-original.get(b);
      const ap = a.dataset.state === 'disponible' ? Number(a.dataset.price) : null;
      const bp = b.dataset.state === 'disponible' ? Number(b.dataset.price) : null;
      if(ap === null && bp === null) return original.get(a)-original.get(b);
      if(ap === null) return 1; if(bp === null) return -1;
      return sort.value === 'asc' ? ap-bp : bp-ap;
    });
    for(const row of sorted) list.appendChild(row);
    document.getElementById('result-count').textContent = `${visible.length} de ${rows.length} modelos`;
    document.getElementById('empty').hidden = visible.length !== 0;
  }
  document.querySelector('.filter-bar').hidden = false;
  search.addEventListener('input', filter);
  stock.addEventListener('change', filter);
  sort.addEventListener('change', filter);
  refresh();
  if (mirror) loadRemote();
  setInterval(refresh, 60000);

  async function loadRemote() {
    try {
      const response = await fetch(remoteRoot+'/assets/datos/precios-observatorio-publico.json', {cache:'no-store', credentials:'omit', signal:AbortSignal.timeout(15000)});
      if(!response.ok) throw new Error('Fuente todavía no disponible');
      const data = await response.json();
      if(data.version !== 1 || !Array.isArray(data.models) || !Array.isArray(data.observations) || !data.latest_attempts) throw new Error('Datos inválidos');
      const labels = {disponible:'Disponible', agotado:'Agotado', error:'Sin verificación', desconocido:'Stock sin confirmar', vencido:'Dato vencido'};
      const currency = new Intl.NumberFormat('es-AR', {style:'currency',currency:'ARS',minimumFractionDigits:2});
      const date = at => new Date(at).toLocaleString('es-AR', {timeZone:'America/Argentina/Buenos_Aires',dateStyle:'short',timeStyle:'short'})+' ART';
      let updated = 0;
      for(const row of rows) {
        const m = data.models.find(m => m.id === row.dataset.id);
        if(!m || m.url !== row.dataset.url || m.variant !== row.dataset.variant || m.brand !== row.dataset.brand || m.model !== row.dataset.model || m.category !== row.dataset.category) continue;
        const series = data.observations.filter(o => o.model_id === m.id && Number.isFinite(Date.parse(o.observed_at)) && (o.price_ars === null || /^\d+\.\d{2}$/.test(o.price_ars)) && ['disponible','agotado','desconocido'].includes(o.availability)).sort((a,b) => Date.parse(a.observed_at)-Date.parse(b.observed_at));
        const o = series.at(-1); if(!o || Date.parse(o.observed_at) < Date.parse(row.dataset.observed || '1970-01-01')) continue;
        const attempt = data.latest_attempts[m.id] || {};
        let state = attempt.status === 'error' && Date.parse(attempt.observed_at) >= Date.parse(o.observed_at) ? 'error' : o.availability;
        if(state === 'disponible' && (!o.price_ars || Number(o.price_ars)<5000 || Number(o.price_ars)>50000000)) state = 'error';
        row.dataset.observed = o.observed_at; row.dataset.price = o.price_ars || ''; row.dataset.state = state;
        row.querySelector('.current-price').textContent = state === 'disponible' ? currency.format(Number(o.price_ars)) : '—';
        row.querySelector('.price-caption').textContent = state === 'disponible' ? 'Precio publicado · ARS' : labels[state];
        row.querySelector('.badge').className = 'badge '+state;
        row.querySelector('.badge').textContent = labels[state];
        row.querySelector('.product-stock small').textContent = date(o.observed_at);
        const previous = series.slice(0,-1).filter(h => h.availability === 'disponible' && h.price_ars).at(-1);
        const change = state === 'disponible' && previous ? (Number(o.price_ars)/Number(previous.price_ars)-1)*100 : null;
        row.querySelector('.change').textContent = change === null ? '—' : (change>=0?'+':'')+change.toFixed(1)+'%';
        row.querySelector('.product-change small').textContent = change === null ? 'vs. captura anterior' : classifyChange(previous, o);
        row.querySelector('.product-change').classList.toggle('down', change !== null && change < 0);
        const history = row.querySelector('.history');
        for(const old of history.querySelectorAll('.error-note,.reference-note')) old.remove();
        if(o.reference_ars && /^\d+\.\d{2}$/.test(o.reference_ars)) {
          const ref = document.createElement('p'); ref.className='reference-note';
          ref.textContent='Precio tachado por el comercio en esa captura: '+currency.format(Number(o.reference_ars))+'. No demuestra un descuento histórico.';
          history.prepend(ref);
        }
        if(state === 'error') {
          const note = document.createElement('p'); note.className = 'error-note'; note.textContent = attempt.reason || 'No se pudo validar la captura más reciente'; history.prepend(note);
        }
        const tbody = row.querySelector('tbody'); tbody.replaceChildren();
        for(const h of series.slice(-30).reverse()) {
          const tr = document.createElement('tr');
          for(const value of [date(h.observed_at), h.price_ars ? currency.format(Number(h.price_ars)) : 'Sin precio', labels[h.availability]]) {
            const td = document.createElement('td'); td.textContent = value; tr.appendChild(td);
          }
          tbody.appendChild(tr);
        }
        updated++;
      }
      if(updated && data.run?.finished_at) {
        document.querySelector('.capture strong').textContent = date(data.run.finished_at);
        // Si el JSON se adelantó al HTML, no mezclar sus precios con destacados antiguos.
        if (Date.parse(data.run.finished_at) > Date.parse(document.querySelector('main').dataset.publication)) {
          const moves = document.querySelector('.moves'); if (moves) moves.hidden = true;
        }
      }
      refresh();
    } catch {
      const warning = document.getElementById('freshness-warning');
      warning.hidden = false;
      warning.textContent = 'No se pudo consultar la actualización remota. Se muestra la captura guardada y se ocultan los datos vencidos. ';
      const link = document.createElement('a'); link.href = remoteRoot+'/datos/precios-herramientas-argentina/'; link.textContent = 'Abrir observatorio actualizado ↗'; warning.appendChild(link);
    }
  }
})();
