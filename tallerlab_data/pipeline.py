"""Validación y normalización documental para TallerLab Data, sin ensayos físicos."""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from tallerlab_data.models import (
    CommercialOffer,
    ContradictionRecord,
    RegionalVariant,
    Specification,
    TechnicalTool,
)
from tallerlab_data.storage import (
    add_candidate,
    add_correction,
    get_tool,
    save_tool,
)

# Factores de conversión estándar físicos
HP_TO_W = 745.7
CV_TO_W = 735.49875
BAR_TO_PSI = 14.50377
CFM_TO_LPM = 28.3168
LPH_TO_LPM = 1.0 / 60.0

VALID_CATEGORIES = {
    "compresores",
    "hidrolavadoras",
    "taladros",
    "amoladoras",
    "soldadoras",
    "generadores",
    "sierras",
}


def _clean_number_locale(val_str: str) -> Optional[float]:
    """Interpreta números con separadores de miles y decimales en formato español/argentino."""
    s = val_str.strip()
    if not s:
        return None

    # Caso: miles con punto y decimal con coma: "1.750,5" -> "1750.5"
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    # Caso: solo punto pero representa miles: "1.750" o "2.800"
    elif re.match(r"^\d{1,3}\.\d{3}$", s):
        s = s.replace(".", "")
    # Caso: solo coma como decimal: "2,5" -> "2.5"
    elif "," in s:
        s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return None


def normalize_unit_value(raw_val: str, unit_type: str) -> Tuple[Optional[float], str]:
    """Extrae valor numérico y unidad normalizada a partir de un texto de especificación."""
    if not raw_val or raw_val.lower() in ("no informado", "no consta", "no aplica", "a confirmar", "—"):
        return None, unit_type

    # 1. Separar la declaración primaria de equivalencias secundarias entre paréntesis
    parenthetical_match = re.search(r"\((.*?)\)", raw_val)
    secondary_text = parenthetical_match.group(1).strip() if parenthetical_match else ""
    primary_text = re.sub(r"\(.*?\)", "", raw_val).strip()

    text_to_eval = primary_text if primary_text else raw_val

    # Manejar rangos: "0–2.800 rpm" o "1,3–2,4 kg" o "20 a 130 bar"
    range_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:[–—-]|a|hasta)\s*(\d+(?:[.,]\d+)?)", text_to_eval)
    # A scalar API cannot encode intervals or multiple conditions. Preserve the
    # original observation instead of selecting an arbitrary endpoint.
    unit_alias = {"presion": "bar", "pressure": "bar", "caudal": "L/min", "flujo": "L/min", "flow": "L/min", "torque": "Nm", "nm": "Nm", "velocidad": "rpm", "speed": "rpm", "peso": "kg"}
    if range_match:
        return None, unit_alias.get(unit_type, unit_type)
    if unit_type in ("torque", "nm", "rpm", "velocidad", "speed", "presion", "bar", "psi", "caudal", "flujo", "flow", "l/min", "l/h") and re.search(r"\d\s*/\s*\d", text_to_eval):
        return None, unit_alias.get(unit_type, unit_type)

    # Manejar potencia
    if unit_type in ("w", "hp", "potencia", "power"):
        # Si W o kW está explícito, preferir Watts directos
        kw_direct = re.search(r"(\d+(?:[.,]\d+)?)\s*kw", raw_val, re.IGNORECASE)
        w_direct = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:w|watt|watts)", raw_val, re.IGNORECASE)
        hp_direct = re.search(r"(\d+(?:[.,]\d+)?)\s*hp", raw_val, re.IGNORECASE)
        cv_direct = re.search(r"(\d+(?:[.,]\d+)?)\s*cv", raw_val, re.IGNORECASE)

        if kw_direct:
            val = _clean_number_locale(kw_direct.group(1))
            if val is not None:
                return round(val * 1000.0, 1), "W"
        elif w_direct:
            val = _clean_number_locale(w_direct.group(1))
            if val is not None:
                return round(val, 1), "W"
        elif hp_direct:
            val = _clean_number_locale(hp_direct.group(1))
            if val is not None:
                return round(val * HP_TO_W, 1), "W"
        elif cv_direct:
            val = _clean_number_locale(cv_direct.group(1))
            if val is not None:
                return round(val * CV_TO_W, 1), "W"

    # Manejar presión
    elif unit_type in ("bar", "psi", "presion", "pressure"):
        bar_match = re.search(r"(\d+(?:[.,]\d+)?)\s*bar", text_to_eval, re.IGNORECASE)
        psi_match = re.search(r"(\d+(?:[.,]\d+)?)\s*psi", text_to_eval, re.IGNORECASE)
        mpa_match = re.search(r"(\d+(?:[.,]\d+)?)\s*mpa", text_to_eval, re.IGNORECASE)

        if bar_match:
            val = _clean_number_locale(bar_match.group(1))
            if val is not None:
                return round(val, 2), "bar"
        elif psi_match:
            val = _clean_number_locale(psi_match.group(1))
            if val is not None:
                return round(val / BAR_TO_PSI, 2), "bar"
        elif mpa_match:
            val = _clean_number_locale(mpa_match.group(1))
            if val is not None:
                return round(val * 10.0, 2), "bar"

    # Manejar caudal / flujo
    elif unit_type in ("l/min", "l/h", "caudal", "flujo", "flow"):
        lpm_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:l/min|lpm|litros/min)", text_to_eval, re.IGNORECASE)
        lph_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:l/h|lph|litros/hora)", text_to_eval, re.IGNORECASE)
        cfm_match = re.search(r"(\d+(?:[.,]\d+)?)\s*cfm", text_to_eval, re.IGNORECASE)

        if lpm_match:
            val = _clean_number_locale(lpm_match.group(1))
            if val is not None:
                return round(val, 2), "L/min"
        elif lph_match:
            val = _clean_number_locale(lph_match.group(1))
            if val is not None:
                return round(val * LPH_TO_LPM, 2), "L/min"
        elif cfm_match:
            val = _clean_number_locale(cfm_match.group(1))
            if val is not None:
                return round(val * CFM_TO_LPM, 2), "L/min"

    # Multiple gear ranges and weight ranges require separate observations.
    elif unit_type in ("rpm", "velocidad", "speed"):
        if len(re.findall(r"[–—-]", text_to_eval)) > 1 or "/" in text_to_eval:
            return None, "rpm"
        if range_match:
            return _clean_number_locale(range_match.group(2)), "rpm"
        match = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*(?:rpm|min-1|min⁻¹)\s*", text_to_eval, re.I)
        return (_clean_number_locale(match.group(1)), "rpm") if match else (None, "rpm")

    elif unit_type in ("kg", "peso", "weight"):
        if range_match:
            return None, "kg"
        match = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*(kg|kilos|g|gramos|lb|lbs)\s*", text_to_eval, re.I)
        if not match:
            return None, "kg"
        value = _clean_number_locale(match.group(1))
        factor = {"g": 0.001, "gramos": 0.001, "lb": 0.45359237, "lbs": 0.45359237}.get(match.group(2).lower(), 1)
        return round(value * factor, 4), "kg"

    # Manejar torque
    elif unit_type in ("nm", "torque"):
        nm_match = re.search(r"(\d+(?:[.,]\d+)?)\s*nm", text_to_eval, re.IGNORECASE)
        if nm_match:
            val = _clean_number_locale(nm_match.group(1))
            if val is not None:
                return round(val, 1), "Nm"

    # Manejar energía de impacto
    elif unit_type in ("j", "joules", "impacto"):
        j_match = re.search(r"(\d+(?:[.,]\d+)?)\s*j", text_to_eval, re.IGNORECASE)
        if j_match:
            val = _clean_number_locale(j_match.group(1))
            if val is not None:
                return round(val, 2), "J"

    if unit_type in ("w", "hp", "potencia", "power", "bar", "psi", "presion", "pressure", "caudal", "flujo", "flow", "nm", "torque", "j", "energia"):
        return None, unit_type

    # Fallback genérico para números simples
    num_match = re.search(r"[-+]?\d+(?:[.,]\d+)?", text_to_eval)
    if num_match:
        val = _clean_number_locale(num_match.group(0))
        if val is not None:
            return val, unit_type

    return None, unit_type


def check_grid_compatibility(voltage_str: str) -> Tuple[bool, Optional[str]]:
    """Check explicitly declared supply; unknown supply is not assumed Argentine."""
    text = (voltage_str or "").lower().strip()
    if not text:
        return False, "Alimentación no documentada; confirmar red 220 V / 50 Hz o plataforma de batería"
    if any(word in text for word in ("nafta", "diesel", "gasolina", "4 tiempos", "2 tiempos")):
        return True, None
    if "hz" not in text and (any(word in text for word in ("cc", "dc", "v max", "batería", "bateria"))
            or re.search(r"(?<!\d)(?:10[.,]8|12|18|20|36|40|54)\s*v", text)):
        return True, None
    compact = re.sub(r"\s+", "", text)
    supports_50 = bool(re.search(r"50(?:[-/–]60)?hz", compact))
    supports_voltage = bool(re.search(r"(?<!\d)(?:220|230|240|380)(?!\d)", compact))
    if not supports_50 or not supports_voltage:
        return False, f"Alimentación '{voltage_str}' incompatible o insuficientemente documentada para la red 220 V / 50 Hz argentina"
    return True, None


def validate_candidate(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Aplica controles automáticos de identidad, coherencia y adecuación regional."""
    errors = []

    # 1. Identidad básica
    brand = payload.get("brand", "").strip()
    model = payload.get("commercial_name", "").strip()
    mpn = payload.get("mpn", "").strip()
    category = payload.get("category", "").strip().lower()

    if not brand:
        errors.append("Falta marca del fabricante")
    if not model:
        errors.append("Falta modelo comercial")
    if not mpn:
        errors.append("Falta código de fabricante o MPN oficial")
    if category not in VALID_CATEGORIES:
        errors.append(f"Categoría '{category}' no admitida en TallerLab Data")

    # 2. Control regional riguroso
    voltage = payload.get("voltage", "")
    is_compat, compat_error = check_grid_compatibility(voltage)
    if not is_compat and compat_error:
        errors.append(compat_error)

    from tallerlab_data.quality import valid_url
    sources = payload.get("primary_sources", [])
    if not sources or not isinstance(sources, list):
        errors.append("Debe incluir al menos una fuente documental")
        sources = []
    if any(not isinstance(source, dict) or not valid_url(source.get("url")) for source in sources):
        errors.append("Las fuentes deben incluir URL HTTP(S) válida")
    specs = payload.get("specs", {})
    if not isinstance(specs, dict):
        specs = {}
    if len(specs) < 2:
        errors.append("Debe incluir especificaciones técnicas comprobables (mínimo 2 parámetros)")
    for key, spec in specs.items():
        data = spec.to_dict() if isinstance(spec, Specification) else spec
        if not isinstance(data, dict):
            errors.append(f"{key}: falta estructura y procedencia por especificación")
            continue
        required = ("name", "raw_value", "condition", "applicable_variant", "applicable_market", "source_type", "source_name", "consultation_date")
        if any(not data.get(field) for field in required) or not valid_url(data.get("source_url")):
            errors.append(f"{key}: evidencia documental incompleta")
        try:
            consulted = datetime.strptime(data.get("consultation_date", ""), "%Y-%m-%d").date()
            if consulted > datetime.now(timezone.utc).date():
                errors.append(f"{key}: fecha de consulta futura")
        except (ValueError, TypeError):
            errors.append(f"{key}: fecha de consulta inválida")

    # 5. Controles de coherencia física
    p_trabajo = specs.get("presion_trabajo")
    p_max = specs.get("presion_maxima")
    if p_trabajo and p_max:
        val_trab = getattr(p_trabajo, "normalized_value", None) or (p_trabajo.get("normalized_value") if isinstance(p_trabajo, dict) else None)
        val_max = getattr(p_max, "normalized_value", None) or (p_max.get("normalized_value") if isinstance(p_max, dict) else None)
        if val_trab and val_max and val_trab > val_max:
            errors.append(f"Incoherencia de presión: trabajo ({val_trab} bar) mayor que máxima ({val_max} bar)")

    i_100 = specs.get("ciclo_trabajo_100")
    i_max = specs.get("corriente_maxima")
    if i_100 and i_max:
        val_100 = getattr(i_100, "normalized_value", None) or (i_100.get("normalized_value") if isinstance(i_100, dict) else None)
        val_imax = getattr(i_max, "normalized_value", None) or (i_max.get("normalized_value") if isinstance(i_max, dict) else None)
        if val_100 and val_imax and val_100 > val_imax:
            errors.append(f"Incoherencia de ciclo de soldadura: corriente continua ({val_100} A) mayor que máxima ({val_imax} A)")

    pot_nom = specs.get("potencia_nominal")
    pot_max = specs.get("potencia_maxima")
    if pot_nom and pot_max:
        val_pnom = getattr(pot_nom, "normalized_value", None) or (pot_nom.get("normalized_value") if isinstance(pot_nom, dict) else None)
        val_pmax = getattr(pot_max, "normalized_value", None) or (pot_max.get("normalized_value") if isinstance(pot_max, dict) else None)
        if val_pnom and val_pmax and val_pnom > val_pmax:
            errors.append(f"Incoherencia de potencia de generador: continua ({val_pnom}) mayor que pico ({val_pmax})")

    return (len(errors) == 0, errors)


def process_candidate_ingestion(candidate_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist candidates for documentary review; formal validation is not publication approval."""
    from dataclasses import asdict, is_dataclass
    def serializable(value):
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, dict):
            return {k: serializable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [serializable(v) for v in value]
        return value
    payload = serializable(candidate_payload)
    valid, errors = validate_candidate(payload)
    code = payload.get("mpn") or payload.get("slug") or "SIN-CODIGO"
    reason = "; ".join(errors) if errors else "Validación formal completa; pendiente de contrastar el documento y aprobar la variante."
    add_candidate(code, payload.get("brand", "Desconocida"), payload.get("commercial_name", "Sin modelo"),
                  payload.get("category", "general"), payload, reason)
    return {"status": "validado_para_revision" if valid else "aislado_en_staging",
            "accepted": False, "persisted_in_staging": True, "errors": errors, "code": code}


def resolve_candidate(candidate_code: str, decision: str, editorial_note: str, reviewed_tool: Optional[TechnicalTool] = None) -> Dict[str, Any]:
    """Close an editorial decision. Approval needs a complete documented tool.

    This is an operator API, never a public HTTP endpoint. Formal validation
    and automatic source recovery are not editorial approval by themselves.
    """
    from tallerlab_data import storage
    if decision not in {'aceptar', 'excluir'} or not editorial_note.strip():
        raise ValueError('Indicar aceptar/excluir y justificar la decisión documental')
    matches = [c for c in storage.list_candidates(include_test=True) if c['candidate_code'] == candidate_code]
    if not matches:
        raise ValueError('Candidato inexistente')
    if decision == 'aceptar':
        if not reviewed_tool or reviewed_tool.mpn != candidate_code:
            raise ValueError('Se requiere el modelo completo con el código exacto del candidato')
        if len(reviewed_tool.specs) < 2 or any(s.documentary_status != 'concordancia_textual' or not s.evidence_reference or not s.evidence_excerpt for s in reviewed_tool.specs.values()):
            raise ValueError('Cada observación aprobada requiere respaldo documental conservado')
        if storage.get_tool(reviewed_tool.slug):
            raise ValueError('La incorporación no sobrescribe un modelo existente; usar una revisión explícita')
        storage.save_tool(reviewed_tool)
    status = 'aceptado' if decision == 'aceptar' else 'excluido'
    from contextlib import closing
    with closing(storage.get_connection()) as connection:
        connection.execute('UPDATE candidates SET status=?, rejection_or_pending_reason=? WHERE candidate_code=?', (status, editorial_note, candidate_code))
        connection.commit()
    from tallerlab_data.documentary import write_snapshot
    version = write_snapshot()
    return {'status': status, 'accepted': decision == 'aceptar', 'persisted': True, 'version': version}


def record_price_observation(
    tool_slug: str,
    seller: str,
    platform: str,
    url: str,
    observed_price_ars: float,
    observation_date: Optional[str] = None,
    evidence_reference: str = "",
    availability: str = "desconocida",
    variant_code: str = "",
    kit_code: str = ""
) -> bool:
    """Registra una observación exacta de oferta comercial sin inventar series."""
    tool = get_tool(tool_slug)
    from tallerlab_data.quality import valid_url
    import math
    if (not tool or not valid_url(url) or not evidence_reference or not isinstance(observed_price_ars, (int, float))
            or not math.isfinite(observed_price_ars) or observed_price_ars <= 0):
        return False

    date_str = observation_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        if datetime.strptime(date_str, "%Y-%m-%d").date() > datetime.now(timezone.utc).date():
            return False
    except ValueError:
        return False
    offer = CommercialOffer(
        seller=seller,
        platform=platform,
        url=url,
        observed_price_ars=observed_price_ars,
        observation_date=date_str,
        item_condition="nuevo",
        verification_status="verificado",
        evidence_reference=evidence_reference, observed_availability=availability,
        variant_code=variant_code, kit_code=kit_code,
    )

    tool.commercial_offers.append(offer)
    save_tool(tool)
    return True
