"""Comandos de línea de comandos (CLI) para mantenimiento y operación de compatibilidad."""

import argparse
import json
import sys
from pathlib import Path

from compatibilidad.catalog import (
    CHANGELOG,
    EVIDENCES,
    PLATFORMS,
    CATALOG_PRODUCTS,
)
from compatibilidad.export import export_compatibility_to_csv, export_compatibility_to_json
from compatibilidad.pipeline import GLOBAL_PIPELINE
from compatibilidad.rules import evaluate_compatibility
from compatibilidad.search import GLOBAL_SEARCH_INDEX
from compatibilidad.telemetry import get_telemetry_summary


def cmd_report(args):
    """Muestra un informe integral del estado de la base de compatibilidad."""
    from compatibilidad.catalog import refresh_published_state
    refresh_published_state()
    print("=" * 70)
    print("TALLERLAB · BASE ARGENTINA DE COMPATIBILIDAD · INFORME DE ESTADO")
    print("=" * 70)
    print(f"Plataformas cubiertas: {len(PLATFORMS)}")
    for p in PLATFORMS:
        prods = [x for x in CATALOG_PRODUCTS if x.platform_id == p.id]
        print(f"  • {p.name}: {sum(x.status=='publicado' for x in prods)} verificados; {sum(x.status!='publicado' for x in prods)} pendientes")
    print("-" * 70)
    print(f"Total productos en catálogo maestro: {len(CATALOG_PRODUCTS)}")
    bat_count = sum(1 for p in CATALOG_PRODUCTS if p.product_type == "bateria")
    chg_count = sum(1 for p in CATALOG_PRODUCTS if p.product_type in ("cargador", "adaptador"))
    tool_count = sum(1 for p in CATALOG_PRODUCTS if p.product_type == "herramienta")
    print(f"  - Baterías:   {bat_count}")
    print(f"  - Cargadores: {chg_count}")
    print(f"  - Herramientas: {tool_count}")
    print(f"Evidencias primarias registradas: {len(EVIDENCES)}")
    print(f"Entradas en historial de cambios: {len(CHANGELOG)}")

    candidates = GLOBAL_PIPELINE.load_candidates()
    print("-" * 70)
    print(f"Cola de registros candidatos en estudio: {len(candidates)}")
    for c in candidates:
        print(f"  [{c.get('status', 'pendiente').upper()}] {c.get('brand')} {c.get('model_name')} (MPN: {c.get('mpn')})")
        if c.get("rejection_reason"):
            print(f"     Motivo: {c.get('rejection_reason')}")

    metrics = get_telemetry_summary()
    print("-" * 70)
    print("Telemetría agregada anónima:")
    if metrics:
        for k, v in metrics.items():
            print(f"  - {k}: {v}")
    else:
        print("  - Sin eventos registrados aún")
    print("=" * 70)


def cmd_sync(args):
    """Ejecuta el ciclo de mantenimiento y actualización de la base."""
    dry_run = getattr(args, "dry_run", False)
    print(f"Iniciando ciclo de mantenimiento (dry_run={dry_run})...")
    res = GLOBAL_PIPELINE.execute_maintenance(dry_run=dry_run,check_online=not args.offline)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print(f"Mantenimiento finalizado con estado: {res['status']}")


def cmd_export(args):
    """Exporta los datasets públicos a archivos CSV y JSON."""
    from compatibilidad.catalog import refresh_published_state
    refresh_published_state()
    assets_dir = Path(__file__).parent.parent / "assets" / "datos"
    assets_dir.mkdir(parents=True, exist_ok=True)

    csv_data = export_compatibility_to_csv()
    snapshot = json.loads(export_compatibility_to_json())
    snapshot.update(snapshot=True, live_dataset_url='https://tallerlab.com.ar/datos/compatibilidad/baterias.json')
    json_data = json.dumps(snapshot, ensure_ascii=False, indent=2)

    csv_path = assets_dir / "compatibilidad-baterias-argentina.csv"
    json_path = assets_dir / "compatibilidad-baterias-argentina.json"

    csv_path.write_text(csv_data, encoding="utf-8")
    json_path.write_text(json_data, encoding="utf-8")

    print(f"OK: Exportado CSV ({len(csv_data.encode('utf-8'))} bytes) a {csv_path}")
    print(f"OK: Exportado JSON ({len(json_data.encode('utf-8'))} bytes) a {json_path}")


def cmd_check_pair(args):
    """Verifica compatibilidad entre dos modelos desde consola."""
    from compatibilidad.catalog import refresh_published_state
    refresh_published_state()
    model_a = args.model_a
    model_b = args.model_b
    prod_a, prod_b, ev = GLOBAL_SEARCH_INDEX.check_pair(model_a, model_b)
    if not prod_a or not prod_b:
        print(f"Error: no se pudo identificar ambos productos (A: {prod_a}, B: {prod_b})")
        sys.exit(1)

    print("=" * 60)
    print(f"DICTAMEN: {prod_a.model_name} <-> {prod_b.model_name}")
    print("=" * 60)
    print(f"Veredicto: {ev.verdict}")
    print(f"Compatibilidad: {'confirmada' if ev.is_compatible else 'incompatible documentado' if ev.verdict=='Incompatible documentado' else 'sin confirmación'}")
    if ev.conditions:
        print("Condiciones obligatorias:")
        for c in ev.conditions:
            print(f"  [!] {c}")
    if ev.exclusions:
        print("Exclusiones:")
        for ex in ev.exclusions:
            print(f"  [x] {ex}")
    print(f"Resumen: {ev.summary_text}")
    print(f"Packs requeridos: {ev.required_packs_count}")
    print("Evidencias:")
    for e in ev.evidence_chain:
        print(f"  - {e.document_title} ({e.manufacturer}): {e.excerpt}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="CLI de Compatibilidad TallerLab")
    subparsers = parser.add_subparsers(dest="subcommand")

    # report
    p_report = subparsers.add_parser("report", help="Reporte general del catálogo y candidatos")
    p_report.set_defaults(func=cmd_report)

    # sync
    p_sync = subparsers.add_parser("sync", help="Ejecutar pipeline de mantenimiento")
    p_sync.add_argument("--dry-run", action="store_true", help="Ejecución de prueba sin persistir cambios")
    p_sync.add_argument("--offline",action="store_true",help="Solo informe sin consultar fuentes ni publicar")
    p_sync.set_defaults(func=cmd_sync)
    p_rollback=subparsers.add_parser('rollback',help='Restaurar una versión persistida completa')
    p_rollback.add_argument('version')
    p_rollback.set_defaults(func=lambda args: print(json.dumps({'restored':GLOBAL_PIPELINE.rollback_to_snapshot(args.version)})))
    p_approve=subparsers.add_parser('approve-source',help='Aprobar explícitamente un cambio documental revisado')
    p_approve.add_argument('product_id')
    p_approve.add_argument('text_hash')
    p_approve.add_argument('--reviewer',required=True)
    p_approve.add_argument('--note',required=True)
    p_approve.set_defaults(func=lambda args: print(json.dumps(GLOBAL_PIPELINE.approve_source_change(args.product_id,args.text_hash,args.reviewer,args.note),ensure_ascii=False)))

    # export
    p_export = subparsers.add_parser("export", help="Exportar datasets a CSV y JSON")
    p_export.set_defaults(func=cmd_export)

    # check-pair
    p_check = subparsers.add_parser("check-pair", help="Contrastar compatibilidad entre dos modelos")
    p_check.add_argument("model_a", help="Modelo o código A")
    p_check.add_argument("model_b", help="Modelo o código B")
    p_check.set_defaults(func=cmd_check_pair)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
