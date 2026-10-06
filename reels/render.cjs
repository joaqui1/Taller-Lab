/* Renderiza los reels HTML a MP4 1080×1920 (30 fps) con Playwright + ffmpeg.
   Uso: node reels/render.cjs            → todos los reels
        node reels/render.cjs 01 03      → solo los que empiezan con esos prefijos
   Variables: FPS (30), POSTER_AT (segundos de la portada; por defecto la marca el propio reel con meta reel-poster). */
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const DIR = __dirname;
const OUT = path.join(DIR, 'salida');
const FPS = Number(process.env.FPS || 30);
const filters = process.argv.slice(2);
const files = fs.readdirSync(DIR).filter((f) => /^\d\d-.*\.html$/.test(f)).filter((f) => !filters.length || filters.some((p) => f.startsWith(p))).sort();
if (!files.length) { console.error('No hay reels que coincidan.'); process.exit(1); }
fs.mkdirSync(OUT, { recursive: true });

function ffmpeg(outFile) {
  const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
    '-r', String(FPS), '-movflags', '+faststart', outFile];
  const p = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  return p;
}

async function renderOne(browser, file) {
  const name = file.replace(/\.html$/, '');
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(DIR, file), { waitUntil: 'load' });
  await page.evaluate(() => window.__ready());
  const duration = await page.evaluate(() => window.__duration);
  const posterAt = Number(process.env.POSTER_AT || await page.evaluate(() => { const m = document.querySelector('meta[name="reel-poster"]'); return m ? m.content : 1.6; }));
  const frames = Math.round(duration / 1000 * FPS);
  const mp4 = path.join(OUT, name + '.mp4');
  const enc = ffmpeg(mp4);
  const done = new Promise((res, rej) => enc.on('close', (c) => (c === 0 ? res() : rej(new Error('ffmpeg salió con ' + c)))));
  const t0 = Date.now();
  for (let i = 0; i < frames; i++) {
    const ms = i * 1000 / FPS;
    await page.evaluate((t) => window.__seek(t), ms);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!enc.stdin.write(buf)) await new Promise((r) => enc.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`\r${name}: cuadro ${i}/${frames}`);
  }
  enc.stdin.end();
  await done;
  await page.evaluate((t) => window.__seek(t), posterAt * 1000);
  await page.screenshot({ type: 'jpeg', quality: 92, path: path.join(OUT, name + '-portada.jpg') });
  await page.close();
  console.log(`\r${name}: ${frames} cuadros · ${((Date.now() - t0) / 1000).toFixed(0)} s → ${path.relative(process.cwd(), mp4)}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const parallel = Number(process.env.PARALLEL || 2);
    const queue = files.slice();
    await Promise.all(Array.from({ length: parallel }, async () => { while (queue.length) await renderOne(browser, queue.shift()); }));
  } finally { await browser.close(); }
})().catch((e) => { console.error(e); process.exit(1); });
