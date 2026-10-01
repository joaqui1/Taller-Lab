const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base=process.env.QA_BASE_URL||'http://127.0.0.1:5058';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  for(const [slug,path] of [['profesionales','/hidrolavadoras/profesionales/'],['bta25','/compresores/bta-25-litros/'],['stihl','/hidrolavadoras/stihl/']]){
   await page.goto(base+path,{waitUntil:'load'});
   const shelf=page.locator('[data-guide-comparison]');
   await shelf.locator('img').evaluateAll(async imgs=>{for(const img of imgs){img.loading='eager';await img.decode();}});
   await page.evaluate(()=>document.querySelector('body > header')?.remove());
   await shelf.screenshot({path:'vista-fotos/comparacion-'+slug+'-'+(process.env.QA_PREFIX||'local')+'.png'});
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
