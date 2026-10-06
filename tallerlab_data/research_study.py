"""Estudio de investigación documental original sobre la muestra de 100 herramientas."""

import csv
import io
import json
from typing import Any, Dict, List
from tallerlab_data.storage import list_tools
from tallerlab_data.quality import usable_spec, latest_verified_offer
import re


def has_output_flow(tool):
    return any(usable_spec(spec) and ("caudal" in key or "flujo" in key)
               and (any(word in key for word in ("salida", "fad", "efectivo"))
                    or bool(re.search(r"\d+(?:[.,]\d+)?\s*(bar|psi)", spec.condition.lower())))
               and not any(word in spec.condition.lower() for word in ("aspir", "teóric", "teoric"))
               for key, spec in tool.specs.items())


def has_work_pressure(tool):
    return any(usable_spec(spec) and "presion" in key
               and any(word in key for word in ("trabajo", "servicio", "nominal"))
               for key, spec in tool.specs.items())


def has_epta_energy(tool):
    return any(usable_spec(spec) and spec.condition_status != 'sin_respaldo' and "energia" in key
               and "epta" in ((spec.condition or "") + " " + (spec.notes or "")).lower()
               for key, spec in tool.specs.items())


def generate_research_study_metrics() -> Dict[str, Any]:
    """Calcula métricas factuales y trazables directamente a partir de la muestra de herramientas."""
    tools = list_tools()
    total_tools = len(tools)
    if total_tools == 0:
        return {
            "sample_size": 0,
            "by_category": {},
            "total_specs_analyzed": 0,
            "pct_specs_conditioned": 0.0,
            "compresores_total": 0,
            "compresores_fad_count": 0,
            "compresores_sin_fad_count": 0,
            "pct_compresores_solo_teorico": 0.0,
            "pct_compresores_fad": 0.0,
            "compresores_sin_fad_slugs": [],
            "hidro_total": 0,
            "hidro_trabajo_separada_count": 0,
            "hidro_solo_max_count": 0,
            "pct_hidro_separada": 0.0,
            "pct_hidro_solo_max": 0.0,
            "hidro_solo_max_slugs": [],
            "contradictions_count": 0,
            "pct_contradictions": 0.0,
            "contradictions_slugs": [],
            "rotary_hammers_total": 0,
            "rotary_hammers_epta_count": 0,
            "pct_rotary_hammers_epta": 0.0,
        }

    by_category: Dict[str, int] = {}
    contradictions_slugs: List[str] = []
    specs_with_conditions = 0
    total_specs = 0

    compresores_total = 0
    compresores_con_fad_slugs: List[str] = []
    compresores_sin_fad_slugs: List[str] = []

    hidro_total = 0
    hidro_con_trabajo_slugs: List[str] = []
    hidro_solo_max_slugs: List[str] = []

    rotary_hammers_total = 0
    rotary_hammers_epta_slugs: List[str] = []

    for t in tools:
        by_category[t.category] = by_category.get(t.category, 0) + 1
        if t.contradictions:
            contradictions_slugs.append(t.slug)

        for s in t.specs.values():
            total_specs += 1
            if s.condition and s.condition != "—":
                specs_with_conditions += 1

        if t.category == "compresores":
            compresores_total += 1
            # Verifica si publica caudal de salida efectivo bajo presión (4 bar, 7 bar, FAD)
            has_fad = has_output_flow(t)
            if has_fad:
                compresores_con_fad_slugs.append(t.slug)
            else:
                compresores_sin_fad_slugs.append(t.slug)

        if t.category == "hidrolavadoras":
            hidro_total += 1
            # Verifica si separa presión de trabajo continuo de presión máxima
            has_trabajo = has_work_pressure(t)
            if has_trabajo:
                hidro_con_trabajo_slugs.append(t.slug)
            else:
                hidro_solo_max_slugs.append(t.slug)

        # Detección de rotomartillos electroneumáticos y cumplimiento EPTA
        if t.category == "taladros" and ("rotomartillo" in t.commercial_name.lower() or "gbh" in t.slug or "dch" in t.slug or t.slug.startswith("makita-hr")):
            rotary_hammers_total += 1
            epta_found = has_epta_energy(t)
            if epta_found:
                rotary_hammers_epta_slugs.append(t.slug)

    compresores_fad_count = len(compresores_con_fad_slugs)
    compresores_sin_fad_count = len(compresores_sin_fad_slugs)
    pct_compresores_fad = round((compresores_fad_count / max(compresores_total, 1)) * 100, 1)
    pct_compresores_solo_teorico = round((compresores_sin_fad_count / max(compresores_total, 1)) * 100, 1)

    hidro_trabajo_separada_count = len(hidro_con_trabajo_slugs)
    hidro_solo_max_count = len(hidro_solo_max_slugs)
    pct_hidro_separada = round((hidro_trabajo_separada_count / max(hidro_total, 1)) * 100, 1)
    pct_hidro_solo_max = round((hidro_solo_max_count / max(hidro_total, 1)) * 100, 1)

    contradictions_count = len(contradictions_slugs)
    pct_contradictions = round((contradictions_count / total_tools) * 100, 1)
    pct_specs_conditioned = round((specs_with_conditions / max(total_specs, 1)) * 100, 1)

    pct_rotary_epta = round((len(rotary_hammers_epta_slugs) / max(rotary_hammers_total, 1)) * 100, 1) if rotary_hammers_total else 0.0

    return {
        "sample_size": total_tools,
        "by_category": by_category,
        "total_specs_analyzed": total_specs,
        "pct_specs_conditioned": pct_specs_conditioned,
        "compresores_total": compresores_total,
        "compresores_fad_count": compresores_fad_count,
        "compresores_sin_fad_count": compresores_sin_fad_count,
        "pct_compresores_solo_teorico": pct_compresores_solo_teorico,
        "pct_compresores_fad": pct_compresores_fad,
        "compresores_sin_fad_slugs": compresores_sin_fad_slugs,
        "hidro_total": hidro_total,
        "hidro_trabajo_separada_count": hidro_trabajo_separada_count,
        "hidro_solo_max_count": hidro_solo_max_count,
        "pct_hidro_separada": pct_hidro_separada,
        "pct_hidro_solo_max": pct_hidro_solo_max,
        "hidro_solo_max_slugs": hidro_solo_max_slugs,
        "contradictions_count": contradictions_count,
        "pct_contradictions": pct_contradictions,
        "contradictions_slugs": contradictions_slugs,
        "rotary_hammers_total": rotary_hammers_total,
        "rotary_hammers_epta_count": len(rotary_hammers_epta_slugs),
        "pct_rotary_hammers_epta": pct_rotary_epta,
        "rotary_hammers_epta_slugs": rotary_hammers_epta_slugs,
    }


def classify_tool(tool):
    """Coverage within this database; absence is not a claim about the manufacturer."""
    return ("disponible" if tool.category == "compresores" and has_output_flow(tool) else "no_cargado",
            "disponible" if tool.category == "hidrolavadoras" and has_work_pressure(tool) else "no_cargado",
            "declarado" if tool.category == "taladros" and has_epta_energy(tool) else "no_cargado")


def export_study_dataset_csv() -> str:
    """One row per observation, including the classifications used by the metrics."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    from tallerlab_data.selection import family
    writer.writerow(["slug", "marca", "modelo_comercial", "mpn_oficial", "categoria",
                     "especificacion", "nombre", "valor_original", "unidad_original", "valor_normalizado",
                     "unidad_normalizada", "condicion", "variante", "mercado", "estado", "tipo_fuente",
                     "fuente_nombre", "fuente_url", "pagina", "fecha_consulta", "notas",
                     "caudal_salida_en_base", "presion_trabajo_en_base", "energia_epta_en_base",
                     "discrepancia_documentada", "ultimo_precio_observado_ars", "fecha_precio_observado", "evidencia_precio", "respaldo_documental", "huella_evidencia", "coincidencia_textual", "respaldo_condicion", "familia_aplicacion"])
    for tool in list_tools():
        fad, pressure, epta = classify_tool(tool)
        offer = latest_verified_offer(tool)
        for key, spec in tool.specs.items():
            writer.writerow([tool.slug, tool.brand, tool.commercial_name, tool.mpn, tool.category,
                             key, spec.name, spec.raw_value, spec.raw_unit, spec.normalized_value,
                             spec.normalized_unit, spec.condition, spec.applicable_variant, spec.applicable_market,
                             spec.status, spec.source_type, spec.source_name, spec.source_url, spec.document_page,
                             spec.consultation_date, spec.notes, fad, pressure, epta, bool(tool.contradictions),
                             offer.observed_price_ars if offer else "", offer.observation_date if offer else "",
                             offer.evidence_reference if offer else "", spec.documentary_status, spec.evidence_reference, spec.evidence_excerpt, spec.condition_status, family(tool)])
    return output.getvalue()


generate_study_csv = export_study_dataset_csv


def get_research_study_data() -> Dict[str, Any]:
    """Retorna los datos y métricas exactos del estudio sin valores por defecto simulados."""
    metrics = generate_research_study_metrics()

    # Mapeo factual a nombres de claves públicas
    total_models = metrics["sample_size"]
    comp_total = metrics["compresores_total"]
    comp_missing_fad = metrics["compresores_sin_fad_count"]
    comp_missing_pct = metrics["pct_compresores_solo_teorico"]

    hidro_total = metrics["hidro_total"]
    hidro_peak = metrics["hidro_solo_max_count"]
    hidro_peak_pct = metrics["pct_hidro_solo_max"]

    contra_count = metrics["contradictions_count"]
    contra_pct = metrics["pct_contradictions"]

    metrics["total_models_analyzed"] = total_models
    metrics["compressors_missing_fad_pct"] = comp_missing_pct
    metrics["compressors_missing_fad_count"] = comp_missing_fad
    metrics["total_compressors_analyzed"] = comp_total

    metrics["washers_advertising_peak_pressure_pct"] = hidro_peak_pct
    metrics["washers_advertising_peak_pressure_count"] = hidro_peak
    metrics["total_washers_analyzed"] = hidro_total

    metrics["rotary_hammers_epta_compliance_pct"] = metrics["pct_rotary_hammers_epta"]
    metrics["documented_contradictions_pct"] = contra_pct
    metrics["documented_contradictions_count"] = contra_count
    metrics["inferred_data_tolerance_pct"] = None

    return {
        "publication_date": "Octubre 2026",
        "metrics": metrics,
    }

