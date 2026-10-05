"""
Suite de verificación exhaustiva de TallerLab Data:
1. Base de datos SQLite (100 modelos, categorías, especificaciones, trazabilidad, variantes, kits, ofertas).
2. Trazabilidad de fuentes y decisiones documentales cerradas.
3. Registro de correcciones y metodología técnica.
4. Pipeline de ingesta, normalización (HP->W, bar->PSI) y detección de incoherencias.
5. Comparador técnico multi-modelo y detección de condiciones no comparables.
6. Comparaciones editoriales curadas (6 comparaciones).
7. Estudio documental y exportación CSV de dataset de 100 modelos.
8. Enlaces bidireccionales con guías comerciales existentes de TallerLab.
"""
import sys
import os
from pathlib import Path

# Asegurar dependencias de QA
qa_paths = [
    './.qa-deps',
    './.consultor-seo-deps',
    './.publication-qa-deps',
    './.integration-qa-deps',
    './.seo-qa-deps',
    './.taladros-qa-deps',
    '.'
]
for p in qa_paths:
    if p not in sys.path:
        sys.path.insert(0, p)

import sqlite3
import csv
import io
from tallerlab_data.models import TechnicalTool, Specification, RegionalVariant
from tallerlab_data.storage import (
    get_connection, get_tool, list_tools, list_candidates, list_corrections,
    get_all_categories
)
from tallerlab_data.pipeline import (
    normalize_unit_value, validate_candidate, process_candidate_ingestion,
    record_price_observation, HP_TO_W, BAR_TO_PSI
)
from tallerlab_data.comparator import compare_tools, analyze_spec_comparability
from tallerlab_data.editorial_comparisons import get_all_editorial_comparisons, get_editorial_comparison
from tallerlab_data.research_study import get_research_study_data, generate_study_csv
from tallerlab_data.guide_links import get_tools_for_guide, render_guide_technical_tools_block
import servidor_local as site

def test_database_integrity():
    print("-> Verificando integridad de la base de datos...")
    tools = list_tools()
    assert len(tools) == 100, f"Se esperaban 100 modelos, pero hay {len(tools)}"
    
    categories = get_all_categories()
    expected_categories = {"compresores", "hidrolavadoras", "taladros", "amoladoras", "soldadoras", "generadores"}
    assert set(categories) == expected_categories, f"Categorías incorrectas: {categories}"
    
    cat_counts = {}
    for t in tools:
        cat_counts[t.category] = cat_counts.get(t.category, 0) + 1
    print(f"   Distribución por categorías: {cat_counts}")
    assert cat_counts["compresores"] == 25, f"Compresores: {cat_counts.get('compresores')}"
    assert cat_counts["hidrolavadoras"] == 25, f"Hidrolavadoras: {cat_counts.get('hidrolavadoras')}"
    assert cat_counts["taladros"] == 20, f"Taladros: {cat_counts.get('taladros')}"
    assert cat_counts["amoladoras"] == 15, f"Amoladoras: {cat_counts.get('amoladoras')}"
    assert cat_counts["soldadoras"] == 8, f"Soldadoras: {cat_counts.get('soldadoras')}"
    assert cat_counts["generadores"] == 7, f"Generadores: {cat_counts.get('generadores')}"
    
    total_specs = 0
    specs_with_sources = 0
    tools_with_220v = 0
    
    for t in tools:
        assert t.slug, f"Herramienta sin slug: {t}"
        assert t.brand, f"Herramienta sin marca: {t.slug}"
        assert t.model_name, f"Herramienta sin modelo: {t.slug}"
        assert len(t.specifications) >= 3, f"{t.slug} tiene menos de 3 especificaciones ({len(t.specifications)})"
        
        assert len(t.variants) >= 1, f"Falta variante regional en {t.slug}"
        for var in t.variants:
            assert var.voltage_frequency or var.market, f"Variante vacía en {t.slug}"
        if any(("220" in v.voltage_frequency and "50" in v.voltage_frequency) for v in t.variants):
            tools_with_220v += 1
            
        for spec in t.specifications:
            total_specs += 1
            if spec.source_name and spec.consultation_date:
                specs_with_sources += 1
            assert spec.status in {"declarado", "medido", "calculado", "contradictorio", "no_encontrado"}, f"Status inválido: {spec.status} en {t.slug}"
            assert spec.condition, f"Falta condición de medición en {t.slug}:{spec.spec_key}"
            
    assert len(tools) == 100
    assert tools_with_220v >= 70, f"Variantes 220V 50Hz registradas: {tools_with_220v}"
    assert specs_with_sources == total_specs, f"Especificaciones sin fuente: {specs_with_sources}/{total_specs}"
    print(f"   Modelos con variantes monofásicas 220V 50Hz directas: {tools_with_220v}/100 (resto: batería/combustión/trifásica)")
    print(f"   Total especificaciones registradas con fuente: {total_specs}")
    print("   [OK] Integridad de base de datos aprobada.")

def test_candidates_and_corrections():
    print("-> Verificando decisiones documentales y registro de correcciones...")
    candidates = list_candidates()
    assert len(candidates) >= 7, f"Se esperaban al menos 7 candidatos en cuarentena, hay {len(candidates)}"
    for c in candidates:
        assert c['status'] in {'aceptado', 'excluido'}, f"Decisión sin cerrar: {c['candidate_code']}"
        reason = getattr(c, 'exclusion_reason', '') or c.get('rejection_or_pending_reason', '')
        assert len(reason) > 10, f"Candidato sin motivo detallado de cuarentena: {c}"
    print(f"   Candidatos en cuarentena documentados: {len(candidates)}")
    
    corrections = list_corrections()
    assert len(corrections) >= 4, f"Se esperaban al menos 4 correcciones históricas, hay {len(corrections)}"
    for corr in corrections:
        date = getattr(corr, 'date', '') or corr.get('correction_date', '')
        reason = getattr(corr, 'reason', '') or corr.get('reason', '')
        source = getattr(corr, 'source_citation', '') or corr.get('source', '')
        assert date and reason and source, f"Corrección incompleta: {corr}"
    print(f"   Correcciones documentadas: {len(corrections)}")
    print("   [OK] Candidatos y correcciones aprobados.")

def test_pipeline_and_normalizer():
    print("-> Verificando pipeline de normalización...")
    
    # HP a Watts
    val, unit = normalize_unit_value("2.5 HP", "potencia")
    assert abs(val - (2.5 * HP_TO_W)) < 0.5 and unit == "W", f"HP a W falló: {val} {unit}"
    
    # PSI a bar
    val_bar, unit_bar = normalize_unit_value("115 PSI", "presion")
    assert abs(val_bar - 7.93) < 0.1 and unit_bar == "bar", f"PSI a bar falló: {val_bar} {unit_bar}"
    
    # Caudal l/h a l/min
    val_flow, unit_flow = normalize_unit_value("360 l/h", "caudal")
    assert abs(val_flow - 6.0) < 0.05 and unit_flow == "L/min", f"l/h a l/min falló: {val_flow}"
    
    # Ingesta candidata inválida -> aislamiento en staging
    res = process_candidate_ingestion({
        "brand": "Modelo Incompleto",
        "commercial_name": "Test100",
        "category": "compresores",
        "mpn": "",  # Sin MPN
        "voltage": "110 V / 60 Hz",  # Incompatible con Argentina
    })
    assert res["accepted"] is False
    assert res["status"] == "aislado_en_staging"
    assert any("MPN" in e for e in res["errors"])
    assert any("220 V / 50 Hz" in e for e in res["errors"])
    print("   [OK] Pipeline de validación y normalización aprobado.")

def test_comparator_logic():
    print("-> Verificando motor de comparaciones técnicas...")
    t1 = get_tool("lusqtoff-lc2550b-8")
    t2 = get_tool("gamma-g2802ar")
    assert t1 and t2, "No se encontraron los modelos para el test del comparador"
    
    comp = compare_tools(["lusqtoff-lc2550b-8", "gamma-g2802ar"])
    assert comp is not None
    assert len(comp.tools) == 2
    assert len(comp.rows) > 0
    
    # Probar análisis de comparabilidad con condiciones dispares
    s1 = Specification(
        spec_key="caudal", name="Caudal de aire", raw_value="206", raw_unit="l/min",
        normalized_value=206, normalized_unit="l/min", condition="Caudal aspirado teórico",
        applicable_variant="220V", applicable_market="AR", source_type="manual",
        source_name="Manual", source_url="https://example.com/manual.pdf", document_page="12",
        consultation_date="2026-10-01", status="declarado"
    )
    s2 = Specification(
        spec_key="caudal", name="Caudal de aire", raw_value="135", raw_unit="l/min",
        normalized_value=135, normalized_unit="l/min", condition="FAD Caudal efectivo a 6 bar",
        applicable_variant="220V", applicable_market="AR", source_type="manual",
        source_name="Manual", source_url="https://example.com/manual.pdf", document_page="15",
        consultation_date="2026-10-01", status="declarado"
    )
    res_comp = analyze_spec_comparability("caudal", [s1, s2])
    assert res_comp["is_comparable"] is False
    assert "NO DIRECTAMENTE COMPARABLE" in res_comp["warning"]
    print(f"   Detección de incomparabilidad verificada: '{res_comp['warning']}'")
    print("   [OK] Motor de comparador aprobado.")

def test_editorial_comparisons():
    print("-> Verificando comparaciones editoriales curadas...")
    editorial_list = get_all_editorial_comparisons()
    assert len(editorial_list) == 6, f"Se esperaban 6 comparaciones editoriales, hay {len(editorial_list)}"
    
    for ed in editorial_list:
        pair_comp = get_editorial_comparison(ed.slug)
        assert pair_comp is not None, f"No se pudo resolver la comparativa {ed.slug}"
        tool_a = get_tool(pair_comp.model_a_slug)
        tool_b = get_tool(pair_comp.model_b_slug)
        assert tool_a is not None, f"Herramienta A ({pair_comp.model_a_slug}) no encontrada para {ed.slug}"
        assert tool_b is not None, f"Herramienta B ({pair_comp.model_b_slug}) no encontrada para {ed.slug}"
        assert len(ed.title) > 0
        assert len(ed.editorial_analysis) > 50
    print("   [OK] Todas las 6 comparativas editoriales están enlazadas.")

def test_research_study_and_csv():
    print("-> Verificando estudio documental y exportación CSV...")
    study_data = get_research_study_data()
    metrics = study_data["metrics"]
    assert metrics["total_models_analyzed"] == 100
    assert metrics["compresores_total"] == 25
    assert metrics["hidro_total"] == 25
    assert metrics["compressors_missing_fad_count"] == len(metrics["compresores_sin_fad_slugs"])
    assert metrics["compressors_missing_fad_pct"] == round(100 * metrics["compressors_missing_fad_count"] / metrics["compresores_total"], 1)
    assert metrics["washers_advertising_peak_pressure_count"] == len(metrics["hidro_solo_max_slugs"])
    assert metrics["washers_advertising_peak_pressure_pct"] == round(100 * metrics["washers_advertising_peak_pressure_count"] / metrics["hidro_total"], 1)
    
    csv_str = generate_study_csv()
    reader = csv.reader(io.StringIO(csv_str))
    rows = list(reader)
    header = rows[0]
    data_rows = rows[1:]
    assert "slug" in header and "marca" in header and "modelo_comercial" in header
    assert len(data_rows) == sum(len(tool.specs) for tool in list_tools()), "CSV incompleto"
    assert len({row[0] for row in data_rows}) == 100
    print(f"   Dataset CSV generado con éxito: {len(data_rows)} filas.")
    print("   [OK] Estudio documental y CSV aprobados.")

def test_guide_links():
    print("-> Verificando integración con guías comerciales existentes...")
    tools_50l = get_tools_for_guide("/compresores/50-litros/")
    assert len(tools_50l) >= 2, f"Guía de 50 litros no tiene herramientas mapeadas: {tools_50l}"
    
    widget_html = render_guide_technical_tools_block("/compresores/50-litros/")
    assert "Fichas documentales" in widget_html or "Modelos de esta guía" in widget_html
    assert "LC2550B" in widget_html
    print("   [OK] Bloque de especificaciones técnicas insertado en guías correctamente.")

def main():
    print("==================================================")
    print("INICIANDO SUITE DE VERIFICACIÓN TALLERLAB DATA")
    print("==================================================")
    test_database_integrity()
    test_candidates_and_corrections()
    test_pipeline_and_normalizer()
    test_comparator_logic()
    test_editorial_comparisons()
    test_research_study_and_csv()
    test_guide_links()
    print("==================================================")
    print("TODAS LAS PRUEBAS DE TALLERLAB DATA PASARON EXITOSAMENTE (CASOS CUBIERTOS OK)")
    print("==================================================")

if __name__ == "__main__":
    import tempfile
    from contextlib import closing
    from unittest.mock import patch
    import tallerlab_data.storage as storage
    folder = Path(__file__).resolve().parent / "tmp"
    folder.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder) as temporary:
        copied = Path(temporary) / "catalog.db"
        with closing(storage.get_connection()) as original, closing(sqlite3.connect(str(copied))) as target:
            original.backup(target)
        with patch.object(storage, "DB_PATH", copied):
            main()
