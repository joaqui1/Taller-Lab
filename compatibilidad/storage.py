"""Versioned state: SQLite locally, PostgreSQL on serverless deployments."""
import json
import os
import sqlite3
import uuid
from copy import deepcopy
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from threading import Lock

from compatibilidad.content_dates import FALLBACK_CONTENT_CHANGED_AT

# Cache por proceso de la versión activa ya migrada. Vive a nivel de módulo porque
# las lecturas públicas crean un StateStore nuevo en cada visita.
_MIGRATION_CACHE = {}
_MIGRATION_CACHE_LOCK = Lock()


def clear_migration_cache():
    """Vacía la caché de migración (tests y procesos que reemplazan la base)."""
    with _MIGRATION_CACHE_LOCK:
        _MIGRATION_CACHE.clear()

class ConcurrentUpdate(RuntimeError):
    pass

class StateStore:
    def __init__(self, path=None, database_url=None):
        self.url = database_url if database_url is not None else (
            os.getenv('COMPATIBILITY_DATABASE_URL') or os.getenv('DATABASE_URL')
            or os.getenv('ALERTAS_DATABASE_DATABASE_URL') or os.getenv('ALERTAS_DATABASE_URL'))
        self.path = Path(path or os.getenv('COMPATIBILITY_STATE_PATH') or Path(__file__).parents[1] / '.compatibilidad-state' / 'state.sqlite3')
        if os.getenv('VERCEL') and not self.url and path is None:
            raise RuntimeError('Compatibilidad requiere PostgreSQL en Vercel')

    @contextmanager
    def connection(self, write=False):
        if self.url:
            import psycopg
            conn = psycopg.connect(self.url, connect_timeout=10)
            mark = '%s'
        else:
            if not write and not self.path.exists():
                yield None, '?'
                return
            if write:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(self.path), timeout=20)
                conn.execute('BEGIN IMMEDIATE')
            else:
                conn = sqlite3.connect(self.path.resolve().as_uri() + '?mode=ro', uri=True)
            mark = '?'
        try:
            if write:
                if self.url:
                    conn.execute('SELECT pg_advisory_xact_lock(19481732)')
                conn.execute('CREATE TABLE IF NOT EXISTS compatibility_versions (version TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)')
                conn.execute('CREATE TABLE IF NOT EXISTS compatibility_current (id INTEGER PRIMARY KEY, version TEXT NOT NULL)')
            yield conn, mark
            if write:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def current(self):
        with self.connection() as (conn, _):
            if conn is None:
                return None
            exists=conn.execute("SELECT to_regclass('compatibility_current')" if self.url else "SELECT name FROM sqlite_master WHERE type='table' AND name='compatibility_current'").fetchone()
            if not exists or not exists[0]:
                return None
            row = conn.execute('SELECT v.version, v.payload FROM compatibility_versions v JOIN compatibility_current c ON c.version=v.version WHERE c.id=1').fetchone()
            if not row:
                return None
            version, raw_payload = row
            cached = self._cached_payload(version)
            if cached is not None:
                return cached
            payload = json.loads(raw_payload)
            first_publication = self._first_publication_dates_for_store(conn) if self._has_missing_content_dates(payload) else {'products': {}, 'relations': {}}
            migrated = self._migrate_legacy_payload(payload, first_publication=first_publication)
            self._remember_payload(version, migrated)
            return deepcopy(migrated)

    def _cache_key(self):
        return self.url or str(self.path.resolve())

    def _cached_payload(self, version):
        with _MIGRATION_CACHE_LOCK:
            cached = _MIGRATION_CACHE.get(self._cache_key())
            if cached and cached[0] == version:
                return deepcopy(cached[1])
        return None

    def _remember_payload(self, version, payload):
        with _MIGRATION_CACHE_LOCK:
            _MIGRATION_CACHE[self._cache_key()] = (version, deepcopy(payload))

    @staticmethod
    def _has_missing_content_dates(payload):
        return any(not item.get('content_changed_at') for section in ('products', 'relations')
                   for item in payload.get(section, []))

    def _first_publication_dates_for_store(self, conn):
        """Read only the per-record publication date projection from immutable snapshots."""
        if self.url:
            query = """
                SELECT 'products', item.value->>'id', MIN(COALESCE(v.payload::jsonb #>> '{metadata,published_at}', v.created_at))
                FROM compatibility_versions v
                CROSS JOIN LATERAL jsonb_array_elements(COALESCE(v.payload::jsonb->'products', '[]'::jsonb)) AS item(value)
                WHERE item.value->>'status'='publicado'
                GROUP BY item.value->>'id'
                UNION ALL
                SELECT 'relations', item.value->>'id', MIN(COALESCE(v.payload::jsonb #>> '{metadata,published_at}', v.created_at))
                FROM compatibility_versions v
                CROSS JOIN LATERAL jsonb_array_elements(COALESCE(v.payload::jsonb->'relations', '[]'::jsonb)) AS item(value)
                GROUP BY item.value->>'id'
            """
        else:
            query = """
                SELECT 'products', json_extract(item.value, '$.id'), MIN(COALESCE(json_extract(v.payload, '$.metadata.published_at'), v.created_at))
                FROM compatibility_versions v, json_each(v.payload, '$.products') AS item
                WHERE json_extract(item.value, '$.status')='publicado'
                GROUP BY json_extract(item.value, '$.id')
                UNION ALL
                SELECT 'relations', json_extract(item.value, '$.id'), MIN(COALESCE(json_extract(v.payload, '$.metadata.published_at'), v.created_at))
                FROM compatibility_versions v, json_each(v.payload, '$.relations') AS item
                GROUP BY json_extract(item.value, '$.id')
            """
        first = {'products': {}, 'relations': {}}
        for section, record_id, raw_date in conn.execute(query).fetchall():
            if not record_id:
                continue
            try:
                published_at = date.fromisoformat(str(raw_date)[:10]).isoformat()
            except (TypeError, ValueError):
                published_at = FALLBACK_CONTENT_CHANGED_AT
            first[section].setdefault(record_id, published_at)
        return first

    @staticmethod
    def _publication_date(payload, created_at):
        raw = payload.get('metadata', {}).get('published_at') or created_at
        try:
            return date.fromisoformat(str(raw)[:10]).isoformat()
        except (TypeError, ValueError):
            return FALLBACK_CONTENT_CHANGED_AT

    @classmethod
    def _first_publication_dates(cls, versions):
        first = {'products': {}, 'relations': {}}
        for raw_payload, created_at in versions:
            try:
                payload = json.loads(raw_payload) if isinstance(raw_payload, str) else raw_payload
            except (TypeError, json.JSONDecodeError):
                continue
            published_at = cls._publication_date(payload, created_at)
            for product in payload.get('products', []):
                if product.get('status') == 'publicado':
                    first['products'].setdefault(product.get('id'), published_at)
            for relation in payload.get('relations', []):
                first['relations'].setdefault(relation.get('id'), published_at)
        return first

    @classmethod
    def _migrate_legacy_payload(cls, payload, versions=(), first_publication=None):
        """Add dates to old snapshots when read, keeping immutable version rows intact."""
        state = json.loads(json.dumps(payload, ensure_ascii=False))
        first_publication = first_publication if first_publication is not None else cls._first_publication_dates(versions)
        for product in state.get('products', []):
            if not product.get('content_changed_at'):
                initial = first_publication['products'].get(product.get('id')) if product.get('status') == 'publicado' else None
                product['content_changed_at'] = initial or FALLBACK_CONTENT_CHANGED_AT
        for relation in state.get('relations', []):
            if not relation.get('content_changed_at'):
                relation['content_changed_at'] = first_publication['relations'].get(relation.get('id'), FALLBACK_CONTENT_CHANGED_AT)
        changelog = state.get('changelog', [])
        for evidence in state.get('evidences', []):
            evidence.setdefault('approved_source_hash', evidence.get('evidence_hash', ''))
            evidence.setdefault('source_approved_by', None)
            evidence.setdefault('source_approved_at', None)
            automatic_label='TallerLab: comprobación automática ' + 'de afirmaciones configuradas'
            if evidence.get('reviewer') == automatic_label:
                evidence['reviewer'] = ''
            if not evidence.get('source_approved_by') and '(aprobación del cambio; afirmaciones comprobadas automáticamente)' in evidence.get('reviewer', ''):
                reviewer = evidence['reviewer'].split(' (aprobación del cambio;', 1)[0].strip()
                source_id = evidence.get('source_id')
                approval = next((item for item in reversed(changelog)
                    if item.get('author') == reviewer and source_id in item.get('affected_records', [])), None)
                if reviewer and approval and approval.get('date'):
                    evidence['source_approved_by'] = reviewer
                    evidence['source_approved_at'] = approval['date']
        return state

    def get(self, version):
        with self.connection() as (conn, mark):
            if conn is None:
                return None
            row = conn.execute(f'SELECT payload FROM compatibility_versions WHERE version={mark}', (version,)).fetchone()
            if not row:
                return None
            versions = conn.execute('SELECT payload,created_at FROM compatibility_versions ORDER BY created_at,version').fetchall()
            return self._migrate_legacy_payload(json.loads(row[0]), versions)

    def publish(self, state, expected_version=None):
        payload = json.loads(json.dumps(state, ensure_ascii=False))
        version = '2-' + uuid.uuid4().hex
        payload['metadata'] = {**payload.get('metadata', {}), 'version': version,
                               'engine_version': '2', 'published_at': datetime.now(timezone.utc).isoformat()}
        for entry in payload.get('changelog', []):
            if entry['version']=='pendiente_publicacion':
                entry['version']=version
        with self.connection(True) as (conn, mark):
            current = conn.execute('SELECT version FROM compatibility_current WHERE id=1').fetchone()
            if (current[0] if current else None) != expected_version:
                raise ConcurrentUpdate('Otra ejecución publicó una versión; repetir desde el estado vigente')
            first_publication = (self._first_publication_dates_for_store(conn)
                                 if self._has_missing_content_dates(payload) else {'products': {}, 'relations': {}})
            payload = self._migrate_legacy_payload(payload, first_publication=first_publication)
            conn.execute(f'INSERT INTO compatibility_versions VALUES ({mark},{mark},{mark})', (version, json.dumps(payload, ensure_ascii=False), payload['metadata']['published_at']))
            conn.execute(f'INSERT INTO compatibility_current (id,version) VALUES (1,{mark}) ON CONFLICT(id) DO UPDATE SET version=excluded.version', (version,))
        self._remember_payload(version, payload)
        return payload

    def rollback(self, version):
        state = self.get(version)
        if not state or state.get('metadata', {}).get('engine_version') != '2':
            raise ValueError('Versión inexistente o incompatible con el motor actual')
        from compatibilidad.catalog import validate_state
        validate_state(state)
        with self.connection(True) as (conn, mark):
            conn.execute(f'UPDATE compatibility_current SET version={mark} WHERE id=1', (version,))
        return state
