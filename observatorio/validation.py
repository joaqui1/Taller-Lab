"""Módulo de validación de tres capas y detección de anomalías de precios."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from observatorio.config import (
    FRESHNESS_HOURS_LIMIT,
    MAX_REASONABLE_PRICE,
    MIN_REASONABLE_PRICE,
    PRICE_JUMP_THRESHOLD_PERCENT,
)
from observatorio.extractors.base import ExtractionResult


@dataclass
class ValidationReport:
    """Resultado detallado de la auditoría de una observación."""
    status: str  # 'valido', 'anomalo', 'rechazado'
    is_published: bool
    incident_type: Optional[str] = None
    incident_severity: str = "info"  # 'info', 'warning', 'critical'
    incident_details: Optional[str] = None
    reasons: List[str] = field(default_factory=list)


def is_observation_fresh(observed_at_utc: datetime) -> bool:
    """Determina si una observación cumple con la política de frescura (máximo 48 horas)."""
    now = datetime.now(timezone.utc)
    delta_hours = (now - observed_at_utc).total_seconds() / 3600.0
    return 0 <= delta_hours <= FRESHNESS_HOURS_LIMIT


def validate_observation(
    extraction: ExtractionResult,
    target_product,
    configured_offer,
    previous_valid_observations: Optional[List[Dict[str, Any]]] = None,
) -> ValidationReport:
    """Aplica controles obligatorios separando captura bruta, observación validada y dato publicado."""
    
    # 1. Control de éxito de extracción
    if not extraction.success or extraction.price_single_payment is None:
        return ValidationReport(
            status="rechazado",
            is_published=False,
            incident_type="extraction_failure",
            incident_severity="warning",
            incident_details=extraction.error_message or "Extracción no exitosa o precio ausente.",
            reasons=[extraction.error_message or "Extracción no exitosa"],
        )

    price = extraction.price_single_payment

    # 2. Control de moneda: solo ARS
    if extraction.currency != "ARS":
        return ValidationReport(
            status="rechazado",
            is_published=False,
            incident_type="invalid_currency",
            incident_severity="critical",
            incident_details=f"Moneda '{extraction.currency}' no admitida. Se requiere ARS.",
            reasons=[f"Moneda rechazada: {extraction.currency}"],
        )

    # 3. Control de rango plausible de precios
    if price < MIN_REASONABLE_PRICE or price > MAX_REASONABLE_PRICE:
        return ValidationReport(
            status="anomalo",
            is_published=False,
            incident_type="price_out_of_bounds",
            incident_severity="critical",
            incident_details=(
                f"Precio ${price:,.2f} fuera del umbral admisible "
                f"(${MIN_REASONABLE_PRICE:,.2f} - ${MAX_REASONABLE_PRICE:,.2f})."
            ),
            reasons=["Precio fuera de rango plausible"],
        )

    # 4. Control de coherencia en transferencias
    if extraction.price_transfer is not None and extraction.price_transfer > price:
        return ValidationReport(
            status="anomalo",
            is_published=False,
            incident_type="inconsistent_transfer_price",
            incident_severity="warning",
            incident_details=(
                f"El precio por transferencia (${extraction.price_transfer:,.2f}) "
                f"supera al precio de lista único (${price:,.2f})."
            ),
            reasons=["Precio por transferencia superior al de lista"],
        )

    # 5. Detección de saltos extraordinarios respecto a la mediana histórica reciente
    if previous_valid_observations:
        # Filtrar observaciones de la misma oferta
        prev_prices = [
            Decimal(str(obs["price_single_payment"]))
            for obs in previous_valid_observations
            if obs.get("price_single_payment") is not None
        ]
        
        if prev_prices:
            # Mediana de precios previos
            sorted_prices = sorted(prev_prices)
            mid = len(sorted_prices) // 2
            prev_median = sorted_prices[mid] if len(sorted_prices) % 2 != 0 else (sorted_prices[mid - 1] + sorted_prices[mid]) / Decimal(2)

            if prev_median > 0:
                jump_pct = (abs(price - prev_median) / prev_median) * Decimal(100)
                if jump_pct >= PRICE_JUMP_THRESHOLD_PERCENT:
                    return ValidationReport(
                        status="anomalo",
                        is_published=False,
                        incident_type="price_jump",
                        incident_severity="critical",
                        incident_details=(
                            f"Salto de precio del {jump_pct:.1f}% respecto a la mediana histórica previa "
                            f"(${prev_median:,.2f} -> ${price:,.2f}). Umbral configurado: {PRICE_JUMP_THRESHOLD_PERCENT}%."
                        ),
                        reasons=[f"Variación extraordinaria de {jump_pct:.1f}%"],
                    )

    # 6. Control de disponibilidad para publicación
    # REGLA OBLIGATORIA: Nunca publicar como mínimo actual un producto agotado o con stock desconocido.
    if extraction.availability == "agotado":
        return ValidationReport(
            status="valido",
            is_published=False,  # Se conserva en el historial pero NO como mínimo vigente activo
            incident_type="out_of_stock",
            incident_severity="info",
            incident_details=f"Oferta observada correctamente pero sin stock en la tienda.",
            reasons=["Producto agotado en la fuente"],
        )
    elif extraction.availability != "disponible":
        return ValidationReport(
            status="valido",
            is_published=False,  # No se publica como mínimo de compra si la disponibilidad no está declarada
            incident_type="unknown_availability",
            incident_severity="info",
            incident_details="Disponibilidad no declarada por la fuente.",
            reasons=["Disponibilidad desconocida"],
        )

    # Si pasa todos los filtros, la observación es válida y apta para publicación
    return ValidationReport(
        status="valido",
        is_published=True,
        incident_type=None,
        reasons=[],
    )
