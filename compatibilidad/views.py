"""Vistas HTML y componentes accesibles para la base de compatibilidad."""

import json
from html import escape
from urllib.parse import urlencode
from compatibilidad.catalog import CURRENT_METADATA, RELATIONS, refresh_published_state
from compatibilidad.catalog import catalog_read_locked
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, quote_plus, unquote_plus

from compatibilidad.catalog import (
    CHANGELOG,
    EVIDENCES_BY_ID,
    PLATFORMS,
    PLATFORMS_BY_ID,
    PRODUCTS_BY_ID,
    PRODUCTS_BY_SLUG,
    CATALOG_PRODUCTS,
)
from compatibilidad.models import Platform, Product, ProductType, Verdict
from compatibilidad.rules import CompatibilityEvaluation, evaluate_compatibility
from compatibilidad.search import GLOBAL_SEARCH_INDEX
from compatibilidad.telemetry import track_event
from compatibilidad.commercial import render_product_commercial, render_pair_commercial, render_related_kit
from compatibilidad.presentation import display_name, compatible_counterparts, relation_meta, relation_schema, product_kind, guide_links
from compatibilidad.presentation import coverage_summary, source_panel, relation_table, relationship_page, resolve_relationship, relationship_paths, model_picker_options, verified_directory, relation_path


def get_verdict_badge_html(verdict: str) -> str:
    """Retorna badge visual accesible con colores de contraste semántico."""
    if verdict == Verdict.COMPATIBLE_DOCUMENTADO.value:
        bg, text, icon = "#064e3b", "#34d399", "✓"
    elif verdict == Verdict.COMPATIBLE_BAJO_CONDICIONES.value:
        bg, text, icon = "#78350f", "#fbbf24", "⚠"
    elif verdict == Verdict.INCOMPATIBLE_DOCUMENTADO.value:
        bg, text, icon = "#7f1d1d", "#f87171", "✕"
    elif verdict == Verdict.CONFLICTO_EN_REVISION.value:
        bg, text, icon = "#581c87", "#c084fc", "⚡"
    else:
        bg, text, icon = "#1e293b", "#94a3b8", "？"

    return f'<span style="display: inline-flex; align-items: center; gap: 0.35rem; background: {bg}; color: {text}; font-weight: 700; font-size: 0.85rem; padding: 0.25rem 0.65rem; border-radius: 9999px; border: 1px solid {text}40;"><span>{icon}</span> {escape(verdict)}</span>'


def render_breadcrumb_html(crumbs: List[Tuple[str, str]]) -> str:
    """Renderiza migas de pan accesibles con marcado Schema.org."""
    items = []
    for i, (name, url) in enumerate(crumbs):
        if url:
            items.append(f'<a href="{escape(url)}" style="color: #94a3b8; text-decoration: none;">{escape(name)}</a>')
        else:
            items.append(f'<span style="color: #f8fafc; font-weight: 600;">{escape(name)}</span>')
    return '<nav aria-label="Breadcrumb" style="font-size: 0.85rem; margin-bottom: 1.5rem; color: #64748b; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;">' + " <span style='color: #475569;'>/</span> ".join(items) + "</nav>"


def get_product_schema_json(prod: Product, site_url: str = "") -> str:
    if prod.status != 'publicado':
        return '<meta name="robots" content="noindex, follow">'

    """WebPage sobre el modelo exacto. Sin Product: sin precio propio, Google lo marcaría como fragmento de producto no válido."""
    page_url = f"{site_url}/baterias/{prod.slug}/" if prod.product_type == ProductType.BATERIA.value else (f"{site_url}/herramientas-bateria/{prod.slug}/" if prod.product_type==ProductType.HERRAMIENTA.value else f"{site_url}/cargadores/{prod.slug}/")
    evidence = EVIDENCES_BY_ID.get(prod.evidence_identity_id)
    about = {"@type": "Thing", "name": f"{prod.brand} {prod.model_name}", "identifier": prod.mpn, "sameAs": prod.official_url}
    if prod.gtin_ean:
        about["identifier"] = [prod.mpn, prod.gtin_ean]
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "url": page_url,
        "inLanguage": "es-AR",
        "description": prod.notes or f"Ficha técnica y compatibilidad de {prod.model_name} en Argentina.",
        "about": about,
        "author": {"@type": "Person", "name": "Joaquín Vallasciani", "url": f"{site_url}/autor/joaquin-vallasciani/"},
        "isPartOf": {"@type": "Dataset", "name": "Base argentina de compatibilidad de baterías, herramientas y cargadores", "url": f"{site_url}/compatibilidad/"},
        "citation": prod.official_url,
    }
    if evidence and evidence.date_reviewed:
        schema["dateModified"] = evidence.date_reviewed[:10]
    return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def render_compatibility_hub_html() -> str:
    """Renderiza el Hub principal (/compatibilidad/)."""
    track_event("visita_hub", query_text="hub_visit")

    # Tarjetas de plataformas cubiertas
    platform_cards = []
    for plat in [p for p in PLATFORMS if any(x.platform_id==p.id and x.status=='publicado' for x in CATALOG_PRODUCTS)]:
        if plat.id in ("bosch-power-for-all-18v", "makita-xgt", "dewalt-60v-max"):
            continue  # Plataformas de contraste se tratan en sección de límites
        
        plat_prods = [p for p in CATALOG_PRODUCTS if p.platform_id == plat.id and p.status=='publicado']
        bat_count = len([p for p in plat_prods if p.product_type == ProductType.BATERIA.value])
        chg_count = len([p for p in plat_prods if p.product_type == ProductType.CARGADOR.value])
        tool_count = len([p for p in plat_prods if p.product_type == ProductType.HERRAMIENTA.value])

        platform_cards.append(f"""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
              <span style="background: {plat.badge_color}22; color: {plat.badge_color}; border: 1px solid {plat.badge_color}55; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;">{escape(plat.voltage_max)}</span>
              <span style="font-size: 0.8rem; color: #8b949e;">{escape(plat.brand)}</span>
            </div>
            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.25rem;"><a href="/plataformas/{plat.id}/" style="color: #f8fafc; text-decoration: none;">{escape(plat.name)}</a></h3>
            <p style="color: #8b949e; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1rem;">{escape('Las relaciones verificadas entre modelos se detallan en sus fichas. No se infiere compatibilidad para toda la plataforma.')}</p>
            <div style="background: #0d1117; border-left: 3px solid #ff5500; padding: 0.5rem 0.75rem; border-radius: 0 4px 4px 0; margin-bottom: 1rem;">
              <span style="color: #ff5500; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Atención / Excepciones:</span>
              <p style="color: #c9d1d9; font-size: 0.85rem; margin: 0.2rem 0 0 0;">{escape('Revisá el modelo y sus condiciones. Un registro pendiente no confirma compatibilidad.')}</p>
            </div>
          </div>
          <div style="border-top: 1px solid #30363d; padding-top: 1rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem;">
            <span style="color: #8b949e;"><strong>{bat_count}</strong> bat · <strong>{chg_count}</strong> carg · <strong>{tool_count}</strong> herr</span>
            <a href="/plataformas/{plat.id}/" style="color: #ff5500; font-weight: 600; text-decoration: none;">Ver plataforma →</a>
          </div>
        </div>
        """)

    cards_html = "".join(platform_cards)

    content = f"""
    <div style="max-width: 1040px; margin: 0 auto; padding: 2rem 1rem;">
      {render_breadcrumb_html([("Inicio", "/"), ("Compatibilidad de Baterías", "")])}

      <header style="margin-bottom: 2.5rem;">
        <span style="color: #ff5500; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;">TALLERLAB / BASE ARGENTINA DE COMPATIBILIDAD</span>
        <h1 style="font-size: 2.4rem; font-weight: 900; color: #f8fafc; margin: 0.5rem 0 1rem 0; line-height: 1.2;">Base argentina de compatibilidad de baterías, herramientas y cargadores</h1>
        <p style="font-size: 1.15rem; color: #8b949e; line-height: 1.6;">
          Encontrá qué batería sirve con tu herramienta o cargador. Cada respuesta identifica modelos exactos y enlaza las fuentes del fabricante. Los registros pendientes no confirman compatibilidad ni disponibilidad en Argentina.
        </p>
      </header>

      {coverage_summary()}
      {model_picker_options()}
      <!-- BUSCADOR DETERMINISTA -->
      <section style="background: #161b22; border: 1px solid #ff550044; border-radius: 12px; padding: 2rem; margin-bottom: 3rem; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
        <h2 style="font-size: 1.4rem; color: #f8fafc; margin-top: 0; margin-bottom: 0.5rem;">Buscador por modelo o código exacto</h2>
        <p style="color: #8b949e; font-size: 0.95rem; margin-bottom: 1.5rem;">
          Ingresá un código exacto verificado: <code>1600A016GB</code>, <code>1600A028U0</code>, <code>G12491AR</code> o <code>G12402/1AR</code>. Los demás registros muestran su estado pendiente.
        </p>
        <form action="/compatibilidad/buscar/" method="GET" style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
          <input type="text" list="compat-models" name="q" aria-label="Modelo o código de fabricante" placeholder="Ej: 1600A016GB o G12491AR" required style="flex: 1 1 320px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 0.75rem 1rem; color: #f8fafc; font-size: 1rem;" />
          <button type="submit" style="background: #ff5500; color: #ffffff; border: none; border-radius: 6px; padding: 0.75rem 1.5rem; font-weight: 700; font-size: 1rem; cursor: pointer; transition: background 0.15s ease;">Buscar modelo →</button>
        </form>

        <!-- VERIFICADOR RÁPIDO DE DOS MODELOS -->
        <div style="margin-top: 1.75rem; padding-top: 1.5rem; border-top: 1px solid #30363d;">
          <h3 style="font-size: 1.05rem; color: #f8fafc; margin-bottom: 0.5rem;">¿Tenés dos modelos y querés contrastar compatibilidad directa?</h3>
          <form action="/compatibilidad/buscar/" method="GET" style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            <input type="text" list="compat-models" name="a" aria-label="Modelo A: batería o cargador" required placeholder="Modelo A: 1600A016GB" style="flex: 1 1 200px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 0.6rem 0.85rem; color: #f8fafc; font-size: 0.95rem;" />
            <input type="text" list="compat-models" name="b" aria-label="Modelo B: herramienta o batería" required placeholder="Modelo B: 06019J40E0" style="flex: 1 1 200px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 0.6rem 0.85rem; color: #f8fafc; font-size: 0.95rem;" />
            <button type="submit" style="background: #30363d; color: #f8fafc; border: 1px solid #484f58; border-radius: 6px; padding: 0.6rem 1.25rem; font-weight: 600; font-size: 0.95rem; cursor: pointer;">Comprobar par →</button>
          </form>
        </div>
      </section>

      <!-- ACTIVO EDITORIAL: PLATAFORMAS CUBIERTAS EN ARGENTINA -->
      <section style="margin-bottom: 3.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; margin-bottom: 1.5rem;">
          <div>
            <h2 style="font-size: 1.6rem; color: #f8fafc; margin: 0;">Plataformas cubiertas en el catálogo argentino</h2>
            <p style="color: #8b949e; font-size: 0.95rem; margin-top: 0.25rem;">{sum(any(x.platform_id==p.id and x.status=='publicado' for x in CATALOG_PRODUCTS) for p in PLATFORMS)} sistemas con modelos verificados. La evidencia se limita a las combinaciones enumeradas.</p>
          </div>
          <a href="/compatibilidad/matriz-imprimible/" style="color: #ff5500; font-size: 0.9rem; font-weight: 600; text-decoration: none;">Ver matriz imprimible de referencia 🖨 →</a>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem;">
          {cards_html}
        </div>
      </section>

      {verified_directory()}
      <section><h2>¿Qué baterías y cargadores son compatibles?</h2><p>Cada fila identifica dos códigos exactos y enlaza la documentación que sostiene la respuesta. Una referencia pendiente no acredita compatibilidad.</p><div class="compat-filter" hidden><label for="compat-filter">Filtrar combinaciones por marca, modelo o código</label><input id="compat-filter" aria-label="Filtrar combinaciones" type="search" placeholder="Ej.: Gamma, GWS o 1600A016GB"><p id="compat-filter-status" role="status" aria-live="polite"></p></div>{relation_table()}</section>
      <section><h2>Preguntas frecuentes</h2><h3>¿Dos baterías de 18 V son intercambiables?</h3><p>El voltaje no basta. Se requiere documentación que vincule cada modelo con el sistema y una regla de compatibilidad del fabricante.</p><h3>¿Sin evidencia significa incompatible?</h3><p>No. Significa que esta base todavía no puede confirmar esa combinación. Consultá el código exacto y la fuente del fabricante.</p><h3>¿La ficha argentina garantiza stock o una variante importada?</h3><p>No. Identifica el producto documentado. En cargadores, verificá además la tensión de entrada en la placa y el manual de tu unidad.</p><h3>¿Qué pasa si cambia una fuente?</h3><p>Un cambio técnico suspende la respuesta y se conserva en el historial. La comprobación documental vence a los 30 días sin renovación.</p></section>
      <!-- METODOLOGÍA Y DESCARGA DE DATOS -->
      <footer style="background: #161b22; border-radius: 8px; border: 1px solid #30363d; padding: 1.5rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <h4 style="margin: 0; color: #f8fafc; font-size: 1.05rem;">Datos abiertos y metodología editorial</h4>
          <p style="margin: 0.25rem 0 0 0; color: #8b949e; font-size: 0.85rem;">
            Investigación documental de Joaquín Vallasciani. Descargá el dataset completo con fuentes y fechas de revisión.
          </p>
        </div>
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
          <a href="/compatibilidad/metodologia/" style="background: #21262d; color: #f8fafc; border: 1px solid #30363d; padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.85rem; text-decoration: none; font-weight: 600;">Metodología y correcciones →</a>
          <a href="/datos/compatibilidad/baterias.csv" style="background: #ff5500; color: #ffffff; padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.85rem; text-decoration: none; font-weight: 700;">Descargar CSV ↓</a>
          <a href="/datos/compatibilidad/baterias.json" style="background: #21262d; color: #8b949e; border: 1px solid #30363d; padding: 0.45rem 0.85rem; border-radius: 6px; font-size: 0.85rem; text-decoration: none; font-weight: 600;">JSON ↓</a>
        </div>
      </footer>
    </div>
    """
    return content


def render_compatibility_search_results_html(query: str = "", model_a: str = "", model_b: str = "") -> str:
    """Renderiza la página de resultados de búsqueda (/compatibilidad/buscar/)."""
    # 1. Caso de comparación de par
    pair_evaluation: Optional[CompatibilityEvaluation] = None
    prod_a: Optional[Product] = None
    prod_b: Optional[Product] = None

    if model_a and model_b:
        prod_a, prod_b, pair_evaluation = GLOBAL_SEARCH_INDEX.check_pair(model_a, model_b)
        if pair_evaluation:
            if pair_evaluation.is_ambiguous:
                track_event(
                    "identidad_ambigua",
                    model_a=model_a,
                    model_b=model_b,
                    verdict=pair_evaluation.verdict,
                )
            elif pair_evaluation.verdict in (Verdict.SIN_EVIDENCIA_SUFICIENTE.value, Verdict.CONFLICTO_EN_REVISION.value):
                track_event(
                    "resultado_desconocido",
                    model_a=model_a,
                    model_b=model_b,
                    verdict=pair_evaluation.verdict,
                )
            else:
                track_event(
                    "busqueda_resuelta",
                    model_a=model_a,
                    model_b=model_b,
                    verdict=pair_evaluation.verdict,
                )
        else:
            track_event(
                "modelo_no_encontrado",
                model_a=model_a,
                model_b=model_b,
            )

    # 2. Búsqueda por término individual
    results = []
    if query:
        results = GLOBAL_SEARCH_INDEX.search(query, limit=30)
        track_event("consulta_modelo" if results else "modelo_no_encontrado", query_text=query[:120])

    crumbs = [("Inicio", "/"), ("Compatibilidad", "/compatibilidad/"), ("Resultados de búsqueda", "")]

    pair_section = ""
    if model_a and model_b:
        if pair_evaluation and pair_evaluation.is_ambiguous:
            groups=[]
            for side, ids in pair_evaluation.candidates_by_side.items():
                if not ids:
                    continue
                links=[]
                for pid in ids:
                    candidate=PRODUCTS_BY_ID[pid]
                    params={'a':model_a,'b':model_b,side:pid}
                    href='/compatibilidad/buscar/?'+urlencode(params)
                    links.append(f'<li><a href="{escape(href)}">{escape(candidate.brand)} {escape(candidate.mpn)} — {escape(candidate.model_name)} ({escape(candidate.status)})</a></li>')
                groups.append('<h3>Modelo '+side.upper()+'</h3><ul>'+''.join(links)+'</ul>')
            pair_section='<section class="compat-ambiguity"><h2>Elegí el modelo exacto</h2><p>Seleccioná cada modelo identificado. Los códigos desconocidos deben corregirse; no se sustituyen por sugerencias del otro extremo.</p>'+''.join(groups)+'</section>'
        elif not prod_a or not prod_b:
            missing = []
            if not prod_a: missing.append(f"'{escape(model_a)}'")
            if not prod_b: missing.append(f"'{escape(model_b)}'")
            pair_section = f"""
            <div style="background: #1f1d1d; border: 1px solid #f8717144; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem;">
              <h3 style="color: #f87171; margin-top: 0;">Modelo no identificado</h3>
              <p style="color: #c9d1d9;">No pudimos encontrar en la base el/los modelo(s): {", ".join(missing)}.</p>
              <p style="color: #8b949e; font-size: 0.85rem; margin-bottom: 0;">Verificá el código exacto de fabricante o <a href="/compatibilidad/metodologia/" style="color: #ff5500;">reportalo para revisión</a>.</p>
            </div>
            """
        else:
            ev = pair_evaluation
            badge = get_verdict_badge_html(ev.verdict)
            evidence_rows = "".join(f"""
              <li style="margin-bottom: 0.75rem; color: #8b949e; font-size: 0.85rem;">
                <strong style="color: #f8fafc;">{escape(e.document_title)}</strong> ({escape(e.manufacturer)}) — Sección: {escape(e.section_or_page)}.<br>
                <em style="color: #c9d1d9; display: block; margin: 0.2rem 0; padding-left: 0.5rem; border-left: 2px solid #30363d;">«{escape(e.excerpt)}»</em>
                    <span style="font-size: 0.75rem; color: #64748b;">Revisado por {escape(e.reviewer)} el {escape(e.date_reviewed)} · <a data-compat-event="clic_fuente" href="{escape(e.official_url)}" target="_blank" rel="noopener" style="color: #ff5500;">Fuente oficial ↗</a></span>
                    {' '.join('<a data-compat-event="clic_fuente" href="'+escape(url)+'">Manual oficial complementario</a>' for url in e.supporting_urls)}
              </li>
            """ for e in ev.evidence_chain)

            conditions_box = ""
            if ev.conditions:
                cond_items = "".join(f"<li style='margin-bottom: 0.35rem;'>{escape(c)}</li>" for c in ev.conditions)
                conditions_box = f"""
                <div style="background: #1c1917; border-left: 4px solid #f59e0b; padding: 1rem 1.25rem; border-radius: 0 6px 6px 0; margin: 1rem 0;">
                  <strong style="color: #fbbf24; font-size: 0.9rem;">Condiciones obligatorias de compatibilidad:</strong>
                  <ul style="color: #d6d3d1; font-size: 0.9rem; margin: 0.5rem 0 0 1.25rem; padding: 0;">{cond_items}</ul>
                </div>
                """

            exclusions_box = ""
            if ev.exclusions:
                excl_items = "".join(f"<li style='margin-bottom: 0.35rem;'>{escape(ex)}</li>" for ex in ev.exclusions)
                exclusions_box = f"""
                <div style="background: #1f1315; border-left: 4px solid #ef4444; padding: 1rem 1.25rem; border-radius: 0 6px 6px 0; margin: 1rem 0;">
                  <strong style="color: #f87171; font-size: 0.9rem;">Exclusiones e incompatibilidades documentadas:</strong>
                  <ul style="color: #fca5a5; font-size: 0.9rem; margin: 0.5rem 0 0 1.25rem; padding: 0;">{excl_items}</ul>
                </div>
                """

            pair_section = f"""
            <div style="background: #161b22; border: 2px solid #ff550055; border-radius: 12px; padding: 2rem; margin-bottom: 2.5rem;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
                <div>
                  <span style="font-size: 0.8rem; color: #8b949e; text-transform: uppercase; font-weight: 700;">DICTAMEN DE COMPATIBILIDAD TALLERLAB</span>
                  <h2 style="font-size: 1.8rem; color: #f8fafc; margin: 0.25rem 0 0.5rem 0;">
                    {escape(prod_a.model_name)} <span style="color: #ff5500;">↔</span> {escape(prod_b.model_name)}
                  </h2>
                </div>
                <div>{badge}<br><a style="font-size:.8rem" href="{relation_path(ev.source_product,ev.target_product)}">Ver respuesta y fuentes</a></div>
              </div>

              <p style="font-size: 1.1rem; color: #e6edf3; line-height: 1.5; margin-bottom: 1rem;">{escape(ev.summary_text)}</p>

              {conditions_box}
              {exclusions_box}

              <div style="background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; margin-top: 1.5rem;">
                <h4 style="margin-top: 0; color: #f8fafc; font-size: 0.95rem;">Cadena de evidencia documental:</h4>
                <p style="font-size: 0.85rem; color: #8b949e; margin-bottom: 0.75rem;">Método de comprobación: <code>{escape(ev.derivation_method)}</code></p>
                <ul style="margin: 0; padding-left: 1.25rem;">
                  {evidence_rows if evidence_rows else "<li style='color: #8b949e; font-size: 0.85rem;'>No hay evidencia suficiente para esta combinación.</li>"}
                </ul>
              </div>
            </div>
            """

    if prod_a and prod_b and pair_evaluation and not pair_evaluation.is_ambiguous:
        pair_section += render_pair_commercial(prod_a, prod_b)

    # Resultados de búsqueda libre
    search_cards = []
    for prod, score in results:
        plat = PLATFORMS_BY_ID.get(prod.platform_id)
        plat_badge = f'<span style="background: {plat.badge_color if plat else "#666"}22; color: {plat.badge_color if plat else "#aaa"}; border: 1px solid {plat.badge_color if plat else "#666"}44; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px;">{escape(plat.name if plat else prod.platform_id)}</span>'
        
        url = f"/baterias/{prod.slug}/" if prod.product_type == ProductType.BATERIA.value else (f"/cargadores/{prod.slug}/" if prod.product_type == ProductType.CARGADOR.value else f"/herramientas-bateria/{prod.slug}/")
        
        search_cards.append(f"""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.35rem;">
              <span style="font-size: 0.8rem; color: #ff5500; font-weight: 700; text-transform: uppercase;">{escape(prod.product_type)}</span>
              {plat_badge}
            </div>
            <h3 style="margin: 0.25rem 0 0.5rem 0; font-size: 1.15rem;">
              <a href="{url}" style="color: #f8fafc; text-decoration: none;">{escape(prod.brand)} {escape(prod.model_name)}</a>
            </h3>
            <p style="font-size: 0.85rem; color: #8b949e; margin-bottom: 0.5rem;">
              Código MPN: <code>{escape(prod.mpn)}</code> {f"· GTIN: {escape(prod.gtin_ean)}" if prod.gtin_ean else ""}
            </p>
            <p style="font-size: 0.85rem; color: #c9d1d9; line-height: 1.4; margin-bottom: 0.75rem;">
              {escape(prod.market_availability_notes)}
            </p>
          </div>
          <div style="border-top: 1px solid #21262d; pt: 0.75rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; margin-top: 0.5rem;">
            <span style="color: #64748b;">{escape(prod.voltage_nominal or "")} {f"· {prod.capacity_ah} Ah" if prod.capacity_ah else ""}</span>
            <a href="{url}" style="color: #ff5500; font-weight: 600; text-decoration: none;">Ver ficha técnica →</a>
          </div>
        </div>
        """)

    cards_grid = "".join(search_cards)

    content = f"""
    <div style="max-width: 1040px; margin: 0 auto; padding: 2rem 1rem;">
      {render_breadcrumb_html(crumbs)}

      <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.2rem; color: #f8fafc; margin-top: 0;">Consulta de compatibilidad</h1>
        <p style="color: #8b949e;">Resultados basados en documentación técnica primaria y catálogo oficial para Argentina.</p>
      </div>

      {pair_section}

      <section style="margin-bottom: 3rem;" {'hidden' if not query else ''}>
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.5rem; flex-wrap: wrap;">
          <h2 style="font-size: 1.4rem; color: #f8fafc; margin: 0;">
            {f"Modelos encontrados para '{escape(query)}' ({len(results)})" if query else "Modelos documentados"}
          </h2>
          <a href="/compatibilidad/" style="color: #ff5500; font-size: 0.9rem; text-decoration: none;">← Nueva búsqueda</a>
        </div>

        {f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem;">{cards_grid}</div>' if results else '<p style="color: #8b949e; background: #161b22; padding: 1.5rem; border-radius: 8px;">No se encontraron modelos con ese término exacto. Probá buscando por código MPN de fábrica (ej. 1600A016GB, BL1850B, DCB115-AR).</p>'}
      </section>
    </div>
    """
    return content


def render_platform_page_html(platform_id: str) -> str:
    """Renderiza la ficha completa de una plataforma (/plataformas/<id>/)."""
    plat = PLATFORMS_BY_ID.get(platform_id)
    if not plat:
        return ""

    track_event("visita_plataforma", query_text=f"platform_{platform_id}")

    prods = [p for p in CATALOG_PRODUCTS if p.platform_id == plat.id and p.status=='publicado']
    batteries = [p for p in prods if p.product_type == ProductType.BATERIA.value]
    chargers = [p for p in prods if p.product_type == ProductType.CARGADOR.value or p.product_type == ProductType.ADAPTADOR.value]
    tools = [p for p in prods if p.product_type == ProductType.HERRAMIENTA.value]

    crumbs = [("Inicio", "/"), ("Compatibilidad", "/compatibilidad/"), (plat.name, "")]

    def render_prod_list(items):
        if not items:
            return "<p style='color: #8b949e; font-size: 0.9rem;'>No hay modelos documentados en esta categoría.</p>"
        rows = []
        for p in items:
            url = f"/baterias/{p.slug}/" if p.product_type == ProductType.BATERIA.value else (f"/cargadores/{p.slug}/" if p.product_type == ProductType.CARGADOR.value else f"/herramientas-bateria/{p.slug}/")
            is_external = False
            rows.append(f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
              <div>
                <strong style="color: #f8fafc; font-size: 1rem;">{escape(p.model_name)}</strong>
                <span style="color: #8b949e; font-size: 0.85rem; margin-left: 0.5rem;">MPN: <code>{escape(p.mpn)}</code></span>
                {f'<span style="background: #e6510022; color: #ff5500; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.4rem; border-radius: 4px; margin-left: 0.5rem;">Exige {p.required_packs} packs</span>' if p.required_packs > 1 else ''}
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0.25rem 0 0 0;">{escape(p.market_availability_notes)}</p>
              </div>
              <a href="{url}" {"target='_blank' rel='noopener'" if is_external else ""} style="color: #ff5500; font-size: 0.85rem; font-weight: 600; text-decoration: none;">
                {"Fuente oficial ↗" if is_external else "Ver ficha →"}
              </a>
            </div>
            """)
        return "".join(rows)

    exceptions_html = '<li>No extrapolar estas respuestas a modelos sin evidencia.</li>'

    content = f"""
    <div style="max-width: 1040px; margin: 0 auto; padding: 2rem 1rem;">
      {render_breadcrumb_html(crumbs)}

      <header style="margin-bottom: 2.5rem;">
        <span style="background: {plat.badge_color}22; color: {plat.badge_color}; border: 1px solid {plat.badge_color}55; font-size: 0.8rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase;">
          {escape(plat.brand)} · {escape(plat.voltage_max)}
        </span>
        <h1 style="font-size: 2.4rem; font-weight: 900; color: #f8fafc; margin: 0.75rem 0 0.5rem 0;">{escape(plat.name)}</h1>
        <p style="font-size: 1.15rem; color: #8b949e; line-height: 1.6;">{escape('Registros verificados de esta plataforma y fuentes documentales.')}</p>
      </header>

      <!-- REGLA DE COMPATIBILIDAD Y EXCEPCIONES -->
      <section style="background: #161b22; border-left: 4px solid {plat.badge_color}; border-radius: 0 8px 8px 0; padding: 1.5rem; margin-bottom: 2.5rem;">
        <h2 style="font-size: 1.25rem; color: #f8fafc; margin-top: 0; margin-bottom: 0.5rem;">Regla técnica de la plataforma</h2>
        <p style="color: #e6edf3; font-size: 1.05rem; line-height: 1.5; margin-bottom: 1rem;">{escape('Las relaciones verificadas entre modelos se detallan en sus fichas. No se infiere compatibilidad para toda la plataforma.')}</p>
        
        <h3 style="font-size: 0.95rem; color: #ff5500; text-transform: uppercase; margin-bottom: 0.5rem;">Excepciones y límites formales:</h3>
        <ul style="color: #c9d1d9; font-size: 0.9rem; margin: 0; padding-left: 1.25rem;">
          {exceptions_html}
        </ul>
      </section>

      <!-- BATERÍAS DOCUMENTADAS -->
      <section style="margin-bottom: 2.5rem;">
        <h2 style="font-size: 1.4rem; color: #f8fafc; margin-bottom: 1rem;">Baterías documentadas en Argentina ({len(batteries)})</h2>
        {render_prod_list(batteries)}
      </section>

      <!-- CARGADORES DOCUMENTADOS -->
      <section style="margin-bottom: 2.5rem;">
        <h2 style="font-size: 1.4rem; color: #f8fafc; margin-bottom: 1rem;">Cargadores con compatibilidad documentada ({len(chargers)})</h2>
        {render_prod_list(chargers)}
      </section>

      <!-- HERRAMIENTAS DOCUMENTADAS -->
      <section style="margin-bottom: 3rem;">
        <h2 style="font-size: 1.4rem; color: #f8fafc; margin-bottom: 1rem;">Herramientas documentadas del sistema ({len(tools)})</h2>
        {render_prod_list(tools)}
      </section>

      <!-- ENLACE METODOLOGÍA -->
      <div style="background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <span style="color: #8b949e; font-size: 0.85rem;">Modelos con evidencia verificada. Fuentes oficiales de {escape(plat.brand)}.</span>
        <a href="/compatibilidad/metodologia/" style="color: #ff5500; font-size: 0.85rem; font-weight: 600; text-decoration: none;">Ver fuentes y canal de corrección →</a>
      </div>
    </div>
    """
    return content + render_related_kit(platform_id=platform_id)


def render_battery_detail_page_html(slug: str) -> str:
    """Renderiza la ficha técnica de una batería (/baterias/<slug>/)."""
    battery = PRODUCTS_BY_SLUG.get(slug)
    if not battery or battery.product_type != ProductType.BATERIA.value:
        return ""

    if battery.status != 'publicado':
        return render_pending_product(battery)
    track_event("visita_ficha", query_text=f"battery_{slug}")

    plat = PLATFORMS_BY_ID.get(battery.platform_id)
    plat_name = plat.name if plat else battery.platform_id
    plat_badge = plat.badge_color if plat else "#ff5500"

    crumbs = [("Inicio", "/"), ("Compatibilidad", "/compatibilidad/"), (plat_name, f"/plataformas/{battery.platform_id}/"), (battery.model_name, "")]

    # Evaluar herramientas candidatas (misma marca o plataforma)
    candidate_tools = [p for p in CATALOG_PRODUCTS if p.product_type == ProductType.HERRAMIENTA.value and (p.platform_id == battery.platform_id or p.brand == battery.brand)]
    compatible_tools = []
    incompatible_tools = []
    for t in candidate_tools:
        ev = evaluate_compatibility(battery, t)
        if ev.is_compatible:
            compatible_tools.append((t, ev))
        elif ev.verdict == Verdict.INCOMPATIBLE_DOCUMENTADO.value:
            incompatible_tools.append((t, ev))

    tool_rows = []
    for t, ev in compatible_tools:
        badge = get_verdict_badge_html(ev.verdict)
        cond_text = f"<span style='color: #fbbf24; font-size: 0.8rem; display: block;'>{'; '.join(ev.conditions)}</span>" if ev.conditions else ""
        recom_text = f"<span style='color: #38bdf8; font-size: 0.8rem; display: block;'>Recomendación: {'; '.join(ev.recommendations)}</span>" if getattr(ev, "recommendations", None) else ""
        tool_rows.append(f"""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <strong style="color: #f8fafc; font-size: 0.95rem;">{escape(t.model_name)}</strong>
            <span style="color: #8b949e; font-size: 0.8rem; margin-left: 0.5rem;">MPN: <code>{escape(t.mpn)}</code></span>
            {f'<span style="background: #e6510022; color: #ff5500; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.4rem; border-radius: 4px; margin-left: 0.5rem;">Exige {t.required_packs} packs</span>' if t.required_packs > 1 else ''}
            {cond_text}
            {recom_text}
          </div>
          <div>{badge}<br><a style="font-size:.8rem" href="{relation_path(ev.source_product,ev.target_product)}">Ver respuesta y fuentes</a></div>
        </div>
        """)

    candidate_chargers = [p for p in CATALOG_PRODUCTS if (p.product_type == ProductType.CARGADOR.value or p.product_type == ProductType.ADAPTADOR.value) and (p.platform_id == battery.platform_id or p.brand == battery.brand)]
    compatible_chargers = []
    for ch in candidate_chargers:
        ev = evaluate_compatibility(ch, battery)
        if ev.is_compatible:
            compatible_chargers.append((ch, ev))

    charger_rows = []
    for ch, ev in compatible_chargers:
        badge = get_verdict_badge_html(ev.verdict)
        cond_text = f"<span style='color: #fbbf24; font-size: 0.8rem; display: block;'>{'; '.join(ev.conditions)}</span>" if ev.conditions else ""
        charger_rows.append(f"""
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <strong style="color: #f8fafc; font-size: 0.95rem;"><a href="/cargadores/{ch.slug}/" style="color: #f8fafc; text-decoration: none;">{escape(ch.model_name)}</a></strong>
            <span style="color: #8b949e; font-size: 0.8rem; margin-left: 0.5rem;">MPN: <code>{escape(ch.mpn)}</code></span>
            {cond_text}
          </div>
          <div>{badge}<br><a style="font-size:.8rem" href="{relation_path(ev.source_product,ev.target_product)}">Ver respuesta y fuentes</a></div>
        </div>
        """)

    specs_rows = "".join(f"<tr><td style='padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;'>{escape(k.replace('_', ' ').capitalize())}</td><td style='padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;'>{escape(v)}</td></tr>" for k, v in battery.specs.items())

    content = f"""
    <div style="max-width: 1040px; margin: 0 auto; padding: 2rem 1rem;">
      {render_breadcrumb_html(crumbs)}

      <header style="margin-bottom: 2.5rem;">
        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
          <span style="background: {plat_badge}22; color: {plat_badge}; border: 1px solid {plat_badge}55; font-size: 0.8rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;">{escape(plat_name)}</span>
          <span style="background: #1e293b; color: #94a3b8; font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px;">Código de pedido: {escape(battery.mpn)}</span>
        </div>
        <h1 style="font-size: 2.4rem; font-weight: 900; color: #f8fafc; margin: 0.5rem 0 0.5rem 0;">{escape(display_name(battery)[0].upper()+display_name(battery)[1:])}: herramientas y cargadores compatibles</h1>
        <p style="font-size: 1.15rem; color: #8b949e;">{escape(battery.notes)}</p>
      </header>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem;">
        <!-- TABLA DE ESPECIFICACIONES TÉCNICAS -->
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem;">
          <h2 style="font-size: 1.2rem; color: #f8fafc; margin-top: 0; margin-bottom: 1rem;">Especificaciones eléctricas</h2>
          <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
            <tbody>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Voltaje nominal</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;">{escape(battery.voltage_nominal or 'No documentado')}</td></tr>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Voltaje máximo</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;">{escape(battery.voltage_max or 'No documentado')}</td></tr>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Capacidad nominal</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;">{battery.capacity_ah} Ah</td></tr>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Catálogo Argentina</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #34d399; font-weight: 600;">{("Catalogado por el fabricante en Argentina" if battery.is_argentina_catalog else "Referencia de catálogo internacional")}</td></tr>
              {specs_rows}
            </tbody>
          </table>
          <p style="font-size: 0.8rem; color: #64748b; margin-top: 1rem; margin-bottom: 0;">
            Fuente oficial: <a href="{escape(battery.official_url)}" target="_blank" rel="noopener" style="color: #ff5500;">Ficha técnica de fabricante ↗</a>
          </p>
        </div>

        <!-- REGLAS DE PLATAFORMA Y EXCEPCIONES -->
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem;">
          <h2 style="font-size: 1.2rem; color: #f8fafc; margin-top: 0; margin-bottom: 1rem;">Pertenencia y límites de sistema</h2>
          <p style="color: #c9d1d9; font-size: 0.95rem; line-height: 1.5;">{escape('Se confirma únicamente la compatibilidad de las relaciones enumeradas en esta ficha.')}</p>
          <div style="background: #0d1117; border-left: 3px solid #ff5500; padding: 0.75rem 1rem; border-radius: 0 4px 4px 0; margin-top: 1rem;">
            <strong style="color: #ff5500; font-size: 0.8rem; text-transform: uppercase;">Aclaración sobre el mercado local:</strong>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0.25rem 0 0 0;">{escape(battery.market_availability_notes)}</p>
          </div>
        </div>
      </div>

      <!-- CARGADORES COMPATIBLES -->
      <section style="margin-bottom: 2.5rem;">
        <h2 style="font-size: 1.35rem; color: #f8fafc; margin-bottom: 0.75rem;">Cargadores compatibles documentados ({len(compatible_chargers)})</h2>
        {"".join(charger_rows) if charger_rows else "<p style='color: #8b949e; font-size: 0.9rem;'>No hay cargadores compatibles documentados.</p>"}
      </section>

      <!-- HERRAMIENTAS COMPATIBLES -->
      <section style="margin-bottom: 3rem;">
        <h2 style="font-size: 1.35rem; color: #f8fafc; margin-bottom: 0.75rem;">Herramientas documentadas que aceptan esta batería ({len(compatible_tools)})</h2>
        {"".join(tool_rows) if tool_rows else "<p style='color: #8b949e; font-size: 0.9rem;'>No hay herramientas compatibles documentadas en este catálogo.</p>"}
      </section>
    </div>
    """
    return content + source_panel(battery) + render_product_commercial(battery)


def render_charger_detail_page_html(slug: str) -> str:
    """Renderiza la ficha técnica de un cargador (/cargadores/<slug>/)."""
    charger = PRODUCTS_BY_SLUG.get(slug)
    if not charger or (charger.product_type != ProductType.CARGADOR.value and charger.product_type != ProductType.ADAPTADOR.value):
        return ""

    if charger.status != 'publicado':
        return render_pending_product(charger)
    track_event("visita_ficha", query_text=f"charger_{slug}")

    plat = PLATFORMS_BY_ID.get(charger.platform_id)
    plat_name = plat.name if plat else charger.platform_id
    plat_badge = plat.badge_color if plat else "#ff5500"

    crumbs = [("Inicio", "/"), ("Compatibilidad", "/compatibilidad/"), (plat_name, f"/plataformas/{charger.platform_id}/"), (charger.model_name, "")]

    # Baterías que carga
    candidate_batteries = [p for p in CATALOG_PRODUCTS if p.product_type == ProductType.BATERIA.value and (p.platform_id == charger.platform_id or charger.brand == p.brand)]
    
    battery_rows = []
    for b in candidate_batteries:
        ev = evaluate_compatibility(charger, b)
        if ev.is_compatible:
            badge = get_verdict_badge_html(ev.verdict)
            cond_text = f"<span style='color: #fbbf24; font-size: 0.8rem; display: block;'>{'; '.join(ev.conditions)}</span>" if ev.conditions else ""
            battery_rows.append(f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <strong style="color: #f8fafc; font-size: 0.95rem;"><a href="/baterias/{b.slug}/" style="color: #f8fafc; text-decoration: none;">{escape(b.model_name)}</a></strong>
                <span style="color: #8b949e; font-size: 0.8rem; margin-left: 0.5rem;">MPN: <code>{escape(b.mpn)}</code> · {b.capacity_ah} Ah</span>
                {cond_text}
              </div>
              <div>{badge}<br><a style="font-size:.8rem" href="{relation_path(ev.source_product,ev.target_product)}">Ver respuesta y fuentes</a></div>
            </div>
            """)

    specs_rows = "".join(f"<tr><td style='padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;'>{escape(k.replace('_', ' ').capitalize())}</td><td style='padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;'>{escape(v)}</td></tr>" for k, v in charger.specs.items())

    content = f"""
    <div style="max-width: 1040px; margin: 0 auto; padding: 2rem 1rem;">
      {render_breadcrumb_html(crumbs)}

      <header style="margin-bottom: 2.5rem;">
        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
          <span style="background: {plat_badge}22; color: {plat_badge}; border: 1px solid {plat_badge}55; font-size: 0.8rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;">{escape(plat_name)}</span>
          <span style="background: #1e293b; color: #94a3b8; font-size: 0.8rem; padding: 0.2rem 0.5rem; border-radius: 4px;">Código de pedido: {escape(charger.mpn)}</span>
        </div>
        <h1 style="font-size: 2.4rem; font-weight: 900; color: #f8fafc; margin: 0.5rem 0 0.5rem 0;">{escape(display_name(charger)[0].upper()+display_name(charger)[1:])}: qué baterías carga</h1>
        <p style="font-size: 1.15rem; color: #8b949e;">{escape(charger.notes)}</p>
      </header>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2.5rem;">
        <!-- TABLA DE ESPECIFICACIONES -->
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem;">
          <h2 style="font-size: 1.2rem; color: #f8fafc; margin-top: 0; margin-bottom: 1rem;">Especificaciones de entrada y carga</h2>
          <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
            <tbody>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Tensión de salida</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;">{escape(charger.voltage_nominal or 'No documentado')}</td></tr>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Tensión de red</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #f8fafc; font-weight: 600;">{escape(charger.specs.get("tension_red", "Consultar placa y manual del código exacto"))}</td></tr>
              <tr><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #8b949e;">Catálogo Argentina</td><td style="padding: 0.4rem 0.75rem; border-bottom: 1px solid #21262d; color: #34d399; font-weight: 600;">{("Ficha oficial argentina (verificar la placa de la unidad)" if charger.is_argentina_catalog else "Referencia internacional (verificar tensión 220V)")}</td></tr>
              {specs_rows}
            </tbody>
          </table>
          <p style="font-size: 0.8rem; color: #64748b; margin-top: 1rem; margin-bottom: 0;">
            Fuente oficial: <a href="{escape(charger.official_url)}" target="_blank" rel="noopener" style="color: #ff5500;">Manual de fabricante ↗</a>
          </p>
        </div>

        <!-- CONDICIÓN REGIONAL Y ADVERTENCIA -->
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.5rem;">
          <h2 style="font-size: 1.2rem; color: #f8fafc; margin-top: 0; margin-bottom: 1rem;">Sufijo regional y seguridad eléctrica</h2>
          <p style="color: #c9d1d9; font-size: 0.95rem; line-height: 1.5;">{escape(charger.market_availability_notes)}</p>
          <div style="background: #0d1117; border-left: 3px solid #ff5500; padding: 0.75rem 1rem; border-radius: 0 4px 4px 0; margin-top: 1rem;">
            <strong style="color: #ff5500; font-size: 0.8rem; text-transform: uppercase;">Importación y voltaje:</strong>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0.25rem 0 0 0;">
              La ficha argentina no certifica variantes importadas. Consultá la tensión de entrada en la placa y el manual del cargador exacto.
            </p>
          </div>
        </div>
      </div>

      <!-- BATERÍAS ADMITIDAS -->
      <section style="margin-bottom: 3rem;">
        <h2 style="font-size: 1.35rem; color: #f8fafc; margin-bottom: 0.75rem;">Baterías verificadas que admite este cargador ({len(battery_rows)})</h2>
        {"".join(battery_rows)}
      </section>
    </div>
    """
    return content + source_panel(charger) + render_product_commercial(charger)


def render_printable_matrix_html() -> str:
    return f'<article class="compat-print"><h1>Matriz de compatibilidad de baterías, cargadores y herramientas</h1><p>Versión: {escape(CURRENT_METADATA["version"])}. Fecha de corte: {escape(CURRENT_METADATA.get("last_checked_at", "")[:10])} (UTC).</p><button onclick="window.print()">Imprimir tabla con fuentes</button>{coverage_summary()}<p>Solo se enumeran combinaciones con evidencia vigente. Recopilación documental de TallerLab; no acredita ensayo físico, stock ni variantes diferentes.</p>{relation_table(printable=True)}<p>Licencia CC BY 4.0 para la recopilación propia. Documentos originales: derechos de sus fabricantes. tallerlab.com.ar/compatibilidad/</p></article>'

def render_compatibility_changes_html() -> str:
    entries=''.join(f'<li><time>{escape(c.date)}</time> · {escape(c.author)}<p>{escape(c.description)}</p><p>Versión: <code>{escape(c.version)}</code> · {len(c.affected_records)} registros afectados.</p></li>' for c in reversed(CHANGELOG))
    return f'<article class="compat-answer"><h1>Historial de la base de compatibilidad</h1>{coverage_summary()}<p>Las fechas corresponden a comprobaciones y publicaciones registradas. Una nueva exportación no renueva la evidencia.</p><ol>{entries}</ol><p><a href="/compatibilidad/metodologia/">Metodología y correcciones</a> · <a href="/compatibilidad/">Ver combinaciones documentadas</a></p></article>'

def render_compatibility_methodology_html() -> str:
    active=sum(p.status=='publicado' for p in CATALOG_PRODUCTS)
    return f"""<article style="max-width:860px;margin:auto;padding:2rem 1rem">
    <h1>Fuentes, cobertura y correcciones</h1>
    <p>Versión: {escape(CURRENT_METADATA['version'])}. {active} registros con identidad y pertenencia comprobadas; {len(CATALOG_PRODUCTS)-active} pendientes.</p>
    <h2>Cómo se obtiene una respuesta</h2><p>Exigimos la identidad de ambos modelos, su pertenencia y una declaración oficial que sostenga la relación. Cada respuesta documentada enlaza la fuente, el extracto y la fecha de comprobación. No se deduce compatibilidad por marca, voltaje o apariencia.</p>
    <h2>Mantenimiento</h2><p>El monitor descarga completas las fichas configuradas y conserva su texto y hash en versiones privadas. Valida afirmaciones explícitas del perfil. Las fuentes inaccesibles y los cambios de contenido suspenden la respuesta hasta comprobarla. Los modelos nuevos requieren un perfil revisado; el sistema no descubre ni aprueba automáticamente cualquier herramienta.</p>
    <p>La programación requiere desplegar el cron y configurar almacenamiento PostgreSQL y un secreto privado. La versión visible y las fechas de cada evidencia indican qué se publicó efectivamente; una descarga del dataset no renueva la comprobación. Una evidencia sin nueva comprobación durante 30 días deja de sostener un veredicto definitivo.</p>
    <h2>Alcance</h2><p>Se trata de comprobación documental, no ensayo físico ni certificación eléctrica. Una ficha oficial argentina no demuestra stock, homologación IRAM ni compatibilidad con adaptadores externos. Las citas breves son extractos del fabricante; la revisión automática se identifica como tal.</p>
    <h2>Estados</h2><p>Compatible documentado, compatible bajo condiciones, incompatible documentado, sin evidencia suficiente y conflicto en revisión. Una ausencia de prueba no demuestra incompatibilidad.</p>
    <h2>Datos y licencia</h2><p>JSON contiene productos, evidencias, relaciones y versiones; CSV enumera relaciones documentadas. La recopilación propia usa CC BY 4.0. Los textos y documentos originales conservan los derechos de sus fabricantes.</p>
    <p><a href="/contacto/">Reportar una corrección</a>: indicá modelo exacto, afirmación y URL oficial.</p></article>"""


def render_pending_product(product):
    return f'<meta name="robots" content="noindex, follow"><article style="max-width:860px;margin:auto;padding:2rem 1rem"><h1>{escape(product.brand)} {escape(product.mpn)}</h1><p>Registro pendiente de verificación documental. No confirmamos identidad técnica, disponibilidad ni compatibilidad.</p><p><a href="/compatibilidad/buscar/">Consultar otro modelo</a> · <a href="/compatibilidad/metodologia/">Fuentes y correcciones</a></p></article>'

def render_tool_detail(product):
    if product.status!='publicado':
        return render_pending_product(product)
    rows=[]
    batteries=[]
    for battery,path in compatible_counterparts(product):
        if battery.product_type!='bateria':
            continue
        ev=evaluate_compatibility(battery,product)
        batteries.append(battery)
        rows.append(f'<li><a href="{escape(path)}">{escape(battery.brand)} {escape(battery.model_name)} ({escape(battery.mpn)})</a> — {escape(ev.verdict)}</li>')
    evidence=EVIDENCES_BY_ID[product.evidence_identity_id]
    name=display_name(product)
    lead=(f'Según la documentación oficial de {escape(product.brand)}, {escape(display_name(product,True))} ({escape(product.mpn)}) funciona con {len(batteries)} baterías verificadas en esta base: '
          + ', '.join(escape(b.model_name) for b in batteries) + '. Cada enlace abre la respuesta con el extracto del fabricante y la fecha de comprobación.') if batteries else 'Todavía no hay baterías con compatibilidad documentada vigente para este código.'
    return f'<article style="max-width:860px;margin:auto;padding:2rem 1rem"><nav aria-label="Migas de pan"><a href="/compatibilidad/">Base de compatibilidad</a> / Herramientas</nav><h1>Baterías compatibles con {escape(display_name(product,True))}</h1><p class="compat-direct-answer">{lead}</p><p>Código exacto: <code>{escape(product.mpn)}</code>. Fuente comprobada el {escape(evidence.date_reviewed)} (UTC).</p><h2>Baterías documentadas para {escape(product.model_name)}</h2><ul>{"".join(rows)}</ul>{guide_links(product)}<p><a href="{escape(evidence.official_url)}">Ficha oficial del fabricante</a> · <a href="/compatibilidad/metodologia/">Metodología</a></p>{source_panel(product)}{render_product_commercial(product)}</article>'


COMPATIBILITY_STATIC_PATHS: Tuple[str, ...] = (
    "/compatibilidad/",
    "/compatibilidad/matriz-imprimible/",
    "/compatibilidad/metodologia/",
    "/compatibilidad/cambios/",
) + tuple(f"/plataformas/{p.id}/" for p in PLATFORMS) + tuple(
    f"/baterias/{p.slug}/" for p in CATALOG_PRODUCTS if p.product_type == ProductType.BATERIA.value
) + tuple(
    f"/cargadores/{p.slug}/" for p in CATALOG_PRODUCTS if p.product_type in (ProductType.CARGADOR.value, ProductType.ADAPTADOR.value)
)+ tuple(
    f"/herramientas-bateria/{p.slug}/" for p in CATALOG_PRODUCTS if p.product_type==ProductType.HERRAMIENTA.value
)

COMPATIBILITY_PATHS: Tuple[str, ...] = COMPATIBILITY_STATIC_PATHS
COMPATIBILITY_SEARCH_PATH: str = "/compatibilidad/buscar/"
COMPATIBILITY_DOWNLOAD_PATHS: Tuple[str, ...] = (
    "/datos/compatibilidad/baterias.csv",
    "/datos/compatibilidad/baterias.json",
)


def get_compatibility_dataset_schema_json(site_url: str = "") -> str:
    """Genera marcado Schema.org/Dataset para la base argentina de compatibilidad."""
    base = site_url.rstrip("/") if site_url else ""
    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Base Argentina de Compatibilidad de Baterías, Herramientas y Cargadores",
        "description": "Dataset técnico y verificación documental de relaciones de compatibilidad para herramientas a batería de 18V y 20V comercializadas en Argentina.",
        "url": f"{base}/compatibilidad/",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "version": CURRENT_METADATA["version"],
        "dateModified": CURRENT_METADATA.get("last_checked_at", "")[:10],
        "measurementTechnique": "Comprobación documental de identidad, pertenencia y declaración oficial por modelo",
        "spatialCoverage": {"@type":"Place","name":"Argentina"},
        "isAccessibleForFree": True,
        "citation": sorted({e.official_url for e in EVIDENCES_BY_ID.values()}),
        "variableMeasured": ["Código de fabricante", "Compatibilidad", "Fuente oficial", "Fecha de comprobación"],
        "creator": {
            "@type": "Person",
            "name": "Joaquín Vallasciani",
            "url": f"{base}/autor/joaquin-vallasciani/",
        },
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": f"{base}/datos/compatibilidad/baterias.csv",
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": f"{base}/datos/compatibilidad/baterias.json",
            },
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def _published_brands() -> str:
    brands = sorted({p.brand for p in CATALOG_PRODUCTS if p.status == "publicado"})
    return " y ".join([", ".join(brands[:-1]), brands[-1]]) if len(brands) > 1 else (brands[0] if brands else "")


def _names(items, limit=3) -> str:
    names = [f"{p.model_name}" for p, _ in items[:limit]]
    extra = len(items) - limit
    return ", ".join(names) + (f" y {extra} más" if extra > 0 else "")


def get_compatibility_meta(path: str, site_url: str = "") -> Tuple[str, str, str]:
    """Retorna (título, descripción, schema_extra) para cada ruta de compatibilidad."""
    base = site_url.rstrip("/") if site_url else ""
    if path == "/compatibilidad/":
        return (
            f"Qué batería sirve con tu herramienta: compatibilidad {_published_brands()}",
            f"Consultá por código exacto qué batería y cargador sirven con cada herramienta. {sum(p.status == 'publicado' for p in CATALOG_PRODUCTS)} modelos y {len(RELATIONS)} combinaciones verificadas con fuentes oficiales de {_published_brands()} en Argentina.",
            get_compatibility_dataset_schema_json(base),
        )
    if path == "/compatibilidad/matriz-imprimible/":
        return (
            "Matriz imprimible de compatibilidad de baterías",
            f"Tabla para imprimir con las {len(RELATIONS)} combinaciones de baterías, cargadores y herramientas {_published_brands()} verificadas con documentación oficial.",
            "",
        )
    if path == "/compatibilidad/metodologia/":
        return (
            "Metodología de compatibilidad y canal de correcciones",
            "Criterios de validación documental, escala de 5 veredictos, proceso de mantenimiento y canal de reporte de discrepancias.",
            get_compatibility_dataset_schema_json(base),
        )
    if path == "/compatibilidad/buscar/":
        return (
            "Consulta de compatibilidad de baterías",
            "Resultados de compatibilidad técnica por modelo o código exacto para el catálogo argentino.",
            "",
        )
    if path.startswith("/plataformas/") and path.endswith("/"):
        plat_id = path[len("/plataformas/"):-1]
        plat = PLATFORMS_BY_ID.get(plat_id)
        if plat:
            coll_schema = {
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": f"{plat.name} · Registros y cobertura documental",
                "description": f"Herramientas, baterías y cargadores documentados de {plat.name} en Argentina.",
                "url": f"{base}{path}",
            }
            schema_tag = '<script type="application/ld+json">' + json.dumps(coll_schema, ensure_ascii=False).replace("<", "\\u003c") + "</script>"
            return (
                f"{plat.name} · Compatibilidad en Argentina",
                f"Reglas de compatibilidad, baterías, cargadores y herramientas verificadas para {plat.name} en Argentina.",
                schema_tag,
            )
    if path.startswith("/baterias/") and path.endswith("/"):
        slug = path[len("/baterias/"):-1]
        prod = PRODUCTS_BY_SLUG.get(slug)
        if prod:
            items = compatible_counterparts(prod)
            tools = [x for x in items if x[0].product_type == ProductType.HERRAMIENTA.value]
            chargers = [x for x in items if x[0].product_type != ProductType.HERRAMIENTA.value]
            desc = (f"La batería {prod.brand} {prod.model_name} ({prod.mpn}) tiene {len(tools)} herramientas y {len(chargers)} cargadores con compatibilidad documentada"
                    + (f": {_names(tools or chargers)}" if items else "") + ". Fuente oficial y fecha de verificación.") if prod.status == "publicado" else f"Registro pendiente de verificación: {prod.brand} {prod.model_name}."
            return (
                f"{prod.brand} {prod.model_name} ({prod.mpn}): herramientas y cargadores compatibles" if prod.mpn.lower() not in prod.model_name.lower() else f"Batería {prod.brand} {prod.model_name}: herramientas y cargadores compatibles",
                desc,
                get_product_schema_json(prod, base),
            )
    if path.startswith("/cargadores/") and path.endswith("/"):
        slug = path[len("/cargadores/"):-1]
        prod = PRODUCTS_BY_SLUG.get(slug)
        if prod:
            items = compatible_counterparts(prod)
            desc = (f"{display_name(prod, True)[0].upper()}{display_name(prod, True)[1:]} ({prod.mpn}) carga {len(items)} baterías con compatibilidad documentada"
                    + (f": {_names(items)}" if items else "") + ". Fuente oficial, condiciones y fecha de verificación.") if prod.status == "publicado" else f"Registro pendiente de verificación: {prod.brand} {prod.model_name}."
            code = f" ({prod.mpn})" if prod.mpn.lower() not in prod.model_name.lower() else ""
            return (
                f"{prod.brand} {prod.model_name}{code}: qué baterías carga",
                desc,
                get_product_schema_json(prod, base),
            )
    if path.startswith('/herramientas-bateria/'):
        prod=PRODUCTS_BY_SLUG.get(path.rstrip('/').split('/')[-1])
        if prod:
            items = [x for x in compatible_counterparts(prod) if x[0].product_type == ProductType.BATERIA.value]
            code = f" ({prod.mpn})" if prod.mpn.lower() not in prod.model_name.lower() else ""
            desc = (f"Baterías que sirven con {display_name(prod, True)}{code}: {_names(items)}. Compatibilidad verificada en la documentación oficial de {prod.brand}, con fuente y fecha."
                    if prod.status == "publicado" and items else f"Registro pendiente de verificación: {prod.brand} {prod.model_name}.")
            return (f"Baterías compatibles con {prod.brand} {prod.model_name}{code}", desc, get_product_schema_json(prod, base))
    if path.startswith("/compatibilidad/") and "-con-" in path:
        resolved=resolve_relationship(path)
        if resolved:
            a,b,evaluation=resolved
            title, desc = relation_meta(a, b, evaluation)
            return (title, desc, '<meta name="robots" content="noindex, follow">' if not evaluation.is_compatible else relation_schema(a, b, evaluation, path, base))
    if path=="/compatibilidad/cambios/":
        return ("Historial de cambios y fuentes de compatibilidad", "Publicaciones y revisiones documentales de TallerLab por versión y fecha.", "")
    return ("Compatibilidad de herramientas", "Base de datos técnica de compatibilidad de herramientas en Argentina.", "")


@catalog_read_locked
def render_compatibility_page_content(path: str, query_params: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Retorna el contenido HTML del cuerpo para cualquier ruta de compatibilidad."""
    if path == "/compatibilidad/":
        return render_compatibility_hub_html()
    if path == "/compatibilidad/matriz-imprimible/":
        return render_printable_matrix_html()
    if path == "/compatibilidad/cambios/":
        return render_compatibility_changes_html()
    if path == "/compatibilidad/metodologia/":
        return render_compatibility_methodology_html()
    if path == "/compatibilidad/buscar/":
        qp = query_params or {}
        q = qp.get("q", "")
        a = qp.get("a", "")
        b = qp.get("b", "")
        return render_compatibility_search_results_html(query=q, model_a=a, model_b=b)
    if path.startswith("/plataformas/") and path.endswith("/"):
        plat_id = path[len("/plataformas/"):-1]
        content = render_platform_page_html(plat_id)
        return content if content else None
    if path.startswith("/baterias/") and path.endswith("/"):
        slug = path[len("/baterias/"):-1]
        content = render_battery_detail_page_html(slug)
        return content if content else None
    if path.startswith("/cargadores/") and path.endswith("/"):
        slug = path[len("/cargadores/"):-1]
        content = render_charger_detail_page_html(slug)
        return content if content else None
    if path.startswith('/herramientas-bateria/'):
        product=PRODUCTS_BY_SLUG.get(path.rstrip('/').split('/')[-1])
        return render_tool_detail(product) if product and product.product_type=='herramienta' else None
    if path.startswith("/compatibilidad/") and "-con-" in path:
        return relationship_page(path)
    return None

