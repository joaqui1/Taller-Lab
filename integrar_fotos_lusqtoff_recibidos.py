"""Relaciona afiliados recibidos con fotos oficiales del código exacto."""
import hashlib, io, json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image

root=Path(__file__).parent
p=root/'fotos-modelos.json'
manifest=json.loads(p.read_text(encoding='utf-8'))
evidence=[]
for link, source in [
 ('https://meli.la/1Rjz39S','https://lusqtoff.com.ar/ver-producto/LC-2550VS'),
 ('https://meli.la/27nVFRy','https://lusqtoff.com.ar/productos/compresor-de-aire-sin-aceite-50l'),
 ('https://meli.la/21fBeVj','https://lusqtoff.com.ar/productos/LCS100-8'),
]:
 record=dict(manifest['products'][source],checked='2026-10-02')
 manifest['products'][link]=record
 evidence.append(dict(affiliate=link,**record))
source='https://lusqtoff.com.ar/productos/LC40100-8'
original='https://lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/COMPRESORES_DE_AIRE/LC40100-8/LC40100-8_web.jpg'
with urlopen(original,timeout=45) as r:
 im=Image.open(io.BytesIO(r.read())).convert('RGB')
im.thumbnail((640,640),Image.Resampling.LANCZOS)
b=io.BytesIO(); im.save(b,format='WEBP',quality=80,method=6); data=b.getvalue()
assert len(data)<=60000
name='lusqtofflc401008-'+hashlib.sha256(data).hexdigest()[:10]+'.webp'
(root/'assets/productos'/name).write_bytes(data)
record=dict(status='verified',brand='Lüsqtoff',model='LC40100-8',source=source,checked='2026-10-02',image='/assets/productos/'+name,width=im.width,height=im.height,bytes=len(data),original_image=original)
for key in [source,'https://meli.la/1GRiWbV']:
 manifest['products'][key]=record
evidence.append(dict(affiliate='https://meli.la/1GRiWbV',**record))
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'evidencia-lusqtoff-afiliados-2026-10-02.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print([(r['model'],r['bytes']) for r in evidence])
