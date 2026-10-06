"""Versioned state: SQLite locally, PostgreSQL on serverless deployments."""
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

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
            row = conn.execute('SELECT v.payload FROM compatibility_versions v JOIN compatibility_current c ON c.version=v.version WHERE c.id=1').fetchone()
            return json.loads(row[0]) if row else None

    def get(self, version):
        with self.connection() as (conn, mark):
            if conn is None:
                return None
            row = conn.execute(f'SELECT payload FROM compatibility_versions WHERE version={mark}', (version,)).fetchone()
            return json.loads(row[0]) if row else None

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
            conn.execute(f'INSERT INTO compatibility_versions VALUES ({mark},{mark},{mark})', (version, json.dumps(payload, ensure_ascii=False), payload['metadata']['published_at']))
            conn.execute(f'INSERT INTO compatibility_current (id,version) VALUES (1,{mark}) ON CONFLICT(id) DO UPDATE SET version=excluded.version', (version,))
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
