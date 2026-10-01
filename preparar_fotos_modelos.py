"""Descubre fotos en fichas específicas y genera WebP locales de hasta 60 KB.

Se ejecuta manualmente; la web y el despliegue no consultan proveedores.
Conserva procedencia, dimensiones y pendientes en fotos-modelos.json.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, unquote
import hashlib
import html
import io
import json
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import servidor_local as site

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'assets' / 'productos'
REPORT = ROOT / 'fotos-modelos.json'
CACHE = ROOT / '.fotos-cache'
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; TallerLab product image verification)'}

def norm(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', unquote(value)).encode('ascii', 'ignore').decode().lower())

def get(url):
    response = requests.get(url, headers=HEADERS, timeout=18)
    response.raise_for_status()
    if len(response.content) > 20_000_000:
        raise ValueError('Recurso demasiado grande')
    return response

def page(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.html')
    if path.exists():
        return path.read_text(encoding='utf-8')
    response = get(url)
    if 'html' not in response.headers.get('Content-Type', ''):
        raise ValueError('No es ficha HTML')
    response.encoding = 'utf-8'
    path.write_text(response.text, encoding='utf-8')
    return response.text

def candidates(model, source):
    soup = BeautifulSoup(page(source), 'html.parser')
    key = norm(model)
    # El título o el código visible de la ficha debe identificar el modelo.
    identity = ' '.join(x.get_text(' ', strip=True) for x in soup.select('h1, h2, .badge, .sku, .product_meta'))
    identity += ' ' + (soup.title.get_text() if soup.title else '')
    if 'btatools.com' in source:
        identity += ' ' + soup.get_text(' ', strip=True)
    if key not in norm(identity) and key not in norm(source):
        return []
    if key.isdigit() and not re.search(r'(?<!\d)' + re.escape(key) + r'(?!\d)', identity + ' ' + source):
        return []
    if 'lusqtoff.com' in source:
        badges = [norm(x.get_text()) for x in soup.select('.badge')]
        if key not in badges:
            return []
    result = []
    if 'pf.honda.com.ar/producto/' in source:
        for img in soup.select('.conf-resp-description-div img'):
            result.append(urljoin(source, img.get('src', '')))
    for img in soup.select('.woocommerce-product-gallery__image img'):
        value = img.get('data-large_image') or img.get('src')
        if value:
            result.append(urljoin(source, value))
    for link in soup.select('a.product-image[href], a[data-fancybox="product-photos"][href]'):
        result.append(urljoin(source, link['href']))
    # Las imágenes de otras herramientas y banners quedan fuera.
    for img in soup.find_all('img'):
        value = img.get('data-src') or img.get('src') or ''
        photo_key = norm(re.sub(r'-(AR|B2)$', '', model, flags=re.I))
        if key in norm(img.get('alt', '')) or photo_key in norm(value):
            result.append(urljoin(source, value))
    for value in re.findall(r'["\']([^"\']+\.(?:jpg|png|webp)(?:\?[^"\']*)?)["\']', str(soup)):
        if key in norm(value) and 'logo' not in value.lower():
            result.append(urljoin(source, html.unescape(value)))
    for meta in soup.select('meta[property="og:image"]'):
        value = meta.get('content', '')
        if value and not value.endswith('/') and not any(s in source for s in ('fravega.com', 'stanleytools.global', 'blackanddecker.global', 'dewalt.com')):
            result.append(urljoin(source, value))
    # Priorizar la foto de catálogo frente a escenas de uso y despieces.
    def priority(value):
        return (bool(re.search(r'icon-image|logo|banner|fallback|explod|diagram|spare|application|lifestyle|_a\d|_f\d|_act', value, re.I)),
                not bool(re.search(r'/product-image/|/mainproduct/|/' + re.escape(re.sub(r'-(AR|B2)$', '', model, flags=re.I)) + r'_1\.', value, re.I)),
                not bool(re.search(r'_1\.|ghost|hero|dynamic|dyn\.|_dyn|estatic', value, re.I)))
    result.sort(key=priority)
    return list(dict.fromkeys(result))

def optimize(url, key):
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(get(url).content)))
    if max(image.size) < 120 or min(image.size) < 24:
        raise ValueError('Miniatura demasiado pequeña')
    image.thumbnail((640, 640), Image.Resampling.LANCZOS)
    image = image.convert('RGBA') if 'A' in image.getbands() else image.convert('RGB')
    # Mechas y electrodos pueden ser muy estrechos: conservar su resolución,
    # con margen transparente en vez de descartarlos como miniaturas.
    if min(image.size) < 120:
        canvas = Image.new('RGBA', (max(120, image.width), max(120, image.height)))
        canvas.paste(image, ((canvas.width-image.width)//2, (canvas.height-image.height)//2))
        image = canvas
    for quality in (82, 75, 65, 55):
        output = io.BytesIO()
        image.save(output, 'WEBP', quality=quality, method=6)
        if output.tell() <= 60_000:
            break
    if output.tell() > 60_000:
        image.thumbnail((480, 480), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, 'WEBP', quality=60, method=6)
    if output.tell() > 60_000:
        raise ValueError('No cumple presupuesto de peso')
    filename = key + '-' + hashlib.sha256(output.getvalue()).hexdigest()[:10] + '.webp'
    (DEST / filename).write_bytes(output.getvalue())
    return dict(image='/assets/productos/' + filename, width=image.width, height=image.height,
                bytes=output.tell(), original_image=url)

def inventory():
    products = {}
    for url, facts in site.PRODUCT_FACTS.items():
        products[url] = dict(brand=facts['brand'], model=facts['model'], existing=facts.get('image'),
                             image_source=facts.get('image_source'), source=facts.get('source'))
    for choice in site.AMOLADORA_CHOICES.values():
        for item in choice['items']:
            if item['url'] not in products:
                brand, _, model = item['name'].partition(' ')
                products[item['url']] = dict(brand=brand, model=model.split(' · ')[0])
    for item in site.CONTEXTUAL_CHOICES.values():
        if item['url'] not in products:
            brand, _, model = item['name'].partition(' ')
            products[item['url']] = dict(brand=brand, model=model.split(' · ')[0])
    for brand, model, source in [
        ('Gamma', 'G2802AR', 'https://www.gammaherramientas.com.ar/producto/compresor-de-50-litros/'),
        ('Einhell', 'TE-AC 270/50 Silent', 'https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/')]:
        products['model:' + norm(brand + model)] = dict(brand=brand, model=model, source=source)
    return products

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    old = json.loads(REPORT.read_text(encoding='utf-8')) if REPORT.exists() else {}
    entries = old.get('products', {})
    text = '\n'.join(p.read_text(encoding='utf-8') for p in (ROOT / 'paginas').rglob('*.md'))
    labelled = re.findall(r'\[([^\]]+)\]\((https://[^\s)]+)\)', text)
    sources = list(dict.fromkeys(re.findall(r'https://[^\s)<>"\']+', text)))
    sources = [u for u in sources if not re.search(r'\.pdf(?:$|\?)|meli\.la|mercadolibre|toolservicenet|boschtoolservice', u)]
    products = inventory()
    # Una misma referencia reutiliza la misma foto en todos sus destinos.
    groups = {}
    for url, p in products.items():
        key = norm(p['brand'] + p['model'])
        groups.setdefault(key, []).append((url, p))
    def work(key, group):
        for url, _ in group:
            if entries.get(url, {}).get('image') and (ROOT / entries[url]['image'].lstrip('/')).exists():
                return key, group, entries[url]
        p = group[0][1]
        model = p['model'].split(' · ')[0]
        model = re.sub(r'^Professional\s+|\s+Black Series$', '', model)
        # Descripciones ambiguas no se convierten en fotos de otro modelo.
        if any(s in model.lower() for s in ('confirmar', 'compatible con', '+', '3000 w')):
            return key, group, dict(status='pending', reason='Identidad o kit ambiguo')
        k = norm(model)
        matched = [u for u in sources if len(k) >= 4 and k in norm(u)]
        matched += [u for label, u in labelled if k in norm(label) and u in sources]
        extra = json.loads((ROOT / 'fuentes-fotos-adicionales.json').read_text(encoding='utf-8')) if (ROOT / 'fuentes-fotos-adicionales.json').exists() else {}
        matched += extra.get(norm(p['brand'] + model), [])
        search = json.loads((ROOT / 'fuentes-fotos-busqueda.json').read_text(encoding='utf-8')) if (ROOT / 'fuentes-fotos-busqueda.json').exists() else {}
        matched += search.get(norm(p['brand'] + model), [])
        aliases = json.loads((ROOT / 'codigos-fotos-modelos.json').read_text(encoding='utf-8')) if (ROOT / 'codigos-fotos-modelos.json').exists() else {}
        lookup_model = aliases.get(norm(p['brand'] + model), model)
        if norm(p['brand']) == 'lusqtoff':
            matched.insert(0, 'https://www.lusqtoff.com.ar/ver-producto/' + model)
        for _, variant in group:
            for field in ('image_source', 'source'):
                u = variant.get(field) or ''
                if u.startswith('https://') and not re.search(r'meli\.la|mercadolibre|\.pdf', u):
                    matched.append(u)
        errors = []
        for _, variant in group:
            photo = variant.get('existing') or ''
            if photo.startswith('https://') and 'TS223558-4' not in model:
                try:
                    return key, group, dict(status='existing-source', model=model, brand=p['brand'],
                        source=variant.get('image_source') or variant.get('source'), checked='2026-10-01',
                        **optimize(photo, key))
                except Exception as exc:
                    errors.append(type(exc).__name__)
        for source in dict.fromkeys(matched):
            try:
                for photo in candidates(lookup_model, source)[:3]:
                    try:
                        return key, group, dict(status='verified', model=model, brand=p['brand'],
                            source=source, checked='2026-10-01', **optimize(photo, key))
                    except Exception as exc:
                        errors.append(type(exc).__name__)
            except Exception as exc:
                errors.append(type(exc).__name__)
        # Fotos ya atribuidas a una ficha de modelo en el catálogo existente.
        for _, variant in group:
            photo = variant.get('existing') or ''
            if photo.startswith('https://') and not ('TS223558-4' in model):
                try:
                    return key, group, dict(status='existing-source', model=model, brand=p['brand'],
                        source=variant.get('image_source') or variant.get('source'), checked='2026-10-01',
                        **optimize(photo, key))
                except Exception as exc:
                    errors.append(type(exc).__name__)
        return key, group, dict(status='pending', model=model, brand=p['brand'],
                               reason='Sin foto verificable en fuentes consultadas', sources=matched,
                               errors=list(dict.fromkeys(errors)))
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(work, key, group) for key, group in groups.items()]
        for future in as_completed(futures):
            key, group, result = future.result()
            for url, _ in group:
                entries[url] = result
            temporary = REPORT.with_suffix('.tmp')
            temporary.write_text(json.dumps(dict(products=entries), ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(REPORT)
            print(result['status'], key, result.get('bytes', ''), flush=True)
    verified = [x for x in entries.values() if x.get('image')]
    print('RESULTADO', len(verified), '/', len(products), 'destinos con foto', flush=True)

if __name__ == '__main__':
    main()
