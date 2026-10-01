"""Portadas locales de las guías, compartidas por tarjetas y buscador."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATH = ROOT / 'portadas-guias.json'
COVERS = json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else {}

def guide_cover(article):
    return COVERS.get(article['url'], {})
