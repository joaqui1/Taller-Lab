"""
Vistas y componentes HTML para TallerLab Data.
Incluye:
- Hub de herramientas (/herramientas/)
- Ficha técnica por modelo (/herramientas/{slug}/)
- Comparador interactivo (/herramientas/comparar/)
- Lista de comparaciones curadas (/herramientas/comparaciones/)
- Detalle de comparativa curada (/herramientas/comparar/{pair_slug}/)
- Metodología técnica y fuentes (/herramientas/metodologia/)
- Registro público de correcciones (/herramientas/correcciones/)
- Estudio documental (/herramientas/investigacion/brecha-especificaciones-argentina/)
"""

from __future__ import annotations

import json
from html import escape
from typing import Any, Dict, List, Optional

from markdown_it import MarkdownIt

_MD = MarkdownIt("commonmark", {"html": True})

import re
from tallerlab_data.quality import latest_verified_offer, source_type_for, backed_specs, tool_is_indexable
from tallerlab_data.documentary import source_record, evidence_source_label
from tallerlab_data.selection import family, family_label, documentary_order, evidence_counts, LABELS, render_decision_guidance
from tallerlab_data.affiliates import affiliate_for, render_affiliate_options
from tallerlab_data.comparator import compare_tools
from tallerlab_data.editorial_comparisons import (
    EDITORIAL_COMPARISONS,
    EditorialComparison,
    get_all_editorial_comparisons,
    get_editorial_comparison,
)
from tallerlab_data.models import TechnicalTool
from comunidad.components import render_model_community
from tallerlab_data.research_study import get_research_study_data
from tallerlab_data.storage import (
    get_all_categories,
    get_all_tools,
    get_tool_by_slug,
    get_tools_by_category,
    list_candidates,
    list_corrections,
)

TALLERLAB_DATA_CSS = """
<style>
/* TallerLab Data - Estilos de catálogo técnico e ingeniería documental */
.tl-container {
  --bg-card: #161b22;
  --border: #303b49;
  --border-subtle: #293341;
  max-width: 1140px;
  margin: 0 auto;
  padding: 1.5rem 1rem 4rem;
}
.tl-container *, .tl-container *::before, .tl-container *::after { box-sizing: border-box; }
.tl-container { overflow-wrap: anywhere; }
.tl-container #tl-commercial-options { scroll-margin-top: 100px; }
.tl-container .co-teaser { color: #cbd5e1; }
.tl-container .co-teaser h2 { color: #ffffff; }
.tl-container .co-teaser p { color: #cbd5e1; }
.tl-container .co-kicker { color: #ff9966; }
.tl-hero {
  background: linear-gradient(135deg, rgba(22, 27, 34, 0.98) 0%, rgba(13, 17, 23, 0.98) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2.25rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}
.tl-hero::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #ff5500, #38bdf8, #10b981);
}
.tl-kicker {
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #ff5500;
  margin-bottom: 0.5rem;
  display: inline-block;
}
.tl-hero h1 {
  font-size: 2.2rem;
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 0.75rem;
  line-height: 1.2;
}
.tl-hero p.lead {
  color: #94a3b8;
  font-size: 1.05rem;
  line-height: 1.6;
  max-width: 860px;
  margin-bottom: 1.5rem;
}
.tl-hero p.tl-byline {
  color: #94a3b8;
  font-size: .9rem;
  margin: -.75rem 0 1rem;
}
.tl-hero p.tl-byline a { color: inherit; text-decoration: underline; }
details.tl-hash { display: inline-block; font-size: .8rem; margin-left: .4rem; }
details.tl-hash code { word-break: break-all; }
.tl-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 1rem;
  margin-top: 1.25rem;
}
.tl-stat-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.15rem;
}
.tl-stat-num {
  font-size: 1.6rem;
  font-weight: 800;
  color: #38bdf8;
  display: block;
  line-height: 1.1;
}
.tl-stat-label {
  font-size: 0.78rem;
  color: #94a3b8;
  margin-top: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.tl-nav-pills {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
}
.tl-nav-pill {
  font-size: 0.85rem;
  font-weight: 700;
  padding: 0.5rem 0.95rem;
  border-radius: 8px;
  background: #1e293b;
  border: 1px solid #334155;
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.15s ease;
}
.tl-nav-pill:hover {
  background: #334155;
  color: #ffffff;
  border-color: #64748b;
}
.tl-nav-pill.active {
  background: rgba(255, 85, 0, 0.15);
  border-color: #ff5500;
  color: #ff7733;
}

/* Tablas y Fichas */
.tl-card {
  color: #cbd5e1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.75rem;
  margin-bottom: 2rem;
}
.tl-card h2, .tl-card h3 { color: #ffffff; }
.tl-card a:not(.tl-nav-pill) { color: #ff9966; }
.tl-card-header {
  margin-bottom: 1.25rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.tl-card-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}
.tl-card-desc {
  font-size: 0.88rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}
.tl-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.tl-badge-declarado { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35); }
.tl-badge-medido { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.35); }
.tl-badge-calculado { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35); }
.tl-badge-contradictorio { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.45); }
.tl-badge-no-encontrado { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }

.tl-badge-220v {
  background: rgba(16, 185, 129, 0.12);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.tl-table-wrap {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--border);
  margin-top: 1rem;
}
.tl-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
}
.tl-table th {
  background: #11151c;
  color: #cbd5e1;
  font-weight: 700;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.tl-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
  color: #e2e8f0;
  vertical-align: top;
}
.tl-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}
.tl-cell-spec {
  font-weight: 700;
  color: #ffffff;
  min-width: 150px;
}
.tl-cell-val {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #38bdf8;
  font-weight: 600;
  white-space: nowrap;
}
.tl-cell-cond {
  color: #94a3b8;
  font-size: 0.83rem;
  min-width: 190px;
}
.tl-cell-src {
  font-size: 0.8rem;
  color: #94a3b8;
  min-width: 170px;
}
.tl-cell-src a {
  color: #cbd5e1;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.tl-cell-src a:hover {
  color: #ff5500;
}

/* Alertas de advertencia e inconsistencia */
.tl-alert-box {
  background: #202a38 !important;
  border-left: 4px solid #f59e0b;
  border-radius: 0 10px 10px 0;
  padding: 1.15rem 1.35rem;
  margin: 1.25rem 0;
}
.tl-alert-title {
  font-weight: 800;
  font-size: 0.95rem;
  color: #fbbf24;
  margin-bottom: 0.35rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.tl-alert-text {
  font-size: 0.88rem;
  color: #e2e8f0;
  line-height: 1.55;
}

.tl-info-box {
  background: #192a3a;
  border-left: 4px solid #38bdf8;
  border-radius: 0 10px 10px 0;
  padding: 1rem 1.25rem;
  margin: 1.25rem 0;
  font-size: 0.86rem;
  color: #cbd5e1;
  line-height: 1.5;
}

/* Cuadrícula de modelos en hub */
.tl-catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(320px, 100%), 1fr));
  gap: 1.25rem;
  margin-top: 1.5rem;
}
.tl-tool-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.tl-tool-card:hover {
  border-color: #ff5500;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
.tl-tool-brand {
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #ff7733;
}
.tl-tool-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0.25rem 0 0.5rem;
}
.tl-tool-category {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 1rem;
}
.tl-tool-specs-list {
  list-style: none;
  margin: 0 0 1.25rem;
  padding: 0;
  font-size: 0.83rem;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.75rem;
}
.tl-tool-specs-list li {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  color: #cbd5e1;
}
.tl-tool-specs-list li span.spec-k {
  color: #94a3b8;
}
.tl-tool-specs-list li span.spec-v {
  font-weight: 700;
  color: #ffffff;
}
.tl-tool-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-subtle);
  padding-top: 0.85rem;
  margin-top: auto;
}
.tl-btn-detail {
  font-size: 0.82rem;
  font-weight: 700;
  color: #ff7733;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
.tl-btn-detail:hover {
  color: #ffffff;
}

/* Comparador de herramientas */
.tl-comparator-matrix {
  display: grid;
  grid-template-columns: 220px repeat(auto-fit, minmax(240px, 1fr));
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  margin-top: 1.5rem;
}
.tl-matrix-col-header {
  background: #11151c;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  text-align: center;
}
.tl-matrix-col-header:last-child {
  border-right: none;
}
.tl-matrix-row-label {
  background: rgba(18, 22, 31, 0.7);
  padding: 0.85rem 1rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: #cbd5e1;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid var(--border);
  display: flex;
  align-items: center;
}
.tl-matrix-cell {
  background: var(--bg-card);
  padding: 0.85rem 1rem;
  font-size: 0.85rem;
  color: #e2e8f0;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid var(--border);
}
.tl-matrix-cell:last-child {
  border-right: none;
}
.tl-matrix-warning {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
  font-size: 0.75rem;
  color: #fbbf24;
  margin-top: 0.4rem;
}

/* Filtros y buscador client-side */
.tl-search-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.tl-search-input {
  flex: 1;
  min-width: min(260px, 100%);
  background: #0d1117;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.7rem 1rem;
  color: #ffffff;
  font-size: 0.92rem;
  font-family: inherit;
}
.tl-search-input:focus {
  outline: none;
  border-color: #ff5500;
}
.tl-select {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  background: #0d1117;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.7rem 1rem;
  color: #ffffff;
  font-size: 0.9rem;
  font-family: inherit;
}
.tl-badge-battery, .tl-badge-corded, .tl-badge-combustion { display:inline-block; background:#253247; color:#e2e8f0; padding:.3rem .5rem; border-radius:6px; font-size:.8rem; }
@media (max-width: 640px) {
  .tl-hero { padding: 1.4rem 1.1rem; }
  .tl-table.tl-stack thead { display: none; }
  .tl-table.tl-stack, .tl-table.tl-stack tbody, .tl-table.tl-stack tr, .tl-table.tl-stack td { display: block; width: 100%; }
  .tl-table.tl-stack tr { padding: .8rem 0; border-bottom: 1px solid var(--border); }
  .tl-table.tl-stack td { border: 0; padding: .2rem 0; }
  .tl-table.tl-stack td.tl-cell-spec { font-weight: 800; font-size: 1rem; color: #fff; }
  .tl-table.tl-stack td[data-label]::before { content: attr(data-label) ": "; font-weight: 700; color: #94a3b8; }
}

/* Tarjetas de ofertas comerciales observadas */
.tl-offer-box {
  background: rgba(18, 22, 31, 0.8);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.15rem;
  margin-top: 1rem;
}
.tl-offer-price {
  font-size: 1.4rem;
  font-weight: 800;
  color: #38bdf8;
  margin-bottom: 0.25rem;
}
.tl-offer-meta {
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.4;
}

/* Callout en guías existentes */
.tl-guide-integration-callout {
  background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(18, 22, 31, 0.98) 100%);
  border: 1px solid rgba(255, 85, 0, 0.3);
  border-radius: 12px;
  padding: 1.5rem 1.75rem;
  margin: 2.5rem 0;
  position: relative;
}
.tl-guide-integration-callout::before {
  content: "";
  position: absolute;
  top: 0; left: 0; width: 4px; bottom: 0;
  background: #ff5500;
  border-radius: 12px 0 0 12px;
}
.tl-guide-callout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.tl-guide-callout-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}
.tl-guide-callout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}
.tl-guide-callout-item {
  background: rgba(13, 17, 23, 0.7);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.85rem 1rem;
}
.tl-guide-callout-item h4 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.35rem;
}
.tl-guide-callout-item p {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 0.5rem;
}
.tl-guide-callout-item a {
  font-size: 0.8rem;
  font-weight: 700;
  color: #ff7733;
}
</style>
"""

TALLERLAB_DATA_JS = """
<script>
// Filtrado client-side para el catálogo de herramientas
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('tl-search-input');
  const categorySelect = document.getElementById('tl-category-filter');
  const familySelect = document.getElementById('tl-family-filter');
  const evidenceSelect = document.getElementById('tl-evidence-filter');
  const resetButton = document.getElementById('tl-reset-filters');
  const cards = document.querySelectorAll('.tl-tool-card');
  const countEl = document.getElementById('tl-visible-count');

  function filterCards() {
    if (!cards.length) return;
    const clean = value => value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
    const term = clean(searchInput ? searchInput.value : '');
    const cat = (categorySelect ? categorySelect.value : '');
    let visible = 0;

    cards.forEach(card => {
      const cardBrand = clean(card.getAttribute('data-brand') || '');
      const cardModel = clean(card.getAttribute('data-model') || '');
      const cardMpn = clean(card.getAttribute('data-mpn') || '');
      const cardCat = card.getAttribute('data-category') || '';

      const matchText = !term || cardBrand.includes(term) || cardModel.includes(term) || cardMpn.includes(term);
      const matchCat = !cat || cardCat === cat;
      const matchFamily = !familySelect || !familySelect.value || card.getAttribute('data-family') === familySelect.value;
      const matchEvidence = !evidenceSelect || !evidenceSelect.value || Number(card.getAttribute('data-supported')) > 0;

      if (matchText && matchCat && matchFamily && matchEvidence) {
        card.style.display = 'flex';
        visible++;
      } else {
        card.style.display = 'none';
      }
    });

    if (countEl) {
      countEl.textContent = visible;
    }
    const empty = document.getElementById('tl-empty-filter');
    if (empty) empty.hidden = visible > 0;
  }

  if (searchInput) searchInput.addEventListener('input', filterCards);
  if (categorySelect) categorySelect.addEventListener('change', filterCards);
  if (familySelect) familySelect.addEventListener('change', filterCards);
  if (evidenceSelect) evidenceSelect.addEventListener('change', filterCards);
  if (resetButton) resetButton.addEventListener('click', function() {
    if (searchInput) searchInput.value = '';
    [categorySelect, familySelect, evidenceSelect].forEach(select => { if (select) select.value = ''; });
    filterCards();
  });
});
</script>
"""

def _status_badge(status: str) -> str:
    badge_map = {
        "declarado": ("tl-badge-declarado", "Declarado"),
        "medido": ("tl-badge-medido", "Medido"),
        "calculado": ("tl-badge-calculado", "Calculado"),
        "contradictorio": ("tl-badge-contradictorio", "Contradictorio"),
        "no_encontrado": ("tl-badge-no-encontrado", "No Encontrado"),
    }
    cls, label = badge_map.get(status, ("tl-badge-no-encontrado", status.capitalize()))
    return f'<span class="tl-badge {cls}">{escape(label)}</span>'


def render_tools_hub_page(category: Optional[str] = None) -> str:
    """Renderiza el catálogo principal de TallerLab Data con los 100 modelos."""
    all_tools = sorted(get_all_tools(), key=documentary_order)
    categories = get_all_categories()
    selected_category = category if category in categories else None
    filtered_tools = [t for t in all_tools if t.category == selected_category] if selected_category else all_tools

    cat_options = "".join(
        f'<option value="{escape(c)}"{(" selected" if c == selected_category else "")}>{escape(c.capitalize())}</option>'
        for c in categories
    )

    cards_html = []
    for tool in filtered_tools:
        # Extraer hasta 3 especificaciones clave
        specs_summary = []
        supported = [s for s in tool.specifications if s.documentary_status == 'concordancia_textual']
        for s in supported[:4]:
            val_display = s.original_value
            specs_summary.append(
                f'<li><span class="spec-k">{escape(s.name)}:</span> <span class="spec-v">{escape(val_display)}</span></li>'
            )
        specs_summary.append(f'<li><span class="spec-k">Datos con fuente:</span> <span class="spec-v">{len(supported)} de {len(tool.specs)}</span></li>')

        card = f"""
        <article class="tl-tool-card" data-brand="{escape(tool.brand)}" data-model="{escape(tool.model_name)}" data-mpn="{escape(tool.mpn or '')}" data-category="{escape(tool.category)}" data-family="{family(tool)}" data-supported="{len(supported)}">
          <div>
            <div class="tl-tool-brand">{escape(tool.brand)}</div>
            <h2 class="tl-tool-name"><a href="/herramientas/{tool.slug}/">{escape(tool.brand)} {escape(tool.model_name)}</a></h2>
            <div class="tl-tool-category">{escape(family_label(tool))} {f'· MPN: {escape(tool.mpn)}' if tool.mpn else ''}</div>
            <ul class="tl-tool-specs-list">
              {"".join(specs_summary)}
            </ul>
          </div>
          <div class="tl-tool-footer">
            <span class="{tool.power_badge_css}">{escape(tool.power_badge_text)}</span>
            <a href="/herramientas/{tool.slug}/" class="tl-btn-detail">Ver ficha técnica →</a>
          </div>
        </article>
        """
        cards_html.append(card)

    return f"""
    {TALLERLAB_DATA_CSS}
    <div class="tl-container">
      <header class="tl-hero">
        <span class="tl-kicker">TallerLab Data · Catálogo técnico</span>
        <h1>Base de Datos Técnica de Herramientas en Argentina</h1>
        <p class="lead">Especificaciones declaradas, fuentes enlazadas y condiciones registradas para comparar modelos. La cobertura documental varía entre fichas; consultá cada fuente y variante antes de comprar.</p>

        <div class="tl-stats-grid">
          <div class="tl-stat-card">
            <span class="tl-stat-num">{len(all_tools)}</span>
            <span class="tl-stat-label">Modelos en el catálogo</span>
          </div>
          <div class="tl-stat-card">
            <span class="tl-stat-num">6</span>
            <span class="tl-stat-label">Categorías</span>
          </div>
          <div class="tl-stat-card">
            <span class="tl-stat-num">{len({s.source_url for t in all_tools for s in backed_specs(t)})}</span>
            <span class="tl-stat-label">Documentos de fabricante con datos localizados</span>
          </div>
          <div class="tl-stat-card">
            <span class="tl-stat-num">{sum(s.documentary_status == 'concordancia_textual' for t in all_tools for s in t.specifications)}</span>
            <span class="tl-stat-label">Valores localizados en esos documentos</span>
          </div>
        </div>

        <nav class="tl-nav-pills" aria-label="Navegación de TallerLab Data">
          <a href="/herramientas/comparar/" class="tl-nav-pill">⚖️ Comparador Técnico</a>
          <a href="/herramientas/comparaciones/" class="tl-nav-pill">📋 Comparativas Curadas</a>
          <a href="/herramientas/investigacion/brecha-especificaciones-argentina/" class="tl-nav-pill">📊 Estudio Brecha de Datos</a>
          <a href="/herramientas/metodologia/" class="tl-nav-pill">📖 Metodología Documental</a>
          <a href="/herramientas/correcciones/" class="tl-nav-pill">📝 Registro de Correcciones</a>
        </nav>
      </header>

      <section class="tl-card">
        <div class="tl-card-header">
          <div>
            <h2 class="tl-card-title">Explorador de Modelos (<span id="tl-visible-count" aria-live="polite">{len(filtered_tools)}</span> disponibles)</h2>
            <p class="tl-card-desc">Primero aparecen las fichas con mayor proporción de observaciones respaldadas; en empate, más observaciones y orden alfabético. No es un ranking de rendimiento. Filtrá por aplicación y documentación.</p>
          </div>
        </div>

        <div class="tl-search-bar">
          <input type="text" id="tl-search-input" class="tl-search-input" placeholder="Buscar por marca, modelo o código de pieza (ej. Lüsqtoff, DCH273, K4)..." aria-label="Buscar herramienta">
          <select id="tl-category-filter" class="tl-select" aria-label="Filtrar por categoría">
            <option value="">Todas las categorías (6)</option>
            {cat_options}
          </select>
          <select id="tl-family-filter" class="tl-select" aria-label="Filtrar por familia de herramienta"><option value="">Todas las familias</option>{''.join(f'<option value="{key}">{escape(label)}</option>' for key, label in LABELS.items())}</select>
          <select id="tl-evidence-filter" class="tl-select" aria-label="Filtrar por respaldo documental"><option value="">Todas las fichas</option><option value="supported">Con observaciones respaldadas</option></select>
          <button type="button" class="tl-nav-pill" id="tl-reset-filters">Limpiar filtros</button>
        </div>
        <p id="tl-empty-filter" hidden>No hay modelos para estos filtros. Cambiá la familia, el respaldo o la búsqueda.</p>

        <div class="tl-catalog-grid">
          {"".join(cards_html)}
        </div>
      </section>

      <div class="tl-info-box">
        <strong>Cómo leer estas fichas:</strong> cada dato muestra el documento del fabricante donde aparece y la fecha de consulta. Los datos que no encontramos en una fuente oficial quedan aparte y no se usan para comparar. TallerLab no vende herramientas ni las ensaya.
      </div>
    </div>
    {TALLERLAB_DATA_JS}
    """


AUTHOR_NAME = "Joaquín Vallasciani"
AUTHOR_PATH = "/autor/joaquin-vallasciani/"

_CONDITION_NOTES = {
    'sin_protocolo_especifico': 'La fuente no indica norma ni condición de medición para este valor.',
    'referencias_presentes': 'La norma o condición de medición citada aparece en el mismo documento.',
    'sin_respaldo': 'La condición de medición registrada no aparece en el documento.',
}


def _source_is_dead(record: Dict[str, Any]) -> bool:
    """Only link sources a reader can actually open and use.

    Linked: recovered documents, scanned manufacturer PDFs, and pages that only
    refuse automated readers (HTTP 403). Shown as plain text: 404/410, product
    pages that now redirect to a listing, and shop pages that could not be read.
    """
    if record.get('status') == 'recuperado':
        return False
    if record.get('reason', '').startswith('PDF sin texto'):
        return False
    return str(record.get('http_status', '')) != '403'


def _evidence_source_label(spec, record: Dict[str, Any]) -> str:
    return evidence_source_label(spec, record)


_MONTHS = ('enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre')


def _specs_section(tool: TechnicalTool, specs_rows: List[str]) -> str:
    return f'''      <section class="tl-card">
        <div class="tl-card-header">
          <div>
            <h2 class="tl-card-title">Especificaciones Técnicas Detalladas</h2>
            <p class="tl-card-desc">Cada valor se buscó, junto a su unidad, en un documento que menciona el código {escape(tool.mpn or tool.model_name)}. Que el texto coincida no prueba rendimiento ni que todas las variantes o kits sean iguales. Los valores sin respaldo quedan aparte, abajo.</p>
          </div>
        </div>

        <div class="tl-table-wrap">
          <table class="tl-table tl-stack">
            <thead>
              <tr>
                <th>Especificación</th>
                <th>Valor Original</th>
                <th>Valor Normalizado</th>
                <th>Condición atribuida por la fuente</th>
                <th>Fuente y Página</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {"".join(specs_rows) if specs_rows else '<tr><td colspan="6">Esta edición no establece especificaciones cuantitativas respaldadas para este código. La ficha conserva las referencias y sus motivos de exclusión.</td></tr>'}
            </tbody>
          </table>
        </div>
      </section>'''


def _sources_checked(tool: TechnicalTool) -> str:
    """Date the sources were last read, not the date the edition was closed."""
    urls = {s.source_url for s in tool.specifications if s.source_url} | {s.get('url', '') for s in tool.primary_sources}
    dates = [source_record(u).get('checked_at', '')[:10] for u in urls]
    return max((d for d in dates if d), default=tool.last_documented_date)


def _retired_notice(tool: TechnicalTool) -> str:
    """Say plainly when the manufacturer no longer lists the model."""
    official = [s for s in tool.primary_sources if source_type_for(s.get('url', ''), s.get('label', ''), s.get('type')) not in {'comercio', 'referencia_externa', 'documento_en_tercero'}]
    records = [source_record(s.get('url', '')) for s in official]
    retired = [r for r in records if 'retirada' in r.get('reason', '') or str(r.get('http_status', '')) in {'404', '410'}]
    if not records or len(retired) < len(records):
        return ''
    checked = max((r.get('checked_at', '')[:10] for r in retired), default='')
    return ('<div class="tl-info-box"><strong>Modelo sin página vigente del fabricante.</strong> '
            f'Al {escape(_human_date(checked))}, las páginas oficiales consultadas ya no muestran este modelo. '
            'Puede estar discontinuado o haber cambiado de código o de dirección web: confirmá con el vendedor que se trate de la misma versión.</div>')


def _human_date(value: str) -> str:
    try:
        y, m, d = (int(x) for x in (value or '')[:10].split('-'))
        return f"{d} de {_MONTHS[m-1]} de {y}"
    except (ValueError, IndexError):
        return value or 'fecha no registrada'


def _detail_lead(tool: TechnicalTool) -> str:
    backed = backed_specs(tool)
    name = escape(f"{tool.brand} {tool.model_name}")
    if not backed:
        return (f"Todavía no localizamos valores de {name} en documentación del fabricante que mencione su código exacto. "
                "Abajo quedan las referencias registradas y el motivo por el que no se usan para comparar.")
    highlights = ', '.join(f"{escape(s.name.lower())} {escape(s.original_value)}" for s in backed[:2])
    docs = len({s.source_url for s in backed})
    return (f"{name}: {highlights}. {len(backed)} {'dato localizado' if len(backed) == 1 else 'datos localizados'} en "
            f"{docs} {'documento' if docs == 1 else 'documentos'} del fabricante, con el texto exacto y la fecha de consulta. "
            f"Alimentación registrada: {escape(tool.power_badge_text)}.")


def render_tool_detail_page(tool: TechnicalTool) -> str:
    """Renderiza la ficha técnica completa de un modelo con todas sus especificaciones y trazabilidad."""
    specs_rows = []
    reference_rows = []
    for s in tool.specifications:
        norm_val_str = f"{s.normalized_value:g} {s.normalized_unit}" if s.normalized_value is not None and s.documentary_status == 'concordancia_textual' else "—"
        source_url = s.source_url + ('#page=' + s.source_page.split(',')[0].strip() if s.source_page and source_record(s.source_url).get('format') == 'pdf' else '')
        record = source_record(s.source_url) if s.source_url else {}
        source_label = _evidence_source_label(s, record)
        source_link = f'<a href="{escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(source_label)}</a>' if s.source_url and not _source_is_dead(record) else escape(source_label)
        if record.get('format') == 'pdf':
            page_str = ('PDF, pág. ' + escape(s.source_page)) if s.source_page else 'PDF, página no identificada'
        elif record.get('status') == 'recuperado':
            page_str = 'página web'
        else:
            page_str = 'fuente no disponible'
        date_str = f"({escape(s.consultation_date)})" if s.consultation_date else ""
        proof_labels = {'concordancia_textual': 'Dato encontrado en la fuente', 'sin_respaldo': 'No encontrado en la fuente', 'identidad_no_coincidente': 'La fuente no menciona este código', 'referencia_comercial': 'Solo figura en un comercio'}
        proof = proof_labels.get(s.documentary_status, 'Referencia de la carga documental')
        proof_html = f'<small style="display:block;margin-top:.4rem">{escape(proof)}</small>'
        if s.documentary_status == 'concordancia_textual':
            condition_note = _CONDITION_NOTES.get(s.condition_status, '')
            proof_html += f'<details><summary>Ver texto localizado</summary><p>Texto en la fuente: <code>{escape(s.evidence_excerpt)}</code></p>{f"<p>{escape(condition_note)}</p>" if condition_note else ""}</details>'

        destination = specs_rows if s.documentary_status == 'concordancia_textual' else reference_rows
        destination.append(f"""
        <tr>
          <td class="tl-cell-spec">{escape(s.name)}</td>
          <td class="tl-cell-val" data-label="Valor">{escape(s.original_value)}</td>
          <td class="tl-cell-val" data-label="Normalizado">{escape(norm_val_str)}</td>
          <td class="tl-cell-cond" data-label="Condición">{escape(s.measurement_condition)}</td>
          <td class="tl-cell-src" data-label="Fuente">{source_link} · {page_str} {date_str}{proof_html}</td>
          <td data-label="Estado">{_status_badge(s.status)}</td>
        </tr>
        """)

    # Bloque de variantes regionales
    variants_rows = []
    for v in tool.regional_variants:
        if v.is_cordless:
            vf_text = escape(v.voltage)
        elif v.is_combustion:
            vf_text = "Combustión interna"
        else:
            vf_text = f"{escape(v.voltage)} ~ {escape(v.frequency)}" if v.frequency else escape(v.voltage)

        motor_display = escape(v.motor_type) if v.motor_type else '<span style="color:#64748b;">—</span>'

        variants_rows.append(f"""
        <tr>
          <td style="font-weight:700;">{escape(v.variant_code)}</td>
          <td>{escape(v.market)}</td>
          <td>{vf_text}</td>
          <td>{escape(v.plug_type or 'No documentado')}</td>
          <td>{motor_display}</td>
        </tr>
        """)

    # Bloque de kits
    kits_rows = []
    for k in tool.kits:
        batt_str = f"{k.battery_capacity or 'Batería incluida'}" if k.includes_battery else "Sin batería (bare tool)"
        if k.battery_included.lower() == "no aplica":
            batt_str = "No aplica"
        charg_str = f"{k.charger_model or 'Cargador incluido'}" if k.includes_charger else "Sin cargador"
        if k.charger_included.lower() == "no aplica":
            charg_str = "No aplica"
        acc_str = ", ".join(k.accessories) if isinstance(k.accessories, list) else str(k.accessories or 'Accesorios de fábrica')
        kits_rows.append(f"""
        <tr>
          <td style="font-weight:700;">{escape(k.kit_name)}</td>
          <td>{escape(batt_str)}</td>
          <td>{escape(charg_str)}</td>
          <td>{escape(acc_str)}</td>
        </tr>
        """)

    # Bloque de ofertas observadas
    offers_box = ""
    offer = latest_verified_offer(tool)
    if offer:
        offers_box = f"""
        <div class="tl-offer-box">
          <div style="font-size:0.8rem; font-weight:700; color:#94a3b8; text-transform:uppercase;">Condición comercial observada</div>
          <div class="tl-offer-price">${offer.observed_price_ars:,.0f} {escape(offer.currency)}</div>
          <div class="tl-offer-meta">
            Canal: <strong>{escape(offer.channel)}</strong> · Vendedor: {escape(offer.seller_name or 'Comercio')} · Observado: {escape(offer.observation_date)}<br>
            Kit cotizado: <em>{escape(offer.kit_quoted)}</em> · Stock detectado: {escape(offer.availability)}<br>
            <span style="color:#f59e0b;">* Último precio observado para referencia de mercado. TallerLab no vende herramientas ni garantiza stock ni vigencia de precios en plataformas de terceros.</span>
          </div>
        </div>
        """

    elif tool.offers:
        offers_box = '<div class="tl-info-box">TallerLab no vende herramientas: confirmá precio, stock y contenido del kit con el vendedor.</div>'

    # Bloque de contradicciones
    contradictions_html = ""
    if tool.contradictions:
        contradiction_items = []
        for c in tool.contradictions:
            contradiction_items.append(f"""
            <div class="tl-alert-box">
              <div class="tl-alert-title">⚠️ Discrepancia Documentada: {escape(c.spec_name)}</div>
              <div class="tl-alert-text">
                <strong>Fuente A:</strong> {escape(c.source_a_name)} ({escape(c.source_a_date or '')}) declaró <code>{escape(c.source_a_value)}</code>.<br>
                <strong>Fuente B:</strong> {escape(c.source_b_name)} ({escape(c.source_b_date or '')}) declaró <code>{escape(c.source_b_value)}</code>.<br>
                <strong>Análisis técnico:</strong> {escape(c.analysis_notes)}
              </div>
            </div>
            """)
        contradictions_html = "".join(contradiction_items)

    # Bloque de límites y advertencias
    warnings_html = ""
    if tool.operational_limits or tool.cautions:
        limits_text = escape(tool.operational_limits) if tool.operational_limits else ""
        cautions_text = escape(tool.cautions) if tool.cautions else ""
        warnings_html = f"""
        <div class="tl-info-box">
          <strong>Antes de comprar:</strong> confirmá código, tensión y contenido del kit en la placa o el manual de la unidad que te ofrecen. Son datos declarados por el fabricante; TallerLab no ensaya herramientas.
          {f'<br><strong>Precauciones de uso:</strong> {cautions_text}' if cautions_text else ''}
        </div>
        """

    sources_html = ""
    if tool.primary_sources:
        links = []
        for source in tool.primary_sources:
            url = source.get("url", "")
            label = source.get("label", "Documento")
            kind = source_type_for(url, label, source.get("type"))
            record = source_record(url)
            if kind == 'referencia_externa' and record.get('format') == 'pdf':
                kind = 'documento_en_tercero'
            status = 'Documento recuperado' if record.get('status') == 'recuperado' else 'Referencia no recuperable en esta edición'
            checked = record.get('checked_at', '')[:10]
            publisher = f' · <a href="{escape(record["publisher_url"], quote=True)}">Página que enlaza el documento</a>' if record.get('publisher_url') else ''
            anchor = escape(label) if _source_is_dead(record) else f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'
            if 'retirada' in record.get('reason', ''):
                status = 'La página ya no muestra este producto (redirige al listado general)'
            elif _source_is_dead(record):
                status = f'Enlace no disponible (HTTP {escape(str(record.get("http_status")))})'
            elif record.get('reason', '').startswith('PDF sin texto'):
                status = 'PDF escaneado: sin texto verificable automáticamente'
            fingerprint = f' <details class="tl-hash"><summary>Huella del texto consultado</summary><code>{escape(record["text_sha256"])}</code></details>' if record.get('text_sha256') and record.get('status') == 'recuperado' else ''
            links.append(f'<li>{anchor} · {escape(kind.replace("_", " "))} · {status} {escape(checked)}{publisher}{fingerprint}</li>')
        sources_html = '<div class="tl-card"><h2 class="tl-card-title">Documentación y fuentes</h2><ul>' + "".join(links) + '</ul></div>'

    return f"""
    {TALLERLAB_DATA_CSS}
    <div class="tl-container">
      <header class="tl-hero">
        <span class="tl-kicker">FICHA TÉCNICA · {escape(tool.category.upper())}</span>
        <h1>{escape(tool.brand)} {escape(tool.model_name)}</h1>
        {f'<a href="#tl-commercial-options" class="tl-nav-pill">Ver publicación comercial (afiliado)</a>' if affiliate_for(tool) else ''}
        <p class="lead">{_detail_lead(tool)}</p>
        <p class="tl-byline">Revisado por <a href="{AUTHOR_PATH}" rel="author">{AUTHOR_NAME}</a> · Fuentes consultadas el <time datetime="{escape(_sources_checked(tool))}">{escape(_human_date(_sources_checked(tool)))}</time> · <a href="/contacto/">Reportar un error</a></p>

        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem;">
          <span class="{tool.power_badge_css}">{escape(tool.power_badge_text)}</span>
          {f'<span class="tl-badge tl-badge-declarado">Código: {escape(tool.mpn)}</span>' if tool.mpn else ''}
        </div>

        <nav class="tl-nav-pills" aria-label="Acciones de la ficha técnica">
          <a href="/herramientas/comparar/?m1={tool.slug}" class="tl-nav-pill">⚖️ Comparar este modelo</a>
          <a href="/herramientas/" class="tl-nav-pill">← Volver al catálogo ({escape(tool.category.capitalize())})</a>
          <a href="/herramientas/metodologia/" class="tl-nav-pill">📖 Criterios de verificación</a>
        </nav>
      </header>

      {_retired_notice(tool)}
      {contradictions_html}

{_specs_section(tool, specs_rows) if specs_rows else ''}

      {warnings_html}

      {'' if not reference_rows else f'''<details class="tl-card"><summary>Datos sin fuente comprobada ({len(reference_rows)})</summary>
      <p>Figuran en publicaciones o en la carga original, pero no los encontramos en un documento oficial con este código. Se muestran por transparencia y no se usan para comparar.</p>
      <div class="tl-table-wrap"><table class="tl-table"><thead><tr><th>Dato</th><th>Valor publicado</th><th>Normalizado</th><th>Condición</th><th>Fuente y motivo</th><th>Tipo</th></tr></thead><tbody>{''.join(reference_rows)}</tbody></table></div></details>'''}

      {f'''
      <section class="tl-card">
        <div class="tl-card-header">
          <div>
            <h2 class="tl-card-title">Referencias de variantes y alimentación</h2>
            <p class="tl-card-desc">Versión registrada para el mercado argentino. Confirmá tensión y enchufe en la placa del equipo.</p>
          </div>
        </div>
        <div class="tl-table-wrap">
          <table class="tl-table">
            <thead>
              <tr>
                <th>Código Variante</th>
                <th>Mercado</th>
                <th>Tensión / Frecuencia</th>
                <th>Ficha Eléctrica</th>
                <th>Tipo de Motor</th>
              </tr>
            </thead>
            <tbody>
              {"".join(variants_rows)}
            </tbody>
          </table>
        </div>
      </section>
      ''' if variants_rows else ''}

      {f'''
      <section class="tl-card">
        <div class="tl-card-header">
          <div>
            <h2 class="tl-card-title">Kits y Configuraciones Comerciales</h2>
            <p class="tl-card-desc">Contenido habitual según el catálogo; puede variar según el vendedor.</p>
          </div>
        </div>
        <div class="tl-table-wrap">
          <table class="tl-table">
            <thead>
              <tr>
                <th>Configuración</th>
                <th>Batería</th>
                <th>Cargador</th>
                <th>Accesorios Incluidos</th>
              </tr>
            </thead>
            <tbody>
              {"".join(kits_rows)}
            </tbody>
          </table>
        </div>
      </section>
      ''' if kits_rows else ''}

      {sources_html}
      {offers_box}
      {render_decision_guidance([tool])}
      {render_affiliate_options([tool])}
      {render_model_community(tool)}
    </div>
    """


def render_tool_comparator_page(selected_slugs: Optional[List[str]] = None, category: Optional[str] = None, segment: Optional[str] = None) -> str:
    """Renderiza el comparador técnico interactivo y multi-modelo."""
    all_tools = sorted(get_all_tools(), key=documentary_order)
    tools_by_slug = {t.slug: t for t in all_tools}

    # Preservar selección de modelos (m1 persistente si se especifica 1 modelo)
    category = category if category in get_all_categories() else None
    valid_selected = list(dict.fromkeys(s for s in (selected_slugs or []) if s in tools_by_slug and (not category or tools_by_slug[s].category == category)))
    if len(valid_selected) == 1:
        s1 = valid_selected[0]
        cat1 = tools_by_slug[s1].category
        peers = [t.slug for t in all_tools if t.category == cat1 and family(t) == family(tools_by_slug[s1]) and t.slug != s1]
        s2 = peers[0] if peers else ''
        slugs = [s1, s2]
    elif len(valid_selected) >= 2:
        slugs = valid_selected[:4]
    else:
        choices = [t for t in all_tools if t.category == category] if category else [t for t in all_tools if t.category == 'compresores']
        valid_families = {family(t) for t in choices}
        default_family = {'compresores': 'compresor-tanque', 'taladros': 'taladro', 'amoladoras': 'amoladora-angular'}.get(category or 'compresores', family(choices[0]))
        selected_family = segment if segment in valid_families else default_family
        slugs = [t.slug for t in choices if family(t) == selected_family][:2]
        if len(slugs) == 1:
            slugs.append('')

    comparison = compare_tools(slugs)
    compared_tools = comparison.tools

    # Construcción de la matriz
    headers_html = ['<div class="tl-matrix-col-header" style="font-weight:800; color:#94a3b8; text-align:left;">Parámetro / Modelo</div>']
    for t in compared_tools:
        headers_html.append(f"""
        <div class="tl-matrix-col-header">
          <div style="font-size:0.75rem; font-weight:800; color:#ff7733; text-transform:uppercase;">{escape(t.brand)}</div>
          <div style="font-size:1.1rem; font-weight:800; color:#ffffff; margin:0.2rem 0;"><a href="/herramientas/{t.slug}/">{escape(t.model_name)}</a></div>
          <div style="font-size:0.75rem; color:#94a3b8;">{escape(family_label(t))}</div>
          <div style="margin-top:0.4rem;"><span class="{t.power_badge_css}">{escape(t.power_badge_text)}</span></div>
        </div>
        """)

    matrix_rows = []
    for row in comparison.rows:
        matrix_rows.append(f'<div class="tl-matrix-row-label">{escape(row.spec_name)}</div>')
        for slug in slugs:
            cell = row.cells.get(slug)
            if not cell:
                matrix_rows.append('<div class="tl-matrix-cell" style="color:#64748b;">No informado</div>')
                continue

            warning_html = ""
            if cell.incomparability_warning:
                warning_html = f'<div class="tl-matrix-warning">⚠️ {escape(cell.incomparability_warning)}</div>'

            val_str = cell.original_value
            normalized_html = f'<small>Normalizado: {cell.normalized_value:g} {escape(cell.normalized_unit)}</small>' if cell.normalized_value is not None and row.is_comparable else ''
            cond_str = f'<div style="font-size:0.75rem; color:#94a3b8; margin-top:0.25rem;">Condición: {escape(cell.condition)}</div>' if cell.condition else ''

            matrix_rows.append(f"""
            <div class="tl-matrix-cell">
              <div style="font-weight:700; color:#38bdf8;">{escape(val_str)}</div>
              {normalized_html}
              {cond_str}
              <div style="margin-top:0.25rem;">{_status_badge(cell.status)}</div>
              {warning_html}
            </div>
            """)

    # Selector de opciones para cambiar modelos dentro del segmento o categoría
    comp_category = tools_by_slug[slugs[0]].category if slugs and slugs[0] in tools_by_slug else None

    select_options = "".join('<optgroup label="' + escape(cat.title()) + '">' + ''.join(f'<option value="{t.slug}">{escape(t.brand)} {escape(t.model_name)}</option>' for t in all_tools if t.category == cat) + '</optgroup>' for cat in ([comp_category] if comp_category else get_all_categories()))
    category_links = ''.join(f'<a class="tl-nav-pill" href="/herramientas/comparar/?categoria={escape(cat)}"'+(' aria-current="page"' if cat == comp_category else '')+f'>{escape(cat.title())}</a>' for cat in get_all_categories())
    family_links = ''.join(f'<a class="tl-nav-pill" href="/herramientas/comparar/?categoria={comp_category}&amp;familia={key}">{escape(LABELS.get(key, key.title()))}</a>' for key in sorted({family(t) for t in all_tools if t.category == comp_category}))
    comparable_count = sum(row.is_comparable for row in comparison.rows)
    summary_html = f'<section class="tl-card"><h2>Qué permite concluir esta selección</h2><p>{comparable_count} de {len(comparison.rows)} parámetros permiten una comparación numérica bajo las condiciones registradas. Los demás se muestran con su motivo de exclusión. Una cifra mayor no acredita mejor rendimiento.</p><p>Para elegir, comprobá primero aplicación, alimentación y código del kit. Después usá los parámetros comparables; las referencias sin respaldo no deciden la recomendación.</p></section>'

    extra_selectors = ""
    for index in (2, 3):
        selected = slugs[index] if len(slugs) > index else ""
        options = '<option value="">Sin modelo adicional</option>' + select_options
        if selected:
            options = options.replace(f'value="{selected}"', f'value="{selected}" selected')
        extra_selectors += f'<div style="flex:1; min-width:220px;"><label for="m{index+1}">Modelo {index+1} (opcional)</label><select class="tl-select" name="m{index+1}" id="m{index+1}">{options}</select></div>'

    return f"""
    {TALLERLAB_DATA_CSS}
    <div class="tl-container">
      <header class="tl-hero">
        <span class="tl-kicker">COMPARADOR TÉCNICO MULTI-MODELO</span>
        <h1>Comparador de Herramientas en Argentina</h1>
        <p class="lead">Contrastá especificaciones normalizadas lado a lado con detección activa de condiciones de ensayo no comparables (ej. caudal desplazado vs FAD efectivo a 7 bar, o presión de alivio vs trabajo continuo).</p>

        <nav class="tl-nav-pills" aria-label="Navegación del comparador">
          <a href="/herramientas/comparaciones/" class="tl-nav-pill">📋 Ver comparativas editoriales curadas</a>
          <a href="/herramientas/" class="tl-nav-pill">← Volver al catálogo general</a>
          <a href="/herramientas/investigacion/brecha-especificaciones-argentina/" class="tl-nav-pill">📊 Ver cobertura documental</a>
        </nav>
      </header>

      <section class="tl-card">
        <div class="tl-card-header">
          <div>
            <h2 class="tl-card-title">Selección de Modelos a Comparar</h2>
            <p class="tl-card-desc">Seleccioná entre los {len(all_tools)} modelos del catálogo. Elegí una categoría para comenzar:</p>
          </div>
        </div>

        <nav class="tl-nav-pills" aria-label="Categoría de comparación">{category_links}</nav>
        <nav class="tl-nav-pills" aria-label="Familia de comparación">{family_links}</nav>
        <form method="GET" action="/herramientas/comparar/" style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end;">
          <div style="flex: 1; min-width: 220px;">
            <label for="m1" style="font-size: 0.8rem; font-weight: 700; color: #94a3b8; display: block; margin-bottom: 0.35rem;">Modelo 1</label>
            <select name="m1" id="m1" class="tl-select" style="width: 100%;">
              <option value="">Elegir modelo</option>
              {select_options.replace(f'value="{slugs[0]}"', f'value="{slugs[0]}" selected')}
            </select>
          </div>
          <div style="flex: 1; min-width: 220px;">
            <label for="m2" style="font-size: 0.8rem; font-weight: 700; color: #94a3b8; display: block; margin-bottom: 0.35rem;">Modelo 2</label>
            <select name="m2" id="m2" class="tl-select" style="width: 100%;">
              <option value=""{' selected' if not slugs[1] else ''}>Elegir segundo modelo</option>
              {select_options.replace(f'value="{slugs[1]}"', f'value="{slugs[1]}" selected')}
            </select>
          </div>
          {extra_selectors}
          <button type="submit" class="tl-nav-pill" style="cursor: pointer; padding: 0.75rem 1.25rem; background: #ff5500; border-color: #ff5500; color: #fff;">Actualizar Comparación</button>
        </form>
      </section>

      {f'''
      <div class="tl-alert-box" style="background: rgba(245, 158, 11, 0.1); border-left-color: #f59e0b; margin-bottom: 1.5rem;">
        <div class="tl-alert-title" style="color: #fbbf24;">⚠️ Categorías Diferentes en Comparación</div>
        <div class="tl-alert-text">
          {escape(comparison.category_warning)}
        </div>
      </div>
      ''' if getattr(comparison, 'category_mismatch', False) else ''}

      <div class="tl-alert-box">
        <div class="tl-alert-title">⚖️ Criterio de Comparabilidad Técnica de TallerLab</div>
        <div class="tl-alert-text">
          No declaramos ganadores sintéticos basados en cifras brutas de folletos comerciales. Si dos modelos miden el caudal o la presión en condiciones físicas dispares, la celda incluye una advertencia explícita para evitar decisiones basadas en datos engañosos.
        </div>
      </div>

      {summary_html}
      {'<div class="tl-alert-box"><strong>Aplicaciones distintas en esta selección</strong><p>Se muestran las referencias de las familias elegidas, pero sus mecanismos o configuraciones no permiten establecer equivalencias numéricas. Elegí modelos de la misma familia para una comparación técnica pertinente.</p></div>' if len({family(t) for t in compared_tools}) > 1 else ''}
      {'<div class="tl-info-box">Esta familia tiene un solo modelo en el catálogo. Podés consultar su ficha; elegí otro modelo para construir una comparación. Las familias distintas no permiten equivalencia numérica.</div>' if len(compared_tools) == 1 else ''}
      {render_decision_guidance(compared_tools, comparison) if compared_tools else ''}
      {render_affiliate_options(compared_tools)}
      <section class="tl-card">
        <div class="tl-card-header">
            <h2 class="tl-card-title">Matriz documental y condiciones de comparación</h2>
        </div>

        <div class="tl-table-wrap" tabindex="0" role="region" aria-label="Matriz técnica; desplazamiento horizontal"><div class="tl-comparator-matrix" style="grid-template-columns: 180px repeat({len(compared_tools)}, minmax(220px, 1fr)); min-width:{180 + 220*len(compared_tools)}px;">
          {"".join(headers_html)}
          {"".join(matrix_rows)}
        </div></div>
      </section>
    </div>
    """


def render_editorial_comparisons_list_page() -> str:
    """Renderiza el índice de las 6 comparativas editoriales curadas."""
    comparisons = get_all_editorial_comparisons()

    cards_html = []
    for c in comparisons:
        cards_html.append(f"""
        <article class="tl-tool-card" style="margin-bottom: 1.25rem;">
          <div class="tl-card-header" style="border: none; padding: 0; margin-bottom: 0.75rem;">
            <div>
              <span class="tl-kicker">{escape(c.category.upper())}</span>
              <h2 class="tl-card-title" style="font-size: 1.3rem;"><a href="/herramientas/comparar/{c.slug}/">{escape(c.title)}</a></h2>
            </div>
            <span class="tl-badge tl-badge-medido">Editorial TallerLab</span>
          </div>
          <p style="font-size: 0.9rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1rem;">Valores declarados, fuentes y condiciones de los dos modelos.</p>
          <div class="tl-tool-footer">
            <span style="font-size: 0.8rem; color: #cbd5e1;"><strong>Modelos:</strong> {escape(c.model_a_slug)} vs {escape(c.model_b_slug)}</span>
            <a href="/herramientas/comparar/{c.slug}/" class="tl-btn-detail">Leer comparativa completa →</a>
          </div>
        </article>
        """)

    return f"""
    {TALLERLAB_DATA_CSS}
    <div class="tl-container">
      <header class="tl-hero">
        <span class="tl-kicker">COMPARACIONES DEL CATÁLOGO</span>
        <h1>Comparativas Técnicas de Herramientas Documentadas</h1>
        <p class="lead">Consultá valores declarados y fuentes de cada modelo, con avisos de datos ausentes, contradictorios o no comparables.</p>

        <nav class="tl-nav-pills" aria-label="Navegación de comparativas curadas">
          <a href="/herramientas/comparar/" class="tl-nav-pill">⚖️ Comparador Libre Multi-Modelo</a>
          <a href="/herramientas/" class="tl-nav-pill">← Volver al catálogo de 100 modelos</a>
          <a href="/herramientas/metodologia/" class="tl-nav-pill">📖 Metodología y Fuentes</a>
        </nav>
      </header>

      <section class="tl-card">
        <div class="tl-card-header">
          <h2 class="tl-card-title">Pares de Comparación Analizados ({len(comparisons)})</h2>
        </div>
        <div style="display: flex; flex-direction: column; gap: 1rem;">
          {"".join(cards_html)}
        </div>
      </section>
    </div>
    """


def render_editorial_comparison_page(slug: str) -> str:
    """Renderiza la vista en profundidad de una comparativa editorial curada."""
    comparison = get_editorial_comparison(slug)
    if not comparison:
        return '<div class="tl-container"><h1>Comparativa no encontrada</h1><p><a href="/herramientas/comparaciones/">Volver</a></p></div>'

    tool_a = get_tool_by_slug(comparison.model_a_slug)
    tool_b = get_tool_by_slug(comparison.model_b_slug)
    name_a = f"{tool_a.brand} {tool_a.model_name}" if tool_a else comparison.model_a_slug
    name_b = f"{tool_b.brand} {tool_b.model_name}" if tool_b else comparison.model_b_slug

    result = compare_tools([tool_a, tool_b])
    rows = []
    for row in result.rows:
        cells = []
        for tool in result.tools:
            spec = tool.specs.get(row.key)
            if not spec:
                cells.append("<td>No cargado</td>")
                continue
            cells.append(f'<td>{escape(spec.raw_value)}<br><small>{escape(spec.condition)}</small><br>{escape(evidence_source_label(spec)) if _source_is_dead(source_record(spec.source_url)) else f'<a href="{escape(spec.source_url, quote=True)}" rel="noopener noreferrer">{escape(evidence_source_label(spec))}</a>'}</td>')
        rows.append(f'<tr><th>{escape(row.name)}</th>{"".join(cells)}<td>{escape(row.warning or "Valores declarados en la misma unidad; revisar variante y condiciones.")}</td></tr>')
    category_advice = {
        'compresores': 'Para elegir un compresor, buscá entrega de aire a la presión requerida. El volumen del tanque describe reserva; el caudal aspirado no demuestra reposición efectiva ni funcionamiento continuo.',
        'hidrolavadoras': 'Para elegir una hidrolavadora, distinguí presión de trabajo, presión máxima y caudal nominal. La presión máxima de una ficha no prueba velocidad de limpieza ni rendimiento sostenido.',
        'soldadoras': 'Para elegir una soldadora, compará el proceso de unión y el ciclo de trabajo bajo el mismo método y temperatura declarados. La corriente máxima no equivale a corriente continua.',
        'generadores': 'Para elegir un generador, distinguí potencia nominal y máxima, kW y kVA. La palabra inverter no acredita por sí sola un valor de distorsión ni compatibilidad con cualquier equipo.',
    }
    advice = category_advice.get(comparison.category, 'Usá las cifras con condiciones equivalentes y revisá alimentación, mecanismo y configuración. Las especificaciones declaradas no prueban durabilidad ni desempeño real.')
    analysis_rendered = '<p>' + escape(advice) + '</p><p>La tabla documenta qué equivalencias se pueden establecer y qué referencias se excluyen. TallerLab no realiza ensayos ni declara ganadores por cifras aisladas.</p><div class="tl-table-wrap"><table class="tl-table"><thead><tr><th>Parámetro</th><th>' + escape(name_a) + '</th><th>' + escape(name_b) + '</th><th>Comparabilidad</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


    return f"""
    {TALLERLAB_DATA_CSS}
    <div class="tl-container">
      <header class="tl-hero">
        <span class="tl-kicker">COMPARATIVA TÉCNICA CURADA · {escape(comparison.category.upper())}</span>
        <h1>{escape(comparison.title)}</h1>
        <p class="lead">Comparación de especificaciones registradas, fuentes y condiciones. Consultá las fichas para confirmar variante y kit.</p>

        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem;">
          <a href="/herramientas/{comparison.model_a_slug}/" class="tl-nav-pill">Ficha {escape(name_a)}</a>
          <a href="/herramientas/{comparison.model_b_slug}/" class="tl-nav-pill">Ficha {escape(name_b)}</a>
          <a href="/herramientas/comparar/?m1={comparison.model_a_slug}&m2={comparison.model_b_slug}" class="tl-nav-pill">Ver en Matriz Dinámica ⚖️</a>
        </div>
      </header>

      <section class="tl-card">
        <div class="tl-card-header">
          <h2 class="tl-card-title">Análisis Documental y Comparabilidad Técnica</h2>
        </div>
        <div class="markdown-body" style="font-size: 0.95rem; line-height: 1.7; color: #cbd5e1;">
          {analysis_rendered}
        </div>
      </section>

      <div class="tl-alert-box" style="background: rgba(16, 185, 129, 0.08); border-left-color: #10b981;">
        <div class="tl-alert-title" style="color: #34d399;">🏁 Principio de Comparabilidad TallerLab</div>
        <div class="tl-alert-text">
          La comparación muestra valores declarados con sus fuentes. Datos similares no prueban igual rendimiento; verificá las condiciones y la variante antes de decidir.
        </div>
      </div>
      {render_decision_guidance(result.tools, result) if result.tools else ''}
      {render_affiliate_options(result.tools)}

      <div style="margin-top: 2rem; display: flex; gap: 1rem;">
        <a href="/herramientas/comparaciones/" class="tl-nav-pill">← Ver todas las comparativas curadas</a>
        <a href="/herramientas/" class="tl-nav-pill">Ir al catálogo de herramientas</a>
      </div>
    </div>
    """


def render_data_methodology_page() -> str:
    candidates = list_candidates()
    rows = "".join(f"<tr><td>{escape(str(c.get('brand', '')))}</td><td>{escape(str(c.get('model_name', '')))}</td><td>{escape(str(c.get('status', 'excluido')))}</td><td>{escape(str(c.get('rejection_or_pending_reason', 'Sin documentación suficiente para este catálogo')))}</td></tr>" for c in candidates)
    return f"""{TALLERLAB_DATA_CSS}<div class="tl-container">
      <header class="tl-hero"><h1>Metodología y estado de los datos de TallerLab</h1>
      <p class="lead">Investigación de documentación técnica para decisiones de compra en Argentina. TallerLab no realiza mediciones ni ensayos de herramientas.</p>
      <p>Responsable editorial: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a> · <a href="/herramientas/correcciones/">Historial de correcciones</a> · <a href="/contacto/">Reportar una discrepancia documental</a></p></header>
      <section class="tl-card"><h2>Procedencia y alcance</h2>
      <p>Registramos valor original, unidad, condición, variante, mercado, fuente y estado. Distinguimos documentación de marca, documentos alojados por terceros y referencias comerciales. El tipo de fuente se determina por el dominio; un comercio no se convierte en fabricante por el título del enlace.</p>
      <p>La edición conserva un inventario fechado de fuentes recuperadas, con huella SHA-256. La concordancia textual exige localizar el código de producto en el contenido y el valor junto a su unidad. Es una comprobación de texto, no una certificación de exactitud técnica. Si el código, el valor o el documento no se recupera, la referencia queda excluida de conclusiones cuantitativas; no se presupone válida.</p>
      <p>Una página web sin paginación no recibe un número de página inventado. Las fechas antiguas son metadata de la carga inicial; la fecha del inventario acredita recuperación del documento. La coincidencia con el modelo no garantiza que todos los kits, mercados o condiciones sean equivalentes.</p></section>
      <section class="tl-card"><h2>Estados y comparaciones</h2>
      <p>Declarado: transcripción atribuida a una fuente; consultar su respaldo. Calculado: conversión de unidades con factores explícitos (HP a W: 745,7; CV a W: 735,49875; CFM a L/min: 28,3168). Contradictorio: valores divergentes registrados, sin elegir uno por suposición. No encontrado: dato ausente de esta observación. Esta edición no contiene mediciones de TallerLab.</p>
      <p>Los rangos y múltiples condiciones conservan su texto original. Torque duro, blando y de impacto no se mezclan; aspiración no equivale a entrega, ni caudal a distinta presión de ensayo. Peso requiere configuración equivalente y ruido requiere la misma magnitud y contexto. Cuando no se establece equivalencia, se muestra el motivo sin producir un ganador.</p></section>
      <section class="tl-card"><h2>Independencia y alcance de la edición</h2>
      <p>El catálogo técnico es una edición documental con seis categorías. No es una medición de rendimiento, certificación de seguridad, prueba de durabilidad ni una cotización en tiempo real. Las observaciones comerciales sin captura se archivan y no se publican como precios actuales.</p>
      <p>Los enlaces comerciales pueden ser afiliados en fichas, comparaciones y guías de compra, siempre identificados. La comisión no modifica el orden documental ni las reglas del comparador, y no convierte una oferta en evidencia técnica. Fuentes de otros mercados no acreditan una variante argentina. Las exclusiones son decisiones editoriales cerradas para esta edición, con su motivo documentado.</p></section>
      <section class="tl-card"><h2>Reproducibilidad y correcciones</h2><p>El CSV publica una observación por fila; el JSON conserva estructura y versión. Los registros de fuente permiten reconstruir el estado documental. El catálogo se publica desde un snapshot versionado: una actualización cambia la versión y conserva las correcciones.</p>
      <a class="tl-nav-pill" href="/herramientas/investigacion/descargar-datos.csv">Dataset CSV</a><a class="tl-nav-pill" href="/herramientas/investigacion/descargar-datos.json">Dataset JSON</a><a class="tl-nav-pill" href="/herramientas/investigacion/fuentes.json">Inventario de fuentes</a>
      <p>Podés citar: TallerLab Data, catálogo documental de herramientas, edición octubre de 2026; indicá URL, versión del dataset y fecha de acceso. La licencia CC BY 4.0 corresponde a nuestra compilación y análisis; los documentos de fabricantes conservan sus derechos.</p></section>
      <section class="tl-card"><h2>Decisiones de exclusión e incorporación</h2>
      <div class="tl-table-wrap"><table class="tl-table"><thead><tr><th>Marca</th><th>Modelo</th><th>Decisión</th><th>Motivo documental</th></tr></thead><tbody>{rows}</tbody></table></div></section>
    </div>"""


def render_corrections_log_page() -> str:
    """Renderiza el registro público de correcciones técnicas."""
    corrections = list_corrections()

    rows = []
    for c in corrections:
        date_val = getattr(c, "date", None) or (c.get("correction_date") if isinstance(c, dict) else "") or ""
        tool_val = getattr(c, "tool_slug", None) or (c.get("tool_slug") if isinstance(c, dict) else "") or ""
        spec_val = getattr(c, "spec_name", None) or (c.get("field_affected") if isinstance(c, dict) else "") or ""
        prev_val = getattr(c, "previous_value", None) or (c.get("old_value") if isinstance(c, dict) else "") or ""
        corr_val = getattr(c, "corrected_value", None) or (c.get("new_value") if isinstance(c, dict) else "") or ""
        reason_val = getattr(c, "reason", None) or (c.get("reason") if isinstance(c, dict) else "") or ""
        source_val = getattr(c, "source_citation", None) or (c.get("source") if isinstance(c, dict) else "") or ""
        rows.append(f"""
        <tr>
          <td style="white-space:nowrap; font-weight:700;">{escape(str(date_val))}</td>
          <td style="font-weight:700; color:#38bdf8;">{escape(str(tool_val))}</td>
          <td>{escape(str(spec_val))}</td>
          <td style="color:#f87171; text-decoration:line-through;">{escape(str(prev_val))}</td>
          <td style="color:#34d399; font-weight:700;">{escape(str(corr_val))}</td>
          <td style="font-size:0.83rem; color:#cbd5e1;">{escape(str(reason_val))}</td>
          <td style="font-size:0.8rem; color:#94a3b8;">{escape(str(source_val))}</td>
        </tr>
        """)

    return f"""
    {TALLERLAB_DATA_CSS}
    <div class="tl-container">
      <header class="tl-hero">
        <span class="tl-kicker">COMPROMISO DE EXACTITUD Y TRANSPARENCIA</span>
        <h1>Registro Público de Correcciones Técnicas</h1>
        <p class="lead">Historial cronológico de erratas, enmiendas y actualizaciones en la base de datos TallerLab Data. Cuando un manual oficial se actualiza o detectamos un error en la transcripción, rectificamos públicamente el dato.</p>

        <nav class="tl-nav-pills" aria-label="Navegación del registro de correcciones">
          <a href="/herramientas/metodologia/" class="tl-nav-pill">📖 Metodología Documental</a>
          <a href="/contacto/" class="tl-nav-pill">✉️ Enviar un reporte o corrección técnica</a>
          <a href="/herramientas/" class="tl-nav-pill">← Volver al Catálogo</a>
        </nav>
      </header>

      <section class="tl-card">
        <div class="tl-card-header">
          <h2 class="tl-card-title">Historial de Correcciones Registradas ({len(corrections)})</h2>
        </div>

        <div class="tl-table-wrap">
          <table class="tl-table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Modelo</th>
                <th>Especificación</th>
                <th>Valor Anterior</th>
                <th>Valor Corregido</th>
                <th>Justificación Técnica</th>
                <th>Fuente Primaria Citada</th>
              </tr>
            </thead>
            <tbody>
              {"".join(rows)}
            </tbody>
          </table>
        </div>
      </section>

      <div class="tl-info-box">
        <strong>¿Detectaste una especificación desactualizada?</strong> Si tenés en tu poder el manual oficial o placa identificatoria de una herramienta con datos diferentes a los consignados en nuestra base, por favor envianos una fotografía nítida o el PDF oficial a través de nuestro <a href="/contacto/" style="color:#ff5500; text-decoration:underline;">canal de contacto</a>. Los reportes se incorporan a la revisión documental.
      </div>
    </div>
    """


def render_research_study_page() -> str:
    """Report database coverage without imputing omissions to manufacturers."""
    metrics = get_research_study_data()["metrics"]
    rows = [
        ("Compresores con caudal de salida registrado", metrics["compresores_fad_count"], metrics["compresores_total"]),
        ("Hidrolavadoras con presión de trabajo registrada", metrics["hidro_trabajo_separada_count"], metrics["hidro_total"]),
        ("Rotomartillos con energía declarada bajo EPTA", metrics["rotary_hammers_epta_count"], metrics["rotary_hammers_total"]),
        ("Modelos con discrepancias registradas", metrics["contradictions_count"], metrics["sample_size"]),
    ]
    table = "".join(f"<tr><td>{escape(label)}</td><td>{count}</td><td>{total}</td><td>{round(100*count/total,1) if total else 0}%</td></tr>" for label, count, total in rows)
    return f"""{TALLERLAB_DATA_CSS}
    <div class="tl-container"><article>
      <header class="tl-hero"><span class="tl-kicker">COBERTURA DOCUMENTAL TALLERLAB DATA</span>
      <h1>Cobertura de especificaciones en el catálogo argentino de TallerLab</h1>
      <p class="lead">{metrics['sample_size']} modelos y {metrics['total_specs_analyzed']} especificaciones registradas. Estos resultados describen nuestra base y cambian al incorporar documentación.</p></header>
      <section class="tl-card"><h2>Datos disponibles en la base</h2>
      <table class="tl-table"><thead><tr><th>Indicador</th><th>Con dato</th><th>Modelos</th><th>Porcentaje</th></tr></thead><tbody>{table}</tbody></table></section>
      <section class="tl-card"><h2>Cómo interpretar los resultados</h2>
      <p>Se cuenta un dato cuando hay un valor numérico finito, respaldo documental utilizable y estado declarado o calculado. Los datos no encontrados, contradictorios o excluidos por falta de respaldo no cuentan como disponibles.</p>
      <p>Una ausencia en este catálogo significa que no hay un dato utilizable cargado: no demuestra que el fabricante lo omita. La muestra es una selección editorial de modelos y no representa estadísticamente a todo el mercado argentino.</p>
      <p>EPTA indica el protocolo mencionado en la fuente para energía de impacto; no constituye una certificación independiente. El caudal de salida registrado tampoco acredita por sí solo un ensayo FAD normalizado. No atribuimos resultados de rendimiento ni mediciones propias a esta investigación.</p>
      <p>Los valores sin respaldo recuperable, las referencias comerciales y los códigos no coincidentes quedan fuera de los indicadores. El inventario distingue recuperación documental de concordancia textual. La edición conserva las exclusiones; no presenta una ausencia en la base como una omisión del fabricante.</p></section>
      <section class="tl-card"><h2>Datos para reproducir el cálculo</h2>
      <p>El CSV contiene una fila por especificación, con valor original, unidad, condición, variante, estado, fuente, respaldo documental y clasificación utilizada en los indicadores. Las cotizaciones sin evidencia se excluyen.</p>
      <p>Investigación editorial: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a>. Muestra editorial de seis categorías; ningún porcentaje se extrapola al mercado completo.</p>
      <a class="tl-nav-pill" href="/herramientas/investigacion/descargar-datos.json">Descargar edición JSON y versión</a>
      <a class="tl-nav-pill" href="/herramientas/investigacion/fuentes.json">Inventario fechado de fuentes</a>
      <a class="tl-nav-pill" href="/herramientas/investigacion/descargar-datos.csv">Descargar especificaciones y clasificaciones</a>
      <a class="tl-nav-pill" href="/herramientas/metodologia/">Consultar metodología</a></section>
    </article></div>"""


def get_tool_product_schema(tool: TechnicalTool, page_url: str) -> str:
    """Genera el schema JSON-LD Schema.org Product para una ficha de herramienta."""
    schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{tool.brand} {tool.model_name}",
        "model": tool.model_name,
        "brand": {
            "@type": "Brand",
            "name": tool.brand,
        },
        "category": tool.category,
        "url": page_url,
    }
    if tool.mpn:
        schema["mpn"] = tool.mpn
    backed = backed_specs(tool)
    if backed:
        props = []
        for s in backed:
            prop: Dict[str, Any] = {"@type": "PropertyValue", "name": s.name}
            if s.normalized_value is not None:
                prop["value"] = s.normalized_value
                if s.normalized_unit:
                    prop["unitText"] = s.normalized_unit
            else:
                prop["value"] = s.original_value
            props.append(prop)
        schema["additionalProperty"] = props

    off = latest_verified_offer(tool)
    if off:
        offer_dict = {"@type": "Offer", "priceCurrency": off.currency, "price": f"{off.observed_price_ars:.2f}",
                      "url": off.url, "seller": {"@type": "Organization", "name": off.seller_name}}
        availability = {"disponible": "InStock", "agotado": "OutOfStock", "preventa": "PreOrder"}.get(off.availability)
        if availability:
            offer_dict["availability"] = "https://schema.org/" + availability
        if off.valid_until:
            from datetime import date
            try:
                if date.fromisoformat(off.valid_until) >= date.today():
                    offer_dict["priceValidUntil"] = off.valid_until
            except ValueError:
                pass
        schema["offers"] = offer_dict

    # Opiniones publicadas en la comunidad y visibles en esta ficha (Review / AggregateRating).
    try:
        from comunidad.components import product_review_markup
        schema.update(product_review_markup(tool.slug))
    except Exception:
        pass
    return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>'


def get_tool_page_schema(tool: TechnicalTool, page_url: str) -> str:
    """ItemPage with author, review date and the documents values were located in."""
    backed = backed_specs(tool)
    base = page_url.split("/herramientas/")[0]
    page: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "ItemPage",
        "url": page_url,
        "name": f"{tool.brand} {tool.model_name}: ficha técnica y fuentes",
        "inLanguage": "es-AR",
        "isPartOf": {"@type": "WebSite", "name": "TallerLab", "url": base + "/"},
        "publisher": {"@id": base + "/#organization"},
        "author": {"@type": "Person", "name": AUTHOR_NAME, "url": base + AUTHOR_PATH},
        "mainEntity": {"@type": "Product", "name": f"{tool.brand} {tool.model_name}", "url": page_url},
    }
    if tool.last_documented_date:
        page["dateModified"] = tool.last_documented_date
    citations = sorted({s.source_url for s in backed if s.source_url})
    if citations:
        page["citation"] = [{"@type": "CreativeWork", "url": url} for url in citations]

    return '<script type="application/ld+json">' + json.dumps(page, ensure_ascii=False).replace("<", "\\u003c") + '</script>'


def get_research_study_schema(study_url: str, csv_download_url: str) -> str:
    """Genera schemas Article y Dataset para la página de investigación documental."""
    dataset_schema = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Cobertura de especificaciones del catálogo TallerLab",
        "description": "Observaciones registradas, fuentes, condiciones, variantes y clasificaciones de cobertura de la base TallerLab.",
        "url": study_url,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "creator": {
            "@type": "Person",
            "name": "Joaquín Vallasciani",
            "url": "https://www.tallerlab.com.ar/autor/joaquin-vallasciani/",
        },
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "text/csv",
                "contentUrl": csv_download_url,
            }
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(dataset_schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
