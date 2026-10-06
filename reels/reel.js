/* Control determinista del tiempo: el renderizador llama a window.__seek(ms) por cada cuadro.
   En el navegador (vista previa) el reel se reproduce en bucle usando el mismo mecanismo. */
(function () {
  const meta = document.querySelector('meta[name="reel-duration"]');
  window.__duration = Math.round(parseFloat((meta && meta.content) || '15') * 1000);
  const counters = Array.from(document.querySelectorAll('[data-count]'));
  const ease = (x) => 1 - Math.pow(1 - x, 3);
  const fmt = (v, el) => {
    const f = el.dataset.format || 'int';
    let s = f === 'dec1' ? v.toFixed(1).replace('.', ',') : Math.round(v).toLocaleString('es-AR');
    return (el.dataset.prefix || '') + s + (el.dataset.suffix || '');
  };
  function updateCounters(ms) {
    for (const el of counters) {
      const [from, to, start, end] = el.dataset.count.split(',').map(Number);
      const p = Math.min(1, Math.max(0, (ms / 1000 - start) / (end - start)));
      el.textContent = fmt(from + (to - from) * ease(p), el);
    }
  }
  window.__seek = function (ms) {
    for (const a of document.getAnimations()) { a.pause(); a.currentTime = ms; }
    updateCounters(ms);
  };
  window.__ready = async function () {
    await document.fonts.ready;
    await Promise.all(Array.from(document.images).map((img) => img.complete ? null : new Promise((r) => { img.onload = img.onerror = r; })));
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  };
  if (!navigator.webdriver) {
    let t0 = performance.now();
    const loop = () => {
      const ms = (performance.now() - t0) % (window.__duration + 600);
      window.__seek(Math.min(ms, window.__duration));
      requestAnimationFrame(loop);
    };
    window.__ready().then(() => requestAnimationFrame(loop));
    document.addEventListener('click', () => { t0 = performance.now(); });
    // Encuadre para mirar la vista previa en una pantalla común.
    const fit = () => { const s = Math.min(innerWidth / 1080, innerHeight / 1920); document.documentElement.style.cssText = `width:100vw;height:100vh;overflow:hidden;background:#111`; document.body.style.cssText = `transform:scale(${s});transform-origin:top left;margin-left:${(innerWidth - 1080 * s) / 2}px`; };
    fit(); addEventListener('resize', fit);
  }
})();
