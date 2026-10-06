"""Explicit mappings to existing affiliate links; no matching by broad category."""
from html import escape

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
}


def affiliate_for(tool):
    entry = LINKS.get(tool.slug)
    return entry if entry and entry[0] == tool.mpn else None


def render_affiliate_options(tools):
    rows = []
    for tool in tools:
        entry = affiliate_for(tool)
        if not entry:
            continue
        code, url, guide = entry
        rows.append(f'<li><strong>{escape(tool.brand)} {escape(tool.model_name)}</strong> · código de referencia {escape(code)}<br><a class="tl-nav-pill" href="{escape(url, quote=True)}" target="_blank" rel="sponsored nofollow noopener noreferrer" data-affiliate-placement="tallerlab-data">Consultar publicación de {escape(tool.brand)} {escape(tool.model_name)} ↗</a> <a href="{guide}">Leer la guía de compra</a></li>')
    if not rows:
        return ''
    return '<section class="tl-card" id="tl-commercial-options" aria-label="Publicaciones comerciales relacionadas"><h2>Consultar una publicación del modelo</h2><p class="tl-affiliate-disclosure"><strong>Aviso comercial:</strong> si comprás mediante estos enlaces de afiliado, TallerLab puede cobrar una comisión.</p><p>Son publicaciones comerciales asociadas a las guías, sin precio ni disponibilidad verificados en esta edición.</p><ul>'+''.join(rows)+'</ul><p>Confirmá que el código completo de la unidad, la alimentación y el kit ofrecido coincidan con lo que necesitás. Una publicación puede agrupar variantes; el enlace no acredita equivalencia con la ficha ni una recomendación por rendimiento.</p></section>'
