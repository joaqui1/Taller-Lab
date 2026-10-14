"""Optional counters and model/code text for searches without alert dossiers."""
import os
import re
import sqlite3
from pathlib import Path
from compatibilidad.storage import StateStore

DB_PATH=Path(__file__).parents[1]/'.compatibilidad-state'/'telemetry.sqlite3'
VALID_EVENTS={'busqueda_resuelta','modelo_no_encontrado','resultado_desconocido','identidad_ambigua',
              'visita_hub','visita_ficha','visita_plataforma','consulta_modelo','clic_fuente','clic_comercial','error_evidencia','calculator_embed_loaded',
              'alert_search_no_result'}

def _store():
    return StateStore() if os.getenv('VERCEL') or os.getenv('COMPATIBILITY_DATABASE_URL') or os.getenv('DATABASE_URL') or os.getenv('ALERTAS_DATABASE_DATABASE_URL') or os.getenv('ALERTAS_DATABASE_URL') else StateStore(path=DB_PATH,database_url='')

def init_telemetry_db():
    # Kept for CLI compatibility: creation is lazy, only when an event is sent.
    return None

def track_event(event_type,query_text=None,model_a=None,model_b=None,verdict=None,source_domain=None):
    if event_type not in VALID_EVENTS:
        return
    try:
        if event_type == 'alert_search_no_result':
            text = re.sub(r'\s+', ' ', str(query_text or '')).strip()[:120]
            if not text:
                return
            with _store().connection(write=True) as (conn,mark):
                conn.execute('CREATE TABLE IF NOT EXISTS alert_search_no_results (query_text TEXT NOT NULL)')
                conn.execute(f'INSERT INTO alert_search_no_results (query_text) VALUES ({mark})',(text,))
            return
        with _store().connection(write=True) as (conn,mark):
            if event_type == 'calculator_embed_loaded':
                domain = (source_domain or '').strip().lower().rstrip('.')[:253]
                if domain:
                    if not re.fullmatch(r'(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*', domain):
                        domain = ''
                if domain:
                    conn.execute('CREATE TABLE IF NOT EXISTS calculator_embed_metrics (domain TEXT PRIMARY KEY, count INTEGER NOT NULL)')
                    conn.execute(f'INSERT INTO calculator_embed_metrics VALUES ({mark},1) ON CONFLICT(domain) DO UPDATE SET count=calculator_embed_metrics.count+1',(domain,))
                return
            conn.execute('CREATE TABLE IF NOT EXISTS compatibility_metrics (event_type TEXT PRIMARY KEY, count INTEGER NOT NULL)')
            conn.execute(f'INSERT INTO compatibility_metrics VALUES ({mark},1) ON CONFLICT(event_type) DO UPDATE SET count=compatibility_metrics.count+1',(event_type,))
    except Exception:
        # Analytics must never change the availability or verdict of a page.
        return

def get_telemetry_summary():
    try:
        with _store().connection() as (conn,_):
            if conn is None:
                return {}
            return dict(conn.execute('SELECT event_type,count FROM compatibility_metrics').fetchall())
    except Exception:
        return {}

def get_alert_search_no_results(limit=100):
    """Devuelve las consultas sin expediente, agregadas solo por el texto buscado."""
    try:
        limit = max(1, min(int(limit), 500))
        store = _store()
        with store.connection() as (conn,_):
            if conn is None:
                return []
            table_exists = conn.execute("SELECT to_regclass('alert_search_no_results')").fetchone() if store.url else conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alert_search_no_results'").fetchone()
            if not table_exists or not table_exists[0]:
                return []
            placeholder = '%s' if store.url else '?'
            rows = conn.execute(f'SELECT query_text, COUNT(*) AS searches FROM alert_search_no_results GROUP BY query_text ORDER BY searches DESC, query_text LIMIT {placeholder}', (limit,)).fetchall()
            return [{'query_text': row[0], 'searches': row[1]} for row in rows]
    except Exception:
        return []
