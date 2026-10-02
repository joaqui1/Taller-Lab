"""Presentaciones recibidas: macizo 0,8 mm / 5 kg y tubular 1,0 mm / 1 kg."""
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image

root=Path(__file__).parent
manifest=json.loads((root/'fotos-modelos.json').read_text(encoding='utf-8'))
records=[
 ('https://meli.la/22SmE5r','WELD 70S-6 · 0,8 mm × 5 kg','esab-weld5kg.jpg','https://www.lfmaquinaseferramentas.com.br/arame-mig-080mm-esab-weld-70s6-5kg/p','https://lfmaquinaseferramentas.vtexassets.com/arquivos/ids/200592-800-800?aspect=true&height=800&v=637916963799930000&width=800','https://esab.com/cl/sam_es/products-solutions/product/filler-metals/mild-steel/mig-wires-tig-rods-gmaw-gtaw/weld-70s-6/'),
 ('https://www.mercadolibre.com.ar/p/MLA44478426?pdp_filters=item_id:MLA3903819884','Gas Free E71T-GS · 1,0 mm × 1 kg','esab-gasfree-142642.jpg','https://esab.com/ar/sam_es/products-solutions/product/filler-metals/mild-steel/self-shielded-flux-cored-wires-fcaw/esab-gas-free/','https://d363suj4pdptk4.cloudfront.net/externalApps/c7efbbab-3f6a-497d-9dae-cbb24f5f4774/conversion/PIM/assets/142642','https://esab.com/ar/sam_es/products-solutions/product/filler-metals/mild-steel/self-shielded-flux-cored-wires-fcaw/esab-gas-free/'),
]
for url,model,file,source,original,facts_source in records:
 with urlopen(original,timeout=45) as response:
  im=Image.open(io.BytesIO(response.read())).convert('RGB')
 im.thumbnail((640,640),Image.Resampling.LANCZOS)
 b=io.BytesIO(); im.save(b,format='WEBP',quality=80,method=6); data=b.getvalue()
 assert len(data)<=60000
 name=file.removesuffix('.jpg')+'-'+hashlib.sha256(data).hexdigest()[:10]+'.webp'
 (root/'assets/productos'/name).write_bytes(data)
 manifest['products'][url]=dict(status='verified',brand='ESAB',model=model,source=source,checked='2026-10-02',image='/assets/productos/'+name,width=im.width,height=im.height,bytes=len(data),original_image=original,technical_source=facts_source)
 print(name,len(data))
(root/'fotos-modelos.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'afiliados-por-completar.json'; slots=json.loads(p.read_text(encoding='utf-8'))
slots['ESAB/Conarco WELD ER70S-6 · 0,8 mm × 5 kg']['affiliate_url']=records[0][0]
slots['ESAB Gas Free E71T-GS · 1,0 mm × 1 kg'].update(publication_url=records[1][0],configuration='Publicación común recibida e incorporada. Falta referido para esta misma presentación de 1,0 mm × 1 kg; ESAB código 0750333.')
for model in ['ESAB OK NiFe-CI 3,2 mm','Bosch PRO Multi Material · 190 mm · 54 dientes · eje 30 mm']:
 slots[model]['availability_review']='2026-10-02: el usuario no encuentra el modelo exacto; conserva ficha documental y espacio de referido.'
for model,url,decision in [
 ('STIHL RE 90 · RE020114544 · 50 Hz','https://meli.la/1fBYuUY','La oferta sigue identificada como 60 Hz, no corresponde a la variante local de 50 Hz.'),
 ('Kärcher K5 · 9.398-295.0','https://meli.la/13vEAhr','Recibido como K5 Power Control: 1,9 kW y 380 L/h difieren de Power Control AR 1.603-501.0; falta código/frecuencia. No asociar a K5 básica.'),
 ('Bosch GSA 1100 E','https://meli.la/2cEAQKh','Es el mismo enlace con título 110 W ya retirado. Modelo oficial 1100 W; pendiente código, voltaje y potencia de la publicación.'),
 ('Hyundai HHY2200F','https://meli.la/11Ddx34','Título HY2200F; verificar modelo de características antes de aplicar datos HHY2200F de catálogo argentino.')]:
 slots[model]['candidate_review']=dict(url=url,decision=decision)
p.write_text(json.dumps(slots,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
 import servidor_local as site
 p=root/'revision-editorial-por-tandas.json'; ledger=json.loads(p.read_text(encoding='utf-8'))
 for article in site.ALL_ARTICLES:
  if article['url'] in ['/soldadoras/alambre-para-soldadura-mig/','/soldadoras/alambre-flux/','/soldadoras/soldadora-mig-con-gas/']:
   ledger[article['url']].update(body_sha256=hashlib.sha256(article['body'].encode()).hexdigest(),commercial_followup='2026-10-02: revisión de los consumibles recibidos por clasificación, diámetro y bobina. WELD 0,8 mm × 5 kg con referido; Gas Free 1,0 mm × 1 kg con publicación común. Fotos y fichas específicas; sin nueva lectura integral.')
 p.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
