// Renderiza reel.html frame a frame con Playwright y lo entrega a ffmpeg.
// Uso:
//   node render.mjs --reel 1 --snap 0.8,2.5,6     -> fotogramas JPG de control en ../salida/control/
//   node render.mjs --reel 1 --video               -> ../salida/tmp/reel-1-video.mp4 + ../salida/tmp/reel-1-events.json
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) => a.startsWith('--') ? [a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true] : []).filter(Boolean));
const reel = +(args.reel || 1);
const FPS = 30;
const outDir = path.resolve(here, '..', 'salida');
const tmpDir = path.join(outDir, 'tmp');
const ctlDir = path.join(outDir, 'control');
mkdirSync(tmpDir, { recursive: true }); mkdirSync(ctlDir, { recursive: true });

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--font-render-hinting=none', '--disable-lcd-text'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('PAGE ERROR', e.message); });
await page.goto('file://' + path.join(here, 'reel.html') + `?reel=${reel}`);
await page.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
const meta = await page.evaluate(() => window.META);
const events = await page.evaluate(() => window.EVENTS);
console.log('reel', reel, meta.slug, 'dur', meta.dur, 'events', events.length);

writeFileSync(path.join(tmpDir, `reel-${reel}-events.json`), JSON.stringify({ meta, events }, null, 1));
if (args.snap) {
  for (const ts of String(args.snap).split(',')) {
    const t = parseFloat(ts);
    await page.evaluate(t => window.seek(t), t);
    const f = path.join(ctlDir, `reel-${reel}-${t.toFixed(2)}s.jpg`);
    await page.screenshot({ path: f, type: 'jpeg', quality: 90 });
    console.log('snap', f);
  }
}

if (args.video) {
  writeFileSync(path.join(tmpDir, `reel-${reel}-events.json`), JSON.stringify({ meta, events }, null, 1));
  const total = Math.round(meta.dur * FPS);
  const out = path.join(tmpDir, `reel-${reel}-video.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1', '-r', String(FPS), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = 0; i < total; i++) {
    const t = i / FPS;
    await page.evaluate(t => window.seek(t), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 96 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`reel ${reel}: frame ${i}/${total} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  console.log('video listo', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
await browser.close();
