"""Datos editoriales públicos de independencia, consultas a fabricantes y prensa."""
import csv
import io
import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


DATA_DIR = Path(__file__).resolve().parent
WHO_PATH = "/quienes-somos/"
MANUFACTURER_PATH = "/fabricantes/respuestas/"
PRESS_PATH = "/en-los-medios/"
MANUFACTURER_CSV_PATH = "/fabricantes/respuestas/descargar.csv"
AUTHORITY_PAGE_PATHS = (WHO_PATH, MANUFACTURER_PATH, PRESS_PATH)
RESPONSE_STATES = {"enviada", "respondida", "sin_respuesta", "rechazada"}
PRESS_TYPES = {"cita", "entrevista", "uso de datos"}
WHO_FIELDS = (
    ("quienes_somos", "Quiénes somos"),
    ("como_se_financia", "Cómo se financia"),
    ("que_no_aceptamos", "Qué no aceptamos"),
    ("politica_independencia", "Política de independencia"),
    ("contacto", "Contacto"),
)
RESPONSE_FIELDS = (
    "id", "marca", "modelo", "codigo", "pregunta", "fecha_envio", "estado",
    "respuesta_textual", "fecha_respuesta", "guias",
)
PRESS_FIELDS = ("medio", "titulo", "url", "fecha", "tipo", "dato_usado")
_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _read_json(filename, data_dir=None):
    try:
        value = json.loads((Path(data_dir or DATA_DIR) / filename).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return value if isinstance(value, dict) else {}


def load_who_data(data_dir=None):
    return _read_json("quienes_somos.json", data_dir)


def _valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}/\d{2}/\d{4}", value):
        return False
    try:
        datetime.strptime(value, "%d/%m/%Y")
    except ValueError:
        return False
    return True


def _text(item, key):
    value = item.get(key)
    return value.strip() if isinstance(value, str) else ""


def _valid_guide_path(value):
    return (isinstance(value, str) and value.startswith("/") and value.endswith("/")
            and not value.startswith("//") and ".." not in value.split("/"))


def valid_response(item):
    if not isinstance(item, dict):
        return False
    if not all(_text(item, key) for key in ("id", "marca", "modelo", "codigo", "pregunta")):
        return False
    if not _ID.fullmatch(_text(item, "id")) or not _valid_date(item.get("fecha_envio")):
        return False
    state = _text(item, "estado")
    if state not in RESPONSE_STATES:
        return False
    if not isinstance(item.get("guias"), list) or not all(_valid_guide_path(path) for path in item["guias"]):
        return False
    if state == "respondida":
        return bool(_text(item, "respuesta_textual") and _valid_date(item.get("fecha_respuesta")))
    return True


def response_records(data_dir=None, data=None):
    payload = data if isinstance(data, dict) else _read_json("consultas_fabricantes.json", data_dir)
    rows = payload.get("consultas", [])
    if not isinstance(rows, list):
        return []
    valid = []
    for source in rows:
        if not valid_response(source):
            continue
        row = dict(source)
        for key in ("id", "marca", "modelo", "codigo", "pregunta", "estado"):
            row[key] = _text(source, key)
        if not isinstance(row.get("respuesta_textual"), str):
            row["respuesta_textual"] = ""
        valid.append(row)
    seen = set()
    unique = []
    for row in valid:
        if row["id"] not in seen:
            seen.add(row["id"])
            unique.append(row)
    return unique


def load_press_records(data_dir=None, data=None):
    payload = data if isinstance(data, dict) else _read_json("prensa.json", data_dir)
    rows = payload.get("menciones", [])
    if not isinstance(rows, list):
        return []
    valid = []
    for row in rows:
        if not isinstance(row, dict) or not all(_text(row, key) for key in PRESS_FIELDS):
            continue
        url = _text(row, "url")
        try:
            parts = urlsplit(url)
        except ValueError:
            continue
        if (_text(row, "tipo") not in PRESS_TYPES or not _valid_date(row.get("fecha"))
                or parts.scheme not in ("https", "http") or not parts.netloc):
            continue
        normalized = dict(row)
        for key in ("medio", "titulo", "url", "tipo", "dato_usado"):
            normalized[key] = _text(row, key)
        valid.append(normalized)
    return valid


def who_is_published(data_dir=None, data=None):
    payload = data if isinstance(data, dict) else load_who_data(data_dir)
    return payload.get("publicado") is True and all(_text(payload, key) for key, _ in WHO_FIELDS)


def manufacturer_responses_are_published(data_dir=None, data=None):
    return len(response_records(data_dir=data_dir, data=data)) >= 5


def press_is_published(data_dir=None, data=None):
    return len(load_press_records(data_dir=data_dir, data=data)) >= 1


def page_is_published(path, data_dir=None):
    if path == WHO_PATH:
        return who_is_published(data_dir=data_dir)
    if path == MANUFACTURER_PATH:
        return manufacturer_responses_are_published(data_dir=data_dir)
    if path == PRESS_PATH:
        return press_is_published(data_dir=data_dir)
    return False


def indexable_authority_paths(data_dir=None):
    return tuple(path for path in AUTHORITY_PAGE_PATHS if page_is_published(path, data_dir=data_dir))


def footer_authority_links(data_dir=None):
    labels = {WHO_PATH: "Quiénes somos", MANUFACTURER_PATH: "Respuestas de fabricantes", PRESS_PATH: "En los medios"}
    return " · ".join(
        f'<a href="{path}">{escape(labels[path])}</a>'
        for path in indexable_authority_paths(data_dir=data_dir)
    )


def manufacturer_response_component(response_id, guide_url, data_dir=None):
    if not manufacturer_responses_are_published(data_dir=data_dir):
        return ""
    row = next((item for item in response_records(data_dir=data_dir)
                if item["id"] == response_id and item["estado"] == "respondida"
                and guide_url in item["guias"]), None)
    if row is None:
        return ""
    answer = escape(row["respuesta_textual"]).replace("\n", "<br>")
    return (
        f'<aside class="manufacturer-response" aria-label="Respuesta oficial del fabricante" id="respuesta-{escape(row["id"], quote=True)}">'
        f'<h2>Respuesta oficial del fabricante · {escape(_text(row, "marca"))} {_escape_optional(row, "modelo")}</h2>'
        f'<p><strong>Consulta:</strong> {escape(_text(row, "pregunta"))}</p>'
        f'<blockquote><p>{answer}</p></blockquote>'
        f'<p><strong>Fecha de respuesta:</strong> {escape(_text(row, "fecha_respuesta"))}</p>'
        f'<p><a href="{MANUFACTURER_PATH}#{escape(row["id"], quote=True)}">Ver consulta y respuesta en la tabla de fabricantes</a></p>'
        "</aside>"
    )


def replace_manufacturer_response_markers(markdown, guide_url, data_dir=None):
    """Expande el marcador documentado solo para respuestas publicables asociadas a esa guía."""
    pattern = re.compile(r"(?m)^\s*\{\{respuesta_fabricante:([a-z0-9-]+)\}\}\s*$")
    return pattern.sub(
        lambda match: "\n" + manufacturer_response_component(match.group(1), guide_url, data_dir=data_dir) + "\n",
        markdown,
    )


def _escape_optional(row, key):
    value = _text(row, key)
    return " " + escape(value) if value else ""


def export_responses_csv(data_dir=None):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=RESPONSE_FIELDS, extrasaction="ignore", lineterminator="\r\n")
    writer.writeheader()
    for row in response_records(data_dir=data_dir):
        safe_row = {key: "; ".join(row[key]) if key == "guias" else row.get(key, "") for key in RESPONSE_FIELDS}
        for key, value in safe_row.items():
            if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
                safe_row[key] = "'" + value
        writer.writerow(safe_row)
    return output.getvalue()


def manufacturer_summary(rows):
    summary = {}
    for row in rows:
        item = summary.setdefault(row["marca"], {"respondidas": 0, "total": 0})
        item["total"] += 1
        item["respondidas"] += row["estado"] == "respondida"
    return summary
