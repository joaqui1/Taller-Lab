"""
Módulo del piloto «Relevamiento TallerLab 2027: herramientas y oficios en Argentina».

Proporciona:
- Esquema de preguntas y opciones normalizadas (con 'otro', 'no sé', 'prefiero no responder').
- Validación de servidor estricta, anti-spam (honeypot, tiempo mínimo, rate-limiting con 429) y detección de duplicados.
- Desacoplamiento estricto de PII respecto a datos analíticos.
- Persistencia atómica en SQLite (relevamiento.db) con transacciones thread-safe.
- Consentimientos independientes y no premarcados, con verificación obligatoria antes de moderar reseñas.
- Sanitización de fórmulas contra inyecciones en CSV.
- Landing y formulario responsive (/relevamiento-2027/) con accesibilidad y telemetría por sendBeacon.
- Borrador de metodología pública (/relevamiento-2027/metodologia/) con aviso Ley 25.326.
- Panel privado de administración (/relevamiento-2027/admin/) con moderación de respuestas y reseñas,
  control de muestra N visible, headers no-store y modo de datos demo aislado.
- Recomendaciones post-envío a guías de compra de TallerLab.
"""

import csv
import hashlib
import io
import json
import math
import os
import re
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent

# Cerrado por defecto. La producción exige almacenamiento externo y sesión estable.
def es_produccion():
    return bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV") or os.environ.get("APP_ENV") == "production")

def relevamiento_abierto():
    enabled = os.environ.get("RELEVAMIENTO_HABILITADO", "0").lower() in ("1", "true")
    ready = not es_produccion() or bool(os.environ.get("RELEVAMIENTO_DATABASE_URL") and len(os.environ.get("RELEVAMIENTO_SESSION_SECRET", "")) >= 32 and get_admin_key())
    return enabled and ready

RELEVAMIENTO_HABILITADO = False  # Compatibilidad; usar relevamiento_abierto().

# Configuración de almacenamiento SQLite
DATA_DIR = ROOT_DIR / "datos_relevamiento"
DB_PATH = DATA_DIR / "relevamiento.db"

# Compatibilidad con fixtures de prueba y overrides
ANALYTICS_FILE = DATA_DIR / "respuestas_analiticas.jsonl"
CONTACTS_FILE = DATA_DIR / "contactos.jsonl"
ABANDONS_FILE = DATA_DIR / "abandonos.jsonl"

DB_LOCK = Lock()
RATE_LIMIT_LOCK = Lock()

# Rate limiter estricto por IP en memoria (IP -> [timestamps])
IP_SUBMISSIONS: Dict[str, List[float]] = {}
RATE_LIMIT_WINDOW = 3600  # 1 hora
MAX_SUBMISSIONS_PER_IP = 10
CONSENT_VERSION = '2026-10-03-v1'

# Clave administrativa (fail-closed si no está configurada en producción)
ADMIN_KEY = os.environ.get("RELEVAMIENTO_ADMIN_KEY", "")


def get_admin_key() -> str:
    """Devuelve la clave de administración configurada actualmente."""
    global ADMIN_KEY
    return os.environ.get("RELEVAMIENTO_ADMIN_KEY", ADMIN_KEY)


# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE ---

class PostgresConnection:
    """Adaptador pequeño para consultas parametrizadas compartidas con SQLite."""
    def __init__(self, raw):
        self.raw = raw
    def execute(self, sql, params=()):
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")
        return self.raw.execute(sql.replace("?", "%s"), params)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        self.raw.rollback() if exc_type else self.raw.commit()
    def close(self):
        self.raw.close()

def get_db_connection(custom_path=None):
    dsn = os.environ.get("RELEVAMIENTO_DATABASE_URL", "") if custom_path is None else ""
    if dsn:
        import psycopg
        from psycopg.rows import dict_row
        conn = PostgresConnection(psycopg.connect(dsn, row_factory=dict_row, connect_timeout=10))
    else:
        if es_produccion():
            raise RuntimeError("El relevamiento requiere una base persistente en producción.")
        target = Path(custom_path or DB_PATH)
        target.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(target), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
    init_db_schema(conn)
    return conn


def init_db_schema(conn: sqlite3.Connection) -> None:
    """Crea las tablas del relevamiento si no existen."""
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            response_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'valida',
            motivos_revision TEXT NOT NULL DEFAULT '[]',
            notas_moderacion TEXT,
            oficio TEXT NOT NULL,
            oficio_otro TEXT,
            provincia TEXT NOT NULL,
            tipo_uso TEXT NOT NULL,
            intensidad TEXT NOT NULL,
            marca_principal TEXT NOT NULL,
            marca_otra TEXT,
            plataformas_bateria TEXT NOT NULL DEFAULT '[]',
            plataforma_otra TEXT,
            cantidad_baterias TEXT NOT NULL,
            proporcion_cable TEXT NOT NULL,
            canal_compra TEXT NOT NULL,
            canal_otro TEXT,
            reparaciones_12m TEXT NOT NULL,
            falla_frecuente TEXT NOT NULL,
            falla_otra TEXT,
            proxima_herramienta TEXT NOT NULL,
            proxima_otra TEXT,
            horizonte_compra TEXT,
            tiempo_llenado_segundos REAL,
            fingerprint TEXT,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            utm_content TEXT,
            consent_review INTEGER NOT NULL DEFAULT 0,
            tiene_resena INTEGER NOT NULL DEFAULT 0,
            es_demo INTEGER NOT NULL DEFAULT 0
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            email TEXT,
            nombre TEXT,
            consent_report INTEGER NOT NULL DEFAULT 0,
            consent_commercial INTEGER NOT NULL DEFAULT 0,
            consent_review INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (response_id) REFERENCES respuestas(response_id) ON DELETE CASCADE
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            modelo_exacto TEXT NOT NULL,
            tiempo_uso TEXT,
            intensidad TEXT,
            ventajas TEXT,
            problemas TEXT,
            reparaciones TEXT,
            volveria_a_comprar TEXT,
            foto_referencia TEXT,
            aprobada_publicacion INTEGER NOT NULL DEFAULT 0,
            tipo_evaluacion TEXT NOT NULL DEFAULT 'experiencia_declarada',
            FOREIGN KEY (response_id) REFERENCES respuestas(response_id) ON DELETE CASCADE
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS abandonos (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            session_id TEXT,
            paso TEXT NOT NULL,
            utm_info TEXT NOT NULL DEFAULT '{}'
        );
        """)
        conn.execute("""CREATE TABLE IF NOT EXISTS limites_envio (
            clave TEXT PRIMARY KEY, ventana INTEGER NOT NULL, cantidad INTEGER NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS consentimientos (
            response_id TEXT PRIMARY KEY, version TEXT NOT NULL, recorded_at TEXT NOT NULL,
            report INTEGER NOT NULL, commercial INTEGER NOT NULL, review INTEGER NOT NULL,
            revoked_at TEXT,
            FOREIGN KEY(response_id) REFERENCES respuestas(response_id) ON DELETE CASCADE
        )""")


# --- ESQUEMA NORMALIZADO DEL CUESTIONARIO ---

OFICIOS = [
    ("herreria", "Herrería / Estructuras metálicas / Soldadura"),
    ("carpinteria", "Carpintería / Mueblería / Construcción en madera"),
    ("mecanica", "Mecánica automotor / Motos / Motores"),
    ("electricidad", "Electricidad / Instalaciones electromecánicas"),
    ("plomeria", "Plomería / Gas / Instalaciones sanitarias"),
    ("construccion", "Construcción tradicional / Albañilería / Durlock"),
    ("mantenimiento", "Mantenimiento general edilicio / Industrial"),
    ("hobista", "Aficionado / Hobista / Bricolaje en el hogar"),
    ("otro", "Otro oficio o actividad"),
    ("no_responde", "Prefiero no responder"),
]

PROVINCIAS = [
    "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
    "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones",
    "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
    "Santiago del Estero", "Tierra del Fuego", "Tucumán", "Prefiero no responder"
]

TIPOS_USO = [
    ("profesional", "Profesional / Comercial (herramienta de trabajo remunerado)"),
    ("domestico", "Doméstico / Hogareño (mantenimiento propio y proyectos personales)"),
    ("mixto", "Mixto (uso propio más trabajos particulares ocasionales)"),
    ("no_responde", "Prefiero no responder"),
]

INTENSIDADES_USO = [
    ("diario_intensivo", "Diario intensivo (más de 6 horas por jornada)"),
    ("diario_moderado", "Diario (hasta 6 horas por jornada)"),
    ("semanal", "Varias veces por semana, sin uso diario"),
    ("mensual", "Ocasional mensual (algunas veces al mes)"),
    ("esporadico", "Esporádico (ante reparaciones imprevistas)"),
    ("no_sabe", "Varía demasiado / No sé"),
]

MARCAS_PRINCIPALES = [
    "Bosch", "DeWalt", "Makita", "Milwaukee", "Einhell", "Gamma", "Lüsqtoff",
    "Stanley", "Black+Decker", "Total", "Ingco", "Dowen Pagio", "Philco",
    "Dremel", "Skil", "Metabo", "Gladiator", "Barovo", "Otra marca", "No sé / No tengo marca fija"
]

# Plataformas de batería con familias e IDs independientes
PLATAFORMAS_BATERIA = [
    ("no_usa", "No uso herramientas a batería (solo cable o neumático)"),
    ("bosch_18v", "Bosch 18V Professional (AMPShare)"),
    ("dewalt_20v", "DeWalt 20V MAX / XR"),
    ("dewalt_flexvolt", "DeWalt 60V / 54V FlexVolt"),
    ("makita_lxt_18v", "Makita 18V LXT"),
    ("makita_xgt_40v", "Makita 40V Max XGT"),
    ("milwaukee_m18", "Milwaukee M18 FUEL / Standard"),
    ("milwaukee_m12", "Milwaukee M12 Subcompacta"),
    ("einhell_pxc", "Einhell Power X-Change (18V)"),
    ("stanley_v20", "Stanley V20 (FatMax)"),
    ("total_ingco_20v", "Total / Ingco 20V (P20S)"),
    ("lusqtoff_18v", "Lüsqtoff 18V / 20V Powerlink"),
    ("gamma_18v", "Gamma 18V / 20V"),
    ("blackdecker_20v", "Black+Decker 20V MAX"),
    ("otra", "Otra plataforma o voltaje"),
    ("no_sabe", "No sé la plataforma exacta"),
]

CANTIDAD_BATERIAS = [
    ("0", "0 (no uso baterías)"),
    ("1", "1 batería"),
    ("2", "2 baterías"),
    ("3_4", "3 a 4 baterías"),
    ("5_mas", "5 o más baterías"),
    ("no_responde", "Prefiero no responder"),
]

PROPORCION_CABLE_BATERIA = [
    ("100_cable", "Todo el tiempo con cable"),
    ("mayormente_cable", "Más de la mitad del tiempo con cable"),
    ("50_50", "Aproximadamente la mitad del tiempo con cada una"),
    ("mayormente_bateria", "Más de la mitad del tiempo a batería"),
    ("100_bateria", "Todo el tiempo a batería"),
    ("no_responde", "Prefiero no responder"),
]

CANALES_COMPRA = [
    ("mercadolibre", "Mercado Libre"),
    ("ferreteria_local", "Ferretería de barrio / Ferretería industrial local"),
    ("grandes_tiendas", "Grandes tiendas de hogar y construcción (Easy, Sodimac)"),
    ("distribuidor_oficial", "Distribuidor oficial o importador de la marca"),
    ("usados", "Herramientas usadas / Marketplace / Redes sociales"),
    ("importacion_directa", "Compra directa en el exterior / importación"),
    ("otro", "Otro canal"),
    ("no_responde", "Prefiero no responder"),
]

REPARACIONES_12M = [
    ("0", "0 reparaciones (no se rompió ninguna herramienta)"),
    ("0_reemplazo", "0 reparaciones (se rompió alguna y se reemplazó sin reparar)"),
    ("1", "1 reparación"),
    ("2_3", "2 a 3 reparaciones"),
    ("4_mas", "4 o más reparaciones"),
    ("no_sabe", "No sé / No llevo registro"),
]

FALLAS_FRECUENTES = [
    ("ninguna", "No tuve fallas"),
    ("no_sabe", "No sé / Prefiero no responder"),
    ("carbones", "Carbones desgastados / Colector chispeante"),
    ("gatillo", "Gatillo / Interruptor de encendido defectuoso"),
    ("mandril", "Mandril o portabrocas trabado / desalineado"),
    ("rodamientos", "Rodamientos o engranajes con juego o rotos"),
    ("bateria", "Batería que perdió autonomía / cargador que dejó de andar"),
    ("cable", "Cable de alimentación cortado o falseado"),
    ("bobinado", "Bobinado quemado / olor a recalentado"),
    ("fugas", "Fugas de aire, aceite o sellos (compresor/hidro)"),
    ("otra", "Otra falla técnica"),
]

PROXIMA_HERRAMIENTA = [
    ("taladro", "Taladro / Atornillador / Rotomartillo"),
    ("amoladora", "Amoladora angular (115, 125 o 230 mm)"),
    ("sierra", "Sierra (circular, caladora, ingletadora o de banco)"),
    ("hidrolavadora", "Hidrolavadora de alta presión"),
    ("compresor", "Compresor de aire"),
    ("soldadora", "Soldadora (inverter MMA, MIG flux o TIG)"),
    ("generador", "Generador eléctrico / Grupo electrógeno"),
    ("soldadura_electronica", "Soldador de estaño / Estación de soldadura"),
    ("otra", "Otra herramienta"),
    ("ninguna", "Ninguna por ahora / No planeo comprar en el corto plazo"),
]

HORIZONTES_COMPRA = [
    ("30_dias", "En los próximos 30 días"),
    ("90_dias", "En los próximos 1 a 3 meses"),
    ("6_meses", "En los próximos 3 a 6 meses"),
    ("mas_6_meses", "En más de 6 meses"),
    ("sin_fecha", "Sin fecha definida / Solo si surge una oportunidad"),
]

# Mapeo de recomendación post-encuesta hacia guías de TallerLab
GUIAS_RECOMENDADAS_POR_HERRAMIENTA = {
    "taladro": [
        ("/taladros/", "Guía completa de taladros y rotomartillos"),
        ("/taladros/inalambricos/", "Taladros inalámbricos: mandril, voltaje y baterías"),
        ("/taladros/rotomartillos/", "Rotomartillos SDS: energía de impacto documentada"),
    ],
    "amoladora": [
        ("/amoladoras/", "Guía de amoladoras angulares"),
        ("/amoladoras/115-o-125/", "Amoladoras de 115 mm vs 125 mm: potencia y corte"),
        ("/amoladoras/9-pulgadas/", "Amoladoras de 230 mm (9 pulgadas) para obra pesada"),
    ],
    "sierra": [
        ("/sierras/", "Guía de sierras para taller y obra"),
        ("/sierras/circulares/", "Sierras circulares: profundidad de corte y guías"),
        ("/sierras/caladoras/", "Sierras caladoras: movimiento pendular y hojas"),
    ],
    "hidrolavadora": [
        ("/hidrolavadoras/", "Guía general de hidrolavadoras"),
        ("/hidrolavadoras/comparativa-general/", "Presión y caudal documentados en hidrolavadoras"),
        ("/hidrolavadoras/profesionales/", "Equipos de uso intensivo y servicio técnico"),
    ],
    "compresor": [
        ("/compresores/", "Guía de compresores de aire"),
        ("/compresores/50-litros/", "Compresores de 50 litros: caudal vs tanque"),
        ("/compresores/100-litros/", "Compresores de 100 litros para taller"),
    ],
    "soldadora": [
        ("/soldadoras/", "Guía de soldadoras y procesos"),
        ("/soldadoras/mig-sin-gas/", "Soldadoras MIG flux sin gas: ventajas y límites"),
        ("/soldadoras/esab-handyarc-162i/", "Análisis documental de la ESAB HandyArc 162i"),
    ],
    "generador": [
        ("/generadores/", "Guía de generadores y grupos electrógenos"),
        ("/generadores/a-nafta/", "Generadores a nafta: cálculo de potencia y consumo"),
        ("/generadores/para-casa/", "Respaldo eléctrico domiciliario ante cortes"),
    ],
    "soldadura_electronica": [
        ("/soldadura-electronica/estacion-de-soldadura/", "Estaciones de soldadura con control de temperatura"),
        ("/soldadura-electronica/kit-soldador-de-estano/", "Kits de soldador de estaño para reparaciones"),
    ],
    "otra": [
        ("/", "Portada de TallerLab: explorá las 8 categorías de herramientas"),
        ("/como-trabajamos/", "Metodología editorial y análisis documental"),
    ],
    "ninguna": [
        ("/", "Portada de TallerLab: comparativas y calculadoras"),
        ("/como-trabajamos/", "Cómo analizamos herramientas y especificaciones"),
    ],
}


# --- UTILIDADES DE VALIDACIÓN Y PARSING ---

def parse_strict_bool(val: Any, default: bool = False) -> Tuple[bool, bool]:
    """
    Parsea de forma estricta un valor booleano.
    Retorna: (parsed_value, is_valid_syntax)
    """
    if val is None:
        return default, True
    if isinstance(val, bool):
        return val, True
    if isinstance(val, (int, float)):
        if val == 1:
            return True, True
        if val == 0:
            return False, True
        return default, False
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "1"):
            return True, True
        if v in ("false", "0", ""):
            return False, True
        return default, False
    return default, False


def sanitize_csv_cell(val: Any) -> str:
    """
    Sanitiza celdas para prevenir inyección de fórmulas en hojas de cálculo
    (Excel/LibreOffice) cuando el valor inicia con =, +, -, @, tab o retorno.
    """
    if val is None:
        return ""
    s = str(val)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def clean_string_field(val: Any, max_len: int = 100) -> Optional[str]:
    """Limpia y valida un campo de texto; retorna None si el tipo no es string."""
    if val is None:
        return ""
    if not isinstance(val, str):
        return None
    cleaned = val.strip()[:max_len]
    return cleaned


# --- FUNCIONES DE ALMACENAMIENTO Y LECTURA ---

def registrar_abandono(paso_alcanzado, utm_info=None, session_id=None):
    allowed = {"start", "profile", "equipment", "purchase", "review", "completed", "exit"}
    if paso_alcanzado not in allowed or not isinstance(session_id, str) or not re.fullmatch(r"[a-zA-Z0-9-]{16,64}", session_id):
        raise ValueError("Evento o sesión inválida")
    if utm_info is not None and not isinstance(utm_info, dict):
        raise ValueError("Origen inválido")
    utm = {}
    for key, val in (utm_info or {}).items():
        if key not in {"source", "medium", "campaign", "content"} or not isinstance(val, str) or len(val) > 80:
            raise ValueError("Origen inválido")
        utm[key] = val
    event_id = hashlib.sha256((session_id + ':' + paso_alcanzado).encode()).hexdigest()
    event = {"id": event_id, "at": datetime.now(timezone.utc).isoformat(), "paso": paso_alcanzado, "session_id": session_id, "utm": utm}
    with DB_LOCK:
        conn = get_db_connection()
        try:
            with conn:
                conn.execute("INSERT INTO abandonos (id, created_at, session_id, paso, utm_info) VALUES (?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
                    (event_id, event['at'], session_id, paso_alcanzado, json.dumps(utm)))
        finally:
            conn.close()
    return event


def guardar_respuesta_y_contacto(datos_analiticos: Dict[str, Any], datos_contacto: Optional[Dict[str, Any]] = None) -> str:
    """
    Almacena los datos del relevamiento en SQLite con transacción atómica,
    separando estrictamente los datos analíticos del contacto (PII).
    """
    response_id = datos_analiticos.get("response_id") or str(uuid.uuid4())
    datos_analiticos["response_id"] = response_id
    created_at = datos_analiticos.get("timestamp") or datetime.now(timezone.utc).isoformat()
    datos_analiticos["timestamp"] = created_at

    with DB_LOCK:
        conn = get_db_connection()
        try:
            with conn:
                # 1. Guardar respuesta analítica
                plataformas_json = json.dumps(
                    datos_analiticos.get("plataformas_bateria", []),
                    ensure_ascii=False
                )
                motivos_json = json.dumps(
                    datos_analiticos.get("motivos_revision", []),
                    ensure_ascii=False
                )

                conn.execute("""
                INSERT INTO respuestas (
                    response_id, created_at, estado, motivos_revision, notas_moderacion,
                    oficio, oficio_otro, provincia, tipo_uso, intensidad,
                    marca_principal, marca_otra, plataformas_bateria, plataforma_otra,
                    cantidad_baterias, proporcion_cable, canal_compra, canal_otro,
                    reparaciones_12m, falla_frecuente, falla_otra, proxima_herramienta,
                    proxima_otra, horizonte_compra, tiempo_llenado_segundos, fingerprint,
                    utm_source, utm_medium, utm_campaign, utm_content, consent_review,
                    tiene_resena, es_demo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    response_id,
                    created_at,
                    datos_analiticos.get("estado", "valida"),
                    motivos_json,
                    datos_analiticos.get("notas_moderacion"),
                    datos_analiticos.get("oficio", ""),
                    datos_analiticos.get("oficio_otro", ""),
                    datos_analiticos.get("provincia", ""),
                    datos_analiticos.get("tipo_uso", ""),
                    datos_analiticos.get("intensidad", ""),
                    datos_analiticos.get("marca_principal", ""),
                    datos_analiticos.get("marca_otra", ""),
                    plataformas_json,
                    datos_analiticos.get("plataforma_otra", ""),
                    datos_analiticos.get("cantidad_baterias", "0"),
                    datos_analiticos.get("proporcion_cable", "100_cable"),
                    datos_analiticos.get("canal_compra", ""),
                    datos_analiticos.get("canal_otro", ""),
                    datos_analiticos.get("reparaciones_12m", "0"),
                    datos_analiticos.get("falla_frecuente", "ninguna"),
                    datos_analiticos.get("falla_otra", ""),
                    datos_analiticos.get("proxima_herramienta", "ninguna"),
                    datos_analiticos.get("proxima_otra", ""),
                    datos_analiticos.get("horizonte_compra", "sin_fecha"),
                    datos_analiticos.get("tiempo_llenado_segundos"),
                    datos_analiticos.get("fingerprint", ""),
                    datos_analiticos.get("utm_source", "organico_directo"),
                    datos_analiticos.get("utm_medium", ""),
                    datos_analiticos.get("utm_campaign", ""),
                    datos_analiticos.get("utm_content", ""),
                    1 if datos_analiticos.get("consent_review") else 0,
                    1 if datos_analiticos.get("tiene_resena") else 0,
                    1 if datos_analiticos.get("es_dato_simulado_demo") else 0,
                ))

                # 2. Guardar reseña opcional si existe
                resena_data = datos_analiticos.get("resena")
                if resena_data:
                    conn.execute("""
                    INSERT INTO resenas (
                        response_id, created_at, modelo_exacto, tiempo_uso, intensidad,
                        ventajas, problemas, reparaciones, volveria_a_comprar,
                        foto_referencia, aprobada_publicacion, tipo_evaluacion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        response_id,
                        created_at,
                        resena_data.get("modelo_exacto", ""),
                        resena_data.get("tiempo_uso", ""),
                        resena_data.get("intensidad", ""),
                        resena_data.get("ventajas", ""),
                        resena_data.get("problemas", ""),
                        resena_data.get("reparaciones", ""),
                        resena_data.get("volveria_a_comprar", ""),
                        resena_data.get("foto_referencia", ""),
                        1 if resena_data.get("aprobada_publicacion") else 0,
                        resena_data.get("tipo_evaluacion", "experiencia_declarada"),
                    ))

                # 3. Guardar registro de contacto y consentimientos de forma aislada
                if datos_contacto is not None:
                    conn.execute("""
                    INSERT INTO contactos (
                        response_id, created_at, email, nombre, consent_report, consent_commercial, consent_review
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        response_id,
                        created_at,
                        (datos_contacto.get("email") or "").strip().lower(),
                        (datos_contacto.get("nombre") or "").strip()[:80],
                        1 if datos_contacto.get("consent_report") else 0,
                        1 if datos_contacto.get("consent_commercial") else 0,
                        1 if datos_contacto.get("consent_review") else 0,
                    ))

                permisos = datos_contacto or {}
                conn.execute('INSERT INTO consentimientos (response_id, version, recorded_at, report, commercial, review) VALUES (?, ?, ?, ?, ?, ?)',
                    (response_id, CONSENT_VERSION, created_at, int(bool(permisos.get('consent_report'))), int(bool(permisos.get('consent_commercial'))), int(bool(datos_analiticos.get('consent_review')))))
        finally:
            conn.close()

    return response_id

def revocar_contacto(response_id):
    """Baja editorial: elimina contacto y revoca permisos en una transacción."""
    if not isinstance(response_id, str) or not 1 <= len(response_id) <= 64:
        return False
    conn = get_db_connection()
    try:
        with conn:
            if isinstance(conn, sqlite3.Connection): conn.execute('BEGIN IMMEDIATE')
            suffix = ' FOR UPDATE' if isinstance(conn, PostgresConnection) else ''
            if not conn.execute('SELECT response_id FROM respuestas WHERE response_id = ?' + suffix, (response_id,)).fetchone():
                return False
            conn.execute('DELETE FROM contactos WHERE response_id = ?', (response_id,))
            conn.execute('UPDATE respuestas SET consent_review = 0 WHERE response_id = ?', (response_id,))
            conn.execute('UPDATE resenas SET aprobada_publicacion = 0 WHERE response_id = ?', (response_id,))
            conn.execute('UPDATE consentimientos SET report = 0, commercial = 0, review = 0, revoked_at = ? WHERE response_id = ?', (datetime.now(timezone.utc).isoformat(),response_id))
        return True
    finally:
        conn.close()


def cargar_respuestas_analiticas() -> List[Dict[str, Any]]:
    """Lee todas las respuestas analíticas almacenadas en SQLite."""
    with DB_LOCK:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM respuestas ORDER BY created_at ASC").fetchall()
        resenas_rows = conn.execute("SELECT * FROM resenas").fetchall()
        conn.close()

    resenas_by_id = {}
    for r in resenas_rows:
        resenas_by_id[r["response_id"]] = {
            "modelo_exacto": r["modelo_exacto"],
            "tiempo_uso": r["tiempo_uso"],
            "intensidad": r["intensidad"],
            "ventajas": r["ventajas"],
            "problemas": r["problemas"],
            "reparaciones": r["reparaciones"],
            "volveria_a_comprar": r["volveria_a_comprar"],
            "foto_referencia": r["foto_referencia"],
            "aprobada_publicacion": bool(r["aprobada_publicacion"]),
            "tipo_evaluacion": r["tipo_evaluacion"],
        }

    resultado = []
    for row in rows:
        item = dict(row)
        try:
            item["motivos_revision"] = json.loads(item["motivos_revision"])
        except Exception:
            item["motivos_revision"] = []
        try:
            plataformas = json.loads(item["plataformas_bateria"])
            item["plataformas_bateria"] = plataformas
            # Compatibilidad con clave singular
            item["plataforma_bateria"] = plataformas[0] if plataformas else "no_usa"
        except Exception:
            item["plataformas_bateria"] = []
            item["plataforma_bateria"] = "no_usa"

        item["consent_review"] = bool(item.get("consent_review"))
        item["tiene_resena"] = bool(item.get("tiene_resena"))
        if item.get("es_demo"):
            item["es_dato_simulado_demo"] = True

        if item["response_id"] in resenas_by_id:
            item["resena"] = resenas_by_id[item["response_id"]]

        # Garantizar que ningún dato identificable (PII) esté presente
        item.pop("email", None)
        item.pop("contacto_email", None)
        item.pop("nombre", None)
        resultado.append(item)

    return resultado


def cargar_contactos() -> List[Dict[str, Any]]:
    """Lee los registros de contacto almacenados en SQLite."""
    with DB_LOCK:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM contactos ORDER BY created_at ASC").fetchall()
        conn.close()

    resultado = []
    for r in rows:
        resultado.append({
            "response_id": r["response_id"],
            "timestamp": r["created_at"],
            "email": r["email"] or "",
            "nombre": r["nombre"] or "",
            "consent_report": bool(r["consent_report"]),
            "consent_commercial": bool(r["consent_commercial"]),
            "consent_review": bool(r["consent_review"]),
        })
    return resultado


def cargar_abandonos() -> List[Dict[str, Any]]:
    """Lee los eventos de abandono almacenados en SQLite."""
    with DB_LOCK:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM abandonos ORDER BY created_at ASC").fetchall()
        conn.close()

    resultado = []
    for r in rows:
        try:
            utm = json.loads(r["utm_info"])
        except Exception:
            utm = {}
        resultado.append({
            "id": r["id"],
            "at": r["created_at"],
            "session_id": r["session_id"] or "",
            "paso": r["paso"],
            "utm": utm,
        })
    return resultado


def actualizar_estado_moderacion(response_id, nuevo_estado=None, notas=None, aprobar_resena=None):
    if not isinstance(response_id, str) or len(response_id) > 64:
        return False
    if nuevo_estado is not None and nuevo_estado not in {"valida", "descartada", "revision_pendiente"}:
        return False
    if aprobar_resena is not None and type(aprobar_resena) is not bool:
        return False
    if notas is not None and (not isinstance(notas, str) or len(notas) > 2000):
        return False
    if nuevo_estado is None and aprobar_resena is None and notas is None:
        return False
    with DB_LOCK:
        conn = get_db_connection()
        try:
            with conn:
                if isinstance(conn, sqlite3.Connection): conn.execute('BEGIN IMMEDIATE')
                suffix = ' FOR UPDATE' if isinstance(conn, PostgresConnection) else ''
                row = conn.execute("SELECT estado, consent_review FROM respuestas WHERE response_id = ?" + suffix, (response_id,)).fetchone()
                review = conn.execute("SELECT response_id FROM resenas WHERE response_id = ?", (response_id,)).fetchone()
                if not row or (aprobar_resena is not None and not review):
                    return False
                final_state = nuevo_estado or row['estado']
                if aprobar_resena is True and (not row['consent_review'] or final_state != 'valida'):
                    return False
                # All requirements checked before any write.
                if nuevo_estado is not None:
                    conn.execute("UPDATE respuestas SET estado = ? WHERE response_id = ?", (nuevo_estado, response_id))
                    if nuevo_estado != 'valida':
                        conn.execute("UPDATE resenas SET aprobada_publicacion = 0 WHERE response_id = ?", (response_id,))
                if notas is not None:
                    conn.execute("UPDATE respuestas SET notas_moderacion = ? WHERE response_id = ?", (notas, response_id))
                if aprobar_resena is not None:
                    conn.execute("UPDATE resenas SET aprobada_publicacion = ? WHERE response_id = ?", (int(aprobar_resena), response_id))
            return True
        finally:
            conn.close()


# --- VALIDACIÓN DE SERVIDOR Y FILTROS ANTI-SPAM ---

def check_ip_rate_limit(client_ip: str, maximum=MAX_SUBMISSIONS_PER_IP) -> bool:
    """Contador atómico persistente por hora, compartido entre procesos."""
    ventana = int(time.time() // RATE_LIMIT_WINDOW)
    secret = os.environ.get('RELEVAMIENTO_SESSION_SECRET', 'local-only')
    clave = hashlib.sha256(f'{secret}:{client_ip}:{ventana}'.encode()).hexdigest()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('DELETE FROM limites_envio WHERE ventana < ?', (ventana - 1,))
            row = conn.execute('''INSERT INTO limites_envio (clave, ventana, cantidad) VALUES (?, ?, 1)
                ON CONFLICT(clave) DO UPDATE SET cantidad = limites_envio.cantidad + 1
                WHERE limites_envio.cantidad < ? RETURNING cantidad''', (clave, ventana, maximum)).fetchone()
            return row is None
    finally:
        conn.close()


def validar_y_procesar_formulario(data: Any, client_ip: str = "127.0.0.1", user_agent: str = "") -> Tuple[bool, Any, int]:
    """
    Aplica validaciones estrictas de esquema, tipos y lógica de negocio.
    Retorna: (es_valido, respuesta_o_errores, status_code_http)
    """
    if not relevamiento_abierto():
        return False, {"_global": "El relevamiento todavía no está abierto."}, 503
    # 0. Verificación de tipo del cuerpo
    if not isinstance(data, dict):
        return False, {"_global": "El cuerpo de la solicitud debe ser un objeto JSON válido."}, 400

    # 1. Rate limiting antes de tocar disco
    if check_ip_rate_limit(client_ip):
        return False, {"_rate_limit": "Demasiadas solicitudes desde esta dirección IP. Intentá más tarde."}, 429

    errores: Dict[str, str] = {}

    # 2. Anti-spam: Honeypot
    honeypot_raw = data.get("empresa_rubro_hidden")
    if honeypot_raw is not None and not isinstance(honeypot_raw, str):
        return False, {"empresa_rubro_hidden": "Tipo de dato no válido."}, 400
    honeypot_val = (honeypot_raw or "").strip()
    es_spam_honeypot = bool(honeypot_val)

    # 3. Anti-spam: Tiempo de llenado y timestamp
    client_start_time = data.get("form_start_timestamp")
    tiempo_llenado_segundos: Optional[float] = None
    es_envio_ultrarrapido = False
    motivo_tiempo = None

    if not client_start_time:
        motivo_tiempo = "sin_marca_temporal_inicio"
    else:
        try:
            tiempo_llenado_segundos = time.time() - float(client_start_time)
            if not math.isfinite(tiempo_llenado_segundos):
                raise ValueError('Timestamp no finito')
            if tiempo_llenado_segundos < 5.0:
                es_envio_ultrarrapido = True
        except (ValueError, TypeError):
            motivo_tiempo = "timestamp_invalido"

    # 4. Validar campos requeridos y tipos
    oficio = clean_string_field(data.get("oficio"), max_len=60)
    if oficio is None:
        errores["oficio"] = "Tipo de dato no válido para oficio."
    elif not oficio or oficio not in {k for k, _ in OFICIOS}:
        errores["oficio"] = "Seleccioná tu oficio o actividad principal."

    oficio_otro = clean_string_field(data.get("oficio_otro"), max_len=80) or ""

    provincia = clean_string_field(data.get("provincia"), max_len=60)
    if provincia is None:
        errores["provincia"] = "Tipo de dato no válido para provincia."
    elif not provincia or provincia not in PROVINCIAS:
        errores["provincia"] = "Seleccioná una provincia de la lista."

    tipo_uso = clean_string_field(data.get("tipo_uso"), max_len=60)
    if tipo_uso is None:
        errores["tipo_uso"] = "Tipo de dato no válido para tipo de uso."
    elif not tipo_uso or tipo_uso not in {k for k, _ in TIPOS_USO}:
        errores["tipo_uso"] = "Indicá si tu uso es profesional, hogareño o mixto."

    intensidad = clean_string_field(data.get("intensidad"), max_len=60)
    if intensidad is None:
        errores["intensidad"] = "Tipo de dato no válido para intensidad."
    elif not intensidad or intensidad not in {k for k, _ in INTENSIDADES_USO}:
        errores["intensidad"] = "Indicá la intensidad de uso habitual."

    marca_principal = clean_string_field(data.get("marca_principal"), max_len=80)
    if not marca_principal or marca_principal not in MARCAS_PRINCIPALES:
        errores["marca_principal"] = "Seleccioná una marca de la lista; para otra marca elegí Otra marca."

    marca_otra = clean_string_field(data.get("marca_otra"), max_len=80) or ""

    # Plataformas de batería: admite lista o valor individual
    plataformas_validas = {k for k, _ in PLATAFORMAS_BATERIA}
    plataformas_in: List[str] = []
    raw_plat = data.get("plataformas_bateria") or data.get("plataforma_bateria")
    if isinstance(raw_plat, list):
        for p in raw_plat:
            if isinstance(p, str) and p.strip() in plataformas_validas:
                plataformas_in.append(p.strip())
    elif isinstance(raw_plat, str) and raw_plat.strip() in plataformas_validas:
        plataformas_in.append(raw_plat.strip())

    if not plataformas_in:
        errores["plataforma_bateria"] = "Seleccioná la plataforma de batería que utilizás."

    plataformas_in = list(dict.fromkeys(plataformas_in))
    if isinstance(raw_plat, list) and any(not isinstance(x, str) or x not in plataformas_validas for x in raw_plat):
        errores["plataforma_bateria"] = "Hay una plataforma no reconocida."
    if len(plataformas_in) > 1 and any(x in plataformas_in for x in ("no_usa", "no_sabe")):
        errores["plataforma_bateria"] = "No uso batería y No sé deben seleccionarse sin otras plataformas."
    plataforma_otra = clean_string_field(data.get("plataforma_otra"), max_len=80) or ""

    cantidad_baterias = clean_string_field(data.get("cantidad_baterias"), max_len=30)
    if not cantidad_baterias or cantidad_baterias not in {k for k, _ in CANTIDAD_BATERIAS}:
        errores["cantidad_baterias"] = "Indicá la cantidad aproximada de baterías."

    proporcion_cable = clean_string_field(data.get("proporcion_cable"), max_len=30)
    if not proporcion_cable or proporcion_cable not in {k for k, _ in PROPORCION_CABLE_BATERIA}:
        errores["proporcion_cable"] = "Indicá la proporción entre herramientas a cable y batería."

    # CONTRADICCIONES LÓGICAS: Si no usa batería, la cantidad debe ser 0 y el uso 100% cable
    if "no_usa" in plataformas_in:
        if cantidad_baterias not in ("0", "no_responde"):
            errores["plataforma_bateria"] = "Si no usás batería, la cantidad de baterías debe ser 0."
        if proporcion_cable not in ("100_cable", "no_responde"):
            errores["proporcion_cable"] = "Si no usás batería, el uso no puede ser mayormente a batería."

    canal_compra = clean_string_field(data.get("canal_compra"), max_len=40)
    if not canal_compra or canal_compra not in {k for k, _ in CANALES_COMPRA}:
        errores["canal_compra"] = "Seleccioná tu canal de compra habitual."

    canal_otro = clean_string_field(data.get("canal_otro"), max_len=80) or ""

    reparaciones_12m = clean_string_field(data.get("reparaciones_12m"), max_len=30)
    if not reparaciones_12m or reparaciones_12m not in {k for k, _ in REPARACIONES_12M}:
        errores["reparaciones_12m"] = "Indicá si realizaste reparaciones en los últimos 12 meses."

    falla_frecuente = clean_string_field(data.get("falla_frecuente"), max_len=40)
    if not falla_frecuente or falla_frecuente not in {k for k, _ in FALLAS_FRECUENTES}:
        errores["falla_frecuente"] = "Indicá si hubo fallas, elegí No sé si no podés responder."

    falla_otra = clean_string_field(data.get("falla_otra"), max_len=80) or ""

    proxima_herramienta = clean_string_field(data.get("proxima_herramienta"), max_len=40)
    if not proxima_herramienta or proxima_herramienta not in {k for k, _ in PROXIMA_HERRAMIENTA}:
        errores["proxima_herramienta"] = "Seleccioná la próxima herramienta que pensás comprar o renovar."

    proxima_otra = clean_string_field(data.get("proxima_otra"), max_len=80) or ""

    horizonte_compra = clean_string_field(data.get("horizonte_compra"), max_len=30)
    if horizonte_compra and horizonte_compra not in {k for k, _ in HORIZONTES_COMPRA}:
        errores['horizonte_compra'] = 'Seleccioná un plazo de la lista.'
    elif not horizonte_compra:
        horizonte_compra = "sin_fecha"

    for name, selected, other in (("oficio", oficio == "otro", oficio_otro), ("marca_principal", marca_principal == "Otra marca", marca_otra), ("plataforma_bateria", "otra" in plataformas_in, plataforma_otra), ("canal_compra", canal_compra == "otro", canal_otro), ("falla_frecuente", falla_frecuente == "otra", falla_otra), ("proxima_herramienta", proxima_herramienta == "otra", proxima_otra)):
        if selected and not other:
            errores[name] = "Especificá la opción Otra."
    limits = {'oficio_otro':80, 'marca_otra':80, 'plataforma_otra':80, 'canal_otro':80,
              'falla_otra':80, 'proxima_otra':80, 'contacto_nombre':80, 'resena_modelo':100,
              'resena_tiempo':50, 'resena_intensidad':50, 'resena_ventajas':1000,
              'resena_problemas':1000, 'resena_reparaciones':500, 'resena_recomienda':20,
              'resena_foto_nombre':100}
    for key, value in data.items():
        if key in limits and value is not None and not isinstance(value,str):
            errores[key] = 'El campo debe contener texto.'
        elif isinstance(value,str) and len(value.strip()) > limits.get(key,120):
            errores[key] = 'El texto supera el límite permitido. Acortalo antes de enviar.'

    # 5. Consentimientos y validación estricta de booleanos
    consent_rep, valid_rep = parse_strict_bool(data.get("consent_report"), default=False)
    consent_com, valid_com = parse_strict_bool(data.get("consent_commercial"), default=False)
    consent_rev, valid_rev = parse_strict_bool(data.get("consent_review"), default=False)

    if not valid_rep or not valid_com or not valid_rev:
        errores["consentimientos"] = "Los valores de consentimiento deben ser booleanos."

    email_raw = data.get("contacto_email")
    if email_raw is not None and not isinstance(email_raw, str):
        errores["contacto_email"] = "El correo debe ser una cadena de texto."
        email = ""
    else:
        email = (email_raw or "").strip().lower()[:120]

    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errores["contacto_email"] = "Ingresá un correo electrónico válido o dejá el campo vacío."

    if (consent_rep or consent_com) and not email:
        errores["contacto_email"] = "Para recibir el informe o comunicaciones es necesario indicar un correo."

    # 6. Reseña opcional
    modelo_resena = clean_string_field(data.get("resena_modelo"), max_len=100) or ""
    if data.get('resena_recomienda') not in (None, '', 'si', 'tal_vez', 'no'):
        errores['resena_recomienda'] = 'Elegí una respuesta de la lista.'
    tiene_resena = bool(modelo_resena)
    resena_data: Optional[Dict[str, Any]] = None
    if tiene_resena and not any(data.get(k) for k in ('resena_ventajas', 'resena_problemas')):
        errores['resena_modelo'] = 'Agregá una experiencia concreta o dejá la reseña vacía.'
    if tiene_resena:
        resena_data = {
            "modelo_exacto": modelo_resena,
            "tiempo_uso": clean_string_field(data.get("resena_tiempo"), max_len=50) or "",
            "intensidad": clean_string_field(data.get("resena_intensidad"), max_len=50) or "",
            "ventajas": clean_string_field(data.get("resena_ventajas"), max_len=1000) or "",
            "problemas": clean_string_field(data.get("resena_problemas"), max_len=1000) or "",
            "reparaciones": clean_string_field(data.get("resena_reparaciones"), max_len=500) or "",
            "volveria_a_comprar": clean_string_field(data.get("resena_recomienda"), max_len=20) or "",
            "foto_referencia": clean_string_field(data.get("resena_foto_nombre"), max_len=100) or "",
            "aprobada_publicacion": False,
            "tipo_evaluacion": "experiencia_declarada",
        }

    if errores:
        return False, errores, 400

    # 7. Detección de posibles anomalías para moderación asistida
    motivos_revision: List[str] = []
    if motivo_tiempo:
        motivos_revision.append(motivo_tiempo)
    if es_spam_honeypot:
        motivos_revision.append("honeypot_completado")
    if es_envio_ultrarrapido:
        motivos_revision.append(f"envio_muy_rapido_{tiempo_llenado_segundos:.1f}s")

    fingerprint_hash = hashlib.sha256(f"{client_ip}::{user_agent}".encode("utf-8")).hexdigest()[:16]

    respuestas_previas = cargar_respuestas_analiticas()
    for prev in respuestas_previas[-50:]:
        if prev.get("fingerprint") == fingerprint_hash:
            motivos_revision.append("huella_ip_navegador_repetida_reciente")
            break

    if email:
        contactos_previos = cargar_contactos()
        for c in contactos_previos:
            if c.get("email") == email:
                motivos_revision.append("email_ya_registrado")
                break

    estado_inicial = "revision_pendiente" if motivos_revision else "valida"

    datos_analiticos = {
        "oficio": oficio,
        "oficio_otro": oficio_otro,
        "provincia": provincia,
        "tipo_uso": tipo_uso,
        "intensidad": intensidad,
        "marca_principal": marca_principal,
        "marca_otra": marca_otra,
        "plataformas_bateria": plataformas_in,
        "plataforma_otra": plataforma_otra,
        "cantidad_baterias": cantidad_baterias,
        "proporcion_cable": proporcion_cable,
        "canal_compra": canal_compra,
        "canal_otro": canal_otro,
        "reparaciones_12m": reparaciones_12m,
        "falla_frecuente": falla_frecuente,
        "falla_otra": falla_otra,
        "proxima_herramienta": proxima_herramienta,
        "proxima_otra": proxima_otra,
        "horizonte_compra": horizonte_compra,
        "tiempo_llenado_segundos": round(tiempo_llenado_segundos, 1) if tiempo_llenado_segundos else None,
        "fingerprint": fingerprint_hash,
        "utm_source": (clean_string_field(data.get("utm_source"), max_len=50) or "organico_directo"),
        "utm_medium": clean_string_field(data.get("utm_medium"), max_len=50) or "",
        "utm_campaign": clean_string_field(data.get("utm_campaign"), max_len=50) or "",
        "utm_content": clean_string_field(data.get("utm_content"), max_len=50) or "",
        "consent_review": consent_rev,
        "estado": estado_inicial,
        "motivos_revision": motivos_revision,
        "tiene_resena": tiene_resena,
    }
    if resena_data:
        datos_analiticos["resena"] = resena_data

    # Contacto: se guarda SIEMPRE el registro de consentimientos aunque no haya email
    datos_contacto = {
        "email": email,
        "nombre": clean_string_field(data.get("contacto_nombre"), max_len=80) or "",
        "consent_report": consent_rep,
        "consent_commercial": consent_com,
        "consent_review": consent_rev,
    }

    response_id = guardar_respuesta_y_contacto(datos_analiticos, datos_contacto)

    return True, {
        "response_id": response_id,
        "proxima_herramienta": proxima_herramienta,
        "guias_recomendadas": GUIAS_RECOMENDADAS_POR_HERRAMIENTA.get(proxima_herramienta, GUIAS_RECOMENDADAS_POR_HERRAMIENTA["ninguna"]),
        "estado": estado_inicial,
    }, 200


# --- DATASET DE DEMOSTRACIÓN ROTULADO ---

def generar_dataset_demo_rotulado() -> List[Dict[str, Any]]:
    """Genera 35 respuestas simuladas de demostración rotuladas de forma explícita."""
    provincias_demo = ["Buenos Aires", "CABA", "Córdoba", "Santa Fe", "Mendoza", "Entre Ríos", "Neuquén"]
    oficios_demo = ["herreria", "carpinteria", "mecanica", "electricidad", "plomeria", "construccion", "mantenimiento", "hobista"]
    marcas_demo = ["Bosch", "DeWalt", "Makita", "Einhell", "Gamma", "Lüsqtoff", "Stanley", "Total"]
    baterias_demo = [["bosch_18v"], ["dewalt_20v"], ["makita_lxt_18v"], ["einhell_pxc"], ["no_usa"], ["lusqtoff_18v"]]
    proximas_demo = ["taladro", "amoladora", "soldadora", "compresor", "hidrolavadora", "sierra"]

    dataset = []
    for i in range(1, 36):
        of = oficios_demo[i % len(oficios_demo)]
        pr = provincias_demo[i % len(provincias_demo)]
        ma = marcas_demo[i % len(marcas_demo)]
        ba = baterias_demo[i % len(baterias_demo)]
        px = proximas_demo[i % len(proximas_demo)]
        fuente = ["ferreterias", "docentes-cfp", "organico_directo", "asociaciones", "creadores"][i % 5]

        resp = {
            "response_id": f"demo-{i:03d}",
            "timestamp": "2026-10-01T12:00:00+00:00",
            "es_dato_simulado_demo": True,
            "oficio": of,
            "oficio_otro": "",
            "provincia": pr,
            "tipo_uso": "profesional" if i % 2 == 0 else "domestico",
            "intensidad": "diario_intensivo" if i % 3 == 0 else "semanal",
            "marca_principal": ma,
            "marca_otra": "",
            "plataformas_bateria": ba,
            "plataforma_bateria": ba[0],
            "plataforma_otra": "",
            "cantidad_baterias": "2" if ba[0] != "no_usa" else "0",
            "proporcion_cable": "50_50" if ba[0] != "no_usa" else "100_cable",
            "canal_compra": "mercadolibre" if i % 2 == 0 else "ferreteria_local",
            "canal_otro": "",
            "reparaciones_12m": "1" if i % 2 == 0 else "0",
            "falla_frecuente": "carbones" if i % 2 == 0 else "ninguna",
            "falla_otra": "",
            "proxima_herramienta": px,
            "proxima_otra": "",
            "horizonte_compra": "30_dias" if i % 2 == 0 else "90_dias",
            "utm_source": fuente,
            "utm_medium": "demo",
            "utm_campaign": "piloto",
            "estado": "valida",
            "motivos_revision": [],
            "consent_review": True,
            "tiene_resena": (i % 3 == 0),
        }
        if i % 3 == 0:
            resp["resena"] = {
                "modelo_exacto": f"{ma} Mod-{100 + i}",
                "tiempo_uso": "1 a 2 años",
                "intensidad": "Diario en taller",
                "ventajas": "Buena potencia, peso balanceado y arranque suave.",
                "problemas": "Se calienta tras 40 minutos seguidos de corte intenso.",
                "reparaciones": "Cambio preventivo de carbones a los 10 meses.",
                "volveria_a_comprar": "Sí",
                "aprobada_publicacion": True,
                "tipo_evaluacion": "experiencia_declarada",
            }
        dataset.append(resp)
    return dataset


# --- ESTADÍSTICAS Y MÉTRICAS DE MUESTRA ---

def calcular_estadisticas(incluir_demo: bool = False) -> Dict[str, Any]:
    """Calcula totales, distribuciones y métricas del relevamiento."""
    if incluir_demo:
        respuestas = generar_dataset_demo_rotulado()
        es_muestra_demo = True
    else:
        respuestas = [r for r in cargar_respuestas_analiticas() if not r.get("es_demo")]
        es_muestra_demo = False

    abandonos = [] if incluir_demo else cargar_abandonos()
    sessions = {}
    for event in abandonos:
        if event.get('session_id'):
            sessions.setdefault(event['session_id'], []).append(event)
    started = [events for events in sessions.values() if any(e['paso'] == 'start' for e in events)]
    completed = [events for events in started if any(e['paso'] == 'completed' for e in events)]
    cutoff = time.time() - 86400
    abandoned = [events for events in started if not any(e['paso'] == 'completed' for e in events) and max(datetime.fromisoformat(e['at']).timestamp() for e in events) < cutoff]
    sesiones_por_fuente = {}
    for events in started:
        source = next(e for e in events if e['paso'] == 'start')['utm'].get('source') or 'directo'
        group = sesiones_por_fuente.setdefault(source, {'iniciadas':0, 'completadas':0})
        group['iniciadas'] += 1
        group['completadas'] += int(any(e['paso'] == 'completed' for e in events))

    total_recibidas = len(respuestas)
    validas = [r for r in respuestas if r.get("estado") == "valida"]
    pendientes = [r for r in respuestas if r.get("estado") == "revision_pendiente"]
    descartadas = [r for r in respuestas if r.get("estado") == "descartada"]

    n_validas = len(validas)

    def frecuencias(campo: str) -> Dict[str, int]:
        conteo: Dict[str, int] = {}
        for r in validas:
            val = r.get(campo, "no_informado")
            conteo[val] = conteo.get(val, 0) + 1
        return conteo

    por_oficio = frecuencias("oficio")
    por_provincia = frecuencias("provincia")
    por_marca = frecuencias("marca_principal")
    por_proporcion = frecuencias("proporcion_cable")
    por_canal = frecuencias("canal_compra")
    por_proxima = frecuencias("proxima_herramienta")

    # Plataformas: permite contabilizar selección múltiple
    por_plataforma: Dict[str, int] = {}
    for r in validas:
        plats = r.get("plataformas_bateria") or [r.get("plataforma_bateria", "no_usa")]
        for p in plats:
            por_plataforma[p] = por_plataforma.get(p, 0) + 1

    por_fuente: Dict[str, int] = {}
    for r in respuestas:
        src = r.get("utm_source", "organico_directo")
        por_fuente[src] = por_fuente.get(src, 0) + 1

    resenas = [r.get("resena") for r in respuestas if r.get("resena")]

    return {
        "es_muestra_demo": es_muestra_demo,
        "total_recibidas": total_recibidas,
        "n_validas": n_validas,
        "n_pendientes": len(pendientes),
        "n_descartadas": len(descartadas),
        "total_abandonos": len(abandoned),
        "sesiones_iniciadas": len(started),
        "sesiones_completadas": len(completed),
        "completitud": round(100 * len(completed) / len(started), 1) if started else None,
        "respuestas": respuestas,
        "sesiones_por_fuente": sesiones_por_fuente,
        "total_resenas": len(resenas),
        "meta_inicial": 100,
        "porcentaje_meta": min(100.0, round((n_validas / 100.0) * 100, 1)),
        "por_oficio": por_oficio,
        "por_provincia": por_provincia,
        "por_marca": por_marca,
        "por_plataforma": por_plataforma,
        "por_proporcion": por_proporcion,
        "por_canal": por_canal,
        "por_proxima": por_proxima,
        "por_fuente": por_fuente,
        "pendientes_moderacion": pendientes,
        "ultimas_respuestas": respuestas[-20:][::-1],
    }


# --- RENDERIZADO DE VISTAS PÚBLICAS ---

def render_relevamiento_page(query_params: Optional[Dict[str, str]] = None) -> str:
    """Renderiza el cuerpo principal de la landing y formulario (/relevamiento-2027/)."""
    if not relevamiento_abierto():
        return '<section class="relevamiento-wrapper"><h1>Relevamiento TallerLab 2027</h1><p>Estamos preparando el piloto. La participación todavía no está abierta.</p><a href="/relevamiento-2027/metodologia/">Conocé la metodología</a></section>'
    params = query_params or {}
    utm_source = escape(params.get("utm_source", ""), quote=True)
    utm_medium = escape(params.get("utm_medium", ""), quote=True)
    utm_campaign = escape(params.get("utm_campaign", ""), quote=True)
    utm_content = escape(params.get("utm_content", ""), quote=True)

    def options_html(lista: List[Tuple[str, str]], selected: str = "") -> str:
        out = []
        for val, label in lista:
            sel = ' selected="selected"' if val == selected else ""
            out.append(f'<option value="{escape(val, quote=True)}"{sel}>{escape(label)}</option>')
        return "\n".join(out)

    def simple_options(lista: List[str], selected: str = "") -> str:
        out = []
        for val in lista:
            sel = ' selected="selected"' if val == selected else ""
            out.append(f'<option value="{escape(val, quote=True)}"{sel}>{escape(val)}</option>')
        return "\n".join(out)

    content = f"""
    <div class="relevamiento-wrapper" style="max-width: 860px; margin: 0 auto; padding: 1.5rem 1rem 4rem;">
      <nav class="breadcrumb" aria-label="Ubicación" style="margin-bottom: 1.5rem;">
        <a href="/">Inicio</a><span>/</span><span>Relevamiento 2027</span>
      </nav>

      <header class="relevamiento-header" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 2rem 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.75rem;">
          <span style="background: var(--orange); color: #fff; font-size: 0.75rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 6px; letter-spacing: 0.05em; text-transform: uppercase;">Piloto de Investigación</span>
          <span style="color: var(--text-muted); font-size: 0.85rem;">Duración a medir durante el piloto</span>
        </div>
        <h1 style="font-size: 1.85rem; font-weight: 800; line-height: 1.25; margin-bottom: 0.75rem; color: var(--text);">
          Relevamiento TallerLab 2027: herramientas y oficios en Argentina
        </h1>
        <p style="color: var(--text); font-size: 0.98rem; line-height: 1.6; margin-bottom: 1.25rem;">
          Conocé qué herramientas se usan realmente en los talleres, obras y hogares del país, qué marcas declaran usar los participantes de cada oficio, cómo avanza la transición a batería y qué fallas obligan a reparar equipos en el mercado argentino.
        </p>

        <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; padding: 0.85rem 1rem; font-size: 0.85rem; color: var(--text-muted); line-height: 1.5;">
          <strong style="color: var(--text);">Privacidad y Ley 25.326:</strong>
          Relevamiento voluntario y seudonimizado. Podés participar sin dejar correo electrónico; las respuestas técnicas se procesan de forma agregada para el estudio. Si optás por recibir el informe o novedades, tu dirección se almacena en una tabla separada, vinculada mediante un identificador interno, garantizando tus derechos de acceso, rectificación y supresión. Consultá nuestro <a href="/relevamiento-2027/metodologia/" style="color: var(--orange); text-decoration: underline;">borrador de metodología pública</a>.
        </div>
      </header>

      <div id="survey-container" style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 2rem 1.5rem;">
        
        <noscript><p>Activá JavaScript para responder. No enviaremos tus respuestas por la URL.</p></noscript>
        <form id="relevamiento-form" method="POST" action="/api/relevamiento/submit" novalidate>
          <input type="hidden" name="form_start_timestamp" id="form_start_timestamp" value="">
          <input type="hidden" name="utm_source" value="{utm_source}">
          <input type="hidden" name="utm_medium" value="{utm_medium}">
          <input type="hidden" name="utm_campaign" value="{utm_campaign}">
          <input type="hidden" name="utm_content" value="{utm_content}">
          
          <div style="position: absolute; left: -9999px; top: -9999px; height: 0; width: 0; overflow: hidden;" aria-hidden="true">
            <label for="empresa_rubro_hidden">No completar este campo:</label>
            <input type="text" name="empresa_rubro_hidden" id="empresa_rubro_hidden" tabindex="-1" autocomplete="off">
          </div>

          <!-- SECCIÓN 1: Perfil y Localización -->
          <fieldset style="border: none; margin: 0 0 2rem; padding: 0;">
            <legend style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; width: 100%;">
              <span style="color: var(--orange);">01.</span> Perfil del taller y ubicación
            </legend>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="oficio" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Oficio o actividad principal <span style="color: var(--orange);">*</span>
              </label>
              <select id="oficio" name="oficio" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná una opción --</option>
                {options_html(OFICIOS)}
              </select>
              <div id="oficio_otro_wrap" style="display: none; margin-top: 0.5rem;">
                <input type="text" id="oficio_otro" aria-label="Detalle de otra opción" maxlength="80" name="oficio_otro" placeholder="¿Cuál es tu oficio o actividad?" style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.9rem;">
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="provincia" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Provincia donde trabajás o residís <span style="color: var(--orange);">*</span>
              </label>
              <select id="provincia" name="provincia" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná tu provincia --</option>
                {simple_options(PROVINCIAS)}
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="tipo_uso" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                ¿El uso de tus herramientas es comercial o doméstico? <span style="color: var(--orange);">*</span>
              </label>
              <select id="tipo_uso" name="tipo_uso" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná tipo de uso --</option>
                {options_html(TIPOS_USO)}
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="intensidad" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Intensidad y frecuencia de uso <span style="color: var(--orange);">*</span>
              </label>
              <select id="intensidad" name="intensidad" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná frecuencia --</option>
                {options_html(INTENSIDADES_USO)}
              </select>
            </div>
          </fieldset>

          <!-- SECCIÓN 2: Equipamiento, Marcas y Baterías -->
          <fieldset style="border: none; margin: 0 0 2rem; padding: 0;">
            <legend style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; width: 100%;">
              <span style="color: var(--orange);">02.</span> Marcas, alimentación y baterías
            </legend>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="marca_principal" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Marca principal o más frecuente en tu taller <span style="color: var(--orange);">*</span>
              </label>
              <select id="marca_principal" name="marca_principal" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná la marca principal --</option>
                {simple_options(MARCAS_PRINCIPALES)}
              </select>
              <div id="marca_otra_wrap" style="display: none; margin-top: 0.5rem;">
                <input type="text" id="marca_otra" aria-label="Detalle de otra opción" maxlength="80" name="marca_otra" placeholder="Indicá cuál es la otra marca" style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.9rem;">
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <p id="plataformas-titulo" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Plataformas de batería que utilizás (seleccioná todas) <span style="color: var(--orange);">*</span>
              </p>
              <div id="plataforma_bateria" class="survey-platforms" role="group" aria-labelledby="plataformas-titulo">
                {''.join('<label><input type="checkbox" name="plataformas_bateria" value="' + escape(k, quote=True) + '"> ' + escape(label) + '</label>' for k, label in PLATAFORMAS_BATERIA)}
              </div>
              <div id="plataforma_otra_wrap" style="display: none; margin-top: 0.5rem;">
                <input type="text" id="plataforma_otra" aria-label="Detalle de otra opción" maxlength="80" name="plataforma_otra" placeholder="¿Qué otra plataforma o voltaje usás?" style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.9rem;">
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="cantidad_baterias" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                ¿Cuántas baterías compatibles tenés activas en uso? <span style="color: var(--orange);">*</span>
              </label>
              <select id="cantidad_baterias" name="cantidad_baterias" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Cantidad de baterías --</option>
                {options_html(CANTIDAD_BATERIAS)}
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="proporcion_cable" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Tiempo de uso de herramientas eléctricas: ¿cable o batería? <span style="color: var(--orange);">*</span>
              </label>
              <select id="proporcion_cable" name="proporcion_cable" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná proporción --</option>
                {options_html(PROPORCION_CABLE_BATERIA)}
              </select>
            </div>
          </fieldset>

          <!-- SECCIÓN 3: Compras y Reparaciones -->
          <fieldset style="border: none; margin: 0 0 2rem; padding: 0;">
            <legend style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; width: 100%;">
              <span style="color: var(--orange);">03.</span> Canal de compra, reparaciones y planes
            </legend>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="canal_compra" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Canal habitual donde comprás tus herramientas <span style="color: var(--orange);">*</span>
              </label>
              <select id="canal_compra" name="canal_compra" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná canal de compra --</option>
                {options_html(CANALES_COMPRA)}
              </select>
              <div id="canal_otro_wrap" style="display: none; margin-top: 0.5rem;">
                <input type="text" id="canal_otro" aria-label="Detalle de otra opción" maxlength="80" name="canal_otro" placeholder="¿Cuál es tu canal de compra?" style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.9rem;">
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="reparaciones_12m" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                ¿Cuántas reparaciones tuviste en los últimos 12 meses? <span style="color: var(--orange);">*</span>
              </label>
              <select id="reparaciones_12m" name="reparaciones_12m" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Cantidad de reparaciones --</option>
                {options_html(REPARACIONES_12M)}
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="falla_frecuente" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Si tuviste roturas, ¿cuál fue el componente que más falló?
              </label>
              <select id="falla_frecuente" name="falla_frecuente" style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Indicá falla, ninguna o No sé --</option>
                {options_html(FALLAS_FRECUENTES)}
              </select>
              <div id="falla_otra_wrap" style="display:none; margin-top:.5rem"><label for="falla_otra">Otra falla</label><input id="falla_otra" name="falla_otra" maxlength="80" style="width:100%; padding:.7rem; background:var(--bg-surface); color:var(--text); border:1px solid var(--border)"></div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="proxima_herramienta" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                ¿Cuál es la próxima herramienta que pensás comprar o renovar? <span style="color: var(--orange);">*</span>
              </label>
              <select id="proxima_herramienta" name="proxima_herramienta" required style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                <option value="">-- Seleccioná próxima herramienta --</option>
                {options_html(PROXIMA_HERRAMIENTA)}
              </select>
              <div id="proxima_otra_wrap" style="display: none; margin-top: 0.5rem;">
                <input type="text" id="proxima_otra" aria-label="Detalle de otra opción" maxlength="80" name="proxima_otra" placeholder="¿Qué herramienta estás buscando?" style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.9rem;">
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="horizonte_compra" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--text);">
                Plazo estimado para esa compra
              </label>
              <select id="horizonte_compra" name="horizonte_compra" style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
                {options_html(HORIZONTES_COMPRA)}
              </select>
            </div>
          </fieldset>

          <!-- SECCIÓN 4: Reseña Opcional -->
          <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
              <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--text); margin: 0;">
                ⭐ Reseña de una herramienta de tu taller (Opcional)
              </h3>
              <span style="font-size: 0.75rem; background: var(--border); padding: 0.2rem 0.5rem; border-radius: 4px; color: var(--text-muted);">Sin compromiso</span>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.45;">
              Contanos tu experiencia con un modelo puntual. En TallerLab etiquetamos estas aportaciones como <em>«Experiencia declarada por el usuario»</em> (no las catalogamos como «compra verificada» sin comprobante documental).
            </p>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="resena_modelo" style="display: block; font-size: 0.88rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem;">Marca y modelo exacto:</label>
              <input type="text" id="resena_modelo" name="resena_modelo" placeholder="Ej: Bosch GWS 770, Lüsqtoff Iron-100, DeWalt DCD771" style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.9rem;">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem;">
              <div>
                <label for="resena_tiempo" style="display: block; font-size: 0.85rem; color: var(--text); margin-bottom: 0.3rem;">Tiempo de uso:</label>
                <input type="text" id="resena_tiempo" name="resena_tiempo" placeholder="Ej: 8 meses, 3 años" style="width: 100%; padding: 0.6rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.88rem;">
              </div>
              <div>
                <label for="resena_recomienda" style="display: block; font-size: 0.85rem; color: var(--text); margin-bottom: 0.3rem;">¿Volverías a comprarlo?</label>
                <select id="resena_recomienda" name="resena_recomienda" style="width: 100%; padding: 0.6rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.88rem;">
                  <option value="">-- Elegir --</option>
                  <option value="si">Sí, totalmente</option>
                  <option value="tal_vez">Tal vez / depende el precio</option>
                  <option value="no">No, buscaría otra alternativa</option>
                </select>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="resena_ventajas" style="display: block; font-size: 0.85rem; color: var(--text); margin-bottom: 0.3rem;">Puntos fuertes o ventajas:</label>
              <textarea id="resena_ventajas" name="resena_ventajas" rows="2" placeholder="Potencia real, peso balanceado, precisión..." style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.88rem; resize: vertical;"></textarea>
            </div>

            <div class="form-group" style="margin-bottom: 1rem;">
              <label for="resena_problemas" style="display: block; font-size: 0.85rem; color: var(--text); margin-bottom: 0.3rem;">Problemas o roturas:</label>
              <textarea id="resena_problemas" name="resena_problemas" rows="2" placeholder="Juego en mandril, calentamiento, cable rígido..." style="width: 100%; padding: 0.65rem 0.85rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.88rem; resize: vertical;"></textarea>
            </div>

            <div class="form-group">
              <label for="resena_reparaciones" style="display: block; font-size: 0.85rem; color: var(--text); margin-bottom: 0.3rem;">Reparaciones que le hiciste:</label>
              <input type="text" id="resena_reparaciones" name="resena_reparaciones" placeholder="Ej: cambio preventivo de carbones, nada..." style="width: 100%; padding: 0.6rem 0.75rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.88rem;">
            </div>
          </div>

          <!-- SECCIÓN 5: Consentimientos y Privacidad -->
          <fieldset style="border: none; margin: 0 0 2rem; padding: 0;">
            <legend style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; width: 100%;">
              <span style="color: var(--orange);">04.</span> Consentimientos y envío del informe
            </legend>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label for="contacto_email" style="display: block; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.3rem; color: var(--text);">
                Correo electrónico (Opcional)
              </label>
              <p style="font-size: 0.83rem; color: var(--text-muted); margin-bottom: 0.5rem;">
                Solo necesario si querés recibir el informe final o comunicarte con nosotros. No publicamos correos ni compartimos bases de datos.
              </p>
              <input type="email" id="contacto_email" name="contacto_email" placeholder="tu_correo@ejemplo.com" style="width: 100%; padding: 0.7rem 0.85rem; background: var(--bg-surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 0.95rem;">
            </div>

            <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.1rem; display: flex; flex-direction: column; gap: 0.9rem;">
              
              <label style="display: flex; align-items: flex-start; gap: 0.65rem; font-size: 0.88rem; color: var(--text); cursor: pointer; line-height: 1.45;">
                <input type="checkbox" name="consent_report" id="consent_report" value="1" style="margin-top: 0.2rem; accent-color: var(--orange); width: 18px; height: 18px;">
                <span><strong>Informe final:</strong> Deseo recibir por correo el informe de resultados cuando se procese la muestra.</span>
              </label>

              <label style="display: flex; align-items: flex-start; gap: 0.65rem; font-size: 0.88rem; color: var(--text); cursor: pointer; line-height: 1.45;">
                <input type="checkbox" name="consent_commercial" id="consent_commercial" value="1" style="margin-top: 0.2rem; accent-color: var(--orange); width: 18px; height: 18px;">
                <span><strong>Comunicaciones editoriales y comerciales:</strong> Acepto recibir guías, novedades y ofertas de TallerLab por correo. Puedo solicitar la baja.</span>
              </label>

              <label style="display: flex; align-items: flex-start; gap: 0.65rem; font-size: 0.88rem; color: var(--text); cursor: pointer; line-height: 1.45;">
                <input type="checkbox" name="consent_review" id="consent_review" value="1" style="margin-top: 0.2rem; accent-color: var(--orange); width: 18px; height: 18px;">
                <span><strong>Publicación de reseña:</strong> Si dejé una opinión, autorizo a citarla en las guías de forma anonimizada (solo con oficio y provincia).</span>
              </label>

            </div>
          </fieldset>

          <div id="form-error-msg" role="alert" tabindex="-1" aria-live="polite" style="display: none; background: rgba(225,29,72,0.15); border: 1px solid #e11d48; color: #9f1239; padding: 0.85rem 1rem; border-radius: 8px; font-size: 0.9rem; margin-bottom: 1.5rem;"></div>

          <div style="text-align: center; margin-top: 1rem;">
            <button type="submit" id="submit-btn" style="background: var(--orange); color: #fff; border: none; font-size: 1.05rem; font-weight: 700; padding: 0.95rem 2.5rem; border-radius: 9px; cursor: pointer; width: 100%; max-width: 380px;">
              Enviar respuestas al relevamiento →
            </button>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.75rem;">
              Podés participar sin suscribirte. No compartimos tus datos identificables.
            </p>
          </div>
        </form>

        <!-- Pantalla de confirmación post-envío -->
        <div id="survey-success" tabindex="-1" role="status" style="display: none; text-align: left; padding: 1rem 0;">
          <div style="background: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
              <span style="font-size: 1.6rem;">✅</span>
              <h2 style="font-size: 1.4rem; font-weight: 800; color: #166534; margin: 0;">¡Muchas gracias por participar!</h2>
            </div>
            <p style="color: var(--text); font-size: 0.95rem; line-height: 1.5; margin: 0;">
              Tu experiencia ya fue registrada en la base del piloto. Cada respuesta nos ayuda a construir un panorama honesto y fundamentado de las herramientas que realmente se usan en Argentina.
            </p>
          </div>

          <div id="guias-sugeridas-wrap" style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">
              📚 Guías de TallerLab para tu próxima compra
            </h3>
            <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.25rem;">
              Como mencionaste que tu próxima adquisición o renovación está en esta categoría, te dejamos nuestras investigaciones documentales:
            </p>
            <ul id="lista-guias-recomendadas" style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.75rem;">
            </ul>
          </div>

          <p id="survey-receipt" style="overflow-wrap:anywhere"></p>
          <div style="text-align: center; margin-top: 1.5rem;">
            <a href="/" style="display: inline-block; background: var(--bg-surface); border: 1px solid var(--border); color: var(--text); padding: 0.7rem 1.4rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem; text-decoration: none;">
              Volver a la portada de TallerLab
            </a>
          </div>
        </div>

      </div>
    </div>

    <!-- Script de interacción, telemetría y envío asíncrono -->
    <script>
      (function() {{
        var startTimeInput = document.getElementById('form_start_timestamp');
        if (startTimeInput) {{
          startTimeInput.value = (Date.now() / 1000).toString();
        }}

        var surveySession = crypto.randomUUID ? crypto.randomUUID() : 'session-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
        var sentStages = new Set();
        var surveyCompleted = false;
        function registrarPaso(stage) {{
          if (sentStages.has(stage)) return;
          sentStages.add(stage);
          var body = JSON.stringify({{paso: stage, session_id: surveySession, utm: {{source: '{utm_source}', medium: '{utm_medium}', campaign: '{utm_campaign}', content: '{utm_content}'}}}});
          if (navigator.sendBeacon) navigator.sendBeacon('/api/relevamiento/abandon', new Blob([body], {{type: 'application/json'}}));
          else fetch('/api/relevamiento/abandon', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:body, keepalive:true}});
        }}
        var formRoot = document.getElementById('relevamiento-form');
        formRoot.addEventListener('input', function() {{registrarPaso('start');}}, {{once:true}});
        formRoot.addEventListener('change', function() {{registrarPaso('start');}}, {{once:true}});
        window.addEventListener('pagehide', function() {{if (!surveyCompleted && sentStages.has('start')) registrarPaso('exit');}});
        document.querySelectorAll('[name="plataformas_bateria"]').forEach(function(box) {{
          box.addEventListener('change', function() {{
            if (box.checked) document.querySelectorAll('[name="plataformas_bateria"]').forEach(function(other) {{
              if (other !== box && (['no_usa','no_sabe'].includes(box.value) || ['no_usa','no_sabe'].includes(other.value))) other.checked = false;
            }});
            document.getElementById('plataforma_otra_wrap').style.display = document.querySelector('[name="plataformas_bateria"][value="otra"]').checked ? 'block' : 'none';
            registrarPaso('equipment');
          }});
        }});

        function bindCond(selectId, wrapId, matchVal, pasoNombre) {{
          var sel = document.getElementById(selectId);
          var wrp = document.getElementById(wrapId);
          if (!sel) return;
          sel.addEventListener('change', function() {{
            if (pasoNombre) registrarPaso(pasoNombre);
            if (wrp) wrp.style.display = (sel.value === matchVal) ? 'block' : 'none';
          }});
        }}
        bindCond('oficio', 'oficio_otro_wrap', 'otro', 'profile');
        bindCond('provincia', null, null, 'profile');
        bindCond('marca_principal', 'marca_otra_wrap', 'Otra marca', 'equipment');
        bindCond('canal_compra', 'canal_otro_wrap', 'otro', 'purchase');
        bindCond('falla_frecuente', 'falla_otra_wrap', 'otra', 'equipment');
        bindCond('proxima_herramienta', 'proxima_otra_wrap', 'otra', 'purchase');

        var form = document.getElementById('relevamiento-form');
        var submitBtn = document.getElementById('submit-btn');
        var errorBox = document.getElementById('form-error-msg');
        var successBox = document.getElementById('survey-success');
        var guiasList = document.getElementById('lista-guias-recomendadas');

        if (form) {{
          form.addEventListener('submit', function(e) {{
            e.preventDefault();
            errorBox.style.display = 'none';
            errorBox.textContent = '';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Enviando respuestas...';

            var formData = new FormData(form);
            var payload = {{}};
            formData.forEach(function(value, key) {{
              payload[key] = value;
            }});

            payload['plataformas_bateria'] = formData.getAll('plataformas_bateria');
            payload['consent_report'] = document.getElementById('consent_report').checked;
            payload['consent_commercial'] = document.getElementById('consent_commercial').checked;
            payload['consent_review'] = document.getElementById('consent_review').checked;

            fetch('/api/relevamiento/submit', {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify(payload)
            }})
            .then(function(res) {{
              return res.json().then(function(data) {{
                return {{ status: res.status, data: data }};
              }}).catch(function() {{
                return {{ status: res.status, data: {{ ok: false, errores: {{ _global: 'Error en la respuesta del servidor.' }} }} }};
              }});
            }})
            .then(function(resObj) {{
              submitBtn.disabled = false;
              submitBtn.textContent = 'Enviar respuestas al relevamiento →';

              if (resObj.status !== 200) {{
                var msg = 'Ocurrió un error al procesar el formulario.';
                if (resObj.data && resObj.data.errores) {{
                  var items = [];
                  for (var k in resObj.data.errores) {{
                    items.push(resObj.data.errores[k]);
                  }}
                  msg = items.join(' | ');
                }} else if (resObj.data && resObj.data.error) {{
                  msg = resObj.data.error;
                }}
                errorBox.textContent = msg;
                errorBox.style.display = 'block';
                errorBox.focus();
                errorBox.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                return;
              }}

              document.getElementById('survey-receipt').textContent = 'Identificador de tu respuesta: ' + resObj.data.response_id + '. Guardalo para consultas o solicitudes de baja.';
              surveyCompleted = true;
              registrarPaso('completed');
              form.style.display = 'none';
              successBox.style.display = 'block';

              if (guiasList && resObj.data && resObj.data.guias_recomendadas) {{
                guiasList.innerHTML = '';
                resObj.data.guias_recomendadas.forEach(function(g) {{
                  var li = document.createElement('li');
                  li.innerHTML = '<a href="' + g[0] + '" style="color: var(--orange); font-weight: 600; text-decoration: underline; font-size: 0.95rem;">' + g[1] + ' →</a>';
                  guiasList.appendChild(li);
                }});
              }}
              successBox.focus();
              successBox.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }})
            .catch(function(err) {{
              submitBtn.disabled = false;
              submitBtn.textContent = 'Enviar respuestas al relevamiento →';
              errorBox.textContent = 'Error de conexión. Verificá tu red e intentá nuevamente.';
              errorBox.style.display = 'block';
            }});
          }});
        }}
      }})();
    </script>
    """
    return content


def render_metodologia_page() -> str:
    """Renderiza el borrador público de metodología (/relevamiento-2027/metodologia/)."""
    return """
    <article class="articulo-contenido" style="max-width: 820px; margin: 0 auto; padding: 1.5rem 1rem 4rem;">
      <nav class="breadcrumb" aria-label="Ubicación" style="margin-bottom: 1.5rem;">
        <a href="/">Inicio</a><span>/</span><a href="/relevamiento-2027/">Relevamiento 2027</a><span>/</span><span>Metodología</span>
      </nav>

      <header style="margin-bottom: 2rem;">
        <div style="font-size: 0.8rem; font-weight: 800; color: var(--orange); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
          Documento Editorial y Estadístico
        </div>
        <h1 style="font-size: 1.9rem; font-weight: 800; line-height: 1.25; margin-bottom: 0.75rem; color: var(--text);">
          Borrador de Metodología: Relevamiento TallerLab 2027
        </h1>
        <p style="color: var(--text-muted); font-size: 0.95rem;">
          Criterios de recolección, limitaciones estadísticas, filtros de calidad y principios de transparencia técnica para herramientas y oficios en Argentina.
        </p>
      </header>

      <section style="margin-bottom: 2rem;">
        <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 0.85rem;">
          1. Alcance y Carácter No Probabilístico
        </h2>
        <p>
          El <strong>Relevamiento TallerLab 2027</strong> es una iniciativa técnica y editorial destinada a recabar datos primarios sobre herramientas, plataformas de alimentación, fallas mecánicas y canales de adquisición en Argentina.
        </p>
        <div style="background: var(--bg-card); border-left: 4px solid var(--orange); padding: 1rem; border-radius: 4px; margin: 1rem 0; font-size: 0.9rem;">
          <strong>Limitación estadística fundamental:</strong>
          La muestra es <strong>no probabilística y por conveniencia</strong> (reclutamiento voluntario a través de lectores de TallerLab, comunidades de oficios, escuelas técnicas y ferreterías). En consecuencia:
          <ul style="margin: 0.5rem 0 0 1.25rem; line-height: 1.5;">
            <li>No se afirma representatividad estadística censal ni nacional sobre la totalidad de los talleres del país.</li>
            <li>No se publicará margen de error probabilístico ni generalizaciones censales estándar, ya que estos solo aplican a muestreos aleatorios formales.</li>
            <li><strong>Popularidad no equivale a calidad técnica:</strong> una marca puede ser más frecuente por precio, disponibilidad o crédito, sin que ello implique superioridad en durabilidad.</li>
          </ul>
        </div>
      </section>

      <section style="margin-bottom: 2rem;">
        <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 0.85rem;">
          2. Fases del Estudio y Meta Mínima de Control
        </h2>
        <p>
          Para salvaguardar la seriedad del proyecto, el estudio se estructura en dos fases:
        </p>
        <ul>
          <li><strong>Fase Piloto (Meta: 100 respuestas válidas):</strong> Evaluar la tasa de finalización, consistencia lógica interna, dispersión por oficios y calibración de los filtros anti-spam.</li>
          <li><strong>Fase Ampliada (300 a 500 respuestas):</strong> Solo se abrirá tras confirmar la calidad técnica del piloto y presentar los primeros resultados de prueba.</li>
        </ul>
      </section>

      <section style="margin-bottom: 2rem;">
        <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 0.85rem;">
          3. Tratamiento de Datos, Consentimientos y Ley 25.326
        </h2>
        <p>
          La privacidad de los participantes se implementa mediante separación estricta por diseño (Privacy by Design):
        </p>
        <ul>
          <li><strong>Seudonimización:</strong> Cada respuesta recibe un identificador UUID único. Los datos técnicos y los contactos se guardan en tablas separadas, vinculadas por ese identificador; no se promete anonimato total.</li>
          <li><strong>Consentimientos triples no premarcados:</strong> El participante decide libremente si desea recibir el informe final, comunicaciones editoriales y comerciales o autorizar la cita anonimizada de su reseña.</li>
          <li><strong>Derechos de acceso y rectificación:</strong> Bajo la Ley 25.326 de Protección de Datos Personales de la República Argentina, cualquier participante puede solicitar la consulta o baja de su correo escribiendo a nuestro canal de contacto editorial.</li>
        </ul>
      </section>

      <section style="margin-bottom: 2rem;">
        <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-bottom: 0.85rem;">
          4. Filtros de Calidad y Moderación Asistida
        </h2>
        <p>
          Para evitar sesgos maliciosos o respuestas automatizadas sin incurrir en descarte ciego desmedido:
        </p>
        <ul>
          <li><strong>Honeypot oculto:</strong> Formularios completados por bots en campos trampa son marcados para revisión.</li>
          <li><strong>Tiempo mínimo:</strong> Envíos con duración inverosímil (&lt; 5 segundos) se derivan a la cola de moderación.</li>
          <li><strong>Rate limiting por IP:</strong> Se limitan las solicitudes concurrentes para evitar inundación (flood), respondiendo con HTTP 429 antes de guardar otra respuesta; el contador se conserva en la base persistente.</li>
          <li><strong>Moderación humana obligatoria:</strong> Ninguna respuesta marcada es eliminada automáticamente; un editor de TallerLab revisa la coherencia del contenido antes de clasificarla.</li>
          <li><strong>Verificación de reseñas:</strong> Las opiniones de usuarios se etiquetan estrictamente como <em>«Experiencia declarada»</em> y nunca se aprueban para su cita si no cuentan con consentimiento afirmativo documentado.</li>
        </ul>
      </section>

      <footer style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border); font-size: 0.85rem; color: var(--text-muted);">
        Cuestionario y aviso: versión 2026-10-03-v1. Fechas de campo: pendientes de apertura y cierre. Antes de publicar resultados se informarán esas fechas, los canales y la cantidad de respuestas recibidas, excluidas y válidas. Equipo editorial de TallerLab.
      </footer>
    </article>
    """


def render_admin_dashboard(query_params: Optional[Dict[str, str]] = None) -> str:
    """
    Panel privado de administración y moderación (/relevamiento-2027/admin/).
    Muestra N visible en todos los grupos y diferencia claramente datos reales vs demo.
    """
    params = query_params or {}
    authenticated = params.get("_authenticated") is True
    csrf = escape(params.get("_csrf", ""), quote=True)
    config_key = get_admin_key()

    # Si la clave administrativa no está configurada, bloquear acceso
    if not config_key:
        return """
        <div style="max-width: 600px; margin: 4rem auto; padding: 2rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; text-align: center;">
          <h2 style="color: var(--text); margin-bottom: 0.75rem;">Panel Administrativo No Configurado</h2>
          <p style="color: var(--text-muted); font-size: 0.9rem;">
            La variable de entorno <code>RELEVAMIENTO_ADMIN_KEY</code> no ha sido definida en este entorno.
          </p>
        </div>
        """

    # Verificación de clave
    if not authenticated:
        return '<section class="survey-login"><h1>Panel privado</h1><form method="POST" action="/relevamiento-2027/admin/login"><input type="hidden" name="csrf_token" value="' + csrf + '"><label for="admin_key_input">Clave de acceso</label><input id="admin_key_input" type="password" name="key" required autocomplete="current-password"><button>Ingresar</button></form></section>'

    usar_demo = params.get("demo", "").strip() in ("1", "true")
    stats = calcular_estadisticas(incluir_demo=usar_demo)

    filas_sesiones = ''.join('<tr><td>' + escape(source) + '</td><td>' + str(group['iniciadas']) + '</td><td>' + str(group['completadas']) + '</td><td>' + str(round(100 * group['completadas'] / group['iniciadas'], 1)) + '%</td></tr>' for source, group in stats['sesiones_por_fuente'].items())
    # Banner de advertencia visual para datos simulados
    if stats["es_muestra_demo"]:
        demo_banner = """
        <div style="background: rgba(234,88,12,0.15); border: 2px solid var(--orange); border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <strong style="color: var(--orange); font-size: 0.95rem;">⚠️ Visualizando Muestra de Demostración (35 casos simulados)</strong>
            <p style="color: var(--text); font-size: 0.85rem; margin: 0.2rem 0 0 0;">Estos datos son sintéticos para ilustrar el comportamiento de los gráficos. N = 35.</p>
          </div>
          <div>
            <a href="/relevamiento-2027/admin/" style="font-size: 0.82rem; background: var(--orange); color: #fff; padding: 0.4rem 0.8rem; border-radius: 6px; text-decoration: none; font-weight: 700;">
              ← Volver a Datos Reales
            </a>
          </div>
        </div>
        """
    else:
        demo_banner = """
        <div style="background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #22c55e;"></span>
            <span style="font-size: 0.85rem; color: var(--text);"><strong>Modo Datos Reales Activo:</strong> Respuestas recolectadas en base de datos.</span>
          </div>
          <div>
            <a href="/relevamiento-2027/admin/?demo=1" style="font-size: 0.82rem; background: var(--bg-card); border: 1px solid var(--border); padding: 0.35rem 0.75rem; border-radius: 6px; color: var(--text-muted); text-decoration: none;">
              Ver ejemplo con muestra demo simulada (35 casos) →
            </a>
          </div>
        </div>
        """

    def render_bars(diccionario: Dict[str, int], total_base: int, max_items: int = 8) -> str:
        if not diccionario or total_base == 0:
            return '<p style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">Sin datos registrados aún en esta categoría.</p>'
        sorted_items = sorted(diccionario.items(), key=lambda x: x[1], reverse=True)[:max_items]
        out = []
        for key, count in sorted_items:
            pct = round((count / total_base) * 100, 1)
            label = key.replace("_", " ").capitalize()
            out.append(f"""
            <div style="margin-bottom: 0.65rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: var(--text); margin-bottom: 0.2rem;">
                <span>{escape(label)}</span>
                <span style="font-weight: 700;">{count} ({pct}%)</span>
              </div>
              <div style="height: 7px; background: var(--bg-surface); border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: {pct}%; background: var(--orange); border-radius: 4px;"></div>
              </div>
            </div>
            """)
        return "".join(out)

    # Tabla de moderación de respuestas sospechosas
    filas_pendientes = []
    for resp in stats["pendientes_moderacion"]:
        rid = resp.get("response_id", "")
        motivos = ", ".join(resp.get("motivos_revision", ["indeterminado"]))
        filas_pendientes.append(f"""
        <tr style="border-bottom: 1px solid var(--border); font-size: 0.85rem;">
          <td style="padding: 0.6rem 0.5rem; font-family: monospace; color: var(--text-muted);">{escape(rid[:8])}</td>
          <td style="padding: 0.6rem 0.5rem; color: var(--text);">{escape(resp.get("oficio", ""))} ({escape(resp.get("provincia", ""))})</td>
          <td style="padding: 0.6rem 0.5rem; color: #f87171;">{escape(motivos)}</td>
          <td style="padding: 0.6rem 0.5rem; text-align: right;">
            <button onclick="moderar('{escape(rid)}', 'valida')" style="background: #15803d; color: #fff; border: none; padding: 0.25rem 0.55rem; border-radius: 4px; cursor: pointer; font-size: 0.78rem; font-weight: 600; margin-right: 0.25rem;">Aprobar</button>
            <button onclick="moderar('{escape(rid)}', 'descartada')" style="background: #991b1b; color: #fff; border: none; padding: 0.25rem 0.55rem; border-radius: 4px; cursor: pointer; font-size: 0.78rem; font-weight: 600;">Descartar</button>
          </td>
        </tr>
        """)
    tabla_pendientes = "".join(filas_pendientes) if filas_pendientes else '<tr><td colspan="4" style="padding: 1rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No hay respuestas sospechosas pendientes de revisión.</td></tr>'

    # Tabla de moderación de reseñas con comprobación visible de consentimiento
    filas_resenas = []
    respuestas_con_resena = [r for r in stats["respuestas"] if r.get("resena")]
    for resp in respuestas_con_resena:
        rid = resp.get("response_id", "")
        res = resp["resena"]
        consent = resp.get("consent_review", False)
        consent_badge = '<span style="color: #166534; font-weight: 700;">Con Consentimiento</span>' if consent else '<span style="color: #f87171; font-weight: 700;">Sin Consentimiento</span>'
        estado_aprob = '<span style="color: #166534;">Aprobada</span>' if res.get("aprobada_publicacion") else '<span style="color: var(--text-muted);">Pendiente</span>'
        
        btn_aprobar = ""
        if consent and resp.get('estado') == 'valida':
            btn_aprobar = f"""<button onclick="moderarResena('{escape(rid)}', true)" style="background: #15803d; color: #fff; border: none; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.75rem; margin-right: 0.25rem;">Aprobar para Guías</button>"""
        else:
            btn_aprobar = """<span style="font-size: 0.72rem; color: var(--text-muted); font-style: italic;">No publicable</span>"""

        filas_resenas.append(f"""
        <tr style="border-bottom: 1px solid var(--border); font-size: 0.83rem;">
          <td style="padding: 0.6rem 0.5rem; font-family: monospace; color: var(--text-muted);">{escape(rid[:8])}</td>
          <td style="padding: 0.6rem 0.5rem; font-weight: 600; color: var(--text);">{escape(res.get("modelo_exacto", ""))}</td>
          <td style="padding: 0.6rem 0.5rem; color: var(--text); max-width: 250px;">{escape(res.get("ventajas", "")[:120])}</td>
          <td style="padding: 0.6rem 0.5rem;">{consent_badge}</td>
          <td style="padding: 0.6rem 0.5rem;">{estado_aprob}</td>
          <td style="padding: 0.6rem 0.5rem; text-align: right;">{btn_aprobar}</td>
        </tr>
        """)
    tabla_resenas = "".join(filas_resenas) if filas_resenas else '<tr><td colspan="6" style="padding: 1rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">No hay reseñas para moderar en este lote.</td></tr>'

    content = f"""
    <div style="max-width: 1100px; margin: 0 auto; padding: 1.5rem 1rem 4rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem;">
        <div>
          <h1 style="font-size: 1.6rem; font-weight: 800; color: var(--text); margin: 0;">Panel Privado: Relevamiento TallerLab 2027</h1>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.25rem 0 0;">Control de avance, calidad de datos y moderación editorial asistida.</p>
        </div>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <form method="POST" action="/relevamiento-2027/admin/logout"><input type="hidden" name="csrf_token" value="{csrf}"><button>Salir</button></form>
          <a href="/api/relevamiento/export?tipo=analitica&formato=csv" style="background: var(--bg-card); border: 1px solid var(--border); color: var(--text); padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.82rem; font-weight: 600; text-decoration: none;">📥 Exportar CSV Analítico</a>
          <a href="/api/relevamiento/export?tipo=comercial&amp;formato=csv">Exportar contactos comerciales</a>
          <a href="/api/relevamiento/export?tipo=publica&amp;formato=csv">Exportar agregados para revisión pública</a>
          <a href="/api/relevamiento/export?tipo=informe&formato=csv" style="background: var(--bg-card); border: 1px solid var(--border); color: var(--text); padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.82rem; font-weight: 600; text-decoration: none;">📥 Exportar destinatarios del informe</a>
        </div>
      </div>

      {demo_banner}
      <form id="survey-revoke" class="survey-login">
        <label for="revoke-id">Baja de contacto y permisos: identificador de respuesta</label>
        <input id="revoke-id" name="response_id" required maxlength="64">
        <button type="submit">Revocar contacto y permisos</button>
        <p>Usar después de verificar la solicitud del participante. Conserva los datos técnicos y retira el contacto y la autorización de reseña.</p>
        <p id="revoke-result" role="status"></p>
      </form>
      <script>document.getElementById('survey-revoke').addEventListener('submit', async function(event) {{
        event.preventDefault();
        if (!confirm('¿Confirmás la baja del contacto y sus permisos para esta respuesta?')) return;
        var response = await fetch('/api/relevamiento/revocar', {{method:'POST', headers:{{'Content-Type':'application/json','X-CSRF-Token':'{csrf}'}}, body:JSON.stringify({{response_id:document.getElementById('revoke-id').value}})}});
        document.getElementById('revoke-result').textContent = response.ok ? 'Contacto y permisos revocados.' : 'No se pudo aplicar la baja.';
      }});</script>

      <!-- MÉTRICAS CLAVE -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
        
        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 0.35rem;">Meta Inicial de Muestra</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: var(--text); display: flex; align-items: baseline; gap: 0.4rem;">
            <span>{stats["n_validas"]}</span>
            <span style="font-size: 1rem; color: var(--text-muted); font-weight: 500;">/ 100 válidas</span>
          </div>
          <div style="margin-top: 0.6rem; height: 6px; background: var(--bg-surface); border-radius: 3px; overflow: hidden;">
            <div style="height: 100%; width: {stats["porcentaje_meta"]}%; background: var(--orange); border-radius: 3px;"></div>
          </div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.35rem;">{stats["porcentaje_meta"]}% del objetivo para evaluar ampliación a 300</div>
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 0.35rem;">Respuestas Totales</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: var(--text);">{stats["total_recibidas"]}</div>
          <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.35rem;">
            <span style="color: #166534;">{stats["n_validas"]} válidas</span> · 
            <span style="color: #f87171;">{stats["n_pendientes"]} a revisar</span>
          </div>
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 0.35rem;">Reseñas de Modelos</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: var(--text);">{stats["total_resenas"]}</div>
          <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.35rem;">Experiencias recibidas; permiso revisado por separado</div>
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <div style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; margin-bottom: 0.35rem;">Abandonos Registrados</div>
          <div style="font-size: 1.8rem; font-weight: 800; color: var(--text);">{stats["total_abandonos"]}</div>
          <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.35rem;">Sesiones iniciadas sin completar tras 24 horas</div><p>Completitud observada: {stats["completitud"] if stats["completitud"] is not None else "Sin datos"}% · {stats["sesiones_completadas"]}/{stats["sesiones_iniciadas"]} sesiones. Medición aproximada: depende del navegador.</p>
        </div>

      </div>

      <h2>Completitud observada por fuente</h2>
      <div style="overflow-x:auto"><table><thead><tr><th>Fuente</th><th>Sesiones iniciadas</th><th>Completadas</th><th>Completitud</th></tr></thead><tbody>{filas_sesiones}</tbody></table></div>
      <p>Eventos aproximados del navegador; una sesión no equivale a una persona única.</p>
      <!-- DISTRIBUCIONES ANALÍTICAS (N VISIBLE) -->
      <h2 style="font-size: 1.25rem; font-weight: 700; color: var(--text); margin-bottom: 1rem;">
        Distribuciones Estadísticas (Muestra válida real: N = {stats["n_validas"]})
      </h2>
      <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;">
        Los gráficos reflejan únicamente respuestas aprobadas como válidas. No se imputan datos ausentes.
      </p>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 1.25rem; margin-bottom: 2.5rem;">
        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;">
            Oficio o Actividad Principal (N={stats["n_validas"]})
          </h3>
          {render_bars(stats["por_oficio"], stats["n_validas"])}
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;">
            Marca Principal en el Taller (N={stats["n_validas"]})
          </h3>
          {render_bars(stats["por_marca"], stats["n_validas"])}
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;">
            Plataforma de Batería (N={stats["n_validas"]})
          </h3>
          {render_bars(stats["por_plataforma"], stats["n_validas"])}
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;">
            Canal Habitual de Compra (N={stats["n_validas"]})
          </h3>
          {render_bars(stats["por_canal"], stats["n_validas"])}
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;">
            Próxima Herramienta a Comprar/Renovar (N={stats["n_validas"]})
          </h3>
          {render_bars(stats["por_proxima"], stats["n_validas"])}
        </div>

        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;">
            Fuentes de Captación UTM (Total={stats["total_recibidas"]})
          </h3>
          {render_bars(stats["por_fuente"], stats["total_recibidas"])}
        </div>
      </div>

      <!-- COLA DE MODERACIÓN DE RESPUESTAS SOSPECHOSAS -->
      <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; margin-bottom: 2rem;">
        <h2 style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">
          Cola de Moderación: Respuestas Marcadas para Revisión ({stats["n_pendientes"]})
        </h2>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">
          Filtros anti-spam, tiempos muy breves o huellas repetidas. Requieren confirmación humana.
        </p>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">
                <th style="padding: 0.5rem;">ID</th>
                <th style="padding: 0.5rem;">Oficio y Provincia</th>
                <th style="padding: 0.5rem;">Motivo de Alerta</th>
                <th style="padding: 0.5rem; text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tabla_pendientes}
            </tbody>
          </table>
        </div>
      </div>

      <!-- COLA DE MODERACIÓN DE RESEÑAS -->
      <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; margin-bottom: 2rem;">
        <h2 style="font-size: 1.15rem; font-weight: 700; color: var(--text); margin-bottom: 0.5rem;">
          Moderación de Reseñas de Herramientas
        </h2>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">
          Solo se permite aprobar para publicación aquellas reseñas donde el participante otorgó consentimiento explícito de publicación.
        </p>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">
                <th style="padding: 0.5rem;">ID</th>
                <th style="padding: 0.5rem;">Modelo</th>
                <th style="padding: 0.5rem;">Opinión declarada</th>
                <th style="padding: 0.5rem;">Consentimiento</th>
                <th style="padding: 0.5rem;">Estado</th>
                <th style="padding: 0.5rem; text-align: right;">Acción</th>
              </tr>
            </thead>
            <tbody>
              {tabla_resenas}
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <script>
      function moderar(responseId, nuevoEstado) {{
        if (!confirm('¿Confirmar cambio de estado a ' + nuevoEstado + '?')) return;
        fetch('/api/relevamiento/moderar', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json', 'X-CSRF-Token': '{csrf}' }},
          body: JSON.stringify({{
            response_id: responseId,
            estado: nuevoEstado
          }})
        }})
        .then(function(res) {{ return res.json(); }})
        .then(function(data) {{
          if (data.ok) {{
            window.location.reload();
          }} else {{
            alert('Error al moderar: ' + (data.error || 'Desconocido'));
          }}
        }})
        .catch(function(err) {{
          alert('Error de red al actualizar estado.');
        }});
      }}

      function moderarResena(responseId, aprobar) {{
        if (!confirm('¿Aprobar publicación de esta reseña?')) return;
        fetch('/api/relevamiento/moderar', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json', 'X-CSRF-Token': '{csrf}' }},
          body: JSON.stringify({{
            response_id: responseId,
            aprobar_resena: aprobar
          }})
        }})
        .then(function(res) {{ return res.json(); }})
        .then(function(data) {{
          if (data.ok) {{
            window.location.reload();
          }} else {{
            alert('No se pudo aprobar la reseña: ' + (data.error || 'Falta consentimiento del usuario.'));
          }}
        }})
        .catch(function(err) {{
          alert('Error de red al actualizar reseña.');
        }});
      }}
    </script>
    """
    return content


def render_relevamiento_callout() -> str:
    """Componente de invitación discreta al relevamiento para las páginas de guías."""
    if not relevamiento_abierto():
        return ""
    return """
    <aside class="relevamiento-invitacion" aria-label="Relevamiento de herramientas" style="margin: 3rem 0; padding: 1.5rem; background: var(--bg-card); border: 1px solid var(--border); border-left: 4px solid var(--orange); border-radius: 10px;">
      <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 1.25rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 0;">
          <div style="font-size: 0.75rem; font-weight: 800; color: var(--orange); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
            Investigación colaborativa
          </div>
          <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text); margin: 0 0 0.4rem 0;">
            ¿Qué herramientas usás en tu taller u oficio?
          </h3>
          <p style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.5; margin: 0;">
            Participá del <strong>Relevamiento TallerLab 2027</strong>. Ayudanos a documentar marcas reales, plataformas de batería y fallas frecuentes en Argentina.
          </p>
        </div>
        <div style="align-self: center;">
          <a href="/relevamiento-2027/?utm_source=interno-tallerlab&amp;utm_medium=callout-guia&amp;utm_campaign=piloto-2027" style="display: inline-block; background: var(--orange); color: #fff; padding: 0.65rem 1.25rem; border-radius: 8px; font-weight: 700; font-size: 0.88rem; text-decoration: none; white-space: nowrap;">
            Completar relevamiento (3 min) →
          </a>
        </div>
      </div>
    </aside>
    """


# --- EXPORTACIONES CSV Y JSON SANITIZADAS ---

def exportar_dataset(tipo: str = "analitica", formato: str = "csv") -> Tuple[str, str, str]:
    """
    Genera el archivo descargable de exportación con protección anti-inyección CSV.
    - tipo='analitica': datos del estudio técnicos (sin emails ni PII).
    - tipo='informe' / 'comercial': contactos filtrados por finalidad.
    """
    if tipo == "publica":
        stats = calcular_estadisticas()
        rows = [{"variable": field, "opcion": option, "n": count, "base": stats['n_validas']} for field in ('por_oficio', 'por_marca', 'por_plataforma') for option, count in stats[field].items() if count >= 5]
        if formato == 'json':
            return json.dumps(rows, ensure_ascii=False), 'application/json', 'relevamiento-agregado.json'
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=['variable', 'opcion', 'n', 'base'])
        writer.writeheader()
        writer.writerows(rows)
        return stream.getvalue(), 'text/csv; charset=utf-8', 'relevamiento-agregado.csv'
    if tipo in ("informe", "comercial"):

        contactos = cargar_contactos()
        contactos_autorizados = [
            c for c in contactos
            if c.get("email") and c.get("consent_report" if tipo == "informe" else "consent_commercial")
        ]
        if formato == "json":
            return json.dumps(contactos_autorizados, ensure_ascii=False, indent=2), "application/json; charset=utf-8", "contactos_relevamiento_2027.json"

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["response_id", "timestamp", "email", "consent_report", "consent_commercial", "consent_review"])
        for c in contactos_autorizados:
            writer.writerow([
                sanitize_csv_cell(c.get("response_id")),
                sanitize_csv_cell(c.get("timestamp")),
                sanitize_csv_cell(c.get("email")),
                "1" if c.get("consent_report") else "0",
                "1" if c.get("consent_commercial") else "0",
                "1" if c.get("consent_review") else "0",
            ])
        return output.getvalue(), "text/csv; charset=utf-8", "contactos_relevamiento_2027.csv"

    else:
        respuestas = [r for r in cargar_respuestas_analiticas() if not r.get('es_demo')]
        if formato == "json":
            return json.dumps(respuestas, ensure_ascii=False, indent=2), "application/json; charset=utf-8", "respuestas_analiticas_2027.json"

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "response_id", "timestamp", "estado", "oficio", "provincia", "tipo_uso",
            "intensidad", "marca_principal", "plataformas_bateria", "cantidad_baterias",
            "proporcion_cable", "canal_compra", "reparaciones_12m", "falla_frecuente",
            "proxima_herramienta", "horizonte_compra", "utm_source", "motivos_revision", "tiene_resena"
        ])
        for r in respuestas:
            writer.writerow([
                sanitize_csv_cell(r.get("response_id")),
                sanitize_csv_cell(r.get("timestamp")),
                sanitize_csv_cell(r.get("estado")),
                sanitize_csv_cell(r.get("oficio")),
                sanitize_csv_cell(r.get("provincia")),
                sanitize_csv_cell(r.get("tipo_uso")),
                sanitize_csv_cell(r.get("intensidad")),
                sanitize_csv_cell(r.get("marca_principal")),
                sanitize_csv_cell(";".join(r.get("plataformas_bateria", []))),
                sanitize_csv_cell(r.get("cantidad_baterias")),
                sanitize_csv_cell(r.get("proporcion_cable")),
                sanitize_csv_cell(r.get("canal_compra")),
                sanitize_csv_cell(r.get("reparaciones_12m")),
                sanitize_csv_cell(r.get("falla_frecuente")),
                sanitize_csv_cell(r.get("proxima_herramienta")),
                sanitize_csv_cell(r.get("horizonte_compra")),
                sanitize_csv_cell(r.get("utm_source")),
                sanitize_csv_cell(";".join(r.get("motivos_revision", []))),
                "1" if r.get("tiene_resena") else "0",
            ])
        return output.getvalue(), "text/csv; charset=utf-8", "respuestas_analiticas_2027.csv"
