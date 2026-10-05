"""Capturas diarias idempotentes, con concesión atómica y presupuesto de duración."""
import email.utils
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import requests
from observatorio import config
from observatorio.catalog import PRODUCTS_BY_ID
from observatorio.db import get_db, adapt_query, execute_stmt, query_all, query_one
from observatorio.extractors.base import ExtractionResult
from observatorio.extractors.feed_importer import FeedImporter
from observatorio.extractors.fixtures import FIXTURE_BULONERA_HTML_VALID, FIXTURE_EASY_HTML_WITH_INSTALLMENTS, FIXTURE_FEED_CATALOG_JSON
from observatorio.extractors.store_adapters import EasyStoreAdapter, VtexStoreAdapter
from observatorio.extractors.structured_data import StructuredDataExtractor
from observatorio.validation import validate_observation

_domain_last_request = {}
class CollectorLockError(Exception):
    pass

def _now():
    return datetime.now(timezone.utc).isoformat()

def get_active_run():
    threshold = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    return query_one("SELECT * FROM collector_runs WHERE status='running' AND started_at > ? ORDER BY started_at DESC LIMIT 1", (threshold,))

def _acquire_run_lock(run_id, now):
    expiry = (datetime.fromisoformat(now) + timedelta(minutes=15)).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        q = lambda sql, params=(): cur.execute(adapt_query(sql, config.STORAGE_MODE), params)
        q("INSERT INTO collector_lease(id,owner,expires_at) VALUES (1,NULL,?) ON CONFLICT(id) DO NOTHING", (now,))
        q("UPDATE collector_lease SET owner=?,expires_at=? WHERE id=1 AND (owner IS NULL OR expires_at<=?)", (run_id, expiry, now))
        if cur.rowcount != 1:
            return False
        threshold = (datetime.fromisoformat(now)-timedelta(minutes=15)).isoformat()
        q("UPDATE collector_runs SET status='failed',finished_at=?,error_summary='Concesión vencida' WHERE status='running' AND started_at<=?", (now,threshold))
        q("INSERT INTO collector_runs(id,started_at,status) VALUES (?,?,'running')",(run_id,now))
    return True

def _throttle_request(domain, per_minute=20):
    pause = max(3.0, 60.0 / max(1, per_minute))
    remaining = pause - (time.monotonic() - _domain_last_request.get(domain, 0))
    if remaining > 0:
        time.sleep(remaining)
    _domain_last_request[domain] = time.monotonic()

def _parse_retry_after(value):
    try:
        return max(0, int(value))
    except (ValueError, TypeError):
        try:
            dt = email.utils.parsedate_to_datetime(value)
            if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
            return max(0, int((dt-datetime.now(timezone.utc)).total_seconds())+1)
        except (ValueError, TypeError, OverflowError):
            return 5

def _select_extractor(method, source_id=None):
    mapping = {'feed_import':FeedImporter, 'easy_store_adapter':EasyStoreAdapter,
               'vtex_store_adapter':VtexStoreAdapter, 'structured_data_jsonld':StructuredDataExtractor}
    if method not in mapping:
        raise ValueError('Método de extracción no configurado correctamente')
    return mapping[method]()

def run_collection_batch(batch_size=None, use_fixtures=False, offer_ids_subset=None, capture_slot=None):
    if use_fixtures and config.STORAGE_MODE == 'postgres':
        raise ValueError('Las muestras solo están permitidas en SQLite de desarrollo.')
    limit = max(1, min(50, int(batch_size or config.MAX_BATCH_SIZE)))
    start = _now(); run_id = str(uuid.uuid4())
    slot = capture_slot or datetime.now(config.TZ_BUENOS_AIRES).date().isoformat()
    if get_active_run() or not _acquire_run_lock(run_id, start):
        raise CollectorLockError('Otra captura tiene una concesión activa.')
    began = time.monotonic()
    successes = failures = anomalies = processed = 0
    details = []
    fatal = None
    prefix = ('synthetic' if use_fixtures else 'real') + ':' + slot + ':'
    try:
        params = []
        subset = ''
        if offer_ids_subset:
            subset = ' AND off.id IN ('+','.join('?' for _ in offer_ids_subset)+')'
            params.extend(offer_ids_subset)
        eligibility = '' if use_fixtures else ' AND src.capture_allowed=1 AND src.terms_verified_date IS NOT NULL'
        if not use_fixtures:
            eligibility += ' AND (off.next_attempt_at IS NULL OR off.next_attempt_at<=?)'
            params.insert(0,start)
        offers = query_all("""SELECT off.*, src.domain,src.max_requests_per_minute,src.redistribution_allowed
            FROM offers off JOIN sources src ON off.source_id=src.id
            WHERE off.enabled=1 AND src.status='habilitada'"""+eligibility+subset+"""
            AND NOT EXISTS (SELECT 1 FROM observations o WHERE o.capture_key=? || off.id)
            ORDER BY off.last_checked_at ASC NULLS FIRST,off.id LIMIT ?""", (*params,prefix,limit))
        for off in offers:
            if time.monotonic()-began >= config.RUN_BUDGET_SECONDS: break
            offer_id = off['id']; observed = _now()
            extraction = ExtractionResult(False,None,error_message='No se pudo extraer la oferta.')
            target = PRODUCTS_BY_ID.get(off['product_id'])
            try:
                extractor = _select_extractor(off['extraction_method'],off['source_id'])
                raw = ''
                if use_fixtures:
                    raw = FIXTURE_FEED_CATALOG_JSON if off['extraction_method']=='feed_import' else FIXTURE_EASY_HTML_WITH_INSTALLMENTS if off['extraction_method']=='easy_store_adapter' else FIXTURE_BULONERA_HTML_VALID
                else:
                    domain = urlparse(off['direct_url']).netloc
                    if domain != off['domain']: raise ValueError('URL fuera del dominio autorizado')
                    for attempt in range(config.MAX_RETRIES+1):
                        # Reservar el timeout antes de iniciar otro intento.
                        remaining = config.RUN_BUDGET_SECONDS-(time.monotonic()-began)
                        if remaining < config.REQUEST_TIMEOUT_SECONDS+4: raise TimeoutError('Oferta diferida por presupuesto de ejecución')
                        _throttle_request(domain,off['max_requests_per_minute'])
                        try:
                            response=requests.get(off['direct_url'],headers={'User-Agent':config.USER_AGENT},timeout=config.REQUEST_TIMEOUT_SECONDS,allow_redirects=False)
                        except requests.RequestException:
                            if attempt == config.MAX_RETRIES: raise
                            continue
                        if response.status_code==200:
                            raw=response.text; break
                        if response.status_code not in (429,503) or attempt==config.MAX_RETRIES:
                            raise ValueError('HTTP '+str(response.status_code))
                        delay=_parse_retry_after(response.headers.get('Retry-After','5'))
                        if delay+config.REQUEST_TIMEOUT_SECONDS+4 > config.RUN_BUDGET_SECONDS-(time.monotonic()-began):
                            execute_stmt('UPDATE offers SET next_attempt_at=? WHERE id=?',
                                         ((datetime.now(timezone.utc)+timedelta(seconds=delay)).isoformat(),offer_id))
                            raise TimeoutError('Oferta diferida hasta Retry-After')
                        time.sleep(delay)
                if not target: raise ValueError('Modelo ausente del catálogo')
                extraction=extractor.extract(raw,off['direct_url'],target)
            except Exception as exc:
                extraction=ExtractionResult(False,None,error_message=str(exc),raw_evidence_hash=extraction.raw_evidence_hash)
            previous=query_all("SELECT price_single_payment FROM observations WHERE offer_id=? AND validation_status='valido' AND is_synthetic=0 ORDER BY observed_at DESC LIMIT 10",(offer_id,))
            report=validate_observation(extraction,target,off,previous)
            published=bool(report.is_published and not use_fixtures and off['redistribution_allowed'])
            observed=_now()
            with get_db() as conn:
                cur=conn.cursor()
                q=lambda sql,params=():cur.execute(adapt_query(sql,config.STORAGE_MODE),params)
                if extraction.price_single_payment is not None:
                    # Los estados válidos, incluidos agotados, no se recapturan en el mismo período.
                    capture_key=prefix+offer_id if report.status=='valido' else None
                    q("""INSERT INTO observations(id,run_id,offer_id,product_id,observed_at,price_single_payment,currency,
                        price_transfer,price_reference_shown,availability,shipping_cost,shipping_note,validation_status,
                        is_published,is_synthetic,extractor_version,raw_evidence_hash,raw_evidence_snippet,created_at,capture_key)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(capture_key) DO NOTHING""",
                        (str(uuid.uuid4()),run_id,offer_id,off['product_id'],observed,str(extraction.price_single_payment),extraction.currency,
                         str(extraction.price_transfer) if extraction.price_transfer is not None else None,
                         str(extraction.price_reference_shown) if extraction.price_reference_shown is not None else None,
                         extraction.availability,None,extraction.shipping_note,report.status,int(published),int(use_fixtures),extraction.extractor_version,
                         extraction.raw_evidence_hash,extraction.raw_evidence_snippet,observed,capture_key))
                q('INSERT INTO collector_attempts(id,run_id,offer_id,observed_at,status,is_synthetic,details) VALUES (?,?,?,?,?,?,?)',
                  (str(uuid.uuid4()),run_id,offer_id,observed,report.status,int(use_fixtures),'; '.join(report.reasons)))
                q('UPDATE offers SET last_checked_at=? WHERE id=?',(observed,offer_id))
                if report.status=='valido':
                    q('UPDATE offers SET next_attempt_at=NULL WHERE id=?',(offer_id,))
                if report.incident_type:
                    q('INSERT INTO incidents(id,offer_id,run_id,incident_type,severity,details,created_at) VALUES (?,?,?,?,?,?,?)',
                      (str(uuid.uuid4()),offer_id,run_id,report.incident_type,report.incident_severity,report.incident_details or '',observed))
            processed+=1
            if report.status=='valido': successes+=1
            elif report.status=='anomalo': anomalies+=1
            else: failures+=1
            details.append({'offer_id':offer_id,'status':report.status,'is_published':published,'is_synthetic':use_fixtures,'reasons':report.reasons})
        pending=query_one("""SELECT COUNT(*) AS c FROM offers off JOIN sources src ON off.source_id=src.id
            WHERE off.enabled=1 AND src.status='habilitada' AND src.capture_allowed=1
            AND NOT EXISTS (SELECT 1 FROM observations o WHERE o.capture_key=? || off.id)""",(prefix,))['c']
        status='no_sources' if not offers else 'completed' if not failures and not anomalies and not pending else 'partial_failure' if successes else 'failed'
    except Exception:
        fatal='Error de persistencia o configuración; revisar los registros del servidor.'
        status='failed'; pending=None
        raise
    finally:
        finish=_now()
        execute_stmt('UPDATE collector_runs SET finished_at=?,status=?,total_offers=?,successful_offers=?,failed_offers=?,anomalies_detected=?,error_summary=? WHERE id=?',
                     (finish,status,processed,successes,failures,anomalies,fatal,run_id))
        execute_stmt('UPDATE collector_lease SET owner=NULL WHERE id=1 AND owner=?',(run_id,))
    return {'run_id':run_id,'status':status,'started_at':start,'finished_at':finish,'total_offers':processed,
            'successful_offers':successes,'failed_offers':failures,'anomalies_detected':anomalies,'pending_offers':pending,'is_fixture_run':use_fixtures,'details':details}
