"""Utilidad de línea de comandos (CLI) para administración y operación del Observatorio."""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from observatorio.catalog import CATALOG_PRODUCTS
from observatorio.collector import run_collection_batch
from observatorio.config import METHODOLOGY_VERSION, SQLITE_PATH, STORAGE_MODE
from observatorio import config
from observatorio.db import execute_stmt, init_db, query_all, query_one
from observatorio.export_csv import export_observations_to_csv
from observatorio.sources import CONFIGURED_OFFERS, SOURCES_REGISTRY


def cmd_init_db(args):
    """Inicializa la estructura de base de datos."""
    print(f"Inicializando base de datos ({STORAGE_MODE})...")
    init_db()
    print("OK: Esquema y tablas creados exitosamente.")


def cmd_seed_catalog(args):
    """Carga o actualiza el catálogo maestro, fuentes y ofertas en la base de datos."""
    print("Sincronizando catálogo maestro y fuentes...")
    init_db()

    now_utc = datetime.now(timezone.utc).isoformat()

    # 1. Fuentes
    for src in SOURCES_REGISTRY:
        execute_stmt(
            """
            INSERT INTO sources (id, name, domain, access_method, terms_reference, status, conservation_restrictions, max_requests_per_minute, created_at, terms_verified_date, redistribution_allowed, capture_allowed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                domain = excluded.domain,
                access_method = excluded.access_method,
                terms_reference = excluded.terms_reference,
                conservation_restrictions = excluded.conservation_restrictions,
                terms_verified_date = excluded.terms_verified_date,
                redistribution_allowed = excluded.redistribution_allowed,
                capture_allowed = excluded.capture_allowed,
                status = CASE WHEN excluded.capture_allowed = 0 THEN excluded.status
                              WHEN sources.status = 'pendiente_evaluacion' THEN excluded.status
                              ELSE sources.status END;
            """,
            (
                src.id, src.name, src.domain, src.access_method, src.terms_reference,
                src.status, src.conservation_restrictions, src.max_requests_per_minute, now_utc,
                src.terms_verified_date, int(src.redistribution_allowed), int(src.capture_allowed)
            )
        )

    # 2. Productos
    for prod in CATALOG_PRODUCTS:
        d = prod.to_dict()
        execute_stmt(
            """
            INSERT INTO catalog_products (id, category, brand, model_name, mpn, gtin_ean, voltage, specs_json, kit_content, item_condition, guide_url, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(id) DO UPDATE SET
                brand = excluded.brand,
                model_name = excluded.model_name,
                mpn = excluded.mpn,
                gtin_ean = excluded.gtin_ean,
                voltage = excluded.voltage,
                specs_json = excluded.specs_json,
                kit_content = excluded.kit_content,
                guide_url = excluded.guide_url;
            """,
            (
                d["id"], d["category"], d["brand"], d["model_name"], d["mpn"],
                d["gtin_ean"], d["voltage"], d["specs_json"], d["kit_content"],
                d["item_condition"], d["guide_url"], now_utc
            )
        )

    # 3. Ofertas
    for off in CONFIGURED_OFFERS:
        execute_stmt(
            """
            INSERT INTO offers (id, product_id, source_id, seller_name, direct_url, affiliate_url, external_sku, extraction_method, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                seller_name = excluded.seller_name,
                direct_url = excluded.direct_url,
                affiliate_url = excluded.affiliate_url,
                external_sku = excluded.external_sku,
                extraction_method = excluded.extraction_method;
            """,
            (
                off.id, off.product_id, off.source_id, off.seller_name, off.direct_url,
                off.affiliate_url, off.external_sku, off.extraction_method,
                1 if off.enabled else 0, now_utc
            )
        )

    print(f"OK: {len(SOURCES_REGISTRY)} fuentes, {len(CATALOG_PRODUCTS)} modelos y {len(CONFIGURED_OFFERS)} ofertas registradas.")


def cmd_run_collector(args):
    """Ejecuta una corrida de recolección de precios."""
    print(f"Iniciando recolección de precios (Lote máx: {args.batch_size}, Fixtures: {args.fixtures})...")
    res = run_collection_batch(
        batch_size=args.batch_size,
        use_fixtures=args.fixtures,
    )
    print(f"Resultado corrida {res['run_id']}:")
    print(f"- Estado: {res['status']}")
    print(f"- Ofertas procesadas: {res['total_offers']}")
    print(f"- Validadas con éxito: {res['successful_offers']}")
    print(f"- Fallos de recolección: {res['failed_offers']}")
    print(f"- Anomalías detectadas: {res['anomalies_detected']}")


def cmd_check_incidents(args):
    """Lista las incidencias y anomalías registradas pendientes de resolución."""
    rows = query_all(
        """
        SELECT i.id, i.offer_id, i.incident_type, i.severity, i.details, i.created_at, off.seller_name, cp.model_name
        FROM incidents i
        JOIN offers off ON i.offer_id = off.id
        JOIN catalog_products cp ON off.product_id = cp.id
        WHERE i.resolved = 0
        ORDER BY i.created_at DESC;
        """
    )
    if not rows:
        print("OK: No hay incidencias pendientes.")
        return

    print(f"Se encontraron {len(rows)} incidencias pendientes:")
    for r in rows:
        print(f"[{r['severity'].upper()}] ID: {r['id']} | {r['model_name']} ({r['seller_name']}) | Tipo: {r['incident_type']}")
        print(f"   Detalle: {r['details']}")
        print(f"   Fecha: {r['created_at']}")


def cmd_resolve_incident(args):
    """Marca una incidencia como resuelta documentando la auditoría."""
    now_utc = datetime.now(timezone.utc).isoformat()
    affected = execute_stmt(
        """
        UPDATE incidents 
        SET resolved = 1, resolution_note = ?, resolved_at = ?
        WHERE id = ?;
        """,
        (args.note, now_utc, args.incident_id)
    )
    if affected:
        print(f"OK: Incidencia {args.incident_id} marcada como resuelta.")
    else:
        print(f"Error: No se encontró la incidencia {args.incident_id}.")


def cmd_export_csv(args):
    """Exporta el dataset de observaciones a archivo o salida estándar."""
    csv_text = export_observations_to_csv(category=args.category)
    if args.output:
        Path(args.output).write_text(csv_text, encoding="utf-8")
        print(f"OK: Dataset exportado a {args.output}")
    else:
        sys.stdout.write(csv_text)


def cmd_backup(args):
    """Realiza una copia de respaldo de la base de datos local."""
    if config.STORAGE_MODE == "sqlite":
        dest = Path(args.dest or f"backup_observatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        import sqlite3
        from contextlib import closing
        from observatorio.db import get_db
        with get_db() as source, closing(sqlite3.connect(dest)) as destination:
            source.backup(destination)
        print(f"OK: Respaldo SQLite guardado en {dest}")
    else:
        print("Para PostgreSQL en producción, use el mecanismo de dump del proveedor (ej. pg_dump).")


def main():
    parser = argparse.ArgumentParser(description="Gestión y operación del Observatorio TallerLab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init-db
    p_init = subparsers.add_parser("init-db", help="Crear tablas y esquemas")
    p_init.set_defaults(func=cmd_init_db)

    # seed-catalog
    p_seed = subparsers.add_parser("seed-catalog", help="Cargar catálogo maestro y ofertas")
    p_seed.set_defaults(func=cmd_seed_catalog)

    # run-collector
    p_run = subparsers.add_parser("run-collector", help="Ejecutar captura de precios")
    p_run.add_argument("--batch-size", type=int, default=config.MAX_BATCH_SIZE, help="Tamaño máximo de lote (1..50)")
    p_run.add_argument("--fixtures", action="store_true", help="Usar muestras offline")
    p_run.set_defaults(func=cmd_run_collector)

    # check-incidents
    p_inc = subparsers.add_parser("check-incidents", help="Ver incidencias activas")
    p_inc.set_defaults(func=cmd_check_incidents)

    # resolve-incident
    p_res = subparsers.add_parser("resolve-incident", help="Resolver una incidencia")
    p_res.add_argument("incident_id", help="UUID de la incidencia")
    p_res.add_argument("note", help="Motivo o resolución técnica")
    p_res.set_defaults(func=cmd_resolve_incident)

    # export-csv
    p_exp = subparsers.add_parser("export-csv", help="Exportar datos a CSV")
    p_exp.add_argument("--category", help="Filtrar por categoría (ej. compresores)")
    p_exp.add_argument("--output", "-o", help="Ruta del archivo de salida")
    p_exp.set_defaults(func=cmd_export_csv)

    # backup
    p_bk = subparsers.add_parser("backup", help="Crear respaldo de datos")
    p_bk.add_argument("--dest", help="Ruta del archivo de destino")
    p_bk.set_defaults(func=cmd_backup)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
