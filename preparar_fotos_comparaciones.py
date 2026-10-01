"""Descarga fotografías reales de las nuevas referencias, con el presupuesto habitual."""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from comparaciones_por_guia import MODELS
from preparar_fotos_modelos import page, candidates, optimize, norm, get

ROOT=Path(__file__).parent
manifest=ROOT/'fotos-modelos.json'
PHOTO_OVERRIDES={
 'einhell90':'https://d2c5rvsfjg2eub.cloudfront.net/image/208244749100/image_7g8k0b3oq16dh4llap9d87as56/-FJPG-FWEBP-B800',
}

def resolve(key, model, existing, covers):
    source=model['source']
    if key in PHOTO_OVERRIDES:
        return source,dict(optimize(PHOTO_OVERRIDES[key],norm(model['brand']+model['model'])),brand=model['brand'],model=model['model'],source=source,status='verified',checked='2026-10-01')
    known=existing.get(source) or next((p for p in list(existing.values())+list(covers.values()) if p.get('source')==source and p.get('image')),None)
    if not known:
        known=next((p for p in existing.values() if norm(p.get('brand','')+p.get('model',''))==norm(model['brand']+model['model'])),None)
    if known:
        return source,dict(known,brand=model['brand'],model=model['model'],status='verified')
    html=page(source)
    soup=BeautifulSoup(html,'html.parser')
    urls=candidates(model['model'].split(' · ')[0],source)
    if 'dewalt.' in source:
        fresh=BeautifulSoup(get(source).text,'html.parser')
        stem=model['model'].split('-')[0]
        urls=[urljoin(source,img.get('src','')) for img in fresh.select('img') if stem in img.get('src','') and 'WHITEBG' in img.get('src','') and '_A' not in img.get('src','')] + urls
    if 'stihl.com' in source:
        urls=[urljoin(source,img.get('src','')) for img in soup.select('img') if norm(model['model']) in norm(img.get('alt',''))] + urls
    if 'mecafer.com' in source:
        # La galería del producto lleva el código exacto; excluir iconos y sugerencias.
        code=norm(model['model'])
        urls=[urljoin(source,img.get('src','')) for img in soup.select('img') if code in norm(img.get('src','')+img.get('alt',''))] + urls
    errors=[]
    for url in dict.fromkeys(urls):
        try:
            result=optimize(url,norm(model['brand']+model['model']))
            return source,dict(result,brand=model['brand'],model=model['model'],source=source,status='verified',checked='2026-10-01')
        except Exception as exc: errors.append(str(exc)[:120])
    raise ValueError(key+': sin foto verificable; candidates='+str(urls[:3])+' errors='+str(errors[:2]))

def main():
    data=json.loads(manifest.read_text(encoding='utf-8'))
    covers=json.loads((ROOT/'fotos-portadas-reales.json').read_text(encoding='utf-8'))
    pending=[]
    with ThreadPoolExecutor(max_workers=5) as pool:
        jobs={pool.submit(resolve,key,model,data['products'],covers):key for key,model in MODELS.items()}
        for job in as_completed(jobs):
            try:
                source,result=job.result();data['products'][source]=result
                print(jobs[job],result['image'],result['bytes'],flush=True)
            except Exception as exc: pending.append(str(exc));print('PENDIENTE',str(exc),flush=True)
    for url,source,code in [
        ('https://meli.la/2Qpd7no','https://www.einhell.de/en/p/4140750-tc-hp-130/','4140750'),
        ('https://meli.la/26hgiky','https://www.einhell.de/en/p/4140760-te-hp-140/','4140760')]:
        soup=BeautifulSoup(get(source).text,'html.parser')
        image=next(img['src'] for img in soup.select('img') if code+'-productimage-001' in img.get('alt',''))
        old=data['products'][url]
        old.update(optimize(image,norm(old['brand']+old['model'])),source=source,checked='2026-10-01',status='verified')
        print('Foto corregida',old['model'],old['image'],flush=True)
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'qa-fotos-comparaciones-pendientes.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not pending,pending

if __name__=='__main__':main()
