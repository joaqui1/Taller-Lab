"""Vistas y componentes HTML para la publicación del Observatorio en TallerLab."""

import json
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List, Optional

from observatorio.analytics import (
    format_art_date,
    get_experimental_tool_basket_index,
    get_product_current_stats,
    get_product_price_history_series,
)
from observatorio.catalog import CATALOG_PRODUCTS, PRODUCTS_BY_ID
from observatorio.config import DATA_VERSION, METHODOLOGY_VERSION, SITE_URL
from observatorio.sources import SOURCES_REGISTRY
from observatorio.charts import render_history_chart
from observatorio.config import TZ_BUENOS_AIRES


def render_observatory_hub_html() -> str:
    """Renderiza el cuerpo principal del Hub del Observatorio de Precios."""
    basket_data = get_experimental_tool_basket_index()

    # Resumen de cobertura por categoría
    categories = [
        {
            "id": "compresores",
            "name": "Compresores de Aire",
            "icon": "💨",
            "url": "/datos/precios/compresores/",
            "desc": "Monitoreo de tanques de 24L, 50L, 100L, bicilíndricos y modelos silenciosos sin aceite.",
            "models_count": len([p for p in CATALOG_PRODUCTS if p.category == "compresores"]),
        },
        {
            "id": "hidrolavadoras",
            "name": "Hidrolavadoras",
            "icon": "💧",
            "url": "/datos/precios/hidrolavadoras/",
            "desc": "Seguimiento de equipos de 100 a 150 bar, modelos residenciales y comerciales.",
            "models_count": len([p for p in CATALOG_PRODUCTS if p.category == "hidrolavadoras"]),
        },
    ]

    cat_cards = "".join(f"""
        <div class="category-card" style="border: 1px solid #334155; border-radius: 8px; padding: 1.5rem; background: #0f172a; margin-bottom: 1rem;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">{c['icon']}</div>
          <h3 style="margin-top: 0; color: #f8fafc;"><a href="{c['url']}" style="color: #ff5500; text-decoration: none;">{escape(c['name'])}</a></h3>
          <p style="color: #94a3b8; font-size: 0.95rem;">{escape(c['desc'])}</p>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; border-top: 1px solid #1e293b; pt: 0.75rem;">
            <span style="font-size: 0.85rem; color: #64748b;"><strong>{c['models_count']}</strong> modelos en catálogo</span>
            <a href="{c['url']}" class="btn-orange" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;">Ver datos y series →</a>
          </div>
        </div>
    """ for c in categories)

    # Indicador de canasta experimental
    basket_html = ""
    if basket_data.get("has_minimum_coverage") and basket_data.get("basket_value_ars"):
        basket_html = f"""
        <div style="background: #1e1b4b; border: 1px solid #4338ca; border-radius: 8px; padding: 1.5rem; margin: 2rem 0;">
          <span style="background: #312e81; color: #a5b4fc; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">{basket_data['status']}</span>
          <h3 style="color: #ffffff; margin: 0.5rem 0 0.25rem 0;">{escape(basket_data['label'])}</h3>
          <p style="color: #c7d2fe; font-size: 0.9rem; margin-bottom: 1rem;">{escape(basket_data['methodology'])}</p>
          <div style="font-size: 2.2rem; font-weight: 900; color: #38bdf8;">
            $ {basket_data['basket_value_ars']:,.2f} <span style="font-size: 1rem; font-weight: normal; color: #94a3b8;">ARS</span>
          </div>
          <p style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem; font-style: italic;">{escape(basket_data['disclaimer'])}</p>
        </div>
        """
    else:
        basket_html = f"""
        <div style="background: #1e293b; border: 1px dashed #475569; border-radius: 8px; padding: 1.25rem; margin: 2rem 0;">
          <h4 style="color: #e2e8f0; margin-top: 0;">Canasta fija de herramientas de taller (En formación)</h4>
          <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            El cálculo requiere precios vigentes de los 5 modelos de referencia.
            Actualmente se dispone de {basket_data.get('coverage_pct', 0):.0f}% de observaciones coincidentes.
          </p>
        </div>
        """

    content = f"""
    <div class="article-container" style="max-width: 900px; margin: 0 auto; padding: 2rem 1rem;">
      <div class="breadcrumb">
        <a href="/">Inicio</a> <span>/</span> <span>Observatorio de Precios</span>
      </div>

      <header style="margin-bottom: 2.5rem;">
        <span class="section-kicker" style="color: #ff5500; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em;">TALLERLAB / DATOS ABIERTOS</span>
        <h1 style="font-size: 2.4rem; font-weight: 900; color: #f8fafc; margin: 0.5rem 0 1rem 0;">Observatorio de Precios de Herramientas en Argentina</h1>
        <p style="font-size: 1.15rem; color: #94a3b8; line-height: 1.6;">
          Relevamiento diario de precios de pago único con impuestos, disponibilidad declarada y condiciones comerciales 
          en fuentes evaluadas, con controles automáticos de identidad, moneda y disponibilidad.
          El piloto permanece en preparación hasta verificar las primeras fuentes y ofertas reales.
        </p>
      </header>

      <div class="observatory-notice" style="background: #0f172a; border-left: 4px solid #ff5500; padding: 1rem 1.25rem; margin-bottom: 2rem; border-radius: 0 6px 6px 0;">
        <strong style="color: #f8fafc;">Marco de transparencia:</strong>
        <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.25rem 0 0.5rem 0;">
          El observatorio publica exclusivamente precios de ofertas válidas correspondientes a modelos exactos identificados por código de fabricante (MPN). 
          No se incluyen publicaciones genéricas, productos agotados en los mínimos de compra ni fuentes restringidas sin autorización expresa.
        </p>
        <a href="/datos/precios/metodologia/" style="color: #ff5500; font-size: 0.85rem; font-weight: 600;">Consultar metodología completa, fuentes y derechos →</a>
      </div>

      {basket_html}

      <section style="margin: 3rem 0;">
        <h2 style="color: #f8fafc; font-size: 1.6rem; margin-bottom: 1.5rem;">Categorías monitoreadas</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;">
          {cat_cards}
        </div>
      </section>

      <section style="background: #09111e; border: 1px solid #1e293b; border-radius: 8px; padding: 1.5rem; margin-top: 3rem;">
        <h3 style="color: #f8fafc; margin-top: 0;">Descarga y reutilización de datos</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
          Los datasets históricos están disponibles en formato CSV normalizado (UTF-8 con protección de fórmulas) 
          para análisis independiente, investigación y control ciudadano.
        </p>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem;">
          <a href="/datos/precios/compresores/descargar-csv" class="btn-orange" style="font-size: 0.85rem;">Descargar CSV Compresores ↓</a>
          <a href="/datos/precios/hidrolavadoras/descargar-csv" class="btn-orange" style="font-size: 0.85rem;">Descargar CSV Hidrolavadoras ↓</a>
        </div>
      </section>
    </div>
    """
    return content


def render_observatory_category_html(category: str) -> str:
    """Renderiza la tabla de precios, series y estadísticas de una categoría específica."""
    cat_names = {
        "compresores": "Compresores de Aire",
        "hidrolavadoras": "Hidrolavadoras",
        "generadores": "Generadores",
    }
    category_name = cat_names.get(category, category.title())
    category_products = [p for p in CATALOG_PRODUCTS if p.category == category]

    table_rows = []
    model_details = []
    has_any_fresh_data = False
    updated_today = False
    now_utc = datetime.now(timezone.utc)
    active_with_data_count = 0

    for prod in category_products:
        stats = get_product_current_stats(prod.id)
        if stats["is_fresh"]:
            has_any_fresh_data = True
            active_with_data_count += 1
            for obs in stats.get("current_offers", []):
                try:
                    obs_dt = datetime.fromisoformat(obs["observed_at"])
                    if obs_dt.tzinfo is None:
                        obs_dt = obs_dt.replace(tzinfo=timezone.utc)
                    elapsed_hours = (now_utc - obs_dt).total_seconds() / 3600.0
                    if 0 <= elapsed_hours <= 24.0 and obs_dt.astimezone(TZ_BUENOS_AIRES).date() == now_utc.astimezone(TZ_BUENOS_AIRES).date():
                        updated_today = True
                except Exception:
                    pass

        min_price_str = f"$ {stats['min_current_price']:,.2f}" if stats["min_current_price"] else '<span style="color:#64748b;">Sin stock / sin datos</span>'
        median_price_str = f"$ {stats['median_current_price']:,.2f}" if stats["median_current_price"] else "-"
        hist_min_str = f"$ {stats['historical_min_price']:,.2f}" if stats["historical_min_price"] else "-"
        obs_date_str = stats["last_observed_at_display"] or "Sin registro reciente"

        offers_count_badge = f'<span style="background:#1e293b; color:#94a3b8; padding:0.15rem 0.4rem; border-radius:4px; font-size:0.75rem;">{stats["active_offers_count"]} ofertas</span>'

        guide_link = f'<a href="{prod.guide_url}" style="color:#ff5500; text-decoration:none; font-size:0.85rem;">Guía técnica →</a>' if prod.guide_url else ""

        table_rows.append(f"""
        <tr>
          <td>
            <strong>{escape(prod.brand)} {escape(prod.model_name)}</strong><br>
            <span style="font-size: 0.78rem; color: #64748b;">MPN: {escape(prod.mpn)}</span>
          </td>
          <td style="color: #38bdf8; font-weight: 700;">{min_price_str}</td>
          <td style="color: #cbd5e1;">{median_price_str}</td>
          <td style="color: #94a3b8; font-size: 0.85rem;">{hist_min_str}</td>
          <td>{offers_count_badge}</td>
          <td style="font-size: 0.8rem; color: #64748b;">{obs_date_str}</td>
          <td><a href="#{escape(prod.id,quote=True)}" style="color:#ff5500">Ofertas e historial</a><br>{guide_link}</td>
        </tr>
        """)

        offers_html = ''.join(f'''<tr><td>{escape(o['seller_name'])}</td><td>$ {o['price_single_payment']:,.2f}</td><td>{('$ '+format(o['price_transfer'],',.2f')) if o['price_transfer'] is not None else 'No declarado'}</td><td>{escape(format_art_date(o['observed_at']))}</td><td><a href="{escape(o['direct_url'],quote=True)}" target="_blank" rel="noopener noreferrer">Ver oferta ↗</a></td></tr>''' for o in stats['current_offers'])
        comparison = f'''<div class="table-scroll"><table><thead><tr><th>Vendedor</th><th>Pago único ARS</th><th>Transferencia ARS</th><th>Captura</th><th>Fuente</th></tr></thead><tbody>{offers_html}</tbody></table></div>''' if offers_html else '<p class="obs-empty">Sin ofertas vigentes con stock verificado.</p>'
        chart = render_history_chart(get_product_price_history_series(prod.id),prod.brand+' '+prod.model_name)
        model_details.append(f'''<details class="obs-model" id="{escape(prod.id,quote=True)}"><summary>{escape(prod.brand)} {escape(prod.model_name)} · ofertas e historial</summary><p class="obs-variant">{escape(prod.voltage)} · {escape(prod.kit_content)} · condición: {escape(prod.item_condition)}</p>{comparison}{chart}</details>''')
    table_html = "".join(table_rows)

    if updated_today:
        fresh_status_badge = '<span style="background: #064e3b; color: #6ee7b7; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">ACTUALIZADO HOY</span>'
    elif has_any_fresh_data:
        fresh_status_badge = '<span style="background: #1e3a8a; color: #93c5fd; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">OBSERVACIÓN VIGENTE (48 HS)</span>'
    else:
        fresh_status_badge = '<span style="background: #3f3f46; color: #d4d4d8; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">EN ESPERA DE RECOLECCIÓN</span>'

    content = f"""
    <div class="article-container" style="max-width: 1000px; margin: 0 auto; padding: 2rem 1rem;">
      <style>.obs-model{{border:1px solid #334155;border-radius:8px;padding:1.1rem;margin:1rem 0;background:#0f172a;color:#e2e8f0;scroll-margin-top:90px}}.obs-model summary{{cursor:pointer;font-weight:700;color:#f8fafc}}.obs-model table{{width:100%;border-collapse:collapse;font-size:.85rem}}.obs-model td,.obs-model th{{padding:.7rem;border-bottom:1px solid #334155;text-align:left}}.obs-model a{{color:#fb923c}}.obs-variant,.obs-empty,.obs-chart figcaption{{font-size:.85rem;color:#94a3b8}}.obs-chart{{margin:1.5rem 0}}.obs-chart svg{{width:100%;height:auto}}.obs-legend{{display:flex;flex-wrap:wrap;gap:1rem}}.obs-legend i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:.4rem}}</style>
      <div class="breadcrumb">
        <a href="/">Inicio</a> <span>/</span> <a href="/datos/precios-herramientas-argentina/">Observatorio</a> <span>/</span> <span>{escape(category_name)}</span>
      </div>

      <header style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
          <span class="section-kicker" style="color: #ff5500; font-weight: 700; font-size: 0.85rem;">OBSERVATORIO DE PRECIOS</span>
          {fresh_status_badge}
        </div>
        <h1 style="font-size: 2.2rem; font-weight: 900; color: #f8fafc; margin: 0.25rem 0 0.75rem 0;">Precios de {escape(category_name)} en Argentina</h1>
        <p style="font-size: 1.05rem; color: #94a3b8; line-height: 1.5;">
          Monitoreo estructurado de {len(category_products)} modelos exactos. Valores de pago único final en pesos con IVA incluido. 
          Mínimos vigentes relevados exclusivamente sobre unidades con disponibilidad acreditada en las últimas 48 horas.
        </p>
      </header>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
        <div style="font-size: 0.85rem; color: #64748b;">
          Mostrando <strong>{len(category_products)}</strong> modelos en catálogo ({active_with_data_count} con datos vigentes)
        </div>
        <div>
          <a href="/datos/precios/{category}/descargar-csv" class="btn-orange" style="font-size: 0.85rem; padding: 0.4rem 0.8rem;">Descargar dataset CSV ↓</a>
        </div>
      </div>

      <div class="table-scroll" style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; overflow-x: auto; margin-bottom: 2.5rem;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
          <thead>
            <tr style="border-bottom: 2px solid #334155; background: #1e293b;">
              <th scope="col" style="padding: 0.85rem;">Herramienta y Modelo</th>
              <th scope="col" style="padding: 0.85rem;">Mínimo Vigente</th>
              <th scope="col" style="padding: 0.85rem;">Mediana Vigente</th>
              <th scope="col" style="padding: 0.85rem;">Mínimo Histórico</th>
              <th scope="col" style="padding: 0.85rem;">Ofertas</th>
              <th scope="col" style="padding: 0.85rem;">Última Observación</th>
              <th scope="col" style="padding: 0.85rem;">Detalle</th>
            </tr>
          </thead>
          <tbody>
            {table_html}
          </tbody>
        </table>
      </div>

      <section aria-label="Ofertas e historiales por modelo">{''.join(model_details)}</section>
      <section style="background: #0b1320; border: 1px solid #1e293b; border-radius: 8px; padding: 1.5rem; margin-top: 2rem;">
        <h3 style="color: #f8fafc; margin-top: 0;">Límites de los datos</h3>
        <ul style="color: #94a3b8; font-size: 0.9rem; line-height: 1.6; padding-left: 1.25rem;">
          <li>El "mínimo vigente" representa el menor precio observado entre las tiendas independientes relevadas; no afirma ser el precio más bajo de todo el territorio nacional.</li>
          <li>Los productos agotados se registran para preservar el historial, pero quedan excluidos del cálculo de mínimos activos.</li>
          <li>Los descuentos por transferencia se detallan en las fichas específicas de cada oferta cuando están explícitos, pero la comparación principal utiliza el precio de pago único universal (tarjeta/débito).</li>
        </ul>
        <p style="margin-top: 1rem; font-size: 0.85rem;"><a href="/datos/precios/metodologia/" style="color: #ff5500;">Leer metodología completa y criterios de exclusión →</a></p>
      </section>
    </div>
    """
    return content


def render_observatory_methodology_html() -> str:
    """Metodología pública: solo afirmaciones respaldadas por el funcionamiento actual."""
    sections = [
        ('Qué medimos', 'Precios declarados de ofertas de modelos exactos. La cobertura se limita a las tiendas efectivamente relevadas; no representa todo el mercado argentino. El piloto está en preparación hasta verificar las primeras fuentes.'),
        ('Modelo y variante', 'Se comprueban código de fabricante, tensión, condición y kit cuando están declarados. Las contradicciones se rechazan. Si no podemos identificar la oferta con certeza, no publicamos un precio.'),
        ('Precio y condiciones', 'Comparamos el precio de pago único en ARS. Las cuotas no equivalen al precio total. Transferencia y precio tachado se muestran por separado cuando el vendedor los declara. El envío y el importe final deben comprobarse en la tienda.'),
        ('Fuentes y reutilización', 'Cada fuente requiere evaluación documentada, fecha y permisos de captura y redistribución. Las fuentes pendientes o descartadas no se consultan. Mercado Libre permanece descartada en este piloto. Esta metodología no concede derechos de terceros.'),
        ('Vigencia y anomalías', 'Los mínimos utilizan el último estado verificable de cada oferta, con hasta 48 horas de antigüedad. Un agotamiento, una anomalía o un fallo posterior retiran el valor anterior del mínimo vigente. Saltos del 35% o más respecto al historial reciente quedan retenidos.'),
        ('Históricos y gráficos', 'Mostramos el último precio publicable de cada día argentino por vendedor, hasta 365 días. Los días sin capturas interrumpen las líneas; no interpolamos precios. Las muestras y los registros retenidos están excluidos del CSV y los históricos públicos.'),
        ('Descuentos e indicadores', 'La comparación de descuentos necesita al menos tres días previos distintos del mismo vendedor, fuera del período del precio actual. Sin cobertura no emitimos una conclusión. La canasta de cinco modelos es una suma de costos con cobertura completa, no un índice de inflación.'),
        ('Correcciones', 'Conservamos evidencia limitada y un hash de cada captura. El hash acredita integridad, no veracidad comercial. Las incidencias se registran por separado; resolver una incidencia no aprueba automáticamente un precio. Las discrepancias pueden reportarse por el canal de contacto del sitio.'),
    ]
    body = ''.join(f'<section style="margin:2rem 0"><h2>{escape(title)}</h2><p>{escape(text)}</p></section>' for title,text in sections)
    return f'<div class="article-container" style="max-width:850px;margin:auto;padding:2rem 1rem"><h1>Metodología del Observatorio</h1><p>Versión {METHODOLOGY_VERSION} · datos {DATA_VERSION}</p>{body}<p><a href="/contacto/">Reportar una corrección</a></p></div>'

def render_model_price_widget(product_id: str) -> str:
    """Genera un bloque embebible para incorporar en las guías técnicas existentes de modelos."""
    try:
        stats = get_product_current_stats(product_id)
        if not stats.get("is_fresh") or not stats.get("min_current_price"):
            return ""

        min_p = stats["min_current_price"]
        active_count = stats["active_offers_count"]
        obs_date = stats.get("last_observed_at_display") or ""
        prod = PRODUCTS_BY_ID.get(product_id)
        prod_title = f"{prod.brand} {prod.model_name}" if prod else ""
        cat_url = f"/datos/precios/{prod.category}/" if prod else "/datos/precios-herramientas-argentina/"

        return f"""
        <div class="observatory-price-box" style="background: #0f172a; border: 1px solid #ff5500; border-radius: 8px; padding: 1.25rem; margin: 2rem 0;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <span style="color: #ff5500; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">OBSERVATORIO TALLERLAB{f' — {escape(prod_title)}' if prod_title else ''}</span>
            <span style="color: #64748b; font-size: 0.75rem;">Última captura: {escape(obs_date)}</span>
          </div>
          <div style="display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap;">
            <div style="font-size: 1.8rem; font-weight: 900; color: #f8fafc;">
              $ {min_p:,.2f} <span style="font-size: 0.9rem; font-weight: normal; color: #94a3b8;">ARS</span>
            </div>
            <span style="color: #10b981; font-size: 0.85rem; font-weight: 600;">Menor precio vigente con stock</span>
          </div>
          <p style="color: #94a3b8; font-size: 0.85rem; margin: 0.5rem 0 0.75rem 0;">
            Precio de pago único declarado por el vendedor entre {active_count} ofertas vigentes. Consultar envío y condiciones en origen.
          </p>
          <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #1e293b; pt: 0.5rem;">
            <a href="{cat_url}" style="color: #ff5500; font-size: 0.85rem; font-weight: 600; text-decoration: none;">Ver comparativa y series de precios →</a>
            <a href="/datos/precios/metodologia/" style="color: #64748b; font-size: 0.78rem; text-decoration: none;">Metodología</a>
          </div>
        </div>
        """
    except Exception:
        return ""


def get_dataset_schema_json(category: str) -> str:
    """Genera marcado Schema.org/Dataset para las páginas de catálogo del observatorio."""
    from observatorio.db import query_one
    from observatorio.publication import PUBLIC_OBSERVATION_SQL
    try:
        dates=query_one(f'''SELECT MIN(o.observed_at) AS first_date, MAX(o.observed_at) AS last_date
            FROM observations o JOIN offers off ON off.id=o.offer_id JOIN sources src ON src.id=off.source_id
            JOIN catalog_products cp ON cp.id=o.product_id WHERE cp.category=? AND {PUBLIC_OBSERVATION_SQL}''',(category,))
        if not dates or not dates['last_date']: return ''
    except Exception:
        return ''
    cat_names = {
        "compresores": "Compresores de Aire",
        "hidrolavadoras": "Hidrolavadoras",
        "generadores": "Generadores",
    }
    cat_name = cat_names.get(category, category.title())
    dataset_url = f"{SITE_URL}/datos/precios/{category}/"
    csv_url = f"{SITE_URL}/datos/precios/{category}/descargar-csv"

    schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"Precios Observados de {cat_name} en Argentina",
        "description": f"Historial y precios diarios de pago único con impuestos para {cat_name} en Argentina, relevados por el Observatorio de TallerLab.",
        "url": dataset_url,
        "version": DATA_VERSION,
        "dateModified": dates['last_date'],
        "temporalCoverage": dates['first_date']+'/'+dates['last_date'],
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": csv_url,
            }
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + "</script>"

