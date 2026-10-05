"""Enlaces del sitio principal hacia el historial de precios (sin depender de datos en tiempo de ejecución)."""
import json
from functools import lru_cache
from html import escape as esc

from observatorio.gratuito import MANIFEST, CATEGORIES
from observatorio.estatico import GUIDES, HUB, model_path

BOX_STYLE = 'margin:2.5rem 0;padding:1.4rem 1.6rem;border:1px solid var(--border);border-left:4px solid var(--orange);border-radius:6px'


@lru_cache(maxsize=1)
def _data():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    guides = json.loads(GUIDES.read_text(encoding='utf-8')) if GUIDES.is_file() else {}
    by_guide = {}
    for model in manifest['models']:
        for guide in guides.get(model['id'], []):
            by_guide.setdefault(guide['url'], []).append(model)
    return manifest['models'], by_guide


def _items(models):
    return ''.join(f'<li><a href="{model_path(m)}">Precio e historial del {esc(m["brand"] + " " + m["model"])}</a></li>' for m in models)


def render_guide_prices(article_url):
    """Bloque para guías que mencionan modelos seguidos a diario."""
    _, by_guide = _data()
    models = by_guide.get(article_url, [])[:6]
    if not models:
        return ''
    return (f'<aside class="observed-prices" aria-labelledby="observed-prices-title" style="{BOX_STYLE}">'
            '<h2 id="observed-prices-title" style="margin-top:0">¿Cuánto cuestan hoy?</h2>'
            '<p>Seguimos todos los días el precio publicado y el stock de estos modelos, con su historial completo:</p>'
            f'<ul>{_items(models)}</ul>'
            f'<p><a href="{HUB}">Ver todos los precios de herramientas →</a></p></aside>')


def render_category_prices(section_id):
    """Bloque para el hub de una categoría con modelos seguidos."""
    if section_id not in CATEGORIES:
        return ''
    models, _ = _data()
    selected = [m for m in models if m['category'] == section_id]
    if not selected:
        return ''
    name = CATEGORIES[section_id].lower()
    return (f'<aside class="observed-prices" aria-labelledby="observed-prices-title" style="{BOX_STYLE}">'
            f'<h2 id="observed-prices-title" style="margin-top:0">Precios de {esc(name)} hoy</h2>'
            f'<p>Seguimos a diario {len(selected)} {esc(name)}: precio publicado, stock e historial para saber si conviene comprar ahora.</p>'
            f'<ul>{_items(selected)}</ul>'
            f'<p><a href="/datos/precios/{section_id}/">Ver la tabla de precios de {esc(name)} →</a></p></aside>')
