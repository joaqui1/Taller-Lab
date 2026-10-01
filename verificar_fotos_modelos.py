"""Verifica correspondencia del manifiesto, peso y entrega de los assets locales."""
from pathlib import Path
from html.parser import HTMLParser
import io
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / '.publication-qa-deps'))
from PIL import Image
from app import app
import servidor_local as s
from fotos_productos import PHOTOS
from portadas_guias import COVERS

class Photos(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.images=[]
        self.feed(text)
    def handle_starttag(self, tag, attributes):
        if tag=='img':
            self.images.append(dict(attributes))

def main():
    client=app.test_client()
    assets={p['image']:p for p in PHOTOS.values() if p.get('image')}
    model_assets=len(assets)
    assert len(COVERS)==len(s.ALL_ARTICLES) and all(p['kind']=='product' and p['image'].startswith('/assets/productos/') for p in COVERS.values()), 'Quedan portadas ilustrativas'
    assets.update({p['image']:p for p in COVERS.values()})
    assert PHOTOS and all(p.get('image') for p in PHOTOS.values()), 'Quedan referencias sin foto'
    for url,photo in assets.items():
        response=client.get(url)
        assert response.status_code==200, url
        assert len(response.data)==photo['bytes']<=60_000, url
        assert response.headers.get('Cache-Control') == 'public, max-age=31536000, immutable', url
        im=Image.open(io.BytesIO(response.data))
        assert im.format=='WEBP' and im.size==(photo['width'],photo['height']),url
        assert max(im.size)<=640 and min(im.size)>=120,url
    shown=set()
    pages=[s.render_category_page(cat) for cat in s.CATEGORY_META]
    pages += [s.render_article_page(a) for a in s.ALL_ARTICLES]
    for document in pages:
        assert 'Imagen ilustrativa · sin foto' not in document, 'Un modelo sigue mostrando una foto ilustrativa'
        assert '/assets/editorial/' not in document and 'Ilustración editorial' not in document, 'Queda una imagen editorial en el HTML o sus metadatos'
        for image in Photos(document).images:
            src=image.get('src','')
            if src.startswith('/assets/productos/'):
                assert src in assets,src
                assert image.get('loading')=='lazy' and image.get('decoding')=='async',src
                shown.add(src)
    assert len(shown)>150, len(shown)
    report=dict(destinos_con_foto=sum(bool(p.get('image')) for p in PHOTOS.values()),
                destinos_pendientes=sum(not p.get('image') for p in PHOTOS.values()),
                fotos_unicas=len(assets), fotos_mostradas=len(shown),
                fotos_catalogo=model_assets, portadas_reales=len(COVERS), portadas_ilustrativas=0,
                peso_total_bytes=sum(p['bytes'] for p in assets.values()),
                peso_medio_bytes=round(sum(p['bytes'] for p in assets.values())/len(assets)),
                peso_maximo_bytes=max(p['bytes'] for p in assets.values()),
                paginas_verificadas=len(pages))
    Path('verificacion-fotos-modelos.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
