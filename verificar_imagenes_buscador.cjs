const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});const rows=[];try{
 const page=await browser.newPage();
 const covers=JSON.parse(fs.readFileSync('portadas-guias.json','utf8'));
 for(const width of [320,390,1440]){
  await page.setViewportSize({width,height:900});await page.goto((process.env.QA_BASE_URL||'https://www.tallerlab.com.ar')+'/');
  const seen=new Set();
  for(const category of ['hidrolavadoras','compresores','taladros','amoladoras','sierras','soldadoras','soldadura-electronica','generadores']){
   await page.locator('#home-query').fill(category);
   await page.waitForFunction(c=>{const grid=document.querySelector('#home-search-grid');return !document.querySelector('#home-search-results').hidden&&!document.querySelector('#home-search-results').hasAttribute('aria-busy')&&grid.children.length&&[...grid.children].every(i=>i.dataset.sec===c);},category);
   const more=page.locator('#home-search-more');while(await more.isVisible())await more.click();
   const result=await page.locator('#home-search-grid .card-media').evaluateAll(async cards=>{
    const result=[];
    for(const card of cards){const i=card.querySelector('img');i.loading='eager';await i.decode();const r=i.getBoundingClientRect(),frame=i.closest('.thumb-photo').getBoundingClientRect();
     const overlaps=[...card.querySelectorAll('.thumb-badge,.thumb-time,.editorial-label')].some(label=>{const b=label.getBoundingClientRect();return r.left<b.right-.5&&r.right>b.left+.5&&r.top<b.bottom-.5&&r.bottom>b.top+.5;});
     result.push({path:new URL(card.href).pathname,image:new URL(i.src).pathname,fit:getComputedStyle(i).objectFit,broken:!i.naturalWidth,overlaps,outside:r.left<frame.left-1||r.right>frame.right+1||r.top<frame.top-1||r.bottom>frame.bottom+1});
    }return result;
   });
   for(const row of result){assert.equal(row.image,covers[row.path].image);assert.equal(row.fit,'contain');assert.ok(!row.broken&&!row.overlaps&&!row.outside);seen.add(row.path);rows.push({width,...row});}
  }
  assert.equal(seen.size,Object.keys(covers).length);console.log(JSON.stringify({width,portadas:seen.size,fallas:0}));
 }
 fs.writeFileSync('qa-imagenes-buscador.json',JSON.stringify({base:process.env.QA_BASE_URL||'https://www.tallerlab.com.ar',rows,failures:[]},null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
