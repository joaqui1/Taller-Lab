"""Semilla maestra y utilidades de carga de TallerLab Data."""

from typing import Dict, List, Optional
from tallerlab_data.catalog_data.common import make_spec
from tallerlab_data.catalog_data import ALL_TOOLS
from tallerlab_data.models import (
    Specification,
    TechnicalTool,
)
from tallerlab_data.storage import (
    add_candidate,
    add_correction,
    init_db,
    save_tool,
)


PENDING_CANDIDATES = [
    {
        "code": "SKIL-9002-OLD",
        "brand": "Skil",
        "model": "9002 (edición 2009)",
        "category": "amoladoras",
        "reason": "Manual F 000 622 318 de 2009 indica 600 W, discrepando con la edición 2015 de 700 W. Pendiente de verificación de lote físico importado en Argentina.",
    },
    {
        "code": "SCHULZ-CSV20-60HZ",
        "brand": "Schulz",
        "model": "MAX CSV 20/200 (922.9303-0)",
        "category": "compresores",
        "reason": "Ficha oficial disponible corresponde a 220 V / 60 Hz (Brasil). No se encontró manual oficial verificado para variante 50 Hz con distribución activa en Argentina.",
    },
    {
        "code": "STANLEY-FHY227-EU",
        "brand": "Stanley Fatmax",
        "model": "FHY227/10/24V",
        "category": "compresores",
        "reason": "Documentación técnica localizada en Mecafer (Europa). No hay importador oficial que acredite certificación IRAM y garantía para ese código exacto en Argentina.",
    },
    {
        "code": "BOSCH-STEP-2608597519",
        "brand": "Bosch",
        "model": "Mecha escalonada 2608597519",
        "category": "taladros",
        "reason": "La oferta comercial no detalla los diámetros de cada escalón en el catálogo local; pendiente de contrastar con código 2608597524.",
    },
    {
        "code": "NIWA-NPRO-HDNW",
        "brand": "Niwa",
        "model": "HDNW-700 comercial",
        "category": "hidrolavadoras",
        "reason": "Los vendedores declaran caudal promedio sin precisar norma de ensayo (IEC/EN 60335-2-79). Pendiente despiece de fábrica con régimen continuo.",
    },
    {
        "code": "TOTAL-TS223558-4",
        "brand": "Total",
        "model": "TS223558-4 Sensitiva",
        "category": "sierras",
        "reason": "La oferta anuncia 3.800 rpm mientras la fábrica declara 3.700 rpm para TS223558 sin sufijo. Pendiente manual con placa del sufijo -4.",
    },
    {
        "code": "BLACK-DECKER-BES603-B2",
        "brand": "Black+Decker",
        "model": "BES603 Caladora",
        "category": "sierras",
        "reason": "La ficha B2 no desglosa acero dulce vs inoxidable en el espesor de 6 mm en metal. Pendiente confirmación de garantía de lote argentino.",
    },
]

INITIAL_CORRECTIONS = [
    {
        "date": "2026-10-01",
        "tool_slug": "gamma-g2802ar",
        "field_affected": "potencia_motor",
        "old_value": "2,0 HP (afirmación comercial previa)",
        "new_value": "2,5 HP en manual / 2,0 HP en web oficial (estado contradictorio)",
        "reason": "Auditoría documental reveló discrepancia entre manual oficial de servicio y folleto de producto. Se preservan ambas fuentes sin suposición.",
        "source": "Manual Gamma G2802AR pág. 2 y web oficial gammaherramientas.com.ar"
    },
    {
        "date": "2026-10-01",
        "tool_slug": "skil-9002ar",
        "field_affected": "potencia",
        "old_value": "600 W (manual 2009)",
        "new_value": "700 W (manual 2015) vs 600 W (manual 2009)",
        "reason": "Actualización de manual oficial de Skil ed. febrero 2015 reemplazó la versión de 2009 para unidades con sufijo AR.",
        "source": "Manual SKIL 1 600 A00 9XF pág. 12"
    },
    {
        "date": "2026-10-01",
        "tool_slug": "lusqtoff-sml120-8dk",
        "field_affected": "tension_alimentacion",
        "old_value": "220 V (suposición por mercado argentino)",
        "new_value": "200 V según ficha web oficial / 220 V tensión nominal argentina",
        "reason": "La ficha del fabricante imprime textualmente 200 V. Se registró la advertencia en lugar de corregir silenciosamente a 220 V.",
        "source": "Ficha oficial lusqtoff.com.ar/ver-producto/SML120-8DK"
    },
    {
        "date": "2026-10-01",
        "tool_slug": "makita-gb801",
        "field_affected": "velocidad_vacio",
        "old_value": "3.450 rpm (dato de 60 Hz tomado erróneamente)",
        "new_value": "2.850 rpm (50 Hz Argentina) / 3.450 rpm (60 Hz)",
        "reason": "La velocidad de sincronismo de motor de inducción a 50 Hz en Argentina es 2.850 rpm. Se aclaró la dependencia de frecuencia.",
        "source": "Catálogo Makita Argentina 2025 pág. 49"
    }
]


def seed_database() -> None:
    init_db()
    from tallerlab_data.storage import get_tool
    for tool in ALL_TOOLS:
        if get_tool(tool.slug) is None:
            save_tool(tool)

    from tallerlab_data.storage import list_candidates
    existing_candidates = {c['candidate_code'] for c in list_candidates()}
    for cand in PENDING_CANDIDATES:
        if cand['code'] in existing_candidates:
            continue
        add_candidate(
            cand["code"],
            cand["brand"],
            cand["model"],
            cand["category"],
            cand,
            cand["reason"], status='excluido'
        )

    for corr in INITIAL_CORRECTIONS:
        add_correction(
            corr["date"],
            corr["tool_slug"],
            corr["field_affected"],
            corr["old_value"],
            corr["new_value"],
            corr["reason"],
            corr["source"]
        )
