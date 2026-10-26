"""Optional, owner-approved editorial content for product compatibility pages."""

from __future__ import annotations

from datetime import datetime
from html import escape
import json
from pathlib import Path
from typing import Any, Mapping

from compatibilidad import catalog
from compatibilidad.presentation import product_path
from compatibilidad.sources import official_url


DATA_PATH = Path(__file__).parent / "data" / "fichas_editorial.json"
_UNIT_WHITELIST = {
    "V", "Ah", "Wh", "kg", "g", "mm", "cm", "min", "h", "W", "rpm",
    "tipo de relación", "condición", "presentación", "elemento", "texto",
    "pregunta", "respuesta", "archivo", "texto alternativo", "autor o licencia",
    "crédito visible",
}
_SPEC_UNITS = {
    "voltage": {"V"},
    "capacity_ah": {"Ah"},
    "energy_wh": {"Wh"},
    "weight": {"kg", "g"},
    "dimensions": {"mm", "cm"},
    "cell_technology": {"texto"},
}
_DATE_FORMAT = "%d/%m/%Y"


def _load_data() -> dict[str, Any]:
    try:
        value = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


# Loaded once per process. Editorial publishing requires a deploy/restart like other static data.
EDITORIAL_FICHAS: dict[str, Any] = _load_data()
_ROOT_METADATA_KEYS = {
    "$schema", "version", "fecha_investigacion", "investigacion_keywords", "fuentes", "productos",
    "_schema_version", "_instructions",
}
_ALLOWED_FICHA_KEYS = {
    "publicado", "compatibility", "specifications", "charge_times", "tool",
    "identification", "common_errors", "faqs", "image",
}


def get_published_ficha(product_id: str) -> dict[str, Any] | None:
    ficha = EDITORIAL_FICHAS.get(product_id)
    if isinstance(ficha, dict) and ficha.get("publicado") is True:
        return ficha
    return None


def _fact_errors(fact: Any, path: str, allowed_units: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(fact, dict):
        return [f"{path}: debe ser un objeto de dato documentado"]
    for key in ("value", "unit", "source", "section", "date_consulted"):
        if key not in fact:
            errors.append(f"{path}: falta {key}")
    value = fact.get("value")
    if value is None or (isinstance(value, str) and not value.strip()):
        errors.append(f"{path}.value: no puede estar vacío")
    unit = fact.get("unit")
    if unit not in _UNIT_WHITELIST:
        errors.append(f"{path}.unit: unidad desconocida ({unit!r})")
    if allowed_units and unit not in allowed_units:
        errors.append(f"{path}.unit: unidad no válida para este dato ({unit!r})")
    if not isinstance(fact.get("source"), str) or not official_url(fact["source"]):
        errors.append(f"{path}.source: debe ser una URL oficial HTTPS")
    if not isinstance(fact.get("section"), str) or not fact["section"].strip():
        errors.append(f"{path}.section: debe identificar la sección del documento")
    date_value = fact.get("date_consulted")
    try:
        if not isinstance(date_value, str) or datetime.strptime(date_value, _DATE_FORMAT).strftime(_DATE_FORMAT) != date_value:
            raise ValueError
    except ValueError:
        errors.append(f"{path}.date_consulted: debe usar dd/mm/aaaa")
    return errors


def validate_fichas_editorial(
    data: Mapping[str, Any] | None = None,
    product_ids: set[str] | None = None,
) -> list[str]:
    """Validate product IDs and documentary provenance without publishing or changing data."""
    data = EDITORIAL_FICHAS if data is None else data
    product_ids = set(catalog.PRODUCTS_BY_ID) if product_ids is None else set(product_ids)
    errors: list[str] = []
    keys = set(data)
    unknown_keys = keys - product_ids - _ROOT_METADATA_KEYS
    missing_keys = product_ids - keys
    errors.extend(f"ID de producto desconocido: {key}" for key in sorted(unknown_keys))
    errors.extend(f"Falta la ficha vacía de: {key}" for key in sorted(missing_keys))

    for product_id in sorted(keys & product_ids):
        ficha = data[product_id]
        prefix = product_id
        if not isinstance(ficha, dict):
            errors.append(f"{prefix}: la ficha debe ser un objeto")
            continue
        if not isinstance(ficha.get("publicado"), bool):
            errors.append(f"{prefix}.publicado: debe ser booleano")
        errors.extend(f"{prefix}: bloque desconocido ({key})" for key in sorted(set(ficha) - _ALLOWED_FICHA_KEYS))

        for index, relation in enumerate(ficha.get("compatibility", [])):
            path = f"{prefix}.compatibility[{index}]"
            if not isinstance(relation, dict):
                errors.append(f"{path}: debe ser un objeto")
                continue
            counterpart_id = relation.get("counterpart_id")
            if counterpart_id not in product_ids:
                errors.append(f"{path}.counterpart_id: ID de producto desconocido")
            errors.extend(_fact_errors(relation.get("type"), f"{path}.type", {"tipo de relación"}))
            if "conditions" in relation:
                errors.extend(_fact_errors(relation["conditions"], f"{path}.conditions", {"condición"}))

        specs = ficha.get("specifications", {})
        if not isinstance(specs, dict):
            errors.append(f"{prefix}.specifications: debe ser un objeto")
        else:
            for name, fact in specs.items():
                allowed = _SPEC_UNITS.get(name)
                if not allowed:
                    errors.append(f"{prefix}.specifications: dato no reconocido ({name})")
                errors.extend(_fact_errors(fact, f"{prefix}.specifications.{name}", allowed))
            if "energy_wh" in specs:
                voltage = specs.get("voltage", {}).get("value") if isinstance(specs.get("voltage"), dict) else None
                capacity = specs.get("capacity_ah", {}).get("value") if isinstance(specs.get("capacity_ah"), dict) else None
                energy = specs["energy_wh"].get("value") if isinstance(specs["energy_wh"], dict) else None
                try:
                    if not (voltage is not None and capacity is not None and energy is not None and abs(float(voltage) * float(capacity) - float(energy)) < 0.01):
                        errors.append(f"{prefix}.specifications.energy_wh: debe coincidir con tensión × capacidad")
                except (TypeError, ValueError):
                    errors.append(f"{prefix}.specifications.energy_wh: requiere tensión y capacidad numéricas")

        for index, charge in enumerate(ficha.get("charge_times", [])):
            path = f"{prefix}.charge_times[{index}]"
            if not isinstance(charge, dict):
                errors.append(f"{path}: debe ser un objeto")
                continue
            if charge.get("counterpart_id") not in product_ids:
                errors.append(f"{path}.counterpart_id: ID de producto desconocido")
            errors.extend(_fact_errors(charge.get("time"), f"{path}.time", {"min", "h"}))

        tool = ficha.get("tool", {})
        if not isinstance(tool, dict):
            errors.append(f"{prefix}.tool: debe ser un objeto")
        else:
            for index, package in enumerate(tool.get("packages", [])):
                path = f"{prefix}.tool.packages[{index}]"
                if not isinstance(package, dict):
                    errors.append(f"{path}: debe ser un objeto")
                    continue
                errors.extend(_fact_errors(package.get("code"), f"{path}.code", {"texto"}))
                errors.extend(_fact_errors(package.get("package_type"), f"{path}.package_type", {"presentación"}))
                product = catalog.PRODUCTS_BY_ID.get(product_id)
                if isinstance(package.get("code"), dict) and product and package["code"].get("value") != product.mpn:
                    errors.append(f"{path}.code.value: debe coincidir con el código exacto del producto")
                if isinstance(package.get("package_type"), dict) and str(package["package_type"].get("value", "")).strip().casefold() not in {"solo cuerpo", "kit"}:
                    errors.append(f"{path}.package_type.value: debe ser Solo cuerpo o Kit")
                for item_index, item in enumerate(package.get("box_contents", [])):
                    errors.extend(_fact_errors(item, f"{path}.box_contents[{item_index}]", {"elemento"}))

        identification = ficha.get("identification", {})
        if not isinstance(identification, dict):
            errors.append(f"{prefix}.identification: debe ser un objeto")
        else:
            if "text" in identification:
                errors.extend(_fact_errors(identification["text"], f"{prefix}.identification.text", {"texto"}))
            if "image" in identification:
                errors.extend(_validate_image(identification["image"], f"{prefix}.identification.image"))

        for field in ("common_errors",):
            for index, fact in enumerate(ficha.get(field, [])):
                errors.extend(_fact_errors(fact, f"{prefix}.{field}[{index}]", {"texto"}))
        for index, faq in enumerate(ficha.get("faqs", [])):
            path = f"{prefix}.faqs[{index}]"
            if not isinstance(faq, dict):
                errors.append(f"{path}: debe ser un objeto")
                continue
            errors.extend(_fact_errors(faq.get("question"), f"{path}.question", {"pregunta"}))
            errors.extend(_fact_errors(faq.get("answer"), f"{path}.answer", {"respuesta"}))

        if "image" in ficha:
            errors.extend(_validate_image(ficha["image"], f"{prefix}.image"))
    return errors


def _validate_image(image: Any, path: str) -> list[str]:
    if not isinstance(image, dict):
        return [f"{path}: debe ser un objeto"]
    errors: list[str] = []
    for key, unit in (("file", "archivo"), ("alt", "texto alternativo"), ("author_or_license", "autor o licencia"), ("credit", "crédito visible")):
        errors.extend(_fact_errors(image.get(key), f"{path}.{key}", {unit}))
    file_fact = image.get("file", {})
    image_path = file_fact.get("value") if isinstance(file_fact, dict) else None
    if not isinstance(image_path, str) or not image_path.startswith("/assets/") or ".." in Path(image_path).parts:
        errors.append(f"{path}.file.value: debe ser una ruta local dentro de /assets/")
    return errors


def _fact_source(fact: Mapping[str, Any], label: str = "Fuente oficial") -> str:
    return (
        f'<a data-compat-event="clic_fuente" href="{escape(str(fact["source"]), quote=True)}" '
        f'target="_blank" rel="noopener noreferrer">{label} ↗</a>'
        f' · <time>{escape(str(fact["date_consulted"]))}</time>'
    )


def _table(rows: list[str], headers: tuple[str, ...]) -> str:
    if not rows:
        return ""
    head = "".join(f"<th scope=\"col\">{escape(label)}</th>" for label in headers)
    return f'<div class="compat-table-scroll" tabindex="0" role="region" aria-label="Tabla de datos documentados"><table class="compat-table"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def _render_compatibility(product, rows: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    has_conditions = any(isinstance(row.get("conditions"), dict) and row["conditions"].get("value") for row in rows)
    for row in rows:
        counterpart = catalog.PRODUCTS_BY_ID.get(row.get("counterpart_id"))
        relation_type = row.get("type")
        if not counterpart or counterpart.status != "publicado" or not isinstance(relation_type, dict):
            continue
        condition = row.get("conditions")
        cells = [
            f'<td><a href="{escape(product_path(counterpart), quote=True)}">{escape(counterpart.brand)} {escape(counterpart.model_name)} (<code>{escape(counterpart.mpn)}</code>)</a></td>',
            f'<td>{escape(str(relation_type.get("value", "")))}</td>',
        ]
        if has_conditions:
            condition_html = ""
            if isinstance(condition, dict):
                condition_html = f'{escape(str(condition.get("value", "")))} · {_fact_source(condition, "Fuente de la condición")} · {escape(str(condition.get("section", "")))}'
            cells.append(f'<td>{condition_html}</td>')
        source_html = _fact_source(relation_type)
        cells.extend((f'<td>{source_html}</td>', f'<td>{escape(str(relation_type.get("section", "")))}</td>'))
        rendered.append("<tr>" + "".join(cells) + "</tr>")
    if not rendered:
        return ""
    headers = ("Contraparte", "Tipo") + (("Condiciones",) if has_conditions else ()) + ("Fuente oficial", "Sección",)
    return f'<section class="compat-editorial-block"><h2>Tabla de compatibilidad</h2>{_table(rendered, headers)}</section>'


def _render_specifications(ficha: Mapping[str, Any]) -> str:
    labels = {
        "voltage": "Tensión",
        "capacity_ah": "Capacidad",
        "energy_wh": "Energía (cálculo de TallerLab)",
        "weight": "Peso",
        "dimensions": "Dimensiones",
        "cell_technology": "Tecnología de celdas",
    }
    rows = []
    for key, label in labels.items():
        fact = ficha.get("specifications", {}).get(key)
        if not isinstance(fact, dict):
            continue
        unit = "" if key == "cell_technology" else f' {escape(str(fact["unit"]))}'
        value = f'{escape(str(fact["value"]))}{unit}'
        rows.append(f'<tr><th scope="row">{label}</th><td>{value}</td><td>{_fact_source(fact)}</td><td>{escape(str(fact["section"]))}</td></tr>')
    if not rows:
        return ""
    return f'<section class="compat-editorial-block"><h2>Especificaciones con fuente</h2>{_table(rows, ("Dato", "Valor", "Fuente oficial", "Sección"))}</section>'


def _render_charge_times(product, ficha: Mapping[str, Any]) -> str:
    rows = []
    for charge in ficha.get("charge_times", []):
        counterpart = catalog.PRODUCTS_BY_ID.get(charge.get("counterpart_id")) if isinstance(charge, dict) else None
        time_fact = charge.get("time") if isinstance(charge, dict) else None
        if not counterpart or counterpart.status != "publicado" or not isinstance(time_fact, dict):
            continue
        link = product_path(counterpart)
        label = f'{counterpart.brand} {counterpart.model_name} (<code>{counterpart.mpn}</code>)'
        rows.append(f'<tr><td><a href="{escape(link, quote=True)}">{label}</a></td><td>{escape(str(time_fact["value"]))} {escape(str(time_fact["unit"]))}</td><td>{_fact_source(time_fact)}</td><td>{escape(str(time_fact["section"]))}</td></tr>')
    if not rows:
        return ""
    title = "Tiempos de carga"
    counterpart_label = "Cargador" if product.product_type == "bateria" else ("Batería" if product.product_type == "cargador" else "Equipo asociado")
    return f'<section class="compat-editorial-block"><h2>{title}</h2>{_table(rows, (counterpart_label, "Tiempo documentado", "Fuente oficial", "Sección"))}</section>'


def _render_packages(ficha: Mapping[str, Any]) -> str:
    rows = []
    for package in ficha.get("tool", {}).get("packages", []):
        if not isinstance(package, dict):
            continue
        code = package.get("code", {})
        package_type = package.get("package_type", {})
        contents = package.get("box_contents", [])
        if not isinstance(code, dict) or not isinstance(package_type, dict) or not contents:
            continue
        rendered_contents = "".join(f'<li>{escape(str(item.get("value", "")))} · {_fact_source(item)}</li>' for item in contents if isinstance(item, dict))
        rows.append(f'<article class="compat-editorial-package"><h3>Código <code>{escape(str(code["value"]))}</code> · {escape(str(package_type["value"]))}</h3><p>Código: {_fact_source(code)} · Presentación: {_fact_source(package_type)}</p><h4>Qué incluye la caja</h4><ul>{rendered_contents}</ul></article>')
    return f'<section class="compat-editorial-block"><h2>Herramienta: presentación y contenido</h2>{"".join(rows)}</section>' if rows else ""


def _render_identification(ficha: Mapping[str, Any]) -> str:
    identification = ficha.get("identification", {})
    text_fact = identification.get("text") if isinstance(identification, dict) else None
    image = identification.get("image") if isinstance(identification, dict) else None
    if not text_fact and not image:
        return ""
    body = ""
    if isinstance(text_fact, dict):
        body += f'<p>{escape(str(text_fact["value"]))} · {_fact_source(text_fact)}</p>'
    if isinstance(image, dict):
        file = image.get("file", {}).get("value", "")
        alt = image.get("alt", {}).get("value", "")
        credit = image.get("credit", {}).get("value", "")
        license_text = image.get("author_or_license", {}).get("value", "")
        provenance = " · ".join(_fact_source(image[key], label=label) for key, label in (("file", "Fuente de imagen"), ("alt", "Fuente del texto alternativo"), ("author_or_license", "Fuente de autoría o licencia"), ("credit", "Fuente del crédito")))
        body += f'<figure><img src="{escape(str(file), quote=True)}" alt="{escape(str(alt), quote=True)}" loading="lazy" style="display:block;max-width:100%;height:auto;border:1px solid #dcdcd5;border-radius:8px"><figcaption>{escape(str(credit))} · {escape(str(license_text))}<br>{provenance}</figcaption></figure>'
    return f'<section class="compat-editorial-block"><h2>Cómo identificar el código en la etiqueta</h2>{body}</section>'


def _render_common_errors(ficha: Mapping[str, Any]) -> str:
    items = []
    for fact in ficha.get("common_errors", []):
        if isinstance(fact, dict):
            items.append(f'<li>{escape(str(fact["value"]))} · {_fact_source(fact)}</li>')
    return f'<section class="compat-editorial-block"><h2>Errores comunes</h2><ul>{"".join(items)}</ul></section>' if items else ""


def _render_faqs(ficha: Mapping[str, Any]) -> str:
    items = []
    for faq in ficha.get("faqs", []):
        if not isinstance(faq, dict):
            continue
        question, answer = faq.get("question"), faq.get("answer")
        if not isinstance(question, dict) or not isinstance(answer, dict):
            continue
        items.append(f'<article><h3>{escape(str(question["value"]))}</h3><p class="compat-editorial-source">{_fact_source(question, "Fuente de la pregunta")}</p><p>{escape(str(answer["value"]))}</p><p class="compat-editorial-source">{_fact_source(answer, "Fuente de la respuesta")}</p></article>')
    return f'<section class="compat-editorial-block"><h2>Preguntas frecuentes</h2>{"".join(items)}</section>' if items else ""


def _render_product_image(ficha: Mapping[str, Any]) -> str:
    image = ficha.get("image")
    if not isinstance(image, dict):
        return ""
    file, alt = image.get("file", {}), image.get("alt", {})
    credit, license_fact = image.get("credit", {}), image.get("author_or_license", {})
    if not all(isinstance(value, dict) for value in (file, alt, credit, license_fact)):
        return ""
    provenance = " · ".join(_fact_source(image[key], label=label) for key, label in (("file", "Fuente de imagen"), ("alt", "Fuente del texto alternativo"), ("author_or_license", "Fuente de autoría o licencia"), ("credit", "Fuente del crédito")))
    return f'<section class="compat-editorial-block"><h2>Imagen del producto</h2><figure><img src="{escape(str(file["value"]), quote=True)}" alt="{escape(str(alt["value"]), quote=True)}" loading="lazy" style="display:block;max-width:100%;height:auto;border:1px solid #dcdcd5;border-radius:8px"><figcaption>{escape(str(credit["value"]))} · {escape(str(license_fact["value"]))}<br>{provenance}</figcaption></figure></section>'


def render_editorial_blocks(product, ficha: Mapping[str, Any]) -> str:
    """Render only populated blocks, in the requested editorial order (blocks 2–9)."""
    blocks = (
        _render_compatibility(product, ficha.get("compatibility", [])),
        _render_specifications(ficha),
        _render_charge_times(product, ficha),
        _render_packages(ficha),
        _render_identification(ficha),
        _render_common_errors(ficha),
        _render_faqs(ficha),
        _render_product_image(ficha),
    )
    return "".join(blocks)


def render_published_product_page(
    product,
    h1: str,
    direct_answer: str,
    ficha: Mapping[str, Any],
    closing_links: str = "",
) -> str:
    """Wrap the enriched blocks; caller supplies the unchanged H1 and direct response."""
    from compatibilidad.commercial import render_product_commercial
    from compatibilidad.presentation import source_panel

    return (
        '<style>.compat-editorial-page{max-width:900px}.compat-editorial-page>h1{margin:.7rem 0 1rem}.compat-editorial-page>.compat-editorial-block{margin:1.5rem 0;padding:1.15rem 1.25rem;background:#fffefa;border:1px solid #dedbd3;border-left:4px solid #c24100;border-radius:8px}.compat-editorial-page .compat-editorial-block>h2{margin:.1rem 0 .8rem;font-size:1.25rem;line-height:1.3;color:#20262a}.compat-editorial-page .compat-table-scroll{margin:.65rem 0 0}.compat-editorial-page .compat-editorial-package{padding:.9rem 0;border-top:1px solid #dedbd3}.compat-editorial-page .compat-editorial-package h3{margin:.15rem 0 .4rem;font-size:1rem}.compat-editorial-page .compat-editorial-package h4{margin:.9rem 0 .35rem}.compat-editorial-page .compat-editorial-package ul,.compat-editorial-page .compat-editorial-block>ul{padding-left:1.25rem}.compat-editorial-page .compat-editorial-source{font-size:.84rem}.compat-editorial-page figure{margin:.8rem 0 0}.compat-editorial-page figcaption{margin-top:.45rem;font-size:.82rem;color:#5b6467;line-height:1.45}.compat-editorial-page time{white-space:nowrap}@media(max-width:520px){.compat-editorial-page>.compat-editorial-block{padding:.9rem}.compat-editorial-page .compat-table{min-width:560px}}</style>'
        '<article class="compat-answer compat-editorial-page">'
        f'<nav aria-label="Migas de pan"><a href="/compatibilidad/">Base de compatibilidad</a> / {escape(product.model_name)}</nav>'
        f'<h1>{escape(h1)}</h1>{direct_answer}'
        f'{render_editorial_blocks(product, ficha)}{closing_links}'
        f'{source_panel(product)}{render_product_commercial(product)}</article>'
    )


def product_image_schema(product_id: str, site_url: str = "") -> str | None:
    ficha = get_published_ficha(product_id)
    image = ficha.get("image") if ficha else None
    file_fact = image.get("file") if isinstance(image, dict) else None
    if not isinstance(file_fact, dict) or not isinstance(file_fact.get("value"), str):
        return None
    path = file_fact["value"]
    return f"{site_url.rstrip('/')}{path}" if site_url else path
