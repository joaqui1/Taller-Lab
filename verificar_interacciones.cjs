const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
const assert=require('node:assert/strict');
const base=process.env.QA_BASE_URL||'http://127.0.0.1:5058';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const rows=[];
 try {
  const page=await browser.newPage({viewport:{width:390,height:900}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const path of JSON.parse(fs.readFileSync('rutas-qa-fotos.json','utf8'))){
   await page.goto(base+path,{waitUntil:'load'});
   const result=await page.evaluate(()=>{
    const failures=[];let sources=0,resources=0,filters=0,comparisons=0;
    const check=(condition,message)=>{if(!condition)failures.push(message);};
    for(const a of document.querySelectorAll('.buying-sources a,.offer-source')){
     sources++;const style=getComputedStyle(a);
     check(!style.backgroundImage.includes('gradient'),'Fuente presentada como botón: '+a.href);
    }
    for(const section of document.querySelectorAll('.editorial-resource')){
     resources++;const config=JSON.parse(section.querySelector('.resource-config').textContent);
     const title=section.querySelector('[data-result-title]');
     if(config.kind==='table')continue;
     check(!!title.textContent.trim(),'Resultado vacío');
     if(config.kind==='selector'){
      const select=section.querySelector('select');
      config.options.forEach((option,i)=>{select.value=String(i);select.dispatchEvent(new Event('change',{bubbles:true}));check(title.textContent===option[1],'Selector sin actualizar');});
     }else if(config.kind==='checklist'){
      const checks=[...section.querySelectorAll('[data-resource-check]')];
      checks.forEach(input=>{input.checked=true;input.dispatchEvent(new Event('change',{bubbles:true}));});
      check(title.textContent==='Todas las comprobaciones registradas','Checklist completo sin actualizar');
     }else if(config.kind==='house'){
      const row=section.querySelector('fieldset');
      for(const [key,value] of [['name','Carga de prueba'],['run','200'],['start','600']]){const input=row.querySelector('[data-load="'+key+'"]');input.value=value;input.dispatchEvent(new Event('input',{bubbles:true}));}
      check(title.textContent.includes('200 W')&&title.textContent.includes('600 W'),'Inventario de cargas no calcula');
      const input=row.querySelector('[data-load="run"]');input.value='-1';input.dispatchEvent(new Event('input',{bubbles:true}));
      check(title.textContent.includes('Faltan'),'Carga inválida no rechazada');
     }else{
      const input=section.querySelector('input[type=number]');
      if(input){input.value='-1';input.dispatchEvent(new Event('input',{bubbles:true}));check(title.textContent.includes('Revisá'),'Número fuera del rango no rechazado');}
     }
    }
    for(const shelf of document.querySelectorAll('.affiliate-shelf')){
     const cards=[...shelf.querySelectorAll('.offer-card')];
     if(cards.length===1){
      check(!shelf.querySelector('.offer-filters,.compare-checkbox,.compare-panel,.offer-empty'),'Una sola publicación muestra filtros o comparador');
      const heading=shelf.querySelector('.affiliate-heading h2,.affiliate-heading h3')?.textContent||'';
      check(!/compar|opciones|Publicaciones/i.test(heading),'Una sola publicación promete comparación o plural');
     }
     const fields=[['brand','.filter-brand'],['use','.filter-use'],['power','.filter-power']];
     for(const [key,selector] of fields){
      const select=shelf.querySelector(selector);if(!select)continue;filters++;
      for(const value of [...new Set(cards.map(c=>c.dataset[key]))]){
       select.value=value;select.dispatchEvent(new Event('change',{bubbles:true}));
       check(cards.filter(c=>!c.hidden).length===cards.filter(c=>c.dataset[key]===value).length,'Filtro incorrecto: '+key);
       if(cards.filter(c=>!c.hidden).length===1){
        check(shelf.querySelector('.affiliate-heading h2,.affiliate-heading h3').textContent==='Publicación que coincide con los filtros','Filtro con una opción mantiene promesa plural');
        check(![...shelf.querySelectorAll('.compare-checkbox')].some(c=>!c.disabled),'Filtro con una opción permite comparar');
        check(![...shelf.querySelectorAll('.compare-select')].some(label=>getComputedStyle(label).display!=='none'),'Filtro con una opción muestra casilla de comparación');
       }
      }
      select.value='';select.dispatchEvent(new Event('change',{bubbles:true}));
     }
     const checks=[...shelf.querySelectorAll('.compare-checkbox')];
     if(!checks.length)continue;comparisons++;
     const panel=shelf.querySelector('.compare-panel');
     checks[0].checked=true;checks[0].dispatchEvent(new Event('change',{bubbles:true}));
     check(!panel.hidden&&!panel.querySelector('table')&&panel.textContent.includes('Elegí otro producto'),'Una selección presenta comparación incompleta');
     const firstType=checks[0].closest('.offer-card').dataset.compareType;
     const same=checks.filter(c=>c.closest('.offer-card').dataset.compareType===firstType);
     check(same.length>=2,'Comparador sin segunda opción del mismo tipo');
     same[1].checked=true;same[1].dispatchEvent(new Event('change',{bubbles:true}));
     check(!panel.hidden&&panel.querySelector('table')?.textContent.includes(checks[0].closest('.offer-card').querySelector('h3').textContent),'Comparación de dos no muestra modelo');
     for(const c of same.slice(1,4)){c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}));}
     check(checks.filter(c=>c.checked).length<=3,'Comparación acepta más de tres');
     const other=checks.find(c=>c.closest('.offer-card').dataset.compareType!==firstType);
     if(other){other.checked=true;other.dispatchEvent(new Event('change',{bubbles:true}));check(!other.checked,'Comparación mezcla tipos');}
     checks.forEach(c=>{c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}));});
     check(panel.hidden,'Comparador vacío visible');
    }
    return {failures,sources,resources,filters,comparisons};
   });
   rows.push({path,...result});
  }
  await page.goto(base+'/');
  let requests=0;await page.route('**/search-cards.html',route=>{requests++;return requests===1?route.fulfill({status:503,body:'Temporal'}):route.continue();});
  await page.locator('#home-query').fill('taladros');
  await page.waitForFunction(()=>document.querySelector('#home-search-status').textContent.includes('No pudimos'));
  await page.locator('#home-search-form').evaluate(form=>form.requestSubmit());
  await page.waitForFunction(()=>document.querySelector('#home-search-grid').children.length>0);
  assert.ok(requests>=2,'El buscador no reintenta');
  await page.locator('#home-query').fill('sierras');
  await page.waitForFunction(()=>document.querySelector('#home-search-status').textContent.includes('guías encontradas'));
  await page.waitForFunction(()=>document.querySelector('#home-search-grid a')?.getAttribute('href').startsWith('/sierras/'));
  const before=await page.locator('#home-search-grid > *').count();
  await page.locator('#home-search-more').click();
  assert.ok(await page.locator('#home-search-grid > *').count()>before,'Ver más no agrega resultados');
  await page.locator('#home-query').fill('zzzzsinresultado');
  await page.waitForFunction(()=>document.querySelector('#home-search-status').textContent.includes('No encontramos'));
  await page.locator('#home-search-clear').click();
  assert.equal(await page.locator('#home-query').inputValue(),'');
  assert.ok(await page.locator('#home-search-results').isHidden());
  const failures=rows.filter(r=>r.failures.length);
  const report={base,pages:rows.length,errors,failures,search:{retry:true,more:true,empty:true,clear:true},rows};
  fs.writeFileSync(process.env.QA_REPORT||'qa-interacciones-local.json',JSON.stringify(report,null,2));
  console.log(JSON.stringify({pages:rows.length,failures,errors,totals:rows.reduce((a,r)=>{for(const k of ['sources','resources','filters','comparisons'])a[k]=(a[k]||0)+r[k];return a;},{})}));
  assert.equal(failures.length,0);assert.equal(errors.length,0);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
