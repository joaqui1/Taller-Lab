import re
from typing import Any, Dict, List, Optional
from tallerlab_data.models import TechnicalTool


def analyze_spec_comparability(
    spec_key: str,
    specs_by_tool: List[Optional[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Determina si una especificación entre 2 o más modelos es directamente comparable."""
    present_specs = [s for s in specs_by_tool if s is not None]

    # Si falta el dato en algún modelo de una selección multi-modelo (ej. 2 de 3)
    if len(present_specs) < len(specs_by_tool) and len(specs_by_tool) > 2:
        return {
            "is_comparable": False,
            "warning": "Dato incompleto en la selección: al menos un modelo no informa este parámetro en su documentación oficial.",
            "status_badge": "incompleto",
        }

    if len(present_specs) < 2:
        return {
            "is_comparable": False,
            "warning": "Dato disponible en solo un modelo de la selección.",
            "status_badge": "incompleto",
        }

    def _prop(s: Any, prop: str) -> str:
        if isinstance(s, dict):
            return str(s.get(prop, "") or "")
        return str(getattr(s, prop, "") or "")

    # 1. Discrepancia por estado contradictorio: impide conclusiones cuantitativas
    if any(_prop(s, "status") == "contradictorio" for s in present_specs):
        return {
            "is_comparable": False,
            "warning": "DATO CONTRADICTORIO DOCUMENTADO: Una de las fichas presenta divergencias sin resolver entre manual oficial y catálogo web.",
            "status_badge": "contradictorio",
        }

    import math
    def _value(item):
        return item.get("normalized_value") if isinstance(item, dict) else getattr(item, "normalized_value", None)
    if any(_prop(item, "status") not in {"declarado", "medido", "calculado"}
           or isinstance(_value(item), bool) or not isinstance(_value(item), (int, float)) or not math.isfinite(_value(item)) for item in present_specs):
        return {"is_comparable": False, "warning": "Dato ausente o sin valor normalizado válido.", "status_badge": "incompleto"}
    # Same magnitude published in different flow units (L/h vs L/min) is
    # converted before comparing; other unit mismatches stay incomparable.
    def _to_common(item):
        unit = _prop(item, "normalized_unit").strip().lower().replace(" ", "")
        if unit not in {"l/h", "lph"}:
            return item
        data = dict(item) if isinstance(item, dict) else dict(vars(item))
        if True:
            data["normalized_value"] = _value(item) / 60.0
            data["normalized_unit"] = "L/min"
        return data
    present_specs = [_to_common(item) for item in present_specs]
    normalized_units = {_prop(item, "normalized_unit").strip().lower() for item in present_specs}
    if "" in normalized_units or len(normalized_units) != 1:
        return {"is_comparable": False, "warning": "Unidades normalizadas distintas o desconocidas: convertir a una misma magnitud antes de comparar.", "status_badge": "incomparable"}

    import unicodedata
    def plain(value):
        return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))
    conditions = [plain(_prop(s, 'condition')).strip() for s in present_specs]
    contexts = [plain(_prop(s, 'name') + ' ' + _prop(s, 'condition')) for s in present_specs]
    def uncertain(message):
        return {'is_comparable': False, 'warning': 'NO DIRECTAMENTE COMPARABLE: ' + message, 'status_badge': 'indeterminado'}
    if any(not c or any(word in c for word in ('no document', 'no inform', 'desconocid', 'a confirmar', 'sin dato')) or c in {'—', '-'} for c in conditions):
        return uncertain('Condición documental desconocida: no se puede establecer equivalencia técnica.')
    if any(_prop(s, 'source_type') in {'referencia_no_contrastada', 'procedencia_pendiente'} for s in present_specs):
        return uncertain('Referencia sin contraste documental: no se utiliza para establecer equivalencia técnica.')
    if any(_prop(s, 'documentary_status') in {'sin_respaldo', 'identidad_no_coincidente', 'referencia_comercial'} for s in present_specs):
        return uncertain('Dato conservado como referencia, excluido de conclusiones cuantitativas por falta de respaldo documental suficiente.')
    if any(_prop(s, 'condition_status') == 'sin_respaldo' for s in present_specs):
        return uncertain('El valor tiene referencia, pero el protocolo o condición de ensayo atribuido no tiene respaldo en el documento.')
    if any(k in spec_key for k in ('potencia', 'corriente')):
        modes = [('maxima' if 'maxim' in text or 'pico' in text else 'nominal' if 'nominal' in text or 'continu' in text else 'no_identificada') for text in contexts]
        dimensions = [('absorbida' if 'absorb' in text or 'entrada' in text else 'salida' if 'salida' in text else 'no_identificada') for text in contexts]
        if len(set(modes)) != 1 or len(set(dimensions)) != 1:
            return uncertain('Potencia/corriente nominal, máxima, absorbida y de salida requieren el mismo significado físico.')
    if 'torque' in spec_key:
        kinds = []
        for text, spec in zip(contexts, present_specs):
            if re.search(r'\d\s*/\s*\d', _prop(spec, 'raw_value')) or ('duro' in text and 'blando' in text):
                return uncertain('Torque con más de una condición: consultar los valores originales; no reducir duro/blando a una sola cifra.')
            kinds.append('impacto' if 'impacto' in text else 'duro' if 'duro' in text else 'blando' if 'blando' in text else None)
        if None in kinds or len(set(kinds)) != 1:
            return uncertain('Torque duro, blando o de impacto: solo se comparan valores con el mismo método declarado.')
    if any(k in spec_key for k in ('caudal', 'flujo', 'aspirado', 'desplazado')):
        kinds = []
        for text in contexts:
            kinds.append('aspiracion' if any(w in text for w in ('aspir', 'teoric', 'desplaz')) else 'salida' if any(w in text for w in ('salida', 'entrega', 'fad', 'efectiv')) or re.search(r'\d\s*(bar|psi|mpa)', text) else None)
        if None in kinds or len(set(kinds)) != 1:
            return uncertain('No se ha establecido el mismo tipo de caudal: aspiración y entrega efectiva son parámetros distintos.')
        qualifiers = [('maximo' if 'maxim' in text else 'nominal' if 'nominal' in text or 'continu' in text else 'sin_clasificar') for text in contexts]
        if len(set(qualifiers)) != 1:
            return uncertain('Caudal máximo y nominal/continuo no son equivalentes.')
    if any(k in spec_key for k in ('peso', 'masa', 'weight')):
        kinds = []
        for text in contexts:
            kinds.append('cuerpo' if any(w in text for w in ('sin bateria', 'solo herramienta', 'solo cuerpo', 'bare', 'sin cable')) else 'equipado' if any(w in text for w in ('con bateria', 'equipo completo', 'con tanque')) else 'neto' if 'neto' in text or 'seco' in text else None)
        if None in kinds or len(set(kinds)) != 1:
            return uncertain('Configuración de peso no equivalente o no documentada: cuerpo, batería y accesorios deben coincidir.')
    if spec_key in {'nivel_sonoro', 'ruido'}:
        kinds = ['lpa' if 'lpa' in text else 'lwa' if 'lwa' in text else None for text in contexts]
        if None in kinds or len(set(kinds)) != 1 or len(set(conditions)) != 1:
            return uncertain('Ruido: se requiere la misma magnitud acústica, distancia y condición declarada.')

    # 2. Magnitudes físicas o unidades no equivalentes (ej. kVA vs kW)
    units = set(_prop(s, "normalized_unit").strip().upper() for s in present_specs if _prop(s, "normalized_unit"))
    if "KVA" in units and "KW" in units:
        return {
            "is_comparable": False,
            "warning": "MAGNITUDES FÍSICAS DISTINTAS: No es directamente comparable potencia aparente (kVA) con potencia activa (kW) sin considerar el factor de potencia (cos phi).",
            "status_badge": "incomparable",
        }

    # 3. Caudal en compresores: aspiración vs salida efectiva y distintas presiones de ensayo
    if any(k in spec_key for k in ("caudal", "flujo", "desplazado", "aspirado")):
        conditions = [_prop(s, "condition").lower() for s in present_specs]
        has_pressure_ref = any("bar" in c or "psi" in c for c in conditions)
        has_free_flow = any("aspirad" in c or "aspirac" in c or "desplaz" in c or "teóric" in c or "teoric" in c or "sin presión" in c or "sin presion" in c or "sin carga" in c for c in conditions)

        if has_pressure_ref and has_free_flow:
            return {
                "is_comparable": False,
                "warning": "NO DIRECTAMENTE COMPARABLE: Una herramienta declara caudal de salida a presión de trabajo calibrada y otra declara aspiración o desplazamiento teórico sin presión de salida.",
                "status_badge": "incomparable",
            }

        # Cotejar si declaran presiones de ensayo distintas (ej. 4 bar vs 7 bar)
        pressures = []
        for condition in conditions:
            matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*(bar|psi|mpa)", condition)
            values = {round(float(value.replace(",", ".")) * {"bar": 1, "psi": 1 / 14.50377, "mpa": 10}[unit], 2)
                      for value, unit in matches}
            if len(values) != 1:
                if has_pressure_ref:
                    return {"is_comparable": False, "warning": "Presión de ensayo ausente o ambigua.", "status_badge": "indeterminado"}
            else:
                pressures.append(next(iter(values)))
        if pressures and max(pressures) - min(pressures) > 0.05:
            return {"is_comparable": False, "warning": "NO DIRECTAMENTE COMPARABLE: caudales a distintas presiones de ensayo.", "status_badge": "incomparable"}
        if not all(conditions):
            return {"is_comparable": False, "warning": "Condiciones de caudal no documentadas.", "status_badge": "indeterminado"}

    # 4. Base de peso no equivalente (ej. bare tool vs con batería/accesorios instalados)
    if any(k in spec_key for k in ("peso", "masa", "weight")):
        conditions = [_prop(s, "condition").lower() for s in present_specs]
        has_bare = any("sin batería" in c or "sin bateria" in c or "bare" in c or "solo cuerpo" in c for c in conditions)
        has_equipped = any("con batería" in c or "con bateria" in c or "con tanque" in c or "completo" in c for c in conditions)
        if any(not c for c in conditions):
            return {"is_comparable": False, "warning": "Configuración de pesaje no documentada; una balanza no identifica batería ni accesorios.", "status_badge": "indeterminado"}
        if has_bare and has_equipped:
            return {
                "is_comparable": False,
                "warning": "NO DIRECTAMENTE COMPARABLE: La base de peso declarada difiere (ej. peso del cuerpo solo sin batería vs equipo completo con batería o accesorios instalados).",
                "status_badge": "incomparable",
            }

    # 5. Presión en hidrolavadoras (trabajo continuo vs máxima de corte)
    if any(k in spec_key for k in ("presion",)):
        is_trabajo = any("trabajo" in _prop(s, "name").lower() or "servicio" in _prop(s, "name").lower() for s in present_specs)
        is_maxima = any("máxima" in _prop(s, "name").lower() or "admisible" in _prop(s, "name").lower() for s in present_specs)

        if is_trabajo and is_maxima:
            return {
                "is_comparable": False,
                "warning": "ATENCIÓN: Se cruza presión de trabajo continuo con presión máxima de descarga o corte. La presión máxima no es sostenible en aplicación continuada.",
                "status_badge": "precaucion",
            }

    return {
        "is_comparable": True,
        "warning": None,
        "status_badge": "comparable",
    }


class ComparisonCell:
    def __init__(self, raw_value, condition, status, source_name, document_page, notes, normalized_value=None, normalized_unit="", incomparability_warning=None):
        self.raw_value = raw_value
        self.original_value = raw_value
        self.condition = condition
        self.status = status
        self.source_name = source_name
        self.document_page = document_page
        self.notes = notes
        self.normalized_value = normalized_value
        self.normalized_unit = normalized_unit
        self.incomparability_warning = incomparability_warning

    def get(self, item, default=None):
        return getattr(self, item, default)

    def __getitem__(self, item):
        return getattr(self, item)


class ComparisonRow:
    def __init__(self, key, name, spec_name, is_comparable, warning, status_badge, cells, values):
        self.key = key
        self.name = name
        self.spec_name = spec_name or name
        self.is_comparable = is_comparable
        self.warning = warning
        self.status_badge = status_badge
        self.cells = cells
        self.values = values

    def get(self, item, default=None):
        return getattr(self, item, default)

    def __getitem__(self, item):
        return getattr(self, item)


class ComparisonResult(dict):
    def __init__(self, tools, rows, editorial_verdict_notice="", category_mismatch=False, category_warning=""):
        super().__init__(
            tools=tools,
            rows=rows,
            editorial_verdict_notice=editorial_verdict_notice,
            category_mismatch=category_mismatch,
            category_warning=category_warning,
        )
        self.tools = tools
        self.rows = rows
        self.editorial_verdict_notice = editorial_verdict_notice
        self.category_mismatch = category_mismatch
        self.category_warning = category_warning


SPEC_KEY_CANONICAL_MAP = {
    "mandril": "capacidad_mandril",
    "mandril_capacidad": "capacidad_mandril",
    # Same physical quantity loaded under different keys by brand.
    "manguera_alta_presion": "manguera",
    "longitud_manguera": "manguera",
    "largo_manguera": "manguera",
    # Hidrolavadoras: each brand names the same quantity differently.
    "presion_servicio": "presion_trabajo",
    "presion_admisible": "presion_maxima",
    "caudal_trabajo": "caudal_nominal",
    # Taladros / rotomartillos.
    "diametro_hormigon": "capacidad_hormigon",
    "impactos_minuto": "frecuencia_impactos",
    "peso_catalogo": "peso",
    "peso_ficha_web": "peso",
}


def _label(spec):
    try:
        from tallerlab_data.documentary import evidence_source_label
        return evidence_source_label(spec)
    except Exception:
        return spec.source_name


def compare_tools(tools: List[Any]) -> Any:
    """Genera la estructura de comparación técnica entre 2 y 4 herramientas."""
    from tallerlab_data.storage import get_tool
    resolved_tools = []
    for t in tools:
        if isinstance(t, str):
            tool_obj = get_tool(t)
            if tool_obj:
                resolved_tools.append(tool_obj)
        elif hasattr(t, "specs"):
            resolved_tools.append(t)

    if not (2 <= len(resolved_tools) <= 4):
        return ComparisonResult(tools=resolved_tools, rows=[])

    tools = resolved_tools
    from tallerlab_data.selection import family
    application_mismatch = len({family(t) for t in tools}) > 1

    # Control de categorías cruzadas
    categories = {t.category for t in tools}
    category_mismatch = len(categories) > 1
    category_warning = ""
    if category_mismatch:
        category_warning = (
            f"⚠️ ATENCIÓN: Estás comparando herramientas de distintas categorías ({', '.join(sorted(categories))}). "
            "Sus especificaciones responden a aplicaciones y principios físicos no equivalentes."
        )

    all_keys = set()
    for t in tools:
        for k in t.specs.keys():
            all_keys.add(SPEC_KEY_CANONICAL_MAP.get(k, k))

    # Orden lógico de especificaciones clave
    ordered_keys = sorted(
        all_keys,
        key=lambda k: (
            0 if "potencia" in k else
            1 if "presion" in k else
            2 if "caudal" in k or "flujo" in k else
            3 if "volumen" in k or "tanque" in k else
            4 if "torque" in k or "energia" in k else
            5 if "velocidad" in k or "impacto" in k else
            6 if "mandril" in k or "disco" in k or "husillo" in k else
            7 if "peso" in k else 10,
            k
        )
    )

    rows = []
    for key in ordered_keys:
        spec_name = None
        tool_specs = []
        for t in tools:
            # Buscar coincidencia exacta o por alias canónico
            spec = t.specs.get(key)
            if not spec:
                for alt_k, can_k in SPEC_KEY_CANONICAL_MAP.items():
                    if can_k == key and alt_k in t.specs:
                        spec = t.specs[alt_k]
                        break

            if spec:
                spec_name = spec_name or spec.name
                tool_specs.append(spec.to_dict())
            else:
                tool_specs.append(None)

        analysis = analyze_spec_comparability(key, tool_specs)

        cells = {}
        values = []
        for t in tools:
            spec = t.specs.get(key)
            if not spec:
                for alt_k, can_k in SPEC_KEY_CANONICAL_MAP.items():
                    if can_k == key and alt_k in t.specs:
                        spec = t.specs[alt_k]
                        break

            if spec:
                cell = ComparisonCell(
                    raw_value=spec.raw_value,
                    condition=spec.condition,
                    status=spec.status,
                    source_name=_label(spec),
                    document_page=spec.document_page,
                    notes=spec.notes,
                    normalized_value=spec.normalized_value,
                    normalized_unit=spec.normalized_unit,
                    incomparability_warning=analysis["warning"] if not analysis["is_comparable"] else None,
                )
            else:
                cell = None
            cells[t.slug] = cell
            values.append(cell)

        row = ComparisonRow(
            key=key,
            name=spec_name or key.replace("_", " ").capitalize(),
            spec_name=spec_name or key.replace("_", " ").capitalize(),
            is_comparable=analysis["is_comparable"],
            warning=analysis["warning"],
            status_badge=analysis["status_badge"],
            cells=cells,
            values=values,
        )
        if category_mismatch or application_mismatch:
            row.is_comparable = False
            row.warning = category_warning if category_mismatch else 'Aplicaciones distintas: estas familias usan mecanismos o configuraciones diferentes. No se establece equivalencia numérica entre ellas.'
            row.status_badge = "incomparable"
            for cell in row.values:
                if cell:
                    cell.incomparability_warning = row.warning
        rows.append(row)

    return ComparisonResult(
        tools=tools,
        rows=rows,
        editorial_verdict_notice=(
            "TallerLab no declara ganadores basándose únicamente en voltaje, torque, potencia o presión declarados. "
            "La herramienta idónea depende del ciclo de trabajo efectivo, el consumo sostenido a la presión requerida, "
            "la red eléctrica disponible y el suministro garantizado de repuestos y servicio técnico en Argentina."
        ),
        category_mismatch=category_mismatch,
        category_warning=category_warning,
    )
