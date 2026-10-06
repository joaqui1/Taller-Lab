// Definición de los 5 reels de amoladoras.
// Cada reel es una timeline absoluta (segundos) construida con los componentes del motor.
// Los datos salen de las guías publicadas en /paginas (fichas Bosch, Makita, Lüsqtoff citadas allí).

import { ease, prog, lerp, clamp } from './engine.js';

const A = '../../assets';
const PH = {
  amoladora: `${A}/editorial/amoladoras.webp`,
  discos: `${A}/editorial/discos.webp`,
  gws850: `${A}/productos/boschgws850-ac6f1144fb.webp`,
  gws30230: `${A}/productos/boschgws30230pb-fc54309c9e.webp`,
  gws180li: `${A}/productos/boschprofessionalgws180li-06d3c18175.webp`,
  ga9020: `${A}/productos/makitaga9020-f1228627b2.webp`,
  aml115: `${A}/productos/lusqtoffaml1159bk-8e9bdd13d3.webp`,
  ga4534: `${A}/productos/makitaga4534-235dbd4cb8.webp`,
};

// Velocidad angular con arranque exponencial: devuelve ángulo(tl).
const spin = (t0, maxDps = 420, accel = .9, dir = 1) => (tl) => {
  const dt = tl - t0; if (dt <= 0) return 0;
  return dir * maxDps * (dt - accel * (1 - Math.exp(-dt / accel)));
};
// Giro constante con frenado al final.
const spinBrake = (t0, tBrake, maxDps = 420, accel = .9) => (tl) => {
  const base = spin(t0, maxDps, accel)(Math.min(tl, tBrake));
  if (tl <= tBrake) return base;
  const dt = tl - tBrake; const tau = .7;
  return base + maxDps * tau * (1 - Math.exp(-dt / tau));
};

// Cierre común: logo, promesa editorial y URL.
function endCard(E, t0, t1, { path, line = ['Guía completa,', 'con fuentes.'], sub = 'Fichas de fabricante citadas. Sin opiniones inventadas.' }) {
  E.wipe(t0 + .1);
  E.shot(t0, t1, s => {
    s.bg('var(--graphite)');
    s.texture();
    s.logo({ x: 190, y: 560, w: 700, at: .15 });
    s.headline({ x: 72, y: 880, size: 104, lines: line.map(l => l.split(' ')), hl: ['fuentes.'], at: .45, stagger: .09, align: 'center', sound: 'word' });
    s.text({ x: 120, y: 1130, w: 840, size: 36, html: sub, at: 1.0, align: 'center', color: '#b5bfbd' });
    s.chip({ x: 540 - 420, y: 1270, text: `<span style="opacity:.75">tallerlab.com.ar</span>${path}`, kind: 'ghost', at: 1.15, size: 30 });
    s.btn({ x: 540 - 230, y: 1400, text: 'Leer la guía', at: 1.4, w: 460 });
  }, { z: 5 });
  // Centrar el chip (ancho desconocido): lo hacemos con un wrapper flexible.
  const last = E.shots[E.shots.length - 1];
  const chip = last.items.find(i => i.el.classList.contains('chip'));
  if (chip) { Object.assign(chip.el.style, { left: '72px', width: '936px', justifyContent: 'center', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0' }); }
}

export const REELS = [
  // ───────────────────────────────────────────────────────────── REEL 1
  {
    id: 'r1-115-o-125',
    title: '¿115 o 125? La diferencia no es la que te vendieron',
    duration: 16,
    fps: 30,
    music: { bpm: 100, root: 45, style: 'dark', drop: .62, outro: 13.3 },
    brand: { show: [.3, 13.4] },
    build(E) {
      E.event(0, 'riser', { dur: .62 });
      // A · Hook
      E.shot(0, 3.1, s => {
        s.bg(); s.photo({ src: PH.amoladora, from: { s: 1.25, x: 4, y: 2 }, to: { s: 1.08, x: 0, y: 0 }, dark: .25 });
        s.texture();
        s.eyebrow({ x: 72, y: 420, text: 'Amoladoras · 115 vs 125 mm', at: .2 });
        s.headline({ x: 72, y: 520, size: 210, lines: [['¿115'], ['o', '125?']], hl: ['125?'], at: .45, stagger: .09, lineGap: .92 });
        s.text({ x: 72, y: 1040, w: 900, size: 60, html: 'La diferencia <b style="color:#fff">no es</b><br>la que te vendieron.', at: 1.45, weight: 600, lineHeight: 1.15 });
        s.sticker({ x: 500, y: 1340, text: 'fichas Bosch,<br>no opiniones', rot: -4, at: 2.15, size: 54 });
      });
      E.impact(.63, { strength: 1.1, flash: .4 });
      E.wipe(3.05);

      // B · Tabla misma serie
      E.shot(2.95, 7.6, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1230, at: .05 });
        s.eyebrow({ x: 130, y: 390, text: 'Misma serie · Bosch GWS 9', at: .3 });
        s.text({ x: 130, y: 460, w: 860, size: 54, html: 'GWS 9-115 S <span style="color:#8f9a9c">vs</span> GWS 9-125 S', cls: 'headline', at: .4, weight: 800 });
        // encabezado de columnas
        s.text({ x: 130, y: 560, w: 860, size: 26, html: '<div style="display:flex;justify-content:flex-end;gap:40px;letter-spacing:.14em;color:#ff874b;font-weight:800"><span style="min-width:240px;text-align:right">9-115 S</span><span style="min-width:240px;text-align:right">9-125 S</span></div>', cls: '', at: .55 });
        const rows = [
          ['Potencia absorbida', '900 W', '900 W', true],
          ['Velocidad en vacío', '2.800–11.000', '2.800–11.000', true],
          ['Peso publicado', '1,9 kg', '1,9 kg', true],
          ['Rosca del eje', 'M14', 'M14', true],
          ['Tensión', '220–240 V', '220–240 V', true],
          ['Disco máximo', '115 mm', '125 mm', false],
        ];
        rows.forEach((r, i) => s.specRow({ x: 110, y: 610 + i * 118, w: 880, k: r[0], a: r[1], b: r[2], same: r[3], at: .75 + i * .32, size: r[1].length > 8 ? 30 : 38 }));
        s.sticker({ x: 500, y: 1330, text: 'lo único que cambia', rot: -5, at: 2.95, size: 52 });
        s.text({ x: 130, y: 1420, w: 840, size: 36, html: 'Igual motor, peso y rpm.<br><b style="color:#fff">Solo cambia el diámetro admitido.</b>', at: 3.3, lineHeight: 1.3 });
      });
      E.impact(2.95 + .75 + 5 * .32 + .1, { strength: .9, flash: .25, color: '#ff5a0a' });
      E.wipe(7.55);

      // C · 10 mm ≠ 5 mm
      E.shot(7.45, 11.0, s => {
        s.bg(); s.photo({ src: PH.discos, from: { s: 1.3, x: -3, y: -2 }, to: { s: 1.18, x: 0, y: 0 }, dark: .5, blur: 2 });
        s.texture();
        s.eyebrow({ x: 72, y: 380, text: 'Geometría vs realidad', at: .15 });
        s.bar({ x: 72, y: 560, w: 115 * 7.4, h: 26, at: .35, color: '#8f9a9c', label: 'Ø 115 mm', labelColor: '#c9d0cf' });
        s.bar({ x: 72, y: 660, w: 125 * 7.4, h: 26, at: .55, color: 'var(--orange)', label: 'Ø 125 mm', labelColor: '#ff874b' });
        s.headline({ x: 72, y: 780, size: 96, lines: [['+10', 'mm'], ['de', 'disco']], hl: ['+10', 'mm'], at: 1.0, stagger: .08 });
        s.headline({ x: 72, y: 1010, size: 230, lines: [['≠']], at: 1.65, stagger: 0, color: 'var(--orange)', sound: null, lineGap: .9 });
        s.headline({ x: 380, y: 1040, size: 96, lines: [['+5', 'mm'], ['de', 'corte']], dim: ['+5', 'mm'], at: 1.85, stagger: .08 });
        s.text({ x: 72, y: 1300, w: 900, size: 40, html: 'Guarda, brida y disco limitan la profundidad útil.<br>Las fichas <b style="color:#fff">no la informan</b>. Nadie te la puede prometer.', at: 2.5, lineHeight: 1.3 });
      });
      E.impact(7.45 + 1.68, { strength: 1.2, flash: .45, color: '#ff5a0a' });
      E.wipe(10.95);

      // D · Decisión
      E.shot(10.85, 13.5, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1100, at: .05, cream: true });
        s.eyebrow({ x: 130, y: 400, text: 'Decisión rápida', at: .3, cream: true });
        s.text({ x: 130, y: 470, w: 820, size: 66, html: 'Elegí por el trabajo,<br>no por la medida.', cls: 'headline', at: .4, color: '#242c2e', weight: 800, lineHeight: 1.02 });
        s.check({ x: 130, y: 680, w: 820, text: '<b>115</b> si el trabajo y los discos que ya usás son de 115.', at: .9, size: 38, color: '#394244' });
        s.check({ x: 130, y: 860, w: 820, text: '<b>125</b> si necesitás admitir ese disco y te aporta algo real.', at: 1.25, size: 38, color: '#394244' });
        s.check({ x: 130, y: 1040, w: 820, text: 'Montar un disco más grande que el admitido. <b>Nunca.</b>', at: 1.6, bad: true, size: 38, color: '#394244' });
        s.sticker({ x: 540, y: 1250, text: 'y compará peso y agarre', rot: -4, at: 2.0, size: 48 });
      });

      // E · Cierre
      endCard(E, 13.4, 16, { path: '/amoladoras/115-o-125/' });
    },
  },

  // ───────────────────────────────────────────────────────────── REEL 2
  {
    id: 'r2-watts',
    title: '900 W vs 1.200 W: ¿cuál corta más rápido? Nadie lo midió',
    duration: 16,
    fps: 30,
    music: { bpm: 108, root: 50, style: 'punchy', drop: 1.3, outro: 13.3 },
    brand: { show: [.3, 13.4] },
    build(E) {
      E.event(0, 'riser', { dur: 1.25 });
      // A · Hook: contador 900 → 1.200 W
      E.shot(0, 3.2, s => {
        s.bg(); s.photo({ src: PH.amoladora, from: { s: 1.1, x: -3, y: 1 }, to: { s: 1.22, x: 2, y: -1 }, dark: .35 });
        s.texture();
        s.eyebrow({ x: 72, y: 400, text: 'Potencia nominal', at: .15 });
        s.counter({ x: 72, y: 520, from: 900, to: 1200, unit: 'W', at: .3, dur: 1.0, size: 250, color: '#fff' });
        s.headline({ x: 72, y: 860, size: 118, lines: [['¿Corta', 'más'], ['rápido?']], hl: ['rápido?'], at: 1.35, stagger: .09 });
        s.sticker({ x: 440, y: 1210, text: 'Nadie lo midió.', rot: -4, at: 2.25, size: 64 });
      });
      E.impact(1.3, { strength: 1.0, flash: .35 });
      E.impact(2.3, { strength: .6, flash: .2, color: '#ff5a0a', sound: 'thud' });
      E.wipe(3.15);

      // B · Tabla 9-125 S vs 12-125 S
      E.shot(3.05, 7.4, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1230, at: .05 });
        s.eyebrow({ x: 130, y: 390, text: 'Fichas Bosch Argentina · 125 mm', at: .3 });
        s.text({ x: 130, y: 460, w: 860, size: 54, html: 'GWS 9-125 S <span style="color:#8f9a9c">vs</span> GWS 12-125 S', cls: 'headline', at: .4, weight: 800 });
        s.text({ x: 130, y: 560, w: 860, size: 26, html: '<div style="display:flex;justify-content:flex-end;gap:40px;letter-spacing:.14em;color:#ff874b;font-weight:800"><span style="min-width:240px;text-align:right">9-125 S</span><span style="min-width:240px;text-align:right">12-125 S</span></div>', cls: '', at: .55 });
        const rows = [
          ['Potencia absorbida', '900 W', '1.200 W', false],
          ['Disco máximo', '125 mm', '125 mm', true],
          ['Velocidad en vacío', '2.800–11.000', '2.800–11.000', true],
          ['Tensión', '220 V', '220 V', true],
          ['Rosca del eje', 'M14', 'M14', true],
          ['Ritmo de corte medido', '—', '—', true],
        ];
        rows.forEach((r, i) => s.specRow({ x: 110, y: 610 + i * 118, w: 880, k: r[0], a: r[1], b: r[2], same: r[3], at: .75 + i * .32, size: r[1].length > 8 ? 30 : 38 }));
        s.sticker({ x: 520, y: 1330, text: 'ese dato no existe', rot: -5, at: 2.7, size: 52 });
        s.text({ x: 130, y: 1420, w: 840, size: 36, html: '+300 W nominales. Misma velocidad en vacío.<br><b style="color:#fff">Ningún dato de corte comparable.</b>', at: 3.1, lineHeight: 1.3 });
      });
      E.impact(3.05 + .85, { strength: .9, flash: .25, color: '#ff5a0a' });
      E.wipe(7.35);

      // C · Lo que engaña leído solo
      E.shot(7.25, 10.8, s => {
        s.bg(); s.photo({ src: PH.discos, from: { s: 1.15, x: 2, y: 0 }, to: { s: 1.28, x: -2, y: -2 }, dark: .6, blur: 3 });
        s.texture();
        s.eyebrow({ x: 72, y: 380, text: 'Leídos solos, engañan', at: .15 });
        s.headline({ x: 72, y: 470, size: 112, lines: [['Etiquetas'], ['que', 'no', 'prueban'], ['nada.']], hl: ['nada.'], at: .35, stagger: .08 });
        const chips = [['WATTS', 72, 920, -2], ['RPM EN VACÍO', 340, 920, 1.5], ['“PROFESIONAL”', 72, 1040, 1], ['“BRUSHLESS”', 560, 1040, -2], ['VOLTIOS · Ah', 72, 1160, -1.5], ['“ALTO RENDIMIENTO”', 460, 1160, 1]];
        chips.forEach((c, i) => s.chip({ x: c[1], y: c[2], text: c[0], kind: 'ghost', at: 1.15 + i * .18, rot: c[3], size: 32 }));
        // tachado animado sobre los chips
        const strike = document.createElement('div'); strike.className = 'abs';
        Object.assign(strike.style, { left: '60px', top: '900px', width: '960px', height: '330px' });
        strike.innerHTML = `<svg viewBox="0 0 960 330" width="960" height="330" fill="none" stroke="#e11d48" stroke-width="10" stroke-linecap="round"><path pathLength="1" d="M20 60 C 300 10, 700 110, 940 70 M20 180 C 300 130, 700 230, 940 190 M20 300 C 300 250, 700 350, 940 310"/></svg>`;
        const p = strike.querySelector('path');
        s.custom(strike, (tl) => { const q = prog(tl, 2.35, 3.1, ease.inOutCubic); p.style.strokeDasharray = '1'; p.style.strokeDashoffset = String(1 - q); strike.style.opacity = q > 0 ? '1' : '0'; });
        s.ev(2.35, 'scratch', { dur: .75 });
        s.text({ x: 72, y: 1300, w: 900, size: 40, html: 'Watts no prueban velocidad de corte. RPM en vacío no es rpm bajo carga.<br><b style="color:#fff">Voltios y Ah no dicen cuánto dura una carga.</b>', at: 2.6, lineHeight: 1.3 });
      });
      E.wipe(10.75);

      // D · Lo que sí importa
      E.shot(10.65, 13.5, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1130, at: .05, cream: true });
        s.eyebrow({ x: 130, y: 400, text: 'Lo que sí importa', at: .3, cream: true });
        s.text({ x: 130, y: 470, w: 820, size: 66, html: 'Compará esto<br>antes que los watts.', cls: 'headline', at: .4, color: '#242c2e', weight: 800, lineHeight: 1.02 });
        s.check({ x: 130, y: 680, w: 820, text: 'Diámetro y montaje del accesorio admitido.', at: .9, size: 36, color: '#394244' });
        s.check({ x: 130, y: 820, w: 820, text: 'RPM máx. del disco <b>≥</b> RPM de la máquina.', at: 1.2, size: 36, color: '#394244' });
        s.check({ x: 130, y: 960, w: 820, text: 'Guarda indicada, peso y agarre.', at: 1.5, size: 36, color: '#394244' });
        s.check({ x: 130, y: 1100, w: 820, text: 'Freno, arranque suave o rearranque: <b>solo si el manual lo dice</b>.', at: 1.8, size: 36, color: '#394244' });
        s.sticker({ x: 560, y: 1300, text: 'código exacto, siempre', rot: -4, at: 2.2, size: 46 });
      });

      endCard(E, 13.4, 16, { path: '/amoladoras/' });
    },
  },

  // ───────────────────────────────────────────────────────────── REEL 3
  {
    id: 'r3-disco-equivocado',
    title: 'Este disco NO es para cortar (y se ve igual)',
    duration: 17,
    fps: 30,
    music: { bpm: 96, root: 40, style: 'heavy', drop: .95, outro: 14.3 },
    brand: { show: [.3, 14.4] },
    build(E) {
      E.event(0, 'riser', { dur: .95 });
      E.event(.2, 'spinup', { dur: 1.6 });
      // A · Hook: disco de desbaste girando con chispas
      E.shot(0, 3.3, s => {
        s.bg('#15191b'); s.texture();
        s.disc({ x: 540, y: 1080, r: 360, kind: 'grind', angle: spin(.2, 460, .8), at: 0, tilt: 14 });
        s.sparks({ x: 540 + 300, y: 1080 + 250, t0: 1.0, t1: 2.75, dir: -.15, spread: .5, rate: 220, speed: 1600, seed: 3 });
        s.eyebrow({ x: 72, y: 380, text: 'Discos para amoladora', at: .15 });
        s.headline({ x: 72, y: 470, size: 128, lines: [['Este', 'disco'], ['NO', 'es', 'para'], ['cortar.']], hl: ['NO'], at: .4, stagger: .1 });
        s.sticker({ x: 110, y: 1500, text: 'y se ve igual que uno que sí', rot: -3, at: 2.3, size: 50 });
      });
      E.impact(.95, { strength: 1.2, flash: .45 });
      E.wipe(3.25);

      // B · Perfil corte vs desbaste (espesores reales)
      E.shot(3.15, 7.2, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1240, at: .05, cream: true });
        s.eyebrow({ x: 130, y: 400, text: 'Vistos de canto · escala real ×60', at: .3, cream: true });
        s.text({ x: 130, y: 470, w: 820, size: 62, html: 'Mismo diámetro.<br>Otro trabajo.', cls: 'headline', at: .4, color: '#242c2e', weight: 800, lineHeight: 1.02 });
        // perfiles: 1,0 mm → 60 px ; 6,0 mm → 360 px? demasiado; usamos ×36: 1,0→36px, 1,6→58px, 6,0→216px
        s.text({ x: 130, y: 690, w: 820, size: 30, html: '<span class="mono" style="color:#c2410c">CORTE</span> &nbsp;Bosch 2608619383 · 115 × <b>1,0</b> × 22,23 mm', cls: '', at: .9, color: '#394244', weight: 600 });
        s.bar({ x: 130, y: 740, w: 820, h: 36, at: 1.0, color: '#3a3f42' });
        s.text({ x: 130, y: 810, w: 820, size: 30, html: '<span class="mono" style="color:#c2410c">CORTE</span> &nbsp;Bosch PRO Metal · 115 × <b>1,6</b> × 22,23 mm', cls: '', at: 1.3, color: '#394244', weight: 600 });
        s.bar({ x: 130, y: 860, w: 820, h: 58, at: 1.4, color: '#3a3f42' });
        s.text({ x: 130, y: 940, w: 820, size: 30, html: '<span class="mono" style="color:#c2410c">DESBASTE</span> &nbsp;Bosch PRO Metal 2 608 600 218<br>115 × <b>6,0</b> × 22,23 mm · A 30 T BF', cls: '', at: 1.75, color: '#394244', weight: 600, lineHeight: 1.25 });
        s.bar({ x: 130, y: 1040, w: 820, h: 200, at: 1.85, dur: .9, color: 'var(--orange)' });
        s.text({ x: 130, y: 1280, w: 820, size: 38, html: 'El de corte es delgado para <b>separar</b>. El de desbaste es rígido y grueso para <b>quitar material</b>.<br><span style="color:#c2410c;font-weight:800">Ni cortar con el grueso, ni apoyar de canto el fino.</span>', at: 2.9, color: '#394244', lineHeight: 1.3 });
      });
      E.impact(3.15 + 1.9, { strength: .8, flash: .25, color: '#ff5a0a' });
      E.wipe(7.15);

      // C · Flap: grano y forma
      E.event(7.1, 'spinup', { dur: 1.2, soft: true });
      E.shot(7.05, 10.7, s => {
        s.bg(); s.texture();
        s.disc({ x: 300, y: 1260, r: 300, kind: 'flap', angle: spin(.1, 240, 1.0, -1), at: 0, tilt: 10 });
        s.eyebrow({ x: 72, y: 380, text: 'Disco flap · terminación', at: .15 });
        s.headline({ x: 72, y: 470, size: 104, lines: [['El', 'grano'], ['decide', 'el'], ['acabado.']], hl: ['grano'], at: .35, stagger: .09 });
        const rows = [['40', 'quita rebabas'], ['60', 'desbaste medio'], ['80', 'suaviza marcas'], ['120', 'acabado fino']];
        rows.forEach((r, i) => s.text({ x: 580, y: 920 + i * 96, w: 480, size: 36, html: `<span class="mono" style="color:var(--orange);font-size:52px;display:inline-block;min-width:110px">${r[0]}</span> ${r[1]}`, cls: '', at: 1.3 + i * .22, from: 'right', color: '#e6eae9', weight: 600, sound: 'tick' }));
        s.text({ x: 600, y: 1330, w: 440, size: 30, html: '<b style="color:#fff">T27</b> plano · 0–15°<br><b style="color:#fff">T29</b> cantos · 15–25°<br><span style="color:#8f9a9c">(referencia Norton)</span>', cls: 'sub', at: 2.4, lineHeight: 1.35 });
      });
      E.wipe(10.65);

      // D · Diamantado
      E.event(10.6, 'spinup', { dur: 1.0, soft: true });
      E.shot(10.55, 13.7, s => {
        s.bg('#15191b'); s.texture();
        s.disc({ x: 760, y: 1240, r: 320, kind: 'diamond', angle: spin(.1, 300, 1.0), at: 0, tilt: 12 });
        s.eyebrow({ x: 72, y: 380, text: 'Disco diamantado', at: .15 });
        s.headline({ x: 72, y: 470, size: 104, lines: [['«Diamantado»'], ['no', 'dice'], ['para', 'qué.']], hl: ['qué.'], at: .35, stagger: .09 });
        s.text({ x: 72, y: 900, w: 620, size: 38, html: 'Hormigón, ladrillo, cerámica o porcelanato: lo que vale es <b style="color:#fff">la ficha del disco</b>.', at: 1.4, lineHeight: 1.3 });
        s.sticker({ x: 72, y: 1120, text: 'si dice “azulejo”,<br>no es porcelanato', rot: -3, at: 2.0, size: 46 });
      });
      E.wipe(13.65);

      // E · Tres reglas
      E.shot(13.55, 15.6, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 820, at: .05, cream: true });
        s.eyebrow({ x: 130, y: 400, text: 'Antes de montar', at: .25, cream: true });
        s.text({ x: 130, y: 470, w: 820, size: 66, html: 'Tres reglas.<br>Sin excepción.', cls: 'headline', at: .35, color: '#242c2e', weight: 800, lineHeight: 1.02 });
        s.check({ x: 130, y: 680, w: 820, text: 'RPM máx. del disco <b>≥</b> rpm en vacío de la máquina.', at: .7, size: 38, color: '#394244' });
        s.check({ x: 130, y: 850, w: 820, text: 'Sin guarda. <b>Nunca.</b>', at: 1.0, bad: true, size: 38, color: '#394244' });
        s.check({ x: 130, y: 1000, w: 820, text: 'Disco más grande que el admitido. <b>Nunca.</b>', at: 1.3, bad: true, size: 38, color: '#394244' });
      });

      endCard(E, 15.5, 17, { path: '/amoladoras/discos/' });
    },
  },

  // ───────────────────────────────────────────────────────────── REEL 4
  {
    id: 'r4-230mm',
    title: '230 mm de disco no son 230 mm de corte',
    duration: 16,
    fps: 30,
    music: { bpm: 92, root: 36, style: 'cinematic', drop: 1.15, outro: 13.3 },
    brand: { show: [.3, 13.4] },
    build(E) {
      E.event(0, 'riser', { dur: 1.15 });
      // A · Hook
      E.shot(0, 3.3, s => {
        s.bg(); s.photo({ src: PH.amoladora, from: { s: 1.3, x: -6, y: 3 }, to: { s: 1.12, x: 0, y: 0 }, dark: .45 });
        s.texture();
        s.eyebrow({ x: 72, y: 400, text: 'Amoladora de 9 pulgadas', at: .15 });
        s.counter({ x: 72, y: 500, from: 115, to: 230, unit: 'mm', at: .3, dur: .85, size: 260 });
        s.text({ x: 72, y: 800, w: 900, size: 54, html: 'de disco.', at: 1.15, weight: 600, color: '#c9d0cf' });
        s.headline({ x: 72, y: 900, size: 118, lines: [['¿230', 'mm'], ['de', 'corte?']], hl: ['corte?'], at: 1.45, stagger: .1 });
        s.sticker({ x: 520, y: 1270, text: 'Ni cerca.', rot: -5, at: 2.35, size: 72 });
      });
      E.impact(1.15, { strength: 1.1, flash: .4 });
      E.impact(2.4, { strength: .7, flash: .25, color: '#ff5a0a', sound: 'thud' });
      E.wipe(3.25);

      // B · El radio que no existe
      E.shot(3.15, 7.6, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1240, at: .05 });
        s.eyebrow({ x: 130, y: 400, text: 'El radio que no existe', at: .3 });
        s.text({ x: 130, y: 470, w: 820, size: 60, html: 'Radio geométrico: 115 mm.<br><span style="color:#8f9a9c">Radio que corta: menos.</span>', cls: 'headline', at: .4, weight: 800, lineHeight: 1.05 });
        const K = 7.0; // px por mm
        s.bar({ x: 130, y: 740, w: 115 * K, h: 44, at: .9, color: 'var(--orange)', label: 'radio 115 mm', labelColor: '#ff874b' });
        // lo que se come el radio
        s.bar({ x: 130, y: 740, w: 34 * K, h: 44, at: 1.6, color: '#3a3f42', label: null });
        s.text({ x: 130, y: 800, w: 300, size: 26, html: 'eje y cuerpo', cls: 'mono', at: 1.75, color: '#c9d0cf' });
        s.bar({ x: 130 + 34 * K, y: 740, w: 18 * K, h: 44, at: 2.1, color: '#5a6165', label: null });
        s.text({ x: 130 + 34 * K, y: 800, w: 300, size: 26, html: 'guarda', cls: 'mono', at: 2.25, color: '#c9d0cf' });
        s.bar({ x: 130 + 52 * K, y: 740, w: 14 * K, h: 44, at: 2.6, color: '#7c858a', label: null });
        s.text({ x: 130 + 52 * K, y: 800, w: 300, size: 26, html: 'desgaste', cls: 'mono', at: 2.75, color: '#c9d0cf' });
        s.text({ x: 130, y: 900, w: 820, size: 34, html: '<span style="color:#8f9a9c">Proporciones ilustrativas. La cifra real depende del cabezal, la guarda, el disco y la pieza.</span>', cls: 'sub', at: 3.0, lineHeight: 1.3 });
        s.headline({ x: 130, y: 1060, size: 78, lines: [['La', 'ficha'], ['no', 'publica'], ['la', 'profundidad.']], hl: ['profundidad.'], at: 3.2, stagger: .08 });
        s.sticker({ x: 540, y: 1400, text: 'no la calcules restando', rot: -4, at: 3.9, size: 46 });
      });
      E.impact(3.15 + 3.3, { strength: .8, flash: .25, color: '#ff5a0a' });
      E.wipe(7.55);

      // C · 180 vs 230
      E.shot(7.45, 10.7, s => {
        s.bg(); s.photo({ src: PH.discos, from: { s: 1.2, x: 2, y: 2 }, to: { s: 1.3, x: -1, y: -1 }, dark: .55, blur: 2 });
        s.texture();
        s.eyebrow({ x: 72, y: 380, text: '7 vs 9 pulgadas', at: .15 });
        s.bar({ x: 72, y: 560, w: 180 * 3.9, h: 26, at: .35, color: '#8f9a9c', label: 'Ø 180 mm', labelColor: '#c9d0cf' });
        s.bar({ x: 72, y: 660, w: 230 * 3.9, h: 26, at: .55, color: 'var(--orange)', label: 'Ø 230 mm', labelColor: '#ff874b' });
        s.headline({ x: 72, y: 790, size: 92, lines: [['+50', 'mm', 'de', 'diámetro'], ['=', '+25', 'mm', 'de', 'radio']], hl: ['+50', '+25'], at: 1.0, stagger: .07 });
        s.headline({ x: 72, y: 1040, size: 150, lines: [['≠']], at: 1.9, stagger: 0, color: 'var(--orange)', sound: null, lineGap: .9 });
        s.headline({ x: 290, y: 1060, size: 92, lines: [['+25', 'mm', 'de'], ['profundidad']], dim: ['+25', 'mm', 'de', 'profundidad'], at: 2.05, stagger: .08 });
        s.text({ x: 72, y: 1320, w: 900, size: 38, html: 'Una de 230 no reemplaza automáticamente a una de 180.<br><b style="color:#fff">Cabezal, guarda, desgaste y pieza</b> deciden el alcance.', at: 2.6, lineHeight: 1.3 });
      });
      E.impact(7.45 + 1.92, { strength: 1.1, flash: .4, color: '#ff5a0a' });
      E.wipe(10.65);

      // D · Modelos documentados
      E.shot(10.55, 13.5, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1230, at: .05, cream: true });
        s.eyebrow({ x: 130, y: 400, text: 'Fichas consultadas · 230 mm', at: .25, cream: true });
        s.productCard({ x: 110, y: 480, w: 420, h: 520, src: PH.gws30230, name: 'Bosch GWS 30-230 PB', data: ['2.800 W', '6.500 rpm', '5,9 kg', 'KickBack Control', 'freno'], at: .5, rot: -1 });
        s.productCard({ x: 550, y: 480, w: 420, h: 520, src: PH.ga9020, name: 'Makita GA9020', data: ['2.200 W', '6.000 rpm', 'anti-reinicio'], at: .75, rot: 1 });
        s.specRow({ x: 110, y: 1040, w: 860, k: 'GWS 25-230', a: '2.500 W · 6.500 rpm · 5,9 kg', b: null, at: 1.3, cream: true, size: 30, same: true });
        s.text({ x: 130, y: 1170, w: 820, size: 38, html: 'Casi <b>6 kilos</b> en las manos. Controlar eso también es parte de la compra. Las funciones de seguridad, <b>solo si figuran en la ficha</b>.', at: 1.7, color: '#394244', lineHeight: 1.3 });
        s.sticker({ x: 560, y: 1390, text: '5,9 kg', rot: -6, at: 2.1, size: 64 });
      });

      endCard(E, 13.4, 16, { path: '/amoladoras/9-pulgadas/' });
    },
  },

  // ───────────────────────────────────────────────────────────── REEL 5
  {
    id: 'r5-cable-o-bateria',
    title: 'La inalámbrica más barata que viste no incluye batería',
    duration: 16,
    fps: 30,
    music: { bpm: 112, root: 43, style: 'bright', drop: 1.55, outro: 13.3 },
    brand: { show: [.3, 13.4] },
    build(E) {
      E.event(0, 'riser', { dur: 1.55 });
      // A · Hook
      E.shot(0, 3.3, s => {
        s.bg(); s.photo({ src: PH.amoladora, from: { s: 1.12, x: 3, y: -2 }, to: { s: 1.26, x: -2, y: 1 }, dark: .4 });
        s.texture();
        s.eyebrow({ x: 72, y: 400, text: 'Amoladoras inalámbricas', at: .15 });
        s.headline({ x: 72, y: 490, size: 104, lines: [['La', 'inalámbrica'], ['más', 'barata'], ['que', 'viste…']], at: .35, stagger: .1 });
        s.headline({ x: 72, y: 920, size: 124, lines: [['no', 'incluye'], ['batería.']], hl: ['batería.'], at: 1.6, stagger: .1, from: 'down' });
        s.sticker({ x: 560, y: 1300, text: 'ni cargador', rot: -5, at: 2.5, size: 60 });
      });
      E.impact(1.6, { strength: 1.1, flash: .4 });
      E.impact(2.55, { strength: .6, flash: .2, color: '#ff5a0a', sound: 'thud' });
      E.wipe(3.25);

      // B · Cuerpo solo vs kit
      E.shot(3.15, 7.6, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1240, at: .05, cream: true });
        s.eyebrow({ x: 130, y: 400, text: 'Lo que dice la ficha', at: .25, cream: true });
        s.text({ x: 130, y: 470, w: 820, size: 62, html: 'Cuerpo solo <span style="color:#8f9a9c">vs</span> kit.', cls: 'headline', at: .35, color: '#242c2e', weight: 800 });
        s.productCard({ x: 110, y: 590, w: 420, h: 600, src: PH.gws180li, name: 'Bosch GWS 180-LI', data: ['125 mm', '11.000 rpm', '1,6 kg s/bat.', '2,2 kg c/bat.'], at: .6, rot: -1 });
        s.productCard({ x: 550, y: 590, w: 420, h: 600, src: PH.aml115, name: 'Lüsqtoff AML115-9BK', data: ['115 mm', '18 V', '2 × 4 Ah', 'cargador'], at: .85, rot: 1 });
        s.chip({ x: 110, y: 1215, text: 'SIN BATERÍA NI CARGADOR', kind: 'cream', at: 1.6, size: 21 });
        s.chip({ x: 550, y: 1215, text: 'KIT: 2 BATERÍAS + CARGADOR', kind: 'orange', at: 1.85, size: 21 });
        s.text({ x: 130, y: 1320, w: 820, size: 38, html: 'Dos precios que <b>no se comparan entre sí</b> hasta sumar lo que falta. La misma marca vende la AML115-9B <b>sin</b> baterías.', at: 2.3, color: '#394244', lineHeight: 1.3 });
      });
      E.impact(3.15 + 1.65, { strength: .6, flash: .2, color: '#ff5a0a', sound: 'thud' });
      E.wipe(7.55);

      // C · El costo real
      E.shot(7.45, 10.9, s => {
        s.bg(); s.photo({ src: PH.amoladora, from: { s: 1.2, x: -2, y: 2 }, to: { s: 1.3, x: 2, y: -1 }, dark: .6, blur: 3 });
        s.texture();
        s.eyebrow({ x: 72, y: 380, text: 'El costo de entrada', at: .15 });
        const items = [['Cuerpo', .5], ['+ Batería compatible', .85], ['+ Cargador', 1.2], ['+ Discos', 1.55]];
        items.forEach((it, i) => s.headline({ x: 72, y: 470 + i * 150, size: 96, lines: [it[0].split(' ')], hl: i > 0 ? [it[0].split(' ')[0]] : [], at: it[1], stagger: .06, from: 'left' }));
        s.rule({ x: 72, y: 1080, w: 936, at: 1.95, color: 'var(--orange)', h: 8 });
        s.headline({ x: 72, y: 1130, size: 92, lines: [['=', 'el', 'precio'], ['que', 'se', 'compara.']], hl: ['compara.'], at: 2.1, stagger: .08 });
        s.text({ x: 72, y: 1400, w: 900, size: 38, html: '¿Ya tenés baterías de esa plataforma? Entonces la cuenta cambia. <b style="color:#fff">Si no, sumalo todo.</b>', at: 2.8, lineHeight: 1.3 });
      });
      E.impact(7.45 + 2.0, { strength: .9, flash: .3, color: '#ff5a0a' });
      E.wipe(10.85);

      // D · Decisión
      E.shot(10.75, 13.5, s => {
        s.bg('var(--graphite-3)'); s.texture({ vignette: false });
        s.panel({ x: 72, y: 330, w: 936, h: 1130, at: .05 });
        s.eyebrow({ x: 130, y: 400, text: 'Cable o batería', at: .25 });
        s.text({ x: 130, y: 470, w: 820, size: 64, html: 'Elegí por dónde<br>y cuánto trabajás.', cls: 'headline', at: .35, weight: 800, lineHeight: 1.02 });
        s.check({ x: 130, y: 690, w: 820, text: '<b>Cable</b> si trabajás cerca de una toma y en sesiones largas.', at: .8, size: 38 });
        s.check({ x: 130, y: 860, w: 820, text: '<b>Batería</b> si la movilidad vale lo que cuesta el pack completo.', at: 1.15, size: 38 });
        s.check({ x: 130, y: 1030, w: 820, text: 'Deducir autonomía de los <b>voltios o los Ah</b>. No se puede.', at: 1.5, bad: true, size: 38 });
        s.sticker({ x: 540, y: 1270, text: 'una 2ª batería<br>evita esperar', rot: -4, at: 1.95, size: 46 });
      });

      endCard(E, 13.4, 16, { path: '/amoladoras/inalambricas/' });
    },
  },
];
