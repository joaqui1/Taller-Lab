"""Publica el piloto gratuito sin SQLite, PostgreSQL ni servidor de aplicaciones."""
import csv
import json
import re
import shutil
import statistics
import unicodedata
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from html import escape as esc
from pathlib import Path
from zoneinfo import ZoneInfo

from observatorio.gratuito import ROOT, MANIFEST, CATEGORIES, read_history, atomic_json

HUB = '/datos/precios-herramientas-argentina/'
METHOD = '/datos/precios/metodologia/'
FRESH_HOURS = 48
PUBLICATION_MANIFEST = ROOT / 'assets' / 'datos' / 'observatorio-publicacion.json'


def parse_time(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None: raise ValueError('Fecha sin zona horaria')
    return result


def stamp(value):
    return parse_time(value).astimezone(ZoneInfo('America/Argentina/Buenos_Aires')).strftime('%d/%m/%Y · %H:%M ART') if value else 'Sin captura'


def peso(value):
    if value is None: return 'Sin precio'
    return '$ ' + format(Decimal(value), ',.2f').replace(',', '@').replace('.', ',').replace('@', '.')


def current_state(observation, attempt, now):
    if not observation: return 'error' if attempt.get('status') == 'error' else 'pendiente'
    age = (now - parse_time(observation['observed_at'])).total_seconds()
    if attempt.get('status') == 'error' and parse_time(attempt['observed_at']) >= parse_time(observation['observed_at']): return 'error'
    if age < 0 or age > FRESH_HOURS * 3600: return 'vencido'
    return observation['availability'] if observation['availability'] in ('disponible', 'agotado') else 'desconocido'


def snapshot(history, manifest, now=None):
    now = now or datetime.now(timezone.utc)
    rows = []
    for model in manifest['models']:
        series = sorted([o for o in history['observations'] if o['model_id'] == model['id']], key=lambda o: o['observed_at'])
        observation = series[-1] if series else None
        attempt = history['latest_attempts'].get(model['id'], {})
        state = current_state(observation, attempt, now)
        previous = [o for o in series[:-1] if o['availability'] == 'disponible' and o['price_ars']]
        change = None
        if state == 'disponible' and observation['price_ars'] and previous:
            change = round((Decimal(observation['price_ars']) / Decimal(previous[-1]['price_ars']) - 1) * 100, 1)
        change_kind = classify_change(previous[-1], observation) if change is not None else None
        rows.append(dict(model=model, observation=observation, attempt=attempt, state=state, series=series, change=change, change_kind=change_kind))
    return rows


CHANGE_LABELS = {'offer_ended': 'Fin de oferta', 'offer_started': 'Inicio de oferta',
                 'offer_changed': 'Cambio de oferta', 'price_changed': 'Cambio de precio',
                 'unchanged': 'Sin cambio'}


def classify_change(previous, current):
    """Clasifica hechos observados; un precio tachado no acredita un precio de lista."""
    before, after = Decimal(previous['price_ars']), Decimal(current['price_ars'])
    old_ref = Decimal(previous['reference_ars']) if previous.get('reference_ars') else None
    new_ref = Decimal(current['reference_ars']) if current.get('reference_ars') else None
    old_offer = old_ref is not None and old_ref > before
    new_offer = new_ref is not None and new_ref > after
    if before == after:
        return 'unchanged'
    if old_offer and not new_offer and after == old_ref:
        return 'offer_ended'
    if new_offer and not old_offer and before == new_ref:
        return 'offer_started'
    if old_offer or new_offer:
        return 'offer_changed'
    return 'price_changed'


LABELS = {'disponible':'Disponible', 'agotado':'Agotado', 'vencido':'Dato vencido',
          'error':'Sin verificación', 'pendiente':'Sin captura', 'desconocido':'Stock sin confirmar'}


def offer_tag(o):
    return f' <small class="offer-tag">oferta · tachado {esc(peso(o["reference_ars"]))}</small>' if is_offer(o) else ''


def render_row(row, sources, href=None):
    m = row['model']; o = row['observation']; state = row['state']; source = sources[m['source']]
    latest = o['observed_at'] if o else ''
    active = state == 'disponible' and o['price_ars']
    price = peso(o['price_ars']) if active else '—'
    change = f"{row['change']:+.1f}%" if row['change'] is not None else '—'
    direction = 'down' if row['change'] is not None and row['change'] < 0 else ''
    history = ''.join(f'<tr><td>{esc(stamp(h["observed_at"]))}</td><td>{esc(peso(h["price_ars"]))}{offer_tag(h)}</td><td>{esc(LABELS[h["availability"]])}</td></tr>' for h in reversed(row['series'][-30:]))
    if not history: history = '<tr><td colspan="3">Todavía no hay una observación válida.</td></tr>'
    reason = row['attempt'].get('reason', '')
    note = '<p class="error-note">'+esc(reason)+'</p>' if reason and state == 'error' else ''
    ref = f'<p class="reference-note">Precio tachado por el comercio en esa captura: {esc(peso(o["reference_ars"]))}. No demuestra un descuento histórico.</p>' if o and o.get('reference_ars') else ''
    return f'''<article class="product" data-id="{esc(m['id'])}" data-brand="{esc(m['brand'])}" data-model="{esc(m['model'])}" data-variant="{esc(m['variant'])}" data-url="{esc(m['url'])}" data-category="{esc(m['category'])}" data-state="{state}" data-observed="{esc(latest)}" data-price="{esc(o['price_ars'] or '') if o else ''}" data-search="{esc(m['brand']+' '+m['model']+' '+m['variant']+' '+CATEGORIES[m['category']])}">
<div class="product-name"><span class="brand">{esc(m['brand'])} <span class="category-small">/ {CATEGORIES[m['category']]}</span></span><h3>{('<a href="'+href+'">'+esc(m['model'])+'</a>') if href else esc(m['model'])}</h3><p>{esc(m['variant'])}</p></div>
<div class="product-price"><strong class="current-price">{price}</strong><span class="price-caption">{'Precio publicado · ARS' if active else LABELS[state]}</span></div>
<div class="product-stock"><span class="badge {state}">{LABELS[state]}</span><small>{esc(stamp(latest))}</small></div>
<div class="product-change {direction}"><span class="change">{change}</span><small>{CHANGE_LABELS.get(row.get('change_kind'), 'vs. captura anterior')}</small></div>
<div class="product-source"><a href="{esc(m['url'])}" target="_blank" rel="noopener noreferrer">{esc(source['name'])} <span aria-hidden="true">↗</span></a><small>Ver condiciones y envío</small></div>
<details><summary>Ver historial <span aria-hidden="true">＋</span></summary><div class="history">{note}<p>Observaciones de esta ficha y variante. Los importes históricos no son ofertas vigentes.</p>{ref}<div class="history-scroll"><table><caption>Últimas 30 capturas de {esc(m['brand']+' '+m['model'])}</caption><thead><tr><th>Captura</th><th>Precio observado (ARS)</th><th>Stock observado</th></tr></thead><tbody>{history}</tbody></table></div></div></details></article>'''


SITE = 'https://www.tallerlab.com.ar'
DATA_LICENSE = 'https://creativecommons.org/licenses/by/4.0/deed.es'
VERDICT_MIN = 14
STATS_WINDOW = 90
ASSET_VERSION = '5'
GUIDES = Path(__file__).resolve().parent / 'guias_por_modelo.json'
ART = ZoneInfo('America/Argentina/Buenos_Aires')
MODEL_RE = re.compile(r'^/datos/precios/(' + '|'.join(CATEGORIES) + r')/([a-z0-9-]+)/$')


def model_slug(model):
    text = unicodedata.normalize('NFKD', f"{model['brand']} {model['model']}")
    text = ''.join(c for c in text if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')


def model_path(model):
    return f"/datos/precios/{model['category']}/{model_slug(model)}/"


def day(value):
    return parse_time(value).astimezone(ART).strftime('%d/%m/%Y') if value else ''


def short_peso(value):
    return peso(value).rsplit(',', 1)[0] if value is not None else 'Sin precio'


def variant_text(model):
    """Variante legible; las fichas sin variante declarada devuelven cadena vacía."""
    value = re.sub(r'\s*·?\s*ficha individual( del comercio)?\s*$', '', model['variant'], flags=re.I).strip(' ·')
    return value


def priced(series):
    return [o for o in series if o['availability'] == 'disponible' and o['price_ars']]


def is_offer(o):
    """La ficha mostraba un precio tachado mayor al cobrado: un descuento visible ese día."""
    try:
        return bool(o.get('reference_ars')) and Decimal(o['reference_ars']) > Decimal(o['price_ars'])
    except (ArithmeticError, TypeError, ValueError, KeyError):
        return False


def price_stats(series):
    window = priced(series)[-STATS_WINDOW:]
    values = [Decimal(o['price_ars']) for o in window]
    if not values: return None
    low = min(values)
    # Si el mínimo solo se vio con descuento visible, se aclara: no es el precio habitual.
    min_offer = next((o for o in window if Decimal(o['price_ars']) == low and is_offer(o)), None)
    if min_offer and any(Decimal(o['price_ars']) == low and not is_offer(o) for o in window):
        min_offer = None
    return {'n': len(values), 'min': low, 'max': max(values), 'median': statistics.median(values), 'min_offer': min_offer}


def verdict(row, stats):
    name = esc(row['model']['brand'] + ' ' + row['model']['model'])
    if row['state'] != 'disponible':
        return 'unknown', f'Hoy no hay un precio vigente para comparar: la última captura figura como «{LABELS[row["state"]].lower()}». El historial sigue disponible abajo.'
    if not stats or stats['n'] < VERDICT_MIN:
        n = stats['n'] if stats else 0
        return 'collecting', f'Todavía no hay historial suficiente para calificar el precio: llevamos {n} de {VERDICT_MIN} capturas con precio de esta ficha. Hasta entonces mostramos los datos sin opinar.'
    diff = (Decimal(row['observation']['price_ars']) / stats['median'] - 1) * 100
    if diff <= -5:
        return 'below', f'El precio de hoy está {abs(diff):.0f}% por debajo de la mediana de sus últimas {stats["n"]} capturas. Es un buen momento relativo para el {name}, si la variante es la que necesitás.'
    if diff >= 5:
        return 'above', f'El precio de hoy está {diff:.0f}% por encima de la mediana de sus últimas {stats["n"]} capturas. Si no tenés apuro, conviene esperar o comparar otros comercios.'
    return 'normal', f'El precio de hoy está cerca de la mediana de sus últimas {stats["n"]} capturas ({diff:+.1f}%). Esta comparación no permite afirmar si es una oferta ni si es el mejor precio del mercado.'


def chart_svg(series, label):
    points = [(parse_time(o['observed_at']), Decimal(o['price_ars'])) for o in priced(series)][-180:]
    if len(points) < 2:
        return f'<p class="chart-empty">El gráfico aparece desde la segunda captura con precio. Por ahora hay {len(points)}.</p>'
    W, H, L, R, T, B = 720, 240, 104, 16, 18, 34
    t0, t1 = points[0][0].timestamp(), points[-1][0].timestamp()
    lo, hi = min(p for _, p in points), max(p for _, p in points)
    if hi == lo: lo, hi = lo * Decimal('0.97'), hi * Decimal('1.03')
    x = lambda t: L + (W - L - R) * ((t.timestamp() - t0) / (t1 - t0) if t1 > t0 else 1)
    y = lambda p: T + (H - T - B) * float((hi - p) / (hi - lo))
    line = ' '.join(f'{x(t):.1f},{y(p):.1f}' for t, p in points)
    grid = ''.join(f'<line x1="{L}" x2="{W-R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/><text x="{L-10}" y="{y(v)+4:.1f}" text-anchor="end">{esc(short_peso(v))}</text>' for v in (hi, (hi + lo) / 2, lo))
    dates = f'<text x="{L}" y="{H-8}">{day(points[0][0].isoformat())}</text><text x="{W-R}" y="{H-8}" text-anchor="end">{day(points[-1][0].isoformat())}</text>'
    t, p = points[-1]
    return f'<svg class="price-chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">{grid}{dates}<polyline points="{line}" class="line"/><circle cx="{x(t):.1f}" cy="{y(p):.1f}" r="4" class="dot"/></svg>'


def movements(rows):
    result = []
    for r in rows:
        series = priced(r['series'])
        if r['state'] != 'disponible' or len(series) < 2: continue
        last = series[-1]; cutoff = parse_time(last['observed_at']) - timedelta(days=30)
        start = next((o for o in series[:-1] if parse_time(o['observed_at']) >= cutoff), None)
        if not start: continue
        change = (Decimal(last['price_ars']) / Decimal(start['price_ars']) - 1) * 100
        if abs(change) >= 1: result.append((change, r, start))
    return sorted(result, key=lambda m: -abs(m[0]))


OFFER_KINDS = ('offer_ended', 'offer_started', 'offer_changed')


def split_movements(moves):
    """Separa cambios del precio publicado de entradas y salidas de ofertas: no se mezclan en un mismo ranking."""
    prices = [m for m in moves if classify_change(m[2], m[1]['observation']) not in OFFER_KINDS]
    offers = [m for m in moves if classify_change(m[2], m[1]['observation']) in OFFER_KINDS]
    return prices[:6], offers[:6]


def dataset_schema(name, description, canonical, csv_url, observations, modified):
    days = sorted(o['day_art'] for o in observations if o.get('day_art'))
    org = {'@type': 'Organization', 'name': 'TallerLab', 'url': SITE + '/'}
    schema = {'@context': 'https://schema.org', '@type': 'Dataset', 'name': name, 'description': description, 'url': canonical,
              'inLanguage': 'es-AR', 'isAccessibleForFree': True, 'license': DATA_LICENSE, 'creator': org, 'publisher': org,
              'spatialCoverage': {'@type': 'Place', 'name': 'Argentina'},
              'variableMeasured': ['Precio publicado en pesos argentinos (ARS)', 'Disponibilidad de stock'],
              'measurementTechnique': 'Captura diaria de fichas públicas de comercios argentinos, con validación de modelo, variante, moneda y stock.',
              'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': csv_url}]}
    if days: schema['temporalCoverage'] = days[0] + '/' + days[-1]
    if modified: schema['dateModified'] = modified
    return schema


def breadcrumb_schema(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}


def breadcrumb_html(items):
    parts = [f'<a href="{h}">{esc(n)}</a>' if h else f'<span aria-current="page">{esc(n)}</span>' for n, h in items]
    return '<nav class="breadcrumbs" aria-label="Ruta de navegación">' + ' <span aria-hidden="true">/</span> '.join(parts) + '</nav>'


def page(title, description, canonical, schema, noindex, url, body, og_type='website', published_at=''):
    robots = 'noindex, follow' if noindex else 'index, follow, max-image-preview:large'
    ld = ''.join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False).replace('<', chr(92) + 'u003c') + '</script>' for s in schema)
    v = '?v=' + ASSET_VERSION
    return f'''<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{esc(canonical)}"><meta name="robots" content="{robots}"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="TallerLab"><meta property="og:locale" content="es_AR"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{SITE}/assets/hero-taller-claro-v3.webp"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="{url('/assets/favicon.svg')}"><link rel="stylesheet" href="{url('/assets/observatorio-gratuito.css')}{v}"><script defer src="{url('/assets/observatorio-gratuito.js')}{v}"></script>{ld}</head><body><a class="skip" href="#main">Ir al contenido</a><header><a class="wordmark" href="{SITE}/" aria-label="TallerLab, inicio">Taller<span>Lab</span><i aria-hidden="true">▦</i></a><nav aria-label="Navegación principal"><a href="{url(HUB)}">Precios</a><a href="{url(METHOD)}">Metodología</a><a class="editorial-link" href="{SITE}/">Guías de compra</a></nav></header><main id="main" data-publication="{esc(published_at)}">{body}</main><footer><a class="wordmark" href="{SITE}/">Taller<span>Lab</span></a><p>Precios de herramientas · Argentina<br>Precios informativos. La oferta final la confirma el comercio.</p><p class="footer-links"><a href="{url(METHOD)}">Metodología</a> · <a href="{url(METHOD)}#citar">Citar los datos</a> · <a href="{url('/assets/datos/precios-observatorio-publico.json')}">Datos JSON</a> · <a href="{SITE}/como-trabajamos/">Cómo trabajamos</a></p></footer></body></html>'''


def cite_block(canonical, observed):
    return f'''<section class="cite" id="citar"><div><p class="eyebrow">Para medios, foros y docentes</p><h2>Usá estos datos,<br>citando la fuente.</h2></div><div><p>Los precios, tablas y gráficos se pueden reproducir con atribución (<a href="{DATA_LICENSE}" rel="license">licencia CC BY 4.0</a>). Sugerimos esta cita, con enlace:</p><blockquote>Fuente: TallerLab, historial de precios de herramientas en Argentina, captura del {esc(day(observed))}. {esc(canonical)}</blockquote><p>¿Necesitás una serie o un corte que no está publicado? <a href="{SITE}/contacto/">Escribinos</a>.</p></div></section>'''


def methodology(manifest, url, count_by_source=None):
    sources = ''.join(f'<li><a href="{esc(s["home"])}" target="_blank" rel="noopener noreferrer">{esc(s["name"])}</a> · <a href="{esc(s["robots"])}" target="_blank" rel="noopener noreferrer">robots.txt</a>{(" · <a href="+chr(34)+esc(s["terms"])+chr(34)+" target="+chr(34)+"_blank"+chr(34)+" rel="+chr(34)+"noopener noreferrer"+chr(34)+">condiciones</a>") if s.get("terms") else ""}</li>' for s in manifest['sources'].values())
    counts = count_by_source or {}
    split = ', '.join(f'{counts.get(k, 0)} de {esc(s["name"])}' for k, s in manifest['sources'].items())
    return f'''<section class="methodology"><p class="eyebrow">Cómo leer los datos</p><h1>Cómo medimos los precios<br>de herramientas.</h1><p class="lead">Observamos fichas concretas de herramientas en comercios argentinos. Publicamos lo que pudimos verificar y dejamos visibles las limitaciones.</p>
<div class="method-grid"><section><span class="chapter">01 / Alcance</span><h2>Un piloto de {len(manifest['models'])} modelos</h2><p>{esc(manifest['selection'])}</p><p>Hay una oferta configurada por modelo. No es una comparación exhaustiva de comercios ni un «mínimo del mercado». Tampoco medimos ventas o inflación oficial.</p></section>
<section><span class="chapter">02 / Captura</span><h2>La ficha, no los recomendados</h2><p>Comprobamos URL, SKU, referencia, marca, título y propiedades de la variante. El precio estructurado debe coincidir con el precio principal de la ficha y la moneda debe ser ARS. En DGM el importe visible se redondea al peso: exigimos ese redondeo exacto y conservamos los centavos estructurados. Un cero de una ficha agotada se guarda como ausencia de precio.</p><p>Se consultan estas fuentes públicas, con al menos tres segundos entre solicitudes al mismo comercio:</p><ul>{sources}</ul><p>Revisamos robots.txt en cada ejecución. No evitamos bloqueos, CAPTCHA, límites ni accesos restringidos. Robots.txt es una regla de acceso técnico, no una licencia comercial.</p></section>
<section><span class="chapter">03 / Vigencia</span><h2>48 horas, como máximo</h2><p>Solo se muestra como actual un precio validado, disponible y con menos de 48 horas. Un error posterior invalida su verificación actual. Los datos vencidos, agotados o sin stock confirmado permanecen en el historial y se excluyen de los precios actuales.</p><p>La página comprueba la edad al abrirse. Una captura programada puede demorarse o fallar; el horario no es una garantía.</p></section>
<section><span class="chapter">04 / Condiciones</span><h2>Antes de pagar, confirmá</h2><p>Mostramos el importe publicado en la ficha; no sumamos envío ni calculamos cuotas o descuentos por transferencia. No damos por incluido ningún accesorio que la variante no identifique. El comercio confirma stock, impuestos, medios de pago y precio final.</p><p>La ficha Bosch GHP 4-50 declara 60 Hz: se conserva esa advertencia. Las propiedades técnicas erróneas del vendedor no se convierten en recomendaciones de uso.</p></section>
<section><span class="chapter">05 / Historia</span><h2>Sin rellenar los días que faltan</h2><p>Guardamos hasta 365 días, una captura válida por modelo y día de Argentina. La variación compara las dos últimas observaciones disponibles de la misma ficha, no necesariamente días consecutivos. Con una sola captura no hay variación.</p><p>Rotulamos «fin de oferta» cuando el precio vuelve exactamente al importe tachado en la captura anterior y ya no tiene descuento visible; «inicio de oferta» cuando sucede lo inverso. Si hay descuentos con otra referencia, indicamos «cambio de oferta». Es una clasificación de las fichas observadas, no una confirmación del motivo comercial ni de un aumento de lista.</p><p>Los cambios de precio se incorporan automáticamente cuando coinciden la identidad, la variante, la moneda y el precio principal visible con la oferta estructurada del comercio. Un salto de 35% o más frente a la mediana de las últimas siete observaciones disponibles queda registrado en el historial. Los datos contradictorios se ocultan; no se inventa un precio intermedio.</p><p>Cada modelo tiene su página con mínimo, mediana y máximo de sus últimas {STATS_WINDOW} capturas con precio. Solo calificamos el precio del día («por debajo», «habitual» o «por encima») desde {VERDICT_MIN} capturas, comparándolo con la mediana: con inflación, un precio puede subir y seguir siendo habitual.</p></section>
<section><span class="chapter">06 / Descarga</span><h2>Los hechos, abiertos a revisión</h2><p>El CSV identifica modelo, comercio, variante, moneda, precio, stock y momento observado. El JSON añade estado de captura y hash SHA-256 de la evidencia. No distribuimos páginas del comercio, imágenes, cookies ni credenciales.</p><p><a class="text-link" href="{url('/datos/precios/descargar-csv')}">Descargar historial CSV ↓</a> · <a href="{url('/assets/datos/precios-observatorio-publico.json')}">Ver JSON</a></p></section>
<section><span class="chapter">07 / Independencia</span><h2>Quién elige y quién paga</h2><p>Los modelos se eligen por tareas y gamas, para cubrir lo que analizan nuestras guías. Distribución actual de fichas: {split}. Por eso el precio de cada modelo refleja a ese comercio, no un promedio del mercado.</p><p>Algunas guías de TallerLab incluyen enlaces de compra que pueden generar una comisión. Los enlaces de estas páginas de precios van directo a la ficha del comercio, sin parámetros de afiliado, y ningún comercio paga por aparecer ni revisa los datos antes de publicarlos.</p></section>
<section id="citar"><span class="chapter">08 / Licencia</span><h2>Citar y reutilizar</h2><p>Los datos se publican con <a href="{DATA_LICENSE}" rel="license">licencia CC BY 4.0</a>: se pueden copiar, graficar y analizar, también con fines comerciales, citando a TallerLab con un enlace a la página del modelo o a este observatorio.</p><p>Cita sugerida: «Fuente: TallerLab, historial de precios de herramientas en Argentina», con la fecha de la captura y el enlace correspondiente.</p></section></div></section>'''


def hub_body(category, selected, rows, manifest, url, observed, canonical):
    count = len(rows)
    nav = ''.join(f'<a class="{"active" if c==category else ""}" href="{url("/datos/precios/"+c+"/")}">{name} <span>{sum(r["model"]["category"]==c for r in rows):02d}</span></a>' for c, name in CATEGORIES.items())
    failed = sum(r['state'] in ('error', 'vencido') for r in selected)
    title_html = 'Precios de herramientas<br>en Argentina.' if not category else 'Precios de ' + CATEGORIES[category].lower() + '<br>en Argentina.'
    sources = len({r['model']['source'] for r in selected})
    crumbs = [('Inicio', SITE + '/'), ('Precios de herramientas', url(HUB) if category else None)] + ([(CATEGORIES[category], None)] if category else [])
    price_moves, offer_moves = split_movements(movements(selected))
    moves_html = ''
    if price_moves:
        items = ''.join(f'<li data-observed="{esc(r["observation"]["observed_at"])}"><a href="{url(model_path(r["model"]))}">{esc(r["model"]["brand"]+" "+r["model"]["model"])}</a><strong class="{"down" if ch < 0 else "up"}">{ch:+.1f}%</strong><small>{CHANGE_LABELS[classify_change(start, r["observation"])]} · desde {esc(day(start["observed_at"]))} · última captura {esc(short_peso(Decimal(r["observation"]["price_ars"])))}</small></li>' for ch, r, start in price_moves)
        moves_html += f'<section class="moves" aria-labelledby="moves-title"><p class="eyebrow">Ventana de hasta 30 días</p><h2 id="moves-title">Cambios del precio publicado</h2><ul>{items}</ul><p class="reading-note">Comparamos la primera y la última captura disponible de la misma ficha en esa ventana. Las ofertas que empiezan o terminan se muestran aparte.</p></section>'
    if offer_moves:
        items = ''.join(f'<li data-observed="{esc(r["observation"]["observed_at"])}"><a href="{url(model_path(r["model"]))}">{esc(r["model"]["brand"]+" "+r["model"]["model"])}</a><strong class="neutral">{CHANGE_LABELS[classify_change(start, r["observation"])]}</strong><small>{esc(short_peso(Decimal(start["price_ars"])))} el {esc(day(start["observed_at"]))} → {esc(short_peso(Decimal(r["observation"]["price_ars"])))} en la última captura</small></li>' for ch, r, start in offer_moves)
        moves_html += f'<section class="moves offers" aria-labelledby="offers-title"><p class="eyebrow">Ventana de hasta 30 días</p><h2 id="offers-title">Ofertas que empezaron o terminaron</h2><ul>{items}</ul><p class="reading-note">El comercio mostraba un precio tachado. Cuando una oferta termina cambia el importe a pagar, pero eso no demuestra que haya subido el precio de lista.</p></section>'
    capture_days = {day(o['observed_at']) for r in selected for o in r['series']}
    split = ', '.join(f'{sum(r["model"]["source"] == key for r in selected)} de {esc(source["name"])}' for key, source in manifest['sources'].items() if any(r['model']['source'] == key for r in selected))
    guide_link = f'<a href="{SITE}/{category}/">Leer la guía de {CATEGORIES[category].lower()} ↗</a>' if category else f'<a href="{SITE}/">Ver las guías de compra ↗</a>'
    return f'''{breadcrumb_html(crumbs)}<section class="hero"><div><p class="eyebrow">Historial diario · {len(selected)} modelos · {sources} comercio{"s" if sources != 1 else ""}</p><h1>{title_html}</h1><p class="lead">Seguimos todos los días el precio publicado y el stock de cada modelo, y guardamos el historial. Antes de comprar, mirá cómo se movió.</p><a class="button" href="#catalogo">Explorar {len(selected)} modelos <span aria-hidden="true">↘</span></a></div><aside class="capture"><span class="capture-mark" aria-hidden="true">↗</span><p class="eyebrow">Última ejecución</p><strong>{esc(stamp(observed))}</strong><p>{len(manifest['sources'])} comercios · moneda ARS</p><div class="capture-note">Una ficha por modelo.<br> Confirmá el precio final en el comercio.</div></aside></section>
<section class="metrics" aria-label="Cobertura del observatorio"><div><strong>{len(selected):02d}</strong><span>modelos monitoreados</span></div><div><strong id="available-count">{sum(r['state']=='disponible' for r in selected):02d}</strong><span>con precio actual y stock</span></div><div><strong id="unavailable-count">{sum(r['state']=='agotado' for r in selected):02d}</strong><span>agotados en la captura</span></div><div><strong>48 h</strong><span>vigencia máxima del dato</span></div></section>
<p class="reading-note coverage-note">Muestra piloto: {len(capture_days)} días con capturas, no necesariamente consecutivos. Distribución de fichas: {split}. Una oferta por modelo; no representa el mercado argentino. El veredicto requiere {VERDICT_MIN} capturas con precio por ficha.</p>
<nav class="categories" aria-label="Categorías de herramientas"><a class="{'active' if not category else ''}" href="{url(HUB)}">Todas <span>{count}</span></a>{nav}</nav>
{moves_html}
<section id="catalogo" class="catalog"><div class="section-head"><div><p class="eyebrow">El relevamiento</p><h2>{CATEGORIES[category] + ': precio por modelo' if category else 'El taller, modelo por modelo.'}</h2></div><a class="download" download="precios-herramientas.csv" href="{url('/datos/precios/'+((category+'/') if category else '')+'historial.csv')}">Descargar CSV <span aria-hidden="true">↓</span></a></div>
<p class="reading-note">No es un mínimo del mercado: se sigue una ficha por modelo y variante. Sin envío ni promociones calculadas. Tocá un modelo para ver su historial completo. <a href="{url(METHOD)}">Cómo lo medimos ↗</a></p>
<div class="filter-bar" hidden><label>Buscar modelo o marca<input id="search" type="search" placeholder="Ej.: Bosch, HL-120, inverter" autocomplete="off"></label><label>Disponibilidad<select id="stock"><option value="all">Todas las fichas</option><option value="disponible">Con precio actual</option><option value="agotado">Agotados</option><option value="unverified">Sin verificación / vencidos</option></select></label><label>Ordenar<select id="sort"><option value="default">Categoría y modelo</option><option value="asc">Menor precio actual</option><option value="desc">Mayor precio actual</option></select></label></div>
<p class="result-count" id="result-count" aria-live="polite">{len(selected)} modelos</p><p id="freshness-warning" class="warning" {'hidden' if not failed else ''}>Hay fichas sin verificación actual. Se conservan sus observaciones históricas y se excluyen de los precios actuales.</p>
<div class="table-labels" aria-hidden="true"><span>Modelo / variante</span><span>Precio observado</span><span>Disponibilidad / captura</span><span>Variación</span><span>Fuente</span></div><div id="products">{''.join(render_row(r, manifest['sources'], url(model_path(r['model']))) for r in selected)}</div><p id="empty" class="empty" hidden>No hay modelos con esos filtros. Probá otra marca o disponibilidad.</p></section>
<section class="closing"><div><p class="eyebrow">Datos con contexto</p><h2>El precio es una parte<br>de la compra.</h2></div><p>Revisá la variante, el voltaje y los accesorios. Los precios cambian; las fechas y las fuentes te permiten evaluar qué estás mirando.<br>{guide_link} · <a href="{url(METHOD)}">Leer la metodología ↗</a></p></section>
{cite_block(canonical, observed)}'''


def model_body(row, rows, sources, guides, url, canonical, observed):
    m = row['model']; o = row['observation']; source = sources[m['source']]; name = m['brand'] + ' ' + m['model']
    category = CATEGORIES[m['category']]; variant = variant_text(m)
    stats = price_stats(row['series']); kind, text = verdict(row, stats)
    active = row['state'] == 'disponible' and o and o['price_ars']
    price = peso(o['price_ars']) if active else '—'
    crumbs = [('Inicio', SITE + '/'), ('Precios de herramientas', url(HUB)), (category, url('/datos/precios/' + m['category'] + '/')), (m['model'], None)]
    if stats:
        stat_cells = f'<div><strong>{esc(short_peso(stats["min"]))}</strong><span>mínimo observado</span></div><div><strong>{esc(short_peso(stats["median"]))}</strong><span>mediana</span></div><div><strong>{esc(short_peso(stats["max"]))}</strong><span>máximo observado</span></div>'
    else:
        stat_cells = '<div><strong>—</strong><span>mínimo observado</span></div><div><strong>—</strong><span>mediana</span></div><div><strong>—</strong><span>máximo observado</span></div>'
    low = stats['min_offer'] if stats else None
    min_offer_note = f'<p class="reference-note min-offer-note">El mínimo observado fue un precio en oferta: el {esc(day(low["observed_at"]))} la ficha mostraba {esc(peso(low["price_ars"]))} con un tachado de {esc(peso(low["reference_ars"]))}. No es el precio habitual.</p>' if low else ''
    since = day(row['series'][0]['observed_at']) if row['series'] else ''
    history = ''.join(f'<tr><td>{esc(stamp(h["observed_at"]))}</td><td>{esc(peso(h["price_ars"]))}{offer_tag(h)}</td><td>{esc(LABELS.get(h["availability"], h["availability"]))}</td></tr>' for h in reversed(row['series'][-120:])) or '<tr><td colspan="3">Todavía no hay una observación válida.</td></tr>'
    guide_items = ''.join(f'<li><a href="{SITE}{esc(g["url"])}">{esc(g["title"])}</a></li>' for g in guides.get(m['id'], []))
    guide_items += f'<li><a href="{SITE}/{m["category"]}/">Guía de compra de {esc(category.lower())}</a></li>'
    def other_price(r):
        if r['state'] == 'disponible' and r['observation'] and r['observation']['price_ars']:
            return short_peso(Decimal(r['observation']['price_ars']))
        return LABELS[r['state']]
    other_items = ''.join(f'<li><a href="{url(model_path(r["model"]))}">{esc(r["model"]["brand"]+" "+r["model"]["model"])}</a><span>{esc(other_price(r))}</span></li>' for r in rows if r['model']['category'] == m['category'] and r is not row)
    ref = f'<p class="reference-note">Precio tachado por el comercio en la última captura: {esc(peso(o["reference_ars"]))}. No demuestra un descuento histórico.</p>' if o and o.get('reference_ars') else ''
    observed_at = o['observed_at'] if o else ''
    return f'''{breadcrumb_html(crumbs)}<section class="model-hero"><div><p class="eyebrow">Historial de precio · {esc(category)}</p><h1>Precio del {esc(m['brand'])} <span class="nw">{esc(m['model'])}</span><br>en Argentina.</h1><p class="lead">{(esc(variant) + '. ') if variant else ''}Seguimos esta ficha de {esc(source['name'])} todos los días{(' desde el ' + esc(since)) if since else ''} y guardamos cada captura: precio publicado, stock y fecha.</p></div><aside class="model-current" data-state="{row['state']}" data-observed="{esc(observed_at)}"><p class="eyebrow">Último precio observado</p><strong class="current-price">{price}</strong><span class="badge {row['state']}">{LABELS[row['state']]}</span><small>{esc(stamp(observed_at))} · {esc(source['name'])}</small><a class="button" href="{esc(m['url'])}" target="_blank" rel="nofollow noopener noreferrer">Ver la ficha en el comercio <span aria-hidden="true">↗</span></a></aside></section>
<section class="verdict {kind}" aria-labelledby="verdict-title"><h2 id="verdict-title">¿Es buen precio hoy?</h2><p>{text}</p>{ref}</section>
<section class="metrics" aria-label="Resumen del historial">{stat_cells}<div><strong>{stats['n'] if stats else 0:02d}</strong><span>capturas con precio</span></div></section>{min_offer_note}
<section class="model-chart" aria-labelledby="chart-title"><h2 id="chart-title">Evolución del precio del {esc(m['model'])}</h2>{chart_svg(row['series'], 'Evolución del precio publicado del ' + name)}</section>
<section class="model-history" aria-labelledby="history-title"><div class="section-head"><h2 id="history-title">Todas las capturas</h2><a class="download" download="precios-{m['category']}.csv" href="{url('/datos/precios/' + m['category'] + '/historial.csv')}">Descargar CSV <span aria-hidden="true">↓</span></a></div><div class="history-scroll"><table><caption>Capturas de {esc(name)}{(' (' + esc(variant) + ')') if variant else ''} en {esc(source['name'])}</caption><thead><tr><th>Captura</th><th>Precio observado (ARS)</th><th>Stock observado</th></tr></thead><tbody>{history}</tbody></table></div><p class="reading-note">Los importes históricos no son ofertas vigentes. Sin envío, cuotas ni descuentos por medio de pago. <a href="{url(METHOD)}">Cómo lo medimos ↗</a></p></section>
<section class="model-context"><div><h2>Antes de comprar el <span class="nw">{esc(m['model'])}</span></h2><ul><li>{('Confirmá que la variante sea esta: <strong>' + esc(variant) + '</strong>. ') if variant else 'Confirmá en la ficha el voltaje y qué incluye la caja. '}Un kit, otra batería u otro voltaje cambian el precio.</li><li>El comercio confirma stock, envío y precio final; acá no sumamos costos de envío.</li><li>Si el precio está por encima de lo habitual, mirá la guía para comparar alternativas.</li></ul></div><div><h2>Guías relacionadas</h2><ul class="link-list">{guide_items}</ul></div></section>
<section class="related-models" aria-labelledby="related-title"><h2 id="related-title">Otros {esc(category.lower())} que seguimos</h2><ul>{other_items}</ul><p><a href="{url('/datos/precios/' + m['category'] + '/')}">Ver la tabla de {esc(category.lower())} ↗</a></p></section>
{cite_block(canonical, observed_at or observed)}'''


def build_site(history_path, output, base_path='', site_url=SITE, manifest_path=MANIFEST, now=None, standalone=True, canonical_url=None):
    """Genera el observatorio. Si canonical_url difiere del hosting (p. ej. GitHub Pages), las páginas
    se marcan noindex y su canonical apunta al dominio principal: la autoridad queda en tallerlab.com.ar."""
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    base = '/'+base_path.strip('/') if base_path.strip('/') else ''
    if any(c in base for c in ('..', '?', '#', '<', '"')): raise ValueError('Base path inválido')
    url = lambda path: esc(base+path, quote=True)
    hosted = site_url.rstrip('/') + base
    canon_base = canonical_url.rstrip('/') if canonical_url else hosted
    mirror = canon_base != hosted
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    history = read_history(history_path); rows = snapshot(history, manifest, now)
    guides = json.loads(GUIDES.read_text(encoding='utf-8')) if GUIDES.is_file() else {}
    paths = [model_path(m) for m in manifest['models']]
    if len(set(paths)) != len(paths): raise ValueError('Dos modelos comparten la misma URL')
    assets = output/'assets'; assets.mkdir(exist_ok=True)
    for name in ('observatorio-gratuito.css', 'observatorio-gratuito.js', 'favicon.svg'):
        shutil.copy2(ROOT/'assets'/name, assets/name)
    fonts = assets/'fonts'; fonts.mkdir(exist_ok=True)
    for name in ('plus-jakarta-sans-latin-v1.woff2', 'jetbrains-mono-latin-v1.woff2', 'plusjakartasans-OFL.txt', 'jetbrainsmono-OFL.txt'):
        shutil.copy2(ROOT/'assets'/'fonts'/name, fonts/name)
    public_models = [dict({k:m[k] for k in ('id','brand','model','variant','category','source','url')}, page=canon_base+model_path(m)) for m in manifest['models']]
    public = dict(history, models=public_models, sources=manifest['sources'], freshness_hours=FRESH_HOURS, license=DATA_LICENSE, attribution='TallerLab, ' + canon_base + HUB)
    atomic_json(assets/'datos'/'precios-observatorio-publico.json', public)
    observed = history.get('run', {}).get('finished_at', '')
    modified = parse_time(observed).astimezone(ART).date().isoformat() if observed else None
    count = len(rows); fresh = sum(r['state']=='disponible' for r in rows)
    failed = sum(r['state']=='error' for r in rows)
    stale = sum(r['state']=='vencido' for r in rows)
    csv_headers = ['modelo_id','marca','modelo','variante','categoria','comercio','url_fuente','moneda','precio_observado_ars','stock_observado','capturado_en_utc','dia_argentina','hash_evidencia','precio_tachado_ars','tipo_cambio']
    for category in (None, *CATEGORIES):
        target = output/'datos'/'precios'/(category or '')/'descargar-csv'
        target.parent.mkdir(parents=True, exist_ok=True)
        selected = {r['model']['id']:r['model'] for r in rows if not category or r['model']['category']==category}
        previous_prices = {}
        with target.open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f); writer.writerow(csv_headers)
            for o in sorted(history['observations'], key=lambda item: item['observed_at']):
                m = selected.get(o['model_id'])
                if not m: continue
                previous = previous_prices.get(m['id'])
                kind = classify_change(previous, o) if previous and o['availability'] == 'disponible' and o['price_ars'] else ''
                if o['availability'] == 'disponible' and o['price_ars']:
                    previous_prices[m['id']] = o
                values = [m['id'],m['brand'],m['model'],m['variant'],m['category'],manifest['sources'][m['source']]['name'],m['url'],'ARS',o['price_ars'] or '',o['availability'],o['observed_at'],o['day_art'],o['evidence_sha256'],o.get('reference_ars') or '',kind]
                writer.writerow(["'"+str(v) if str(v).startswith(('=', '+', '-', '@')) else v for v in values])
        shutil.copy2(target, target.with_name('historial.csv'))
    date_label = day(observed)
    source_name = lambda m: manifest['sources'][m['source']]['name']
    pages = []
    for category in (None, *CATEGORIES):
        path = HUB if not category else '/datos/precios/'+category+'/'
        selected = [r for r in rows if not category or r['model']['category']==category]
        ids = {r['model']['id'] for r in selected}
        obs = [o for o in history['observations'] if o['model_id'] in ids]
        canonical = canon_base + path
        csv_url = canon_base + '/datos/precios/' + (category + '/' if category else '') + 'historial.csv'
        if category:
            brands = sorted({r['model']['brand'] for r in selected})
            name = f'Precios de {CATEGORIES[category].lower()} en Argentina'
            title = f'{name}: historial de {len(selected)} modelos | TallerLab'
            desc = f'Seguimos a diario {len(selected)} {CATEGORIES[category].lower()} ({", ".join(brands)}): precio publicado, stock e historial en comercios argentinos.' + (f' Última captura: {date_label}.' if date_label else '')
            crumbs = [('Inicio', SITE + '/'), ('Precios de herramientas', canon_base + HUB), (CATEGORIES[category], canonical)]
        else:
            name = 'Precios de herramientas en Argentina'
            title = f'{name}: historial diario | TallerLab'
            desc = f'Precio publicado, stock e historial diario de {count} herramientas en {len(manifest["sources"])} comercios de Argentina.' + (f' Última captura: {date_label}.' if date_label else '') + ' Datos abiertos en CSV.'
            crumbs = [('Inicio', SITE + '/'), ('Precios de herramientas', canonical)]
        schema = [dataset_schema(name, desc, canonical, csv_url, obs, modified), breadcrumb_schema(crumbs)]
        pages.append((path, page(title, desc, canonical, schema, mirror, url, hub_body(category, selected, rows, manifest, url, observed, canonical), published_at=observed)))
    counts = {}
    for m in manifest['models']: counts[m['source']] = counts.get(m['source'], 0) + 1
    method_canonical = canon_base + METHOD
    method_crumbs = [('Inicio', SITE + '/'), ('Precios de herramientas', canon_base + HUB), ('Metodología', method_canonical)]
    pages.append((METHOD, page('Cómo medimos los precios de herramientas | TallerLab', 'Metodología del historial de precios de TallerLab: qué fichas seguimos, cómo validamos precio y stock, vigencia de 48 horas, independencia y licencia de los datos.', method_canonical, [breadcrumb_schema(method_crumbs)], mirror, url, methodology(manifest, url, counts), published_at=observed)))
    for row in rows:
        m = row['model']; o = row['observation']; path = model_path(m); canonical = canon_base + path
        name = m['brand'] + ' ' + m['model']
        if row['state'] == 'disponible' and o and o['price_ars']:
            desc = f'{name}: {short_peso(Decimal(o["price_ars"]))} el {day(o["observed_at"])} en {source_name(m)}. Historial diario de precio y stock, con mínimo y máximo observados.'
        else:
            desc = f'{name}: {LABELS[row["state"]].lower()} en la última captura. Historial diario de precio y stock en {source_name(m)}, con mínimo y máximo observados.'
        crumbs = [('Inicio', SITE + '/'), ('Precios de herramientas', canon_base + HUB), (CATEGORIES[m['category']], canon_base + '/datos/precios/' + m['category'] + '/'), (m['model'], canonical)]
        schema = [dataset_schema('Historial de precios del ' + name, f'Precio publicado y stock observados a diario del {name}' + (f' ({variant_text(m)})' if variant_text(m) else '') + f' en {source_name(m)}, Argentina.', canonical, canon_base + '/datos/precios/' + m['category'] + '/historial.csv', row['series'], modified), breadcrumb_schema(crumbs)]
        pages.append((path, page(f'{name}: precio hoy e historial | TallerLab', desc, canonical, schema, mirror, url, model_body(row, rows, manifest['sources'], guides, url, canonical, observed), published_at=observed)))
    routes = [p for p, _ in pages]
    for path, html in pages:
        target = output/path.strip('/')/'index.html'; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(html, encoding='utf-8')
        if path == HUB and standalone:
            (output/'index.html').write_text(html, encoding='utf-8')
    summary = {'monitored':count,'observations':len(history['observations']),'available':fresh,'unverified':failed,'stale':stale,'run':history.get('run',{}),'routes':routes}
    atomic_json(output / 'assets' / 'datos' / 'observatorio-publicacion.json',
                {'schema_version': 1, 'routes': routes, 'run': summary['run']})
    if not standalone:
        return summary
    (output/'.nojekyll').write_text('', encoding='utf-8')
    if mirror:
        (output/'robots.txt').write_text('User-agent: *\nAllow: /\n', encoding='utf-8')
        if (output/'sitemap.xml').exists(): (output/'sitemap.xml').unlink()
    else:
        (output/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+hosted+'/sitemap.xml\n', encoding='utf-8')
        lastmod = f'<lastmod>{modified}</lastmod>' if modified else ''
        sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(hosted+p)+'</loc>'+lastmod+'</url>' for p in routes)+'</urlset>'
        (output/'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (output/'404.html').write_text(f'<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="robots" content="noindex"><title>Página no encontrada | TallerLab</title><link rel="stylesheet" href="{url("/assets/observatorio-gratuito.css")}"><main class="methodology"><h1>Página no encontrada.</h1><a href="{url(HUB)}">Volver a los precios</a></main></html>', encoding='utf-8')
    atomic_json(output/'estado.json', summary)
    return summary


def static_observatory_file(path):
    """Solo rutas del observatorio; no reemplaza la portada ni las otras funciones."""
    if path == HUB or path == METHOD or path in ('/datos/precios/'+c+'/' for c in CATEGORIES) or MODEL_RE.match(path):
        target = ROOT/'public'/path.strip('/')/'index.html'
    elif path in ('/datos/precios/'+(c+'/' if c else '')+'descargar-csv' for c in (None,*CATEGORIES)) or path in ('/datos/precios/'+(c+'/' if c else '')+'historial.csv' for c in (None,*CATEGORIES)):
        target = ROOT/'public'/path.lstrip('/')
    else: return None
    if target.is_file():
        return target
    # En Vercel, public/ no entra en la función: el build deja una copia aquí.
    copy = ROOT/'observatorio_publicado'/target.relative_to(ROOT/'public')
    return copy if copy.is_file() else None


def expected_observatory_paths():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    return [HUB] + ['/datos/precios/'+c+'/' for c in CATEGORIES] + [METHOD] + [model_path(m) for m in manifest['models']]


def verify_publication(output, summary):
    """Detiene el build si falta cualquier página, descarga o dataset esperado."""
    output = Path(output)
    expected = expected_observatory_paths()
    if set(summary['routes']) != set(expected):
        raise RuntimeError('El observatorio no generó todas las rutas previstas')
    artifacts = [output / path.strip('/') / 'index.html' for path in expected]
    for category in (None, *CATEGORIES):
        folder = output / 'datos' / 'precios'
        if category:
            folder /= category
        artifacts.extend(folder / name for name in ('descargar-csv', 'historial.csv'))
    artifacts.extend(output / 'assets' / 'datos' / name for name in
                     ('precios-observatorio-publico.json', 'observatorio-publicacion.json'))
    missing = [str(path.relative_to(output)) for path in artifacts
               if not path.is_file() or not path.stat().st_size]
    if missing:
        raise RuntimeError('Faltan artefactos del observatorio: ' + ', '.join(missing))
    publication = json.loads(artifacts[-1].read_text(encoding='utf-8'))
    if publication.get('schema_version') != 1 or publication.get('routes') != summary['routes']:
        raise RuntimeError('El manifiesto no corresponde al observatorio generado')


def published_observatory_paths():
    """El manifiesto solo prueba el build; el sitemap exige archivos servibles."""
    return [p for p in expected_observatory_paths() if static_observatory_file(p)]
