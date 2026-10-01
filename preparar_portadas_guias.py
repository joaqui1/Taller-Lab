"""Prepara miniaturas livianas y asignaciones revisables para todas las guías."""
from pathlib import Path
import hashlib
import io
import json
import re
from PIL import Image
import servidor_local as site
from fotos_productos import PHOTOS, model_key

ROOT = Path(__file__).resolve().parent

def main():
    folder = ROOT / 'assets' / 'portadas'
    folder.mkdir(parents=True, exist_ok=True)
    contextual = {}
    for file in sorted((ROOT / 'assets' / 'editorial').glob('*.webp')):
        image = Image.open(file).convert('RGB')
        image.thumbnail((640, 480), Image.Resampling.LANCZOS)
        for quality in (76, 68, 60):
            output = io.BytesIO()
            image.save(output, 'WEBP', quality=quality, method=6)
            if output.tell() <= 40_000:
                break
        assert output.tell() <= 40_000, file
        name = file.stem + '-' + hashlib.sha256(output.getvalue()).hexdigest()[:10] + '.webp'
        (folder / name).write_bytes(output.getvalue())
        contextual[file.stem] = dict(image='/assets/portadas/' + name,
            width=image.width, height=image.height, bytes=output.tell(), kind='context',
            label='Ilustración editorial', source='/assets/editorial/' + file.name)
    covers = {}
    for article in site.ALL_ARTICLES:
        topic = article['section']
        title = article['title'].lower()
        if topic == 'amoladoras' and any(t in title for t in ('disco', 'flap')):
            topic = 'discos'
        elif topic == 'taladros' and any(t in title for t in ('mecha', 'broca', 'mandril')):
            topic = 'mechas'
        elif topic == 'sierras' and any(t in title for t in ('hoja', 'disco')):
            topic = 'hojas-sierra'
        elif topic == 'compresores' and any(t in title for t in ('manguera', 'acople', 'pistola', 'herramientas neumáticas', 'kit')):
            topic = 'neumaticos'
        elif topic == 'soldadoras' and any(t in title for t in ('electrodo', 'alambre', 'flux', 'consumible')):
            topic = 'soldadura-consumibles'
        cover = dict(contextual[topic], alt='Ilustración contextual de ' + article['title'])
        # Una portada de marca/modelo sólo toma fotos de productos citados
        # en la propia guía; las demás portadas mantienen carácter editorial.
        title_key = model_key('', article['title'])
        candidates = []
        assigned = []
        for name in ('HIDROLAVADORAS_OFFERS', 'COMPRESORES_OFFERS', 'GENERADORES_OFFERS',
                     'SIERRAS_OFFERS', 'TALADROS_OFFERS', 'SOLDADORAS_OFFERS'):
            config = getattr(site, name).get(article['url'], {})
            assigned += [offer['url'] for offer in config.get('offers', [])]
        assigned += [item['url'] for item in site.AMOLADORA_CHOICES.get(article['url'], {}).get('items', [])]
        for url, photo in PHOTOS.items():
            if (url not in article['body'] and url not in assigned) or not photo.get('image'):
                continue
            brand = model_key('', photo.get('brand', ''))
            model = model_key('', photo.get('model', ''))
            exact = len(model) >= 4 and model in title_key
            branded = len(brand) >= 3 and brand in title_key
            priority = 100 if exact else 20 if branded else 5 if url in assigned else 1
            order = assigned.index(url) if url in assigned else article['body'].find(url)
            candidates.append((priority, -order, photo))
        if candidates and '/comparativa-general/' not in article['url']:
            photo = max(candidates, key=lambda p: p[:2])[2]
            subject = photo.get('photo_subject') or (photo['brand'] + ' ' + photo['model'])
            cover = {k: photo[k] for k in ('image', 'width', 'height', 'bytes', 'source')}
            cover.update(kind='product', label='Modelo citado', alt=subject)
        covers[article['url']] = cover
    (ROOT / 'portadas-guias.json').write_text(json.dumps(covers, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(guias=len(covers), modelos=sum(c['kind']=='product' for c in covers.values()),
        contextuales=sum(c['kind']=='context' for c in covers.values()),
        miniaturas=len(contextual), peso_medio=round(sum(c['bytes'] for c in contextual.values())/len(contextual))), ensure_ascii=False))

if __name__ == '__main__':
    main()
