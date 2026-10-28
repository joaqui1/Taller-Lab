"""Genera el registro único de enlaces afiliados por modelo exacto."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from tallerlab_data.model_equivalences import ROOT, build_equivalences, normalize

TABLE_PATH = Path(__file__).with_name("afiliados_por_modelo.json")
REVIEW_PATH = Path(__file__).with_name("afiliados_por_modelo_review.json")
AFFILIATE_URL = re.compile(r"^https://meli\.la/[A-Za-z0-9]+$")
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\((https://meli\.la/[A-Za-z0-9]+)(?:[^)]*)\)")
HTML_CARD = re.compile(r"<article\b.*?</article>", re.IGNORECASE | re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _contains_identifier(text: str, identifier: str) -> bool:
    """Busca un código como secuencia completa, tolerando separadores editoriales."""
    target = normalize(identifier)
    if not target:
        return False
    tokens = re.findall(r"[A-Za-z0-9]+", text or "")
    for start in range(len(tokens)):
        for end in range(start + 1, min(len(tokens), start + 5) + 1):
            if normalize("".join(tokens[start:end])) == target:
                return True
    return False


def _has_brand(text: str, brand: str) -> bool:
    return _contains_identifier(text, brand)


def _tools():
    payload = _read_json(ROOT / "tallerlab_data/data/catalog_snapshot.json", {})
    return [tool for tool in payload.get("tools", []) if tool.get("status") == "aceptado"]


def _add(hits, tools_by_slug, tool, url, source):
    if not AFFILIATE_URL.fullmatch(str(url or "")):
        return
    slug = tool["slug"]
    hits[slug][url].add(source)


def _source_records(tools):
    """Reúne solo enlaces cortos afiliados respaldados por marca y código exactos."""
    from tallerlab_data.affiliates import LINKS as CURATED_LINKS

    hits = defaultdict(lambda: defaultdict(set))
    tools_by_slug = {tool["slug"]: tool for tool in tools}
    context_candidates = []

    # La oferta anidada en una ficha tiene una asociación directa con ese
    # registro; no se buscan coincidencias por categoría o familia.
    for tool in tools:
        for offer in tool.get("commercial_offers", []):
            _add(hits, tools_by_slug, tool, offer.get("url"), "catalog_snapshot.commercial_offers")

    # Datos de producto ya revisados que acompañan las opciones de las guías.
    import servidor_local as server

    for url, facts in server.PRODUCT_FACTS.items():
        for tool in tools:
            if (normalize(facts.get("brand")) == normalize(tool.get("brand"))
                    and normalize(facts.get("model")) == normalize(tool.get("mpn"))):
                _add(hits, tools_by_slug, tool, url, "PRODUCT_FACTS")

    # Enlaces editoriales estructurados, incluida la curaduría previa de fichas.
    for slug, (code, url, guide) in CURATED_LINKS.items():
        tool = tools_by_slug.get(slug)
        if tool and normalize(code) == normalize(tool.get("mpn")):
            _add(hits, tools_by_slug, tool, url, "tallerlab_data/affiliates.py")

    for category, products in server.AFFILIATE_PRODUCTS.items():
        for name, _detail, url, _guide in products:
            for tool in tools:
                if (normalize(tool.get("category")) == normalize(category)
                        and normalize(tool.get("mpn"))
                        and _has_brand(name, tool.get("brand", ""))
                        and _contains_identifier(name, tool.get("mpn", ""))):
                    _add(hits, tools_by_slug, tool, url, "AFFILIATE_PRODUCTS")

    from amoladoras_comerciales import AMOLADORA_CHOICES, CONTEXTUAL_CHOICES

    for page, choice in AMOLADORA_CHOICES.items():
        for item in choice.get("items", []):
            for tool in tools:
                if (_has_brand(item.get("name", ""), tool.get("brand", ""))
                        and _contains_identifier(item.get("name", ""), tool.get("mpn", ""))):
                    _add(hits, tools_by_slug, tool, item.get("url"), "AMOLADORA_CHOICES:" + page)
    for page, item in CONTEXTUAL_CHOICES.items():
        for tool in tools:
            if (_has_brand(item.get("name", ""), tool.get("brand", ""))
                    and _contains_identifier(item.get("name", ""), tool.get("mpn", ""))):
                _add(hits, tools_by_slug, tool, item.get("url"), "CONTEXTUAL_CHOICES:" + page)

    # Captura las configuraciones por categoría como JSON, sin ampliar variantes.
    for path in ROOT.glob("*-ofertas.json"):
        category = path.name.removesuffix("-ofertas.json")
        payload = _read_json(path, {})
        for section in payload.values():
            if not isinstance(section, dict):
                continue
            for offer in section.get("offers", []):
                for tool in tools:
                    if (normalize(tool.get("category")) == normalize(category)
                            and normalize(offer.get("model")) == normalize(tool.get("mpn"))):
                        _add(hits, tools_by_slug, tool, offer.get("url"), path.name)

    # En las guías, las tarjetas HTML mantienen el título y su URL juntos.
    # Las tablas se asocian por las dos primeras celdas (uso y modelo), para no
    # confundir una mención de otro modelo en la descripción con la publicación.
    for path in (ROOT / "paginas").rglob("*.md"):
        body = path.read_text(encoding="utf-8")
        cards = list(HTML_CARD.finditer(body))
        for card in cards:
            block = card.group(0)
            title_match = re.search(r"<h3\b[^>]*>(.*?)</h3>", block, re.IGNORECASE | re.DOTALL)
            title = HTML_TAG.sub(" ", title_match.group(1) if title_match else block)
            links = list(re.finditer(r"https://meli\.la/[A-Za-z0-9]+", block))
            for match in links:
                for tool in tools:
                    identity = title + " " + block[:match.start()]
                    if (_has_brand(identity, tool.get("brand", ""))
                            and _contains_identifier(identity, tool.get("mpn", ""))):
                        _add(hits, tools_by_slug, tool, match.group(0), "Markdown:" + path.relative_to(ROOT).as_posix())

            # Si el modelo se reconoce en el título pero no aparece su MPN,
            # guardar el enlace como candidato manual, nunca como asociación.
            for tool in tools:
                slug_model = normalize(tool.get("slug", "").split("-", 1)[-1])
                if (slug_model and _has_brand(title, tool.get("brand", ""))
                        and slug_model in normalize(title)
                        and not _contains_identifier(block, tool.get("mpn", ""))):
                    for match in links:
                        context_candidates.append({
                            "tool_slug": tool["slug"],
                            "codigo": tool.get("mpn"),
                            "candidato": match.group(0),
                            "motivo": "El título coincide con el modelo, pero el contexto de la publicación no contiene el MPN exacto; requiere revisión y no se enlaza automáticamente.",
                            "fuentes": ["Markdown:" + path.relative_to(ROOT).as_posix()],
                        })

        remainder = HTML_CARD.sub("", body)
        for line in remainder.splitlines():
            links = list(MARKDOWN_LINK.finditer(line))
            if not links:
                continue
            cells = [cell.strip() for cell in line.split("|")] if "|" in line else []
            identity = " ".join(cells[:2]) if cells else ""
            for match in links:
                linked_text = match.group(1)
                row_identity = identity or line[:match.start()]
                for tool in tools:
                    model_code = tool.get("mpn", "")
                    brand = tool.get("brand", "")
                    exact_label = _has_brand(linked_text, brand) and _contains_identifier(linked_text, model_code)
                    exact_row = _has_brand(row_identity, brand) and _contains_identifier(row_identity, model_code)
                    if exact_label or exact_row:
                        _add(hits, tools_by_slug, tool, match.group(2), "Markdown:" + path.relative_to(ROOT).as_posix())

    context_candidates = [
        candidate for candidate in context_candidates
        if candidate["candidato"] not in hits.get(candidate["tool_slug"], {})
    ]
    return hits, CURATED_LINKS, context_candidates


def build_files() -> tuple[dict, list]:
    """Construye modelo → enlace meli.la, con equivalencias exactas para cada ficha."""
    tools = _tools()
    tools_by_slug = {tool["slug"]: tool for tool in tools}
    hits, curated, context_candidates = _source_records(tools)
    equivalences, _equivalence_review = build_equivalences()

    chosen = {}
    review = list(context_candidates)
    for slug, urls in sorted(hits.items()):
        tool = tools_by_slug[slug]
        exact_urls = sorted(urls)
        preferred = curated.get(slug)
        if preferred and normalize(preferred[0]) == normalize(tool.get("mpn")) and preferred[1] in urls:
            selected = preferred[1]
            for url in exact_urls:
                if url != selected:
                    review.append({
                        "tool_slug": slug,
                        "codigo": tool.get("mpn"),
                        "candidato": url,
                        "motivo": "Hay otra publicación afiliada para el mismo código; se conserva solo la selección editorial existente.",
                        "fuentes": sorted(urls[url]),
                    })
        elif len(exact_urls) == 1:
            selected = exact_urls[0]
        else:
            selected = None
            review.append({
                "tool_slug": slug,
                "codigo": tool.get("mpn"),
                "candidatos": exact_urls,
                "motivo": "Más de una URL afiliada coincide con el código exacto y no hay una selección editorial única.",
                "fuentes": {url: sorted(urls[url]) for url in exact_urls},
            })
        if not selected:
            continue

        relation = equivalences.get(slug, {})
        legacy = curated.get(slug)
        chosen[slug] = {
            "tool_slug": slug,
            "tool_path": f"/herramientas/{slug}/",
            "price_path": relation.get("price_path"),
            "brand": tool.get("brand", ""),
            "model": tool.get("commercial_name", ""),
            "mpn": tool.get("mpn", ""),
            "url": selected,
            "guide_url": legacy[2] if legacy and legacy[1] == selected else None,
            "sources": sorted(urls[selected]),
        }

    reverse = defaultdict(list)
    for slug, entry in chosen.items():
        reverse[entry["url"]].append(slug)
    for url, slugs in reverse.items():
        if len(slugs) > 1:
            for slug in slugs:
                chosen.pop(slug, None)
            review.append({
                "candidato": url,
                "tool_slugs": sorted(slugs),
                "motivo": "La misma URL quedó asociada a más de un código de herramienta; requiere revisión.",
            })

    table = {"schema_version": 1, "models": chosen}
    review.sort(key=lambda row: (row.get("tool_slug", ""), row.get("candidato", "")))
    return table, review


def generate_files() -> tuple[dict, list]:
    table, review = build_files()
    TABLE_PATH.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW_PATH.write_text(json.dumps({
        "_instrucciones": "Revisar los candidatos antes de cambiar el enlace publicado. Los registros de este archivo no se enlazan automáticamente.",
        "candidates": review,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return table, review


if __name__ == "__main__":
    table, review = generate_files()
    print(json.dumps({"models": len(table["models"]), "review": len(review)}, ensure_ascii=False))
