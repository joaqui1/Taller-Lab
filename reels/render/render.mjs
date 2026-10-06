// Render de frames con Playwright (Chromium) a 1080×1920.
// Uso:
//   node render.mjs --out <dir> [--reel id,id] [--fps 30] [--preview 0.5,2,4.1]
// Para cada reel escribe <out>/<id>/f%05d.jpg y <out>/<id>.json (duración, fps, eventos de audio, música).

import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(process.argv.slice(2).map((a, i, arr) => a.startsWith('--') ? [a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true] : []).filter(Boolean));
const out = args.out || join(here, 'out');
const fps = Number(args.fps || 30);
const only = args.reel ? String(args.reel).split(',') : null;
const preview = args.preview ? String(args.preview).split(',').map(Number) : null;
const metaOnly = !!args['meta-only'];
mkdirSync(out, { recursive: true });

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--allow-file-access-from-files', '--font-render-hinting=none', '--disable-lcd-text', '--force-color-profile=srgb', '--hide-scrollbars'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('[page error]', e.message); });
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[console]', m.text()); });
await page.goto('file://' + join(here, 'engine.html'));
await page.waitForFunction(() => window.__ready === true);
const reels = await page.evaluate(() => window.listReels());

for (const r of reels) {
  if (only && !only.includes(r.id)) continue;
  const t0 = Date.now();
  const meta = await page.evaluate(id => window.loadReel(id), r.id);
  const dir = join(out, r.id);
  mkdirSync(dir, { recursive: true });
  if (preview) {
    for (const t of preview) {
      await page.evaluate(t => window.seek(t), t);
      await page.screenshot({ path: join(dir, `preview_${t.toFixed(2).replace('.', '_')}.png`), type: 'png' });
    }
    console.log(`${r.id}: ${preview.length} previews`);
    continue;
  }
  const n = Math.round(meta.duration * fps);
  for (let i = 0; i < n && !metaOnly; i++) {
    const t = i / fps;
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: join(dir, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 94 });
    if (i % 60 === 0) process.stdout.write(`\r${r.id}: ${i}/${n}`);
  }
  writeFileSync(join(out, `${r.id}.json`), JSON.stringify({ id: r.id, title: meta.title, duration: meta.duration, fps, music: meta.music, events: meta.events }, null, 1));
  console.log(`\r${r.id}: ${n} frames en ${((Date.now() - t0) / 1000).toFixed(1)}s`);
}
await browser.close();
