const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('assert');
const {spawn}=require('child_process');const readline=require('readline');
(async()=>{
const bridge=spawn('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['tests/comunidad_browser_bridge.py'],{env:{...process.env,PYTHONPATH:process.cwd()+';'+process.cwd()+'/.consultor-seo-deps;'+process.cwd()+'/tmp/auditoria-observatorio-deps'}});
bridge.stderr.on('data',d=>process.stderr.write(d));
const pending=[];readline.createInterface({input:bridge.stdout}).on('line',line=>pending.shift()(JSON.parse(line)));
const browser=await chromium.launch({headless:true,channel:'msedge'});
const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
const base='http://community.local', path='/comunidad/modelos/bosch-gsb-18v-50/';
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());
 if(url.origin!==base){await route.abort();return;}
 const result=await new Promise(resolve=>{pending.push(resolve);bridge.stdin.write(JSON.stringify({path:url.pathname+url.search,method:req.method(),body:req.postData(),type:req.headers()['content-type']})+'\n');});
 await route.fulfill({status:result.status,headers:result.headers,body:Buffer.from(result.body,'base64')});
});
for(const width of [390,1440]){
 await page.setViewportSize({width,height:900});
 for(const [name,route] of [['hub','/comunidad/'],['model',path],['guide','/taladros/bosch-inalambrico/'],['multi','/compresores/50-litros/'],['category','/amoladoras/'],['selector','/sierras/bosch-gks-150/']]){
  const res=await page.goto(base+route,{waitUntil:'networkidle'});assert.equal(res.status(),200);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'horizontal overflow '+route+' '+width);
  await page.screenshot({path:'tmp/community-'+name+'-'+width+'.png',fullPage:route.startsWith('/comunidad/')});
  if(!route.startsWith('/comunidad/')){
   // El acceso superior solo aparece cuando la guía tiene aportes publicados; el bloque inferior siempre.
   assert(await page.locator('.co-guide-entry a').count()<=1);
   assert.equal(await page.locator('#comunidad-guia').count(),1);
   if(await page.locator('.co-guide-entry a').count() && await page.locator('.co-guide-entry a').getAttribute('href')==='#comunidad-guia'){
    await page.locator('.co-guide-entry a').click();
    await page.waitForFunction(()=>document.getElementById('comunidad-guia').getBoundingClientRect().top>=document.querySelector('body>header').getBoundingClientRect().bottom-1);
   }
   await page.locator('#comunidad-guia').screenshot({path:'tmp/community-'+name+'-block-'+width+'.png'});
  }
 }
}
await page.goto(base+path+'#contar');await page.waitForFunction(()=>document.getElementById('contar').open);
const form=page.locator('#contar form');
assert.equal(await form.locator('[name=adult],[name=relationship]').count(),0);
await form.locator('[name=alias]').fill('Prueba visual');
await form.locator('[name=body]').fill('Probé esta herramienta en mi taller durante varios meses.');
await form.locator('[name=usage]').selectOption('profesional');await form.locator('[name=duration]').selectOption('3_12');
await form.locator('[name=frequency]').selectOption('semanal');await form.locator('[name=task]').fill('Perforar madera');
await form.locator('[name=repurchase]').selectOption('si');
await form.locator('[name=consent]').check();
await page.reload();assert.equal(await form.locator('[name=alias]').inputValue(),'Prueba visual');
await form.getByRole('button',{name:'Enviar experiencia para revisión'}).click();
await page.waitForURL('**/#participacion');assert(await page.getByText('Recibimos tu aporte.',{exact:false}).isVisible());
assert.equal(await page.evaluate(()=>sessionStorage.getItem('tl-community:bosch-gsb-18v-50:review')),null);
assert(await page.locator('#mis-aportes').getByText('Pendiente de revisión',{exact:false}).isVisible());
await page.locator('#mis-aportes').getByRole('button',{name:'Retirar mi aporte'}).click();
await page.locator('#mis-aportes').getByText('Experiencia · Retirado').waitFor({state:'visible'});
assert.deepEqual(errors,[]);console.log('OK: escritorio/celular sin desborde; borrador, envío y retiro en navegador.');
await browser.close();
bridge.stdin.end();
})().catch(e=>{console.error(e);process.exit(1)});
