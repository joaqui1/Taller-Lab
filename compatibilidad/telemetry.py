"""Optional aggregate counters; never store users' free-text queries."""
import os
import sqlite3
from pathlib import Path
from compatibilidad.storage import StateStore

DB_PATH=Path(__file__).parents[1]/'.compatibilidad-state'/'telemetry.sqlite3'
VALID_EVENTS={'busqueda_resuelta','modelo_no_encontrado','resultado_desconocido','identidad_ambigua',
              'visita_hub','visita_ficha','visita_plataforma','consulta_modelo','clic_fuente','clic_comercial','error_evidencia'}

def _store():
    return StateStore() if os.getenv('VERCEL') or os.getenv('COMPATIBILITY_DATABASE_URL') or os.getenv('DATABASE_URL') or os.getenv('ALERTAS_DATABASE_DATABASE_URL') or os.getenv('ALERTAS_DATABASE_URL') else StateStore(path=DB_PATH,database_url='')

def init_telemetry_db():
    # Kept for CLI compatibility: creation is lazy, only when an event is sent.
    return None

def track_event(event_type,query_text=None,model_a=None,model_b=None,verdict=None):
    if event_type not in VALID_EVENTS:
        return
    try:
        with _store().connection(write=True) as (conn,mark):
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
