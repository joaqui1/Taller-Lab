"""Acquisition and assertions for explicitly configured manufacturer records.

Assertions describe documentary facts, not guesses from voltage or brand.
Unknown products require an additional reviewed profile before automatic publication.
"""
import hashlib
import gzip
import io
import re
import unicodedata
import json
from pathlib import Path
from functools import lru_cache
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler

OFFICIAL_DOMAINS = {
    'bosch-professional.com', 'einhell.com.ar', 'einhell.com',
    'dewalt.com.ar', 'dewalt.com', 'makita.com.ar', 'makitatools.com',
    'gammaherramientas.com.ar',
    'media.bosch-pt.com', 'media.th.bosch-pt.com',
}

def official_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or '').lower().rstrip('.')
        return (parsed.scheme == 'https' and not parsed.username and not parsed.password
                and parsed.port in (None, 443)
                and any(host == d or host.endswith('.' + d) for d in OFFICIAL_DOMAINS))
    except (ValueError, TypeError):
        return False

@lru_cache(maxsize=128)
def normalize(value):
    value = unicodedata.normalize('NFKD', str(value))
    value = ''.join(x for x in value if not unicodedata.combining(x))
    return re.sub(r'\s+', ' ', value).strip().casefold()

def contains(text, assertion):
    return normalize(assertion) in normalize(text)

class OfficialRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not official_url(newurl):
            raise ValueError('Redirección fuera de los dominios oficiales')
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch_source(url):
    if not official_url(url):
        raise ValueError('URL oficial inválida')
    opener = build_opener(OfficialRedirect())
    with opener.open(Request(url, headers={'User-Agent': 'TallerLab-Evidence-Monitor/2.0'}), timeout=12) as response:
        if not official_url(response.geturl()):
            raise ValueError('URL final no autorizada')
        body = response.read(8 * 1024 * 1024 + 1)
        if len(body) > 8 * 1024 * 1024:
            raise ValueError('Documento supera el límite; requiere extractor específico')
        if response.status != 200:
            raise ValueError('Respuesta HTTP no exitosa')
        if response.headers.get('Content-Encoding', '').lower() == 'gzip' or body[:2] == b'\x1f\x8b':
            with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed:
                body = compressed.read(8 * 1024 * 1024 + 1)
            if len(body) > 8 * 1024 * 1024:
                raise ValueError('Documento descomprimido supera el límite')
        if body.startswith(b'%PDF'):
            from pypdf import PdfReader
            text=' '.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(body)).pages)
        else:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(body, 'html.parser')
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()
            text = ' '.join(soup.stripped_strings)
        if not text:
            raise ValueError('Documento sin texto extraíble')
        return {'url': response.geturl(), 'http_status': response.status,
                'hash': hashlib.sha256(body).hexdigest(), 'text': text,
                'fetched_at': datetime.now(timezone.utc).isoformat()}

# A changed or missing assertion suspends the associated record. Broadening
# coverage means adding a reviewed profile, never promoting a fuzzy match.
PROFILES = [
    {'product_id': 'BAT-BOSCH-PROCORE-4AH', 'assertions': ['ProCORE18V 4.0Ah', '1.600.A01.6GB', 'Compatible con todas las herramientas y los cargadores del Professional 18V System de Bosch'],
     'excerpt': 'Compatible con todas las herramientas y los cargadores del Professional 18V System de Bosch', 'platform': 'bosch-professional-18v'},
    {'product_id': 'TOOL-BOSCH-GWS-18V-10', 'assertions': ['GWS 18V-10', '0.601.9J4.0E0', '18 V'],
     'excerpt': 'GWS 18V-10', 'platform': 'bosch-professional-18v'},
    {'product_id': 'TOOL-BOSCH-GWS-18V-10PSC', 'assertions': ['GWS 18V-10 PSC', '0.601.9G3.F0B', 'con todas las baterías y cargadores Bosch Professional 18V'],
     'excerpt': 'con todas las baterías y cargadores Bosch Professional 18V', 'platform': 'bosch-professional-18v'},
    {'product_id': 'BAT-GAMMA-G12490AR', 'assertions': ['g12490ar', 'Capacidad: 2000 mAh', 'sistema Multienergy'],
     'excerpt': 'Capacidad: 2000 mAh', 'platform': 'gamma-multi-energy'},
    {'product_id': 'BAT-GAMMA-G12491AR', 'assertions': ['g12491ar', 'Capacidad: 4000 mAh', 'sistema Multienergy', 'G12493AR', 'G12492AR'],
     'excerpt': 'Capacidad: 4000 mAh', 'platform': 'gamma-multi-energy'},
    {'product_id': 'CHG-GAMMA-G12492AR', 'assertions': ['g12492ar', 'Cargador', 'Multienergy', '220 VCA 50Hz'],
     'excerpt': 'Alimentación: 220 VCA 50Hz', 'platform': 'gamma-multi-energy'},
    {'product_id': 'CHG-GAMMA-G12493AR', 'assertions': ['g12493ar', 'Cargador', 'multi energy', '40 minutos', 'G12490AR', 'G12491AR'],
     'excerpt': 'Tiempo de carga: 40 minutos', 'platform': 'gamma-multi-energy'},
]
PROFILE_NAMES={
    'BAT-BOSCH-PROCORE-4AH':'ProCORE18V 4.0Ah',
    'TOOL-BOSCH-GWS-18V-10':'GWS 18V-10',
    'TOOL-BOSCH-GWS-18V-10PSC':'GWS 18V-10 PSC',
    'BAT-GAMMA-G12490AR':'G12490AR Multi Energy 2.0 Ah',
    'BAT-GAMMA-G12491AR':'G12491AR Multi Energy 4.0 Ah',
    'CHG-GAMMA-G12492AR':'G12492AR Cargador Multi Energy',
    'CHG-GAMMA-G12493AR':'G12493AR Cargador Multi Energy',
}

profile_file=Path(__file__).parent/'data/document_profiles.json'
if profile_file.exists():
    PROFILES=json.loads(profile_file.read_text(encoding='utf8'))
    PROFILE_NAMES={p['product_id']:p['model_name'] for p in PROFILES}

def technical_text(text, url=''):
    """Ignore peripheral menus and rotating recommendations, retain technical text."""
    if '/producto/' in url or 'Dónde Comprar' in text:
        start=text.find('Buscar ×')
        end=text.find('Líneas de productos',max(0,start))
    elif 'Número de pedido' in text:
        start=max(0,text.find('Número de pedido')-80)
        end=text.find('¿Necesita algún repuesto?',start)
    else:
        return normalize(text)
    return normalize(text[max(0,start):end if end>=0 else None])

def documented_facts(profile, product):
    if 'facts' in profile:
        return profile['facts']
    # Transitional profiles for the original verified cut.
    gamma=product.brand=='Gamma'
    capacity=4.0 if product.id in ('BAT-BOSCH-PROCORE-4AH','BAT-GAMMA-G12491AR') else 2.0 if product.id=='BAT-GAMMA-G12490AR' else None
    return {'mpn':product.mpn,'product_type':product.product_type,'platform_id':profile['platform'],
        'capacity_ah':capacity,'voltage_nominal':None if gamma else '18 V',
        'specs':{'tiempo_carga_G12490AR':'40 minutos según fabricante'} if product.id=='CHG-GAMMA-G12493AR' else {}}

def proof_valid(evidence, product_id=None, check_age=True):
    try:
        reviewed=datetime.fromisoformat(evidence.date_reviewed).date()
        age=(datetime.now(timezone.utc).date()-reviewed).days
        if age<0 or (check_age and age>30):
            return False
    except (ValueError,TypeError):
        return False
    return (evidence.status == 'verificada' and official_url(evidence.official_url)
            and bool(evidence.text_assertions) and bool(evidence.content_text)
            and len(evidence.evidence_hash) == 64
            and bool(re.fullmatch(r'[0-9a-f]{64}', evidence.evidence_hash))
            and evidence.evidence_hash == hashlib.sha256(evidence.content_text.encode('utf8')).hexdigest()
            and (product_id is None or product_id in evidence.product_ids)
            and all(contains(evidence.content_text, value) for value in evidence.text_assertions)
            and contains(evidence.content_text, evidence.excerpt))
