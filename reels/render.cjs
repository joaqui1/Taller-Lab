// Render determinista: Playwright (frame a frame) -> ffmpeg. Uso: node render.cjs reel-01 [--preview N] [--fps 30]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');

const args = process.argv.slice(2);
const names = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const preview = opt('--preview', null);
const out = path.join(__dirname, 'salida');
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none', '--disable-lcd-text'] });
  for (const name of names) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => console.error('[page]', name, e.message));
    await page.goto('file://' + path.join(__dirname, 'src', name + '.html'));
    await page.evaluate(async () => { await document.fonts.ready; await Promise.all(Array.from(document.images).map(i => i.complete ? 1 : new Promise(r => { i.onload = r; i.onerror = r; }))); });
    const meta = await page.evaluate(() => window.__prepare());
    fs.writeFileSync(path.join(out, name + '.timeline.json'), JSON.stringify(meta, null, 1));
    const fps = +opt('--fps', meta.fps || 30); const total = Math.round(meta.dur * fps);
    console.log(`[${name}] ${meta.dur}s @${fps}fps = ${total} frames, ${meta.events.length} eventos`);
    if (preview) {
      const dir = path.join(out, 'preview-' + name); fs.mkdirSync(dir, { recursive: true });
      const n = +preview; 
      for (let i = 0; i < n; i++) {
        const t = (i + .5) * meta.dur / n;
        await page.evaluate(t => window.__seek(t), t);
        await page.screenshot({ path: path.join(dir, `f${String(i).padStart(2, '0')}_${t.toFixed(2)}.png`), type: 'png' });
      }
      await page.close(); continue;
    }
    const video = path.join(out, name + '.video.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', video]);
    ff.stderr.on('data', d => process.stderr.write(d));
    const t0 = Date.now();
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.__seek(t), i / fps);
      const buf = await page.screenshot({ type: 'jpeg', quality: 97 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) process.stdout.write(`\r[${name}] ${i}/${total} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log(`\n[${name}] video listo en ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
