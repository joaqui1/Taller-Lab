"""Clase base y estructuras de datos para los extractores de precios."""

import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional


@dataclass
class ExtractionResult:
    """Resultado estructurado y normalizado de una extracción."""
    success: bool
    price_single_payment: Optional[Decimal]
    currency: str = "ARS"
    price_transfer: Optional[Decimal] = None
    price_reference_shown: Optional[Decimal] = None
    availability: str = "desconocido"  # 'disponible', 'agotado', 'desconocido'
    shipping_cost: Optional[Decimal] = None
    shipping_note: Optional[str] = None
    extracted_mpn: Optional[str] = None
    extracted_title: Optional[str] = None
    raw_evidence_hash: Optional[str] = None
    raw_evidence_snippet: Optional[str] = None
    error_message: Optional[str] = None
    extractor_version: str = "1.0.0"


class BaseExtractor(ABC):
    """Interfaz base para adaptadores de extracción."""

    VERSION = "1.0.0"

    @abstractmethod
    def extract(self, content: str, url: str, target_product) -> ExtractionResult:
        """Extrae precio, variante y disponibilidad desde el contenido."""
        pass

    @staticmethod
    def parse_money(raw_value) -> Optional[Decimal]:
        """Convierte una representación cruda a Decimal exacto en unidades monetarias.
        
        Maneja formatos argentinos e internacionales:
        - 125000 -> 125000.00
        - "125.000,50" -> 125000.50
        - "125,000.50" -> 125000.50
        - "$ 125.000" -> 125000.00
        """
        if raw_value is None or raw_value == "":
            return None

        if isinstance(raw_value, float):
            import math
            if math.isnan(raw_value) or math.isinf(raw_value):
                return None

        if isinstance(raw_value, (int, float, Decimal)):
            if raw_value <= 0:
                return None
            return Decimal(str(raw_value)).quantize(Decimal("0.01"))

        s = str(raw_value).strip()
        # Rechazar valores negativos explícitamente: el precio de venta nunca es negativo
        if s.startswith("-") or s.startswith("−"):
            return None

        # Retirar símbolos monetarios y espacios no separadores
        s = re.sub(r"[^\d,\.]", "", s)
        if not s:
            return None

        # Si contiene coma y punto, determinar cuál es el separador decimal
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                # Formato argentino/europeo: 125.000,50 -> 125000.50
                s = s.replace(".", "").replace(",", ".")
            else:
                # Formato anglosajón: 125,000.50 -> 125000.50
                s = s.replace(",", "")
        elif "," in s:
            # Solo contiene coma: si tiene 2 decimales al final es separador decimal
            parts = s.split(",")
            if len(parts) == 2 and len(parts[1]) in (1, 2):
                s = parts[0] + "." + parts[1]
            else:
                s = s.replace(",", "")
        elif "." in s:
            # Solo contiene punto: si tiene 3 dígitos al final podría ser miles (ej. 125.000)
            parts = s.split(".")
            if len(parts) == 2 and len(parts[1]) == 3 and int(parts[0]) > 0:
                s = parts[0] + parts[1]
            elif len(parts) > 2:
                # Varios puntos (ej. 1.250.000)
                s = s.replace(".", "")

        try:
            val = Decimal(s).quantize(Decimal("0.01"))
            return val
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def compute_evidence_hash(content: str) -> str:
        """Calcula el hash SHA-256 de la evidencia cruda."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def extract_snippet(content: str, max_length: int = 500) -> str:
        """Extrae un fragmento de evidencia sanitizado y limitado en longitud."""
        clean = " ".join(content.split())
        return clean[:max_length]
