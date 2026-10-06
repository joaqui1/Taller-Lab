"""
Integración bidireccional entre guías editoriales existentes (paginas/) y TallerLab Data.
Mapea URLs de guías a fichas de modelos documentados y renderiza bloques enriquecidos.
"""

from __future__ import annotations

from html import escape
from typing import Dict, List, Optional

from tallerlab_data.models import TechnicalTool
from tallerlab_data.storage import get_tool_by_slug, get_tools_by_category

GUIDE_TOOL_MAPPINGS: Dict[str, List[str]] = {
    # Compresores
    "/compresores/50-litros/": [
        "lusqtoff-lc2550b-8",
        "gamma-g2802ar",
        "einhell-te-ac-270-50-silent",
        "bta-50-litros",
        "lusqtoff-lc2550vs",
    ],
    "/compresores/lusqtoff-50-litros/": [
        "lusqtoff-lc2550b-8",
        "lusqtoff-lc2550vs",
        "lusqtoff-lc3550bk",
    ],
    "/compresores/gamma-50-litros/": [
        "gamma-g2802ar",
    ],
    "/compresores/100-litros/": [
        "lusqtoff-lc30100",
        "lusqtoff-lc40100-8",
        "lusqtoff-lcs100-8",
    ],
    "/compresores/lusqtoff-100-litros/": [
        "lusqtoff-lc30100",
        "lusqtoff-lc40100-8",
    ],
    "/compresores/sin-aceite/": [
        "lusqtoff-lc2550vs",
        "einhell-te-ac-270-50-silent",
        "bta-24-oilfree",
        "fengda-as-186",
    ],
    "/compresores/bta-25-litros/": [
        "bta-25-litros",
    ],
    "/compresores/24-litros/": [
        "lusqtoff-lc2024b",
        "gamma-g2801ar",
        "einhell-th-ac-240-24",
        "bta-25-litros",
    ],
    "/compresores/para-aerografo/": [
        "fengda-as-186",
    ],
    "/compresores/kits-aerografo/": [
        "fengda-as-186",
    ],

    # Hidrolavadoras
    "/hidrolavadoras/karcher-k2/": [
        "karcher-k2-basic",
    ],
    "/hidrolavadoras/karcher-k3/": [
        "karcher-k3-black-edition",
    ],
    "/hidrolavadoras/karcher-k4/": [
        "karcher-k4-power-control",
        "karcher-k4-standard",
    ],
    "/hidrolavadoras/karcher-k5/": [
        "karcher-k5-power-control",
        "karcher-k5-base",
    ],
    "/hidrolavadoras/karcher/": [
        "karcher-k2-basic",
        "karcher-k3-black-edition",
        "karcher-k4-power-control",
        "karcher-k5-power-control",
    ],
    "/hidrolavadoras/bosch/": [
        "bosch-ghp-180",
        "bosch-ghp-220",
        "bosch-universalaquatak-36v-100",
    ],
    "/hidrolavadoras/stihl/": [
        "stihl-re-90",
        "stihl-re-110",
        "stihl-re-150",
    ],
    "/hidrolavadoras/lusqtoff-hl-120/": [
        "lusqtoff-hl-120",
    ],
    "/hidrolavadoras/lusqtoff/": [
        "lusqtoff-hl-120",
        "lusqtoff-hl-150",
        "lusqtoff-hl100-8",
    ],
    "/hidrolavadoras/gamma-130/": [
        "gamma-130-elite",
    ],
    "/hidrolavadoras/gamma-150/": [
        "gamma-150-elite",
    ],
    "/hidrolavadoras/gamma/": [
        "gamma-130-elite",
        "gamma-150-elite",
        "gamma-elite-200",
    ],
    "/hidrolavadoras/profesionales/": [
        "bosch-ghp-220",
        "bosch-ghp-4-50",
        "comet-k-250-10-150",
        "comet-k-250-13-190",
    ],

    # Taladros y Rotomartillos
    "/taladros/rotomartillos/": [
        "dewalt-dch273",
        "bosch-gbh-180-li",
        "bosch-gbh-2-26-dre",
        "makita-hr2470",
        "einhell-te-hd-18-li",
    ],
    "/taladros/rotomartillo-bosch/": [
        "bosch-gbh-180-li",
        "bosch-gbh-2-26-dre",
        "bosch-gbh-220",
    ],
    "/taladros/rotomartillo-dewalt/": [
        "dewalt-dch273",
        "dewalt-dch133",
        "dewalt-d25333",
    ],
    "/taladros/rotomartillo-einhell/": [
        "einhell-te-hd-18-li",
    ],
    "/taladros/percutores/": [
        "bosch-gsb-18v-50",
        "dewalt-dcd776",
        "makita-dhp453",
        "einhell-te-cd-18-40",
    ],
    "/taladros/dewalt-inalambrico/": [
        "dewalt-dcd776",
        "dewalt-dch273",
        "dewalt-dcf887",
    ],
    "/taladros/bosch-inalambrico/": [
        "bosch-gsb-18v-50",
        "bosch-gbh-180-li",
        "bosch-gdr-120-li",
    ],
    "/taladros/einhell-inalambrico/": [
        "einhell-te-cd-18-40",
        "einhell-te-hd-18-li",
    ],
    "/taladros/lusqtoff-inalambrico/": [
        "lusqtoff-tbl16-7",
        "lusqtoff-tbl710-9d",
    ],

    # Amoladoras
    "/amoladoras/bosch/": [
        "bosch-gws-770",
        "bosch-gws-850",
        "bosch-gws-25-180-lvi-r",
    ],
    "/amoladoras/dewalt/": [
        "dewalt-dwe4010",
        "dewalt-dwe4120",
        "dewalt-dcg412",
    ],
    "/amoladoras/makita/": [
        "makita-ga4530",
        "makita-m0901",
        "makita-gb801",
    ],
    "/amoladoras/skil-830w/": [
        "skil-9002ar",
    ],
    "/amoladoras/gamma/": [
        "gamma-g1910kar",
    ],
    "/amoladoras/dowen-pagio/": [
        "dowen-pagio-9993220-7",
    ],
    "/amoladoras/stanley/": [
        "stanley-sg7115",
    ],
    "/amoladoras/lusqtoff/": [
        "lusqtoff-mcl150-8",
    ],
    "/amoladoras/7-pulgadas/": [
        "bosch-gws-25-180-lvi-r",
        "bosch-gws-25-230",
    ],

    # Soldadoras
    "/soldadoras/esab-handyarc-162i/": [
        "esab-handyarc-162i",
    ],
    "/soldadoras/esab/": [
        "esab-handyarc-132i",
        "esab-handyarc-142i",
        "esab-handyarc-162i",
    ],
    "/soldadoras/lusqtoff-sml120-8d/": [
        "lusqtoff-sml120-8dk",
    ],
    "/soldadoras/lusqtoff-iron-250/": [
        "lusqtoff-iron-250",
    ],
    "/soldadoras/lusqtoff-iron-100/": [
        "lusqtoff-iron-100",
    ],
    "/soldadoras/lusqtoff/": [
        "lusqtoff-iron-250",
        "lusqtoff-sml120-8dk",
        "lusqtoff-iron-100",
        "lusqtoff-mig-195",
    ],
    "/soldadoras/mig-sin-gas/": [
        "lusqtoff-sml120-8dk",
        "lusqtoff-mig-195",
    ],
    "/soldadoras/soldadora-inverter-160-amp/": [
        "esab-handyarc-162i",
    ],

    # Generadores
    "/generadores/honda/": [
        "honda-eu22i",
        "honda-eu30is",
        "honda-eg6500cxs",
    ],
    "/generadores/honda-6500/": [
        "honda-eg6500cxs",
    ],
    "/generadores/inverter/": [
        "honda-eu22i",
        "honda-eu30is",
        "gamma-inverter-2kw",
        "lusqtoff-lgi3-8",
    ],
    "/generadores/gamma/": [
        "gamma-inverter-2kw",
    ],
    "/generadores/lusqtoff/": [
        "lusqtoff-lgi3-8",
    ],
}


def get_tools_for_guide(guide_url: str) -> List[TechnicalTool]:
    """Obtiene la lista de herramientas documentadas asociadas a una guía específica."""
    slugs = GUIDE_TOOL_MAPPINGS.get(guide_url, [])
    tools = []
    for s in slugs:
        t = get_tool_by_slug(s)
        if t:
            tools.append(t)
    return tools


def render_guide_technical_tools_block(guide_url: str) -> str:
    """
    Genera un bloque de HTML con enlaces directos a las fichas técnicas
    de TallerLab Data para los modelos relevantes de la guía actual.
    """
    tools = get_tools_for_guide(guide_url)
    if not tools:
        return ""

    items_html = []
    for tool in tools[:4]:  # Hasta 4 modelos destacados
        # Tomar 2 especificaciones principales
        specs_snippets = []
        for s in [s for s in tool.specifications if s.documentary_status == 'concordancia_textual'][:2]:
            val = s.original_value
            specs_snippets.append(f"{escape(s.name)}: <strong>{escape(val)}</strong>")

        specs_text = " · ".join(specs_snippets)

        items_html.append(f"""
        <div class="tl-guide-callout-item">
          <h4>{escape(tool.brand)} {escape(tool.model_name)}</h4>
          <p>{specs_text}</p>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="{tool.power_badge_css}" style="font-size:0.75rem; font-weight:700;">{escape(tool.power_badge_text)}</span>
            <a href="/herramientas/{tool.slug}/">Ver ficha completa →</a>
          </div>
        </div>
        """)

    return f"""
    <div class="tl-guide-integration-callout">
      <div class="tl-guide-callout-header">
        <div>
          <span style="font-size:0.75rem; font-weight:800; color:#ff5500; text-transform:uppercase; letter-spacing:0.06em;">TallerLab Data · Fichas documentales</span>
          <h3 class="tl-guide-callout-title">Modelos de esta guía en nuestra Base Técnica</h3>
        </div>
        <a href="/herramientas/comparar/" style="font-size:0.82rem; font-weight:700; color:#38bdf8;">Comparar en Matriz ↗</a>
      </div>
      <p style="font-size:0.86rem; color:#94a3b8; margin-bottom:0.75rem;">
        Datos declarados, variantes y fuentes registradas. Consultá cada ficha para conocer su cobertura documental:
      </p>
      <div class="tl-guide-callout-grid">
        {"".join(items_html)}
      </div>
    </div>
    """
