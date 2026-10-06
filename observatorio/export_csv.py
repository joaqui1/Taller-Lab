"""Exportación de observaciones y datasets a formato CSV seguro y estandarizado."""

import csv
import io
from decimal import Decimal
from typing import Any, Dict, List, Optional

from observatorio.analytics import format_art_date
from observatorio.config import DATA_VERSION, METHODOLOGY_VERSION
from observatorio.db import query_all
from observatorio.publication import PUBLIC_OBSERVATION_SQL

VALID_CATEGORIES = ("compresores", "hidrolavadoras", "generadores")


def sanitize_csv_field(val: Any) -> str:
    """Previene inyección de fórmulas en planillas de cálculo (Excel/LibreOffice) para campos de texto."""
    if val is None:
        return ""
    s = str(val).strip()
    # Si comienza con caracteres ejecutables en hojas de cálculo, prefijar con apóstrofe
    if s.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + s
    return s


def export_observations_to_csv(category: Optional[str] = None) -> str:
    """Genera el contenido CSV de observaciones validadas en UTF-8 con metadatos y protección."""
    if category and category not in VALID_CATEGORIES:
        return ""

    params = []
    category_filter = ""
    if category:
        category_filter = "AND cp.category = ?"
        params.append(category)

    sql = f"""
        SELECT 
            o.id AS observacion_id,
            off.id AS oferta_id,
            cp.category AS categoria,
            cp.brand AS marca,
            cp.model_name AS modelo,
            cp.mpn AS codigo_fabricante,
            cp.gtin_ean AS gtin_ean,
            cp.voltage AS tension,
            o.price_single_payment AS precio_pago_unico_ars,
            o.currency AS moneda,
            o.price_transfer AS precio_transferencia_ars,
            o.price_reference_shown AS precio_referencia_mostrado_ars,
            o.availability AS disponibilidad,
            off.seller_name AS vendedor,
            off.direct_url AS url_directa,
            src.domain AS dominio_fuente,
            o.observed_at AS fecha_observacion_utc,
            o.extractor_version AS version_extractor
        FROM observations o
        JOIN catalog_products cp ON o.product_id = cp.id
        JOIN offers off ON o.offer_id = off.id
        JOIN sources src ON off.source_id = src.id
        WHERE {PUBLIC_OBSERVATION_SQL}
          {category_filter}
        ORDER BY o.observed_at DESC;
    """

    rows = query_all(sql, params)

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    # Encabezado con metadatos institucionales y versión

    fieldnames = [
        "observacion_id",
        "oferta_id",
        "categoria",
        "marca",
        "modelo",
        "codigo_fabricante",
        "gtin_ean",
        "tension",
        "precio_pago_unico_ars",
        "moneda",
        "precio_transferencia_ars",
        "precio_referencia_mostrado_ars",
        "disponibilidad",
        "vendedor",
        "url_directa",
        "dominio_fuente",
        "fecha_observacion_utc",
        "fecha_observacion_art",
        "version_extractor",
        "version_datos",
    ]
    writer.writerow(fieldnames)

    for r in rows:
        utc_dt = r.get("fecha_observacion_utc") or ""
        art_dt = format_art_date(utc_dt) if utc_dt else ""

        p_single = r.get("precio_pago_unico_ars")
        p_trans = r.get("precio_transferencia_ars")
        p_ref = r.get("precio_referencia_mostrado_ars")

        row_values = [
            sanitize_csv_field(r.get("observacion_id")),
            sanitize_csv_field(r.get("oferta_id")),
            sanitize_csv_field(r.get("categoria")),
            sanitize_csv_field(r.get("marca")),
            sanitize_csv_field(r.get("modelo")),
            sanitize_csv_field(r.get("codigo_fabricante")),
            sanitize_csv_field(r.get("gtin_ean")),
            sanitize_csv_field(r.get("tension")),
            f"{Decimal(str(p_single)):.2f}" if p_single is not None else "",
            sanitize_csv_field(r.get("moneda")),
            f"{Decimal(str(p_trans)):.2f}" if p_trans is not None else "",
            f"{Decimal(str(p_ref)):.2f}" if p_ref is not None else "",
            sanitize_csv_field(r.get("disponibilidad")),
            sanitize_csv_field(r.get("vendedor")),
            sanitize_csv_field(r.get("url_directa")),
            sanitize_csv_field(r.get("dominio_fuente")),
            sanitize_csv_field(utc_dt),
            sanitize_csv_field(art_dt),
            sanitize_csv_field(r.get("version_extractor")),
            sanitize_csv_field(DATA_VERSION),
        ]
        writer.writerow(row_values)

    return output.getvalue()
