"""Public aggregate health and external supervision of documentary maintenance."""
import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from compatibilidad import catalog
from compatibilidad.storage import StateStore

ALERT_AFTER_EVIDENCE_DAYS = 20
MIN_EXPECTED_PUBLISHED_PRODUCTS = 18
MIN_EXPECTED_DOCUMENTED_RELATIONS = 40
MONITOR_STATE_PATH = Path(__file__).resolve().parents[1] / '.compatibilidad-monitor' / 'state.json'
ARGENTINA = ZoneInfo('America/Argentina/Buenos_Aires')


def _configured_minimum(environment_name, default):
    try:
        return max(0, int(os.environ.get(environment_name, default)))
    except (TypeError, ValueError):
        return default


def _date_from_iso(value):
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _today_argentina():
    return datetime.now(ARGENTINA).date()


def capture_health():
    catalog.refresh_published_state()
    ready = False
    try:
        state = StateStore().current()
        ready = bool(state)
    except Exception:
        state = None
    metadata = (state or {}).get('metadata', catalog.CURRENT_METADATA)
    try:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(metadata['last_checked_at'])).total_seconds()
        fresh = 0 <= age <= 26 * 3600
    except (KeyError, ValueError, TypeError):
        age = None
        fresh = False

    sources = (state or {}).get('sources', [])
    failed_sources = [
        {
            'source_id': source.get('source_id') or source.get('id') or 'fuente-desconocida',
            'status': source.get('status') or 'desconocida',
            'checked_at': source.get('last_fetched_at'),
        }
        for source in sources if source.get('status') != 'accesible'
    ]
    products = [
        {'id': product.id, 'brand': product.brand, 'model_name': product.model_name,
         'mpn': product.mpn, 'status': product.status}
        for product in catalog.CATALOG_PRODUCTS
    ]
    relation_ids = sorted(relation.get('id', '') for relation in catalog.RELATIONS if relation.get('id'))
    evidence_dates = [
        reviewed for reviewed in (_date_from_iso(evidence.date_reviewed) for evidence in catalog.EVIDENCES)
        if reviewed is not None
    ]
    oldest_evidence_date = min(evidence_dates) if evidence_dates else None
    max_evidence_age_days = (datetime.now(timezone.utc).date() - oldest_evidence_date).days if oldest_evidence_date else None

    verified = sum(product.status == 'publicado' for product in catalog.CATALOG_PRODUCTS)
    ok = ready and fresh and bool(sources) and not failed_sources and verified > 0
    return {
        'status': 'ok' if ok else 'degradado', 'version': metadata.get('version'),
        'storage_ready': ready, 'fresh': fresh, 'last_checked_at': metadata.get('last_checked_at'),
        'sources_checked': len(sources), 'source_failures': len(failed_sources),
        'failed_sources': failed_sources, 'verified_products': verified,
        'pending_products': len(catalog.CATALOG_PRODUCTS) - verified,
        'documented_relations': len(relation_ids), 'products': products,
        'relation_ids': relation_ids,
        'oldest_evidence_date': oldest_evidence_date.isoformat() if oldest_evidence_date else None,
        'max_evidence_age_days': max_evidence_age_days,
    }


def make_monitor_snapshot(health, observed_at=None):
    """Keep only the public fields needed for the next comparison."""
    observed = observed_at or datetime.now(ARGENTINA).isoformat()
    products = health.get('products') if isinstance(health.get('products'), list) else None
    source_failures = health.get('failed_sources') if isinstance(health.get('failed_sources'), list) else []
    source_failure_count = health.get('source_failures')
    if not isinstance(source_failure_count, int):
        source_failure_count = len(source_failures)
    return {
        'observed_at': observed,
        'status': health.get('status', 'desconocido'),
        'storage_ready': health.get('storage_ready'),
        'fresh': health.get('fresh'),
        'products': products,
        'published_products': health.get('verified_products'),
        'relation_ids': health.get('relation_ids') if isinstance(health.get('relation_ids'), list) else None,
        'documented_relations': health.get('documented_relations'),
        'source_failures': source_failures,
        'source_failure_count': source_failure_count,
        'max_evidence_age_days': health.get('max_evidence_age_days'),
        'oldest_evidence_date': health.get('oldest_evidence_date'),
        'last_checked_at': health.get('last_checked_at'),
    }


def _event_date(snapshot, as_of=None):
    if as_of is not None:
        value = as_of
    else:
        value = snapshot.get('observed_at')
    try:
        dt = datetime.fromisoformat(value) if isinstance(value, str) else value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ARGENTINA)
        return dt.astimezone(ARGENTINA).date().strftime('%d/%m/%Y')
    except (TypeError, ValueError):
        return _today_argentina().strftime('%d/%m/%Y')


def compare_monitor_states(previous, current, as_of=None):
    """Return incidents that started since the previous successful monitor run."""
    if not isinstance(current, dict):
        return []
    if not isinstance(previous, dict):
        previous = None
    events = []
    event_date = _event_date(current, as_of)

    prev_products = {item.get('id'): item for item in (previous or {}).get('products') or [] if item.get('id')}
    current_products = {item.get('id'): item for item in current.get('products') or [] if item.get('id')}
    prev_published = (previous or {}).get('published_products')
    now_published = current.get('published_products')
    if isinstance(prev_published, int) and isinstance(now_published, int) and now_published < prev_published:
        events.append({'type': 'products_decreased', 'before': prev_published, 'current': now_published, 'date': event_date})
    minimum_published = _configured_minimum(
        'COMPATIBILITY_EXPECTED_PUBLISHED_PRODUCTS', MIN_EXPECTED_PUBLISHED_PRODUCTS)
    if isinstance(now_published, int) and now_published < minimum_published:
        events.append({'type': 'products_below_baseline', 'minimum': minimum_published,
                       'current': now_published, 'date': event_date})

    if previous and prev_products and current.get('products') is not None:
        failed_by_id = {item.get('source_id'): item for item in current.get('source_failures') or []}
        for product_id, old_product in prev_products.items():
            if old_product.get('status') != 'publicado':
                continue
            new_product = current_products.get(product_id)
            if new_product and new_product.get('status') == 'publicado':
                continue
            label = ' '.join(filter(None, (old_product.get('brand'), old_product.get('model_name')))) or product_id
            source = failed_by_id.get(product_id)
            if source:
                reason = f"falló la fuente oficial asociada ({source.get('status', 'inaccesible')})"
            elif new_product and new_product.get('status') == 'conflicto':
                reason = 'la comprobación detectó un cambio documental y quedó en conflicto, pendiente de revisión'
            elif new_product:
                reason = f"el mantenimiento cambió su estado de publicado a {new_product.get('status', 'pendiente')}"
            else:
                reason = 'ya no figura publicado en el estado vigente'
            events.append({
                'type': 'product_suspended', 'product_id': product_id, 'product_name': label,
                'mpn': old_product.get('mpn'), 'reason': reason, 'date': event_date,
            })

    prev_relations = (previous or {}).get('documented_relations')
    now_relations = current.get('documented_relations')
    old_relation_ids = set((previous or {}).get('relation_ids') or [])
    new_relation_ids = set(current.get('relation_ids') or [])
    removed_relations = sorted(old_relation_ids - new_relation_ids)
    if isinstance(prev_relations, int) and isinstance(now_relations, int) and now_relations < prev_relations:
        events.append({'type': 'relations_decreased', 'before': prev_relations, 'current': now_relations,
                       'relation_ids': removed_relations, 'date': event_date})
    minimum_relations = _configured_minimum(
        'COMPATIBILITY_EXPECTED_DOCUMENTED_RELATIONS', MIN_EXPECTED_DOCUMENTED_RELATIONS)
    if isinstance(now_relations, int) and now_relations < minimum_relations:
        events.append({'type': 'relations_below_baseline', 'minimum': minimum_relations,
                       'current': now_relations, 'date': event_date})
    if removed_relations and not (isinstance(prev_relations, int) and isinstance(now_relations, int) and now_relations < prev_relations):
        events.append({'type': 'relations_removed', 'relation_ids': removed_relations, 'date': event_date})

    previous_failures = {
        item.get('source_id') for item in (previous or {}).get('source_failures') or [] if item.get('source_id')
    }
    new_failed_sources = []
    for failure in current.get('source_failures') or []:
        source_id = failure.get('source_id')
        if not source_id or source_id in previous_failures:
            continue
        new_failed_sources.append(source_id)
        product = current_products.get(source_id) or prev_products.get(source_id) or {}
        label = ' '.join(filter(None, (product.get('brand'), product.get('model_name')))) or source_id
        events.append({
            'type': 'source_failed', 'source_id': source_id, 'source_name': label,
            'reason': f"la fuente oficial figura como {failure.get('status', 'inaccesible')}",
            'date': event_date,
        })
    previous_source_count = (previous or {}).get('source_failure_count')
    current_source_count = current.get('source_failure_count')
    if not isinstance(previous_source_count, int):
        previous_source_count = len(previous_failures)
    if not isinstance(current_source_count, int):
        current_source_count = len(current.get('source_failures') or [])
    if current_source_count > previous_source_count and not new_failed_sources:
        events.append({
            'type': 'source_failure_count', 'count': current_source_count,
            'reason': 'el endpoint informó fuentes fallidas sin detallar sus identidades', 'date': event_date,
        })

    current_age = current.get('max_evidence_age_days')
    previous_age = (previous or {}).get('max_evidence_age_days')
    crossed_threshold = isinstance(current_age, (int, float)) and current_age > ALERT_AFTER_EVIDENCE_DAYS and (
        previous is None or not isinstance(previous_age, (int, float)) or previous_age <= ALERT_AFTER_EVIDENCE_DAYS
        or current.get('oldest_evidence_date') != (previous or {}).get('oldest_evidence_date')
    )
    if crossed_threshold:
        events.append({
            'type': 'evidence_age', 'age_days': int(current_age),
            'oldest_evidence_date': current.get('oldest_evidence_date'), 'date': event_date,
        })

    if current.get('status') != 'ok' and (previous is None or previous.get('status') == 'ok'):
        details = []
        if current.get('storage_ready') is False:
            details.append('almacenamiento persistente no disponible')
        if current.get('fresh') is False:
            details.append('sin comprobación reciente')
        if current.get('source_failures'):
            failures = current['source_failures']
            count = len(failures) if isinstance(failures, list) else failures
            details.append(f"{count} fuente(s) fallida(s)")
        events.append({
            'type': 'health_degraded', 'reason': ', '.join(details) or 'el endpoint informó estado degradado',
            'date': event_date,
        })
    return events


def format_alert(events, health=None):
    """Build a concise Spanish notice with the product, cause and date."""
    lines = ['TallerLab · alerta de compatibilidad']
    for event in events:
        when = event.get('date') or _today_argentina().strftime('%d/%m/%Y')
        kind = event.get('type')
        if kind == 'product_suspended':
            product = event.get('product_name') or event.get('product_id') or 'Producto sin identificar'
            mpn = f" (MPN {event['mpn']})" if event.get('mpn') else ''
            lines.append(f"- Producto suspendido: {product}{mpn}. Motivo: {event.get('reason', 'estado cambiado')}. Fecha: {when}.")
        elif kind == 'products_decreased':
            lines.append(f"- Productos publicados: {event['before']} → {event['current']}. Fecha: {when}.")
        elif kind == 'products_below_baseline':
            lines.append(f"- Productos publicados por debajo del mínimo esperado: {event['current']} (mínimo {event['minimum']}). Fecha: {when}.")
        elif kind == 'relations_decreased':
            removed = f" Retiradas: {', '.join(event.get('relation_ids') or [])}." if event.get('relation_ids') else ''
            lines.append(f"- Relaciones documentadas: {event['before']} → {event['current']}.{removed} Fecha: {when}.")
        elif kind == 'relations_below_baseline':
            lines.append(f"- Relaciones documentadas por debajo del mínimo esperado: {event['current']} (mínimo {event['minimum']}). Fecha: {when}.")
        elif kind == 'relations_removed':
            lines.append(f"- Relaciones retiradas: {', '.join(event['relation_ids'])}. Fecha: {when}.")
        elif kind == 'source_failed':
            lines.append(f"- Fuente fallida: {event.get('source_name', event.get('source_id'))}. Motivo: {event.get('reason')}. Fecha: {when}.")
        elif kind == 'source_failure_count':
            lines.append(f"- Fuentes fallidas: {event['count']}. Motivo: {event.get('reason')}. Fecha: {when}.")
        elif kind == 'evidence_age':
            reviewed = event.get('oldest_evidence_date') or 'fecha desconocida'
            lines.append(f"- Evidencia más antigua: {event['age_days']} días (revisada el {reviewed}). Superó el umbral de 20 días. Fecha del aviso: {when}.")
        elif kind == 'health_degraded':
            lines.append(f"- Estado operativo degradado. Motivo: {event.get('reason')}. Fecha: {when}.")
        elif kind == 'endpoint_unreachable':
            lines.append(f"- No respondió /api/compatibilidad/estado. Motivo: {event.get('reason')}. Fecha: {when}.")
    if health is not None:
        lines.append(f"Estado actual: {health.get('status', 'desconocido')}; última comprobación: {health.get('last_checked_at') or 'sin dato'}.")
    return '\n'.join(lines)


def notify_owner(message):
    """Reuse Comunidad's configured Resend/Telegram delivery channels."""
    from comunidad import avisos

    delivered = []
    configured = False
    if avisos.telegram_ready():
        configured = True
        if avisos.send_telegram(message):
            delivered.append('telegram')
    editor_email = os.environ.get('COMUNIDAD_AVISO_EDITOR_EMAIL', '').strip()
    if editor_email and avisos.email_ready():
        configured = True
        if avisos.send_email(editor_email, 'TallerLab: alerta de compatibilidad', message):
            delivered.append('email')
    if not configured:
        raise RuntimeError('Configurar un canal existente de avisos de Comunidad en los secretos del workflow')
    if not delivered:
        raise RuntimeError('No se pudo entregar la alerta por los canales configurados')
    return delivered


def load_monitor_state(path=None):
    state_path = Path(path or os.environ.get('COMPATIBILITY_MONITOR_STATE_PATH') or MONITOR_STATE_PATH)
    try:
        return json.loads(state_path.read_text(encoding='utf8'))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return None


def save_monitor_state(snapshot, path=None):
    state_path = Path(path or os.environ.get('COMPATIBILITY_MONITOR_STATE_PATH') or MONITOR_STATE_PATH)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix(state_path.suffix + '.tmp')
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, sort_keys=True), encoding='utf8')
    temporary.replace(state_path)


def run_monitor(site_url=None, state_path=None):
    from urllib.error import HTTPError
    from urllib.request import urlopen

    url = (site_url or os.environ.get('SITE_URL', 'https://www.tallerlab.com.ar')).rstrip('/') + '/api/compatibilidad/estado'
    try:
        try:
            with urlopen(url, timeout=25) as response:
                health = json.load(response)
        except HTTPError as exc:
            try:
                health = json.loads(exc.read().decode('utf8'))
            except (UnicodeDecodeError, json.JSONDecodeError):
                health = {'status': 'degradado', 'http_status': exc.code}
        if not isinstance(health, dict):
            raise ValueError('El endpoint devolvió un estado JSON inválido')
    except Exception as exc:
        health = {'status': 'degradado', 'monitor_error': type(exc).__name__}
        event = {'type': 'endpoint_unreachable', 'reason': type(exc).__name__, 'date': _today_argentina().strftime('%d/%m/%Y')}
        health['alert_events'] = [event]
        health['notice_channels'] = notify_owner(format_alert([event]))
        return health

    previous = load_monitor_state(state_path)
    current = make_monitor_snapshot(health)
    events = compare_monitor_states(previous, current)
    if events:
        health['notice_channels'] = notify_owner(format_alert(events, health))
        health['alert_events'] = events
    save_monitor_state(current, state_path)
    return health


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['health', 'monitor'])
    args = parser.parse_args()
    health = capture_health() if args.command == 'health' else run_monitor()
    print(json.dumps(health, ensure_ascii=False))
    raise SystemExit(0 if health.get('status') == 'ok' else 1)


if __name__ == '__main__':
    main()
