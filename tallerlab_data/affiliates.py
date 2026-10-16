"""Explicit mappings to existing affiliate links; no matching by broad category."""
import json
from html import escape
from functools import lru_cache
from pathlib import Path
import re

# Already used in TallerLab's buying guides. A listing is not a verified offer.
LINKS = {
    'ingco-cidli20668-4': ('CIDLI20668-4', 'https://meli.la/2xvJRJp', '/taladros/taladro-percutor-inalambrico/'),
    'omaha-ab550161k': ('AB550161K', 'https://meli.la/2Znq55m', '/taladros/taladro-de-banco/'),
    'lusqtoff-hl100-7': ('HL100-7', 'https://meli.la/1cZXqxL', '/hidrolavadoras/lusqtoff/'),
    'logus-hl-105': ('HL-105', 'https://meli.la/2Rcddpg', '/hidrolavadoras/comparativa-general/'),
    'dowen-pagio-9993220-7': ('9993220.7', 'https://meli.la/1QUvfns', '/amoladoras/dowen-pagio/'),
    'gamma-g1910kar': ('G1910KAR', 'https://meli.la/12aMvrG', '/amoladoras/gamma/'),
    'bosch-gws-770': ('06013980E0', 'https://meli.la/1GRCAjZ', '/amoladoras/bosch/'),
    'lusqtoff-sml120-8dk': ('SML120-8DK', 'https://meli.la/26RsZRw', '/soldadoras/mig-lusqtoff/'),
    'lusqtoff-iron-100': ('MEGAIRON100-8', 'https://meli.la/1knTbU1', '/soldadoras/lusqtoff-iron-100/'),
    'esab-handyarc-162i': ('0409616', 'https://meli.la/1mZhwNS', '/soldadoras/esab-handyarc-162i/'),
    'pektra-gpk980': ('GPK980', 'https://meli.la/2jcLSy1', '/generadores/chicos/'),
    'philco-ge-ph2500alp': ('GE-PH2500ALP', 'https://meli.la/1nUAUuv', '/generadores/a-nafta/'),
    # Selecciones previas mantenidas al sumar ofertas exactas del catálogo.
    'bosch-gws-850': ('06013775H0', 'https://meli.la/1hDoFyN', None),
    'dewalt-dwe4120': ('DWE4120', 'https://meli.la/13LHGQm', None),
    'dewalt-dcf887': ('DCF887B', 'https://meli.la/1hh4SkK', None),
    'gamma-g2801ar': ('G2801AR', 'https://meli.la/1vR4xKe', None),
    'lusqtoff-iron-250': ('IRON-250', 'https://meli.la/26R9o7z', None),
}

TABLE_PATH = Path(__file__).with_name("afiliados_por_modelo.json")
DISCLOSURE = "Podemos recibir una comisión si comprás desde este enlace"


@lru_cache(maxsize=1)
def _table():
    try:
        payload = json.loads(TABLE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload.get("models", {}) if isinstance(payload, dict) else {}


def affiliate_record_for(tool):
    record = _table().get(tool.slug)
    if (not isinstance(record, dict) or record.get("mpn") != tool.mpn
            or not re.fullmatch(r"https://meli\.la/[A-Za-z0-9]+", str(record.get("url", "")))):
        return None
    return record


def affiliate_for(tool):
    record = affiliate_record_for(tool)
    if not record:
        return None
    return (record["mpn"], record["url"], record.get("guide_url"))


def affiliate_urls():
    return {record["url"] for record in _table().values()
            if isinstance(record, dict)
            and re.fullmatch(r"https://meli\.la/[A-Za-z0-9]+", str(record.get("url", "")))}


def render_affiliate_button(tool):
    record = affiliate_record_for(tool)
    if not record:
        return ""
    url = escape(record["url"], quote=True)
    return (f'<div class="tl-affiliate-action"><a class="tl-nav-pill active" href="{url}" '
            'target="_blank" rel="sponsored nofollow noopener" '
            'data-affiliate-placement="tallerlab-data">Ver precio en Mercado Libre ↗</a>'
            f'<small class="tl-affiliate-disclosure">{DISCLOSURE}</small></div>')


def render_affiliate_options(tools):
    rows = []
    for tool in tools:
        entry = affiliate_for(tool)
        if not entry:
            continue
        code, url, guide = entry
        guide_link = f' <a href="{escape(guide, quote=True)}">Leer la guía de compra</a>' if guide else ""
        rows.append(f'<li><strong>{escape(tool.brand)} {escape(tool.model_name)}</strong> · código de referencia {escape(code)}<br><a class="tl-nav-pill" href="{escape(url, quote=True)}" target="_blank" rel="sponsored nofollow noopener" data-affiliate-placement="tallerlab-data">Ver precio en Mercado Libre ↗</a> <small class="tl-affiliate-disclosure">{DISCLOSURE}</small>{guide_link}</li>')
    if not rows:
        return ''
    return '<section class="tl-card" id="tl-commercial-options" aria-label="Enlaces afiliados de Mercado Libre"><h2>Ver precio en Mercado Libre</h2><p>Publicaciones asociadas a guías de compra; el precio y la disponibilidad pueden cambiar.</p><ul>'+''.join(rows)+'</ul><p>Confirmá que el código completo, la alimentación y el kit coincidan con lo que necesitás. El enlace no acredita equivalencia con la ficha ni una recomendación por rendimiento.</p></section>'
