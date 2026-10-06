"""Reference candidates and the verified, versioned documentary ledger."""
import json
import threading
from pathlib import Path
from dataclasses import replace
from compatibilidad.models import Product,Platform,Evidence,ChangeLogEntry

reference=json.loads((Path(__file__).parent/'data/reference_catalog.json').read_text(encoding='utf8'))
CATALOG_PRODUCTS=[Product(**p) for p in reference['products']]
PLATFORMS=[Platform(**p) for p in reference['platforms']]
EVIDENCES=[]
CHANGELOG=[]
PRODUCTS_BY_ID={}
PRODUCTS_BY_SLUG={}
PRODUCTS_BY_MPN={}
PLATFORMS_BY_ID={}
EVIDENCES_BY_ID={}

_STATE_LOCK = threading.RLock()
def catalog_read_locked(func):
    from functools import wraps
    @wraps(func)
    def wrapped(*args, **kwargs):
        with _STATE_LOCK:
            return func(*args, **kwargs)
    return wrapped
RELATIONS = []
CURRENT_METADATA = {'version': '2-baseline', 'engine_version': '2'}
_RAW_STATE = None
_LEGACY_PRODUCTS = list(CATALOG_PRODUCTS)
_LEGACY_PLATFORMS = list(PLATFORMS)

def baseline_state():
    products = []
    for product in _LEGACY_PRODUCTS:
        products.append(replace(product, status='pendiente', gtin_ean=None,
            capacity_ah=None, voltage_nominal=None, voltage_max=None, required_packs=1, is_argentina_catalog=False,
            specs={}, market_availability_notes='Registro pendiente de verificación documental para Argentina.',
            evidence_identity_id=None, evidence_platform_id=None,
            notes='No se confirma compatibilidad hasta verificar identidad y pertenencia.').to_dict())
    platforms = [p.to_dict() for p in _LEGACY_PLATFORMS]
    if 'gamma-21v' not in {p['id'] for p in platforms}:
        platforms.append(replace(_LEGACY_PLATFORMS[4], id='gamma-21v', name='Gamma 21V: referencia pendiente',
            brand='Gamma', system_name='Pendiente de verificar', compatibility_rule='Sin regla de compatibilidad verificada.',
            conditions_summary='No extrapolar compatibilidad con Multi Energy.', exceptions=[]).to_dict())
    state = {'metadata': dict(CURRENT_METADATA), 'products': products,
             'platforms': platforms,
             'evidences': [], 'relations': [], 'sources': [], 'candidates': [], 'changelog': []}
    seed = Path(__file__).parent / 'data' / 'verified_seed.json'
    if seed.exists():
        verified = json.loads(seed.read_text(encoding='utf8'))
        known = {p['id']: p for p in products}
        known.update({p['id']: p for p in verified['products']})
        state.update(verified)
        state['products'] = list(known.values())
    for platform in state['platforms']:
        platform.update(description='Plataforma de referencia; consultar las relaciones por modelo.',
            compatibility_rule='Solo se confirman las relaciones documentadas entre modelos exactos.',
            conditions_summary='Un registro pendiente no acredita pertenencia ni compatibilidad.',exceptions=[])
    return state

def validate_state(state):
    from compatibilidad.sources import proof_valid
    products = [Product(**p) for p in state['products']]
    evidences = {e.id: e for e in (Evidence(**e) for e in state['evidences'])}
    platforms = {p['id'] for p in state['platforms']}
    if len({p.id for p in products}) != len(products) or len({p.slug for p in products}) != len(products):
        raise ValueError('Identidades duplicadas en la versión')
    by_id = {p.id:p for p in products}
    for p in products:
        if p.product_type not in ('bateria', 'cargador', 'herramienta', 'adaptador') or p.status not in ('publicado','pendiente','conflicto'):
            raise ValueError('Tipo o estado inválido: ' + p.id)
        if p.platform_id not in platforms:
            raise ValueError('Plataforma inexistente: ' + p.id)
        if p.status == 'publicado':
            for field, claim in ((p.evidence_identity_id, 'identidad'), (p.evidence_platform_id, 'pertenencia')):
                e = evidences.get(field)
                if not e or not proof_valid(e, p.id, check_age=False) or claim not in e.claim_types:
                    raise ValueError('Producto sin evidencia de ' + claim + ': ' + p.id)
            from compatibilidad.sources import PROFILES, documented_facts
            profile = next((v for v in PROFILES if v['product_id']==p.id), None)
            if not profile:
                raise ValueError('Modelo sin perfil documental: ' + p.id)
            facts = documented_facts(profile, p)
            for key, value in facts.items():
                if getattr(p,key) != value:
                    raise ValueError('Especificación sin respaldo: '+p.id+' '+key)
                if evidences[p.evidence_identity_id].product_facts.get(key)!=value:
                    raise ValueError('Ledger de especificaciones incompleto: '+p.id+' '+key)
    for rel in state['relations']:
        if rel['source_product_id'] not in by_id or rel['target_product_id'] not in by_id:
            raise ValueError('Relación con producto inexistente')
        if rel['verdict'] not in ('Compatible documentado','Compatible bajo condiciones','Incompatible documentado') or rel['relation_type'] not in ('bateria_hacia_herramienta','cargador_hacia_bateria') or rel['required_packs_count'] not in (1,2):
            raise ValueError('Semántica de relación inválida')
        proofs = [evidences.get(eid) for eid in rel['evidence_ids']]
        if not proofs or any(not e or not proof_valid(e, check_age=False) for e in proofs) or not any('compatibilidad' in e.claim_types for e in proofs):
            raise ValueError('Relación sin regla documental verificada')
    return state

def apply_state(state):
    global _RAW_STATE
    validate_state(state)
    from compatibilidad.sources import proof_valid
    state=json.loads(json.dumps(state))
    raw_state=json.loads(json.dumps(state))
    evidences={e['id']:Evidence(**e) for e in state['evidences']}
    for product in state['products']:
        if product['status']=='publicado' and not all(proof_valid(evidences[eid],product['id'])
                for eid in (product['evidence_identity_id'],product['evidence_platform_id'])):
            product['status']='pendiente'
    active={p['id'] for p in state['products'] if p['status']=='publicado'}
    state['relations']=[r for r in state['relations'] if {r['source_product_id'],r['target_product_id']} <= active]
    with _STATE_LOCK:
        _RAW_STATE=raw_state
        CATALOG_PRODUCTS[:] = [Product(**p) for p in state['products']]
        PLATFORMS[:] = [Platform(**p) for p in state['platforms']]
        EVIDENCES[:] = [Evidence(**e) for e in state['evidences']]
        RELATIONS[:] = state['relations']
        CURRENT_METADATA.clear(); CURRENT_METADATA.update(state['metadata'])
        for container, records, key in ((PRODUCTS_BY_ID,CATALOG_PRODUCTS,'id'), (PRODUCTS_BY_SLUG,CATALOG_PRODUCTS,'slug'),
                                       (PLATFORMS_BY_ID,PLATFORMS,'id'),(EVIDENCES_BY_ID,EVIDENCES,'id')):
            container.clear(); container.update({getattr(p,key):p for p in records})
        PRODUCTS_BY_MPN.clear()
        for p in CATALOG_PRODUCTS:
            PRODUCTS_BY_MPN.setdefault(p.mpn.upper(), []).append(p)
        CHANGELOG[:] = [ChangeLogEntry(**c) for c in state.get('changelog', [])]
        import sys
        search = sys.modules.get('compatibilidad.search')
        if search and hasattr(search, 'GLOBAL_SEARCH_INDEX'):
            search.GLOBAL_SEARCH_INDEX.products = CATALOG_PRODUCTS
            search.GLOBAL_SEARCH_INDEX._build_index()

def refresh_published_state():
    from compatibilidad.storage import StateStore
    # Storage failure leaves the verified baseline/current state usable, never
    # invokes a write during a public read. Maintenance reports the actual error.
    try:
        state = StateStore().current()
        if state and state['metadata']['version'] != CURRENT_METADATA['version']:
            apply_state(state)
    except Exception:
        import logging
        logging.getLogger(__name__).warning('No se pudo leer la versión persistida de compatibilidad')
    # Re-evaluate age even on warm workers and when persistence is unavailable.
    from compatibilidad.sources import proof_valid
    with _STATE_LOCK:
        if _RAW_STATE and any(p.status=='publicado' and not all(proof_valid(EVIDENCES_BY_ID[eid],p.id)
                for eid in (p.evidence_identity_id,p.evidence_platform_id)) for p in CATALOG_PRODUCTS):
            apply_state(_RAW_STATE)

apply_state(baseline_state())
