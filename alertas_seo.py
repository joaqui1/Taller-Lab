"""SEO de la sección Documentación y alertas.

Todo se deriva de los datos publicados del expediente: no agrega afirmaciones
que el expediente no contenga. Títulos, descripciones, resumen visible, datos
estructurados, indexación, sitemap y avisos en guías relacionadas.
"""
from __future__ import annotations

import re
import time
from html import escape
from typing import Any, Dict, Iterable, List, Optional, Tuple

from alertas_datos import ESTADOS_ALERTA, EDITOR_RESPONSABLE, derivar_estado_expediente

AUTOR_PATH = "/autor/joaquin-vallasciani/"
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre")


# ---------------------------------------------------------------- utilidades
def fecha_legible(iso: Optional[str]) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(iso or ""))
    if not m:
        return str(iso or "")
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{d} de {MESES[mo - 1]} de {y}"


def _anio(iso: Optional[str]) -> str:
    m = re.match(r"^(\d{4})", str(iso or ""))
    return m.group(1) if m else ""


def _recortar(texto: str, limite: int = 158) -> str:
    texto = re.sub(r"\s+", " ", texto).strip()
    if len(texto) <= limite:
        return texto
    corte = texto[: limite - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return corte + "…"


def _es_argentina(al: Dict[str, Any]) -> bool:
    return "argentina" in str(al.get("pais_mercado", "")).lower()


def alertas_confirmadas(exp: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [a for a in exp.get("alertas", []) if a.get("estado_alcance", "ALERTA_OFICIAL") == "ALERTA_OFICIAL"]


def alertas_argentinas(exp: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [a for a in alertas_confirmadas(exp) if _es_argentina(a)]


def paises_confirmados(exp: Dict[str, Any]) -> List[str]:
    return list(dict.fromkeys(a.get("pais_mercado", "") for a in alertas_confirmadas(exp) if a.get("pais_mercado")))


def estado_efectivo(exp: Dict[str, Any]) -> str:
    """Estado público: con alertas se respeta el editorial; sin alertas se deriva de las fuentes."""
    if exp.get("alertas"):
        return exp.get("estado_general", "NO_REVISADO")
    if exp.get("estado_general") == "NO_REVISADO":
        return "NO_REVISADO"
    return derivar_estado_expediente([], exp.get("fuentes_consultadas", []))


def expediente_indexable(exp: Dict[str, Any]) -> bool:
    """Una ficha en relevamiento no se ofrece a buscadores hasta completar la revisión."""
    return estado_efectivo(exp) != "NO_REVISADO"


def _alertas_ordenadas(exp: Dict[str, Any]) -> List[Dict[str, Any]]:
    return sorted(exp.get("alertas", []), key=lambda a: str(a.get("fecha", "")), reverse=True)


# ---------------------------------------------------------------- metadatos
def dossier_meta(exp: Dict[str, Any]) -> Tuple[str, str]:
    """Título (sin sufijo de marca del sitio) y meta description del expediente."""
    nombre = f"{exp['marca']} {exp['modelo_base']}"
    ar = alertas_argentinas(exp)
    confirmadas = alertas_confirmadas(exp)
    extranjeros = [p for p in paises_confirmados(exp) if "argentina" not in p.lower()]
    if ar:
        titulo = f"{nombre}: alerta en Argentina, recall y manual"
    elif confirmadas:
        titulo = f"{nombre}: recall en {' y '.join(extranjeros[:2])} y variante argentina"
    else:
        titulo = f"{nombre}: manual, despiece y variantes en Argentina"

    codigos = list(dict.fromkeys(v.get("codigo", "") for v in exp.get("variantes", []) if v.get("codigo")))
    if confirmadas:
        orden = [a for a in _alertas_ordenadas(exp) if a in confirmadas and _es_argentina(a)] + \
                [a for a in _alertas_ordenadas(exp) if a in confirmadas and not _es_argentina(a)]
        avisos = ", ".join(f"{a['organismo']} ({a.get('pais_mercado', '')}, {_anio(a.get('fecha'))})" for a in orden)
        desc = (f"Avisos oficiales sobre {nombre}: {avisos}. "
                f"Modelos y fechas alcanzados, {'variantes ' + ' y '.join(codigos[:2]) if len(codigos) > 1 else 'variante ' + (codigos[0] if codigos else exp['modelo_base'])}, manual y fuentes.")
    else:
        estado = estado_efectivo(exp)
        cierre = ("Sin alertas coincidentes en las fuentes consultadas a la fecha de revisión."
                  if estado == "SIN_ALERTAS" else "Revisión de antecedentes de seguridad en curso.")
        desc = (f"{nombre}, {exp.get('nombre_comercial', '')}: variantes {', '.join(codigos[:3])}, "
                f"manual oficial, despiece y fuentes. {cierre}")
    return titulo, _recortar(desc)


HUB_TITULO = "Alertas, recalls y manuales de herramientas en Argentina"
HUB_DESCRIPCION = ("Expedientes por modelo con avisos oficiales de Defensa del Consumidor, SERNAC y CPSC, "
                   "variantes argentinas, manuales y despieces. Fuentes y fechas verificables.")


# ---------------------------------------------------------------- resumen visible
def render_resumen(exp: Dict[str, Any]) -> str:
    """Respuesta directa al inicio de la ficha: qué avisos hay, dónde y qué revisar."""
    if estado_efectivo(exp) == "NO_REVISADO":
        return ""
    nombre = f"{escape(exp['marca'])} {escape(exp['modelo_base'])}"
    items = []
    for al in _alertas_ordenadas(exp):
        estado = al.get("estado_alcance", "ALERTA_OFICIAL")
        etiqueta = "" if estado == "ALERTA_OFICIAL" else f' <em>({escape(ESTADOS_ALERTA.get(estado, {}).get("etiqueta", estado).lower())})</em>'
        items.append(
            f'<li><strong>{escape(al.get("pais_mercado", ""))}</strong> · {escape(al["organismo"])} · '
            f'<time datetime="{escape(str(al.get("fecha", "")), quote=True)}">{escape(fecha_legible(al.get("fecha")))}</time>: '
            f'{escape(al.get("modelos_afectados", ""))}{etiqueta}</li>'
        )
    ar = alertas_argentinas(exp)
    if ar:
        situacion = (f"Este expediente registra {len(ar)} aviso{'s' if len(ar) > 1 else ''} oficial{'es' if len(ar) > 1 else ''} "
                     f"publicado{'s' if len(ar) > 1 else ''} en Argentina ({escape(', '.join(fecha_legible(a.get('fecha')) for a in ar))}). "
                     "Antes de reclamar, confirmá variante, lote y período de venta con el aviso y el canal oficial del fabricante.")
    elif exp.get("alertas"):
        situacion = ("Este expediente no registra un aviso argentino equivalente. Las campañas listadas corresponden a otros mercados "
                     "y no acreditan por sí solas cobertura o reparación gratuita en Argentina.")
    else:
        situacion = ("No se registraron alertas coincidentes en las fuentes consultadas. "
                     "Eso no certifica la seguridad del producto: revisá el manual y el estado de cada consulta.")
    lista = f'<ul class="dossier-resumen-lista">{"".join(items)}</ul>' if items else ""
    return f"""
      <section class="dossier-section dossier-resumen" id="resumen" aria-labelledby="resumen-titulo">
        <h2 id="resumen-titulo">Resumen: ¿hay alertas para el {nombre}?</h2>
        <p>{escape(exp.get('resumen_editorial', ''))}</p>
        {lista}
        <p><strong>Situación en Argentina:</strong> {situacion}</p>
        <ol class="dossier-pasos">
          <li>Identificá el código exacto y el tipo en la placa de la herramienta (<a href="#variantes">tabla de variantes</a>).</li>
          <li>Compará modelos, lotes, fechas y excepciones con cada <a href="#alertas">aviso oficial</a>.</li>
          <li>Usá el <a href="#documentacion">manual y el canal oficial</a> del fabricante para confirmar la reparación o el reemplazo.</li>
        </ol>
      </section>"""


RESUMEN_CSS = """
<style>
.dossier-resumen{border-left:4px solid #ff5500}
.dossier-resumen p{color:#cbd5e1;font-size:.95rem;line-height:1.65;margin:0 0 .85rem}
.dossier-resumen-lista,.dossier-pasos{color:#cbd5e1;font-size:.92rem;line-height:1.6;padding-left:1.25rem;margin:0 0 .9rem}
.dossier-resumen-lista li,.dossier-pasos li{margin-bottom:.35rem}
.alertas-registro td a{font-weight:700}
.guia-alerta-aviso{margin:1.25rem 0;padding:1rem 1.15rem;border:1px solid #fca5a5;border-left:4px solid #dc2626;border-radius:10px;background:#fef2f2;color:#450a0a;font-size:.92rem;line-height:1.6}
.guia-alerta-aviso strong{color:#7f1d1d}
.guia-alerta-aviso a{color:#b91c1c;font-weight:700;text-decoration:underline}
.guia-alerta-aviso .guia-alerta-nota{display:block;font-size:.84rem;color:#7f1d1d}
</style>
"""


# ---------------------------------------------------------------- registro del hub
def render_registro_hub(expedientes: Iterable[Dict[str, Any]]) -> str:
    filas = []
    for exp in expedientes:
        for al in exp.get("alertas", []):
            filas.append((str(al.get("fecha", "")), exp, al))
    if not filas:
        return ""
    filas.sort(key=lambda f: f[0], reverse=True)
    rows = "".join(
        f'<tr><td><time datetime="{escape(f, quote=True)}">{escape(fecha_legible(f))}</time></td>'
        f'<td><a href="/alertas/{escape(exp["slug"], quote=True)}/">{escape(exp["marca"])} {escape(exp["modelo_base"])}</a></td>'
        f'<td>{escape(al.get("pais_mercado", ""))}</td><td>{escape(al["organismo"])}</td>'
        f'<td>{escape(ESTADOS_ALERTA.get(al.get("estado_alcance", "ALERTA_OFICIAL"), {}).get("etiqueta", ""))}</td></tr>'
        for f, exp, al in filas
    )
    return f"""
      <section class="dossier-section alertas-registro" style="margin-top: 2.5rem;" aria-labelledby="registro-titulo">
        <h2 id="registro-titulo">Registro de alertas y recalls de herramientas</h2>
        <p class="dossier-section-desc">Avisos oficiales incorporados a los expedientes, del más reciente al más antiguo. Cada fila enlaza a la ficha con el alcance,
          las excepciones y la publicación original. El país indica el mercado de la fuente: un aviso extranjero no confirma una campaña en Argentina.</p>
        <div class="dossier-table-wrap">
          <table class="dossier-table">
            <thead><tr><th>Fecha del aviso</th><th>Modelo</th><th>Mercado</th><th>Organismo</th><th>Estado</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <p class="dossier-section-desc" style="margin-top:.75rem;">Descargá el registro completo en <a href="/datos/alertas/avisos.csv">CSV</a> o <a href="/datos/alertas/avisos.json">JSON</a>.</p>
      </section>"""


# ---------------------------------------------------------------- datos estructurados
def _base(canonical_url: str) -> str:
    return canonical_url.split("/alertas/")[0]


def _persona(base: str) -> Dict[str, Any]:
    return {"@type": "Person", "@id": base + AUTOR_PATH + "#joaquin-vallasciani",
            "name": EDITOR_RESPONSABLE, "url": base + AUTOR_PATH}


def dossier_schema(exp: Dict[str, Any], canonical_url: str) -> Dict[str, Any]:
    base = _base(canonical_url)
    nombre = f"{exp['marca']} {exp['modelo_base']}"
    fuentes = [a.get("enlace_original") for a in exp.get("alertas", []) if a.get("enlace_original")]
    doc = exp.get("documentacion", {})
    fuentes += [doc.get(k) for k in ("manual_url", "ficha_url") if doc.get(k)]
    titulo, descripcion = dossier_meta(exp)
    article = {
        "@type": "TechArticle",
        "@id": f"{canonical_url}#techarticle",
        "url": canonical_url,
        "mainEntityOfPage": canonical_url,
        "headline": f"Expediente técnico: {nombre}",
        "name": titulo,
        "description": exp.get("resumen_editorial") or descripcion,
        "inLanguage": "es-AR",
        "datePublished": exp.get("fecha_publicacion") or exp["fecha_revision"],
        "dateModified": exp["fecha_revision"],
        "author": _persona(base),
        "editor": {"@id": base + AUTOR_PATH + "#joaquin-vallasciani"},
        "publisher": {"@id": base + "/#organization"},
        "isPartOf": {"@id": base + "/alertas/#collection"},
        # Thing y no Product: un Product sin precio ni reseñas genera errores en Search Console.
        "about": {
            "@type": "Thing",
            "name": nombre,
            "identifier": exp["modelo_base"],
            "description": f"{exp.get('nombre_comercial', '')} ({exp['marca']})",
        },
    }
    if fuentes:
        article["isBasedOn"] = list(dict.fromkeys(fuentes))
    return {"@context": "https://schema.org", **article}


def hub_schema(expedientes: List[Dict[str, Any]], hub_url: str, publisher: Dict[str, Any]) -> Dict[str, Any]:
    base = _base(hub_url)
    visibles = [e for e in expedientes if expediente_indexable(e)]
    fechas = [e.get("fecha_revision") for e in visibles if e.get("fecha_revision")]
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": hub_url + "#collection",
        "name": HUB_TITULO,
        "description": HUB_DESCRIPCION,
        "url": hub_url,
        "inLanguage": "es-AR",
        "publisher": publisher,
        "editor": _persona(base),
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(visibles),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": f"{base}/alertas/{e['slug']}/",
                 "name": f"{e['marca']} {e['modelo_base']}"}
                for i, e in enumerate(visibles)
            ],
        },
    }
    if fechas:
        schema["dateModified"] = max(fechas)
    return schema


# ---------------------------------------------------------------- sitemap
def sitemap_alertas() -> Tuple[Dict[str, Optional[str]], set]:
    """Rutas indexables con su lastmod y rutas a excluir del sitemap."""
    from alertas_datos import cargar_expedientes
    incluir: Dict[str, Optional[str]] = {}
    excluir = set()
    expedientes = cargar_expedientes()
    fechas = []
    for exp in expedientes:
        path = f"/alertas/{exp['slug']}/"
        if expediente_indexable(exp):
            incluir[path] = exp.get("fecha_revision")
            if exp.get("fecha_revision"):
                fechas.append(exp["fecha_revision"])
        else:
            excluir.add(path)
    incluir["/alertas/"] = max(fechas) if fechas else None
    return incluir, excluir


# ---------------------------------------------------------------- avisos en guías
_CACHE: Dict[str, Any] = {"t": 0.0, "datos": None}
_TTL = 300


def _expedientes_con_alerta() -> List[Dict[str, Any]]:
    ahora = time.monotonic()
    if _CACHE["datos"] is None or ahora - _CACHE["t"] > _TTL:
        from alertas_datos import cargar_expedientes
        _CACHE["datos"] = [e for e in cargar_expedientes() if alertas_confirmadas(e)]
        _CACHE["t"] = ahora
    return _CACHE["datos"]


def render_aviso_guia(article_url: str, body: str) -> str:
    """Aviso visible en guías que tratan un modelo con alertas oficiales. Nunca rompe la guía."""
    try:
        expedientes = _expedientes_con_alerta()
    except Exception:
        return ""
    avisos = []
    for exp in expedientes:
        patron = rf"(?<![A-Za-z0-9]){re.escape(exp['modelo_base'])}(?![0-9])"
        if exp.get("guia_url") != article_url and not re.search(patron, body or "", re.IGNORECASE):
            continue
        paises = paises_confirmados(exp)
        nombre = f"{escape(exp['marca'])} {escape(exp['modelo_base'])}"
        avisos.append(
            f'<li><strong>{nombre}</strong>: aviso{"s" if len(alertas_confirmadas(exp)) > 1 else ""} oficial'
            f'{"es" if len(alertas_confirmadas(exp)) > 1 else ""} en {escape(", ".join(paises))}. '
            f'<a href="/alertas/{escape(exp["slug"], quote=True)}/">Ver alcance, variantes y fuentes →</a></li>'
        )
    if not avisos:
        return ""
    return (RESUMEN_CSS + '<aside class="guia-alerta-aviso" role="note" aria-label="Alertas de seguridad relacionadas">'
            '<strong>⚠️ Alertas de seguridad relacionadas con modelos de esta guía</strong>'
            f'<ul style="margin:.5rem 0 .4rem;padding-left:1.2rem;">{"".join(avisos)}</ul>'
            '<span class="guia-alerta-nota">El alcance depende de la variante, el lote y el mercado de venta; '
            'un aviso extranjero no confirma una campaña en Argentina.</span></aside>')
