const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('fs');
const base=process.env.QA_BASE_URL||'http://127.0.0.1:5058';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const rows=[];
 try{
  for(const width of [320,390,1440]){
   const page=await browser.newPage({viewport:{width,height:1000}});
   await page.goto(base+'/hidrolavadoras/200-bar/');
   const shelf=page.locator('[data-guide-comparison]');
   assert.equal(await shelf.locator('.offer-card').count(),3);
   await shelf.locator('img').evaluateAll(async imgs=>{for(const img of imgs){img.loading='eager';await img.decode();}});
   const images=await shelf.locator('img').evaluateAll(imgs=>imgs.map(img=>({src:img.src,loaded:img.complete&&img.naturalWidth>0,fit:getComputedStyle(img).objectFit,box:[img.clientWidth,img.clientHeight],natural:[img.naturalWidth,img.naturalHeight]})));
   assert(images.every(img=>img.loaded&&img.fit==='contain'));
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   const checks=shelf.locator('.compare-checkbox');
   for(let i=0;i<3;i++)await checks.nth(i).check();
   assert.equal(await shelf.locator('.compare-panel table').count(),1);
   assert((await shelf.locator('.compare-panel').innerText()).includes('Emona'));
   await page.evaluate(()=>document.querySelector('body > header')?.remove());
   await shelf.screenshot({path:'vista-fotos/comparacion-200-bar-'+width+'-local.png'});
   rows.push({width,models:3,images,comparison:true});
   await page.close();
  }
  fs.writeFileSync('qa-comparacion-200-bar-local.json',JSON.stringify({base,failures:[],rows},null,2));
  console.log('OK: tres modelos, imágenes completas, sin desborde y comparación de tres en 320/390/1440.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
