/* Progressive enhancement: normal POST remains the source of truth. */
(() => {
  'use strict';
  const message = document.querySelector('[data-clear-draft]');
  if (message) { try { sessionStorage.removeItem('tl-community:' + message.dataset.clearDraft); } catch (_) {} }
  for (const form of document.querySelectorAll('form[data-draft]')) {
    const key = 'tl-community:' + form.dataset.draft;
    const fields = Array.from(form.elements).filter(el => el.name && !['csrf_token', 'website', 'action', 'parent_id'].includes(el.name));
    try {
      const draft = JSON.parse(sessionStorage.getItem(key) || 'null');
      if (draft) for (const el of fields) {
        if (Object.hasOwn(draft, el.name)) {
          if (el.type === 'checkbox') el.checked = draft[el.name] === true;
          else el.value = draft[el.name];
        }
      }
    } catch (_) {}
    form.addEventListener('input', () => {
      const draft = {};
      for (const el of fields) draft[el.name] = el.type === 'checkbox' ? el.checked : el.value;
      try { sessionStorage.setItem(key, JSON.stringify(draft)); } catch (_) {}
    });
    const discard = document.createElement('button');
    discard.type = 'button'; discard.className = 'co-link'; discard.textContent = 'Descartar borrador';
    discard.addEventListener('click', () => {
      try { sessionStorage.removeItem(key); } catch (_) {}
      form.reset();
      for (const el of fields) if (el.type !== 'hidden') { if (el.type === 'checkbox') el.checked = false; else el.value = ''; }
    });
    form.append(discard);
    form.addEventListener('submit', () => {
      if (form.checkValidity()) for (const button of form.querySelectorAll('button[type=submit], button:not([type])')) {
        button.disabled = true; button.textContent = 'Enviando…';
      }
    });
  }
  const alert = document.querySelector('.co-error');
  if (alert) {
    alert.focus();
    for (const detail of document.querySelectorAll('.co-compose')) detail.open = true;
  }
  const openTarget = () => {
    const target = document.getElementById(location.hash.slice(1));
    if (target && target.tagName === 'DETAILS') target.open = true;
  };
  openTarget();
  window.addEventListener('hashchange', openTarget);
})();
