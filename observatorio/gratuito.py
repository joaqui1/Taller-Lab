"""Captura y publicación estática: sin base remota, API paga ni cron de Vercel.

Solo captura las URLs del manifiesto, respeta robots y no elude bloqueos.
El historial público contiene hechos observados y hashes, nunca HTML ni secretos.
"""
import argparse
import hashlib
import json
import os
import re
import tempfile
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:  # generar páginas (build de Vercel) no necesita las dependencias de captura
    requests = BeautifulSoup = None

from observatorio.extractors.base import BaseExtractor

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'observatorio' / 'piloto_gratuito.json'
DEFAULT_HISTORY = ROOT / 'assets' / 'datos' / 'precios-observatorio.json'
USER_AGENT = 'TallerLabObservatorio/1.0 (+https://www.tallerlab.com.ar/datos/precios/metodologia/)'
CATEGORIES = {'compresores': 'Compresores', 'hidrolavadoras': 'Hidrolavadoras',
              'generadores': 'Generadores', 'soldadoras': 'Soldadoras',
              'taladros': 'Taladros', 'amoladoras': 'Amoladoras', 'sierras': 'Sierras'}


def normalized(value):
    value = unicodedata.normalize('NFKD', str(value))
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in value if not unicodedata.combining(c)).lower())


def same_url(left, right):
    return str(left).rstrip('/') == str(right).rstrip('/')


def products_from_html(soup):
    result = []
    def walk(value):
        if isinstance(value, list):
            for v in value: walk(v)
        elif isinstance(value, dict):
            types = value.get('@type', [])
            if types == 'Product' or isinstance(types, list) and 'Product' in types:
                result.append(value)
            for k in ('@graph', 'mainEntity'):
                if k in value: walk(value[k])
    for script in soup.find_all('script', type='application/ld+json'):
        try: walk(json.loads(script.string or '', parse_float=Decimal))
        except (ValueError, TypeError): continue
    return result


def product_url(product):
    page = product.get('mainEntityOfPage') or {}
    offers = product.get('offers') or {}
    return product.get('@id') or product.get('url') or (page.get('@id') if isinstance(page, dict) else page) or (offers.get('url') if isinstance(offers, dict) else '')


def money(value):
    parsed = BaseExtractor.parse_money(value)
    if parsed is None or not parsed.is_finite() or not Decimal('5000') <= parsed <= Decimal('50000000'):
        raise ValueError('Precio ausente, ambiguo o fuera de rango')
    return parsed


def extract_public_product(html, model):
    """Identidad exacta, URL propia y precio principal; nunca productos recomendados."""
    soup = BeautifulSoup(html, 'html.parser')
    candidates = [p for p in products_from_html(soup) if same_url(product_url(p), model['url'])]
    if len(candidates) != 1:
        raise ValueError('No hay un único producto estructurado con la URL configurada')
    product = candidates[0]
    if str(product.get('sku', '')) != str(model['schema_sku']):
        raise ValueError('SKU de la oferta cambió')
    if str(product.get('mpn', '')) != str(model.get('schema_mpn') or ''):
        raise ValueError('Referencia de producto cambió')
    if normalized(product.get('name', '')) != normalized(model['schema_name']):
        raise ValueError('Título o variante cambió; requiere revisión')
    brand = product.get('brand') or {}
    brand = brand.get('name', '') if isinstance(brand, dict) else brand
    if normalized(brand) != normalized(model['schema_brand']):
        raise ValueError('Marca contradictoria')
    # Las propiedades que definen variantes tampoco pueden cambiar silenciosamente.
    props = {p.get('name'): p.get('value') for p in product.get('additionalProperty', []) if isinstance(p, dict)}
    for key, expected in model.get('variant_properties', {}).items():
        if str(props.get(key)) != str(expected):
            raise ValueError('Variante cambió: ' + key)
    offer = product.get('offers')
    if not isinstance(offer, dict):
        raise ValueError('Oferta ausente o múltiple')
    if offer.get('@type') == 'AggregateOffer':
        children = offer.get('offers', [])
        if len(children) != 1 or not isinstance(children[0], dict):
            raise ValueError('Agregado ambiguo de ofertas')
        offer = children[0]
    if offer.get('@type') != 'Offer':
        raise ValueError('No hay oferta individual')
    if offer.get('url') and not same_url(offer['url'], model['url']):
        raise ValueError('Oferta de otra URL')
    if str(offer.get('priceCurrency', '')).upper() != 'ARS':
        raise ValueError('Moneda ausente o distinta de ARS')
    condition = str(offer.get('itemCondition') or product.get('itemCondition') or '')
    if condition and condition.rstrip('/').split('/')[-1] != 'NewCondition':
        raise ValueError('Condición distinta de nuevo')
    stock = str(offer.get('availability', '')).rstrip('/').split('/')[-1]
    availability = {'InStock': 'disponible', 'OutOfStock': 'agotado', 'Discontinued': 'agotado',
                    'SoldOut': 'agotado'}.get(stock, 'desconocido')
    inventory = offer.get('inventoryLevel')
    if isinstance(inventory, dict) and inventory.get('value') is not None:
        if Decimal(str(inventory['value'])) == 0: availability = 'agotado'
    selector = {'megastore': '#price_display', 'dgm': '#precio-mostrado',
                'bulonfer': '.vtex-product-price-1-x-sellingPriceValue--precio-product'}[model['source']]
    visible = soup.select(selector)
    if len(visible) != 1:
        raise ValueError('Precio principal no identificable')
    # VTEX divide los miles en varios spans: conservar el separador, sin añadir espacios.
    raw_price = BaseExtractor.parse_money(offer.get('price'))
    raw_visible = BaseExtractor.parse_money(visible[0].get_text('', strip=True))
    # Algunas fichas agotadas informan cero. Es ausencia de precio, nunca una oferta gratis.
    no_price = availability == 'agotado' and raw_price == 0 and raw_visible in (None, 0)
    price = None if no_price else money(offer.get('price'))
    visible_price = None if no_price else money(visible[0].get_text('', strip=True))
    # DGM muestra pesos enteros redondeados; JSON-LD conserva los centavos.
    rounded_dgm = (not no_price and model['source'] == 'dgm'
                   and ',' not in visible[0].get_text('', strip=True)
                   and price.quantize(Decimal('1'), rounding=ROUND_HALF_UP) == visible_price)
    if not no_price and not rounded_dgm and abs(price - visible_price) > Decimal('0.01'):
        raise ValueError('Precio estructurado y principal visible contradictorios')
    reference = None
    ref_selector = {'megastore': '#compare_price_display', 'dgm': '#precio-tachado-mostrado',
                    'bulonfer': '.vtex-product-price-1-x-listPriceValue--tachado-product'}[model['source']]
    ref = soup.select_one(ref_selector)
    if ref:
        raw_reference = BaseExtractor.parse_money(ref.get_text('', strip=True))
        if price is not None and raw_reference and raw_reference.is_finite() and raw_reference > price:
            reference = format(raw_reference, '.2f')
    return {'price_ars': format(price, '.2f') if price is not None else None, 'reference_ars': reference,
            'availability': availability, 'currency': 'ARS',
            'evidence_sha256': hashlib.sha256(html.encode('utf-8')).hexdigest(),
            'extractor_version': 'gratuito-1.0'}


def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); temp = Path(f.name)
    os.replace(temp, path)


def read_history(path):
    if not Path(path).exists():
        return {'version': 1, 'observations': [], 'latest_attempts': {}, 'run': {}}
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('version') != 1 or not isinstance(data.get('observations'), list):
        raise ValueError('Historial inválido; no se sobrescribe')
    return data


def get_allowed_robots(session, origin):
    response = session.get(origin + '/robots.txt', timeout=25, allow_redirects=False)
    if response.status_code != 200:
        raise ValueError('No se pudo comprobar robots.txt: HTTP ' + str(response.status_code))
    parser = RobotFileParser(); parser.parse(response.text.splitlines())
    return parser


def fetch_page(session, model):
    """Sin redirects, sin cookies de login, sin reintentos de bloqueos o CAPTCHA."""
    with session.get(model['url'], timeout=25, allow_redirects=False, stream=True) as response:
        if response.status_code != 200:
            raise ValueError('HTTP ' + str(response.status_code))
        if 'text/html' not in response.headers.get('Content-Type', ''):
            raise ValueError('La fuente no devuelve HTML')
        data = bytearray()
        for chunk in response.iter_content(65536):
            data.extend(chunk)
            if len(data) > 6_000_000: raise ValueError('Página demasiado grande')
        return data.decode('utf-8', errors='replace')


def collect(history_path=DEFAULT_HISTORY, manifest_path=MANIFEST):
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    models = manifest['models']
    data = read_history(history_path)
    start = datetime.now(timezone.utc).isoformat(); today = datetime.now(timezone.utc).astimezone(__import__('zoneinfo').ZoneInfo('America/Argentina/Buenos_Aires')).date().isoformat()
    existing = {(o['model_id'], o['day_art']) for o in data['observations']}
    if not models: raise ValueError('No hay modelos configurados')
    data['run'] = {'started_at': start, 'models': len(models), 'captured': 0,
                   'failed': 0, 'already_captured': 0, 'status': 'running'}
    sessions = {}; robots = {}; checked = {}; succeeded = failed = skipped = 0
    blocked_domains = set()
    try:
        for model in models:
            if (model['id'], today) in existing:
                skipped += 1; continue
            parts = urlparse(model['url']); origin = parts.scheme+'://'+parts.netloc
            observed = datetime.now(timezone.utc).isoformat()
            try:
                if parts.scheme != 'https' or parts.netloc != manifest['sources'][model['source']]['domain']:
                    raise ValueError('URL fuera de la fuente configurada')
                if origin in blocked_domains: raise ValueError('Dominio pausado por bloqueo en esta ejecución')
                if origin not in sessions:
                    session = requests.Session(); session.headers['User-Agent'] = USER_AGENT
                    sessions[origin] = session; robots[origin] = get_allowed_robots(session, origin)
                    checked[origin] = time.monotonic()
                if not robots[origin].can_fetch(USER_AGENT, model['url']):
                    raise ValueError('robots.txt no permite esta URL')
                interval = max(3, robots[origin].crawl_delay(USER_AGENT) or 0)
                wait = interval - (time.monotonic() - checked.get(origin, 0))
                if wait > 0: time.sleep(wait)
                checked[origin] = time.monotonic()
                html = fetch_page(sessions[origin], model)
                result = extract_public_product(html, model)
                previous = [o for o in data['observations'] if o['model_id'] == model['id'] and o['availability'] == 'disponible'][-7:]
                # Una revisión humana aceptada inicia una nueva referencia de precios.
                reviewed = [i for i, o in enumerate(previous) if o.get('jump_reviewed')]
                if reviewed: previous = previous[reviewed[-1]:]
                if previous and result['price_ars'] is not None:
                    import statistics
                    median = statistics.median(Decimal(o['price_ars']) for o in previous)
                    if abs(Decimal(result['price_ars']) - median) / median >= Decimal('0.35'):
                        approval = model.get('price_review') or {}
                        if approval.get('day_art') != today or str(approval.get('price_ars')) != result['price_ars']:
                            raise ValueError('Variación de 35% o más: dato retenido para revisión')
                        result['jump_reviewed'] = True
                observed = datetime.now(timezone.utc).isoformat()
                observation = dict(result, model_id=model['id'], observed_at=observed, day_art=today)
                data['observations'].append(observation); existing.add((model['id'], today))
                data['latest_attempts'][model['id']] = {'observed_at': observed, 'status': 'ok'}
                succeeded += 1
                print(model['id'], result['price_ars'], result['availability'], flush=True)
            except (requests.RequestException, ValueError, KeyError, TypeError, ArithmeticError) as exc:
                message = str(exc)
                if any(code in message for code in ('HTTP 403', 'HTTP 429', 'HTTP 503')):
                    blocked_domains.add(origin)
                # No publicar excepciones de red: podrían contener detalles del entorno.
                reason = message if isinstance(exc, ValueError) else 'No se pudo consultar o validar la fuente'
                data['latest_attempts'][model['id']] = {'observed_at': observed, 'status': 'error', 'reason': reason}
                failed += 1; print(model['id'], 'ERROR', reason, flush=True)
            data['run'] = {'started_at': start, 'finished_at': datetime.now(timezone.utc).isoformat(),
                           'models': len(models), 'captured': succeeded, 'failed': failed, 'already_captured': skipped,
                           'status': 'running'}
            atomic_json(history_path, data)
    finally:
        for session in sessions.values(): session.close()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
    data['observations'] = [o for o in data['observations'] if o['observed_at'] >= cutoff]
    data['run'].update(status='degraded' if failed else 'ok', already_captured=skipped,
                       captured=succeeded, failed=failed,
                       finished_at=datetime.now(timezone.utc).isoformat())
    atomic_json(history_path, data)
    return data['run']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', type=Path, default=DEFAULT_HISTORY)
    parser.add_argument('--output', type=Path, default=ROOT / 'public')
    parser.add_argument('--base-path', default='')
    parser.add_argument('--site-url', default='https://www.tallerlab.com.ar')
    parser.add_argument('--canonical-url', default=None, help='Dominio principal para canonical; si difiere del hosting, las páginas quedan noindex.')
    parser.add_argument('--skip-collection', action='store_true')
    args = parser.parse_args()
    if not args.skip_collection: collect(args.history)
    from observatorio.estatico import build_site
    summary = build_site(args.history, args.output, args.base_path, args.site_url, canonical_url=args.canonical_url)
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    # Publicar las páginas degradadas para no mantener precios viejos como actuales.
    # El workflow informa el estado después de publicar, sin ocultar un fallo de captura.


if __name__ == '__main__': main()
