const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage();const results=[];const failures=[];
 const paths=JSON.parse(fs.readFileSync(process.env.QA_PATHS_FILE||'rutas-qa-fotos.json','utf8'));
 for(const width of [320,390,1440]){
  await page.setViewportSize({width,height:900});
  for(const path of paths){
   const errors=[];const listener=e=>errors.push(e.message);page.on('pageerror',listener);
   const response=await page.goto((process.env.QA_BASE_URL||'http://127.0.0.1:5058')+path,{waitUntil:'load'});
   const result=await page.evaluate(async()=>{
    document.querySelectorAll('details').forEach(details=>details.open=true);
    const photos=[...document.querySelectorAll('img[src*="/assets/productos/"],img[src*="/assets/portadas/"]')];
    await Promise.all(photos.map(async i=>{i.loading='eager';if(!i.complete)await new Promise(resolve=>{i.addEventListener('load',resolve,{once:true});i.addEventListener('error',resolve,{once:true});});await i.decode().catch(()=>{i.dataset.decodeError='true';});}));
    const frames=[];
    const intersects=(a,b)=>a.left<b.right-.5&&a.right>b.left+.5&&a.top<b.bottom-.5&&a.bottom>b.top+.5;
    for(const i of photos){
     const style=getComputedStyle(i),r=i.getBoundingClientRect();if(!r.width||!r.height)continue;
     const problems=[];
     if(style.objectFit!=='contain')problems.push('El ajuste puede cortar o deformar la foto');
     if(style.transform!=='none')problems.push('Transformación aplicada a la foto');
     const parent=i.closest('.thumb-photo,.offer-photo')?.getBoundingClientRect();
     if(parent&&(r.left<parent.left-1||r.right>parent.right+1||r.top<parent.top-1||r.bottom>parent.bottom+1))problems.push('La imagen sale del encuadre');
     const thumb=i.closest('.card-thumb');
     if(thumb){const outer=thumb.getBoundingClientRect();if(r.left<outer.left-1||r.right>outer.right+1||r.top<outer.top-1||r.bottom>outer.bottom+1)problems.push('La foto queda cortada por la tarjeta');for(const label of thumb.querySelectorAll('.thumb-badge,.thumb-time,.editorial-label'))if(intersects(r,label.getBoundingClientRect()))problems.push('Etiqueta superpuesta a la imagen');}
     if(problems.length)frames.push({src:i.src,problems});
    }
    return {overflow:document.documentElement.scrollWidth>innerWidth+1,photos:photos.length,broken:photos.filter(i=>!i.naturalWidth||i.dataset.decodeError).map(i=>i.src),frames,fallbacks:document.querySelectorAll('.fallback-photo,.illustrative-product,.graphic-thumb,.thumb-symbol,.context-guide-thumb,.offer-no-photo,img[src*="/assets/editorial/"],img[src*="/assets/portadas/"]').length};
   });
   page.off('pageerror',listener);
   const row={width,path,status:response.status(),errors,...result};results.push(row);
   if(row.status!==200||row.overflow||row.broken.length||row.errors.length||row.frames.length||row.fallbacks)failures.push(row);
  }
  console.log(JSON.stringify({width,pages:paths.length,failures:failures.filter(r=>r.width===width).length}));
 }
 fs.writeFileSync(process.env.QA_REPORT||'qa-fotos-navegador.json',JSON.stringify({pages:paths.length,viewports:[320,390,1440],results,failures},null,2));
 await browser.close();if(failures.length){console.log(JSON.stringify(failures.slice(0,8)));process.exitCode=1;}
})().catch(e=>{console.error(e);process.exitCode=1;});
