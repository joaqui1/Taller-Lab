"""Fotos oficiales de los dos códigos Gamma cuyos afiliados recibió TallerLab."""
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from PIL import Image

root = Path(__file__).parent
manifest_path = root/'fotos-modelos.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
evidence = []
for model, link, slug, photo in [
    ('G2801AR','https://meli.la/1vR4xKe','compresor-de-25-litros','compresores_compresor-de-25-litros_G2801AR-00.jpg'),
    ('G2803AR','https://meli.la/1jaQvxd','compresor-bicilindrico-de-100-litros','compresores_compresor-bicilindrico-de-100-litros_G2803AR-00.jpg'),
]:
    source = 'https://www.gammaherramientas.com.ar/producto/'+slug+'/'
    original = 'https://www.gammaherramientas.com.ar/web/wp-content/uploads/2024/09/'+photo
    with urlopen(original, timeout=45) as response:
        raw = response.read()
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    im.thumbnail((640,640), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    im.save(buffer,format='WEBP',quality=80,method=6)
    data = buffer.getvalue()
    assert len(data)<=60000
    name = 'gamma'+model.lower()+'-'+hashlib.sha256(data).hexdigest()[:10]+'.webp'
    target = root/'assets/productos'/name
    target.write_bytes(data)
    record = dict(status='verified',brand='Gamma',model=model,source=source,checked='2026-10-02',image='/assets/productos/'+name,width=im.width,height=im.height,bytes=len(data),original_image=original)
    manifest['products'][link] = record
    manifest['products'][source] = record
    evidence.append(dict(affiliate=link,**record))
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'evidencia-fotos-gamma-recibidos-2026-10-02.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print([(r['model'],r['image'],r['bytes']) for r in evidence])
