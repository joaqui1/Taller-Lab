"""Owner-approved editorial copy for battery compatibility platform pages."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import quote


DATA_PATH = Path(__file__).parent / "data" / "plataformas_editorial.json"


def _load_platforms() -> dict[str, dict]:
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        row["platform_id"]: row
        for row in data.get("plataformas", [])
        if isinstance(row, dict) and isinstance(row.get("platform_id"), str)
    }


EDITORIAL_PLATFORMS = _load_platforms()


def has_platform_editorial(platform_id: str) -> bool:
    return platform_id in EDITORIAL_PLATFORMS


def platform_page_is_indexable(platform_id: str) -> bool:
    """Hide owner-unapproved draft pages from the generated sitemap paths."""
    page = EDITORIAL_PLATFORMS.get(platform_id)
    return page is None or page.get("publicado") is True


def render_platform_editorial_page(platform_id: str) -> str | None:
    """Render an approved platform page; keep unapproved copy out of responses."""
    page = EDITORIAL_PLATFORMS.get(platform_id)
    if page is None:
        return None
    if page.get("publicado") is not True:
        return ""

    from compatibilidad.catalog import CATALOG_PRODUCTS, PLATFORMS_BY_ID, RELATIONS
    from compatibilidad.presentation import product_path

    platform = PLATFORMS_BY_ID.get(platform_id)
    if platform is None:
        return ""
    products = {product.id: product for product in CATALOG_PRODUCTS}

    def product_link(product_id: str) -> str:
        product = products.get(product_id)
        if product is None:
            return ""
        return (
            f'<a href="{escape(product_path(product), quote=True)}">'
            f'{escape(product.brand)} {escape(product.model_name)} '
            f'(<code>{escape(product.mpn)}</code>)</a>'
        )

    def product_list(product_ids: list[str]) -> str:
        rows = []
        for product_id in product_ids:
            product = products.get(product_id)
            if product is None or product.status != "publicado":
                continue
            rows.append(f"<li>{product_link(product_id)}</li>")
        return "<ul>" + "".join(rows) + "</ul>" if rows else "<p>Sin modelos publicados en esta categoría.</p>"

    rows = []
    for relation in RELATIONS:
        if isinstance(relation, dict):
            source_id = relation.get("source_product_id")
            target_id = relation.get("target_product_id")
            relation_type = relation.get("relation_type", "")
        else:
            source_id = relation.source_product_id
            target_id = relation.target_product_id
            relation_type = relation.relation_type
        source, target = products.get(source_id), products.get(target_id)
        if (not source or not target or source.platform_id != platform_id
                or target.platform_id != platform_id
                or source.status != "publicado" or target.status != "publicado"):
            continue
        relation_label = (
            "Cargador para batería" if relation_type == "cargador_hacia_bateria"
            else "Batería para herramienta"
        )
        rows.append(
            "<tr><td>" + product_link(source_id) + "</td><td>" + escape(relation_label)
            + "</td><td>" + product_link(target_id) + "</td></tr>"
        )
    compatibility_table = (
        '<div class="compat-table-scroll" tabindex="0" role="region" '
        'aria-label="Tabla de relaciones de compatibilidad"><table class="compat-table">'
        '<thead><tr><th>Modelo</th><th>Relación documentada</th><th>Modelo asociado</th></tr></thead>'
        '<tbody>' + "".join(rows) + "</tbody></table></div>"
        if rows else '<p>No hay relaciones publicadas para esta plataforma todavía.</p>'
    )
    faqs = "".join(
        f'<details><summary>{escape(item["pregunta"])}</summary>'
        f'<p>{escape(item["respuesta"])}</p></details>'
        for item in page.get("preguntas_frecuentes", [])
        if isinstance(item, dict) and item.get("pregunta") and item.get("respuesta")
    )
    sources = "".join(
        f'<li><a href="{escape(item["url"], quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{escape(item["titulo"])} ↗</a> — {escape(item["uso"])}</li>'
        for item in page.get("fuentes", [])
        if isinstance(item, dict) and item.get("url") and item.get("titulo") and item.get("uso")
    )
    return f"""<article class="compat-platform-editorial" style="max-width: 1040px; margin: 0 auto; padding: 2rem 1rem;">
      <nav aria-label="Migas de pan"><a href="/">Inicio</a> / <a href="/compatibilidad/">Compatibilidad</a> / {escape(platform.name)}</nav>
      <header><p>{escape(platform.brand)} · {escape(platform.system_name)}</p>
        <h1>{escape(page['title'])}</h1><p class="compat-direct-answer">{escape(page['respuesta_directa'])}</p></header>
      <section><h2>Qué incluye el sistema</h2><p>{escape(page['sistema'])}</p>
        <h3>Baterías {escape(platform.system_name)}</h3>{product_list(page.get('baterias', []))}
        <h3>Cargadores {escape(platform.system_name)}</h3>{product_list(page.get('cargadores', []))}
        <h3>Herramientas documentadas</h3>{product_list(page.get('herramientas', []))}</section>
      <section><h2>{escape(page.get('tabla_titulo', 'Compatibilidad por modelo'))}</h2>
        <p>{escape(page.get('tabla_intro', ''))}</p>{compatibility_table}</section>
      <section><h2>Tiempos de carga</h2><p>{escape(page.get('tiempos_de_carga', ''))}</p></section>
      <section><h2>Preguntas frecuentes</h2>{faqs}</section>
      <section><h2>Fuentes oficiales</h2><ul>{sources}</ul>
        <p>Las relaciones se basan en documentación oficial del fabricante; no se realizaron pruebas físicas.</p></section>
    </article>"""
