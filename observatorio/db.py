"""Capa de abstracción de base de datos para el Observatorio."""

import sqlite3
from contextlib import contextmanager, closing
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from observatorio import config
import os



class DatabaseConnection:
    """Wrapper uniforme para operaciones sobre SQLite o PostgreSQL."""

    def __init__(self, mode: Optional[str] = None):
        self.mode = mode or config.STORAGE_MODE
        self._raw_conn = None

    def connect(self):
        if os.environ.get('VERCEL_ENV') == 'production' and self.mode != 'postgres':
            raise RuntimeError('El observatorio requiere PostgreSQL persistente en producción.')
        if self.mode == "postgres":
            if not config.DATABASE_URL:
                raise RuntimeError("Modo de almacenamiento 'postgres' configurado pero DATABASE_URL está vacía.")
            try:
                import psycopg
                self._raw_conn = psycopg.connect(config.DATABASE_URL, connect_timeout=10)
            except ImportError:
                try:
                    import psycopg2
                    self._raw_conn = psycopg2.connect(config.DATABASE_URL, connect_timeout=10)
                except Exception as exc:
                    raise RuntimeError('No se pudo abrir PostgreSQL; comprobar controlador y configuración.') from exc
        else:
            # Modo local predeterminado: SQLite
            config.SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
            self._raw_conn = sqlite3.connect(str(config.SQLITE_PATH), timeout=30)
            self._raw_conn.row_factory = sqlite3.Row
            # Habilitar claves foráneas en SQLite
            self._raw_conn.execute("PRAGMA foreign_keys = ON;")
        return self._raw_conn

    def close(self):
        if self._raw_conn:
            self._raw_conn.close()
            self._raw_conn = None


@contextmanager
def get_db(mode: Optional[str] = None):
    """Context manager para transacciones de base de datos."""
    effective_mode = mode or config.STORAGE_MODE
    db_wrapper = DatabaseConnection(effective_mode)
    conn = db_wrapper.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        db_wrapper.close()


def adapt_query(query: str, mode: str) -> str:
    """Adapta sintaxis de placeholders entre SQLite (?) y Postgres (%s)."""
    if mode == "postgres":
        return query.replace("?", "%s")
    return query


def query_all(query: str, params: Union[Tuple, List] = (), mode: Optional[str] = None) -> List[Dict[str, Any]]:
    """Ejecuta una consulta SELECT y retorna una lista de diccionarios con tipos adaptados."""
    effective_mode = mode or config.STORAGE_MODE
    with get_db(effective_mode) as conn:
        cursor = conn.cursor()
        adapted = adapt_query(query, effective_mode)
        cursor.execute(adapted, params)
        
        if effective_mode == "sqlite":
            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                _convert_decimals(d)
                result.append(d)
            return result
        else:
            # Postgres cursor
            desc = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(zip(desc, row))
                _convert_decimals(d)
                result.append(d)
            return result


def query_one(query: str, params: Union[Tuple, List] = (), mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Ejecuta una consulta SELECT y retorna un solo registro como diccionario."""
    rows = query_all(query, params, mode)
    return rows[0] if rows else None


def execute_stmt(query: str, params: Union[Tuple, List] = (), mode: Optional[str] = None) -> int:
    """Ejecuta una sentencia INSERT/UPDATE/DELETE y retorna filas afectadas."""
    effective_mode = mode or config.STORAGE_MODE
    with get_db(effective_mode) as conn:
        cursor = conn.cursor()
        adapted = adapt_query(query, effective_mode)
        cursor.execute(adapted, params)
        return cursor.rowcount


def _convert_decimals(row_dict: Dict[str, Any]):
    """Convierte campos de precio almacenados a tipo Decimal exacto."""
    decimal_fields = (
        "price_single_payment",
        "price_transfer",
        "price_reference_shown",
        "shipping_cost",
    )
    for field in decimal_fields:
        val = row_dict.get(field)
        if val is not None and not isinstance(val, Decimal):
            row_dict[field] = Decimal(str(val))


def init_db(schema_path: Optional[Path] = None, mode: Optional[str] = None):
    """Inicializa la base de datos aplicando el esquema relacional."""
    target_schema = schema_path or (config.OBSERVATORIO_DIR / "schema.sql")
    sql = target_schema.read_text(encoding="utf-8")
    effective_mode = mode or config.STORAGE_MODE

    with get_db(effective_mode) as conn:
        cursor = conn.cursor()
        if effective_mode == 'sqlite':
            prior = {r[1] for r in cursor.execute('PRAGMA table_info(observations)').fetchall()}
            if prior and ('capture_key' not in prior or 'is_synthetic' not in prior):
                backup = config.SQLITE_PATH.with_name(config.SQLITE_PATH.name+'.pre-v2-'+datetime.now().strftime('%Y%m%d%H%M%S%f')+'.bak')
                with closing(sqlite3.connect(backup)) as destination:
                    conn.backup(destination)
            cursor.execute('BEGIN IMMEDIATE')
        # Crear tablas antes de los índices: una base antigua necesita columnas nuevas.
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        tables = [s for s in statements if 'CREATE INDEX' not in s and 'CREATE UNIQUE INDEX' not in s]
        indexes = [s for s in statements if s not in tables]
        for stmt in tables:
            cursor.execute(stmt)
        additions = {
            'offers': {'next_attempt_at': 'TEXT'},
            'observations': {'is_synthetic': 'INTEGER NOT NULL DEFAULT 1', 'capture_key': 'TEXT'},
            'sources': {'terms_verified_date': 'TEXT', 'redistribution_allowed': 'INTEGER NOT NULL DEFAULT 0', 'capture_allowed': 'INTEGER NOT NULL DEFAULT 0'},
        }
        for table, columns in additions.items():
            if effective_mode == 'sqlite':
                existing = {r[1] for r in cursor.execute(f'PRAGMA table_info({table})').fetchall()}
            else:
                cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_schema=current_schema() AND table_name=%s', (table,))
                existing = {r[0] for r in cursor.fetchall()}
            for name, definition in columns.items():
                if name not in existing:
                    cursor.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')
        for stmt in indexes:
            cursor.execute(stmt)
        # Fixtures conocidos nunca pueden heredar procedencia real de un esquema anterior.
        from observatorio.extractors import fixtures
        from observatorio.extractors.base import BaseExtractor
        for name in dir(fixtures):
            value = getattr(fixtures,name)
            if name.startswith('FIXTURE_') and isinstance(value,str):
                cursor.execute(adapt_query('UPDATE observations SET is_synthetic=1,is_published=0 WHERE raw_evidence_hash=?',effective_mode),
                               (BaseExtractor.compute_evidence_hash(value),))
        cursor.execute(adapt_query('INSERT INTO data_versions(version_id,applied_at,description,methodology_version) VALUES (?, ?, ?, ?) ON CONFLICT(version_id) DO NOTHING', effective_mode),
                       ('2', datetime.now(timezone.utc).isoformat(), 'Procedencia conservadora, derechos y captura idempotente', '2026.2'))
