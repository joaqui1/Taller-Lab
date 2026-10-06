"""Editorial placement of existing referrals; commercial offers never grant a verdict."""
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from compatibilidad import catalog
from compatibilidad.rules import evaluate_compatibility
from sierras_comerciales import OFFERS

# Only exact offers with an explicit SKU and review belong here. No fuzzy match.
EXACT_OFFERS = json.loads((Path(__file__).parent/'data'/'commercial_offers.json').read_text(encoding='utf-8'))['exact_offers']
KIT_CODE = '1600A015TD'
KIT_REFERENCE = 'BAT-BOSCH-GBA-4AH'


def exact_offer(product):
    offer = EXACT_OFFERS.get(product.id)
    if not offer or product.status != 'publicado':
        return None
    if offer.get('mpn') != product.mpn or offer.get('brand') != product.brand:
        return None
    try:
        reviewed = datetime.fromisoformat(offer['reviewed_at'])
        age = (datetime.now(timezone.utc) - reviewed).total_seconds()
        if not 0 <= age <= 30 * 86400:
            return None
    except (KeyError, ValueError, TypeError):
        return None
    if not offer.get('identity_confirmed') or not offer.get('url', '').startswith('https://meli.la/'):
        return None
    return offer


def render_exact_offer(product):
    offer = exact_offer(product)
    if not offer:
        return ''
    return f'<section class="compat-buy"><span class="compat-buy-label">Oferta del modelo identificado</span><h2>¿Buscás {escape(product.brand)} {escape(product.model_name)}?</h2><p>Código documentado: <code>{escape(product.mpn)}</code>. {escape(offer.get("contents_note", "Confirmá variante y contenido con el vendedor."))}</p><a class="compat-buy-cta" href="{escape(offer["url"],quote=True)}" target="_blank" rel="sponsored nofollow noopener noreferrer" data-compat-event="clic_comercial">Consultar precio y disponibilidad de {escape(product.mpn)} ↗</a>{disclosure()}</section>'


def disclosure():
    return '<p class="compat-buy-disclosure">Precio, stock, vendedor y contenido se consultan en Mercado Libre.</p>'


def kit_is_relevant(product):
    battery = catalog.PRODUCTS_BY_ID.get(KIT_REFERENCE)
    if not battery or battery.status != 'publicado' or product.status != 'publicado':
        return False
    return product.id == battery.id or (product.product_type == 'herramienta' and evaluate_compatibility(battery, product).is_compatible)


def render_related_kit(product=None, pair=None, platform_id=None):
    if pair:
        evaluation = evaluate_compatibility(*pair)
        if not evaluation.is_compatible or evaluation.source_product.id != KIT_REFERENCE or evaluation.target_product.product_type != 'herramienta':
            return ''
    elif product:
        if not kit_is_relevant(product):
            return ''
    elif platform_id == 'bosch-professional-18v':
        battery = catalog.PRODUCTS_BY_ID.get(KIT_REFERENCE)
        if not battery or battery.status != 'publicado':
            return ''
    else:
        return ''
    title, token, note = OFFERS['BOSCH1600A015TD']
    return f'<section class="compat-buy compat-buy-related"><span class="compat-buy-label">Kit complementario · componentes por confirmar</span><h2>¿Necesitás batería y cargador en una misma compra?</h2><p>La publicación recibida identifica <strong>{escape(title)}</strong> y anuncia dos baterías de 4 Ah y cargador. Es un kit distinto de los códigos individuales de esta base.</p><p><strong>Antes de comprar:</strong> pedí los códigos de las baterías y del cargador, comprobá la tensión de entrada y consultá esos códigos en el buscador. La documentación de los modelos individuales no confirma el contenido ni la variante de este kit.</p><a class="compat-buy-cta" href="https://meli.la/{escape(token,quote=True)}" target="_blank" rel="sponsored nofollow noopener noreferrer" data-compat-event="clic_comercial">Consultar precio y contenido del kit Bosch {KIT_CODE} ↗</a>{disclosure()}</section>'


def render_product_commercial(product):
    return render_exact_offer(product) or render_related_kit(product=product)


def render_pair_commercial(source, target):
    if not evaluate_compatibility(source, target).is_compatible:
        return ''
    exact = render_exact_offer(source) + render_exact_offer(target)
    return exact or render_related_kit(pair=(source, target))
