const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base=process.env.QA_BASE_URL||'http://127.0.0.1:5058';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1100,height:950}});
  await page.goto(base+'/hidrolavadoras/profesionales/',{waitUntil:'load'});
  const shelf=page.locator('.affiliate-shelf');
  await shelf.scrollIntoViewIfNeeded();
  await shelf.locator('img').evaluateAll(async imgs=>{for(const img of imgs){img.loading='eager';await img.decode();}});
  await shelf.screenshot({path:'vista-fotos/opcion-profesional-'+(process.env.QA_PREFIX||'local')+'.png'});
  console.log(await shelf.locator('.affiliate-heading').innerText());
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
