document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.offer-photo img').forEach(img => img.addEventListener('error', () => {
    const fallback = document.createElement('div');
    fallback.className = 'offer-no-photo';
    fallback.textContent = 'Foto del modelo no disponible en este momento';
    img.replaceWith(fallback);
  }));
  document.querySelectorAll('.affiliate-shelf').forEach(shelf => {
    const cards = [...shelf.querySelectorAll('.offer-card')];
    const fields = [
      ['brand', shelf.querySelector('.filter-brand')],
      ['use', shelf.querySelector('.filter-use')],
      ['power', shelf.querySelector('.filter-power')],
    ];
    // Los bloques contextuales solo tienen tarjetas y CTA, sin filtros ni comparador.
    if (fields.some(([, select]) => !select)) return;
    fields.forEach(([key, select]) => {
      [...new Set(cards.map(card => card.dataset[key]))].sort().forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.append(option);
      });
      select.addEventListener('change', () => {
        let visible = 0;
        cards.forEach(card => {
          card.hidden = fields.some(([field, control]) => control.value && card.dataset[field] !== control.value);
          if (!card.hidden) visible++;
        });
        shelf.querySelector('.offer-empty').hidden = visible !== 0;
      });
    });

    const panel = shelf.querySelector('.compare-panel');
    const checks = cards.map(card => card.querySelector('.compare-checkbox'));
    checks.forEach(check => check.addEventListener('change', () => {
      let chosen = checks.filter(item => item.checked);
      const types = new Set(chosen.map(item => item.closest('.offer-card').dataset.compareType));
      if (types.size > 1) {
        check.checked = false;
        panel.hidden = false;
        panel.textContent = 'Compará herramientas del mismo tipo. Desmarcá las elegidas para cambiar de tipo.';
        return;
      }
      if (chosen.length > 3) {
        check.checked = false;
        panel.hidden = false;
        panel.textContent = 'Podés comparar hasta tres productos.';
        return;
      }
      if (!chosen.length) {
        panel.hidden = true;
        panel.replaceChildren();
        return;
      }
      const table = document.createElement('table');
      const caption = document.createElement('caption');
      caption.textContent = `Comparación de ${chosen.length} producto${chosen.length > 1 ? 's' : ''}`;
      table.append(caption);
      const selectedCards = chosen.map(item => item.closest('.offer-card'));
      const labels = JSON.parse(selectedCards[0].dataset.compareLabels);
      const headings = ['Modelo', 'Uso', 'Alimentación', ...labels, 'Incluye'];
      headings.forEach((heading, rowIndex) => {
        const row = document.createElement('tr');
        const th = document.createElement('th');
        th.scope = 'row';
        th.textContent = heading;
        row.append(th);
        selectedCards.forEach(card => {
          const cell = document.createElement('td');
          const specs = JSON.parse(card.dataset.compareDetails);
          const values = [
            card.querySelector('h3').textContent,
            card.dataset.use,
            card.dataset.power,
            ...labels.map((_, index) => specs[index] || 'No informado'),
            card.querySelector('.offer-includes').textContent.replace(/^Incluye:\s*/, ''),
          ];
          cell.textContent = values[rowIndex];
          row.append(cell);
        });
        table.append(row);
      });
      panel.replaceChildren(table);
      panel.hidden = false;
    }));
  });

  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="https://meli.la/"], a[data-affiliate-placement]');
    if (!link) return;
    const payload = JSON.stringify({
      product: link.href,
      page: window.location.pathname,
      placement: link.dataset.affiliatePlacement || (link.closest('.markdown-body') ? (link.classList.contains('btn-mercado-libre') ? 'article-button' : 'article-inline') : 'other'),
    });
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/affiliate-click', new Blob([payload], {type: 'application/json'}));
    } else {
      fetch('/api/affiliate-click', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: payload, keepalive: true}).catch(() => {});
    }
  });
});
