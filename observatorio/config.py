"""Configuración central para el Observatorio de Precios de TallerLab."""

import os
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT_DIR = Path(__file__).resolve().parent.parent
OBSERVATORIO_DIR = Path(__file__).resolve().parent

# Dominio y URLs
SITE_URL = (os.environ.get("SITE_URL", "").strip() or "https://www.tallerlab.com.ar").rstrip("/")

# Base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DEFAULT_SQLITE_PATH = OBSERVATORIO_DIR / "observatorio.db"
SQLITE_PATH = Path(os.environ.get("OBSERVATORY_SQLITE_PATH", str(DEFAULT_SQLITE_PATH)))

# Modo de almacenamiento: "postgres" si DATABASE_URL apunta a Postgres, de lo contrario "sqlite"
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    STORAGE_MODE = "postgres"
else:
    STORAGE_MODE = "sqlite"

# Seguridad y autorización para endpoints de cron y administración
OBSERVATORY_SECRET = os.environ.get("OBSERVATORY_SECRET", "").strip()

# Parámetros operativos y límites
_raw_batch = os.environ.get("OBSERVATORY_MAX_BATCH_SIZE", "50")
try:
    _batch_val = int(_raw_batch)
except (ValueError, TypeError):
    _batch_val = 50
MAX_BATCH_SIZE = max(1, min(50, _batch_val))  # rango seguro: 1..50
REQUEST_TIMEOUT_SECONDS = int(os.environ.get("OBSERVATORY_TIMEOUT", "10"))
MAX_RETRIES = 2
RUN_BUDGET_SECONDS = max(30, min(240, int(os.environ.get('OBSERVATORY_RUN_BUDGET_SECONDS', '240'))))
USER_AGENT = "TallerLabObservatorio/1.0 (+https://www.tallerlab.com.ar/datos/precios/metodologia/)"

# Umbrales metodológicos y de calidad
# Límite de frescura: 48 horas. Una captura más antigua se preserva en el historial pero
# no se considera "mínimo actual vigente".
FRESHNESS_HOURS_LIMIT = 48

# Umbral de salto anómalo respecto a la mediana histórica reciente de la oferta (35%)
PRICE_JUMP_THRESHOLD_PERCENT = Decimal("35.0")

# Límites de plausibilidad de precio para herramientas eléctricas y de taller en ARS
MIN_REASONABLE_PRICE = Decimal("5000.00")
MAX_REASONABLE_PRICE = Decimal("50000000.00")

# Zona horaria oficial para presentación
TZ_BUENOS_AIRES = ZoneInfo("America/Argentina/Buenos_Aires")
TZ_UTC = ZoneInfo("UTC")

# Versión del esquema y metodología
METHODOLOGY_VERSION = "2026.2"
DATA_VERSION = "2.0.0"
