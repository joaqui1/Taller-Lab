const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});try{
 const page=await browser.newPage({viewport:{width:1100,height:900}});
 await page.goto('https://www.tallerlab.com.ar/hidrolavadoras/');
 const card=page.locator('.card-media[href="/hidrolavadoras/comparativa-general/"]').first();
 await card.scrollIntoViewIfNeeded();await card.locator('img').evaluate(async image=>{image.loading='eager';await image.decode();});
 await card.screenshot({path:'vista-fotos/produccion-tarjeta-hidrolavadoras-real.png'});
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
