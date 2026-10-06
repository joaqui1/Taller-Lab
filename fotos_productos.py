"""Fotos locales verificadas; sin solicitudes externas al renderizar páginas."""
from html import escape, unescape
import json
from pathlib import Path
from urllib.parse import urlsplit
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'fotos-modelos.json'
PHOTOS = json.loads(MANIFEST.read_text(encoding='utf-8')).get('products', {}) if MANIFEST.exists() else {}

def source_key(url):
    parsed=urlsplit(url or '')
    host=(parsed.hostname or '').lower()
    if host.startswith('www.'):
        host=host[4:]
    return (parsed.scheme,host,parsed.port,parsed.path.rstrip('/'),parsed.query)

SOURCE_PHOTOS={source_key(url):photo for url,photo in PHOTOS.items()}

def model_key(brand, model):
    text = unicodedata.normalize('NFKD', brand + model).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', text)

def photo_for(url=None, brand='', model=''):
    photo = PHOTOS.get(url, {}) or SOURCE_PHOTOS.get(source_key(url),{})
    if not photo.get('image') and brand and model:
        key = model_key(brand, model)
        photo = next((p for p in PHOTOS.values() if p.get('image') and model_key(p.get('brand', ''), p.get('model', '')) == key), {})
    return photo if photo.get('image', '').startswith('/assets/productos/') else {}

def apply_photos(facts):
    for url, fact in facts.items():
        photo = photo_for(url)
        if photo:
            fact.update(image=photo['image'], image_source=photo['source'], illustrative=False,
                        image_width=photo['width'], image_height=photo['height'])
            # Una advertencia histórica sobre la foto anterior queda obsoleta.
            if 'La foto de CIDLI20668-3' in (fact.get('warning') or ''):
                fact['warning'] = 'Datos declarados en la publicación comercial; confirmá variante y contenido del kit.'

def render_photo(url=None, brand='', model=''):
    photo = photo_for(url, brand, model)
    if not photo:
        return ''
    label = (brand + ' ' + model).strip() or (photo.get('brand', '') + ' ' + photo.get('model', '')).strip()
    return (f'<div class="offer-photo"><img src="{escape(photo["image"], quote=True)}" '
            f'alt="{escape(label, quote=True)}" width="{photo["width"]}" height="{photo["height"]}" '
            'loading="lazy" decoding="async"></div>')

def add_photos_to_cards(document):
    """Completa las tarjetas comerciales históricas guardadas dentro del Markdown."""
    def decorate(match):
        card=match.group(0)
        if 'class="offer-photo"' in card or 'class="illustrative-product"' in card:
            return card
        urls=[unescape(u) for u in re.findall(r'href="([^"]+)"',card)]
        url=next((u for u in urls if photo_for(u)),None)
        if not url:
            return card
        heading=re.search(r'<h3\b[^>]*>(.*?)</h3>',card,re.S)
        label=unescape(re.sub(r'<[^>]+>','',heading.group(1))) if heading else ''
        photo=render_photo(url,model=label)
        return card[:heading.start()]+photo+card[heading.start():] if heading else card
    document=re.sub(r'<article\b[^>]*class="[^\"]*\boffer-card\b[^\"]*"[^>]*>.*?</article>',decorate,document,flags=re.S)
    def decorate_row(match):
        row=match.group(0)
        if '/assets/productos/' in row:
            return row
        urls=[unescape(u) for u in re.findall(r'href="([^"]+)"',row)]
        url=next((u for u in urls if photo_for(u)),None)
        cell=re.search(r'<td\b[^>]*>(.*?)</td>',row,re.S)
        if not url or not cell:
            return row
        label=unescape(re.sub(r'<[^>]+>','',cell.group(1)))
        photo=photo_for(url)
        tag=(f'<img class="model-table-photo" src="{escape(photo["image"],quote=True)}" '
             f'alt="{escape(label,quote=True)}" width="{photo["width"]}" height="{photo["height"]}" '
             'loading="lazy" decoding="async">')
        return row[:cell.start(1)]+tag+row[cell.start(1):]
    document = re.sub(r'<tr\b[^>]*>.*?</tr>',decorate_row,document,flags=re.S)
    def wrap_table(match):
        table = match.group(0)
        if 'model-table-photo' not in table:
            return table
        return '<div class="model-table-scroll" tabindex="0" aria-label="Comparación de modelos">' + table + '</div>'
    return re.sub(r'<table\b[^>]*>.*?</table>',wrap_table,document,flags=re.S)
