const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});const page=await browser.newPage();
for(const width of [1100,390]){await page.setViewportSize({width,height:900});for(const category of ['hidrolavadoras','compresores','amoladoras','taladros','sierras','soldadoras','soldadura-electronica','generadores']){
 await page.goto('http://127.0.0.1:5058/'+category+'/');const first=page.locator('.card-thumb').first();await first.scrollIntoViewIfNeeded();await page.locator('.card-thumb img').evaluateAll(images=>Promise.all(images.map(async i=>{i.loading='eager';if(!i.complete)await new Promise((resolve,reject)=>{i.addEventListener('load',resolve,{once:true});i.addEventListener('error',()=>reject(new Error(i.src)),{once:true});});await i.decode();}))); await page.screenshot({path:'vista-fotos/portadas-'+category+'-'+width+'.png'});
 console.log(category,width,await page.locator('.card-thumb img').count());
}}await browser.close();})().catch(e=>{console.error(e);process.exitCode=1;});
