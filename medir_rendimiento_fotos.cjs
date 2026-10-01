const {chromium}=require('C:/Users/joaqu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge',args:['--remote-debugging-port=9228']});
 try {
  const {default:lighthouse}=await import('./.seo-tools/_npx/0f94ee7615faf582/node_modules/lighthouse/core/index.js');
  const results=[];
  for(const [name,path] of [['home','/'],['hub','/taladros/'],['guia','/taladros/inalambricos/'],['mas-fotos','/generadores/comparativa-general/']]) {
   const {lhr}=await lighthouse('http://127.0.0.1:5058'+path,{port:9228,output:'json',onlyCategories:['performance'],logLevel:'error'});
   fs.writeFileSync('lighthouse-fotos-'+name+'.json',JSON.stringify(lhr,null,2));
   const metrics={name,score:lhr.categories.performance.score,LCP:lhr.audits['largest-contentful-paint'].numericValue,CLS:lhr.audits['cumulative-layout-shift'].numericValue,TBT:lhr.audits['total-blocking-time'].numericValue,bytes:lhr.audits['total-byte-weight'].numericValue};
   results.push(metrics);console.log(JSON.stringify(metrics));
  }
  fs.writeFileSync('rendimiento-fotos-resumen.json',JSON.stringify(results,null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
