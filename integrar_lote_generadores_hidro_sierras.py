"""Fotos y registro del lote recibido: equipos, variantes y repuestos separados."""
import hashlib, io, json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image

root=Path(__file__).parent
p=root/'fotos-modelos.json'; manifest=json.loads(p.read_text(encoding='utf-8'))
for new,old in [('https://meli.la/25pcKkk','https://www.lusqtoff.com.ar/ver-producto/LGI11.0-9'),('https://meli.la/1FVSrCT','https://meli.la/2oUJyrQ')]:
    manifest['products'][new]=dict(manifest['products'][old],checked='2026-10-02')
source='https://ar.blackanddecker.global/producto/bepw1800t-ar/hidrolavadora-1810-psi-125-bar'
original='https://ar.blackanddecker.global/LAG/PRODUCT/IMAGES/HIRES/BEPW1800T_1.jpg?resize=530x530'
with urlopen(original,timeout=45) as r:
    im=Image.open(io.BytesIO(r.read())).convert('RGB')
im.thumbnail((640,640),Image.Resampling.LANCZOS)
b=io.BytesIO(); im.save(b,format='WEBP',quality=80,method=6); data=b.getvalue()
assert len(data)<=60000
name='blackdeckerbepw1800tar-'+hashlib.sha256(data).hexdigest()[:10]+'.webp'
(root/'assets/productos'/name).write_bytes(data)
record=dict(status='verified',brand='BLACK+DECKER',model='BEPW1800T-AR',source=source,checked='2026-10-02',image='/assets/productos/'+name,width=im.width,height=im.height,bytes=len(data),original_image=original)
manifest['products']['https://meli.la/1D4gf5k']=record
manifest['products'][source]=record
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'afiliados-por-completar.json'; slots=json.loads(p.read_text(encoding='utf-8'))
for model,url in [('Lüsqtoff LGI11.0-9','https://meli.la/25pcKkk'),('BLACK+DECKER BEPW1800T-AR','https://meli.la/1D4gf5k')]:
    slots[model]['affiliate_url']=url
slots['BLACK+DECKER CS1004-AR']=dict(affiliate_url='https://meli.la/1FVSrCT',guides=['/sierras/circulares-black-decker/'],configuration='CS1004; no sustituye a CS1350P. Confirmar sufijo AR y disco incluido.')
for model in ['Fengda AS-186','Lüsqtoff HL100-8','Bosch UniversalAquatak 36V-100 06008C7002','Einhell TC-SM 2131/2 Dual 4300390','TOTAL TS42182553','BLACK+DECKER CS1350P-AR']:
    slots[model]['availability_review']='2026-10-02: el usuario no encuentra la publicación exacta; conservar referencia documental sin atribuirle otra oferta.'
slots['Lüsqtoff LGI3.8-8']['candidate_review']=dict(affiliate_url='https://meli.la/2TcYRTK',model='LGIS3.8-8',decision='Motosoldadora distinta del LGI3.8-8; enlace ya integrado en la guía de gama Lüsqtoff, no sustituye al generador inverter solo.')
slots['Gamma 150 Elite G2514AR']['candidate_review']=dict(url='https://www.mercadolibre.com.ar/up/MLAU3371988530?pdp_filters=item_id:MLA1515656193',decision='Bomba de repuesto, no hidrolavadora completa. No usar como oferta del equipo.')
slots['Bosch GHP 220 0600910EH0']['candidate_review']=dict(affiliate_url='https://meli.la/2BRPsKf',offered_code='0600910EG0',listing_frequency='50 Hz / 60 Hz',manufacturer_frequency='60 Hz',source='https://www.bosch-professional.com/binary/manualsmedia/o485788v21_F016L94691_202408.pdf',source_page=12,decision='No asociar a EH0 de 50 Hz: Bosch identifica EG0 como 60 Hz. Los datos de frecuencia del catálogo contradicen el manual.')
slots['Bosch GHP 4-50 0600910FH0']['candidate_review']=dict(affiliate_url='https://meli.la/1gVPfjo',listing_frequency='60 Hz',listing_voltage='220 V',offered_code=None,decision='No asociar a FH0 de 50 Hz: la publicación declara 60 Hz y no aporta código de producto.')
slots['Bosch GHP 220 0600910EH0']['configuration']='Buscar código EH0 de 50 Hz; el referido 2BRPsKf identifica EG0, de 60 Hz según manual Bosch página 12.'
slots['Bosch GHP 4-50 0600910FH0']['configuration']='Buscar código FH0 de 50 Hz; el referido 1gVPfjo declara 60 Hz y no acredita el código argentino.'
p.write_text(json.dumps(slots,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'lote-afiliados-generadores-hidro-sierras-2026-10-02.json').write_text(json.dumps(dict(integrated=['https://meli.la/25pcKkk','https://meli.la/1D4gf5k','https://meli.la/1FVSrCT'],pending_bosch=['https://meli.la/2BRPsKf','https://meli.la/1gVPfjo'],photo=record),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(name,len(data),'bytes; tres afiliados integrados; Bosch pendientes de identidad regional')
