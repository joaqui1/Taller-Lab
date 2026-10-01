const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage();
  for(const width of [390,1100]){
   await page.setViewportSize({width,height:900});
   await page.goto((process.env.QA_BASE_URL||'http://127.0.0.1:5058')+'/taladros/inalambricos/');
   await page.locator('.buying-sources').scrollIntoViewIfNeeded();
   await page.screenshot({path:'vista-fotos/'+(process.env.QA_PREFIX||'local-')+'fuentes-'+width+'.png'});
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
