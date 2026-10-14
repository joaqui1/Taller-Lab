"""Equivalencias conservadoras entre identificadores públicos de modelos.

La tabla versionada se genera desde snapshots publicados. Solo acepta coincidencias
únicas de marca y código/modelo tras quitar separadores; no expande variantes.
"""

from __future__ import annotations

import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = Path(__file__).with_name("model_equivalences.json")
REVIEW_PATH = Path(__file__).with_name("model_equivalences_review.json")


def normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _keys(brand: str, *values: Any) -> set[tuple[str, str]]:
    b = normalize(brand)
    return {(b, normalize(value)) for value in values if normalize(value)}


def build_equivalences() -> tuple[dict, list]:
    tools_payload = _read_json(ROOT / "tallerlab_data/data/catalog_snapshot.json", {})
    price_payload = _read_json(ROOT / "observatorio/piloto_gratuito.json", {})
    compatibility_payload = _read_json(ROOT / "compatibilidad/data/verified_seed.json", {})
    alert_payload = _read_json(ROOT / "datos_alertas/modelos_expedientes.json", [])

    tools = [tool for tool in tools_payload.get("tools", []) if tool.get("status") == "aceptado"]
    prices = price_payload.get("models", [])
    compatibility = [product for product in compatibility_payload.get("products", [])
                     if product.get("status") == "publicado" and product.get("product_type") == "herramienta"]
    alerts = alert_payload if isinstance(alert_payload, list) else []

    def index(records, key_fn):
        result: dict[tuple[str, str], list] = {}
        for record in records:
            for key in key_fn(record):
                result.setdefault(key, []).append(record)
        return result

    price_index = index(prices, lambda row: _keys(row.get("brand"), row.get("model"), row.get("schema_sku"), row.get("schema_mpn")))
    compatibility_index = index(compatibility, lambda row: _keys(row.get("brand"), row.get("model_name"), row.get("mpn")))

    alert_index: dict[tuple[str, str], list] = {}
    for dossier in alerts:
        for variant in dossier.get("variantes", []):
            for key in _keys(dossier.get("marca"), variant.get("codigo"), dossier.get("modelo_base")):
                alert_index.setdefault(key, []).append(dossier)

    table = {}
    review = []
    for tool in tools:
        slug = tool["slug"]
        keys = _keys(tool.get("brand"), tool.get("mpn"), tool.get("commercial_name"))
        # El nombre comercial suele incluir la marca; conservar también el token del modelo.
        keys |= _keys(tool.get("brand"), re.sub(rf"^{re.escape(tool.get('brand', ''))}\s+", "", tool.get("commercial_name", ""), flags=re.I))
        resolved = {"tool_slug": slug, "price_path": None, "alert_path": None, "compatibility_path": None}
        for kind, source_index, path_fn, source_records, values_fn, brand_fn in (
            ("price_path", price_index, lambda row: f"/datos/precios/{row['category']}/" + _price_slug(row) + "/",
             prices, lambda row: (row.get("model"), row.get("schema_sku"), row.get("schema_mpn")), lambda row: row.get("brand")),
            ("alert_path", alert_index, lambda row: f"/alertas/{row['slug']}/",
             alerts, lambda row: (row.get("modelo_base"), *(v.get("codigo") for v in row.get("variantes", []))), lambda row: row.get("marca")),
            ("compatibility_path", compatibility_index, lambda row: _compatibility_path(row),
             compatibility, lambda row: (row.get("model_name"), row.get("mpn")), lambda row: row.get("brand")),
        ):
            candidates = {id(record): record for key in keys for record in source_index.get(key, [])}
            if len(candidates) == 1:
                resolved[kind] = path_fn(next(iter(candidates.values())))
            elif len(candidates) > 1:
                review.append({"tool_slug": slug, "area": kind.removesuffix("_path"),
                               "candidatos": sorted(path_fn(record) for record in candidates.values()),
                               "motivo": "Más de un registro coincide con marca y código/modelo normalizado."})
            matched_ids = set(candidates)
            tool_codes = [normalize(tool.get("mpn")), normalize(re.sub(
                rf"^{re.escape(tool.get('brand', ''))}\s+", "", tool.get("commercial_name", ""), flags=re.I))]
            for record in source_records:
                if id(record) in matched_ids or normalize(brand_fn(record)) != normalize(tool.get("brand")):
                    continue
                record_codes = [normalize(value) for value in values_fn(record) if normalize(value)]
                score = max((SequenceMatcher(None, a, b).ratio() for a in tool_codes for b in record_codes if len(a) >= 5 and len(b) >= 5), default=0)
                if 0.86 <= score < 1:
                    review.append({"tool_slug": slug, "area": kind.removesuffix("_path"),
                                   "candidato": path_fn(record), "similitud": round(score, 3),
                                   "motivo": "Coincidencia aproximada; requiere revisión y no se enlaza automáticamente."})
        if any(resolved[key] for key in ("price_path", "alert_path", "compatibility_path")):
            table[slug] = resolved
    return table, review


def _price_slug(row: dict) -> str:
    text = unicodedata.normalize("NFKD", f"{row['brand']} {row['model']}")
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _compatibility_path(row: dict) -> str:
    return f"/herramientas-bateria/{row['slug']}/"


def generate_files() -> tuple[dict, list]:
    table, review = build_equivalences()
    TABLE_PATH.write_text(json.dumps({"schema_version": 1, "equivalences": table}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW_PATH.write_text(json.dumps({"_instrucciones": "Revisar manualmente antes de agregar equivalencias. Estos candidatos no se enlazan.", "candidates": review}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return table, review


def load_equivalences() -> dict[str, dict]:
    payload = _read_json(TABLE_PATH, {})
    return payload.get("equivalences", {})


def related_paths(tool_slug: str) -> dict[str, str | None]:
    return load_equivalences().get(tool_slug, {"tool_slug": tool_slug, "price_path": None, "alert_path": None, "compatibility_path": None})


def tool_slug_for_related_path(field: str, path: str) -> str | None:
    for tool_slug, equivalence in load_equivalences().items():
        if equivalence.get(field) == path:
            return tool_slug
    return None


def guides_for_tool_slug(tool_slug: str) -> list[tuple[str, str]]:
    from tallerlab_data.guide_links import GUIDE_TOOL_MAPPINGS

    equivalents = load_equivalences()
    accepted_slugs = {tool_slug}
    for primary, entry in equivalents.items():
        if tool_slug in {primary, (entry.get("price_path") or "").rstrip("/").split("/")[-1],
                         (entry.get("alert_path") or "").rstrip("/").split("/")[-1],
                         (entry.get("compatibility_path") or "").rstrip("/").split("/")[-1]}:
            accepted_slugs.add(primary)
    guide_urls = {url for url, slugs in GUIDE_TOOL_MAPPINGS.items() if accepted_slugs.intersection(slugs)}
    titles = {article["url"]: article["title"] for article in _published_articles()}
    return [(titles.get(url, url.strip("/").split("/")[-1].replace("-", " ").title()), url)
            for url in sorted(guide_urls)]


def _published_articles() -> list[dict]:
    try:
        from servidor_local import ALL_ARTICLES
        return ALL_ARTICLES
    except Exception:
        return []
