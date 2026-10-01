"""Asigna exclusivamente fotos reales verificadas a todas las guías."""
from pathlib import Path
import json
import servidor_local as site
from fotos_productos import PHOTOS, model_key

ROOT=Path(__file__).resolve().parent
REUSED={
 '/compresores/aceite/':'model:gammag2802ar',
 '/compresores/filtros/':'model:gammag2802ar',
 '/compresores/gamma-50-litros/':'model:gammag2802ar',
 '/generadores/comparativa-general/':'https://meli.la/2AwxqaH',
 '/hidrolavadoras/comparativa-general/':'https://meli.la/1cZXqxL',
 '/sierras/sable/':'https://meli.la/2mTTC3F',
 '/taladros/rotomartillos/':'https://meli.la/2cRLSJx',
 '/taladros/atornilladores-de-impacto/':'https://meli.la/1hh4SkK',
 '/taladros/taladro-percutor-inalambrico/':'https://meli.la/2xvJRJp',
 '/taladros/combo-taladro-amoladora/':'https://meli.la/2z7Capd',
}

def cover_for(photo):
 cover={k:photo[k] for k in ('image','width','height','bytes','source')}
 cover.update(kind='product',label='Foto del producto',alt=photo.get('photo_subject') or (photo['brand']+' '+photo['model']))
 return cover

def main():
 extra=json.loads((ROOT/'fotos-portadas-reales.json').read_text(encoding='utf-8'))
 covers={}
 for article in site.ALL_ARTICLES:
  path=article['url']
  if path in extra:
   covers[path]=extra[path];continue
  if path in REUSED:
   covers[path]=cover_for(PHOTOS[REUSED[path]]);continue
  assigned=[]
  for name in ('HIDROLAVADORAS_OFFERS','COMPRESORES_OFFERS','GENERADORES_OFFERS','SIERRAS_OFFERS','TALADROS_OFFERS','SOLDADORAS_OFFERS'):
   assigned.extend(offer['url'] for offer in getattr(site,name).get(path,{}).get('offers',[]))
  assigned.extend(item['url'] for item in site.AMOLADORA_CHOICES.get(path,{}).get('items',[]))
  title_key=model_key('',article['title']);candidates=[]
  for url,photo in PHOTOS.items():
   if (url not in article['body'] and url not in assigned) or not photo.get('image'):continue
   brand=model_key('',photo.get('brand',''));model=model_key('',photo.get('model',''))
   priority=100 if len(model)>=4 and model in title_key else 20 if len(brand)>=3 and brand in title_key else 5 if url in assigned else 1
   order=assigned.index(url) if url in assigned else article['body'].find(url)
   candidates.append((priority,-order,photo))
  if not candidates:raise ValueError('Guía sin foto real verificada: '+path)
  covers[path]=cover_for(max(candidates,key=lambda p:p[:2])[2])
 assert len(covers)==len(site.ALL_ARTICLES) and all(c['kind']=='product' and c['image'].startswith('/assets/productos/') for c in covers.values())
 (ROOT/'portadas-guias.json').write_text(json.dumps(covers,ensure_ascii=False,indent=2),encoding='utf-8')
 print('OK:',len(covers),'portadas con fotos reales; cero ilustraciones.')

if __name__=='__main__':main()
