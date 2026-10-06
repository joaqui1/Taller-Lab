// Motor de render determinista para reels TallerLab.
// Todo se calcula a partir de un tiempo t (segundos): seek(t) deja el DOM en el estado exacto de ese instante.
// Así cada frame es reproducible y la pista de audio se sincroniza con la lista de eventos que emite la timeline.

export const ease = {
  linear: p => p,
  inCubic: p => p * p * p,
  outCubic: p => 1 - Math.pow(1 - p, 3),
  inOutCubic: p => (p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
  outQuint: p => 1 - Math.pow(1 - p, 5),
  outExpo: p => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p)),
  inExpo: p => (p <= 0 ? 0 : Math.pow(2, 10 * p - 10)),
  inOutExpo: p => (p <= 0 ? 0 : p >= 1 ? 1 : p < .5 ? Math.pow(2, 20 * p - 10) / 2 : (2 - Math.pow(2, -20 * p + 10)) / 2),
  outBack: p => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  outBackSoft: p => { const c1 = 1.1, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  outElastic: p => (p <= 0 ? 0 : p >= 1 ? 1 : Math.pow(2, -10 * p) * Math.sin((p * 10 - .75) * (2 * Math.PI / 3)) + 1),
};

export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
export const lerp = (a, b, p) => a + (b - a) * p;
// Progreso 0..1 de t entre t0 y t1 con una curva.
export const prog = (t, t0, t1, e = ease.outCubic) => e(clamp((t - t0) / Math.max(1e-6, t1 - t0)));
// Ventana: sube en [t0, t0+fi], baja en [t1-fo, t1].
export const window_ = (t, t0, t1, fi = .3, fo = .3, ei = ease.outCubic, eo = ease.inCubic) => {
  if (t < t0 || t > t1) return 0;
  const a = fi > 0 ? ei(clamp((t - t0) / fi)) : 1;
  const b = fo > 0 ? 1 - eo(clamp((t - (t1 - fo)) / fo)) : 1;
  return Math.min(a, b);
};

// PRNG determinista (mulberry32).
export function rng(seed) {
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const hash = (n) => { let x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

const fmtNum = (v, decimals = 0, sep = '.') => {
  const f = v.toFixed(decimals);
  const [i, d] = f.split('.');
  const ii = i.replace(/\B(?=(\d{3})+(?!\d))/g, sep);
  return d ? `${ii},${d}` : ii;
};

export class Engine {
  constructor(stage) {
    this.stage = stage;
    this.world = stage.querySelector('#world');
    this.progressEl = stage.querySelector('#progress');
    this.flashEl = stage.querySelector('#flash');
    this.grainEl = stage.querySelector('#grain');
    this.wipeEl = stage.querySelector('#wipe');
    this.wipe2El = stage.querySelector('#wipe2');
    this.brandEl = stage.querySelector('#brand');
    this.grainEl.style.backgroundImage = `url(${makeGrain(420)})`;
  }

  async load(def) {
    this.def = def;
    this.dur = def.duration;
    this.fps = def.fps || 30;
    this.events = [];
    this.shots = [];
    this.impacts = [];
    this.wipes = [];
    this.flashes = [];
    this.world.innerHTML = '';
    this.brand = def.brand || { show: [0.0, def.duration] };
    this.stage.querySelector('#brand-logo').src = def.logo || '../../assets/logo_dark.png';
    def.build(this);
    await this.waitAssets();
    this.seek(0);
  }

  async waitAssets() {
    const fams = ["800 100px 'Plus Jakarta Sans'", "600 100px 'Plus Jakarta Sans'", "500 100px 'Plus Jakarta Sans'", "700 100px 'Caveat'", "700 100px 'JetBrains Mono'", "500 100px 'JetBrains Mono'"];
    await Promise.all(fams.map(f => document.fonts.load(f)));
    await document.fonts.ready;
    const imgs = [...this.stage.querySelectorAll('img')];
    await Promise.all(imgs.map(im => (im.complete ? Promise.resolve() : new Promise(r => { im.onload = r; im.onerror = r; })).then(() => im.decode().catch(() => {}))));
  }

  // ---------- eventos / globales ----------
  event(t, type, data = {}) { this.events.push({ t: +t.toFixed(4), type, ...data }); }
  impact(t, { strength = 1, flash = .35, punch = .035, sound = 'impact', color = '#fff' } = {}) {
    this.impacts.push({ t, strength, punch });
    if (flash > 0) this.flashes.push({ t, a: flash, color });
    if (sound) this.event(t, sound, { strength });
  }
  wipe(t, { dur = .55, sound = 'whoosh' } = {}) {
    this.wipes.push({ t, dur });
    if (sound) this.event(t - dur * .25, sound, { dur });
  }

  // ---------- shots ----------
  shot(t0, t1, fn, { z = 0 } = {}) {
    const el = document.createElement('div');
    el.className = 'layer';
    el.style.zIndex = String(10 + z);
    this.world.appendChild(el);
    const shot = new Shot(this, el, t0, t1);
    this.shots.push(shot);
    fn(shot);
    return shot;
  }

  seek(t) {
    this.t = t;
    for (const s of this.shots) s.seek(t);
    // progreso
    this.progressEl.style.width = `${(clamp(t / this.dur) * 1080).toFixed(1)}px`;
    // brand
    const [b0, b1] = this.brand.show;
    const bo = window_(t, b0, b1, .5, .35);
    this.brandEl.style.opacity = bo.toFixed(3);
    this.brandEl.style.transform = `translateY(${((1 - bo) * -20).toFixed(1)}px)`;
    // sacudida + punch-in de cámara
    let dx = 0, dy = 0, rot = 0, sc = 1;
    const frame = Math.round(t * this.fps);
    for (const im of this.impacts) {
      const dt = t - im.t;
      if (dt < 0 || dt > .6) continue;
      const env = Math.exp(-dt * 9) * im.strength;
      dx += (hash(frame * 3 + 1) - .5) * 2 * 26 * env;
      dy += (hash(frame * 3 + 2) - .5) * 2 * 20 * env;
      rot += (hash(frame * 3 + 3) - .5) * 2 * .6 * env;
      sc += im.punch * Math.exp(-dt * 6);
    }
    this.world.style.transform = `translate(${dx.toFixed(2)}px, ${dy.toFixed(2)}px) rotate(${rot.toFixed(3)}deg) scale(${sc.toFixed(4)})`;
    // flash
    let fl = 0, flc = '#fff';
    for (const f of this.flashes) { const dt = t - f.t; if (dt >= 0 && dt < .35) { const v = f.a * Math.exp(-dt * 14); if (v > fl) { fl = v; flc = f.color; } } }
    this.flashEl.style.opacity = fl.toFixed(3);
    this.flashEl.style.background = flc;
    // grano
    this.grainEl.style.backgroundPosition = `${Math.floor(hash(frame + 11) * 400)}px ${Math.floor(hash(frame + 29) * 400)}px`;
    // wipes
    let wx = -200, wx2 = -200;
    for (const w of this.wipes) {
      const p = (t - (w.t - w.dur / 2)) / w.dur;
      if (p >= 0 && p <= 1) {
        wx = lerp(-200, 200, ease.inOutExpo(p));
        wx2 = lerp(-200, 200, ease.inOutExpo(clamp(p - .08)));
      }
    }
    this.wipeEl.style.transform = `translateX(${wx.toFixed(2)}%) skewX(-18deg)`;
    this.wipe2El.style.transform = `translateX(${wx2.toFixed(2)}%) skewX(-18deg)`;
  }
}

class Shot {
  constructor(engine, el, t0, t1) {
    this.engine = engine; this.el = el; this.t0 = t0; this.t1 = t1; this.dur = t1 - t0;
    this.items = [];
  }
  // t absoluto para eventos
  abs(tl) { return this.t0 + tl; }
  ev(tl, type, data) { this.engine.event(this.abs(tl), type, data); }

  add(el, update) {
    this.el.appendChild(el);
    const item = { el, update };
    this.items.push(item);
    return item;
  }
  seek(t) {
    const on = t >= this.t0 && t < this.t1;
    this.el.style.display = on ? 'block' : 'none';
    if (!on) return;
    const tl = t - this.t0;
    for (const it of this.items) it.update(tl, t);
  }

  // ---------- componentes ----------
  bg(color = 'var(--graphite)') {
    const d = mk('div', 'layer'); d.style.background = color;
    return this.add(d, () => {});
  }
  texture({ vignette = true, diag = true } = {}) {
    if (diag) { const d = mk('div', 'layer diag'); this.add(d, () => {}); }
    if (vignette) { const v = mk('div', 'layer vignette'); this.add(v, () => {}); }
  }
  // Foto con ken burns y gradiente grafito.
  photo({ src, from = { s: 1.08, x: 0, y: 0 }, to = { s: 1.18, x: -2, y: -1 }, t0 = 0, t1 = this.dur, grade = true, opacity = 1, fade = [0, 0], blur = 0, dark = 0 }) {
    const wrap = mk('div', 'layer'); wrap.style.overflow = 'hidden';
    const im = mk('img', 'photo'); im.src = src; im.decoding = 'sync';
    wrap.appendChild(im);
    if (grade) { const g = mk('div', 'layer photo-grade'); wrap.appendChild(g); }
    if (dark > 0) { const g = mk('div', 'layer'); g.style.background = `rgba(22,28,31,${dark})`; wrap.appendChild(g); }
    return this.add(wrap, (tl) => {
      const p = prog(tl, t0, t1, ease.linear);
      const s = lerp(from.s, to.s, p), x = lerp(from.x, to.x, p), y = lerp(from.y, to.y, p);
      im.style.transform = `translate(${x}%, ${y}%) scale(${s})`;
      if (blur) im.style.filter = `blur(${blur}px)`;
      let o = opacity;
      if (fade[0]) o *= prog(tl, 0, fade[0], ease.outCubic);
      if (fade[1]) o *= 1 - prog(tl, this.dur - fade[1], this.dur, ease.inCubic);
      wrap.style.opacity = o.toFixed(3);
    });
  }
  // Panel grafito (o crema) que entra desde la izquierda con clip.
  panel({ x, y, w, h, at = 0, dur = .6, out = null, cream = false, radius = 6 }) {
    const d = mk('div', cream ? 'panel-cream' : 'panel');
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', borderRadius: radius + 'px' });
    this.ev(at, 'panel');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + dur, ease.outExpo);
      let o = 1, sx = lerp(-40, 0, p);
      d.style.clipPath = `inset(0 ${((1 - p) * 100).toFixed(2)}% 0 0 round ${radius}px)`;
      if (out) { const q = prog(tl, out[0], out[1], ease.inCubic); o = 1 - q; sx += q * 40; }
      d.style.opacity = o.toFixed(3);
      d.style.transform = `translateX(${sx.toFixed(2)}px)`;
    });
  }
  eyebrow({ x, y, text, at = 0, dur = .5, out = null, cream = false }) {
    const d = mk('div', 'abs eyebrow'); d.textContent = text;
    Object.assign(d.style, { left: x + 'px', top: y + 'px' });
    if (cream) d.style.color = '#9e3905';
    this.ev(at, 'tick', { soft: true });
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + dur, ease.outExpo);
      d.style.clipPath = `inset(-20% ${((1 - p) * 100).toFixed(2)}% -20% 0)`;
      d.style.transform = `translateX(${((1 - p) * -30).toFixed(2)}px)`;
      d.style.opacity = out ? (1 - prog(tl, out[0], out[1], ease.inCubic)).toFixed(3) : '1';
    });
  }
  // Titular palabra por palabra. lines: [["¿115", "o", "125?"], [...]]; hl: palabras naranja; dim: palabras apagadas.
  headline({ x, y, w = 936, size = 112, lines, hl = [], dim = [], at = 0, stagger = .085, wdur = .55, out = null, align = 'left', color = null, sound = 'word', lineGap = 1.0, weight = 800, from = 'up' }) {
    const d = mk('div', 'abs headline');
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', fontSize: size + 'px', textAlign: align, fontWeight: String(weight), lineHeight: String(lineGap) });
    if (color) d.style.color = color;
    const words = [];
    lines.forEach((line, li) => {
      const row = mk('div');
      line.forEach((word, wi) => {
        const s = mk('span', 'w' + (hl.includes(word) ? ' hl' : '') + (dim.includes(word) ? ' dim' : ''));
        s.textContent = word + (wi < line.length - 1 ? ' ' : '');
        row.appendChild(s);
        words.push(s);
      });
      d.appendChild(row);
    });
    words.forEach((s, i) => { const t = at + i * stagger; if (sound) this.ev(t, sound, { i, n: words.length, size }); });
    return this.add(d, (tl) => {
      words.forEach((s, i) => {
        const t0 = at + i * stagger;
        const p = prog(tl, t0, t0 + wdur, ease.outExpo);
        const ty = from === 'up' ? (1 - p) * size * .55 : from === 'down' ? (1 - p) * -size * .4 : 0;
        const tx = from === 'left' ? (1 - p) * -80 : 0;
        s.style.transform = `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(${lerp(.86, 1, p).toFixed(4)})`;
        s.style.opacity = p.toFixed(3);
        s.style.filter = p < 1 ? `blur(${((1 - p) * 14).toFixed(1)}px)` : 'none';
      });
      if (out) { const q = prog(tl, out[0], out[1], ease.inCubic); d.style.opacity = (1 - q).toFixed(3); d.style.transform = `translateY(${(-q * 40).toFixed(1)}px)`; }
      else { d.style.opacity = '1'; d.style.transform = 'none'; }
    });
  }
  // Texto genérico (html) con entrada.
  text({ x, y, w = 936, size = 40, html, cls = 'sub', at = 0, dur = .6, out = null, from = 'up', align = 'left', color = null, weight = null, lineHeight = null, sound = null }) {
    const d = mk('div', 'abs ' + cls); d.innerHTML = html;
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', fontSize: size + 'px', textAlign: align });
    if (color) d.style.color = color; if (weight) d.style.fontWeight = String(weight); if (lineHeight) d.style.lineHeight = String(lineHeight);
    if (sound) this.ev(at, sound);
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + dur, ease.outExpo);
      const ty = from === 'up' ? (1 - p) * 50 : from === 'down' ? (1 - p) * -50 : 0;
      const tx = from === 'left' ? (1 - p) * -70 : from === 'right' ? (1 - p) * 70 : 0;
      let o = p;
      if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px)`;
      d.style.filter = p < 1 ? `blur(${((1 - p) * 8).toFixed(1)}px)` : 'none';
    });
  }
  sticker({ x, y, text, rot = -3, at = 0, light = false, out = null, size = 58 }) {
    const d = mk('div', 'sticker' + (light ? ' light' : '')); d.innerHTML = text;
    Object.assign(d.style, { left: x + 'px', top: y + 'px', fontSize: size + 'px' });
    this.ev(at, 'pop');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + .55, ease.outBack);
      let o = clamp(p * 2);
      if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      const wob = Math.sin((tl - at) * 2.2) * .8;
      d.style.opacity = o.toFixed(3);
      d.style.transform = `rotate(${(rot + wob + (1 - p) * -12).toFixed(2)}deg) scale(${p.toFixed(4)})`;
    });
  }
  // Fila de specs: etiqueta + dos valores. same=true → ambos valores gris; false → naranja.
  specRow({ x, y, w = 936, k, a, b, at = 0, same = true, cream = false, out = null, size = 38, sound = 'tick' }) {
    const d = mk('div', 'spec' + (cream ? ' cream' : ''));
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px' });
    const ke = mk('div', 'k'); ke.textContent = k;
    const ae = mk('div', 'v ' + (same ? 'same' : 'diff')); ae.innerHTML = a; ae.style.fontSize = size + 'px';
    const be = mk('div', 'v ' + (same ? 'same' : 'diff')); be.innerHTML = b; be.style.fontSize = size + 'px';
    if (b === null || b === undefined) { be.style.display = 'none'; d.style.gridTemplateColumns = '1fr auto'; }
    d.append(ke, ae, be);
    if (sound) this.ev(at, sound, { same });
    if (!same) this.ev(at + .12, 'alert');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + .55, ease.outExpo);
      let o = p;
      if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `translateX(${((1 - p) * 90).toFixed(2)}px)`;
      // los valores entran un pelo después
      const q = prog(tl, at + .12, at + .6, ease.outExpo);
      ae.style.opacity = be.style.opacity = q.toFixed(3);
      ae.style.transform = be.style.transform = `translateY(${((1 - q) * 18).toFixed(1)}px)`;
      // pulso naranja en diferencias
      if (!same) { const pulse = clamp(1 - (tl - at - .15) / .5); d.style.background = `rgba(255,90,10,${(.18 * Math.max(0, pulse)).toFixed(3)})`; }
    });
  }
  // Número que cuenta. fmt(v) opcional.
  counter({ x, y, w = 936, from = 0, to, unit = '', at = 0, dur = 1.1, size = 220, decimals = 0, align = 'left', color = '#fff', out = null, prefix = '', unitSize = null }) {
    const d = mk('div', 'abs mono');
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', fontSize: size + 'px', textAlign: align, color, lineHeight: '1' });
    const n = mk('span'); const u = mk('span'); u.style.fontSize = (unitSize || size * .42) + 'px'; u.style.marginLeft = '.15em'; u.style.color = 'var(--orange)'; u.style.fontWeight = '600';
    u.textContent = unit; d.append(n, u);
    this.ev(at, 'count', { dur });
    this.ev(at + dur, 'tick');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + dur, ease.outExpo);
      n.textContent = prefix + fmtNum(lerp(from, to, p), decimals);
      let o = prog(tl, at, at + .3);
      if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `scale(${lerp(.9, 1, prog(tl, at, at + .6, ease.outExpo)).toFixed(4)})`;
      d.style.transformOrigin = align === 'center' ? '50% 50%' : '0 50%';
    });
  }
  chip({ x, y, text, kind = 'orange', at = 0, out = null, rot = 0, size = 30 }) {
    const d = mk('div', 'abs chip ' + kind); d.innerHTML = text;
    Object.assign(d.style, { left: x + 'px', top: y + 'px', fontSize: size + 'px' });
    this.ev(at, 'tick');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + .5, ease.outBack);
      let o = clamp(p * 2); if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `rotate(${rot}deg) scale(${p.toFixed(4)})`;
    });
  }
  btn({ x, y, text, at = 0, w = null }) {
    const d = mk('div', 'abs btn'); d.innerHTML = text + ' <span style="font-size:1.2em;line-height:0">→</span>';
    Object.assign(d.style, { left: x + 'px', top: y + 'px' }); if (w) { d.style.width = w + 'px'; }
    this.ev(at, 'pop');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + .6, ease.outBack);
      d.style.opacity = clamp(p * 2).toFixed(3);
      d.style.transform = `scale(${p.toFixed(4)})`;
      const glow = .5 + .5 * Math.sin((tl - at) * 3.5);
      d.style.boxShadow = `0 ${12 + glow * 6}px ${30 + glow * 20}px rgba(255,90,10,${(.35 + glow * .25).toFixed(2)})`;
    });
  }
  // Ítem de checklist con tilde que se dibuja.
  check({ x, y, w = 900, text, at = 0, bad = false, out = null, size = 40, color = null }) {
    const d = mk('div', 'abs check' + (bad ? ' bad' : ''));
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', fontSize: size + 'px' });
    if (color) d.style.color = color;
    const box = mk('div', 'box');
    const path = bad ? 'M7 7 L27 27 M27 7 L7 27' : 'M6 18 L14 26 L29 8';
    box.innerHTML = `<svg viewBox="0 0 34 34" fill="none" stroke="${bad ? '#e11d48' : '#ff5a0a'}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="${path}" pathLength="1"/></svg>`;
    const pth = box.querySelector('path');
    const tx = mk('div'); tx.innerHTML = text;
    d.append(box, tx);
    this.ev(at, 'tick'); this.ev(at + .25, bad ? 'buzz' : 'check');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + .5, ease.outExpo);
      const q = prog(tl, at + .25, at + .6, ease.outCubic);
      let o = p; if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `translateX(${((1 - p) * -60).toFixed(2)}px)`;
      pth.style.strokeDasharray = '1'; pth.style.strokeDashoffset = String(1 - q);
      box.style.background = bad ? `rgba(225,29,72,${(.18 * q).toFixed(3)})` : `rgba(255,90,10,${(.18 * q).toFixed(3)})`;
    });
  }
  // Barra horizontal que crece (diagramas de medidas).
  bar({ x, y, w, h = 14, at = 0, dur = .7, color = 'var(--orange)', out = null, label = null, labelSize = 30, labelColor = '#fff' }) {
    const d = mk('div', 'abs'); Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: color, borderRadius: '3px', transformOrigin: '0 50%' });
    let lab = null;
    if (label) { lab = mk('div', 'abs mono'); lab.innerHTML = label; Object.assign(lab.style, { left: x + 'px', top: (y - labelSize - 14) + 'px', width: w + 'px', textAlign: 'center', fontSize: labelSize + 'px', color: labelColor, whiteSpace: 'nowrap' }); this.el.appendChild(lab); }
    this.ev(at, 'slide', { dur });
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + dur, ease.outExpo);
      let o = 1; if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.transform = `scaleX(${p.toFixed(4)})`; d.style.opacity = o.toFixed(3);
      if (lab) { const q = prog(tl, at + dur * .5, at + dur + .2, ease.outCubic); lab.style.opacity = (q * o).toFixed(3); lab.style.transform = `translateY(${((1 - q) * 14).toFixed(1)}px)`; }
    });
  }
  // Disco de amoladora dibujado en SVG. kind: cut | grind | flap | diamond. angle(tl) en grados.
  disc({ x, y, r = 300, kind = 'cut', angle = () => 0, at = 0, out = null, tilt = 0, label = null, scaleIn = true }) {
    const d = mk('div', 'abs'); Object.assign(d.style, { left: (x - r) + 'px', top: (y - r) + 'px', width: 2 * r + 'px', height: 2 * r + 'px' });
    d.innerHTML = discSVG(kind, r);
    const rot = d.querySelector('.rot');
    this.ev(at, 'disc');
    return this.add(d, (tl) => {
      const p = scaleIn ? prog(tl, at, at + .7, ease.outBack) : 1;
      let o = clamp(p * 2); if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `perspective(1600px) rotateX(${tilt}deg) scale(${p.toFixed(4)})`;
      rot.setAttribute('transform', `rotate(${(angle(tl) % 360).toFixed(2)} ${r} ${r})`);
    });
  }
  // Chispas: canvas determinista. origin {x,y}, dir en radianes (hacia dónde vuelan), activo [t0,t1].
  sparks({ x, y, t0 = 0, t1 = this.dur, dir = -Math.PI / 4, spread = .55, rate = 180, speed = 1500, seed = 7, gravity = 2600, life = .55, size = 1 }) {
    const c = mk('canvas'); c.width = 1080; c.height = 1920; c.className = 'layer';
    const ctx = c.getContext('2d');
    const N = Math.ceil(rate * (t1 - t0)) + 1;
    const R = rng(seed);
    const parts = [];
    for (let i = 0; i < N; i++) {
      const birth = t0 + (i / N) * (t1 - t0) + (R() - .5) * (1 / rate);
      const a = dir + (R() - .5) * 2 * spread;
      const v = speed * (.45 + R() * .9);
      parts.push({ birth, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: life * (.5 + R()), w: (R() < .2 ? 3.2 : 1.8) * size, bright: R() });
    }
    this.ev(t0, 'grind', { dur: t1 - t0 });
    return this.add(c, (tl) => {
      ctx.clearRect(0, 0, 1080, 1920);
      if (tl < t0 || tl > t1 + life) return;
      ctx.globalCompositeOperation = 'lighter';
      // halo en el punto de contacto
      const act = window_(tl, t0, t1 + .05, .08, .15);
      if (act > 0) {
        const g = ctx.createRadialGradient(x, y, 0, x, y, 120);
        g.addColorStop(0, `rgba(255,220,160,${(.95 * act).toFixed(3)})`); g.addColorStop(.25, `rgba(255,140,40,${(.55 * act).toFixed(3)})`); g.addColorStop(1, 'rgba(255,90,10,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, 120, 0, Math.PI * 2); ctx.fill();
      }
      for (const p of parts) {
        const age = tl - p.birth;
        if (age < 0 || age > p.life) continue;
        const k = age / p.life;
        const px = x + p.vx * age, py = y + p.vy * age + .5 * gravity * age * age;
        const px0 = x + p.vx * (age - .018), py0 = y + p.vy * (age - .018) + .5 * gravity * (age - .018) * (age - .018);
        const alpha = (1 - k) * (0.7 + .3 * p.bright);
        ctx.strokeStyle = k < .35 ? `rgba(255,235,190,${alpha.toFixed(3)})` : `rgba(255,${Math.round(150 - k * 90)},${Math.round(60 - k * 50)},${alpha.toFixed(3)})`;
        ctx.lineWidth = p.w * (1 - k * .5); ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(px0, py0); ctx.lineTo(px, py); ctx.stroke();
      }
      ctx.globalCompositeOperation = 'source-over';
    });
  }
  // Elemento libre con función de actualización.
  custom(el, update) { return this.add(el, update); }
  // Línea fina horizontal (separador) que se dibuja.
  rule({ x, y, w, at = 0, color = 'rgba(255,255,255,.14)', h = 2 }) {
    const d = mk('div', 'abs'); Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: color, transformOrigin: '0 50%' });
    return this.add(d, (tl) => { d.style.transform = `scaleX(${prog(tl, at, at + .6, ease.outExpo).toFixed(4)})`; });
  }
  // Tarjeta de producto: foto sobre crema + nombre + chips de datos.
  productCard({ x, y, w = 440, h = 560, src, name, data = [], at = 0, out = null, rot = 0 }) {
    const d = mk('div', 'abs');
    Object.assign(d.style, { left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', background: 'var(--cream-2)', borderRadius: '8px', borderTop: '8px solid var(--orange)', boxShadow: '0 30px 60px rgba(0,0,0,.45)', overflow: 'hidden', color: 'var(--ink)' });
    const ph = mk('div'); Object.assign(ph.style, { position: 'absolute', left: '24px', right: '24px', top: '24px', height: (h * .5) + 'px', background: '#fff', border: '1px solid #e9e6df', borderRadius: '4px', display: 'grid', placeItems: 'center', overflow: 'hidden' });
    const im = mk('img'); im.src = src; Object.assign(im.style, { maxWidth: '92%', maxHeight: '92%', objectFit: 'contain' }); ph.appendChild(im);
    const nm = mk('div'); nm.innerHTML = name; Object.assign(nm.style, { position: 'absolute', left: '24px', right: '24px', top: (h * .5 + 44) + 'px', fontSize: '34px', fontWeight: '800', letterSpacing: '-.03em', lineHeight: '1.1', color: '#242c2e' });
    const dl = mk('div'); Object.assign(dl.style, { position: 'absolute', left: '24px', right: '24px', bottom: '22px', display: 'flex', flexWrap: 'wrap', gap: '10px' });
    data.forEach(t => { const s = mk('span'); s.textContent = t; Object.assign(s.style, { fontFamily: "'JetBrains Mono', monospace", fontSize: '23px', fontWeight: '700', background: '#efece5', border: '1px solid #ddd8cf', padding: '6px 10px', borderRadius: '3px', color: '#3d4648' }); dl.appendChild(s); });
    d.append(ph, nm, dl);
    this.ev(at, 'card');
    return this.add(d, (tl) => {
      const p = prog(tl, at, at + .7, ease.outExpo);
      let o = p; if (out) o *= 1 - prog(tl, out[0], out[1], ease.inCubic);
      d.style.opacity = o.toFixed(3);
      d.style.transform = `translateY(${((1 - p) * 120).toFixed(1)}px) rotate(${(rot * p).toFixed(2)}deg) scale(${lerp(.92, 1, p).toFixed(4)})`;
      im.style.transform = `scale(${lerp(1.15, 1, prog(tl, at, at + 1.4, ease.outCubic)).toFixed(4)})`;
    });
  }
  // Logo grande (cierre).
  logo({ x, y, w = 760, at = 0, src = '../../assets/logo_dark.png' }) {
    const im = mk('img', 'abs'); im.src = src; Object.assign(im.style, { left: x + 'px', top: y + 'px', width: w + 'px', filter: 'drop-shadow(0 20px 40px rgba(0,0,0,.55))' });
    this.ev(at, 'logo');
    return this.add(im, (tl) => {
      const p = prog(tl, at, at + .9, ease.outExpo);
      im.style.opacity = p.toFixed(3);
      im.style.transform = `translateY(${((1 - p) * 40).toFixed(1)}px) scale(${lerp(.94, 1, p).toFixed(4)})`;
    });
  }
}

function mk(tag, cls) { const e = document.createElement(tag); if (cls) e.className = cls; return e; }

// Grano: ruido monocromo en canvas → dataURL.
function makeGrain(n) {
  const c = document.createElement('canvas'); c.width = n; c.height = n;
  const ctx = c.getContext('2d'); const img = ctx.createImageData(n, n);
  const R = rng(1234);
  for (let i = 0; i < img.data.length; i += 4) { const v = 90 + R() * 120; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
  ctx.putImageData(img, 0, 0);
  return c.toDataURL('image/png');
}

// Disco de amoladora en SVG. El grupo .rot gira.
function discSVG(kind, r) {
  const cx = r, cy = r;
  const R = r * .96, hole = r * .12, flange = r * .26;
  let body = '';
  const defs = `
  <defs>
    <radialGradient id="gCut" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#3a3f42"/><stop offset=".55" stop-color="#2a2f32"/><stop offset=".97" stop-color="#4a5054"/><stop offset="1" stop-color="#1a1e20"/></radialGradient>
    <radialGradient id="gGrind" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#5a5248"/><stop offset=".6" stop-color="#3b3733"/><stop offset=".97" stop-color="#5f574e"/><stop offset="1" stop-color="#1c1a18"/></radialGradient>
    <radialGradient id="gFlap" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#8a4a2a"/><stop offset=".7" stop-color="#a65a30"/><stop offset="1" stop-color="#4a2a18"/></radialGradient>
    <radialGradient id="gDia" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#b9c0c4"/><stop offset=".7" stop-color="#8f979b"/><stop offset=".92" stop-color="#d8dde0"/><stop offset="1" stop-color="#5a6165"/></radialGradient>
    <radialGradient id="gFl" cx="40%" cy="38%" r="60%"><stop offset="0" stop-color="#f1f3f4"/><stop offset=".6" stop-color="#9aa3a7"/><stop offset="1" stop-color="#4c5457"/></radialGradient>
    <pattern id="grit" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="rgba(255,255,255,.08)"/><circle cx="4.5" cy="4" r=".8" fill="rgba(0,0,0,.25)"/></pattern>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="30" stdDeviation="28" flood-color="#000" flood-opacity=".55"/></filter>
  </defs>`;
  if (kind === 'cut' || kind === 'grind') {
    const fill = kind === 'cut' ? 'url(#gCut)' : 'url(#gGrind)';
    const ring = kind === 'grind' ? `<circle cx="${cx}" cy="${cy}" r="${R * .55}" fill="none" stroke="rgba(0,0,0,.35)" stroke-width="${r * .06}"/>` : '';
    let spokes = '';
    for (let i = 0; i < 36; i++) { const a = (i / 36) * Math.PI * 2; spokes += `<line x1="${cx + Math.cos(a) * R * .3}" y1="${cy + Math.sin(a) * R * .3}" x2="${cx + Math.cos(a) * R * .98}" y2="${cy + Math.sin(a) * R * .98}" stroke="rgba(255,255,255,${i % 3 === 0 ? .05 : .025})" stroke-width="${r * .01}"/>`; }
    const label = kind === 'cut'
      ? `<text x="${cx}" y="${cy - R * .62}" text-anchor="middle" font-family="'Plus Jakarta Sans'" font-weight="800" font-size="${r * .11}" fill="#ff874b" letter-spacing="${r * .01}">METAL · CORTE</text>`
      : `<text x="${cx}" y="${cy - R * .62}" text-anchor="middle" font-family="'Plus Jakarta Sans'" font-weight="800" font-size="${r * .11}" fill="#ff874b" letter-spacing="${r * .01}">DESBASTE</text>`;
    body = `<g class="rot"><circle cx="${cx}" cy="${cy}" r="${R}" fill="${fill}"/><circle cx="${cx}" cy="${cy}" r="${R}" fill="url(#grit)"/>${spokes}${ring}
      <circle cx="${cx}" cy="${cy}" r="${R * .72}" fill="none" stroke="#ff5a0a" stroke-width="${r * .035}" stroke-dasharray="${r * .5} ${r * .12}" opacity=".85"/>
      ${label}
      <text x="${cx}" y="${cy + R * .72}" text-anchor="middle" font-family="'JetBrains Mono'" font-weight="700" font-size="${r * .085}" fill="#d9dedd">115 × ${kind === 'cut' ? '1,0' : '6,0'} × 22,23 mm</text>
      <circle cx="${cx}" cy="${cy}" r="${flange}" fill="url(#gFl)"/><circle cx="${cx}" cy="${cy}" r="${hole}" fill="#15191b"/>
      ${[0, 1, 2, 3].map(i => { const a = i * Math.PI / 2 + .4; return `<circle cx="${cx + Math.cos(a) * flange * .68}" cy="${cy + Math.sin(a) * flange * .68}" r="${r * .02}" fill="#2a2f32"/>`; }).join('')}
    </g>`;
  } else if (kind === 'flap') {
    let flaps = '';
    const n = 72;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      const x1 = cx + Math.cos(a) * R * .42, y1 = cy + Math.sin(a) * R * .42;
      const x2 = cx + Math.cos(a + .32) * R, y2 = cy + Math.sin(a + .32) * R;
      const x3 = cx + Math.cos(a + .40) * R, y3 = cy + Math.sin(a + .40) * R;
      const x4 = cx + Math.cos(a + .10) * R * .42, y4 = cy + Math.sin(a + .10) * R * .42;
      const shade = i % 2 ? '#a65a30' : '#8c4825';
      flaps += `<path d="M${x1} ${y1} L${x2} ${y2} L${x3} ${y3} L${x4} ${y4} Z" fill="${shade}" stroke="rgba(0,0,0,.35)" stroke-width="1.5"/>`;
    }
    body = `<g class="rot"><circle cx="${cx}" cy="${cy}" r="${R}" fill="url(#gFlap)"/>${flaps}<circle cx="${cx}" cy="${cy}" r="${R * .44}" fill="#2b2a28"/><circle cx="${cx}" cy="${cy}" r="${R * .44}" fill="url(#grit)"/>
      <text x="${cx}" y="${cy - R * .2}" text-anchor="middle" font-family="'Plus Jakarta Sans'" font-weight="800" font-size="${r * .1}" fill="#ff874b">FLAP</text>
      <text x="${cx}" y="${cy + R * .3}" text-anchor="middle" font-family="'JetBrains Mono'" font-weight="700" font-size="${r * .085}" fill="#d9dedd">GRANO 60 · T29</text>
      <circle cx="${cx}" cy="${cy}" r="${flange * .8}" fill="url(#gFl)"/><circle cx="${cx}" cy="${cy}" r="${hole}" fill="#15191b"/></g>`;
  } else {
    let seg = '';
    const n = 12;
    for (let i = 0; i < n; i++) { const a0 = (i / n) * Math.PI * 2, a1 = a0 + (Math.PI * 2 / n) * .8; seg += `<path d="M${cx + Math.cos(a0) * R * .86} ${cy + Math.sin(a0) * R * .86} A${R * .86} ${R * .86} 0 0 1 ${cx + Math.cos(a1) * R * .86} ${cy + Math.sin(a1) * R * .86} L${cx + Math.cos(a1) * R} ${cy + Math.sin(a1) * R} A${R} ${R} 0 0 0 ${cx + Math.cos(a0) * R} ${cy + Math.sin(a0) * R} Z" fill="#6b7276" stroke="#2c3134" stroke-width="2"/>`; }
    body = `<g class="rot"><circle cx="${cx}" cy="${cy}" r="${R * .87}" fill="url(#gDia)"/>${seg}
      <text x="${cx}" y="${cy - R * .5}" text-anchor="middle" font-family="'Plus Jakarta Sans'" font-weight="800" font-size="${r * .1}" fill="#20272b">DIAMANTADO</text>
      <text x="${cx}" y="${cy + R * .62}" text-anchor="middle" font-family="'JetBrains Mono'" font-weight="700" font-size="${r * .08}" fill="#20272b">HORMIGÓN · SEGMENTADO</text>
      <circle cx="${cx}" cy="${cy}" r="${hole}" fill="#15191b"/></g>`;
  }
  return `<svg viewBox="0 0 ${2 * r} ${2 * r}" width="${2 * r}" height="${2 * r}" style="overflow:visible"><g filter="url(#sh)">${defs}${body}</g></svg>`;
}

export const fmt = fmtNum;
