const { chromium } = require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'msedge'});
  const page = await browser.newPage({viewport: {width: 390, height: 844}, deviceScaleFactor: 1});
  const results = [];
  for (const category of ['taladros', 'compresores', 'hidrolavadoras', 'sierras', 'soldadoras', 'amoladoras', 'generadores']) {
    await page.goto('file:///' + path.resolve('vista-fotos', category + '.html').replace(/\\/g, '/'));
    const photo = page.locator('img[src*="/productos/"]').first();
    if (await photo.count()) {
      await photo.scrollIntoViewIfNeeded();
      await photo.evaluate(img => img.decode());
      await page.screenshot({path: 'vista-fotos/' + category + '-movil.png'});
    }
    const stats = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > innerWidth + 1,
      loaded: [...document.querySelectorAll('img[src*="/productos/"]')].filter(i => i.complete && i.naturalWidth > 0).length
    }));
    if (stats.overflow) throw new Error('Desborde horizontal: ' + category);
    results.push({category, ...stats});
  }
  console.log(JSON.stringify(results));
  await browser.close();
})();
