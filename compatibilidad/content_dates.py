"""Track publication changes separately from automated source checks."""
import json

FALLBACK_CONTENT_CHANGED_AT = '2026-10-04'
_PRODUCT_SPEC_FIELDS = (
    'capacity_ah', 'voltage_nominal', 'voltage_max', 'specs', 'gtin_ean',
    'required_packs',
)


def _canonical(value):
    def normalize_numbers(item):
        if isinstance(item, bool):
            return item
        if isinstance(item, (int, float)):
            if isinstance(item, float) and item.is_integer():
                return int(item)
            return item
        if isinstance(item, dict):
            return {key: normalize_numbers(child) for key, child in item.items()}
        if isinstance(item, (list, tuple)):
            return [normalize_numbers(child) for child in item]
        return item

    return json.dumps(normalize_numbers(value), ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _published_evidence(evidence):
    if not evidence or evidence.get('status') != 'verificada':
        return None
    return {
        'excerpt': evidence.get('excerpt', ''),
        'approved_source_hash': evidence.get('approved_source_hash') or evidence.get('evidence_hash', ''),
    }


def product_content_signature(product, evidences):
    published = product.get('status') == 'publicado'
    evidence = _published_evidence(evidences.get(product.get('evidence_identity_id')))
    specs = {field: product.get(field) for field in _PRODUCT_SPEC_FIELDS} if published else None
    editorial = None
    try:
        from compatibilidad.editorial import EDITORIAL_FICHAS
        ficha = EDITORIAL_FICHAS.get(product.get('id'))
        if isinstance(ficha, dict) and ficha.get('publicado') is True:
            editorial = ficha
    except (ImportError, AttributeError):
        editorial = None
    return _canonical({'published': published, 'specifications': specs, 'source': evidence,
                       'editorial': editorial})


def relation_content_signature(relation, evidences):
    sources = []
    for evidence_id in relation.get('evidence_ids', []):
        evidence = _published_evidence(evidences.get(evidence_id))
        if evidence is not None:
            sources.append(evidence)
    return _canonical({
        'verdict': relation.get('verdict'),
        'conditions': relation.get('conditions', []),
        'exclusions': relation.get('exclusions', []),
        'required_packs_count': relation.get('required_packs_count'),
        'sources': sources,
    })


def stamp_content_changed_at(state, previous_state, changed_at):
    """Stamp only records whose published content differs from the active version."""
    previous_state = previous_state or {}
    previous_products = {p['id']: p for p in previous_state.get('products', [])}
    previous_relations = {r['id']: r for r in previous_state.get('relations', [])}
    current_evidences = {e['id']: e for e in state.get('evidences', [])}
    previous_evidences = {e['id']: e for e in previous_state.get('evidences', [])}

    for product in state.get('products', []):
        previous = previous_products.get(product['id'])
        old_date = (previous or {}).get('content_changed_at') or product.get('content_changed_at')
        if previous and product_content_signature(product, current_evidences) == product_content_signature(previous, previous_evidences):
            product['content_changed_at'] = old_date or FALLBACK_CONTENT_CHANGED_AT
        elif previous or product.get('status') == 'publicado':
            product['content_changed_at'] = changed_at
        else:
            product['content_changed_at'] = old_date or FALLBACK_CONTENT_CHANGED_AT

    for relation in state.get('relations', []):
        previous = previous_relations.get(relation['id'])
        old_date = (previous or {}).get('content_changed_at') or relation.get('content_changed_at')
        if previous and relation_content_signature(relation, current_evidences) == relation_content_signature(previous, previous_evidences):
            relation['content_changed_at'] = old_date or FALLBACK_CONTENT_CHANGED_AT
        else:
            relation['content_changed_at'] = changed_at
    return state
