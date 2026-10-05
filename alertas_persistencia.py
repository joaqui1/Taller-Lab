"""Estado y capturas duraderos: PostgreSQL en producción, SQLite para QA/local."""
import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

_local = threading.local()


class AlmacenOcupado(RuntimeError):
    pass


def database_url():
    return os.getenv('ALERTAS_DATABASE_URL') or os.getenv('ALERTAS_DATABASE_DATABASE_URL') or os.getenv('DATABASE_URL')


def configurado():
    return bool(database_url() or os.getenv('ALERTAS_STATE_PATH'))


def _sql(sql):
    return sql.replace('?', '%s') if _local.postgres else sql


def execute(sql, args=()):
    return _local.conn.execute(_sql(sql), args)


@contextmanager
def transaccion(seed_dir, lectura=False):
    url = database_url()
    if url:
        import psycopg
        conn = psycopg.connect(url, connect_timeout=10)
    else:
        path = Path(os.environ['ALERTAS_STATE_PATH'])
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path, timeout=2)
    _local.conn, _local.postgres = conn, bool(url)
    try:
        initialized = False
        if url:
            conn.execute('BEGIN ISOLATION LEVEL REPEATABLE READ')
            if lectura:
                exists = conn.execute("SELECT to_regclass('tallerlab_alertas_estado')").fetchone()[0]
                initialized = bool(exists and conn.execute('SELECT nombre FROM tallerlab_alertas_estado LIMIT 1').fetchone())
            if not lectura or not initialized:
                locked = conn.execute('SELECT pg_try_advisory_xact_lock(19481734)').fetchone()[0]
                if not locked:
                    raise AlmacenOcupado('Otra operación de alertas está en curso')
        else:
            try:
                conn.execute('BEGIN IMMEDIATE')
            except sqlite3.OperationalError as exc:
                raise AlmacenOcupado('Otra operación de alertas está en curso') from exc
        if not initialized:
            execute('CREATE TABLE IF NOT EXISTS tallerlab_alertas_estado (nombre TEXT PRIMARY KEY, payload TEXT NOT NULL)')
            execute('CREATE TABLE IF NOT EXISTS tallerlab_alertas_capturas (hash TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        if not initialized and not execute('SELECT nombre FROM tallerlab_alertas_estado LIMIT 1').fetchone():
            if (seed_dir / 'transaccion.json').exists():
                raise RuntimeError('Recuperar el snapshot local antes de inicializar el almacén')
            for name, default in [('modelos_expedientes.json', []), ('candidatos_revision.json', []), ('registro_fuentes.json', {})]:
                path = seed_dir / name
                value = json.loads(path.read_text(encoding='utf-8')) if path.exists() else default
                guardar(name, value)
            import hashlib
            for path in (seed_dir / 'capturas').glob('*.json'):
                raw = path.read_text(encoding='utf-8')
                if hashlib.sha256(raw.encode('utf-8')).hexdigest() != path.stem:
                    raise ValueError('Captura del snapshot corrupta')
                execute('INSERT INTO tallerlab_alertas_capturas(hash,payload) VALUES (?,?)', (path.stem, raw))
        yield
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()
        _local.conn = None


def leer(name, default):
    row = execute('SELECT payload FROM tallerlab_alertas_estado WHERE nombre=?', (name,)).fetchone()
    return json.loads(row[0]) if row else default


def guardar(name, value):
    execute('INSERT INTO tallerlab_alertas_estado(nombre,payload) VALUES (?,?) ON CONFLICT(nombre) DO UPDATE SET payload=excluded.payload',
            (name, json.dumps(value, ensure_ascii=False)))


def captura(digest):
    row = execute('SELECT payload FROM tallerlab_alertas_capturas WHERE hash=?', (digest,)).fetchone()
    return row[0] if row else None


def guardar_captura(digest, raw):
    existing = captura(digest)
    if existing is not None and existing != raw:
        raise ValueError('Captura existente no coincide con su hash')
    execute('INSERT INTO tallerlab_alertas_capturas(hash,payload) VALUES (?,?) ON CONFLICT(hash) DO NOTHING', (digest, raw))
