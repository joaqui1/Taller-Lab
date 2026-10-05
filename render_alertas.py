"""
Generador de vistas HTML para la sección de 'Documentación y alertas de herramientas'.
Reutiliza la estética industrial oscura de TallerLab, sus tipografías y su paleta de colores.
"""

from __future__ import annotations

import json
from html import escape
from typing import Any, Dict, List, Optional

from alertas_datos import (
    DESCARGO_CAMPANA_EXTRANJERA,
    DESCARGO_INDEPENDENCIA,
    DESCARGO_NO_GARANTIA_SEGURIDAD,
    ESTADOS_ALERTA,
    cargar_expedientes,
    expediente_publico,
    obtener_expediente,
)
from alertas_seo import (
    RESUMEN_CSS,
    dossier_schema as _dossier_schema_seo,
    fecha_legible,
    render_registro_hub,
    render_resumen,
)

ALERTAS_CSS = """
<style>
/* Estilos especializados para Documentación y Alertas de Herramientas */
.alertas-hub,.dossier-detail {
  --bg-card:#161f29; --border:#34404d;
  background:#0d141b; color:#cbd5e1; border-radius:14px;
}
.alertas-hub a,.dossier-detail a {color:#fbbf24;}
.alertas-hub .breadcrumb,.dossier-detail .breadcrumb {color:#94a3b8;}
.alertas-hub :focus-visible,.dossier-detail :focus-visible {outline:3px solid #fbbf24;outline-offset:3px;}
.alertas-hub {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3.5rem;
}
.alertas-hero {
  background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(13, 17, 23, 0.98) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2.25rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.alertas-hero::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #ff5500, #f59e0b, #ef4444);
}
.alertas-hero h1 {
  font-size: 2.2rem;
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}
.alertas-hero p.lead {
  color: #94a3b8;
  font-size: 1.08rem;
  line-height: 1.6;
  max-width: 850px;
  margin-bottom: 1.25rem;
}
.alertas-disclaimer-box {
  background: rgba(15, 23, 42, 0.7);
  border-left: 3px solid #ff5500;
  padding: 0.85rem 1.15rem;
  border-radius: 0 8px 8px 0;
  font-size: 0.85rem;
  color: #cbd5e1;
  line-height: 1.5;
}

/* Buscador y Filtros */
.alertas-controls {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}
.alertas-search-input-wrap {
  position: relative;
  margin-bottom: 1.25rem;
}
.alertas-search-input {
  width: 100%;
  padding: 0.85rem 1rem 0.85rem 2.85rem;
  background: #0d1117;
  border: 1px solid var(--border);
  border-radius: 10px;
  color: #ffffff;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.alertas-search-input:focus {
  outline: none;
  border-color: #ff5500;
  box-shadow: 0 0 0 3px rgba(255, 85, 0, 0.2);
}
.alertas-search-icon {
  position: absolute;
  left: 0.95rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
}
.alertas-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
}
.alertas-filter-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #94a3b8;
  margin-right: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.alertas-chip {
  background: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.4rem 0.85rem;
  border-radius: 20px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}
.alertas-chip:hover {
  border-color: #ff5500;
  color: #ffffff;
}
.alertas-chip.active {
  background: #ff5500;
  border-color: #ff5500;
  color: #ffffff;
  font-weight: 700;
}

/* Grilla de Expedientes */
.alertas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}
.dossier-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}
.dossier-card:hover {
  transform: translateY(-3px);
  border-color: rgba(255, 85, 0, 0.45);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.5), 0 0 15px rgba(255, 85, 0, 0.12);
}
.dossier-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}
.dossier-brand-tag {
  font-size: 0.75rem;
  font-weight: 800;
  color: #ff5500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.dossier-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.7rem;
  border-radius: 14px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.dossier-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.25rem 0 0.5rem;
  line-height: 1.3;
}
.dossier-desc {
  font-size: 0.88rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 1.15rem;
  flex: 1;
}
.dossier-variants-summary {
  background: #0d1117;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  font-size: 0.78rem;
  color: #cbd5e1;
  margin-bottom: 1.15rem;
}
.dossier-variants-summary strong {
  color: #f1f5f9;
}
.dossier-card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.85rem;
  font-size: 0.84rem;
}
.dossier-card-link {
  color: #ff5500;
  font-weight: 700;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.dossier-card-link:hover {
  text-decoration: underline;
}

/* Ficha / Expediente Técnico Individual */
.dossier-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
}
.dossier-header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 1.75rem;
  margin-bottom: 2rem;
}
.dossier-header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
.dossier-header h1 {
  font-size: 2.4rem;
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}
.dossier-subtitle {
  color: #94a3b8;
  font-size: 1.12rem;
  line-height: 1.5;
  margin-bottom: 1.25rem;
}
.dossier-status-banner {
  border-radius: 12px;
  padding: 1.15rem 1.35rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.dossier-status-banner-icon {
  font-size: 1.6rem;
  line-height: 1;
}
.dossier-status-banner-content h3 {
  font-size: 1.05rem;
  font-weight: 800;
  margin: 0 0 0.25rem;
}
.dossier-status-banner-content p {
  font-size: 0.88rem;
  margin: 0;
  line-height: 1.45;
}
.dossier-meta-bar {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.82rem;
  color: #64748b;
  padding-top: 0.75rem;
  border-top: 1px dashed #21262d;
}

/* Secciones de Contenido */
.dossier-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.75rem;
  margin-bottom: 2rem;
}
.dossier-section h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
  margin-top: 0;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.dossier-section-desc {
  font-size: 0.88rem;
  color: #94a3b8;
  margin-bottom: 1.25rem;
  line-height: 1.5;
}

/* Tablas técnicas */
.dossier-table-wrap {
  overflow-x: auto;
  margin-bottom: 1rem;
}
.dossier-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
  text-align: left;
}
.dossier-table th {
  background: #111722;
  color: #f1f5f9;
  font-weight: 700;
  padding: 0.75rem 0.9rem;
  border-bottom: 2px solid #21262d;
  white-space: nowrap;
}
.dossier-table td {
  padding: 0.75rem 0.9rem;
  border-bottom: 1px solid #21262d;
  color: #cbd5e1;
  vertical-align: top;
}
.dossier-table tr:hover td {
  background: rgba(255, 85, 0, 0.03);
}

/* Tarjetas de Alerta */
.alert-card {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 1.35rem;
  margin-bottom: 1.35rem;
}
.alert-card.alerta-confirmada {
  border-left: 4px solid #ef4444;
}
.alert-card.alerta-posible {
  border-left: 4px solid #f59e0b;
}
.alert-card.alerta-neutral {
  border-left: 4px solid #475569;
}
.alert-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.85rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid #21262d;
}
.alert-card-agency {
  font-weight: 800;
  font-size: 0.95rem;
  color: #ffffff;
}
.alert-card-market {
  font-size: 0.78rem;
  background: #1f2937;
  color: #93c5fd;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}
.alert-exclusion-box {
  background: rgba(185, 28, 28, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  margin: 0.85rem 0;
  font-size: 0.86rem;
  color: #fca5a5;
  line-height: 1.5;
}
.alert-field {
  margin-bottom: 0.65rem;
  font-size: 0.86rem;
  line-height: 1.5;
}
.alert-field strong {
  color: #f1f5f9;
  display: inline-block;
  min-width: 140px;
}
.alert-card-footer {
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #21262d;
  font-size: 0.82rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Enlaces y botones */
.btn-doc {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #1e293b;
  border: 1px solid #334155;
  color: #ffffff;
  padding: 0.45rem 0.95rem;
  border-radius: 6px;
  font-size: 0.84rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}
.btn-doc:hover {
  background: #ff5500;
  border-color: #ff5500;
  color: #ffffff;
}
</style>
"""


def _render_status_badge(estado_key: str) -> str:
    """Genera la píldora visual de estado con diseño técnico sobrio."""
    info = ESTADOS_ALERTA.get(estado_key, ESTADOS_ALERTA["NO_REVISADO"])
    return f"""<span class="dossier-status-pill" style="background: {info['bg']}; color: {info['color']};">
      <span aria-hidden="true">{info['icono']}</span>
      <span>{escape(info['etiqueta'])}</span>
    </span>"""


def render_alerts_hub_page() -> str:
    """Genera la página principal (/alertas/) con buscador, filtros y tarjetas de expedientes."""
    expedientes = cargar_expedientes(forzar_recarga=True)

    cards_html = []
    marcas_set = set()

    for exp in expedientes:
        marcas_set.add(exp["marca"])
        status_info = ESTADOS_ALERTA.get(exp["estado_general"], ESTADOS_ALERTA["NO_REVISADO"])
        variantes_str = " · ".join(v["codigo"] for v in exp.get("variantes", [])[:3])
        if len(exp.get("variantes", [])) > 3:
            variantes_str += " y más"

        alertas_cnt = len(exp.get("alertas", []))
        alertas_label = (f"{alertas_cnt} alerta analizada" if alertas_cnt == 1 else f"{alertas_cnt} alertas analizadas") if alertas_cnt else "Sin alertas registradas"

        # Corpus de búsqueda unificado: marca, modelo base, nombre comercial, categoría, códigos de variante, EANs y tipos
        tokens_search = [
            exp["marca"],
            exp["modelo_base"],
            exp.get("nombre_comercial", ""),
            exp.get("categoria", ""),
        ]
        for v in exp.get("variantes", []):
            tokens_search.append(v.get("codigo", ""))
            if v.get("codigo_barras"):
                tokens_search.append(v["codigo_barras"])
            if v.get("tipo_revision"):
                tokens_search.append(v["tipo_revision"])
        search_corpus = " ".join(t for t in tokens_search if t).lower()

        card = f"""
        <article class="dossier-card" data-marca="{escape(exp['marca'].lower())}" data-estado="{escape(exp['estado_general'])}" data-search="{escape(search_corpus)}">
          <div class="dossier-card-top">
            <span class="dossier-brand-tag">{escape(exp['marca'])} · {escape(exp['categoria'].capitalize())}</span>
            {_render_status_badge(exp['estado_general'])}
          </div>
          <h2 class="dossier-title">{escape(exp['marca'])} {escape(exp['modelo_base'])}</h2>
          <p class="dossier-desc">{escape(exp['nombre_comercial'])}</p>
          <div class="dossier-variants-summary">
            <strong>Variantes identificadas:</strong> {escape(variantes_str)}
          </div>
          <div class="dossier-card-actions">
            <span style="font-size: 0.78rem; color: #64748b;">{alertas_label}</span>
            <a href="/alertas/{exp['slug']}/" class="dossier-card-link">Ver expediente técnico →</a>
          </div>
        </article>
        """
        cards_html.append(card)

    marcas_chips = "".join(
        f'<button type="button" class="alertas-chip" data-filter-marca="{escape(m.lower())}" aria-pressed="false">{escape(m)}</button>'
        for m in sorted(marcas_set)
    )

    registro_html = render_registro_hub(expedientes)

    content = f"""
    {ALERTAS_CSS}{RESUMEN_CSS}
    <div class="alertas-hub">
      <nav class="breadcrumb" aria-label="Migas de pan">
        <a href="/">Inicio</a>
        <span aria-hidden="true">/</span>
        <span aria-current="page">Documentación y alertas</span>
      </nav>

      <section class="alertas-hero">
        <span class="dossier-brand-tag" style="margin-bottom: 0.5rem; display: inline-block;">SERVICIO DE INVESTIGACIÓN DOCUMENTAL</span>
        <h1>Alertas de seguridad, recalls y documentación de herramientas</h1>
        <p class="lead">
          Expedientes técnicos por modelo: avisos oficiales de retiro y seguridad (Defensa del Consumidor, SERNAC y CPSC),
          variantes que se venden en Argentina, manuales originales, despieces y soporte oficial, con el alcance
          geográfico y las exclusiones de cada aviso delimitados.
        </p>
        <div class="alertas-disclaimer-box">
          <strong>Aviso de independencia y alcance:</strong> {escape(DESCARGO_INDEPENDENCIA)}
          {escape(DESCARGO_NO_GARANTIA_SEGURIDAD)}
        </div>
        <p class="dossier-section-desc">Publicación con revisión editorial. La recolección diaria de CPSC y Argentina se configura en producción;
          SERNAC tiene seguimiento de las campañas citadas. La fecha de cada ficha corresponde a su revisión documental,
          sin promesa de vigilancia continua ni cobertura exhaustiva.</p>
        <p class="dossier-section-desc">Editor responsable: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a> ·
          <a href="/alertas/estado/">Estado de actualización</a> · <a href="/alertas/metodologia/">Metodología y cobertura</a> ·
          <a href="/datos/alertas/avisos.csv">Datos CSV</a></p>
      </section>

      <section class="alertas-controls" aria-label="Buscador y filtros de expedientes">
        <div class="alertas-search-input-wrap">
          <svg class="alertas-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input type="search" id="alertas-query" class="alertas-search-input" placeholder="Buscar por marca, modelo, EAN o variante (ej.: DeWalt, DWS780, 885911235112, DW8307-AR, Makita DGP180)..." autocomplete="off" aria-label="Buscar herramienta en expedientes técnicos">
        </div>
        <div class="alertas-filters">
          <span class="alertas-filter-label">Estado:</span>
          <button type="button" class="alertas-chip active" data-filter-estado="TODOS" aria-pressed="true">Todos</button>
          <button type="button" class="alertas-chip" data-filter-estado="ALERTA_OFICIAL" aria-pressed="false">Alerta oficial</button>
          <button type="button" class="alertas-chip" data-filter-estado="SIN_ALERTAS" aria-pressed="false">Sin alertas encontradas</button>
          <span class="alertas-filter-label" style="margin-left: 0.75rem;">Marca:</span>
          <button type="button" class="alertas-chip active" data-filter-marca="TODAS" aria-pressed="true">Todas</button>
          {marcas_chips}
        </div>
      </section>

      <div id="alertas-contador" aria-live="polite" style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 1.25rem;">
        Mostrando {len(expedientes)} expedientes técnicos disponibles
      </div>

      <div id="alertas-grid" class="alertas-grid">
        {"".join(cards_html)}
      </div>

      <div id="alertas-vacio" style="display: none; text-align: center; padding: 3rem 1rem; color: #94a3b8; background: var(--bg-card); border-radius: 14px; border: 1px solid var(--border);">
        <p style="font-size: 1.1rem; color: #ffffff; margin-bottom: 0.5rem;">No se encontraron expedientes para la búsqueda especificada.</p>
        <p style="font-size: 0.9rem;">Verificá la ortografía del modelo, ingresá el código de variante o restablecé los filtros para ver todos los modelos revisados.</p>
      </div>

      {registro_html}

      <section class="dossier-section" style="margin-top: 3rem;">
        <h2>Metodología de monitoreo y fuentes oficiales</h2>
        <p class="dossier-section-desc">
          La actualización diaria se configura en producción; su ejecución efectiva puede comprobarse en el estado del servicio. Las fuentes consultadas son:
        </p>
        <ul style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6; padding-left: 1.25rem;">
          <li><strong>CPSC (Estados Unidos):</strong> monitoreo vía API oficial sobre avisos de retiro y seguridad en Norteamérica.</li>
          <li><strong>Defensa del Consumidor (Argentina):</strong> registro oficial nacional de alertas y retiros de productos.</li>
          <li><strong>SERNAC (Chile):</strong> sistema de alertas de seguridad del mercado chileno y regional del Cono Sur.</li>
          <li><strong>Documentación primaria:</strong> repositorios oficiales de despiece (Toolservicenet), manuales originales y redes de asistencia autorizada.</li>
        </ul>
        <p style="font-size: 0.82rem; color: #94a3b8; margin-top: 1rem; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
          {escape(DESCARGO_CAMPANA_EXTRANJERA)}
        </p>
      </section>
    </div>

    <script>
    (function() {{
      const input = document.getElementById('alertas-query');
      const cards = Array.from(document.querySelectorAll('.dossier-card'));
      const emptyState = document.getElementById('alertas-vacio');
      const counter = document.getElementById('alertas-contador');

      let currentEstado = 'TODOS';
      let currentMarca = 'TODAS';

      function filtrar() {{
        const rawQ = (input ? input.value : '').trim().toLowerCase();
        const tokens = rawQ.split(/\\s+/).filter(Boolean);
        let visibles = 0;

        cards.forEach(card => {{
          const cardSearch = card.getAttribute('data-search') || '';
          const cardMarca = card.getAttribute('data-marca') || '';
          const cardEstado = card.getAttribute('data-estado') || '';

          const matchQ = tokens.length === 0 || tokens.every(tok => cardSearch.includes(tok));
          const matchEstado = currentEstado === 'TODOS' || cardEstado === currentEstado;
          const matchMarca = currentMarca === 'TODAS' || cardMarca === currentMarca;

          if (matchQ && matchEstado && matchMarca) {{
            card.style.display = 'flex';
            visibles++;
          }} else {{
            card.style.display = 'none';
          }}
        }});

        if (emptyState) {{
          emptyState.style.display = visibles === 0 ? 'block' : 'none';
        }}
        if (counter) {{
          counter.textContent = 'Mostrando ' + visibles + ' de ' + cards.length + ' expedientes técnicos disponibles';
        }}
      }}

      if (input) {{
        input.addEventListener('input', filtrar);
      }}

      document.querySelectorAll('[data-filter-estado]').forEach(btn => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('[data-filter-estado]').forEach(b => {{
            b.classList.remove('active');
            b.setAttribute('aria-pressed', 'false');
          }});
          btn.classList.add('active');
          btn.setAttribute('aria-pressed', 'true');
          currentEstado = btn.getAttribute('data-filter-estado');
          filtrar();
        }});
      }});

      document.querySelectorAll('[data-filter-marca]').forEach(btn => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('[data-filter-marca]').forEach(b => {{
            b.classList.remove('active');
            b.setAttribute('aria-pressed', 'false');
          }});
          btn.classList.add('active');
          btn.setAttribute('aria-pressed', 'true');
          currentMarca = btn.getAttribute('data-filter-marca');
          filtrar();
        }});
      }});
    }})();
    </script>
    """
    return content


def render_model_dossier_page(exp: Dict[str, Any]) -> str:
    """Genera la página individual del expediente técnico de un modelo (/alertas/<slug>/)."""
    exp = expediente_publico(exp)
    avisos_html = "".join(
        f'<p class="alertas-disclaimer-box" role="status">{escape(aviso)}</p>'
        for aviso in exp.get("avisos_actualizacion", [])
    )
    status_info = ESTADOS_ALERTA.get(exp["estado_general"], ESTADOS_ALERTA["NO_REVISADO"])

    # Tabla de variantes
    variantes_rows = []
    for v in exp.get("variantes", []):
        variantes_rows.append(f"""
        <tr>
          <td><strong style="color: #ffffff;">{escape(v['codigo'])}</strong></td>
          <td>{escape(v.get('tipo_revision', 'S/D'))}</td>
          <td>{escape(v.get('alimentacion', 'S/D'))}</td>
          <td><code>{escape(v.get('codigo_barras', 'S/D'))}</code></td>
          <td>{escape(v.get('mercado', 'S/D'))}</td>
          <td>{escape(v.get('notas', ''))}</td>
        </tr>
        """)

    # Documentación técnica
    doc = exp.get("documentacion", {})
    doc_links = []
    if doc.get("manual_url"):
        doc_links.append(f'<a href="{escape(doc["manual_url"], quote=True)}" target="_blank" rel="noopener noreferrer" class="btn-doc"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> {escape(doc.get("manual_rotulo", "Manual oficial"))} ↗</a>')
    if doc.get("despiece_url"):
        doc_links.append(f'<a href="{escape(doc["despiece_url"], quote=True)}" target="_blank" rel="noopener noreferrer" class="btn-doc"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg> {escape(doc.get("despiece_rotulo", "Despiece de partes"))} ↗</a>')
    if doc.get("ficha_url"):
        doc_links.append(f'<a href="{escape(doc["ficha_url"], quote=True)}" target="_blank" rel="noopener noreferrer" class="btn-doc"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M14 9h4"/><path d="M14 15h4"/></svg> {escape(doc.get("ficha_rotulo", "Ficha técnica oficial"))} ↗</a>')

    # Alertas
    alertas = exp.get("alertas", [])
    for tipo in ("manual", "despiece", "ficha"):
        if not doc.get(tipo + "_url") and doc.get(tipo + "_rotulo"):
            doc_links.append(f'<p class="dossier-section-desc">{escape(doc[tipo + "_rotulo"])}</p>')
    alertas_html = []
    if alertas:
        for al in alertas:
            estado_al = al.get("estado_alcance", "ALERTA_OFICIAL")
            card_class = "alerta-confirmada" if estado_al == "ALERTA_OFICIAL" else ("alerta-posible" if estado_al == "POSIBLE_COINCIDENCIA" else "alerta-neutral")

            excepcion_box = ""
            if al.get("excepciones_expresas") and al["excepciones_expresas"] != "N/A":
                excepcion_box = f"""
                <div class="alert-exclusion-box">
                  <strong>⚠️ EXCEPCIONES Y ALCANCE ESPECÍFICO:</strong><br>
                  {escape(al['excepciones_expresas'])}
                </div>
                """

            # Campos estructurados adicionales
            campos_extra = []
            if al.get("identificacion_lotes_series"):
                campos_extra.append(f'<div class="alert-field"><strong>Lotes y series:</strong> {escape(al["identificacion_lotes_series"])}</div>')
            if al.get("periodo_comercializacion"):
                campos_extra.append(f'<div class="alert-field"><strong>Período de venta:</strong> {escape(al["periodo_comercializacion"])}</div>')
            if al.get("ubicacion_identificador"):
                campos_extra.append(f'<div class="alert-field"><strong>Ubicación etiqueta:</strong> {escape(al["ubicacion_identificador"])}</div>')
            if al.get("unidades_involucradas"):
                campos_extra.append(f'<div class="alert-field"><strong>Unidades involucradas:</strong> {escape(al["unidades_involucradas"])}</div>')

            ev = al.get("evidencia_fuente", {})
            ev_texto = ""
            if isinstance(ev, dict) and ev.get("cotejo_contra_registro"):
                ev_texto = f"""
                <div class="alert-field" style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem; padding-top: 0.4rem; border-top: 1px dotted #21262d;">
                  <strong>Cotejo documental:</strong> {escape(ev.get('cotejo_contra_registro', ''))}
                  (Revisión: {escape(ev.get('revisado_por', 'TallerLab'))})
                </div>
                """

            alertas_html.append(f"""
            <div class="alert-card {card_class}">
              <div class="alert-card-header">
                <div>
                  <span class="alert-card-agency">{escape(al['organismo'])}</span>
                  <span class="alert-card-market">{escape(al['pais_mercado'])}</span>
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                  Aviso: <code>{escape(al['id_aviso'])}</code> · Fecha: {escape(al['fecha'])}
                </div>
              </div>
              <div class="alert-field">
                <strong>Tipo de aviso:</strong> {escape(al.get('tipo_aviso', 'Seguridad'))}
              </div>
              <div class="alert-field">
                <strong>Modelos afectados:</strong> {escape(al['modelos_afectados'])}
              </div>
              {"".join(campos_extra)}
              {excepcion_box}
              <div class="alert-field">
                <strong>Defecto y riesgo:</strong> {escape(al['defecto_riesgo'])}
              </div>
              <div class="alert-field">
                <strong>Acción de la autoridad:</strong> {escape(al['accion_oficial'])}
              </div>
              {ev_texto}
              <div class="alert-card-footer">
                <span style="color: #64748b;">Investigación técnica independiente TallerLab</span>
                <a href="{escape(al['enlace_original'], quote=True)}" target="_blank" rel="noopener noreferrer" style="color: #ff5500; font-weight: 700; text-decoration: none;">Ver publicación original en {escape(al['organismo'])} ↗</a>
              </div>
            </div>
            """)
    else:
        # Estado sin alertas o no revisado
        fuentes_nombres = [fc["fuente"] for fc in exp.get("fuentes_consultadas", [])]
        fuentes_txt = ", ".join(fuentes_nombres) if fuentes_nombres else "fuentes oficiales"

        if exp["estado_general"] == "NO_REVISADO":
            alertas_html.append(f"""
            <div class="alert-card alerta-neutral" style="padding: 1.75rem;">
              <h3 style="color: #94a3b8; margin-top: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>ℹ️</span> Relevamiento documental en proceso
              </h3>
              <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                Este modelo se encuentra en cola de análisis documental. Aún no se han completado las consultas
                sistemáticas en las bases de datos de seguridad para documentar antecedentes históricos.
              </p>
              <div class="alertas-disclaimer-box" style="border-left-color: #64748b; background: rgba(30, 41, 59, 0.5);">
                <strong>Aviso de alcance:</strong> {escape(DESCARGO_NO_GARANTIA_SEGURIDAD)}
              </div>
            </div>
            """)
        elif exp["estado_general"] == "FUENTE_INACCESIBLE":
            alertas_html.append(f"""
            <div class="alert-card alerta-posible" style="padding: 1.75rem;">
              <h3 style="color: #fbbf24; margin-top: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>⚠️</span> Consulta de fuentes externas no completada
              </h3>
              <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                Una o más fuentes externas no pudieron ser contactadas durante la última actualización.
                Se preservan los datos históricos archivados sin asumir ausencia de alertas.
              </p>
              <div class="alertas-disclaimer-box" style="border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08);">
                <strong>Aviso de exactitud:</strong> {escape(DESCARGO_NO_GARANTIA_SEGURIDAD)}
              </div>
            </div>
            """)
        else:
            alertas_html.append(f"""
            <div class="alert-card alerta-neutral" style="padding: 1.75rem;">
              <h3 style="color: #94a3b8; margin-top: 0; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>ℹ️</span> Sin alertas coincidentes registradas
              </h3>
              <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                En los relevamientos documentados de {escape(fuentes_txt)},
                no se registraron coincidencias para <strong>{escape(exp['marca'])} {escape(exp['modelo_base'])}</strong>.
                El resultado corresponde a los modelos, períodos y métodos detallados en cada consulta.
                Fecha de revisión editorial: {escape(exp['fecha_revision'])}.
              </p>
              <div class="alertas-disclaimer-box" style="border-left-color: #64748b; background: rgba(30, 41, 59, 0.5);">
                <strong>Regla de exactitud técnica:</strong> {escape(DESCARGO_NO_GARANTIA_SEGURIDAD)}
              </div>
            </div>
            """)

    # Fuentes consultadas
    fuentes_rows = []
    for fc in exp.get("fuentes_consultadas", []):
        st = fc.get("estado_actualizacion", fc.get("estado", "PENDIENTE"))
        if st == "FALLIDA":
            badge_fc = '<span style="color: #f87171; font-weight: 700;">⚠️ Inaccesible</span>'
            resultado_txt = f"{fc.get('resultado', '')} (Fallo temporal en la consulta; no presupone ausencia de alertas)"
        elif st == "EXITOSA":
            badge_fc = '<span style="color: #38bdf8; font-weight: 600;">Consultada</span>'
            resultado_txt = fc.get("resultado", "")
        else:
            badge_fc = f'<span style="color: #94a3b8; font-weight: 600;">{escape(st)}</span>'
            resultado_txt = fc.get("resultado", "")

        fuentes_rows.append(f"""
        <tr>
          <td><strong style="color: #f1f5f9;">{escape(fc['fuente'])}</strong></td>
          <td>{escape(fc['fecha_consulta'])}</td>
          <td>{badge_fc}</td>
          <td>{escape(resultado_txt)}</td>
        </tr>
        """)

    # Enlace a guía de compra
    guia_box = ""
    if exp.get("guia_url"):
        guia_box = f"""
        <div style="margin-top: 1.5rem; padding: 1.15rem; background: #0d1117; border: 1px solid var(--border); border-radius: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <strong style="color: #ffffff; display: block; margin-bottom: 0.2rem;">¿Estás evaluando este equipo antes de comprar?</strong>
            <span style="font-size: 0.85rem; color: #94a3b8;">Consultá la comparativa técnica de capacidades, alternativas y diferencias de taller.</span>
          </div>
          <a href="{escape(exp['guia_url'], quote=True)}" class="btn-doc" style="background: #ff5500; border-color: #ff5500;">Ver comparativa en TallerLab →</a>
        </div>
        """

    resumen_html = render_resumen(exp)
    fecha_rev = escape(str(exp['fecha_revision']))

    content = f"""
    {ALERTAS_CSS}{RESUMEN_CSS}
    <div class="dossier-detail">
      <nav class="breadcrumb" aria-label="Migas de pan">
        <a href="/">Inicio</a>
        <span aria-hidden="true">/</span>
        <a href="/alertas/">Documentación y alertas</a>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{escape(exp['marca'])} {escape(exp['modelo_base'])}</span>
      </nav>

      <header class="dossier-header">
        <div class="dossier-header-top">
          <span class="dossier-brand-tag">{escape(exp['marca'])} · {escape(exp['categoria'].capitalize())}</span>
          {_render_status_badge(exp['estado_general'])}
        </div>
        <h1>Expediente técnico: {escape(exp['marca'])} {escape(exp['modelo_base'])}</h1>
        <p class="dossier-subtitle">{escape(exp['nombre_comercial'])}</p>

        <div class="dossier-status-banner" style="background: {status_info['bg']}; color: {status_info['color']}; border: 1px solid rgba(255,255,255,0.15);">
          <span class="dossier-status-banner-icon">{status_info['icono']}</span>
          <div class="dossier-status-banner-content">
            <h3>{escape(status_info['etiqueta'])}</h3>
            <p>{escape(status_info['descripcion'])}</p>
          </div>
        </div>

        {avisos_html}
        <div class="dossier-meta-bar">
          <span>Editor responsable: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a></span>
          <span>Última revisión editorial: <strong style="color: #cbd5e1;"><time datetime="{fecha_rev}">{escape(fecha_legible(exp['fecha_revision']))}</time></strong></span>
          <span>Cotejo documental: <strong style="color: #cbd5e1;">{escape(exp['revisado_por'])}</strong></span>
          <span>Estado: <strong style="color: #cbd5e1;">{escape(status_info["etiqueta"])}</strong></span>
          <span><a href="/alertas/metodologia/">Cómo investigamos</a></span>
        </div>
      </header>
      {resumen_html}

      <section class="dossier-section" id="variantes">
        <h2>Variantes y códigos identificados</h2>
        <p class="dossier-section-desc">
          En Argentina y la región conviven distintas variantes con sufijos regionales, revisiones de fabricación (Tipos)
          y tensiones eléctricas. No deben extrapolarse piezas, garantías ni campañas entre códigos distintos.
        </p>
        <div class="dossier-table-wrap">
          <table class="dossier-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Tipo / Revisión</th>
                <th>Tensión / Frecuencia</th>
                <th>Código EAN/Barras</th>
                <th>Mercado documentado</th>
                <th>Notas técnicas</th>
              </tr>
            </thead>
            <tbody>
              {"".join(variantes_rows)}
            </tbody>
          </table>
        </div>
      </section>

      <section class="dossier-section" id="documentacion">
        <h2>Documentación oficial y soporte en Argentina</h2>
        <p class="dossier-section-desc">
          Enlaces directos a repositorios originales del fabricante, red de asistencia autorizada y condiciones de garantía en el país:
        </p>
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
          {"".join(doc_links)}
        </div>
        <div style="background: #0d1117; border: 1px solid var(--border); border-radius: 10px; padding: 1.25rem; font-size: 0.88rem; line-height: 1.6;">
          <p style="margin: 0 0 0.65rem;"><strong style="color: #ffffff;">Garantía en Argentina:</strong> {escape(str(doc.get('garantia_detalle', 'Por confirmar; consultar póliza oficial.')))}</p>
          <p style="margin: 0 0 0.65rem;"><strong style="color: #ffffff;">Servicio técnico autorizado:</strong> {escape(str(doc.get('servicio_oficial', 'Red oficial del fabricante.')))}</p>
          <p style="margin: 0;"><strong style="color: #ffffff;">Baterías y alimentación:</strong> {escape(str(doc.get('baterias_compatibles', 'Consultar manual oficial.')))}</p>
        </div>
      </section>

      <section class="dossier-section" id="alertas">
        <h2>Expediente de alertas de seguridad y campañas</h2>
        <p class="dossier-section-desc">
          Detalle cronológico de avisos regulatorios, retiros y notas de seguridad emitidos por organismos oficiales:
        </p>
        {"".join(alertas_html)}
      </section>

      <section class="dossier-section">
        <h2>Fuentes consultadas y registro de verificación</h2>
        <p class="dossier-section-desc">
          Historial de comprobación de organismos oficiales para este expediente. Si una fuente externa no responde,
          se preservan los hallazgos anteriores y no se asume ausencia de alertas.
        </p>
        <div class="dossier-table-wrap">
          <table class="dossier-table">
            <thead>
              <tr>
                <th>Organismo / Fuente</th>
                <th>Fecha de consulta</th>
                <th>Estado de acceso</th>
                <th>Resultado de la comprobación</th>
              </tr>
            </thead>
            <tbody>
              {"".join(fuentes_rows)}
            </tbody>
          </table>
        </div>
        <div class="alertas-disclaimer-box" style="margin-top: 1.25rem;">
          <strong>Independencia técnica:</strong> {escape(DESCARGO_INDEPENDENCIA)}
        </div>
      </section>

      {guia_box}
    </div>
    """
    return content


def dossier_schema(exp: Dict[str, Any], canonical_url: str) -> Dict[str, Any]:
    """Marcado Schema.org (TechArticle) del expediente; ver alertas_seo.dossier_schema."""
    return _dossier_schema_seo(exp, canonical_url)
