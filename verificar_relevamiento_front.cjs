// Ejecuta el JavaScript generado con controles simulados: no certifica diseño visual.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const fixture=JSON.parse(fs.readFileSync('tmp/relevamiento-front-fixture.json','utf8'));
fixture.admin_scripts.forEach(script=>new vm.Script(script));
const elements=fixture.elements.map(e=>({...e,checked:false,style:{},events:{},addEventListener(type,fn){(this.events[type]??=[]).push(fn)},focus(){},scrollIntoView(){},appendChild(){}}));
const byId=id=>elements.find(e=>e.id===id);
const platforms=elements.filter(e=>e.name==='plataformas_bateria');
const sent=[];
const document={getElementById:byId,querySelectorAll(){return platforms},querySelector(selector){return platforms.find(e=>e.value===selector.match(/value="([^"]+)"/)[1])},createElement(){return {}}};
class FormData {constructor(){this.entries=elements.filter(e=>e.name&&(!['checkbox','radio'].includes(e.type)||e.checked)).map(e=>[e.name,e.value])}forEach(fn){this.entries.forEach(([k,v])=>fn(v,k))}getAll(name){return this.entries.filter(([k])=>k===name).map(([,v])=>v)}}
const context={document,FormData,crypto:{randomUUID:()=> 'test-session-123456789'},Set,Date,Math,Blob,navigator:{sendBeacon(){return true}},window:{addEventListener(){}},fetch:async(url,opts)=>{sent.push(JSON.parse(opts.body));return {status:200,json:async()=>({ok:true,guias_recomendadas:[]})}}};
vm.runInNewContext(fixture.script,context);
const fire=e=>e.events.change?.forEach(fn=>fn());
const two=platforms.filter(e=>e.value.includes('milwaukee')).slice(0,2);assert.equal(two.length,2);
two.forEach(e=>{e.checked=true;fire(e)});assert(two.every(e=>e.checked));
const none=platforms.find(e=>e.value==='no_usa');none.checked=true;fire(none);assert(two.every(e=>!e.checked));
two.forEach(e=>{e.checked=true;fire(e)});assert(!none.checked);
const form=byId('relevamiento-form');form.events.submit[0]({preventDefault(){}});
setImmediate(()=>{assert.deepEqual(sent[0].plataformas_bateria,two.map(e=>e.value));assert.equal(form.style.display,'none');assert.equal(byId('survey-success').style.display,'block');console.log('OK: selección múltiple, exclusión No uso, serialización y confirmación de envío.');});
