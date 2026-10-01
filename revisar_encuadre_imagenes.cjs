const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});try{
 const page=await browser.newPage({viewport:{width:1100,height:900}});
 await page.goto((process.env.QA_BASE_URL||'https://www.tallerlab.com.ar')+'/hidrolavadoras/');
 const card=page.locator('.card-media[href="/hidrolavadoras/bosch/"]').first();
 await card.scrollIntoViewIfNeeded();await card.locator('img').evaluate(async image=>{image.loading='eager';await image.decode();});
 console.log(JSON.stringify(await card.locator('img').evaluate(i=>{const s=getComputedStyle(i),r=i.getBoundingClientRect(),p=i.parentElement.getBoundingClientRect();return {src:i.src,natural:[i.naturalWidth,i.naturalHeight],box:[r.width,r.height],parent:[p.width,p.height],fit:s.objectFit,padding:s.padding,position:s.objectPosition,label:i.parentElement.textContent,css:document.querySelector('link[rel=stylesheet]').href};})));
 await card.screenshot({path:process.env.QA_SCREENSHOT||'vista-fotos/bosch-antes.png'});
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
