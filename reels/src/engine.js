/* Motor determinista: todo se calcula a partir del tiempo t (segundos). */
(function () {
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const L = (a, b, u) => a + (b - a) * u;
  const E = {
    linear: u => u,
    inQuad: u => u * u,
    outQuad: u => 1 - (1 - u) * (1 - u),
    inCubic: u => u * u * u,
    outCubic: u => 1 - Math.pow(1 - u, 3),
    inOutCubic: u => u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2,
    outQuart: u => 1 - Math.pow(1 - u, 4),
    outQuint: u => 1 - Math.pow(1 - u, 5),
    inOutQuint: u => u < .5 ? 16 * u ** 5 : 1 - Math.pow(-2 * u + 2, 5) / 2,
    outExpo: u => u === 1 ? 1 : 1 - Math.pow(2, -10 * u),
    inExpo: u => u === 0 ? 0 : Math.pow(2, 10 * u - 10),
    inOutExpo: u => u === 0 ? 0 : u === 1 ? 1 : u < .5 ? Math.pow(2, 20 * u - 10) / 2 : (2 - Math.pow(2, -20 * u + 10)) / 2,
    outBack: u => { const c = 1.70158, d = c + 1; return 1 + d * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); },
    outBackSoft: u => { const c = 0.9, d = c + 1; return 1 + d * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); },
    outElastic: u => u === 0 ? 0 : u === 1 ? 1 : Math.pow(2, -10 * u) * Math.sin((u * 10 - .75) * (2 * Math.PI / 3)) + 1,
    inOutSine: u => -(Math.cos(Math.PI * u) - 1) / 2,
  };
  const tw = (t, t0, d, ease) => (E[ease || 'outExpo'])(clamp((t - t0) / d, 0, 1));
  // pseudo-random determinista
  const hash = (n) => { let x = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };

  const R = window.R = {
    dur: 14, fps: 30, events: [], music: { bpm: 104, root: 'D', mode: 'minor', sections: [] },
    scenes: [], frames: [], wipes: [], flashes: [], title: '',
    ev(t, kind, o) { R.events.push(Object.assign({ t: +t.toFixed(3), kind }, o || {})); },
  };

  const q = (s, r) => (r || document).querySelector(s);
  const qa = (s, r) => Array.from((r || document).querySelectorAll(s));
  const el = (tag, cls, html, parent) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; };

  function st(e, p) {
    const x = p.x || 0, y = p.y || 0, s = p.s == null ? 1 : p.s, sx = p.sx == null ? s : p.sx, sy = p.sy == null ? s : p.sy;
    let tr = `translate3d(${x}px,${y}px,0)`;
    if (p.r) tr += ` rotate(${p.r}deg)`;
    if (p.rx) tr += ` rotateX(${p.rx}deg)`;
    if (p.ry) tr += ` rotateY(${p.ry}deg)`;
    if (p.skx) tr += ` skewX(${p.skx}deg)`;
    if (sx !== 1 || sy !== 1) tr += ` scale(${sx},${sy})`;
    e.style.transform = tr;
    if (p.o != null) e.style.opacity = clamp(p.o, 0, 1);
    let f = '';
    if (p.blur) f += `blur(${p.blur}px) `;
    if (p.bright != null) f += `brightness(${p.bright}) `;
    e.style.filter = f;
  }

  // Entrada genérica: de "from" a identidad.
  function enter(e, t, t0, d, o) {
    o = o || {}; const from = o.from || { y: 60, o: 0 };
    const u = tw(t, t0, d, o.ease || 'outExpo');
    const p = {};
    for (const k in from) p[k] = L(from[k], (k === 'o' || k === 's' || k === 'sx' || k === 'sy' || k === 'bright') ? 1 : 0, u);
    if (from.o == null) p.o = 1;
    // salida opcional
    if (o.t1 != null && t >= o.t1) {
      const v = tw(t, o.t1, o.d1 || .5, o.ease1 || 'inExpo'); const to = o.to || { y: -60, o: 0 };
      for (const k in to) p[k] = L(p[k] == null ? ((k === 'o' || k === 's') ? 1 : 0) : p[k], to[k], v);
    }
    st(e, p);
  }

  // Hook por palabras. lines: [[word|{w,o:true}],...]
  function buildWords(e, lines) {
    e.innerHTML = '';
    lines.forEach(ln => {
      const l = el('span', 'line', null, e);
      ln.forEach((w, i) => {
        const o = typeof w === 'object';
        const s = el('span', 'w' + (o && w.o ? ' o' : ''), (o ? w.w : w), l);
        if (i < ln.length - 1) l.appendChild(document.createTextNode(' '));
      });
    });
    return qa('.w', e);
  }
  // mode: slam | rise | blur ; registra eventos sonoros cuando se construye (once)
  function wordsAnim(ws, t, t0, stagger, d, mode, ease) {
    ws.forEach((w, i) => {
      const u = tw(t, t0 + i * stagger, d, ease || (mode === 'rise' ? 'outQuint' : 'outExpo'));
      if (mode === 'slam') { w.parentElement.style.overflow = 'visible'; st(w, { s: L(1.9, 1, u), o: Math.min(1, u * 3), blur: (1 - u) * 18 }); }
      else if (mode === 'rise') { w.parentElement.style.overflow = 'hidden'; st(w, { y: L(130, 0, u), o: Math.min(1, u * 2.5), r: L(4, 0, u) }); }
      else if (mode === 'drop') st(w, { y: L(-90, 0, u), o: Math.min(1, u * 3), s: L(1.25, 1, u) });
      else st(w, { o: u, blur: (1 - u) * 24, s: L(1.08, 1, u) });
    });
  }

  function typeText(e, text, t, t0, cps, caret) {
    const n = clamp(Math.floor((t - t0) * cps), 0, text.length);
    const done = n >= text.length;
    e.textContent = text.slice(0, n) + ((!done || caret) && t >= t0 && (Math.floor(t * 3) % 2 === 0 || !done) ? '▍' : '');
    e.style.opacity = t >= t0 ? 1 : 0;
  }

  function counter(e, t, t0, d, from, to, fmt, ease) {
    const u = tw(t, t0, d, ease || 'outQuart');
    const v = L(from, to, u);
    e.textContent = fmt ? fmt(v) : Math.round(v).toLocaleString('es-AR');
  }
  const fmtInt = v => Math.round(v).toLocaleString('es-AR');
  const fmtDec = (n) => v => v.toLocaleString('es-AR', { minimumFractionDigits: n, maximumFractionDigits: n });

  function bar(e, t, t0, d, pct, ease) {
    const i = q('i', e); i.style.width = (tw(t, t0, d, ease || 'outExpo') * pct) + '%';
  }
  function strike(e, t, t0, d) {
    e.style.setProperty('--sx', tw(t, t0, d, 'outExpo'));
    const u = tw(t, t0, d, 'outExpo');
    let a = e.querySelector('.sk'); if (!a) { a = el('i', 'sk', null, e); a.style.cssText = 'position:absolute;left:-4%;right:-4%;top:52%;height:.09em;background:var(--orange);transform-origin:left;border-radius:3px'; }
    a.style.transform = `scaleX(${u}) rotate(-2deg)`;
  }

  // Transiciones
  function addWipe(t0, d, kind) { const w = el('div', 'wipe ' + (kind || ''), null, q('#stage')); R.wipes.push({ t0, d: d || .55, e: w }); R.ev(t0, 'whoosh', { len: d || .55 }); return w; }
  function addFlash(t0, d) { const f = el('div', 'flash', null, q('#stage')); R.flashes.push({ t0, d: d || .35, e: f }); return f; }

  function scene(o) { R.scenes.push(o); return o; }

  // Fondo y cromo comunes
  function chrome(opts) {
    opts = opts || {};
    const stage = q('#stage');
    const bg = el('div', 'bg', `<div class="bg-base"></div><div class="bg-lines"></div><div class="bg-grid"></div><div class="bg-glow a"></div><div class="bg-glow b"></div><div class="vignette"></div>`, stage);
    const brand = el('div', 'brand', `<img src="../../assets/logo_dark.png" alt=""><span class="tag">${opts.tag || 'Generadores'}</span>`, stage);
    const prog = el('div', 'progress', '<i></i>', stage);
    const foot = el('div', 'footer', `<span><b>tallerlab</b>.com.ar</span><span>${opts.foot || 'Dato documentado'}</span>`, stage);
    const grain = el('div', 'grain', null, stage);
    const scan = el('div', 'scan', null, stage);
    const ga = q('.bg-glow.a', bg), gb = q('.bg-glow.b', bg);
    R.frames.push(t => {
      q('i', prog).style.width = (clamp(t / R.dur, 0, 1) * 100) + '%';
      st(ga, { x: 520 + Math.sin(t * .35) * 120, y: -520 + Math.cos(t * .27) * 90, s: 1 + Math.sin(t * .5) * .06 });
      st(gb, { x: -700 + Math.cos(t * .22) * 100, y: 1100 + Math.sin(t * .31) * 120 });
      const f = Math.floor(t * R.fps);
      grain.style.backgroundPosition = `${Math.floor(hash(f) * 400)}px ${Math.floor(hash(f + 999) * 400)}px`;
      const light = opts.lightAt ? opts.lightAt(t) : false;
      stage.classList.toggle('light', !!light);
      q('img', brand).src = light ? '../../assets/logo_cropped.png' : '../../assets/logo_dark.png';
      bg.style.opacity = light ? 0 : 1;
    });
    return { bg, brand, prog, foot };
  }

  window.__seek = function (t) {
    for (const s of R.scenes) {
      const on = t >= s.t0 && t < s.t1;
      if (on && !s._built) { s.root = el('div', 'scene', null, q('#stage')); s.state = s.build(s.root) || {}; s._built = true; }
      if (s._built) { s.root.classList.toggle('on', on); if (on) s.frame(t - s.t0, t, s.state, s.root); }
    }
    for (const f of R.frames) f(t);
    for (const w of R.wipes) {
      const u = tw(t, w.t0, w.d, 'inOutQuint');
      w.e.style.transform = `translateX(${L(-120, 120, u)}%) skewX(-12deg)`;
      w.e.style.display = (t >= w.t0 && t < w.t0 + w.d) ? 'block' : 'none';
    }
    for (const f of R.flashes) { const u = clamp((t - f.t0) / f.d, 0, 1); f.e.style.opacity = t >= f.t0 ? (1 - E.outCubic(u)) * .9 : 0; }
  };
  // Construir todo de antemano (para eventos de audio) recorriendo escenas.
  window.__prepare = function () {
    for (const s of R.scenes) if (!s._built) { s.root = el('div', 'scene', null, q('#stage')); s.state = s.build(s.root) || {}; s._built = true; }
    R.events.sort((a, b) => a.t - b.t);
    return { dur: R.dur, fps: R.fps, events: R.events, music: R.music, title: R.title };
  };

  // SVG icons
  const ICON = {
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 7"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 5l7 7-7 7"/></svg>',
    bolt: '<svg viewBox="0 0 24 24" fill="#fff"><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/></svg>',
    warn: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"><path d="M12 3L2 21h20L12 3z"/><path d="M12 10v5M12 18.5v.5"/></svg>',
  };

  Object.assign(window, { R, E, tw, L, clamp, hash, q, qa, el, st, enter, buildWords, wordsAnim, typeText, counter, fmtInt, fmtDec, bar, strike, addWipe, addFlash, scene, chrome, ICON });
})();
