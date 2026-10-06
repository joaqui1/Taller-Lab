"""Módulo de analítica, estadísticas y agregaciones para el Observatorio."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from observatorio.config import (
    FRESHNESS_HOURS_LIMIT,
    TZ_BUENOS_AIRES,
    TZ_UTC,
)
from observatorio.db import query_all, query_one
from observatorio.publication import PUBLIC_OBSERVATION_SQL
import logging

def empty_product_stats(product_id):
    return {'product_id':product_id,'active_offers_count':0,'min_current_price':None,'median_current_price':None,
            'max_current_price':None,'current_offers':[],'historical_min_price':None,'historical_max_price':None,
            'historical_observations_count':0,'last_observed_at_display':None,'is_fresh':False,'unavailable':True}


def format_art_date(dt_utc_str: str) -> str:
    """Convierte un timestamp UTC ISO a formato legible en hora argentina (ART)."""
    try:
        dt = datetime.fromisoformat(dt_utc_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ_UTC)
        art_dt = dt.astimezone(TZ_BUENOS_AIRES)
        return art_dt.strftime("%d/%m/%Y %H:%M ART")
    except Exception:
        return dt_utc_str


def get_product_current_stats(product_id: str) -> Dict[str, Any]:
    """Calcula mínimo, mediana y máximo vigente para un producto entre ofertas activas con stock.
    
    Selecciona primero el ÚLTIMO estado conocido de cada oferta (por observed_at),
    luego aplica filtros de disponibilidad, frescura y publicación sobre ese estado.
    Nunca retrocede a una observación anterior si la más reciente dice agotado.
    """
    now = datetime.now(timezone.utc)
    freshness_threshold = (now - timedelta(hours=FRESHNESS_HOURS_LIMIT)).isoformat()

    # Subconsulta: último estado por oferta (sin filtrar disponibilidad todavía)
    # Compatible con SQLite y PostgreSQL
    sql_latest = """
        SELECT 
            o.id AS obs_id,
            o.offer_id,
            o.price_single_payment,
            o.price_transfer,
            o.price_reference_shown,
            o.availability,
            o.observed_at,
            o.is_published,
            o.is_synthetic,
            o.validation_status,
            off.seller_name,
            off.direct_url,
            src.name AS source_name
        FROM observations o
        JOIN offers off ON o.offer_id = off.id
        JOIN sources src ON off.source_id = src.id
        WHERE o.product_id = ?
          AND o.is_synthetic = 0
          AND off.enabled = 1
          AND src.status = 'habilitada'
          AND src.capture_allowed=1 AND src.redistribution_allowed=1 AND src.terms_verified_date IS NOT NULL
          AND o.id = (
              SELECT o2.id
              FROM observations o2
              WHERE o2.offer_id = o.offer_id
                AND o2.is_synthetic = 0
              ORDER BY o2.observed_at DESC,o2.created_at DESC,o2.id DESC LIMIT 1
          )
          AND NOT EXISTS (SELECT 1 FROM collector_attempts a WHERE a.offer_id=o.offer_id AND a.is_synthetic=0 AND a.observed_at>o.observed_at)
    """
    try:
        latest_by_offer = query_all(sql_latest, (product_id,))
    except Exception:
        logging.getLogger(__name__).warning('Observatorio sin esquema o conexión disponible')
        return empty_product_stats(product_id)

    # Filtrar: solo disponibles, publicados y frescos
    active_obs = [
        obs for obs in latest_by_offer
        if obs["availability"] == "disponible"
        and obs["is_published"] == 1
        and obs['validation_status'] == 'valido'
        and obs["observed_at"] >= freshness_threshold
        and obs['observed_at'] <= now.isoformat()
    ]

    prices = [Decimal(str(obs["price_single_payment"])) for obs in active_obs]
    
    min_price = None
    median_price = None
    max_price = None

    if prices:
        min_price = min(prices)
        max_price = max(prices)
        sorted_p = sorted(prices)
        n = len(sorted_p)
        if n % 2 != 0:
            median_price = sorted_p[n // 2]
        else:
            median_price = (sorted_p[n // 2 - 1] + sorted_p[n // 2]) / Decimal(2)

    # Histórico del producto
    sql_hist = f"""
        SELECT 
            MIN(o.price_single_payment) AS hist_min,
            MAX(o.price_single_payment) AS hist_max,
            COUNT(o.id) AS hist_count,
            MIN(o.observed_at) AS first_obs,
            MAX(o.observed_at) AS last_obs
        FROM observations o JOIN offers off ON off.id=o.offer_id JOIN sources src ON src.id=off.source_id
        WHERE o.product_id = ? AND {PUBLIC_OBSERVATION_SQL};
    """
    hist_row = query_one(sql_hist, (product_id,)) or {}

    last_observed_str = None
    if active_obs:
        last_dt = max(obs["observed_at"] for obs in active_obs)
        last_observed_str = format_art_date(last_dt)
    elif hist_row.get("last_obs"):
        last_observed_str = format_art_date(hist_row["last_obs"]) + " (histórico — sin captura fresca)"

    return {
        "product_id": product_id,
        "active_offers_count": len(active_obs),
        "min_current_price": min_price,
        "median_current_price": median_price,
        "max_current_price": max_price,
        "current_offers": active_obs,
        "historical_min_price": Decimal(str(hist_row["hist_min"])) if hist_row.get("hist_min") else None,
        "historical_max_price": Decimal(str(hist_row["hist_max"])) if hist_row.get("hist_max") else None,
        "historical_observations_count": hist_row.get("hist_count", 0),
        "last_observed_at_display": last_observed_str,
        "is_fresh": len(active_obs) > 0,
    }


def get_product_price_history_series(product_id: str) -> List[Dict[str, Any]]:
    """Retorna las series históricas de precios observados por oferta para gráficos.
    
    Conserva huecos explícitos para observaciones faltantes (no interpola días).
    """
    sql = f"""
        SELECT 
            o.observed_at,
            o.price_single_payment,
            o.price_transfer,
            o.availability,
            off.seller_name,
            off.id AS offer_id
        FROM observations o
        JOIN offers off ON o.offer_id = off.id
        JOIN sources src ON src.id=off.source_id
        WHERE o.product_id = ? AND {PUBLIC_OBSERVATION_SQL}
        ORDER BY o.observed_at ASC,o.id ASC;
    """
    try:
        rows = query_all(sql, (product_id,))
    except Exception:
        return []
    
    series = []
    for r in rows:
        series.append({
            "observed_at": r["observed_at"],
            "date_display": format_art_date(r["observed_at"]),
            "offer_id": r["offer_id"],
            "seller": r["seller_name"],
            "price": float(r["price_single_payment"]) if r["price_single_payment"] else None,
            "transfer_price": float(r["price_transfer"]) if r["price_transfer"] else None,
            "availability": r["availability"],
        })
    if not series:
        return []
    today = datetime.now(TZ_BUENOS_AIRES).date()
    start = today - timedelta(days=364)
    by_offer = {}
    for row in series:
        day = datetime.fromisoformat(row['observed_at']).astimezone(TZ_BUENOS_AIRES).date()
        if start <= day <= today:
            row['day'] = day.isoformat()
            by_offer.setdefault(row['offer_id'], {})[day] = row
    calendar = []
    for offer_id, daily in by_offer.items():
        first = min(daily)
        seller = daily[first]['seller']
        day = first
        while day <= today:
            calendar.append(daily.get(day, {'day':day.isoformat(),'offer_id':offer_id,'seller':seller,'price':None,'transfer_price':None,'availability':'sin captura'}))
            day += timedelta(days=1)
    return calendar


def analyze_seller_discount(offer_id: str, days_window: int = 30) -> Dict[str, Any]:
    """Analiza descuento comparando precio actual vs ventana previa de N días (mismo vendedor/oferta).
    
    Requiere mínimo 3 días distintos de cobertura. La ventana previa excluye registros
    desde el momento en que detecta un cambio de precio.
    """
    offer=query_one('SELECT product_id FROM offers WHERE id=?',(offer_id,))
    if not offer or not any(row['offer_id']==offer_id for row in get_product_current_stats(offer['product_id'])['current_offers']):
        return {'has_data':False,'reason':'No hay una oferta actual verificable para comparar.'}
    now = datetime.now(timezone.utc)
    window_start = (now - timedelta(days=days_window)).isoformat()

    sql = f"""
        SELECT o.price_single_payment,o.price_reference_shown,o.observed_at,o.availability
        FROM observations o JOIN offers off ON off.id=o.offer_id JOIN sources src ON src.id=off.source_id
        WHERE o.offer_id = ? AND {PUBLIC_OBSERVATION_SQL}
          AND o.observed_at >= ?
        ORDER BY o.observed_at ASC,o.id ASC;
    """
    rows = query_all(sql, (offer_id, window_start))
    if not rows:
        return {"has_data": False, "reason": "Sin observaciones suficientes en la ventana de 30 días."}

    latest = rows[-1]
    current_price = Decimal(str(latest["price_single_payment"]))
    ref_shown = Decimal(str(latest["price_reference_shown"])) if latest.get("price_reference_shown") else None

    # Contar días distintos en hora argentina / UTC
    daily = {}
    for r in rows:
        daily[datetime.fromisoformat(r['observed_at']).astimezone(TZ_BUENOS_AIRES).date()] = r
    rows = list(daily.values())
    distinct_days = len(rows)

    # Ventana previa: observaciones anteriores a la actual
    # Excluir todo el período de precio actual, no solo la última captura.
    baseline_rows = rows[:]
    while baseline_rows and Decimal(str(baseline_rows[-1]['price_single_payment'])) == current_price:
        baseline_rows.pop()
    if len(baseline_rows) < 3:
        return {'has_data':False,'cobertura_insuficiente':True,'days_observed_in_window':distinct_days,
                'reason':'Se requieren al menos tres días previos distintos, fuera del período del precio actual.'}

    past_prices = [
        Decimal(str(r["price_single_payment"]))
        for r in baseline_rows
        if r.get("price_single_payment") is not None
    ]

    past_median = None
    real_drop_pct = None
    if past_prices:
        sorted_p = sorted(past_prices)
        n = len(sorted_p)
        if n % 2 != 0:
            past_median = sorted_p[n // 2]
        else:
            past_median = (sorted_p[n // 2 - 1] + sorted_p[n // 2]) / Decimal(2)
        if past_median > 0:
            real_drop_pct = ((past_median - current_price) / past_median) * Decimal(100)

    announced_discount_pct = None
    if ref_shown and ref_shown > 0:
        announced_discount_pct = ((ref_shown - current_price) / ref_shown) * Decimal(100)

    return {
        "has_data": True,
        "cobertura_insuficiente": distinct_days < 3,
        "days_observed_in_window": distinct_days,
        "current_price": current_price,
        "reference_price_shown": ref_shown,
        "announced_discount_pct": announced_discount_pct,
        "baseline_30d_median": past_median,
        "actual_reduction_vs_baseline_pct": real_drop_pct,
    }


def get_equipment_cost_estimate() -> Dict[str, Any]:
    """Calcula el costo estimado de equipamiento de taller para una canasta fija de 5 herramientas.
    
    Es una suma directa de los precios mínimos vigentes de los 5 modelos.
    Si alguno no tiene precio vigente, el resultado es None (no se presenta parcial).
    Esto NO es un índice de precios: no tiene base 100, no compara períodos ni pondera por ventas.
    """
    basket_products = [
        "COMP-LUSQ-LC2550B",
        "HIDRO-KARCH-K2",
        "HIDRO-LUSQ-HL120",
        "COMP-LUSQ-LC0122",
        "COMP-LUSQ-MCL150",
    ]

    total_cost = Decimal("0.00")
    items_detail = []
    all_present = True

    for prod_id in basket_products:
        stats = get_product_current_stats(prod_id)
        min_p = stats["min_current_price"]
        if min_p is not None:
            total_cost += min_p
            items_detail.append({
                "product_id": prod_id,
                "current_min_price": float(min_p),
                "is_present": True,
            })
        else:
            all_present = False
            items_detail.append({
                "product_id": prod_id,
                "current_min_price": None,
                "is_present": False,
            })

    return {
        "label": "Costo estimado de equipamiento de taller (5 herramientas — TallerLab)",
        "status": "referencia",
        "methodology": (
            "Suma directa de los precios mínimos vigentes de 5 herramientas de taller. "
            "No es un índice de precios ni refleja la totalidad del mercado. "
            "Si alguna herramienta no tiene precio disponible, el total no se calcula."
        ),
        "disclaimer": (
            "Indicador de referencia. Publicado solo cuando los 5 modelos tienen datos frescos y verificados."
        ),
        "all_present": all_present,
        "total_cost_ars": float(total_cost) if all_present else None,
        "items": items_detail,
    }


def get_experimental_tool_basket_index() -> Dict[str, Any]:
    """Función de compatibilidad para vistas y pruebas que consumen la canasta de herramientas."""
    estimate = get_equipment_cost_estimate()
    total_cost = estimate.get("total_cost_ars")
    items = estimate.get("items", [])
    present_count = sum(1 for it in items if it.get("is_present"))
    total_count = len(items) if items else 1
    coverage_pct = (present_count / total_count) * 100.0
    return {
        "label": estimate["label"],
        "status": estimate["status"],
        "methodology": estimate["methodology"],
        "disclaimer": estimate["disclaimer"],
        "has_minimum_coverage": estimate["all_present"],
        "basket_value_ars": total_cost,
        "coverage_pct": coverage_pct,
        "items": items,
    }
