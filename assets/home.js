/* El catálogo se pide solo al buscar, para mantener la portada liviana. */
(() => {
  const form = document.getElementById('home-search-form');
  if (!form) return;
  const input = document.getElementById('home-query');
  const results = document.getElementById('home-search-results');
  const status = document.getElementById('home-search-status');
  const grid = document.getElementById('home-search-grid');
  const more = document.getElementById('home-search-more');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es').trim();
  let catalogPromise, matches = [], limit = 12, generation = 0, timer;
  function catalog() {
    if (!catalogPromise) {
      catalogPromise = fetch('/search-cards.html').then(response => {
        if (!response.ok) throw new Error('Search unavailable');
        return response.text();
      }).then(html => {
        const template = document.createElement('template');
        template.innerHTML = html;
        return [...template.content.querySelectorAll('.live-search-item')].map(card => ({
          card, text: normalize(`${card.dataset.title} ${card.dataset.sec} ${card.querySelector('.card-desc').textContent}`)
        }));
      }).catch(error => { catalogPromise = undefined; throw error; });
    }
    return catalogPromise;
  }
  function render() {
    grid.replaceChildren(...matches.slice(0, limit).map(({card}) => {
      const node = card.cloneNode(true);
      node.style.removeProperty('display');
      return node;
    }));
    status.textContent = matches.length ? `${matches.length} guías encontradas. Mostrando ${Math.min(limit, matches.length)}.` : 'No encontramos guías para esa búsqueda. Probá con una categoría, marca o menos palabras.';
    more.hidden = limit >= matches.length;
  }
  async function search() {
    clearTimeout(timer);
    const version = ++generation;
    const query = normalize(input.value);
    grid.replaceChildren();
    more.hidden = true;
    results.removeAttribute('aria-busy');
    results.hidden = !query;
    if (!query) return;
    status.textContent = 'Buscando guías…';
    results.setAttribute('aria-busy', 'true');
    try {
      const cards = await catalog();
      if (version !== generation) return;
      const terms = query.split(/\s+/);
      matches = cards.filter(({text}) => terms.every(term => text.includes(term)));
      limit = 12;
      render();
    } catch {
      if (version === generation) status.textContent = 'No pudimos cargar el buscador. Volvé a pulsar Buscar o explorá las categorías.';
    } finally {
      if (version === generation) results.removeAttribute('aria-busy');
    }
  }
  form.addEventListener('submit', event => { event.preventDefault(); search(); });
  input.addEventListener('input', () => {
    ++generation;
    clearTimeout(timer);
    timer = setTimeout(search, 200);
  });
  document.getElementById('home-search-clear').addEventListener('click', () => {
    input.value = '';
    search();
    input.focus();
  });
  more.addEventListener('click', () => { limit += 12; render(); });
})();
