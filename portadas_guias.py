"""Portadas locales de las guías, compartidas por tarjetas y buscador."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATH = ROOT / 'portadas-guias.json'
COVERS = json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else {}

def guide_cover(article):
    cover = COVERS.get(article['url'], {})
    if cover.get('kind') != 'product' or not cover.get('image', '').startswith('/assets/productos/'):
        raise ValueError('Guía sin foto real verificada: ' + article['url'])
    return cover
