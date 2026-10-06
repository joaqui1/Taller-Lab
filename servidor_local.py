"""
Servidor local para Taller Lab.
Lee todos los archivos Markdown de 'paginas/' y los sirve con el diseño oficial de TallerLab
(inspirado directamente en la maqueta del usuario: logo oficial, hero con drill de taller,
tipografía Plus Jakarta Sans + Caveat, paleta industrial naranja #ff5500 + grafito oscuro).
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
import re
from html import escape
from pathlib import Path
import urllib.parse
from datetime import datetime, timezone
from threading import Lock
from markdown_it import MarkdownIt
from validacion_enlaces import validar_html
from hubs import COMPRESSOR_HUB_FILES, COMPRESSOR_HUB_STEPS, HUB_COVER_COPY, HUB_EDITORIAL, HUB_STEPS
from home import HOME_COMPARISONS, HOME_TOOLS, HOME_CATEGORY_COPY, HOME_CATEGORY_IMAGES
from recursos_editoriales import RESOURCES, render_resource
from recursos_compra import BUYING_NOTES, render_buying_note
from amoladoras_comerciales import AMOLADORA_CHOICES, CONTEXTUAL_CHOICES, render_amoladora_choice, render_contextual_choice
from compresores_comerciales import install_catalog
from generadores_comerciales import install_catalog as install_generator_catalog
from hidrolavadoras_comerciales import install_catalog as install_pressure_washer_catalog
from sierras_comerciales import install_catalog as install_saw_catalog
from soldadoras_comerciales import install_catalog as install_welder_catalog
from taladros_comerciales import install_catalog as install_drill_catalog
from observatorio.catalog import CATALOG_PRODUCTS
from observatorio.enlaces import render_guide_prices, render_category_prices
from observatorio.export_csv import export_observations_to_csv
from observatorio.views import (
    get_dataset_schema_json,
    render_model_price_widget,
    render_observatory_category_html,
    render_observatory_hub_html,
    render_observatory_methodology_html,
)
from relevamiento_piloto import (
    ADMIN_KEY as RELEVAMIENTO_ADMIN_KEY,
    actualizar_estado_moderacion,
    exportar_dataset,
    get_admin_key,
    registrar_abandono,
    render_admin_dashboard,
    render_metodologia_page,
    render_relevamiento_callout,
    render_relevamiento_page,
    relevamiento_abierto,
    validar_y_procesar_formulario,
)

OBSERVATORY_PATHS = (
    "/datos/precios-herramientas-argentina/",
    "/datos/precios/compresores/",
    "/datos/precios/hidrolavadoras/",
    "/datos/precios/generadores/",
    "/datos/precios/metodologia/",
)
OBSERVATORY_DOWNLOAD_PATHS = (
    "/datos/precios/compresores/descargar-csv",
    "/datos/precios/hidrolavadoras/descargar-csv",
    "/datos/precios/generadores/descargar-csv",
)

RELEVAMIENTO_PATHS = (
    "/relevamiento-2027/",
    "/relevamiento-2027/metodologia/",
)

from alertas_datos import obtener_todos_los_slugs, obtener_expediente
from render_alertas import render_alerts_hub_page, render_model_dossier_page, dossier_schema
from alertas_seo import render_aviso_guia

ALERTAS_HUB_PATH = "/alertas/"
ALERTAS_DOSSIER_PATHS = tuple(f"/alertas/{slug}/" for slug in obtener_todos_los_slugs())
ALERTAS_PATHS = (ALERTAS_HUB_PATH,) + ALERTAS_DOSSIER_PATHS

from compatibilidad.views import (
    COMPATIBILITY_PATHS,
    COMPATIBILITY_SEARCH_PATH,
    COMPATIBILITY_DOWNLOAD_PATHS,
    get_compatibility_meta,
    render_compatibility_page_content,
)
from compatibilidad.export import (
    export_compatibility_to_csv,
    export_compatibility_to_json,
)
from compatibilidad.telemetry import track_event
from compatibilidad.pipeline import MaintenancePipeline

from tallerlab_data import (
    get_all_tools,
    get_tool_by_slug,
    get_editorial_comparison,
    get_all_editorial_comparisons,
)
from tallerlab_data.research_study import generate_study_csv
from tallerlab_data.guide_links import render_guide_technical_tools_block
from comunidad.components import render_guide_community, render_guide_community_entry
from tallerlab_data.views import (
    render_tools_hub_page,
    render_tool_detail_page,
    render_tool_comparator_page,
    render_editorial_comparisons_list_page,
    render_editorial_comparison_page,
    render_data_methodology_page,
    render_corrections_log_page,
    render_research_study_page,
    get_tool_product_schema,
    get_tool_page_schema,
    get_research_study_schema,
)

TALLERLAB_DATA_HUB_PATH = "/herramientas/"
TALLERLAB_DATA_COMPARATOR_PATH = "/herramientas/comparar/"
TALLERLAB_DATA_EDITORIAL_LIST_PATH = "/herramientas/comparaciones/"
TALLERLAB_DATA_METHODOLOGY_PATH = "/herramientas/metodologia/"
TALLERLAB_DATA_CORRECTIONS_PATH = "/herramientas/correcciones/"
TALLERLAB_DATA_RESEARCH_PATH = "/herramientas/investigacion/brecha-especificaciones-argentina/"
TALLERLAB_DATA_DOWNLOAD_PATHS = (
    "/herramientas/investigacion/descargar-datos.csv",
    "/herramientas/investigacion/descargar-datos.json",
    "/herramientas/investigacion/fuentes.json",
)

TALLERLAB_DATA_TOOL_PATHS = tuple(f"/herramientas/{t.slug}/" for t in get_all_tools())
TALLERLAB_DATA_EDITORIAL_PATHS = tuple(f"/herramientas/comparar/{c['slug'] if isinstance(c, dict) else c.slug}/" for c in get_all_editorial_comparisons())

TALLERLAB_DATA_STATIC_PATHS = (
    TALLERLAB_DATA_HUB_PATH,
    TALLERLAB_DATA_COMPARATOR_PATH,
    TALLERLAB_DATA_EDITORIAL_LIST_PATH,
    TALLERLAB_DATA_METHODOLOGY_PATH,
    TALLERLAB_DATA_CORRECTIONS_PATH,
    TALLERLAB_DATA_RESEARCH_PATH,
)

TALLERLAB_DATA_PATHS = (
    TALLERLAB_DATA_STATIC_PATHS
    + TALLERLAB_DATA_EDITORIAL_PATHS
    + TALLERLAB_DATA_TOOL_PATHS
)

ROOT_DIR = Path(__file__).parent
PAGES_DIR = ROOT_DIR / "paginas"
ASSETS_DIR = ROOT_DIR / "assets"
PORT = 8080
IS_PRODUCTION = os.environ.get("VERCEL_ENV") == "production" or os.environ.get("APP_ENV") == "production"
if IS_PRODUCTION and not os.environ.get("SITE_URL", "").strip():
    raise ValueError("Producción requiere SITE_URL con el dominio canónico definitivo")
SITE_URL = (os.environ.get("SITE_URL", "").strip() or f"http://localhost:{PORT}").rstrip("/")
_site_parts = urllib.parse.urlsplit(SITE_URL)
if (_site_parts.scheme not in ("http", "https") or not _site_parts.hostname
        or _site_parts.path or _site_parts.query or _site_parts.fragment or _site_parts.username):
    raise ValueError("SITE_URL debe ser un origen absoluto, por ejemplo https://tudominio.com")
if IS_PRODUCTION and (_site_parts.scheme != "https" or _site_parts.hostname in ("localhost", "127.0.0.1", "::1")
                      or _site_parts.hostname.endswith(".vercel.app")):
    raise ValueError("SITE_URL de producción debe usar HTTPS y el dominio canónico propio")
MARKDOWN = MarkdownIt("commonmark", {"html": True}).enable("table")

# Cargar imagen de logo en Base64 para garantizar carga 100% instantánea sin fallos
LOGO_SRC = "/assets/logo_cropped.webp"

AUTHOR_NAME = "Joaquín Vallasciani"
AUTHOR_ROLE = "Responsable de investigación documental de TallerLab"
AUTHOR_PATH = "/autor/joaquin-vallasciani/"

def extract_frontmatter(content):
    """Extrae metadatos del frontmatter YAML básico."""
    fm = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2]
            for line in raw_fm.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if val.startswith("[") and val.endswith("]"):
                        items = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",") if x.strip()]
                        fm[key] = items
                    else:
                        fm[key] = val
    return fm, body.strip()

CATEGORY_META = {
    "hidrolavadoras": {
        "name": "Hidrolavadoras",
        "icon": "💧",
        "desc": "Presión declarada/documentada, caudal declarado/documentado y comparativa de marcas.",
        "badge": "Limpieza y Presión",
        "accent": "#0284c7",
        "intro": "Presión de trabajo y máxima documentadas por código, caudal declarado y límites de las fichas de cada modelo."
    },
    "compresores": {
        "name": "Compresores",
        "icon": "💨",
        "desc": "Tanques de 24L a 200L, caudal CFM/PCM, lubricados y neumáticos.",
        "badge": "Aire Comprimido",
        "accent": "#f59e0b",
        "intro": "Capacidad de tanque, caudal declarado/documentado con su presión de referencia y consumo de herramientas neumáticas."
    },
    "amoladoras": {
        "name": "Amoladoras",
        "icon": "⚙️",
        "desc": "Discos de corte, flap, desbaste, marcas líderes y modelos a batería.",
        "badge": "Corte y Abrasivos",
        "accent": "#ff5500",
        "intro": "Modelos de 115 mm, 125 mm y 230 mm, comparativa a batería vs con cable y selección técnica de discos abrasivos según el material."
    },
    "taladros": {
        "name": "Taladros y atornilladores",
        "icon": "🔩",
        "desc": "Percutores, rotomartillos SDS, atornilladores de impacto y mechas.",
        "badge": "Perforación y Fijación",
        "accent": "#ea580c",
        "intro": "Taladros percutores para mampostería, rotomartillos para hormigón, atornilladores de impacto y selección de mechas diamantadas."
    },
    "sierras": {
        "name": "Sierras",
        "icon": "🪚",
        "desc": "Circulares, caladoras, de banco, ingletadoras y hojas de corte.",
        "badge": "Corte de Madera y Metal",
        "accent": "#d97706",
        "intro": "Sierras circulares de mano, caladoras para curvas, sensitivas para metal y sierras de banco para cortes longitudinales precisos."
    },
    "soldadoras": {
        "name": "Soldadura",
        "icon": "🧑‍🏭",
        "desc": "Inverter MMA, MIG sin gas (flux), TIG alta frecuencia y electrodos.",
        "badge": "Unión y Metales",
        "accent": "#e11d48",
        "intro": "Soldadoras inverter compactas, sistemas MIG flux para trabajar sin gas y tecnología TIG para aluminio y acero inoxidable."
    },
    "soldadura-electronica": {
        "name": "Soldadura electrónica",
        "icon": "🔌",
        "desc": "Cautines, estaciones de soldadura, aire caliente y accesorios para electrónica.",
        "badge": "Electrónica y reparación",
        "accent": "#e11d48",
        "intro": "Kits de estaño, estaciones con control de temperatura, aire caliente y soportes para reparar placas y cableado."
    },
    "generadores": {
        "name": "Generadores",
        "icon": "⚡",
        "desc": "Grupos electrógenos, inverter, cálculo de potencia kVA y nafta/gas.",
        "badge": "Energía y Respaldo",
        "accent": "#ca8a04",
        "intro": "Potencia nominal y máxima documentadas, cargas con motor y diferencias entre generadores inverter y equipos por combustible."
    }
}

# Enlaces de afiliado ya publicados en las guías. Cada opción apunta a un
# producto concreto; las búsquedas de catálogo se muestran por separado.
AFFILIATE_PRODUCTS = {
    "hidrolavadoras": [
        ("Logus eléctrica 1200 W · 105 bar", "Compacta para tareas de casa", "https://meli.la/2Rcddpg", "/hidrolavadoras/comparativa-general/"),
        ("Lüsqtoff HL100-7 · 100 bar", "Modelo de entrada con cable", "https://meli.la/1cZXqxL", "/hidrolavadoras/lusqtoff/"),
        ("Logus a nafta · 154 bar", "Para trabajar sin conexión eléctrica", "https://meli.la/1KQjHgT", "/hidrolavadoras/150-bar/"),
    ],
    "compresores": [
        ("Nictom IE01 portátil", "Inflador a batería para el auto", "https://meli.la/2m7TJWQ", "/compresores/para-auto/"),
        ("JD Extreme 107 · doble pistón", "Compresor de 12 V para neumáticos", "https://meli.la/274KM8a", "/compresores/12v-doble-piston/"),
        ("Kit Lüsqtoff de 5 piezas", "Accesorios; no incluye el compresor", "https://meli.la/32SJoX7", "/compresores/kits-accesorios/"),
    ],
    "amoladoras": [
        ("Gamma G1910KAR · 750 W", "Kit compacto con disco de 115 mm", "https://meli.la/12aMvrG", "/amoladoras/gamma/"),
        ("Dowen Pagio 9993220.7 · 900 W", "Amoladora angular con cable", "https://meli.la/1QUvfns", "/amoladoras/dowen-pagio/"),
        ("Bosch GWS 770", "Modelo compacto Bosch Professional", "https://meli.la/1GRCAjZ", "/amoladoras/bosch/"),
    ],
    "taladros": [
        ("Ingco CIDLI20668-4 · dos baterías", "Percutor inalámbrico para perforación y atornillado", "https://meli.la/2xvJRJp", "/taladros/taladro-percutor-inalambrico/"),
        ("Omaha AB550161K · 550 W", "Taladro fijo para banco de trabajo", "https://meli.la/2Znq55m", "/taladros/taladro-de-banco/"),
        ("Kommberg KB-TP650 + KB-AA820", "Taladro y amoladora con cable en un kit", "https://meli.la/2z7Capd", "/taladros/combo-taladro-amoladora/"),
    ],
    "sierras": [
        ("Black+Decker BES603 · 400 W", "Caladora de velocidad variable", "https://meli.la/1ntghna", "/sierras/caladoras-black-decker/"),
        ("Total · 2200 W y disco de 355 mm", "Sensitiva para metal", "https://meli.la/1mLrBwo", "/sierras/sensitivas-total/"),
    ],
    "soldadoras": [
        ("Lüsqtoff MEGAIRON100-8", "Kit inverter con máscara y escuadras", "https://meli.la/1knTbU1", "/soldadoras/lusqtoff-iron-100/"),
        ("Lüsqtoff MIG Flux", "Kit para soldar sin gas", "https://meli.la/26RsZRw", "/soldadoras/mig-lusqtoff/"),
        ("ESAB HandyArc 162i", "Soldadora inverter MMA", "https://meli.la/1mZhwNS", "/soldadoras/esab-handyarc-162i/"),
    ],
    "generadores": [
        ("Pektra · 720 W", "Grupo electrógeno chico de 2 tiempos", "https://meli.la/2jcLSy1", "/generadores/chicos/"),
        ("Pektra · 2,2 kVA", "Generador a nafta para cargas mayores", "https://meli.la/2bL6gVj", "/generadores/a-nafta/"),
        ("Philco · 2500 W", "Alternativa a nafta de 2500 W", "https://meli.la/1nUAUuv", "/generadores/a-nafta/"),
    ],
}

# Datos declarados en las fuentes enlazadas, con su procedencia visible.
# Las publicaciones comerciales no equivalen a documentación primaria.
# La imagen ilustra el modelo,
# no garantiza que la publicación de Mercado Libre incluya esa variante.
PRODUCT_FACTS = {
    "https://meli.la/2xvJRJp": dict(brand="Ingco", model="CIDLI20668-4", use="Obra", power="Batería", specs=["20 V", "66 Nm", "Mandril 13 mm"], includes="Dos baterías, cargador y accesorios según la publicación; verificá el vendedor", image="https://supertoolsbd.com/wp-content/uploads/2024/11/ingco-CIDLI20668-3.jpg", source="https://www.mercadolibre.com.ar/atornillador-taladro-percutor-2-bateriasaccesorios-color-naranja-frecuencia-0/p/MLA42241463", image_source="https://supertoolsbd.com/product/ingco-20v-brushless-impact-drill-66nm/"),
    "https://meli.la/2Znq55m": dict(brand="Omaha", model="AB550161K", use="Taller", power="Cable", specs=["550 W", "Mandril 16 mm", "5 velocidades"], includes="Morsa plana de 3 pulgadas según la publicación", image="https://images.fravega.com/f1000/d865236291f0ae3d2201283f5d7fbf8c.jpg", source="https://www.mercadolibre.com.ar/taladro-agujereadora-de-banco-16mm-550w-34-hp-5-vel-morsa/p/MLA68679095", image_source="https://www.fravega.com/p/taladro-de-banco-16mm-3-4hp-perforador-agujereadora-550w-velocidad-variable-morza-990039049/"),
    "https://meli.la/2z7Capd": dict(brand="Kommberg", model="KB-TP650 + KB-AA820", use="Hogar", power="Cable", specs=["Taladro 650 W", "Amoladora 820 W", "28 piezas"], includes="Cinco discos de corte, nueve mechas, abrasivos y maletín según la publicación", image="https://http2.mlstatic.com/D_NQ_NP_796058-MLA96317117276_102025-O.webp", source="https://www.mercadolibre.com.ar/kit-kommberg-amoladora-angular-820w-taladro-650w/p/MLA59099749"),
    "https://meli.la/1cZXqxL": dict(brand="Lüsqtoff", model="HL100-7", use="Hogar", power="Cable", specs=["1200 W", "100 bar máx.", "5,5 L/min"], includes="Pistola, lanza y manguera según ficha de referencia; verificá el aviso", image="https://images.fravega.com/f1000/b52c0f7278b0da1a4195245940c2bae8.jpg", source="https://www.mercadolibre.com.ar/hidrolavadora-lusqtoff-hl100-7-100-bar-1200w/p/MLA29665124", image_source="https://www.fravega.com/p/hidrolavadora-lusqtoff-100-bar-1200w-alta-presion-c-autostop-21261615/"),
    "https://meli.la/1KQjHgT": dict(brand="Logus", model="GHL150", use="Obra", power="Nafta", specs=["154 bar", "7,5 L/min", "Motor 6,5 hp"], includes="Manguera y boquillas según la publicación; verificá el aviso", image="https://acdn-us.mitiendanube.com/stores/006/185/083/products/sin-titulo-1_mesa-de-trabajo-1-090a64d5a9f1ca543d17544105719811-1024-1024.webp", source="https://www.mercadolibre.com.ar/hidrolavadora-nafta-logus-154-bar-65hp-a-explosion-uso-intensivo/p/MLA52112649", image_source="https://logus.com.ar/productos/hidrolavadora-a-explosion-6-5hp-industrial-154-bar-ghl-150/"),
    "https://meli.la/2m7TJWQ": dict(brand="Nictom", model="IE01", use="Hogar", power="Batería", specs=["16 L/min", "480 g", "Pantalla digital"], includes="Picos adaptadores según la publicación", image="https://dcdn-us.mitiendanube.com/stores/006/331/603/products/2-2bef6618825344eed517509424588157-1024-1024.jpg", source="https://www.mercadolibre.com.ar/inflador-compresor-de-aire-portatil-bateria-nictom-ie01-auto/p/MLA35806384", image_source="https://www.nictom.com.ar/productos/inflador-compresor-de-aire-portatil-bateria-powerbank-ie01-gris/"),
    "https://meli.la/274KM8a": dict(brand="JD Extreme", model="107", use="Hogar", power="12 V", specs=["150 PSI máx.", "Doble pistón", "85 L/min"], includes="Manguera, adaptadores y bolso según ficha de referencia; verificá el aviso", image="https://d2eebw31vcx88p.cloudfront.net/tiendashopealo/uploads-r/p/bb6f3873c8807408e876d43217bab037b4adeaa8.jpg", source="https://www.mercadolibre.com.ar/compresor-de-aire-portatil-jd-extreme-de-150-psi-con-doble-piston-para-auto-y-moto/p/MLA45403244", image_source="https://tiendashopealo.com.ar/p/inflador-compresor-de-aire-portatil-jd-extreme-107-manometro-12v-bolso/78944498-b3ba-483d-b5ff-5b21cd09a64b"),
    "https://meli.la/32SJoX7": dict(brand="Lüsqtoff", model="AA-5000K", use="Taller", power="Neumática", specs=["5 piezas", "Manguera 5 m", "Pistola 600 ml"], includes="Pistolas de pintar, lavar, soplar e inflar, más manguera; no incluye compresor", image="/assets/editorial/neumaticos.webp", illustrative=True, source="https://www.mercadolibre.com.ar/kit-compresor-aire-lusqtoff-5-piezas-pintar-set-acc-inflador/up/MLAU161535782"),
    "https://meli.la/1QUvfns": dict(brand="Dowen Pagio", model="9993220.7", use="Taller", power="Cable", specs=["900 W", "Disco 115 mm", "12.000 rpm"], includes="Empuñadura y protector según ficha de referencia; verificá si trae disco", image="https://images.fravega.com/f500/5b589cc8172df203d7d6eb5550730c94.jpg", source="https://www.mercadolibre.com.ar/amoladora-angular-115-mm-900-w-dowen-pagio-99932207-frecuencia-50hz-color-naranja/p/MLA19689037", image_source="https://www.fravega.com/p/amoladora-angular-115mm-dowen-pagio-9993220-7-900w-990018584/"),
    "https://meli.la/1mLrBwo": dict(brand="Total", model="TS223558-4", use="Obra", power="Cable", specs=["2200 W", "Disco 355 mm", "3.800 rpm"], includes="Disco, llave y carbones según la publicación", image="https://toolmart.me/cdn/shop/files/875743e3-6f13-4be7-8611-ea574e2358b3.webp?v=1741764964", source="https://www.mercadolibre.com.ar/sierra-sensitiva-total-disco-14--2200w-355mm-industrial/up/MLAU153228257", image_source="https://toolmart.me/en/products/total-cut-off-saw-2200w-355mm-14-ts223558"),
    "https://meli.la/26RsZRw": dict(brand="Lüsqtoff", model="SML120-8DK", use="Taller", power="Cable", specs=["220 V", "MIG flux y MMA", "Hasta 120 A"], includes="Máscara, escuadras, alambre, pinzas y torcha según la publicación", image="https://lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/SOLDADORAS_INVERTER/SML120-8DK/kit_web-jpg.jpg", source="https://www.mercadolibre.com.ar/soldadora-inverter-mig-alambre-flux-lusqtoff--antiadherente/up/MLAU2451359321", image_source="https://lusqtoff.com.ar/ver-producto/SML120-8DK"),
    "https://meli.la/1mZhwNS": dict(brand="ESAB", model="HandyArc 162i", use="Taller", power="Cable", specs=["220 V", "MMA", "Hasta 160 A"], includes="Pinza portaelectrodo, pinza de masa, correa y manual según la publicación", image="https://tfcvb6.vtexassets.com/arquivos/ids/238790-800-800?aspect=true&height=800&v=637776023027000000&width=800", source="https://www.mercadolibre.com.ar/soldadora-inverter-esab-handyarc-162i-amarilla-y-negra-50hz60hz/p/MLA17794906", image_source="https://revendapjba.ferimport.com.br/maquina-de-solda-inversora-esab-handyarc-162i-220v/p"),
    "https://meli.la/2jcLSy1": dict(brand="Pektra", model="GPK980", use="Hogar", power="Nafta", specs=["650 W nominales", "720 W máximos", "Motor 2 tiempos"], includes="Manual según la publicación", image="https://images.fravega.com/f1000/61d549f6e6e598ecafc73b1f4c5e1bd9.jpg", source="https://www.mercadolibre.com.ar/grupo-electrogeno-720w-pektra-072kva-34hp-980-nafta-generador-2t/p/MLA26044602", image_source="https://www.fravega.com/p/grupo-electrogeno-pektra-gpk980-720w-63-cc-310651/"),
    "https://meli.la/2bL6gVj": dict(brand="Pektra", model="GPK2200", use="Obra", power="Nafta", specs=["2,2 kVA máximos", "Motor 5,5 hp", "AVR"], includes="Contenido adicional a verificar en la publicación", image="https://images.fravega.com/f500/eb4c5afca76f256ad4ea980d91d2b83b.jpg", source="https://www.mercadolibre.com.ar/grupo-electrogeno-generador-pektra-22kva-55-hp-nafta/p/MLA20005447", image_source="https://www.fravega.com/p/grupo-electrogeno-generador-pektra-2-2kva-5-5-hp-nafta-990049032/"),
    "https://meli.la/1nUAUuv": dict(brand="Philco", model="GE-PH2500ALP", use="Hogar", power="Nafta", specs=["2500 W nominales", "2800 W máximos", "Tanque 15 L"], includes="Contenido adicional a verificar en la publicación", image="/assets/editorial/generadores.webp", illustrative=True, source="https://www.mercadolibre.com.ar/generador-electrico-philco-2500w-65hp-196cc-tanque-15l/p/MLA29450496"),
    "https://meli.la/2Rcddpg": dict(brand="Logus", model="HL-105", use="Hogar", power="Cable", specs=["1200 W", "105 bar máx.", "6,5 L/min"], includes="Lanza, manguera y dosificador según ficha del fabricante; verificá el aviso", image="https://acdn-us.mitiendanube.com/stores/006/185/083/products/2-58a6bef53d49637ba217507716217358-1024-1024.webp", source="https://logus.com.ar/productos/hidrolavadora-105-bar-1200w-hl-105/"),
    "https://meli.la/12aMvrG": dict(brand="Gamma", model="G1910KAR", use="Taller", power="Cable", specs=["750 W", "Disco 115 mm", "11.000 rpm"], includes="Configuración del kit a confirmar en el aviso", image="https://acdn-us.mitiendanube.com/stores/001/417/257/products/d_788148-mla42150887122_062020-b-c125585f91790a4ad617636443422920-1024-1024.webp", source="https://www.gramabi.com.ar/productos/amoladora-angular-750w-gamma-115mm-kit-g1910kar-caja-discos-celeste-60-hz-vvvco/"),
    "https://meli.la/1GRCAjZ": dict(brand="Bosch", model="GWS 770", use="Taller", power="Cable", specs=["770 W", "Disco 115 mm", "12.000 rpm"], includes="Empuñadura y protector según ficha del fabricante; verificá el aviso", image="https://static.titaferramentas.com.br/public/titaferramentas/imagens/produtos/esmerilhadeira-4-1-2-770w-220v-gws-770-06013980e0-bosch-6a42d2dfa97eb.png", source="https://www.bosch-professional.com/br/pt/products/gws-770-06013980E0", image_source="https://www.titaferramentas.com.br/esmerilhadeira-angular-4-1-2-770w-220v-gws-770-06013980e0-bosch/p/4053423348033"),
    "https://meli.la/1knTbU1": dict(brand="Lüsqtoff", model="MEGAIRON100-8", use="Taller", power="Cable", specs=["220 V", "Hasta 105 A", "MMA"], includes="Máscara y dos escuadras según ficha del fabricante; verificá el aviso", image="https://www.lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/SOLDADORAS_INVERTER/MEGAIRON100-8/MEGAIRON100-8_3_web.jpg", source="https://www.lusqtoff.com.ar/ver-producto/MEGAIRON100-8"),
    "https://meli.la/1ntghna": dict(brand="Black+Decker", model="BES603", use="Hogar", power="Cable", specs=["400 W", "Hasta 3.000 rpm", "Sierra caladora"], includes="Contenido de la caja a confirmar en el aviso", image="https://http2.mlstatic.com/D_NQ_NP_829009-MLA84554917660_052025-O.webp", source="https://www.mercadolibre.com.ar/sierra-caladora-black-decker-bes603-400w-3000-rpm/p/MLA39008702"),
}

# Correcciones de procedencia y variantes frente a la documentación revisada.
PRODUCT_FACTS["https://meli.la/26RsZRw"].update(
    specs=["200 V según ficha", "MIG flux / MMA / Lift TIG", "FLUX 20–120 A; MMA/TIG 20–100 A"],
    source="https://lusqtoff.com.ar/ver-producto/SML120-8DK",
    warning="La ficha oficial declara 200 V–50 Hz. Confirmá placa y tensión de la unidad ofrecida; 120 A corresponde a FLUX, no a todos los procesos.",
)
PRODUCT_FACTS["https://meli.la/1knTbU1"]["specs"] = ["220 V", "105 A al 30 % declarado", "MMA"]
PRODUCT_FACTS["https://meli.la/1mZhwNS"].update(
    specs=["220 V", "MMA", "160 A al 20 %; 72 A al 100 %"],
    source="https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/stick-welders-smaw/handyarc-132i-dv-142i-162i/",
    warning="Datos del código ESAB 0409616. Confirmá ese código en la oferta; corriente máxima y continua son distintas.",
)
PRODUCT_FACTS["https://meli.la/12aMvrG"]["source"] = "https://www.gammaherramientas.com.ar/producto/amoladora-angular-750-w/"
PRODUCT_FACTS["https://meli.la/2Rcddpg"].update(
    specs=["1200 W", "105 bar máximos declarados", "Caudal no informado"],
    includes="Contenido a confirmar en el aviso y manual del código HL-105",
)
PRODUCT_FACTS["https://meli.la/1KQjHgT"].update(
    specs=["Motor 6,5 hp", "154 bar declarados; tipo no informado", "Caudal no informado"],
    source="https://logus.com.ar/productos/hidrolavadora-a-explosion-6-5hp-industrial-154-bar-ghl-150/",
)
PRODUCT_FACTS["https://meli.la/2xvJRJp"].update(
    image="/assets/editorial/taladros.webp", illustrative=True,
    warning="Datos declarados en la publicación comercial. La foto de CIDLI20668-3 no identifica CIDLI20668-4, por eso se usa una ilustración.",
)
PRODUCT_FACTS["https://meli.la/2xvJRJp"].pop("image_source", None)
PRODUCT_FACTS["https://meli.la/1GRCAjZ"]["warning"] = "Fuente Bosch Brasil para 06013980E0; no confirma la variante, el kit ni la garantía de una oferta argentina."
PRODUCT_FACTS["https://meli.la/1mLrBwo"]["warning"] = "La oferta identifica TS223558-4; la documentación de TS223558 sin sufijo no prueba que sean la misma variante."
PRODUCT_FACTS["https://meli.la/1mLrBwo"].update(
    specs=["2200 W anunciados", "Disco 355 mm anunciado", "Rpm: confirmar variante"],
    warning="La oferta TS223558-4 anuncia 3.800 rpm; fábrica publica 3.700 rpm para TS223558. Confirmar placa y manual del sufijo -4; no tratar las dos fichas como equivalentes.",
)
PRODUCT_FACTS["https://meli.la/1ntghna"]["specs"] = ["400 W anunciados", "Velocidad variable: confirmar variante", "Caladora; hoja de movimiento alternativo"]
PRODUCT_FACTS["https://meli.la/1ntghna"]["warning"] = "BES603-B2 de 220 V declara 65 mm en madera y 6 mm en metal, sin identificar acero en ese campo. Confirmar sufijo, tensión y garantía de la oferta argentina."
PRODUCT_FACTS["https://meli.la/1cZXqxL"].update(
    source="https://www.lusqtoff.com.ar/ver-producto/HL100-7",
    specs=["1200 W · 220 V–50 Hz", "70 bar nominales / 100 bar máximos", "Flujo: 5,5 L/min; condición no precisada"],
    warning="HL100-7 tiene ficha propia; no hereda los datos de HL100-8. Confirmar código y contenido del kit en la unidad ofrecida.",
)
PRODUCT_FACTS["https://meli.la/2m7TJWQ"].update(
    source="https://www.nictom.com.ar/productos/inflador-compresor-de-aire-portatil-bateria-powerbank-ie01-gris/",
    specs=["Batería incorporada", "16 L/min máximos anunciados", "Pantalla digital y PowerBank"],
    warning="Declaraciones de la marca; faltan ensayo de inflado común, condición de caudal y autonomía bajo carga. Confirmar configuración IE01.",
)
SOURCE_ROLES = {
    "lusqtoff.com.ar": "fabricante", "www.lusqtoff.com.ar": "fabricante",
    "logus.com.ar": "marca", "www.bosch-professional.com": "fabricante",
    "www.gammaherramientas.com.ar": "fabricante", "esab.com": "fabricante",
    "www.nictom.com.ar": "marca", "www.mercadolibre.com.ar": "publicación comercial",
}
for facts in PRODUCT_FACTS.values():
    host = urllib.parse.urlsplit(facts["source"]).hostname or ""
    facts["source_type"] = SOURCE_ROLES.get(host, "fuente comercial por identificar")
    facts["evidence_label"] = {"fabricante": "Datos declarados por el fabricante", "marca": "Datos declarados por la marca"}.get(facts["source_type"], "Declaración comercial")

# Las guías seleccionadas presentan ofertas contextualizadas. La asignación
# por URL evita estanterías heredadas por categoría.
ARTICLE_AFFILIATE_SHELVES = {
    "/sierras/caladoras-black-decker/": ("https://meli.la/1ntghna",),
    "/amoladoras/": ("https://meli.la/12aMvrG", "https://meli.la/1QUvfns", "https://meli.la/1GRCAjZ"),
    "/soldadoras/": ("https://meli.la/1knTbU1", "https://meli.la/26RsZRw", "https://meli.la/1mZhwNS"),
    "/compresores/50-litros/": (),
    "/hidrolavadoras/comparativa-general/": (), "/hidrolavadoras/lusqtoff/": (),
    "/taladros/inalambricos/": (), "/taladros/percutores/": (),
    "/taladros/taladro-de-banco/": (), "/amoladoras/bosch/": (),
    "/compresores/para-auto/": (), "/sierras/caladoras/": (),
    "/generadores/comparativa-general/": (), "/generadores/precios/": (),
}

COMPARE_TYPES = {
    "https://meli.la/1KQjHgT": "hidrolavadora-nafta",
    "https://meli.la/2m7TJWQ": "inflador-portatil",
    "https://meli.la/274KM8a": "inflador-portatil",
    "https://meli.la/32SJoX7": "accesorio-neumatico",
    "https://meli.la/2Znq55m": "taladro-de-banco",
    "https://meli.la/2z7Capd": "kit-mixto",
    "https://meli.la/2xvJRJp": "taladro-percutor",
    "https://meli.la/1ntghna": "sierra-caladora",
    "https://meli.la/1mLrBwo": "sierra-sensitiva",
    "https://meli.la/1knTbU1": "soldadora-mma",
    "https://meli.la/26RsZRw": "soldadora-mig",
    "https://meli.la/1mZhwNS": "soldadora-mma",
}
COMPARE_ROWS = {
    "amoladoras": ("Potencia", "Diámetro de disco", "Velocidad", "Peso"),
    "hidrolavadoras": ("Potencia o motor declarados", "Presión declarada/documentada", "Caudal declarado/documentado"),
    "compresores": ("Dato principal", "Dato secundario", "Dato adicional"),
    "taladros": ("Dato principal", "Dato secundario", "Dato adicional"),
    "sierras": ("Potencia", "Disco u hoja", "Velocidad"),
    "soldadoras": ("Alimentación", "Proceso", "Corriente"),
    "generadores": ("Potencia nominal", "Potencia máxima", "Motor o tanque"),
}
COMPARE_ROWS.update({
    "inflador-portatil": ("Caudal declarado/documentado", "Presión máxima declarada", "Peso declarado"),
    "hidrolavadora-nafta": ("Motor declarado", "Presión declarada/documentada", "Caudal declarado/documentado"),
    "accesorio-neumatico": ("Piezas", "Manguera", "Pistola"),
    "taladro-de-banco": ("Potencia", "Mandril", "Velocidades"),
    "taladro-percutor": ("Voltaje", "Torque", "Mandril"),
    "kit-mixto": ("Taladro", "Amoladora", "Accesorios"),
    "sierra-caladora": ("Potencia", "Velocidad", "Tipo"),
    "sierra-de-banco": ("Potencia", "Disco", "Velocidad"),
    "sierra-sensitiva": ("Potencia", "Disco", "Velocidad"),
    "soldadora-mma": ("Alimentación", "Proceso", "Corriente"),
    "soldadora-mig": ("Alimentación", "Proceso", "Corriente"),
})
COMPARE_DETAILS = {
    "https://meli.la/12aMvrG": ("750 W", "115 mm", "11.000 rpm", "No informado"),
    "https://meli.la/1QUvfns": ("900 W", "115 mm", "12.000 rpm", "No informado"),
    "https://meli.la/1GRCAjZ": ("770 W", "115 mm", "12.000 rpm", "1,37 kg según Bosch"),
    "https://meli.la/2m7TJWQ": ("16 L/min", "No informado", "480 g"),
    "https://meli.la/274KM8a": ("85 L/min", "150 PSI", "No informado"),
    "https://meli.la/1knTbU1": ("220 V", "MMA", "105 A al 30 % declarado"),
    "https://meli.la/2bL6gVj": ("No informado", "2,2 kVA máximos", "Motor 5,5 hp"),
}
COMPARE_DETAILS.update({
    "https://meli.la/26RsZRw": ("200 V según ficha", "FLUX / MMA / Lift TIG", "FLUX 20–120 A; MMA/TIG 20–100 A"),
    "https://meli.la/1mZhwNS": ("220 V", "MMA", "160 A al 20 %; 72 A al 100 %"),
})
UNVERIFIED_SPECS = {
    "hidrolavadoras": ["Presión: verificar", "Caudal: verificar", "Potencia: verificar"],
    "compresores": ["Presión: verificar", "Caudal: verificar", "Tanque: verificar"],
    "amoladoras": ["Potencia: verificar", "Disco: verificar", "Velocidad: verificar"],
    "taladros": ["Voltaje: verificar", "Torque: verificar", "Mandril: verificar"],
    "sierras": ["Potencia: verificar", "Hoja: verificar", "Capacidad de corte: verificar"],
    "soldadoras": ["Corriente: verificar", "Ciclo de trabajo: verificar", "Proceso: verificar"],
    "generadores": ["Potencia: verificar", "Combustible: verificar", "Salidas: verificar"],
}

COMPRESORES_OFFERS = json.loads((ROOT_DIR / 'compresores-ofertas.json').read_text(encoding='utf-8'))
install_catalog(AFFILIATE_PRODUCTS, PRODUCT_FACTS, COMPRESORES_OFFERS)
GENERADORES_OFFERS = json.loads((ROOT_DIR / 'generadores-ofertas.json').read_text(encoding='utf-8'))
install_generator_catalog(AFFILIATE_PRODUCTS, PRODUCT_FACTS, GENERADORES_OFFERS)
HIDROLAVADORAS_OFFERS = json.loads((ROOT_DIR / 'hidrolavadoras-ofertas.json').read_text(encoding='utf-8'))
install_pressure_washer_catalog(AFFILIATE_PRODUCTS, PRODUCT_FACTS, HIDROLAVADORAS_OFFERS)
SIERRAS_OFFERS = json.loads((ROOT_DIR / 'sierras-ofertas.json').read_text(encoding='utf-8'))
install_saw_catalog(AFFILIATE_PRODUCTS, PRODUCT_FACTS, SIERRAS_OFFERS)
SOLDADORAS_OFFERS = json.loads((ROOT_DIR / 'soldadoras-ofertas.json').read_text(encoding='utf-8'))
install_welder_catalog(AFFILIATE_PRODUCTS, PRODUCT_FACTS, SOLDADORAS_OFFERS)
TALADROS_OFFERS = json.loads((ROOT_DIR / 'taladros-ofertas.json').read_text(encoding='utf-8'))
install_drill_catalog(AFFILIATE_PRODUCTS, PRODUCT_FACTS, TALADROS_OFFERS)
from fotos_productos import apply_photos, photo_for, render_photo, add_photos_to_cards
apply_photos(PRODUCT_FACTS)
from comparaciones_por_guia import PLANS as GUIDE_COMPARISON_PLANS, install_models as install_comparison_models, selection as guide_comparison_selection, editorial_config as guide_comparison_config
install_comparison_models(PRODUCT_FACTS)
# Las cards de estas guías se insertan en su marcador editorial, sin repetirlas al pie.
ARTICLE_AFFILIATE_SHELVES.update({path: () for path in COMPRESORES_OFFERS})
ARTICLE_AFFILIATE_SHELVES.update({path: () for path in GENERADORES_OFFERS})
ARTICLE_AFFILIATE_SHELVES.update({path: () for path in HIDROLAVADORAS_OFFERS})
ARTICLE_AFFILIATE_SHELVES.update({path: () for path in SIERRAS_OFFERS})
ARTICLE_AFFILIATE_SHELVES.update({path: () for path in SOLDADORAS_OFFERS})
ARTICLE_AFFILIATE_SHELVES.update({path: () for path in TALADROS_OFFERS})
ARTICLE_AFFILIATE_SHELVES.update({f'/compresores/{slug}/': () for slug in ('manguera', 'acoples-rapidos', 'aceite', 'filtros')})
from contenido_publico import es_enlace_afiliado
AFFILIATE_URLS = {item[2] for group in AFFILIATE_PRODUCTS.values() for item in group
                  if es_enlace_afiliado(item[2])}
CLICK_LOG = ROOT_DIR / "affiliate-clicks.jsonl"
CLICK_LOCK = Lock()

QUICK_BY_SECTION = {
    "taladros": [("Hogar", "Taladro atornillador inalámbrico", "Cómodo para muebles y fijaciones", "Revisá si trae baterías y cargador", "/taladros/inalambricos/"), ("Taller", "Percutor inalámbrico", "Suma trabajo en ladrillo", "La percusión no sustituye un SDS en hormigón", "/taladros/taladro-percutor-inalambrico/"), ("Obra", "Rotomartillo SDS", "Mejor para perforación frecuente en hormigón", "Más peso y menos precisión para atornillar", "/taladros/rotomartillos/")],
    "amoladoras": [("Hogar", "Amoladora compacta de 115 mm", "Fácil de maniobrar", "Menor profundidad de corte", "/amoladoras/115-o-125/"), ("Taller", "Amoladora de 125 mm", "Equilibrio entre corte y manejo", "Elegí el disco según material", "/amoladoras/115-o-125/"), ("Obra", "Amoladora de 230 mm", "Mayor profundidad de corte", "Más peso y exigencia eléctrica", "/amoladoras/9-pulgadas/")],
    "hidrolavadoras": [("Hogar", "Equipo compacto eléctrico", "Práctico para limpieza ocasional", "Compará caudal, no solo presión", "/hidrolavadoras/comparativa-general/"), ("Taller", "Equipo de mayor caudal", "Avanza mejor en superficies grandes", "Requiere suministro de agua adecuado", "/hidrolavadoras/comparativa-general/"), ("Obra", "Equipo profesional", "Revisá el ciclo documentado para la tarea", "Mayor costo y mantenimiento", "/hidrolavadoras/profesionales/")],
    "compresores": [("Hogar", "Inflador portátil", "Ocupa poco espacio", "No sirve para herramientas neumáticas continuas", "/compresores/para-auto/"), ("Taller", "Compresor con tanque", "Permite usos intermitentes", "Verificá caudal documentado a la presión de uso", "/compresores/50-litros/"), ("Obra", "Mayor tanque y caudal", "Compará caudal con el consumo de la herramienta", "Más peso, ruido y consumo", "/compresores/100-litros/")],
    "sierras": [("Hogar", "Sierra caladora", "Permite curvas y cortes ocasionales", "Menos rectitud en tramos largos", "/sierras/caladoras/"), ("Taller", "Sierra circular", "Cortes rectos rápidos", "Requiere guía y apoyo estable", "/sierras/circulares/"), ("Obra", "Sierra de banco o sensitiva según material", "Repetibilidad o corte de metal", "Equipo fijo y de mayor tamaño", "/sierras/")],
    "soldadoras": [("Hogar", "Inverter MMA compacta", "Portable para reparaciones", "Exige práctica con electrodo", "/soldadoras/"), ("Taller", "MIG flux", "Alimentación continua de alambre", "Produce escoria y salpicaduras", "/soldadoras/mig-sin-gas/"), ("Obra", "Inverter según ciclo de trabajo", "Compará corriente y ciclo documentados", "Verificá alimentación y protección", "/soldadoras/")],
    "generadores": [("Hogar", "Generador según cargas esenciales", "Respaldo dimensionado", "Calculá picos de arranque", "/generadores/para-casa/"), ("Taller", "Equipo con margen de potencia", "Admite herramientas con motor", "Mayor consumo y ruido", "/generadores/a-nafta/"), ("Obra", "Generador de capacidad superior", "Alimenta varias cargas", "Requiere ventilación y mantenimiento", "/generadores/a-nafta/")],
    "soldadura-electronica": [("Hogar", "Kit de soldador de estaño", "Resuelve uniones sencillas", "Control de temperatura limitado", "/soldadura-electronica/kit-soldador-de-estano/"), ("Taller", "Estación de soldadura", "Mejor control de temperatura", "Ocupa más espacio", "/soldadura-electronica/estacion-de-soldadura/"), ("Reparación SMD", "Estación con aire caliente", "Permite trabajar componentes superficiales", "Requiere práctica para evitar daños", "/soldadura-electronica/estacion-de-soldadura/")],
}

# Las selecciones editoriales de una guía se declaran por URL. No se reutiliza
# una recomendación de categoría en artículos con necesidades distintas.
QUICK_BY_ARTICLE = {
    "/hidrolavadoras/comparativa-general/": [
        ("Auto", "Guía para lavar el auto", "Compará manguera, caudal y accesorios para el vehículo", "Elegí un chorro controlable y mantené distancia prudente", "/hidrolavadoras/para-autos/"),
        ("Sin enchufe", "Hidrolavadora inalámbrica", "Priorizá movilidad cuando no tenés una toma cercana", "Autonomía y caudal pueden ser más limitados", "/hidrolavadoras/inalambricas/"),
        ("Trabajo frecuente", "Hidrolavadora profesional", "Dimensioná la máquina para las horas de uso previstas", "Verificá alimentación, ciclo de trabajo y servicio técnico", "/hidrolavadoras/profesionales/"),
        ("HVAC", "Limpieza de aire acondicionado", "Revisá presión controlable, drenaje y acceso", "Seguí el procedimiento indicado para la unidad", "/hidrolavadoras/hidrolavadora-para-aire-acondicionado/"),
    ],
    "/compresores/50-litros/": [
        ("Uso intermitente", "Lüsqtoff LC2550B-8", "50 L y 206 L/min de flujo declarados", "El caudal entregado a presión de trabajo no está informado", "https://www.lusqtoff.com.ar/productos/compresor-de-aire-o-25-hp-50-lts-lc2550b-8"),
        ("Inflar y sopletear", "Gamma G2802AR", "Tanque de 50 L y motor de 2,5 HP según su manual", "La página comercial y el manual discrepan en la potencia; confirmá la variante", "https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf"),
        ("Menos ruido", "Einhell TE-AC 270/50 Silent", "50 L y 70 dB(A) declarados por el fabricante", "El caudal cae a 98 L/min a 7 bar", "https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/"),
    ],
}
SOURCE_CLAIMS = {
    "/compresores/50-litros/": [
        ("Lüsqtoff LC2550B-8: tanque, potencia, flujo declarado, presión y contenido", "https://www.lusqtoff.com.ar/productos/compresor-de-aire-o-25-hp-50-lts-lc2550b-8"),
        ("Gamma G2802AR: tanque, potencia, desplazamiento y presión según manual", "https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf"),
        ("Gamma G2802AR: página comercial con potencia discrepante y peso", "https://www.gammaherramientas.com.ar/producto/compresor-de-50-litros/"),
        ("Einhell TE-AC 270/50 Silent: tanque, potencia, caudal a 7 bar y ruido", "https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/"),
    ],
}
GENERAL_QUICK_URLS = {
    "/hidrolavadoras/comparativa-general/",
    "/generadores/comparativa-general/",
}

def render_quick_guide(article):
    rows = QUICK_BY_ARTICLE.get(article["url"])
    if rows is None and (article["url"] == f'/{article["section"]}/' or article["url"] in GENERAL_QUICK_URLS):
        rows = QUICK_BY_SECTION.get(article["section"], [])
    if not rows:
        return ""
    cards = ""
    for need, choice, advantage, limit, path in rows:
        link = f'<a href="{escape(path, quote=True)}">Ver guía →</a>' if not path.startswith(('https://', 'http://')) else ''
        cards += f'<article><span>{escape(need)}</span><h3>{escape(choice)}</h3><p><strong>Ventaja:</strong> {escape(advantage)}</p><p><strong>Límite:</strong> {escape(limit)}</p>{link}</article>'
    has_product_sources = bool(rows) and all(path.startswith("https://") for *_, path in rows)
    kicker = 'MODELOS CON FICHA CONSULTADA' if has_product_sources else 'ORIENTACIÓN POR TAREA'
    return f'<section class="quick-guide" aria-label="Recomendación rápida"><span class="section-kicker">ANTES DE LEER · {kicker}</span><h2>Elegí según tu tarea</h2><div class="quick-grid">{cards}</div></section>'

def render_50l_models():
    """Modelos de 50 L documentados; no se presentan como ofertas afiliadas."""
    models = [
        ("Lüsqtoff", "LC2550B-8", "Uso intermitente en taller", ("50 L", "2,5 HP", "206 L/min de flujo declarado"), "Filtro de aire y ruedas", "https://www.lusqtoff.com.ar/productos/compresor-de-aire-o-25-hp-50-lts-lc2550b-8", "https://http2.mlstatic.com/D_NQ_NP_2X_813264-MLA110043387697_042026-O.webp", "https://www.mercadolibre.com.ar/compresor-de-aire-lusqtoff-lc2550b-8-50-lts-25-hp-1750w/p/MLA57291244"),
        ("Gamma", "G2802AR", "Inflar, soplar y pintar por tramos", ("50 L", "2,5 HP según manual", "203 L/min desplazados"), "Confirmar kit en la publicación", "https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf", None, None),
        ("Einhell", "TE-AC 270/50 Silent", "Cuando importa reducir el ruido", ("50 L", "1.650 W", "98 L/min a 7 bar"), "Ruedas y asa; accesorios aparte", "https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/", "https://d2c5rvsfjg2eub.cloudfront.net/image/208244749100/image_qid1e9h9vd42rb1sou1jcfh14q/-FJPG-FWEBP-B800", "https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/"),
    ]
    cards = ""
    for brand, model, use, specs, includes, source, image, image_source in models:
        local_photo = photo_for(brand=brand, model=model)
        if local_photo:
            image, image_source = local_photo['image'], local_photo['source']
        photo = f'<img src="{escape(image, quote=True)}" alt="{escape(brand + " " + model, quote=True)}" width="800" height="800" loading="lazy" decoding="async">' if image else '<span class="offer-no-photo">Foto no disponible</span>'
        cards += f'<article class="offer-card model-card"><div class="offer-card-top"><span>COMPRESOR DE 50 L</span><span>MODELO DOCUMENTADO</span></div><div class="offer-photo">{photo}</div><h3>{escape(brand)} · {escape(model)}</h3><p class="offer-description">{escape(use)}</p><ul class="offer-specs">{"".join(f"<li>{escape(spec)}</li>" for spec in specs)}</ul><p class="offer-includes"><strong>Incluye:</strong> {escape(includes)}</p></article>'
    return f'<section class="documented-models" aria-label="Modelos de compresor de 50 litros"><div class="affiliate-heading"><div><span class="section-kicker">OPCIONES PARA ESTA GUÍA</span><h2>Compará compresores de 50 litros</h2></div><p>Modelos y datos de fichas de fabricante. Comprobá la variante, el caudal útil y el contenido del aviso antes de comprar.</p></div><div class="offer-grid">{cards}</div></section>'

TAXONOMY_MAP = {
    "hidrolavadoras": {
        "general": ["01-hidrolavadoras.md"],
        "necesidad": [
            "02-hidrolavadora-inalambrica.md",
            "11-hidrolavadora-profesional.md",
            "18-hidrolavadora-150-bar.md",
            "19-hidrolavadora-200-bar.md",
            "22-hidrolavadoras-para-autos.md",
            "23-hidrolavadora-para-aire-acondicionado.md"
        ],
        "marcas": [
            "21-hidrolavadoras-karcher.md",
            "03-hidrolavadoras-lusqtoff.md",
            "04-hidrolavadoras-gamma.md",
            "05-hidrolavadoras-stihl.md",
            "06-hidrolavadoras-bosch.md",
            "07-hidrolavadoras-black-decker.md",
            "13-hidrolavadoras-einhell.md",
            "15-hidrolavadoras-hyundai.md",
            "20-hidrolavadoras-niwa.md"
        ],
        "modelos": [
            "08-hidrolavadora-karcher-k2.md",
            "12-hidrolavadora-karcher-k3.md",
            "17-hidrolavadora-karcher-k4.md",
            "09-hidrolavadora-karcher-k5.md",
            "14-hidrolavadora-gamma-130.md",
            "10-hidrolavadora-gamma-150.md",
            "16-hidrolavadora-lusqtoff-hl-120.md"
        ],
        "accesorios": []
    },
    "compresores": {
        "general": ["02-compresor-de-50-litros.md"],
        "necesidad": [
            "01-compresor-de-aire-para-auto.md",
            "23-compresor-12v-doble-piston.md",
            "22-inflador-de-neumaticos-portatil.md",
            "07-compresor-para-aerografo.md",
            "11-compresor-de-100-litros.md",
            "15-compresor-sin-aceite.md",
            "16-compresor-de-200-litros.md",
            "18-compresor-de-24-litros.md",
            "19-compresor-inalambrico.md",
            "04-aerografo-con-compresor.md",
            "21-compresor-para-pintar.md"
        ],
        "marcas": [
            "20-compresor-stanley.md"
        ],
        "modelos": [
            "09-compresor-lusqtoff-50-litros.md",
            "12-compresor-gamma-50-litros.md",
            "14-compresor-lusqtoff-100-litros.md",
            "17-compresor-bta-25-litros.md"
        ],
        "accesorios": [
            "03-manguera-para-compresor-de-aire.md",
            "05-pistola-para-pintar-con-compresor.md",
            "06-acople-rapido-para-compresor.md",
            "08-aceite-para-compresor-de-aire.md",
            "10-filtro-de-aire-para-compresor.md",
            "13-kit-para-compresor-de-aire.md"
        ]
    },
    "amoladoras": {
        "general": [
            "00-amoladoras.md"
        ],
        "necesidad": [
            "08-amoladoras-inalambricas.md",
            "20-amoladora-115-o-125.md",
            "19-amoladora-7-pulgadas.md",
            "12-amoladora-de-9-pulgadas.md",
            "05-amoladora-recta.md",
            "06-amoladora-de-banco.md",
            "18-amoladora-velocidad-variable.md"
        ],
        "marcas": [
            "03-amoladoras-dewalt.md",
            "07-amoladoras-makita.md",
            "10-amoladoras-bosch.md",
            "11-amoladoras-lusqtoff.md",
            "15-amoladoras-stanley.md",
            "17-amoladoras-ingco.md",
            "21-amoladoras-gamma.md",
            "22-amoladoras-total.md",
            "23-amoladoras-dowen-pagio.md"
        ],
        "modelos": [
            "13-amoladora-skil-830w.md"
        ],
        "accesorios": [
            "02-discos-para-amoladora.md",
            "01-disco-flap.md",
            "04-disco-de-desbaste.md",
            "09-disco-para-cortar-ceramica.md",
            "14-disco-diamantado-segmentado.md",
            "16-disco-de-corte.md",
            "24-disco-para-cortar-vidrio.md"
        ]
    },
    "taladros": {
        "general": [],
        "necesidad": [
            "01-taladro-inalambrico.md",
            "02-rotomartillo.md",
            "03-taladro-percutor.md",
            "04-taladro-de-banco.md",
            "05-atornillador-de-impacto.md",
            "07-taladro-percutor-inalambrico.md",
            "08-atornillador-para-durlock.md",
            "23-combo-taladro-amoladora.md",
        ],
        "marcas": [
            "09-taladro-black-decker.md",
            "12-taladro-inalambrico-einhell.md",
            "13-taladro-inalambrico-dewalt.md",
            "15-taladro-milwaukee.md",
            "16-taladro-inalambrico-lusqtoff.md",
            "18-taladro-stanley.md",
            "20-taladro-inalambrico-bosch.md"
        ],
        "modelos": [
            "06-rotomartillo-bosch.md",
            "10-rotomartillo-einhell.md",
            "11-rotomartillo-dewalt.md",
            "19-atornillador-de-impacto-dewalt.md"
        ],
        "accesorios": [
            "14-mecha-para-porcelanato.md",
            "17-brocas-para-ceramica.md",
            "21-mechas-escalonadas.md",
            "22-mecha-forstner-35-mm.md"
        ]
    },
    "sierras": {
        "general": [],
        "necesidad": [
            "01-sierra-circular.md",
            "02-sensitiva.md",
            "03-sierra-sable.md",
            "04-sierra-caladora.md",
            "05-sierra-sin-fin-para-madera.md",
            "06-sierra-de-banco.md",
            "07-sierra-sin-fin-para-metal.md",
            "21-ingletadoras.md",
            "19-sierra-sable-inalambrica.md",
            "30-sierra-circular-inalambrica.md"
        ],
        "marcas": [
            "08-ingletadora-einhell.md",
            "10-caladora-skil.md",
            "09-sierra-de-banco-einhell.md",
            "12-sensitiva-dewalt.md",
            "27-sensitiva-lusqtoff.md",
            "29-sensitiva-total.md",
            "13-ingletadora-dewalt.md",
            "14-ingletadora-total.md",
            "17-sierra-circular-black-and-decker.md",
            "18-caladora-einhell.md",
            "20-sierra-circular-lusqtoff.md",
            "22-caladoras-bosch.md",
            "25-caladoras-black-decker.md",
            "26-sierra-de-banco-lusqtoff.md",
            "28-sierra-sin-fin-lusqtoff.md"
        ],
        "modelos": [
            "16-sierra-circular-bosch-gks-150.md",
            "23-sierra-circular-dewalt-dwe560.md",
            "24-stanley-sc16.md"
        ],
        "accesorios": [
            "11-guia-para-sierra-circular.md",
            "15-disco-para-sierra-circular.md"
        ]
    },
    "soldadoras": {
        "general": [
            "00-soldadoras.md"
        ],
        "necesidad": [
            "04-soldadora-mig-con-gas.md",
            "06-soldadora-tig.md",
            "07-soldadora-mig-sin-gas.md",
            "03-soldadora-de-punto.md",
            "11-soldadora-inverter-200-amp.md",
            "17-soldadora-para-aluminio.md",
            "19-soldadora-tig-ac-dc.md",
            "20-soldadora-inverter-160-amp.md"
        ],
        "marcas": [
            "02-soldadora-lusqtoff.md",
            "15-soldadora-esab.md"
        ],
        "modelos": [
            "14-soldadora-dogo-180.md",
            "18-soldadora-lusqtoff-iron-250.md"
        ],
        "accesorios": [
            "01-electrodo-7018.md",
            "05-guantes-para-soldar.md",
            "08-alambre-para-soldadura-mig.md",
            "09-mascara-de-soldar-fotosensible.md",
            "10-electrodo-6013.md",
            "12-electrodo-para-fundicion.md",
            "13-alambre-flux.md",
            "16-electrodo-para-acero-inoxidable.md"
        ]
    },
    "soldadura-electronica": {
        "general": ["02-estacion-de-soldadura.md"],
        "necesidad": ["01-kit-soldador-de-estano.md"],
        "marcas": [],
        "modelos": ["03-gadnic-878d.md", "04-yihua-898d.md"],
        "accesorios": ["05-soporte-para-soldar-con-lupa.md"],
    },
    "generadores": {
        "general": [
            "01-grupos-electrogenos.md",
            "02-precios-de-grupos-electrogenos.md"
        ],
        "necesidad": [
            "05-generador-para-casa.md",
            "06-generadores-inverter.md",
            "07-generadores-trifasicos.md",
            "08-generadores-a-nafta.md",
            "13-grupos-electrogenos-monofasicos.md",
            "14-generadores-diesel.md",
            "15-generadores-portatiles.md",
            "21-grupos-electrogenos-chicos.md",
            "16-generadores-silenciosos.md",
            "19-generadores-a-gas.md",
            "20-estaciones-de-energia-portatiles.md"
        ],
        "marcas": [
            "03-grupos-electrogenos-honda.md",
            "09-generadores-hyundai.md",
            "11-generadores-lusqtoff.md",
            "12-generadores-gamma.md",
            "18-generadores-niwa.md"
        ],
        "modelos": [
            "04-honda-6500.md",
            "10-gamma-6500.md",
            "17-gamma-950.md"
        ],
        "accesorios": []
    }
}

# Completar el recorrido con las guías añadidas después del mapa original.
TAXONOMY_MAP["soldadoras"]["modelos"].extend([
    "21-soldadora-lusqtoff-iron-100.md", "22-soldadora-mig-lusqtoff.md",
    "23-soldadora-lusqtoff-sml150-8.md", "24-soldadora-lusqtoff-sml120-8d.md",
    "26-esab-handyarc-162i.md", "28-soldadora-lusqtoff-sml130-7.md",
])
TAXONOMY_MAP["soldadoras"]["accesorios"].extend([
    "25-carro-para-soldadora-mig.md", "27-mascara-lusqtoff-st-1x.md",
])

BRANDS_LIST = [
    'karcher', 'gamma', 'lusqtoff', 'bosch', 'dewalt', 'stihl', 'einhell', 
    'makita', 'stanley', 'milwaukee', 'black-decker', 'black+decker', 'hyundai', 
    'niwa', 'skil', 'esab', 'dogo', 'total'
]

def extract_brands(text):
    text_clean = text.lower().replace("+", "-").replace(" ", "-")
    found = set()
    for b in BRANDS_LIST:
        if b in text_clean:
            found.add(b)
    return found

def get_related_articles(curr, all_articles, taxonomy_map, limit=3):
    """Calcula las guías más relevantes para el artículo actual según marca, sinergia de funnel y temas."""
    sec = curr["section"]
    cands = [a for a in all_articles if a["section"] == sec and a["url"] != curr["url"]]
    if not cands:
        return []
        
    curr_brands = extract_brands(curr["filename"] + " " + curr["title"])
    curr_keywords = set(curr.get("keywords", []))
    
    sec_tax = taxonomy_map.get(sec, {})
    curr_type = "necesidad"
    for t, files in sec_tax.items():
        if curr["filename"] in files:
            curr_type = t
            break
            
    scored = []
    stopwords = {"de", "la", "el", "los", "las", "un", "una", "para", "en", "y", "a", "con", "que", "por", "vs", "o", "del", "al"}
    curr_words = set(re.findall(r'[a-zA-Z0-9]+', curr["title"].lower())) - stopwords

    for cand in cands:
        score = 0
        cand_brands = extract_brands(cand["filename"] + " " + cand["title"])
        cand_keywords = set(cand.get("keywords", []))
        
        cand_type = "necesidad"
        for t, files in sec_tax.items():
            if cand["filename"] in files:
                cand_type = t
                break
                
        # 1. Coincidencia de marca
        common_brands = curr_brands & cand_brands
        if common_brands:
            score += 35
            
        # 2. Sinergia de taxonomía en el funnel
        if curr_type == "modelos":
            if cand_type == "modelos" and common_brands:
                score += 30
            elif cand_type == "marcas" and common_brands:
                score += 25
            elif cand_type == "general":
                score += 20
        elif curr_type == "general":
            if cand_type == "modelos":
                score += 25
            elif cand_type == "necesidad":
                score += 20
        elif curr_type == "accesorios":
            if cand_type == "accesorios":
                score += 30
            elif cand_type == "general":
                score += 15
        elif curr_type == "marcas":
            if cand_type == "modelos" and common_brands:
                score += 35
                
        # 3. Superposición de palabras clave
        score += len(curr_keywords & cand_keywords) * 6
        
        # 4. Superposición de tokens del título
        cand_words = set(re.findall(r'[a-zA-Z0-9]+', cand["title"].lower())) - stopwords
        score += len(curr_words & cand_words) * 4
        
        scored.append((score, cand))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in scored[:limit]]

def load_all_articles():
    """Escanea y carga los artículos markdown del repositorio."""
    articles = []
    
    # 1. Amoladoras en la raíz de paginas/
    for p in PAGES_DIR.glob("*.md"):
        fm, body = extract_frontmatter(p.read_text(encoding="utf-8"))
        cat = fm.get("category", "Amoladoras")
        url = fm.get("url", f"/amoladoras/{p.stem}/")
        if not url.endswith("/"):
            url += "/"
        articles.append({
            "path": p,
            "filename": p.name,
            "section": "amoladoras",
            "category": cat,
            "title": fm.get("title", p.stem),
            "h1": fm.get("h1", p.stem),
            "url": url,
            "description": fm.get("description", ""),
            "author": fm.get("author", AUTHOR_NAME),
            "reviewed": fm.get("reviewed", ""),
            "published": fm.get("published", ""),
            "research_type": fm.get("research_type", ""),
            "physical_test": fm.get("physical_test", ""),
            "specifications_contrasted": fm.get("specifications_contrasted", ""),
            "buyer_opinions": fm.get("buyer_opinions", ""),
            "primary_sources": fm.get("primary_sources", ""),
            "information_asset": fm.get("information_asset", ""),
            "asset_status": fm.get("asset_status", ""),
            "keywords": fm.get("keywords", []),
            "body": body,
            "word_count": len(body.split()),
        })
        
    # 2. Artículos en subcarpetas
    for sub in PAGES_DIR.iterdir():
        if sub.is_dir():
            sec_id = sub.name
            for p in sub.glob("*.md"):
                fm, body = extract_frontmatter(p.read_text(encoding="utf-8"))
                cat = fm.get("category", sec_id.capitalize())
                url = fm.get("url", f"/{sec_id}/{p.stem}/")
                if not url.endswith("/"):
                    url += "/"
                articles.append({
                    "path": p,
                    "filename": p.name,
                    "section": sec_id,
                    "category": cat,
                    "title": fm.get("title", p.stem),
                    "h1": fm.get("h1", p.stem),
                    "url": url,
                    "description": fm.get("description", ""),
                    "author": fm.get("author", AUTHOR_NAME),
                    "reviewed": fm.get("reviewed", ""),
                    "published": fm.get("published", ""),
                    "research_type": fm.get("research_type", ""),
                    "physical_test": fm.get("physical_test", ""),
                    "specifications_contrasted": fm.get("specifications_contrasted", ""),
                    "buyer_opinions": fm.get("buyer_opinions", ""),
                    "primary_sources": fm.get("primary_sources", ""),
                    "information_asset": fm.get("information_asset", ""),
                    "asset_status": fm.get("asset_status", ""),
                    "keywords": fm.get("keywords", []),
                    "body": body,
                    "word_count": len(body.split()),
                })
                
    return articles

_ALL_DRAFTS = load_all_articles()
# La publicación requiere una decisión explícita y una revisión fechada.
# Los archivos sin ambos campos permanecen en el repositorio, fuera del sitio.
REQUIRED_RESEARCH_FIELDS = ("research_type", "physical_test", "specifications_contrasted", "buyer_opinions", "primary_sources", "information_asset", "asset_status")
ALL_ARTICLES = [
    a for a in _ALL_DRAFTS
    if a.get("published") == "true" and a["reviewed"]
    and all(a.get(field) for field in REQUIRED_RESEARCH_FIELDS)
    and a["primary_sources"] == "sí" and a["specifications_contrasted"] == "sí"
    and a["asset_status"] == "verificado"
    and re.search(r'^## Fuentes consultadas\s*$', a["body"], re.MULTILINE)
    and "Dato documentado" in a["body"]
    and "Análisis TallerLab" in a["body"]
]
def get_published_observatory_paths():
    from observatorio.estatico import published_observatory_paths
    static_paths = published_observatory_paths()
    if static_paths:
        return static_paths
    categories = [c for c in ('compresores','hidrolavadoras','generadores') if category_has_published_data(c)]
    if not categories:
        return []
    return ['/datos/precios-herramientas-argentina/','/datos/precios/metodologia/'] + [f'/datos/precios/{c}/' for c in categories]

PUBLIC_SECTIONS = {a["section"] for a in ALL_ARTICLES}
INDEXABLE_PATHS = tuple(dict.fromkeys(
    ["/", "/comunidad/", "/comunidad/criterios/", "/como-trabajamos/", "/autor/joaquin-vallasciani/", "/contacto/", "/privacidad/"]
    + list(RELEVAMIENTO_PATHS)
    + list(ALERTAS_PATHS)
    + ['/alertas/metodologia/']
    + list(COMPATIBILITY_PATHS)
    + list(TALLERLAB_DATA_PATHS)
    + [f"/{section}/" for section in PUBLIC_SECTIONS]
    + [article["url"] for article in ALL_ARTICLES]
))
INDEXABLE_PATH_SET = set(INDEXABLE_PATHS) | set(OBSERVATORY_PATHS) | set(OBSERVATORY_DOWNLOAD_PATHS) | set(COMPATIBILITY_DOWNLOAD_PATHS) | set(TALLERLAB_DATA_DOWNLOAD_PATHS) | {COMPATIBILITY_SEARCH_PATH}

def validate_published_links():
    """Falla al iniciar si cualquier artículo publicado contiene una ruta inválida."""
    errors = []
    for article in ALL_ARTICLES:
        try:
            validar_html(MARKDOWN.render(article["body"]), article["url"], INDEXABLE_PATH_SET, SITE_URL)
        except ValueError as error:
            errors.append(f"{article['filename']}: {error}")
    if errors:
        raise ValueError("Validación de publicación fallida:\n" + "\n".join(errors))

validate_published_links()

def absolute_url(path):
    return SITE_URL + path

# Perfiles oficiales de la marca (sameAs y pie de página). Solo cuentas activas.
SOCIAL_PROFILES = (
    ("Instagram", "https://www.instagram.com/tallerlabarg/"),
    ("TikTok", "https://www.tiktok.com/@tallerlab"),
    ("YouTube", "https://www.youtube.com/channel/UCOUGV2YAHP6joTT00_2hjIg"),
)

def organization_schema():
    return {
        "@type": "Organization",
        "@id": absolute_url("/") + "#organization",
        "name": "TallerLab",
        "url": absolute_url("/"),
        "logo": {
            "@type": "ImageObject",
            "@id": absolute_url(LOGO_SRC) + "#logo",
            "url": absolute_url(LOGO_SRC),
            "contentUrl": absolute_url(LOGO_SRC),
            "caption": "TallerLab",
        },
        "description": "Guías de herramientas y equipamiento para Argentina basadas en investigación documental, comparación de fuentes y cálculos explicados.",
        "sameAs": [url for _, url in SOCIAL_PROFILES],
    }

def get_tallerlab_data_meta(path):
    if path == TALLERLAB_DATA_HUB_PATH:
        return "Base de Datos Técnica de Herramientas en Argentina", "Fichas técnicas normalizadas, condiciones de medición, variantes regionales de 220V 50Hz y comparador documental de herramientas en Argentina."
    if path == TALLERLAB_DATA_COMPARATOR_PATH:
        return "Comparador Técnico de Herramientas en Argentina", "Compará especificaciones técnicas de herramientas en Argentina lado a lado, con alertas de condiciones de medición no comparables."
    if path == TALLERLAB_DATA_EDITORIAL_LIST_PATH:
        return "Comparativas Técnicas de Herramientas Documentadas", "Comparaciones de valores declarados, fuentes enlazadas y condiciones registradas entre modelos de herramientas."
    if path == TALLERLAB_DATA_METHODOLOGY_PATH:
        return "Metodología Técnica de TallerLab Data", "Criterios de extracción documental, jerarquía de fuentes primarias, estados de especificación y política de exclusión de datos."
    if path == TALLERLAB_DATA_CORRECTIONS_PATH:
        return "Registro Público de Correcciones Técnicas", "Historial cronológico de rectificaciones, actualizaciones de manuales y ajustes documentales en la base de datos TallerLab Data."
    if path == TALLERLAB_DATA_RESEARCH_PATH:
        return "Cobertura de Especificaciones del Catálogo TallerLab", "Cobertura de especificaciones registradas en TallerLab: fuentes, variantes y datos descargables para reproducir los indicadores."
    if path in TALLERLAB_DATA_EDITORIAL_PATHS:
        slug = path.strip("/").split("/")[-1]
        comp = get_editorial_comparison(slug)
        if comp:
            return f"{comp.title} — Comparativa Técnica", "Comparación de especificaciones registradas, fuentes y condiciones entre dos modelos."
        return "Comparativa Técnica", "Comparativa técnica de herramientas."
    if path in TALLERLAB_DATA_TOOL_PATHS:
        slug = path.strip("/").split("/")[-1]
        tool = get_tool_by_slug(slug)
        if tool:
            return f"{tool.brand} {tool.model_name}: ficha técnica y fuentes", tool_meta_description(tool)
        return "Ficha Técnica", "Ficha técnica de herramienta."
    return "TallerLab Data", "Base de datos técnica de herramientas en Argentina."

def tool_meta_description(tool):
    from tallerlab_data.quality import backed_specs
    name = f"{tool.brand} {tool.model_name}"
    backed = backed_specs(tool)
    if not backed:
        return f"{name}: referencias registradas y por qué todavía no se usan para comparar. Fuentes enlazadas y fecha de consulta."
    parts = ", ".join(f"{s.name.lower()} {s.original_value}" for s in backed[:3])
    text = f"{name}: {parts}. Datos localizados en documentación del fabricante, con fuente y fecha de consulta."
    if len(text) > 165:
        parts = ", ".join(f"{s.name.lower()} {s.original_value}" for s in backed[:2])
        text = f"{name}: {parts}. Con fuente del fabricante y fecha de consulta."
    return text


MIN_INDEXABLE_COMPARABLE_ROWS = 3


def _editorial_comparable_rows(slug):
    from tallerlab_data.comparator import compare_tools
    comp = get_editorial_comparison(slug)
    if not comp:
        return 0
    slugs = getattr(comp, 'tool_slugs', None) or [v for k, v in vars(comp).items() if 'slug' in k and k != 'slug']
    return sum(1 for row in compare_tools(list(slugs)).rows if row.is_comparable)


def tool_path_is_indexable(path):
    """Model pages and curated comparisons are only offered to search engines
    when they carry enough backed data to answer the query on their own."""
    if path in TALLERLAB_DATA_EDITORIAL_PATHS:
        return _editorial_comparable_rows(path.strip("/").split("/")[-1]) >= MIN_INDEXABLE_COMPARABLE_ROWS
    if path == "/herramientas/comparaciones/":
        return any(tool_path_is_indexable(p) for p in TALLERLAB_DATA_EDITORIAL_PATHS)
    if path not in TALLERLAB_DATA_TOOL_PATHS:
        return True
    from tallerlab_data.quality import tool_is_indexable
    tool = get_tool_by_slug(path.strip("/").split("/")[-1])
    return bool(tool and tool_is_indexable(tool))


def category_has_published_data(category: str) -> bool:
    try:
        from observatorio.db import query_one
        row = query_one(
            """
            SELECT COUNT(o.id) AS c
            FROM observations o
            JOIN catalog_products cp ON o.product_id = cp.id
            JOIN offers off ON o.offer_id = off.id
            JOIN sources src ON off.source_id = src.id
            WHERE cp.category = ?
              AND o.is_published = 1
              AND o.is_synthetic = 0
              AND o.validation_status='valido'
              AND src.capture_allowed=1 AND src.redistribution_allowed=1 AND src.terms_verified_date IS NOT NULL
              AND src.status = 'habilitada'
              AND off.enabled = 1;
            """,
            (category,)
        )
        return bool(row and row["c"] > 0)
    except Exception:
        return False

def canonical_tag(path, title=None, description=None, og_type=None, robots=None):
    title_override, description_override = title, description
    organization = {"@context": "https://schema.org", **organization_schema()}
    schema = '<script type="application/ld+json">' + json.dumps(organization, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
    article = next((a for a in ALL_ARTICLES if a["url"] == path), None)
    section = path.strip("/").split("/")[0]
    editorial = {
        "/": ("Comparativas de herramientas para elegir mejor en Argentina", "Guías documentales y comparativas para elegir herramientas en Argentina."),
        "/como-trabajamos/": ("Cómo trabajamos en TallerLab", "Fuentes, método de comparación, límites de las pruebas y afiliación."),
        AUTHOR_PATH: (AUTHOR_NAME, "Investigación documental y edición de las guías de TallerLab."),
        "/contacto/": ("Contacto y correcciones", "Cómo enviar consultas y reportar errores en las guías de TallerLab."),
        "/privacidad/": ("Privacidad y datos", "Qué datos se registran al visitar TallerLab y usar sus enlaces comerciales."),
        "/datos/precios-herramientas-argentina/": ("Observatorio de Precios de Herramientas en Argentina", "Relevamiento diario de precios, disponibilidad y condiciones comerciales en Argentina."),
        "/datos/precios/compresores/": ("Precios de Compresores de Aire en Argentina", "Precios observados, mínimos vigentes y series históricas de compresores en Argentina."),
        "/datos/precios/hidrolavadoras/": ("Precios de Hidrolavadoras en Argentina", "Precios observados, mínimos vigentes y series históricas de hidrolavadoras en Argentina."),
        "/datos/precios/metodologia/": ("Metodología del Observatorio de Precios", "Método de recolección, marco legal de fuentes, tratamiento de anomalías y derechos."),
        "/relevamiento-2027/": ("Relevamiento TallerLab 2027: herramientas y oficios en Argentina", "Piloto de investigación sobre herramientas, marcas, baterías y reparaciones en talleres y obras de Argentina."),
        "/relevamiento-2027/metodologia/": ("Borrador de Metodología: Relevamiento TallerLab 2027", "Diseño de investigación, reclutamiento voluntario, controles de calidad y límites estadísticos del estudio."),
    }
    if path in TALLERLAB_DATA_PATHS:
        title, description = get_tallerlab_data_meta(path)
    elif path in COMPATIBILITY_PATHS or path == COMPATIBILITY_SEARCH_PATH or (path.startswith('/compatibilidad/') and '-con-' in path):
        title, description, _ = get_compatibility_meta(path, SITE_URL)
    else:
        title, description = editorial.get(path, (CATEGORY_META.get(section, {}).get("name", "TallerLab"), CATEGORY_META.get(section, {}).get("intro", "Guías documentales de herramientas.")))
    if article:
        title, description = article["h1"], article["description"]
    if title_override is not None:
        title = title_override
    if description_override is not None:
        description = description_override
    from portadas_guias import guide_cover
    cover_article = article or next((a for a in ALL_ARTICLES if a['section'] == section and '/comparativa-general/' in a['url']), None) or next((a for a in ALL_ARTICLES if a['section'] == section), None)
    cover = guide_cover(cover_article) if cover_article else {}
    image_path = cover.get('image', LOGO_SRC)
    image_url = absolute_url(image_path)
    tags = {
        "og:type": og_type or ("article" if article else "website"), "og:locale": "es_AR",
        "og:site_name": "TallerLab", "og:title": title, "og:description": description,
        "og:url": absolute_url(path), "og:image": image_url,
        "og:image:alt": cover.get('alt', 'TallerLab'),
        "twitter:card": "summary_large_image", "twitter:title": title,
        "twitter:description": description, "twitter:image": image_url,
    }
    social = "".join(f'<meta {"name" if key.startswith("twitter:") else "property"}="{key}" content="{escape(value, quote=True)}">' for key, value in tags.items())
    breadcrumb = ""
    if path != "/":
        items = [{"@type": "ListItem", "position": 1, "name": "Inicio", "item": absolute_url("/")}]
        category_path = f"/{section}/"
        if section in CATEGORY_META and path != category_path:
            items.append({"@type": "ListItem", "position": 2, "name": CATEGORY_META[section]["name"], "item": absolute_url(category_path)})
        elif path.startswith("/datos/precios/"):
            items.append({"@type": "ListItem", "position": 2, "name": "Observatorio", "item": absolute_url("/datos/precios-herramientas-argentina/")})
        elif path == "/relevamiento-2027/metodologia/":
            items.append({"@type": "ListItem", "position": 2, "name": "Relevamiento 2027", "item": absolute_url("/relevamiento-2027/")})
        elif path in COMPATIBILITY_PATHS or path == COMPATIBILITY_SEARCH_PATH or (path.startswith('/compatibilidad/') and '-con-' in path):
            if path != "/compatibilidad/":
                items.append({"@type": "ListItem", "position": 2, "name": "Compatibilidad", "item": absolute_url("/compatibilidad/")})
        elif path.startswith("/alertas/") and path != "/alertas/":
            items.append({"@type": "ListItem", "position": 2, "name": "Documentación y alertas", "item": absolute_url("/alertas/")})
        elif path.startswith("/herramientas/"):
            items.append({"@type": "ListItem", "position": 2, "name": "TallerLab Data", "item": absolute_url("/herramientas/")})
            if path.startswith("/herramientas/comparar/") and path != "/herramientas/comparar/":
                items.append({"@type": "ListItem", "position": 3, "name": "Comparaciones", "item": absolute_url("/herramientas/comparaciones/")})
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": title, "item": absolute_url(path)})
        breadcrumb = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}, ensure_ascii=False).replace("<", "\\u003c") + '</script>'

    dataset_schema = ""
    robots_meta = ""
    if path.startswith("/datos/precios/"):
        cat = path.strip("/").split("/")[-1]
        if cat in ("compresores", "hidrolavadoras", "generadores"):
            if category_has_published_data(cat):
                dataset_schema = get_dataset_schema_json(cat)
            else:
                robots_meta = '<meta name="robots" content="noindex, follow">'
    elif path == "/datos/precios-herramientas-argentina/":
        if not any(category_has_published_data(c) for c in ("compresores", "hidrolavadoras", "generadores")):
            robots_meta = '<meta name="robots" content="noindex, follow">'

    tallerlab_schema = ""
    if path in TALLERLAB_DATA_TOOL_PATHS:
        tool_slug = path.strip("/").split("/")[-1]
        tool_obj = get_tool_by_slug(tool_slug)
        if tool_obj:
            tallerlab_schema = get_tool_product_schema(tool_obj, absolute_url(path)) + get_tool_page_schema(tool_obj, absolute_url(path))
            if not tool_path_is_indexable(path):
                robots_meta = '<meta name="robots" content="noindex, follow">'
    elif path == TALLERLAB_DATA_RESEARCH_PATH:
        tallerlab_schema = get_research_study_schema(absolute_url(path), absolute_url("/herramientas/investigacion/descargar-datos.csv"))
    elif (path in TALLERLAB_DATA_EDITORIAL_PATHS or path == "/herramientas/comparaciones/") and not tool_path_is_indexable(path):
        robots_meta = '<meta name="robots" content="noindex, follow">'

    elif path == AUTHOR_PATH:
        profile_page = {"@context": "https://schema.org", "@type": "ProfilePage",
                        "url": absolute_url(AUTHOR_PATH),
                        "mainEntity": {**author_schema(), "knowsAbout": [meta["name"] for meta in CATEGORY_META.values()]}}
        perfil = author_profile()
        if perfil["experiencia"] or perfil["formacion"]:
            profile_page["mainEntity"]["description"] = " ".join(x for x in (perfil["experiencia"], perfil["formacion"]) if x)
        tallerlab_schema = '<script type="application/ld+json">' + json.dumps(profile_page, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
    elif path in RELEVAMIENTO_PATHS and not relevamiento_abierto():
        # Mientras el relevamiento no recibe respuestas, su aviso no compite en buscadores.
        robots_meta = '<meta name="robots" content="noindex, follow">'

    if robots:
        robots_meta = f'<meta name="robots" content="{escape(robots, quote=True)}">'
    return robots_meta + f'<link rel="canonical" href="{escape(absolute_url(path), quote=True)}">' + schema + dataset_schema + tallerlab_schema + social + breadcrumb

def render_observatory_page(path):
    if path == "/datos/precios-herramientas-argentina/":
        content = render_observatory_hub_html()
        title = "Observatorio de Precios de Herramientas en Argentina"
        desc = "Relevamiento diario de precios, disponibilidad y condiciones comerciales en Argentina."
    elif path == "/datos/precios/compresores/":
        content = render_observatory_category_html("compresores")
        title = "Precios de Compresores de Aire en Argentina"
        desc = "Precios observados, mínimos vigentes y series históricas de compresores en Argentina."
    elif path == "/datos/precios/hidrolavadoras/":
        content = render_observatory_category_html("hidrolavadoras")
        title = "Precios de Hidrolavadoras en Argentina"
        desc = "Precios observados, mínimos vigentes y series históricas de hidrolavadoras en Argentina."
    elif path == "/datos/precios/metodologia/":
        content = render_observatory_methodology_html()
        title = "Metodología del Observatorio de Precios"
        desc = "Método de recolección, marco legal de fuentes, tratamiento de anomalías y derechos."
    elif path == '/datos/precios/generadores/':
        content = render_observatory_category_html('generadores')
        title = 'Precios de Generadores en Argentina'
        desc = 'Ofertas observadas e historial por modelo exacto.'
    else:
        return render_not_found(path)

    return HTML_SHELL.format(
        PAGE_TITLE=title,
        CANONICAL_TAG=canonical_tag(path),
        PAGE_DESC=escape(desc, quote=True),
        PORT=PORT,
        CONTENT=content,
        LOGO_SRC=LOGO_SRC,
    )

def render_relevamiento_view(kind, query_params=None):
    if kind == "formulario":
        path = "/relevamiento-2027/"
        title = "Relevamiento TallerLab 2027: herramientas y oficios en Argentina"
        desc = "Piloto de investigación sobre herramientas, marcas, baterías y reparaciones en talleres y obras de Argentina."
        content = render_relevamiento_page(query_params)
        return HTML_SHELL.format(
            PAGE_TITLE=title,
            PAGE_DESC=escape(desc, quote=True),
            CANONICAL_TAG=canonical_tag(path),
            PORT=PORT,
            CONTENT=content,
            LOGO_SRC=LOGO_SRC,
        )
    elif kind == "metodologia":
        path = "/relevamiento-2027/metodologia/"
        title = "Borrador de Metodología: Relevamiento TallerLab 2027"
        desc = "Diseño de investigación, reclutamiento voluntario, controles de calidad y límites estadísticos del estudio."
        content = render_metodologia_page()
        return HTML_SHELL.format(
            PAGE_TITLE=title,
            PAGE_DESC=escape(desc, quote=True),
            CANONICAL_TAG=canonical_tag(path),
            PORT=PORT,
            CONTENT=content,
            LOGO_SRC=LOGO_SRC,
        )
    elif kind == "admin":
        title = "Panel Privado: Relevamiento 2027"
        desc = "Panel de moderación y estadísticas."
        content = render_admin_dashboard(query_params)
        return HTML_SHELL.format(
            PAGE_TITLE=title,
            PAGE_DESC=escape(desc, quote=True),
            CANONICAL_TAG='<meta name="robots" content="noindex, nofollow">',
            PORT=PORT,
            CONTENT=content,
            LOGO_SRC=LOGO_SRC,
        )
    return render_not_found("/relevamiento-2027/")

def render_alertas_page(path):
    from alertas_seo import HUB_TITULO, HUB_DESCRIPCION, dossier_meta, expediente_indexable, hub_schema
    from alertas_datos import cargar_expedientes, expediente_publico
    if path == "/alertas/":
        content = render_alerts_hub_page()
        title, desc = HUB_TITULO, HUB_DESCRIPCION
        schema = hub_schema(cargar_expedientes(), absolute_url("/alertas/"), organization_schema())
        schema_tag = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
        return HTML_SHELL.format(
            PAGE_TITLE=title,
            CANONICAL_TAG=canonical_tag("/alertas/", title=title, description=desc) + schema_tag,
            PAGE_DESC=escape(desc, quote=True),
            PORT=PORT,
            CONTENT=content,
            LOGO_SRC=LOGO_SRC,
        )
    elif path.startswith("/alertas/") and path.endswith("/"):
        slug = path[len("/alertas/"):-1]
        exp = obtener_expediente(slug)
        if exp is None:
            return render_not_found(path)
        content = render_model_dossier_page(exp)
        publico = expediente_publico(exp)
        title, desc = dossier_meta(publico)
        robots = None if expediente_indexable(publico) else "noindex, follow"
        schema = dossier_schema(publico, absolute_url(path))
        schema_tag = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
        return HTML_SHELL.format(
            PAGE_TITLE=title,
            CANONICAL_TAG=canonical_tag(path, title=title, description=desc, og_type="article", robots=robots) + schema_tag,
            PAGE_DESC=escape(desc, quote=True),
            PORT=PORT,
            CONTENT=content,
            LOGO_SRC=LOGO_SRC,
        )
    return render_not_found(path)

def render_compatibility_page(path, query_params=None):
    from compatibilidad.catalog import refresh_published_state
    refresh_published_state()
    content = render_compatibility_page_content(path, query_params)
    if content is None:
        return render_not_found(path)
    content='<link rel="stylesheet" href="/assets/compatibilidad.css"><link rel="stylesheet" href="/assets/compatibilidad-navegacion.css">'+content+'<script defer src="/assets/compatibilidad.js"></script>'
    title, desc, extra_schema = get_compatibility_meta(path, SITE_URL)
    if path == COMPATIBILITY_SEARCH_PATH:
        canonical_meta = '<meta name="robots" content="noindex, follow">\n  <link rel="canonical" href="' + escape(absolute_url('/compatibilidad/'), quote=True) + '">'
    else:
        canonical_meta = canonical_tag(path)
        if extra_schema:
            canonical_meta += extra_schema

    return HTML_SHELL.format(
        PAGE_TITLE=title,
        CANONICAL_TAG=canonical_meta,
        PAGE_DESC=escape(desc, quote=True),
        PORT=PORT,
        CONTENT=content,
        LOGO_SRC=LOGO_SRC,
    )

def render_tallerlab_data_page(path, query_params=None):
    if path == TALLERLAB_DATA_HUB_PATH:
        cat = (query_params or {}).get("categoria")
        content = render_tools_hub_page(cat)
    elif path == TALLERLAB_DATA_COMPARATOR_PATH:
        params = query_params or {}
        selected = [params.get(f"m{number}") for number in range(1, 5) if params.get(f"m{number}")] or None
        content = render_tool_comparator_page(selected, params.get('categoria'), params.get('familia'))
    elif path == TALLERLAB_DATA_EDITORIAL_LIST_PATH:
        content = render_editorial_comparisons_list_page()
    elif path in TALLERLAB_DATA_EDITORIAL_PATHS:
        slug = path.strip("/").split("/")[-1]
        comp = get_editorial_comparison(slug)
        if not comp:
            return render_not_found(path)
        content = render_editorial_comparison_page(slug)
    elif path == TALLERLAB_DATA_METHODOLOGY_PATH:
        content = render_data_methodology_page()
    elif path == TALLERLAB_DATA_CORRECTIONS_PATH:
        content = render_corrections_log_page()
    elif path == TALLERLAB_DATA_RESEARCH_PATH:
        content = render_research_study_page()
    elif path in TALLERLAB_DATA_TOOL_PATHS:
        slug = path.strip("/").split("/")[-1]
        tool = get_tool_by_slug(slug)
        if not tool:
            return render_not_found(path)
        content = render_tool_detail_page(tool)
    else:
        return render_not_found(path)

    title, desc = get_tallerlab_data_meta(path)
    return HTML_SHELL.format(
        PAGE_TITLE=title,
        CANONICAL_TAG=('<meta name="robots" content="noindex, follow">\n' if path == TALLERLAB_DATA_COMPARATOR_PATH and query_params else "") + canonical_tag(path),
        PAGE_DESC=escape(desc, quote=True),
        PORT=PORT,
        CONTENT=content,
        LOGO_SRC=LOGO_SRC,
    )

def render_sitemap():
    paths = tuple(dict.fromkeys([p for p in INDEXABLE_PATHS if p not in OBSERVATORY_PATHS]+get_published_observatory_paths()))
    from compatibilidad.catalog import refresh_published_state, PRODUCTS_BY_SLUG, CATALOG_PRODUCTS
    from compatibilidad.presentation import relationship_paths
    refresh_published_state()
    paths=tuple(dict.fromkeys(paths+relationship_paths()+('/compatibilidad/cambios/',)))
    def compatibility_indexable(path):
        if path.startswith(('/baterias/','/cargadores/','/herramientas-bateria/')):
            product=PRODUCTS_BY_SLUG.get(path.rstrip('/').split('/')[-1])
            return bool(product and product.status=='publicado')
        if path.startswith('/plataformas/'):
            platform=path.rstrip('/').split('/')[-1]
            return any(p.platform_id==platform and p.status=='publicado' for p in CATALOG_PRODUCTS)
        return True
    paths=tuple(p for p in paths if compatibility_indexable(p) and tool_path_is_indexable(p))
    from alertas_seo import sitemap_alertas
    try:
        alertas_lastmod, alertas_excluidas = sitemap_alertas()
    except Exception:
        alertas_lastmod, alertas_excluidas = {}, set()
    paths=tuple(dict.fromkeys(paths+tuple(alertas_lastmod) ))
    paths=tuple(p for p in paths if p not in alertas_excluidas)
    # Comunidad: solo modelos y preguntas con contenido suficiente, con su fecha de última actividad.
    try:
        from comunidad.components import community_sitemap_lastmod, community_sitemap_excluded
        comunidad_lastmod = community_sitemap_lastmod()
        comunidad_excluidas = community_sitemap_excluded()
    except Exception:
        # Si no se puede confirmar que la portada sea indexable, no se declara (nunca sitemap + noindex).
        comunidad_lastmod, comunidad_excluidas = {}, {'/comunidad/'}
    paths=tuple(dict.fromkeys(paths+tuple(comunidad_lastmod)))
    # La portada de la comunidad no va al sitemap mientras sea «noindex» (todavía sin páginas de modelo con contenido).
    paths=tuple(p for p in paths if p not in comunidad_excluidas)
    if not relevamiento_abierto():
        paths=tuple(p for p in paths if p not in RELEVAMIENTO_PATHS)
    alertas_lastmod = {**comunidad_lastmod, **alertas_lastmod}
    try:
        from compatibilidad.presentation import compatibility_lastmod
        alertas_lastmod = {**compatibility_lastmod(), **alertas_lastmod}
    except Exception:
        pass
    def sitemap_entry(path):
        lastmod = alertas_lastmod.get(path)
        extra = f"<lastmod>{escape(lastmod)}</lastmod>" if lastmod else ""
        return f"  <url><loc>{escape(absolute_url(path))}</loc>{extra}</url>\n"
    entries = "".join(sitemap_entry(path) for path in paths)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + entries + '</urlset>\n'

def render_robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {absolute_url('/sitemap.xml')}\n"

AFFILIATE_URLS.update(
    url for article in ALL_ARTICLES
    for url in re.findall(r"https://meli\.la/[A-Za-z0-9]+", article["body"])
)
AFFILIATE_URLS.update(item['url'] for path, choice in AMOLADORA_CHOICES.items()
                      if path in INDEXABLE_PATH_SET for item in choice['items'])
AFFILIATE_URLS.update(item['url'] for path, item in CONTEXTUAL_CHOICES.items()
                      if path in INDEXABLE_PATH_SET)

def validate_affiliate_click(data):
    """Valida el evento compartido por el servidor local y la entrada Flask."""
    if not isinstance(data, dict):
        raise ValueError("Invalid click event")
    product = data.get("product", "")
    page = data.get("page", "")
    placement = data.get("placement", "")
    if (product not in AFFILIATE_URLS or not isinstance(page, str)
            or not page.startswith("/") or len(page) > 250
            or not isinstance(placement, str)
            or not re.fullmatch(r"[a-z0-9-]{1,64}", placement)):
        raise ValueError("Invalid click event")
    return {"at": datetime.now(timezone.utc).isoformat(), "product": product, "page": page, "placement": placement}

def render_affiliate_shelf(section_id, products=None, ctas=None, editorial=None):
    """Muestra publicaciones concretas ya enlazadas en las guías del sitio."""
    selected = products if products is not None else [(section_id, item) for item in AFFILIATE_PRODUCTS.get(section_id, [])]
    if not selected:
        return ""
    type_counts = {}
    for category, (_, _, url, _) in selected:
        kind = category if editorial else COMPARE_TYPES.get(url, category)
        type_counts[kind] = type_counts.get(kind, 0) + 1
    has_comparison = any(count >= 2 for count in type_counts.values())
    cards = ""
    for index, (category, (name, detail, url, guide)) in enumerate(selected, 1):
        category_name = CATEGORY_META[category]["name"]
        facts = PRODUCT_FACTS.get(url)
        brand = facts["brand"] if facts else "Marca sin confirmar"
        model = facts["model"] if facts else "Modelo sin confirmar"
        use = facts["use"] if facts else "Uso a verificar"
        power = facts["power"] if facts else "Alimentación a verificar"
        specs = facts["specs"] if facts else UNVERIFIED_SPECS.get(category, ["Ficha técnica no informada"])
        includes = facts["includes"] if facts else "Contenido del kit a confirmar en la publicación"
        affiliate = url in AFFILIATE_URLS and es_enlace_afiliado(url)
        action_rel = 'nofollow sponsored noopener noreferrer' if affiliate else 'noopener noreferrer'
        placement_name = (editorial or {}).get('placement', 'shelf-'+section_id)
        placement = f' data-affiliate-placement="{escape(placement_name, quote=True)}"' if affiliate else ''
        cta_label = (ctas or {}).get(url, (facts or {}).get('cta',
                     f'Ver precio de {brand} {model}' if category == 'hidrolavadoras' else 'Ver precio en Mercado Libre'))
        purchase_button = (f'<a class="offer-button" href="{escape(url, quote=True)}" target="_blank" rel="{action_rel}"{placement}>{escape(cta_label)} ↗</a>'
                           if affiliate else '')
        if facts and facts.get("image") and not facts.get("illustrative"):
            media = f'<img src="{escape(facts["image"], quote=True)}" alt="{escape(brand + " " + model, quote=True)}" width="{facts.get("image_width", 800)}" height="{facts.get("image_height", 800)}" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
        else:
            media = '<span class="offer-no-photo">Foto no disponible</span>'
        source = (f'<p class="offer-evidence">{escape(facts["evidence_label"])} · sin prueba física de TallerLab</p>' if facts and facts.get("evidence_label") else '')
        compare_type = category if editorial else COMPARE_TYPES.get(url, category)
        labels = (editorial or {}).get('labels') or COMPARE_ROWS.get(compare_type, COMPARE_ROWS.get(category, ("Dato principal", "Dato secundario", "Dato adicional")))
        compare_labels = escape(json.dumps(labels, ensure_ascii=False), quote=True)
        compare_details = escape(json.dumps(specs[:3] if editorial else COMPARE_DETAILS.get(url, specs[:3]), ensure_ascii=False), quote=True)
        cards += f"""
        <article class="offer-card" data-brand="{escape(brand, quote=True)}" data-use="{escape(use, quote=True)}" data-power="{escape(power, quote=True)}" data-product="{escape(url, quote=True)}" data-compare-type="{escape(compare_type, quote=True)}" data-compare-labels="{compare_labels}" data-compare-details="{compare_details}">
          <div class="offer-card-top"><span>{index:02d} / {escape(category_name)}</span><span>{'PUBLICACIÓN CONCRETA' if affiliate else 'MODELO DOCUMENTADO'}</span></div>
          <div class="offer-photo">{media}</div>
          <h3>{escape(brand)} · {escape(model)}</h3>
          <p class="offer-description">{escape(detail)} · {escape(name)}</p>
          {f'<p class="offer-warning">{escape(facts["warning"])}</p>' if facts and facts.get("warning") else ''}
          <p class="offer-use"><strong>Para:</strong> {escape(use)}</p>
          <ul class="offer-specs">{"".join(f"<li>{escape(spec)}</li>" for spec in specs)}</ul>
          <p class="offer-includes"><strong>Incluye:</strong> {escape(includes)}</p>
          {source}
          <div class="offer-actions">
            {purchase_button}
            <a class="offer-guide" href="{escape(guide, quote=True)}">Leer guía →</a>
          </div>
          {'<label class="compare-select"><input type="checkbox" class="compare-checkbox"> Comparar</label>' if type_counts[compare_type] >= 2 else ''}
        </article>
        """
    title = "Publicación disponible en Mercado Libre" if len(selected) == 1 else ("Publicaciones para comparar" if has_comparison else "Publicaciones disponibles")
    if section_id == "inicio" and len(selected) > 1:
        title = "Del taller a la compra"
    if editorial:
        title = 'Compará los modelos de esta guía' if len(selected) > 1 else 'Modelo documentado para esta guía'
    explanation = (editorial or {}).get('reason', 'Datos declarados en la fuente indicada, sin medición propia. La presión máxima no equivale a presión de trabajo; el caudal sin condición de medición no acredita caudal entregado. Revisá código, kit y vendedor.')
    filters = '''<div class="offer-filters" aria-label="Filtrar productos">
        <label>Marca <select class="filter-brand"><option value="">Todas</option></select></label>
        <label>Uso <select class="filter-use"><option value="">Todos</option></select></label>
        <label>Alimentación <select class="filter-power"><option value="">Todas</option></select></label>
      </div>''' if len(selected) > 1 else ''
    return f"""
    <section class="affiliate-shelf" aria-label="{'Modelos y enlaces de esta guía' if editorial else 'Publicaciones con enlace de afiliado'}"{(' data-guide-comparison="true"' if editorial else '')}>
      <div class="affiliate-heading">
        <div><span class="section-kicker">SELECCIÓN DE PRODUCTOS</span><h2>{title}</h2></div>
        <p>{escape(explanation)}</p>
      </div>
      {filters}
      <div class="offer-grid">{cards}</div>
      {'<p class="offer-empty" hidden>No hay productos con esos filtros.</p>' if filters else ''}
      {'<div class="compare-panel" hidden aria-live="polite"></div>' if has_comparison else ''}
      {'<p class="buying-disclosure">Comparación documental, sin prueba física. Las fichas de fabricante no confirman stock. En los enlaces de afiliado TallerLab puede recibir una comisión, sin costo adicional para vos.</p>' if editorial else ''}
    </section>
    """

HTML_SHELL = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{PAGE_TITLE} · TallerLab</title>
  <meta name="description" content="{PAGE_DESC}">
  <link rel="icon" href="/favicon.svg?v=2" type="image/svg+xml">
  {CANONICAL_TAG}
  <link rel="preload" href="/assets/fonts/plus-jakarta-sans-latin-v1.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/fonts/fonts.css?v=1">
  <style>
    :root {{
      --bg: #0d1117;
      --bg-card: #161b22;
      --bg-card-hover: #1f242c;
      --bg-surface: #12161f;
      --text: #ffffff;
      --text-muted: #8b949e;
      --border: #30363d;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --orange: #ff5500;
      --orange-light: #ff7733;
      --orange-hover: #e64d00;
      --orange-glow: rgba(255, 85, 0, 0.25);
      --orange-bg: rgba(255, 85, 0, 0.12);
      --accent: #38bdf8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    a {{ color: inherit; text-decoration: none; transition: all 0.15s ease; }}
    
    /* Header & Nav */
    body > header {{
      background: rgba(13, 17, 23, 0.96);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 50;
    }}
    .nav-container {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 0.85rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-shrink: 0;
    }}
    .logo-img {{
      height: 36px;
      width: auto;
      display: block;
      object-fit: contain;
    }}
    .nav-links {{
      display: flex;
      gap: 0.35rem;
      align-items: center;
      overflow-x: auto;
      white-space: nowrap;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }}
    .nav-links::-webkit-scrollbar {{ display: none; }}
    .nav-btn {{
      padding: 0.45rem 0.85rem;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--text-muted);
      border: 1px solid transparent;
      transition: all 0.15s ease;
    }}
    .nav-btn:hover, .nav-btn.active {{
      color: #fff;
      background: var(--bg-card);
      border-color: var(--border);
    }}
    
    /* Main Layout */
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 2.5rem 1.25rem;
      flex: 1;
      width: 100%;
    }}
    
    /* Hero Split Layout */
    .hero-container {{
      position: relative;
      padding: 3rem 2.5rem 2.5rem;
      margin-bottom: 2rem;
      background: radial-gradient(ellipse 80% 60% at 50% -15%, rgba(255, 85, 0, 0.22), transparent 75%), #0d1117;
      border-radius: 20px;
      border: 1px solid var(--border-subtle);
      overflow: hidden;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 2.5rem;
      align-items: center;
    }}
    .hero-col-left {{
      text-align: left;
    }}
    .hero-eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(255, 85, 0, 0.12);
      border: 1px solid rgba(255, 85, 0, 0.3);
      color: var(--orange-light);
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      margin-bottom: 1.25rem;
    }}
    .hero-title {{
      font-size: 3.1rem;
      font-weight: 900;
      letter-spacing: -0.04em;
      line-height: 1.15;
      margin-bottom: 1.2rem;
      color: #ffffff;
    }}
    .text-orange {{
      color: var(--orange);
      background: linear-gradient(135deg, #ff7a29 0%, #ff5500 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-desc {{
      color: #94a3b8;
      font-size: 1.15rem;
      line-height: 1.6;
      margin-bottom: 2rem;
    }}
    
    /* Right side drill mockup display */
    .hero-col-right {{
      display: flex;
      justify-content: center;
      align-items: center;
      position: relative;
    }}
    .hero-media-wrapper {{
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(255, 85, 0, 0.2);
      border: 1px solid var(--border);
    }}
    .hero-drill-img {{
      width: 100%;
      max-width: 440px;
      height: 220px;
      display: block;
      object-fit: cover;
    }}
    .handwritten-sticker {{
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: rgba(13, 17, 23, 0.88);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 85, 0, 0.4);
      padding: 0.65rem 0.9rem;
      border-radius: 12px;
      font-family: 'Caveat', cursive;
      font-size: 1.25rem;
      line-height: 1.25;
      color: #fff;
      text-align: center;
      transform: rotate(2deg);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }}
    
    /* CTA button */
    .btn-orange {{
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      background: linear-gradient(135deg, #ff6600 0%, #ff4500 100%);
      color: #ffffff !important;
      font-weight: 700;
      font-size: 1.05rem;
      padding: 0.85rem 1.8rem;
      border-radius: 999px;
      box-shadow: 0 6px 20px rgba(255, 85, 0, 0.35);
      transition: all 0.2s ease;
      border: none;
      cursor: pointer;
    }}
    .btn-orange:hover {{
      background: linear-gradient(135deg, #ff771a 0%, #ff5500 100%);
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(255, 85, 0, 0.45);
    }}
    
    /* Search Box */
    .search-box {{
      position: relative;
      max-width: 580px;
      margin-top: 1.75rem;
    }}
    .search-box input {{
      width: 100%;
      padding: 0.95rem 1.25rem 0.95rem 3rem;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: rgba(22, 27, 34, 0.9);
      backdrop-filter: blur(10px);
      color: #ffffff;
      font-size: 1rem;
      outline: none;
      transition: all 0.2s ease;
    }}
    .search-box input:focus {{
      border-color: var(--orange);
      box-shadow: 0 0 0 3px rgba(255, 85, 0, 0.2);
    }}
    .search-icon {{
      position: absolute;
      left: 1.1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 1.1rem;
    }}
    
    /* Horizontal Category Strip (Mockup style) */
    .category-strip {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.6rem;
      background: rgba(22, 27, 34, 0.9);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 0.75rem 1rem;
      margin-bottom: 3.5rem;
      overflow-x: auto;
      scrollbar-width: none;
    }}
    .category-strip::-webkit-scrollbar {{ display: none; }}
    .category-strip-item {{
      display: flex;
      align-items: center;
      gap: 0.55rem;
      padding: 0.55rem 0.85rem;
      border-radius: 10px;
      font-size: 0.88rem;
      font-weight: 600;
      color: #e2e8f0;
      flex-shrink: 0;
      transition: all 0.15s ease;
    }}
    .category-strip-item:hover {{
      background: rgba(255, 85, 0, 0.12);
      color: var(--orange);
    }}
    .category-strip-item .cat-icon {{ font-size: 1.15rem; }}
    
    /* Section Headers */
    .section-header {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 1.25rem;
    }}
    .section-title {{
      font-size: 1.5rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 0.6rem;
    }}
    .section-subtitle {{
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-top: 0.25rem;
    }}
    .section-link {{
      color: var(--orange);
      font-size: 0.88rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
    }}
    
    /* Card Grid (Mockup 16:9 style) */
    .article-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.35rem;
    }}
    .card-media {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.25s ease;
    }}
    .card-media:hover {{
      transform: translateY(-4px);
      border-color: rgba(255, 85, 0, 0.45);
      box-shadow: 0 14px 30px rgba(0, 0, 0, 0.45), 0 0 15px rgba(255, 85, 0, 0.15);
    }}
    .card-thumb {{
      position: relative;
      height: 145px;
      width: 100%;
      background: #111722;
      overflow: hidden;
      display: flex;
      align-items: flex-end;
      padding: 0.85rem;
    }}
    .thumb-img {{
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      object-fit: cover;
    }}
    .thumb-pattern {{
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      pointer-events: none;
    }}
    .thumb-overlay {{
      position: absolute;
      top: 0.75rem;
      left: 0.75rem;
      right: 0.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 2;
    }}
    .thumb-badge {{
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      color: #ffffff;
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      padding: 0.2rem 0.55rem;
      border-radius: 5px;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .thumb-time {{
      background: rgba(0, 0, 0, 0.8);
      color: #cbd5e1;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
    }}
    .thumb-spec {{
      position: relative;
      z-index: 2;
      color: #ffffff;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
    }}
    
    .card-body {{
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      flex: 1;
    }}
    .card-title {{
      font-size: 1.05rem;
      font-weight: 700;
      line-height: 1.35;
      color: #ffffff;
      margin-bottom: 0.5rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      transition: color 0.15s;
    }}
    .card-media:hover .card-title {{
      color: var(--orange);
    }}
    .card-desc {{
      color: var(--text-muted);
      font-size: 0.86rem;
      line-height: 1.5;
      margin-bottom: 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      flex: 1;
    }}
    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: var(--orange);
      font-size: 0.82rem;
      font-weight: 700;
      border-top: 1px solid var(--border-subtle);
      padding-top: 0.75rem;
    }}
    
    /* Category Featured Card */
    .featured-hero-card {{
      background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(13, 17, 23, 0.95) 100%);
      border: 1px solid var(--orange);
      border-radius: 16px;
      padding: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 2.5rem;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 85, 0, 0.15);
      transition: all 0.25s ease;
    }}
    .featured-hero-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 25px rgba(255, 85, 0, 0.25);
    }}
    
    /* Article Reader */
    .article-container {{ max-width: 880px; margin: 0 auto; }}
    .breadcrumb {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 1.5rem;
      display: flex;
      gap: 0.5rem;
      align-items: center;
      flex-wrap: wrap;
    }}
    .breadcrumb a:hover {{ color: var(--orange); }}
    .article-header {{
      margin-bottom: 2.25rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.75rem;
    }}
    .meta-bar {{
      display: flex;
      gap: 0.85rem;
      align-items: center;
      flex-wrap: wrap;
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-bottom: 0.75rem;
    }}
    .article-header h1 {{
      font-size: 2.5rem;
      font-weight: 900;
      letter-spacing: -0.03em;
      line-height: 1.2;
      color: #ffffff;
      margin-bottom: 0.85rem;
    }}
    .article-lead {{
      color: #94a3b8;
      font-size: 1.12rem;
      line-height: 1.65;
    }}
    
    /* Markdown Body */
    .markdown-body {{ font-size: 1.05rem; line-height: 1.8; color: #cbd5e1; }}
    .markdown-body h2 {{
      font-size: 1.6rem; font-weight: 800; color: #ffffff;
      margin-top: 2.5rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;
      letter-spacing: -0.02em;
    }}
    .markdown-body h3 {{ font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-top: 1.75rem; margin-bottom: 0.75rem; }}
    .markdown-body p {{ margin-bottom: 1.35rem; }}
    .markdown-body ul, .markdown-body ol {{ margin-bottom: 1.35rem; padding-left: 1.5rem; }}
    .markdown-body li {{ margin-bottom: 0.4rem; }}
    .markdown-body table {{
      width: 100%; border-collapse: collapse; margin: 1.75rem 0; font-size: 0.92rem;
      background: var(--bg-card); border-radius: 10px; overflow: hidden; border: 1px solid var(--border);
    }}
    .markdown-body th, .markdown-body td {{
      padding: 0.85rem 1rem; border: 1px solid var(--border); text-align: left;
    }}
    .markdown-body th {{ background: rgba(0, 0, 0, 0.4); color: var(--orange-light); font-weight: 700; }}
    .markdown-body blockquote {{
      border-left: 4px solid var(--orange); padding: 0.85rem 1.25rem; background: var(--orange-bg);
      margin: 1.75rem 0; border-radius: 0 8px 8px 0; color: #f1f5f9; font-size: 0.98rem;
    }}
    .markdown-body code {{
      font-family: 'JetBrains Mono', monospace; background: rgba(255, 255, 255, 0.08);
      padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.9em; color: #fcd34d;
    }}
    
    /* CTA Mercado Libre */
    .btn-mercado-libre {{
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      background: linear-gradient(135deg, #ffe600 0%, #ffc800 100%);
      color: #1a1e29 !important;
      font-weight: 800;
      font-size: 1.05rem;
      padding: 0.95rem 1.8rem;
      border-radius: 12px;
      text-decoration: none !important;
      margin: 1.5rem 0;
      transition: all 0.2s ease;
      box-shadow: 0 4px 15px rgba(255, 230, 0, 0.25);
    }}
    .btn-mercado-libre:hover {{
      background: linear-gradient(135deg, #fff033 0%, #ffd000 100%);
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(255, 230, 0, 0.4);
    }}
    
    /* Trust Footer */
    .trust-footer {{
      margin-top: 4rem;
      border-top: 1px solid var(--border);
      padding: 1.5rem;
      background: var(--bg-surface);
      border-radius: 12px;
      color: var(--text-muted);
      font-size: 0.86rem;
      line-height: 1.6;
    }}
    .trust-footer strong {{ color: #ffffff; }}
    
    /* Responsive Mobile */
    @media (max-width: 860px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .hero-col-right {{ display: none; }}
      .hero-col-left {{ text-align: center; }}
      .hero-title {{ font-size: 2.2rem; }}
      .hero-desc {{ font-size: 1rem; }}
      .article-header h1 {{ font-size: 1.85rem; }}
      .article-grid {{ grid-template-columns: 1fr; }}
      .category-strip {{ padding: 0.5rem; }}
      .category-strip-item {{ padding: 0.4rem 0.6rem; font-size: 0.82rem; }}
    }}
    
    /* Footer */
    footer {{
      border-top: 1px solid var(--border);
      padding: 2.5rem 1.25rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.88rem;
      background: #090c10;
      margin-top: 4rem;
    }}
  </style>
  <link rel="stylesheet" href="/assets/site.css?v=21">
  <script src="/assets/commerce.js?v=4" defer></script>
</head>
<body>
  <a class="skip-link" href="#contenido-principal">Saltar al contenido</a>
  <header>
    <div class="nav-container">
      <div class="home-nav-tools"><a href="/#home-search-form" aria-label="Ir al buscador"><svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg></a><details class="home-mobile-menu"><summary aria-label="Abrir menú"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></summary><nav aria-label="Menú de navegación"><a href="/">Inicio</a><a href="/herramientas/">Herramientas</a><a href="/datos/precios-herramientas-argentina/">Precios</a><a href="/comunidad/">Comunidad</a><a href="/como-trabajamos/">Cómo trabajamos</a></nav></details></div>
      <a href="/" class="logo">
        <img src="{LOGO_SRC}" alt="TallerLab" class="logo-img" width="952" height="284">
      </a>
      <nav class="nav-links">
        <a href="/" class="nav-btn">Inicio</a>
        <a href="/herramientas/" class="nav-btn">Herramientas</a>
        <a href="/datos/precios-herramientas-argentina/" class="nav-btn">Precios</a>
        <a href="/comunidad/" class="nav-btn">Comunidad</a>
        <a href="/como-trabajamos/" class="nav-btn">Cómo trabajamos</a>
      </nav>
    </div>
  </header>

  <main id="contenido-principal" tabindex="-1">
    {CONTENT}
  </main>

  <footer>
    <div style="max-width: 700px; margin: 0 auto;">
      <img src="{LOGO_SRC}" alt="TallerLab" width="952" height="284" style="height: 28px; width: auto; opacity: 0.7; margin-bottom: 0.75rem;">
      <p><strong>TallerLab</strong> · Guías técnicas y comparativas de especificaciones para elegir herramientas en Argentina.</p>
      <p style="margin-top: 0.5rem; font-size: 0.78rem; color: #64748b;">Guías técnicas para elegir mejor cada herramienta.</p>
      <p><a href="/comunidad/">Comunidad</a> · <a href="/compatibilidad/">Compatibilidad de baterías</a> · <a href="/alertas/">Documentación y alertas</a> · <a href="/como-trabajamos/">Metodología</a> · <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani · Autor</a> · <a href="/contacto/">Contacto</a> · <a href="/privacidad/">Privacidad</a></p>
      <p>Seguinos: <a href="https://www.instagram.com/tallerlabarg/" rel="me noopener" target="_blank">Instagram</a> · <a href="https://www.tiktok.com/@tallerlab" rel="me noopener" target="_blank">TikTok</a> · <a href="https://www.youtube.com/channel/UCOUGV2YAHP6joTT00_2hjIg" rel="me noopener" target="_blank">YouTube</a></p>
    </div>
  </footer>
</body>
</html>
"""

from contenido_publico import PublicTemplate
HTML_SHELL = PublicTemplate(HTML_SHELL)


def render_thumb_svg(section_id, badge_label="GUÍA", reading_time="5 min"):
    """Genera miniaturas visuales dinámicas con estética técnica y oscura para las tarjetas."""
    styles = {
        "hidrolavadoras": {
            "bg": "linear-gradient(135deg, #091e3a 0%, #061122 100%)",
            "accent": "#38bdf8",
            "icon": "💧",
            "spec": "PRESIÓN BAR & CAUDAL",
            "pattern": """<path d="M20 70 Q 150 10 280 70 T 400 70" fill="none" stroke="rgba(56,189,248,0.2)" stroke-width="3"/><circle cx="280" cy="50" r="30" fill="none" stroke="rgba(56,189,248,0.25)" stroke-width="2"/>"""
        },
        "compresores": {
            "bg": "linear-gradient(135deg, #201806 0%, #110c02 100%)",
            "accent": "#f59e0b",
            "icon": "💨",
            "spec": "TANQUE LITROS & CFM",
            "pattern": """<circle cx="260" cy="50" r="35" fill="none" stroke="rgba(245,158,11,0.25)" stroke-width="2"/><line x1="260" y1="50" x2="280" y2="35" stroke="#f59e0b" stroke-width="3"/>"""
        },
        "amoladoras": {
            "bg": "linear-gradient(135deg, #281005 0%, #130701 100%)",
            "accent": "#ff5500",
            "icon": "⚙️",
            "spec": "CORTE & DESBASTE",
            "pattern": """<circle cx="270" cy="50" r="38" fill="none" stroke="rgba(255,85,0,0.3)" stroke-width="2" stroke-dasharray="6,4"/><circle cx="270" cy="50" r="14" fill="rgba(255,85,0,0.15)"/>"""
        },
        "taladros": {
            "bg": "linear-gradient(135deg, #221406 0%, #100802 100%)",
            "accent": "#ea580c",
            "icon": "🔩",
            "spec": "TORQUE & ROTOMARTILLO",
            "pattern": """<rect x="230" y="35" width="60" height="30" rx="6" fill="none" stroke="rgba(234,88,12,0.25)" stroke-width="2"/><circle cx="290" cy="50" r="8" fill="#ea580c" opacity="0.3"/>"""
        },
        "sierras": {
            "bg": "linear-gradient(135deg, #1f1406 0%, #0d0802 100%)",
            "accent": "#d97706",
            "icon": "🪚",
            "spec": "HOJAS DE CORTE & RPM",
            "pattern": """<circle cx="260" cy="50" r="36" fill="none" stroke="rgba(217,119,6,0.25)" stroke-width="3" stroke-dasharray="4,3"/><line x1="220" y1="50" x2="300" y2="50" stroke="#d97706" stroke-width="2" opacity="0.4"/>"""
        },
        "soldadoras": {
            "bg": "linear-gradient(135deg, #240c17 0%, #11050a 100%)",
            "accent": "#e11d48",
            "icon": "🧑‍🏭",
            "spec": "INVERTER MMA & FLUX",
            "pattern": """<polygon points="260,20 280,50 250,50 270,80" fill="none" stroke="rgba(225,29,72,0.35)" stroke-width="2"/><circle cx="265" cy="50" r="25" fill="rgba(225,29,72,0.1)"/>"""
        },
        "generadores": {
            "bg": "linear-gradient(135deg, #1f1b06 0%, #0d0b02 100%)",
            "accent": "#ca8a04",
            "icon": "⚡",
            "spec": "POTENCIA KVA & 220V",
            "pattern": """<path d="M220 50 Q 250 15 280 50 T 340 50" fill="none" stroke="rgba(202,138,4,0.3)" stroke-width="2.5"/><line x1="220" y1="50" x2="340" y2="50" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>"""
        }
    }
    st = styles.get(section_id, styles["amoladoras"])
    return f"""
    <div class="card-thumb" style="background: {st['bg']};">
      <svg class="thumb-pattern" viewBox="0 0 340 100" preserveAspectRatio="none">
        {st['pattern']}
      </svg>
      <div class="thumb-overlay">
        <span class="thumb-badge">{badge_label}</span>
        <span class="thumb-time">{reading_time}</span>
      </div>
      <div class="thumb-spec">
        <span>{st['icon']}</span>
        <span>{st['spec']}</span>
      </div>
    </div>
    """

def render_card_thumb(a, badge_text, reading_time, image_src=None):
    from portadas_guias import guide_cover
    cover = guide_cover(a)
    if not cover:
        raise ValueError('Guía sin portada: ' + a['url'])
    photo_class = 'product-guide-thumb' if cover['kind'] == 'product' else 'context-guide-thumb'
    return f"""
        <div class="card-thumb editorial-thumb {photo_class}">
          <div class="thumb-overlay">
            <span class="thumb-badge">{escape(badge_text)}</span>
            <span class="thumb-time">{reading_time}</span>
          </div>
          <div class="thumb-photo">
            <img class="thumb-img" src="{escape(image_src or cover['image'], quote=True)}"
                 alt="{escape(cover['alt'], quote=True)}" width="{cover['width']}" height="{cover['height']}"
                 loading="lazy" decoding="async">
          </div>
          <span class="editorial-label">{escape(cover['label'])}</span>
        </div>
    """

def render_article_card(a, badge_text="GUÍA", action_text="Ver análisis", image_src=None):
    reading_time = f"{max(3, a.get('word_count', 600) // 200)} min"
    thumb_html = render_card_thumb(a, badge_text, reading_time, image_src)
        
    return f"""
    <a href="{a['url']}" class="card-media" data-title="{a['title'].lower()}" data-sec="{a['section']}">
      {thumb_html}
      <div class="card-body">
        <h3 class="card-title">{a['title']}</h3>
        <p class="card-desc">{a['description']}</p>
        <div class="card-footer">
          <span>{action_text}</span>
          <span>→</span>
        </div>
      </div>
    </a>
    """

def render_search_cards():
    cards = []
    for a in ALL_ARTICLES:
        cards.append(f"""
        <a href="{escape(a['url'], quote=True)}" class="card-media live-search-item" data-title="{escape(a['title'].lower(), quote=True)}" data-sec="{escape(a['section'], quote=True)}" style="display: none;">
          {render_card_thumb(a, a['category'][:12].upper(), f"{max(3, a['word_count'] // 200)} min")}
          <div class="card-body">
            <h3 class="card-title">{escape(a['title'])}</h3>
            <p class="card-desc">{escape(a['description'])}</p>
            <div class="card-footer"><span>Leer guía</span><span>→</span></div>
          </div>
        </a>
        """)
    return "".join(cards)

def render_editorial_page(kind):
    if kind in ("contacto", "privacidad"):
        from paginas_institucionales import PRIVACY, contact_markdown
        path = f"/{kind}/"
        title = "Contacto y correcciones" if kind == "contacto" else "Privacidad y datos"
        desc = "Consultas y correcciones de las guías documentales de TallerLab." if kind == "contacto" else "Registros de navegación, clics comerciales y servicios externos de TallerLab."
        breadcrumbs = f'<nav class="breadcrumb" aria-label="Ubicación"><a href="/">Inicio</a><span>/</span><span>{title}</span></nav>'
        content = f'<article class="markdown-body">{breadcrumbs}<h1>{title}</h1>{MARKDOWN.render(contact_markdown() if kind == "contacto" else PRIVACY)}</article>'
        return HTML_SHELL.format(PAGE_TITLE=title, PAGE_DESC=desc, CANONICAL_TAG=canonical_tag(path), PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC)
    members_html = ""
    if kind == "metodologia":
        title = "Cómo trabajamos"
        path = "/como-trabajamos/"
        body = """
## De dónde salen los datos

Identificamos el código exacto de cada modelo y consultamos fichas, manuales y catálogos del fabricante. Indicamos la fuente junto a cada cifra decisiva. Si una ficha comercial contradice un manual, mostramos la diferencia y pedimos confirmar la variante antes de comprar. Un dato no publicado queda como «no informado»; no lo estimamos a partir de otro modelo.

El recorrido es: **documentación oficial → identificación del modelo y código → contraste de fichas, manuales y catálogos → cálculos cuando corresponden → contradicciones y datos desconocidos → conclusión**. Los cálculos explican sus entradas, unidades, supuestos y límites; una estimación documental no equivale a una medición del producto. Cada artículo muestra sus fuentes directamente, para que puedas consultar los documentos utilizados.

## Cómo clasificamos las afirmaciones

**Dato documentado** identifica una cifra o característica respaldada por una fuente enlazada; no implica una medición ni una comprobación física de TallerLab. **Declaración del fabricante** atribuye expresamente al fabricante una prestación o beneficio que no medimos. **Experiencia de compradores** resume opiniones externas solo cuando identificamos plataforma, modelo, fecha y muestra consultada; no equivale a una prueba propia. **Análisis TallerLab** indica una comparación, cálculo o conclusión documental explicada en la guía. **Desconocido** marca lo que las fuentes disponibles no permiten afirmar. Estas etiquetas ayudan a leer la evidencia; no sustituyen la fuente de cada dato decisivo.

## Cómo comparamos

El marco TallerLab parte del trabajo que querés hacer. Para cada modelo registramos capacidad útil a la presión o condición relevante, potencia declarada, peso, alimentación o plataforma de batería, garantía, servicio y repuestos en Argentina, accesorios incluidos y costo de consumibles. Estas variables no tienen siempre el mismo peso: en compresores importa más el caudal de salida a la presión de uso que el volumen del tanque. Cuando faltan datos comparables, no damos un ganador ni una puntuación artificial.

## Precios y Mercado Libre

Los precios, el stock y el envío cambian por vendedor y fecha. No publicamos un «mejor precio» sin verificar la oferta concreta y registrar cuándo se consultó. Los enlaces de búsqueda de Mercado Libre sirven para comprobar opciones vigentes; no prueban disponibilidad ni prestaciones. Antes de comprar recomendamos comprobar código de modelo, tensión, accesorios, garantía y costo final con envío.

## Opiniones y pruebas propias

Las opiniones de compradores pueden señalar dudas recurrentes, pero no equivalen a una medición técnica. No trasladamos calificaciones ajenas a una reseña propia. Solo llamamos «prueba propia» a una evaluación realizada por TallerLab, con método, condiciones y resultados documentados en la página. Las guías actualmente publicadas son análisis documentales de especificaciones; no afirman uso directo de los equipos.

**Prueba física: no realizada** en las guías actuales. TallerLab no realiza pruebas físicas sistemáticas de los productos.

## Afiliación y correcciones

Algunos enlaces a productos pueden generar una comisión para TallerLab. Cuando una opción encaja con el uso y tiene documentación suficiente, priorizamos ofrecer su enlace de afiliado. La comisión no convierte al producto en ganador ni reemplaza los criterios técnicos: conservamos alternativas y señalamos datos faltantes o contradictorios antes de recomendar. Identificamos los enlaces de afiliado como patrocinados; las búsquedas generales no llevan esa etiqueta. Corregimos una guía cuando cambia una fuente o encontramos un error; la fecha de revisión solo se actualiza después de verificar de nuevo las afirmaciones afectadas.

La fecha visible corresponde a la última revisión documental registrada del artículo. Cambiar la firma, el diseño o un enlace de navegación no modifica esa fecha. Cuando corregimos un error importante, agregamos un **Historial de correcciones** en el artículo con la fecha, el dato corregido y su fuente. Los cambios menores de estilo no requieren una entrada. No reconstruimos fechas ni correcciones sin un registro que las respalde.

## Cuándo publicamos

Cada guía requiere fuentes identificadas, comprobación de cifras, límites explicados y revisión documental registrada. Los borradores no se sirven como páginas públicas. [Joaquín Vallasciani](/autor/joaquin-vallasciani/) es responsable de la investigación documental y edición de las guías. La firma identifica a su autor; no implica una revisión independiente por otra persona.
"""
        desc = "Fuentes, variables de comparación, precios, opiniones, pruebas propias y afiliación de TallerLab."
    else:
        title = "Joaquín Vallasciani — Editor e investigador de TallerLab"
        path = AUTHOR_PATH
        body = """
**Responsable de investigación documental de TallerLab.**

Responsable de la investigación, comparación de fuentes y edición de las guías publicadas en TallerLab. El trabajo se basa principalmente en manuales, catálogos, fichas oficiales de fabricantes y documentación comercial identificada. Las guías distinguen los datos publicados por terceros de los cálculos y análisis realizados por TallerLab.

Actualmente TallerLab no realiza pruebas físicas sistemáticas de los productos. Cuando un equipo no fue probado, esto se indica de forma explícita: **Prueba física: no realizada**.

## Cómo investiga

**Manual → ficha oficial → catálogo → comparación → inconsistencias → conclusión.**

La investigación comienza con documentación oficial y la identificación del modelo, código y mercado. Se contrastan fichas y manuales, se realizan cálculos cuando corresponde y se señalan contradicciones y datos desconocidos. Las fuentes están enlazadas en cada artículo.

## Áreas investigadas

Amoladoras y discos · Compresores y accesorios neumáticos · Sierras · Taladros y mechas · Soldadura · Soldadura electrónica · Generadores · Hidrolavadoras.

Consultá [Cómo trabajamos](/como-trabajamos/) para conocer el método, las fechas de revisión, el historial de correcciones y el tratamiento de enlaces comerciales.
"""
        desc = "Investigación documental y edición de las guías de TallerLab: fuentes, comparaciones y límites."
        guide_groups = []
        for section, meta in CATEGORY_META.items():
            guides = sorted((a for a in ALL_ARTICLES if a["section"] == section and a["author"] == AUTHOR_NAME), key=lambda a: a["title"])
            if guides:
                links = "".join(f'<li><a href="{escape(a["url"], quote=True)}">{escape(a["h1"])}</a></li>' for a in guides)
                guide_groups.append(f'<details class="author-guides"><summary>{escape(meta["name"])} · {len(guides)} guías</summary><ul>{links}</ul></details>')
        members_html = '<section class="markdown-body"><h2>Guías de Joaquín Vallasciani</h2>' + "".join(guide_groups) + '</section>'
        perfil = author_profile()
        extra = []
        if perfil["experiencia"]:
            extra.append(f'<h2>Experiencia</h2><p>{escape(perfil["experiencia"])}</p>')
        if perfil["formacion"]:
            extra.append(f'<h2>Formación</h2><p>{escape(perfil["formacion"])}</p>')
        if perfil["perfiles"] or perfil["email"]:
            enlaces = [f'<li><a href="{escape(u, quote=True)}" rel="me noopener" target="_blank">{escape(urllib.parse.urlsplit(u).hostname or u)}</a></li>' for u in perfil["perfiles"]]
            if perfil["email"]:
                enlaces.append(f'<li><a href="mailto:{escape(perfil["email"], quote=True)}">{escape(perfil["email"])}</a></li>')
            extra.append('<h2>Perfiles y contacto</h2><ul>' + "".join(enlaces) + '</ul>')
        try:
            from alertas_datos import cargar_expedientes
            from alertas_seo import expediente_indexable
            fichas = [e for e in cargar_expedientes() if expediente_indexable(e)]
        except Exception:
            fichas = []
        if fichas:
            extra.append('<h2>Expedientes de documentación y alertas</h2><ul>' + "".join(
                f'<li><a href="/alertas/{escape(e["slug"], quote=True)}/">{escape(e["marca"])} {escape(e["modelo_base"])}</a> · revisión {escape(str(e.get("fecha_revision", "")))}</li>'
                for e in fichas) + '</ul>')
        if extra:
            members_html = '<section class="markdown-body">' + "".join(extra) + '</section>' + members_html
    content = f'<div class="article-container"><div class="article-header"><h1>{title}</h1><p class="article-lead">{desc}</p></div><div class="markdown-body">{MARKDOWN.render(body)}</div>{members_html}</div>'
    schema = "" if kind == "metodologia" else '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": author_schema()}, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
    return HTML_SHELL.format(PAGE_TITLE=title, CANONICAL_TAG=canonical_tag(path) + schema, PAGE_DESC=desc, PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC)


def render_home_page():
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": absolute_url("/") + "#website",
        "name": "TallerLab",
        "url": absolute_url("/"),
        "inLanguage": "es-AR",
        "publisher": {"@id": absolute_url("/") + "#organization"},
    }
    website_tag = '<script type="application/ld+json">' + json.dumps(website, ensure_ascii=False).replace("<", "\\u003c") + '</script>'
    articles = {a["url"]: a for a in ALL_ARTICLES}
    categories = "".join(f'''<a class="home-category" href="/{key}/"><img src="/assets/productos/{image}" alt="" width="160" height="120" loading="lazy"><div><h3>{escape(label)}</h3><span aria-hidden="true">→</span></div></a>''' for key, (label, image) in HOME_CATEGORY_IMAGES.items())
    comparisons = []
    for url, title, description in HOME_COMPARISONS:
        article = articles.get(url)
        if article is None:
            continue
        i = len(comparisons) + 1
        comparisons.append(f'''<a class="home-comparison" href="{url}"><div class="home-comparison-top"><span>{i:02d} / COMPARATIVA</span><span>{escape(CATEGORY_META[article["section"]]["name"])}</span></div><h3>{escape(title)}</h3><p>{escape(description)}</p><span class="home-card-action">Comparar opciones <span aria-hidden="true">→</span></span></a>''')
    tools = []
    for url, kind, title, description, unit in HOME_TOOLS:
        if url not in articles or url not in RESOURCES:
            continue
        tools.append(f'''<a class="home-tool" href="{url}#resource-title"><span class="home-tool-unit" aria-hidden="true">{escape(unit)}</span><div><span class="home-kicker">{kind}</span><h3>{escape(title)}</h3><p>{escape(description)}</p><span class="home-card-action">Usar {kind.lower()} <span aria-hidden="true">→</span></span></div></a>''')
    tools_section = f'''<section id="herramientas" class="home-section home-tools-section" aria-labelledby="home-tools-title"><div class="home-section-heading"><div><span class="home-kicker">03 / RESOLVÉ TU DUDA</span><h2 id="home-tools-title">Menos suposiciones. Más números.</h2></div><p>Calculadoras y selectores con sus supuestos explicados.</p></div><div class="home-tool-grid">{"".join(tools)}</div></section>''' if tools else ""
    tools_action = '<a class="home-secondary" href="#herramientas"><svg width="18" height="20" viewBox="0 0 20 22" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="3" y="2" width="14" height="18" rx="1.5"/><path d="M6 6h8M6 10h2m4 0h2M6 13h2m4 0h2M6 16h2m4 0h2"/></svg>Usar calculadoras</a>' if tools else '<a class="home-secondary" href="#categorias">Explorar categorías ↗</a>'
    content = f'''<div class="home-page">
      <section class="home-hero" aria-labelledby="home-title">
        <div class="home-hero-inner"><div class="home-hero-copy"><span class="home-kicker"><span class="home-status-dot" aria-hidden="true"></span> HERRAMIENTAS EN ARGENTINA</span><h1 id="home-title">Herramientas <span class="home-title-prefix">para</span><br> <span class="home-title-accent">trabajar <span class="home-title-last">mejor.</span></span></h1><p>Comparativas y calculadoras para elegir el equipo que tu trabajo necesita. Con datos, fuentes y criterio.</p><div class="home-hero-actions"><a class="btn-orange" href="#comparativas">Ver comparativas <span aria-hidden="true">→</span></a>{tools_action}</div></div>
        <img class="home-scene" src="/assets/hero-taller-claro-v3.webp" alt="" width="1774" height="887" fetchpriority="high">
        <section class="home-search" aria-label="Buscador de herramientas"><form id="home-search-form" role="search"><label class="sr-only" for="home-query">Buscar guías de herramientas</label><svg class="home-search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input id="home-query" type="search" placeholder="Ej.: taladro inalámbrico, Bosch, compresor…" autocomplete="off" maxlength="120" aria-controls="home-search-results"><button type="submit">Buscar <span aria-hidden="true">→</span></button></form><p>Ej.: taladro inalámbrico, Bosch, compresor…</p><noscript><p>Para buscar activá JavaScript, o explorá las categorías de abajo.</p></noscript></section></div>
      </section>
      <section id="home-search-results" class="home-results" aria-labelledby="home-results-title" hidden><div class="home-section-heading"><div><h2 id="home-results-title">Resultados de búsqueda</h2><span id="home-search-status" role="status" aria-live="polite"></span></div><button id="home-search-clear" type="button">Cerrar búsqueda ×</button></div><div id="home-search-grid" class="article-grid"></div><button id="home-search-more" type="button" hidden>Ver más resultados ↓</button></section>
      <section id="categorias" class="home-section" aria-labelledby="home-categories-title"><div class="home-section-heading"><div><span class="home-kicker">01 / CATEGORÍAS</span><h2 id="home-categories-title">Explorá por categoría</h2></div><p>Del trabajo que tenés al equipo que necesitás.</p></div><div class="home-category-grid">{categories}</div></section>
      <section id="comparativas" class="home-section" aria-labelledby="home-comparisons-title"><div class="home-section-heading"><div><span class="home-kicker">02 / ANTES DE COMPRAR</span><h2 id="home-comparisons-title">Comparativas para empezar</h2></div><p>Opciones, diferencias y límites para decidir.</p></div><div class="home-comparison-grid">{"".join(comparisons)}</div></section>
      {tools_section}
      <section id="precios" class="home-section" aria-labelledby="home-prices-title"><div class="home-section-heading"><div><span class="home-kicker">04 / PRECIOS</span><h2 id="home-prices-title">Antes de comprar, mirá el precio</h2></div><p>Seguimos todos los días el precio publicado y el stock de herramientas concretas en comercios argentinos, con historial descargable.</p></div><p><a class="home-secondary" href="/datos/precios-herramientas-argentina/">Ver precios e historial →</a></p></section>
      <aside class="home-trust"><strong>La fuente también importa.</strong><p>Contrastamos documentación de modelos concretos y señalamos lo que falta confirmar. Algunos enlaces de productos pueden generar una comisión para TallerLab.</p><a href="/como-trabajamos/">Nuestro método →</a></aside>
    </div><script src="/assets/home.js?v=2" defer></script>'''
    return HTML_SHELL.format(PAGE_TITLE="Comparativas y calculadoras de herramientas en Argentina", CANONICAL_TAG=canonical_tag("/") + website_tag, PAGE_DESC="Elegí herramientas para tu trabajo: explorá 8 categorías, compará modelos y usá calculadoras de potencia, caudal y costos antes de comprar en Argentina.", PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC)


def render_category_page(section_id):
    articles = [a for a in ALL_ARTICLES if a["section"] == section_id]
    meta = CATEGORY_META[section_id]
    editorial = HUB_EDITORIAL[section_id]
    taxonomy = TAXONOMY_MAP[section_id]
    if section_id == "compresores":
        groups = {key: [a for a in articles if a["filename"] in COMPRESSOR_HUB_FILES[key]] for key, *_ in COMPRESSOR_HUB_STEPS}
    else:
        groups = {key: [a for a in articles if a["filename"] in taxonomy[key]] for key, *_ in HUB_STEPS}
    if editorial.get("main"):
        main = next(a for a in articles if a["filename"] == editorial["main"])
        groups["general"].insert(0, main)
        groups["necesidad"] = [a for a in groups["necesidad"] if a != main]
    separate_category = editorial.get("separate_category")
    separate_article = next((a for a in articles if separate_category and a["filename"] == separate_category["filename"]), None)
    if separate_article:
        groups = {key: [a for a in group if a != separate_article] for key, group in groups.items()}
    assigned = {a["url"] for group in groups.values() for a in group}
    if separate_article:
        assigned.add(separate_article["url"])
    if assigned != {a["url"] for a in articles}:
        raise ValueError(f"Hay guías sin recorrido editorial en {section_id}")
    trunk = next((a for a in articles if a["url"] == f"/{section_id}/"), None)
    visible_steps = COMPRESSOR_HUB_STEPS if section_id == "compresores" else [step for step in HUB_STEPS if section_id != "taladros" or step[0] != "general"]
    step_labels = {
        "necesidad": "Tipo de herramienta",
        "marcas": "Marca",
        "modelos": "Modelos",
        "accesorios": "Mechas y accesorios",
    } if section_id == "taladros" else {}
    nav = "".join(
        f'<a href="#{anchor}"><span>{i:02d}</span>{escape(step_labels.get(key, label))}</a>'
        for i, (key, anchor, label, _) in enumerate(visible_steps, 1)
    )
    criteria = "".join(f'<li>{escape(item)}</li>' for item in editorial["criteria"])
    start_links = ""
    cover_links = editorial.get("start_links") or [
        (step_labels.get(key, label), f"#{anchor}")
        for key, anchor, label, _ in visible_steps[:3]
    ]
    links = "".join(f'<a href="{url}"><span class="hub-start-index" aria-hidden="true">{i:02d}</span><span class="hub-start-label">{escape(label)}</span><span class="hub-start-arrow" aria-hidden="true">→</span></a>' for i, (label, url) in enumerate(cover_links, 1))
    start_links = f'<aside class="hub-start"><strong><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 5v16M12 5C8 2 4 3 2 4v15c3-1 7-1 10 2 3-3 7-3 10-2V4c-2-1-6-2-10 1Z"/></svg>Empezá por acá</strong><nav aria-label="Accesos rápidos">{links}</nav></aside>'
    separate_category_html = ""
    if separate_category and separate_article:
        card = render_article_card(separate_article, badge_text="ALTERNATIVA", action_text="Ver guía")
        separate_category_html = f'<section class="hub-section hub-alternative" aria-labelledby="hub-alternative-title"><div class="hub-section-heading"><span class="hub-step" aria-hidden="true">↗</span><div><h2 id="hub-alternative-title">{escape(separate_category["title"])}</h2><p>{escape(separate_category["description"])}</p></div></div><div class="article-grid">{card}</div></section>'
    task_selector = ""
    if editorial.get("task_selector"):
        if section_id == "taladros":
            cards = "".join(
                f'<a class="hub-task-card" href="{escape(url, quote=True)}"><span class="hub-task-number" aria-hidden="true">{i:02}</span><span class="hub-task-name">{escape(task)}</span><span class="hub-task-type">{escape(tool)}</span><span class="hub-task-description">{escape(description)}</span><span class="hub-task-action">Ver guía <span aria-hidden="true">→</span></span></a>'
                for i, (task, tool, description, url) in enumerate(editorial["task_selector"], 1)
            )
            task_selector = f'<section class="hub-task-selector" aria-labelledby="hub-task-selector-title"><div class="hub-section-heading"><div><h2 id="hub-task-selector-title">Elegí por tarea</h2><p>¿Qué necesitás hacer? Abrí la guía correspondiente al material o al tipo de trabajo.</p></div></div><div class="hub-task-grid">{cards}</div></section>'
        else:
            rows = "".join(
                f'<tr><th scope="row">{escape(task)}</th><td><a href="{url}">{escape(tool)}</a></td></tr>'
                for task, tool, url in editorial["task_selector"]
            )
            task_selector = f'<section class="hub-task-selector" aria-labelledby="hub-task-selector-title"><div class="hub-section-heading"><div><h2 id="hub-task-selector-title">Qué tipo de sierra necesitás</h2><p>Empezá por el trabajo y abrí la guía de la herramienta que puede resolverlo.</p></div></div><div class="table-scroll"><table><thead><tr><th scope="col">Trabajo</th><th scope="col">Herramienta</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
    main_guide = render_article_page(trunk, embedded=True) if trunk and section_id == "amoladoras" else ""
    sections = []
    for i, (key, anchor, default_label, default_desc) in enumerate(visible_steps, 1):
        label = step_labels.get(key, default_label)
        desc = default_desc
        if section_id == "taladros":
            desc = {
                "necesidad": "Elegí primero la herramienta según la tarea y el material.",
                "marcas": "Explorá las guías disponibles por fabricante.",
                "modelos": "Compará modelos concretos y sus variantes.",
                "accesorios": "Revisá mechas y accesorios según material y encastre.",
            }[key]
        action = "Comparar hidrolavadoras" if section_id == "hidrolavadoras" and key == "general" else "Leer guía"
        cards = "".join(render_article_card(a, badge_text=label.upper(), action_text=action) for a in groups[key] if a != trunk)
        extra = ""
        if key == "general" and trunk:
            if section_id != "amoladoras":
                extra = f'<details class="hub-documental"><summary>Leer guía principal documentada: {escape(trunk["h1"])}</summary>{render_article_page(trunk, embedded=True)}</details>'
                if section_id == 'soldadoras':
                    extra = render_article_page(trunk, embedded=True)
        if key == "marcas" and section_id == "soldadura-electronica":
            cards = "".join(f'<a class="hub-brand-link" href="{a["url"]}">{escape(a["title"])}</a>' for a in groups["modelos"])
            extra = '<p class="hub-note">Las guías disponibles de Gadnic y YiHUA comparan modelos concretos; no representan toda la gama de cada marca.</p>'
        if key == "accesorios" and editorial.get("accessories"):
            extra = '<ul class="hub-checklist">' + "".join(f'<li>{escape(item)}</li>' for item in editorial["accessories"]) + '</ul>'
            extra += f'<p class="hub-note">Consultá los accesorios documentados en la <a href="{groups["general"][0]["url"]}">guía principal</a> y en las fichas de modelos de esta categoría.</p>'
        sections.append(f'<section id="{anchor}" class="hub-section" aria-labelledby="{anchor}-title"><div class="hub-section-heading"><span class="hub-step">{i:02d}</span><div><h2 id="{anchor}-title">{label}</h2><p>{desc}</p></div></div>{extra}<div class="article-grid">{cards}</div></section>')
    headline = meta["name"]
    cover_name, cover_file = HOME_CATEGORY_IMAGES[section_id]
    first_anchor = visible_steps[0][1]
    content = f'''<div class="article-container category-hub">
      <div class="breadcrumb"><a href="/">Inicio</a><span>/</span><span>{escape(meta["name"])}</span></div>
      <header class="category-hero category-cover">
        <div class="category-hero-copy">
          <span class="section-kicker">TALLERLAB / GUÍAS DE COMPRA</span>
          <h1>{escape(headline)}</h1>
          {render_guide_community_entry({'url': '/' + section_id + '/', 'section': section_id})}
          <div class="category-cover-rule" aria-hidden="true"></div>
          <p class="category-cover-intro">{escape(HUB_COVER_COPY[section_id])}</p>
          <a class="category-cover-action" href="#{first_anchor}">Explorar guías <span aria-hidden="true">→</span></a>
          <p class="hub-byline">Por <a href="/autor/joaquin-vallasciani/">{escape(AUTHOR_NAME)}</a></p>
        </div>
        <figure class="category-cover-media">
          <img src="/assets/productos/{escape(cover_file, quote=True)}" alt="Equipo de la categoría {escape(cover_name, quote=True)}" width="640" height="640" fetchpriority="high" decoding="async">
          <figcaption><span class="category-cover-count"><strong>{len(articles):02d}</strong> guías</span></figcaption>
        </figure>
      </header>
      {start_links}
      {task_selector}
      {main_guide}
      {separate_category_html}
      <nav class="hub-nav" aria-label="Recorrido de la categoría">{nav}</nav>
      <aside class="hub-criteria"><strong>Antes de comparar</strong><ul>{criteria}</ul><a href="/como-trabajamos/">Cómo documentamos las guías →</a></aside>
      {"".join(sections)}
      {render_category_prices(section_id)}
      {render_guide_community({'url': '/' + section_id + '/', 'section': section_id})}
    </div>'''
    schema = article_schema_tag(trunk) if trunk else ""
    page = HTML_SHELL.format(PAGE_TITLE=trunk["title"] if trunk else editorial.get("page_title", meta["name"]), CANONICAL_TAG=canonical_tag(f"/{section_id}/") + schema, PAGE_DESC=escape(editorial["intro"], quote=True), PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC)
    if section_id == "hidrolavadoras":
        page = page.replace(f'<title>{editorial["page_title"]} · TallerLab</title>', f'<title>{editorial["page_title"]}</title>', 1)
    return page


def render_article_page(article, embedded=False):
    validar_html(MARKDOWN.render(article["body"]), article["url"], INDEXABLE_PATH_SET, SITE_URL)
    # Pre-procesamiento de markdown:
    # 1. Quitar el H1 inicial del markdown para evitar títulos duplicados
    clean_body = re.sub(r'^\s*#\s+[^\n]+\n+', '', article["body"])
    resource = RESOURCES.get(article["url"])
    if resource:
        # La transparencia queda una vez, en el detalle de método del pie.
        clean_body = re.sub(r'^## Cómo investigamos esta guía\s*\n(?:[ \t]*-[^\n]*\n)+\s*', '', clean_body, flags=re.MULTILINE)
        # Retirar solo preámbulos comunes que explican las etiquetas, no datos.
        clean_body = re.sub(r'^\*\*Dato documentado:\*\* las (?:cifras|especificaciones) (?:se atribuyen|se transcriben)[^\n]*\n\s*', '', clean_body, flags=re.MULTILINE)
        clean_body = re.sub(r'^- \*\*Opiniones(?: de compradores)?:\*\* no se revisó una muestra verificable\.\n?', '', clean_body, flags=re.MULTILINE)
    
    # 2. Formatear botones comerciales de Mercado Libre
    def render_ml_link(match):
        label, url, button = match.groups()
        host = urllib.parse.urlsplit(url).hostname or ""
        is_marketplace = host == "meli.la" or host == "mercadolibre.com.ar" or host.endswith(".mercadolibre.com.ar")
        css_class = ' class="btn-mercado-libre"' if button and is_marketplace else (' class="catalog-link"' if button else '')
        rel = "nofollow sponsored noopener noreferrer" if is_marketplace else "nofollow noopener noreferrer"
        suffix = ' ↗' if button else ''
        return f'<a href="{url}" target="_blank" rel="{rel}"{css_class}>{label}{suffix}</a>'

    clean_body = re.sub(
        r'\[([^\]]+)\]\((https://(?:meli\.la/[A-Za-z0-9]+|(?:www\.)?mercadolibre\.com\.ar/[^\)]+|listado\.mercadolibre\.com\.ar/[^\)]+))\)'
        r'\s*\{:target="_blank" rel="[^"]*"( \.btn-mercado-libre)?\}',
        render_ml_link,
        clean_body,
    )
    clean_body = re.sub(r'\{:target="_blank"[^\}]*\}', '', clean_body)

    if article["section"] == "sierras":
        # Las URLs de búsqueda comunes no son enlaces de referido válidos.
        # Mostrar una oferta solo cuando haya un enlace de afiliado del producto exacto.
        clean_body = re.sub(
            r'\[(.*?)\]\(https?://listado\.mercadolibre\.com\.ar/[^\)]+\)',
            '',
            re.sub(
                r'<a href="https?://listado\.mercadolibre\.com\.ar/[^\"]+" target="_blank" rel="nofollow sponsored" class="btn-mercado-libre">.*?</a>',
                '',
                clean_body,
            ),
        )
        rendered_body = MARKDOWN.render(clean_body)
        body_script = ""
        trust_html = """
        <p><strong>Criterio editorial:</strong> Esta guía compara documentación de fabricantes; TallerLab no realizó una prueba física de los equipos. Las tarjetas comerciales indican su propia fuente y sus límites.</p>
        <p style="margin-top: 0.5rem;"><strong>Enlaces comerciales:</strong> Priorizamos los productos enlazados cuando encajan con el uso y su documentación. Una variante sin identificar se presenta para contrastar, con sus límites visibles.</p>
        """
    else:
        rendered_body = MARKDOWN.render(clean_body)
        body_script = ""
        if article["section"] == "amoladoras":
            trust_html = """
            <p><strong>Criterio editorial:</strong> Esta guía reúne criterios de elección y, cuando corresponde, datos identificados de fichas oficiales del fabricante.</p>
            """
        else:
            trust_html = """
            <p><strong>Criterio editorial:</strong> Esta guía reúne criterios de elección y, cuando corresponde, datos identificados de fichas oficiales del fabricante.</p>
            <p style="margin-top: 0.5rem;"><strong>Aviso de afiliación:</strong> TallerLab participa en el programa de afiliados de Mercado Libre. Algunos enlaces de productos son de afiliado; también hay enlaces a búsquedas generales. Consultá precio, stock y condiciones vigentes en Mercado Libre.</p>
            """
    if re.search(r'href=["\']https://meli\.la/', rendered_body):
        trust_html += '<p class="buying-disclosure"><strong>Enlaces de afiliado:</strong> TallerLab puede recibir una comisión si comprás desde los enlaces de Mercado Libre identificados en esta guía. La comisión no acredita compatibilidad: comprobá el código exacto, la variante, el vendedor y las condiciones de la publicación.</p>'

    def normalize_commercial_anchor(match):
        tag = match.group(0)
        href_match = re.search(r'href="(https://[^\"]+)"', tag)
        if not href_match:
            return tag
        href = href_match.group(1)
        host = urllib.parse.urlsplit(href).hostname or ""
        if not (host == "meli.la" or host == "mercadolibre.com.ar" or host.endswith(".mercadolibre.com.ar")):
            return tag
        tag = re.sub(r'\s(?:target|rel)="[^"]*"', '', tag)
        rel = "nofollow sponsored noopener noreferrer" if href.startswith("https://meli.la/") or host == "mercadolibre.com.ar" or host.endswith(".mercadolibre.com.ar") else "nofollow noopener noreferrer"
        return tag[:-1] + f' target="_blank" rel="{rel}">'

    compressor_config = COMPRESORES_OFFERS.get(article['url'])
    guide_selection = guide_comparison_selection(article['url'], article['section'], PRODUCT_FACTS)
    guide_editorial = guide_comparison_config(article['url'], article['section']) if guide_selection else None
    if compressor_config:
        selected = [
            ('compresores', (offer['model'], next(item[1] for item in AFFILIATE_PRODUCTS['compresores'] if item[2] == offer['url']), offer['url'], article['url']))
            for offer in compressor_config['offers']
        ]
        contextual_shelf = render_affiliate_shelf('compresores', guide_selection or selected, {offer['url']: offer['cta'] for offer in compressor_config['offers']}, editorial=guide_editorial)
        rendered_body = rendered_body.replace('<!-- COMPRESORES-OFFERS -->', contextual_shelf)
    washer_config = HIDROLAVADORAS_OFFERS.get(article['url'])
    if washer_config and (washer_config['offers'] or guide_selection):
        catalog = {item[2]: item for item in AFFILIATE_PRODUCTS['hidrolavadoras']}
        selected = [('hidrolavadoras', (*catalog[offer['url']][:3], article['url'])) for offer in washer_config['offers']]
        ctas = {offer['url']: 'Ver precio de ' + catalog[offer['url']][0] for offer in washer_config['offers']}
        contextual_shelf = render_affiliate_shelf('hidrolavadoras', guide_selection or selected, ctas, editorial=guide_editorial)
        title = ('Consultá esta publicación en Mercado Libre' if len(selected) == 1 else
                 'Nuestra selección según el uso' if article['url'] == '/hidrolavadoras/comparativa-general/' else
                 'Compará estas opciones en Mercado Libre')
        contextual_shelf = contextual_shelf.replace('<h2>Publicaciones para comparar</h2>', '<h3>' + title + '</h3>')
        contextual_shelf = contextual_shelf.replace('<h2>Publicación disponible en Mercado Libre</h2>', '<h3>' + title + '</h3>')
        rendered_body = rendered_body.replace('<!-- HIDROLAVADORAS-OFERTAS -->', contextual_shelf)
        if guide_selection and '<!-- HIDROLAVADORAS-OFERTAS -->' not in article['body']:
            anchor = 'Gamma 150 G2514AR: prestaciones y contenido' if article['url']=='/hidrolavadoras/gamma-150/' else 'Equipos publicados en Argentina cerca de 200 bar'
            section = re.search(r'(<h2>'+re.escape(anchor)+r'</h2>.*?)(?=<h2>|$)',rendered_body,re.S)
            if not section:
                raise ValueError('Falta la sección para comparar modelos: '+article['url'])
            rendered_body = rendered_body[:section.end()] + contextual_shelf + rendered_body[section.end():]
    if guide_selection and article['section']=='generadores':
        config = GENERADORES_OFFERS.get(article['url'],{})
        guide_ctas = {offer['url']:offer['cta'] for offer in config.get('offers',[]) if offer.get('cta')}
        selected_urls = {item[2] for _,item in guide_selection}
        # One purchase action per model; tables retain their technical data.
        def generator_table_label(match):
            return match.group(2) if match.group(1) in selected_urls and match.group(1) in AFFILIATE_URLS else match.group(0)
        rendered_body = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',generator_table_label,rendered_body,flags=re.S)
        comparison = render_affiliate_shelf('generadores',guide_selection,guide_ctas,editorial=guide_editorial)
        marker='<!-- GENERADORES-COMPARACION -->'
        if marker not in rendered_body:
            raise ValueError('Falta ubicación de comparación: '+article['url'])
        rendered_body=rendered_body.replace(marker,comparison)
    if guide_selection and article['section'] not in {'hidrolavadoras','compresores','generadores'}:
        config = (TALADROS_OFFERS if article['section']=='taladros' else SOLDADORAS_OFFERS).get(article['url'],{})
        guide_ctas = {offer['url']:offer['cta'] for offer in config.get('offers',[]) if offer.get('cta')}
        comparison = render_affiliate_shelf(article['section'], guide_selection, guide_ctas, editorial=guide_editorial)
        rendered_body = re.sub(r'<!-- (TALADROS|SOLDADORAS)-OFERTAS -->.*?<!-- /\1-OFERTAS -->', comparison, rendered_body, flags=re.S)
    rendered_body = add_photos_to_cards(rendered_body)
    rendered_body = re.sub(r'<a\b[^>]*>', normalize_commercial_anchor, rendered_body)
    if article["url"] in AMOLADORA_CHOICES:
        # Affiliate CTAs live in one editorially placed comparison block. Keep
        # product names in the technical tables, but do not repeat buy buttons.
        if article["url"] != "/amoladoras/discos/":
            def keep_only_selected_product_link(match):
                href, label = match.groups()
                host = urllib.parse.urlsplit(href).hostname or ""
                if not (host == "meli.la" or host == "mercadolibre.com.ar" or host.endswith(".mercadolibre.com.ar")):
                    return match.group(0)
                label = re.sub(r"(?i)\s*(?:ver precio(?: y disponibilidad)?(?: de [^\]]+)?|ver publicación|consultar)(?: en mercado libre)?\s*", "", label).strip()
                return label
            rendered_body = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', keep_only_selected_product_link, rendered_body, flags=re.DOTALL)
        choice_html = render_amoladora_choice(article["url"])
        if "<!-- EDITORIAL-COMMERCE -->" in rendered_body:
            rendered_body = rendered_body.replace("<!-- EDITORIAL-COMMERCE -->", choice_html)
        elif choice_html:
            # Most pages place the offer after the first complete editorial
            # section; pages can set the marker where their decision block ends.
            editorial_section = re.search(r"(?s)(<h2\b.*?</h2>.*?)(?=<h2\b|$)", rendered_body)
            if editorial_section:
                rendered_body = rendered_body[:editorial_section.end(1)] + choice_html + rendered_body[editorial_section.end(1):]
        rendered_body = rendered_body.replace("<!-- EDITORIAL-COMMERCE-SECONDARY -->", render_contextual_choice(article["url"]))
    rendered_body = rendered_body.replace('<h2>Fuentes consultadas</h2>', '<h2 id="fuentes-consultadas">Fuentes consultadas</h2>')
    if resource:
        source_heading = {"table": "Fichas detrás de la comparación", "selector": "Documentos de este recorrido", "checklist": "Documentos para estas comprobaciones"}.get(resource["kind"], "Fuentes del cálculo y sus límites")
        rendered_body = rendered_body.replace('<h2 id="fuentes-consultadas">Fuentes consultadas</h2>', f'<h2 id="fuentes-consultadas">{source_heading}</h2>')
        rendered_body = re.sub(r'<strong>(Dato documentado|Análisis TallerLab|Desconocido|Declaración del fabricante)([:.]?)</strong>', r'<strong class="evidence-label">\1\2</strong>', rendered_body)
        body_script += '<script src="/assets/decision-tools.js?v=5" defer></script>'
    sec_meta = CATEGORY_META.get(article["section"], {"name": article["category"], "icon": "📁"})
    reading_time = max(3, article.get("word_count", 600) // 200)
    assigned = ARTICLE_AFFILIATE_SHELVES.get(article["url"])
    shelf_products = [
        (article["section"], item)
        for item in AFFILIATE_PRODUCTS.get(article["section"], [])
        if (item[2] in assigned if assigned is not None else item[2] in article["body"])
    ]
    affiliate_shelf = render_affiliate_shelf(article["section"], shelf_products) if shelf_products and article["section"] != "amoladoras" else ""
    
    # 3. Enlazado interno contextual basado en algoritmo de relevancia
    related = get_related_articles(article, ALL_ARTICLES, TAXONOMY_MAP, limit=3)
    related_html = "".join([render_article_card(r, badge_text="RELACIONADO", action_text="Leer guía") for r in related])
    # El pie enumera únicamente fuentes citadas en el cuerpo o en una oferta
    # realmente visible en esta página; nunca hereda fichas de toda la categoría.
    cited_sources = []
    for label, url in re.findall(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', article["body"]):
        source_host = urllib.parse.urlsplit(url).hostname or ""
        if not (source_host == "meli.la" or source_host == "mercadolibre.com.ar" or source_host.endswith(".mercadolibre.com.ar")):
            cited_sources.append((label, url))
    for category, product in shelf_products:
        facts = PRODUCT_FACTS.get(product[2])
        if facts:
            cited_sources.append((facts["brand"] + " " + facts["model"] + ": ficha del producto mostrado", facts["source"]))
    buying_urls = [] if guide_selection or article['url'] in HIDROLAVADORAS_OFFERS or article['url'] in SIERRAS_OFFERS or article['url'] in SOLDADORAS_OFFERS or article['url'] in TALADROS_OFFERS else BUYING_NOTES.get(article["url"], {}).get("urls", [])
    for url, label in buying_urls:
        facts = PRODUCT_FACTS[url]
        cited_sources.append((label + ": " + facts["source_type"], facts["source"]))
    if article["url"] in SOURCE_CLAIMS:
        cited_sources = SOURCE_CLAIMS[article["url"]]
    source_items = []
    seen_sources = set()
    for label, url in cited_sources:
        if url in seen_sources:
            continue
        seen_sources.add(url)
        source_host = urllib.parse.urlsplit(url).hostname or ""
        source_rel = "nofollow sponsored noopener noreferrer" if source_host == "meli.la" or source_host == "mercadolibre.com.ar" or source_host.endswith(".mercadolibre.com.ar") else "noopener noreferrer"
        source_items.append(f'<li><a href="{escape(url, quote=True)}" target="_blank" rel="{source_rel}">{escape(label)} ↗</a></li>')
    sources_html = ("<ul>" + "".join(source_items) + "</ul>") if source_items else "<p>Esta guía aún no cita una fuente externa para sus afirmaciones técnicas.</p>"
    sources_footer = "" if re.search(r'^## Fuentes consultadas\s*$', article["body"], re.MULTILINE) else f'<div class="article-sources"><strong>Fuentes consultadas:</strong>{sources_html}</div>'
    reviewed_label = f'Última revisión documental: {escape(article["reviewed"])}'
    physical_label = "no realizada" if article["physical_test"] == "no" else escape(article["physical_test"])
    primary_label = "Fuentes primarias consultadas" if article["primary_sources"] == "sí" else "Fuentes primarias: no documentadas"
    transparency_html = f'''<section class="article-sources" aria-label="Cómo investigamos esta guía">
      <h2>Cómo investigamos esta guía</h2>
      <ul>
        <li>Tipo de análisis: {escape(article["research_type"])}</li>
        <li>Prueba física: {physical_label}</li>
        <li>Especificaciones contrastadas: {escape(article["specifications_contrasted"])}</li>
        <li>Opiniones de compradores: {escape(article["buyer_opinions"])}</li>
        <li>Fuentes primarias: {escape(article["primary_sources"])}</li>
        <li>Última revisión: {escape(article["reviewed"])}</li>
      </ul>
      <p>Documentación oficial → identificación del modelo y código → contraste de fichas y manuales → cálculos si corresponden → contradicciones y datos desconocidos → conclusión.</p>
      <a href="/como-trabajamos/">Ver metodología de TallerLab</a>
    </section>'''
    if resource:
        transparency_html = f'<details class="research-detail"><summary>Método, revisión y alcance de la evidencia</summary>{transparency_html}</details>'

    if embedded:
        return f'<div class="hub-main-guide markdown-body">{rendered_body}</div>'
        
    if article["url"] == f"/{article['section']}/":
        breadcrumb_html = f"""<a href="/">Inicio</a> <span>/</span> <span style="color: #ffffff;">{sec_meta['name']}</span>"""
    else:
        breadcrumb_html = f"""<a href="/">Inicio</a> <span>/</span> <a href="/{article['section']}/">{sec_meta['name']}</a> <span>/</span> <span style="color: #ffffff;">{article['title']}</span>"""
        
    content = f"""
    <div class="article-container">
      <div class="breadcrumb">
        {breadcrumb_html}
      </div>

      <div class="article-header">
        <div class="meta-bar">
          <span class="thumb-badge" style="background: rgba(255, 85, 0, 0.15); color: var(--orange); border-color: rgba(255, 85, 0, 0.3);">{sec_meta['name'].upper()}</span>
          <span>Por <a href="/autor/joaquin-vallasciani/">{escape(article['author'])}</a></span>
          <span>·</span>
          <span>{reviewed_label}</span>
          <span>·</span>
          <span>{reading_time} min de lectura</span>
        </div>
        <h1>{article['h1']}</h1>
        <p class="article-lead">{article['description']}</p>
        {render_guide_community_entry(article) if not embedded else ""}
      </div>

      {render_aviso_guia(article["url"], article["body"]) if not embedded else ""}

      {render_resource(article) if article["section"] != "amoladoras" else ""}
      {render_buying_note(article, PRODUCT_FACTS) if not guide_selection and article["section"] != "amoladoras" and article['url'] not in HIDROLAVADORAS_OFFERS and article['url'] not in SIERRAS_OFFERS and article['url'] not in SOLDADORAS_OFFERS and article['url'] not in TALADROS_OFFERS else ""}
      {render_quick_guide(article) if article["section"] != "amoladoras" else ""}
      {render_50l_models() if article["url"] == "/compresores/50-litros/" and not guide_selection else ""}
      {affiliate_shelf}
      {next((w for p in CATALOG_PRODUCTS if p.guide_url == article["url"] for w in [render_model_price_widget(p.id)] if w), "")}

      <div id="markdown-target" class="markdown-body">
        {rendered_body}
      </div>

      {render_guide_prices(article["url"]) if not embedded else ""}
      {render_guide_community(article) if not embedded else ""}
      {render_guide_technical_tools_block(article["url"])}
      {__import__("compatibilidad.presentation", fromlist=["x"]).guide_compatibility_block(article["url"]) if not embedded else ""}
      {render_resource(article) if article["section"] == "amoladoras" else ""}
      {render_quick_guide(article) if article["section"] == "amoladoras" else ""}

      <!-- Bloque de Confianza y Transparencia -->
      <div class="trust-footer">
        {transparency_html}
        {trust_html}
        <div class="article-authorship">
          <p><strong>Investigación documental y edición: <a href="/autor/joaquin-vallasciani/">{escape(article['author'])}</a> · TallerLab</strong></p>
          <p>{AUTHOR_ROLE}</p>
          <p>{reviewed_label} · {primary_label} · <strong>Prueba física: {physical_label}</strong></p>
          <p><a href="/como-trabajamos/">Cómo trabajamos</a></p>
        </div>
        {sources_footer}
      </div>

      {render_relevamiento_callout()}

      <!-- Guías Relacionadas por Relevancia -->
      <div style="margin-top: 3.5rem; border-top: 1px solid var(--border); padding-top: 2.25rem;">
        <div class="section-header">
          <div>
            <h2 class="section-title">Guías relacionadas en {sec_meta['name']}</h2>
            <p class="section-subtitle">Artículos complementarios seleccionados para profundizar en tu decisión.</p>
          </div>
        </div>
        <div class="article-grid">
          {related_html}
        </div>
      </div>
    </div>

    {body_script}
    """
    
    if embedded:
        return content.replace("<h1>", "<h3>").replace("</h1>", "</h3>")
    return HTML_SHELL.format(
        PAGE_TITLE=article["title"],
        CANONICAL_TAG=canonical_tag(article["url"]) + article_schema_tag(article),
        PAGE_DESC=article["description"], PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC,
    )


def author_profile():
    """Datos reales del autor cargados por el editor en perfil_autor.json (vacíos = no se muestran)."""
    try:
        data = json.loads((Path(__file__).with_name("perfil_autor.json")).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    perfiles = [u for u in data.get("perfiles", []) if isinstance(u, str) and re.fullmatch(r"https://[^\s<>\"]+", u)]
    email = str(data.get("email_publico", "")).strip()
    email = email if re.fullmatch(r"[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+", email) else ""
    return {"experiencia": str(data.get("experiencia", "")).strip(), "formacion": str(data.get("formacion", "")).strip(),
            "perfiles": perfiles, "email": email}


def author_schema(name=AUTHOR_NAME):
    schema = {
        "@type": "Person",
        "@id": absolute_url(AUTHOR_PATH) + "#joaquin-vallasciani",
        "name": name,
        "url": absolute_url(AUTHOR_PATH),
        "jobTitle": AUTHOR_ROLE,
        "worksFor": {"@id": absolute_url("/") + "#organization"},
    }
    perfil = author_profile()
    if perfil["perfiles"]:
        schema["sameAs"] = perfil["perfiles"]
    if perfil["email"]:
        schema["email"] = "mailto:" + perfil["email"]
    return schema


def article_schema_tag(article):
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["h1"],
        "description": article["description"],
        "mainEntityOfPage": absolute_url(article["url"]),
        "author": author_schema(article["author"]),
        "publisher": {"@id": absolute_url("/") + "#organization"},
    }
    if article.get("reviewed"):
        article_schema["dateModified"] = datetime.strptime(article["reviewed"], "%d/%m/%Y").date().isoformat()
    from portadas_guias import guide_cover
    article_schema["image"] = absolute_url(guide_cover(article)['image'] if article['url'] in INDEXABLE_PATH_SET else LOGO_SRC)
    return '<script type="application/ld+json">' + json.dumps(article_schema, ensure_ascii=False).replace("<", "\\u003c") + '</script>'

def render_not_found(path):
    not_found_content = f"""
        <div style="text-align: center; padding: 5rem 1rem;">
          <h1 style="font-size: 3rem; margin-bottom: 1rem; font-weight: 900; color: var(--orange);">404</h1>
          <p style="color: var(--text-muted); margin-bottom: 2rem;">La página <code>{escape(path)}</code> no existe en TallerLab.</p>
          <a href="/" class="btn-orange">Volver al Inicio</a>
        </div>
        """
    return HTML_SHELL.format(
        PAGE_TITLE="Página no encontrada",
        CANONICAL_TAG='<meta name="robots" content="noindex">',
        PAGE_DESC="Error 404",
        PORT=PORT,
        CONTENT=not_found_content,
        LOGO_SRC=LOGO_SRC
    )

class TallerLabHandler(BaseHTTPRequestHandler):
    def _serve_relevamiento(self):
        from app import app
        size = int(self.headers.get('Content-Length', '0'))
        if size > 65536:
            self.send_error(413)
            return
        body = self.rfile.read(size) if size else None
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ('content-length', 'host')}
        with app.test_client(use_cookies=False) as client:
            response = client.open(self.path, method=self.command, data=body, headers=headers, environ_overrides={'REMOTE_ADDR': self.client_address[0]})
        self.send_response(response.status_code)
        for key, value in response.headers:
            self.send_header(key, value)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(response.get_data())

    def do_POST(self):
        url_path = urllib.parse.urlparse(self.path).path
        if url_path.startswith(('/api/relevamiento/', '/relevamiento-2027/', '/comunidad/')):
            return self._serve_relevamiento()
        if url_path == "/api/affiliate-click":
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 2048:
                    raise ValueError("Invalid body size")
                data = json.loads(self.rfile.read(size))
                event = validate_affiliate_click(data)
                with CLICK_LOCK:
                    with CLICK_LOG.open("a", encoding="utf-8") as log:
                        log.write(json.dumps(event, ensure_ascii=False) + "\n")
            except (ValueError, TypeError, json.JSONDecodeError):
                self.send_error(400)
                return
            self.send_response(204)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        elif url_path == "/api/compatibilidad/evento":
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 4096:
                    raise ValueError("Invalid body size")
                data = json.loads(self.rfile.read(size))
                track_event(
                    event_type=data.get("event_type", ""),
                    query_text=data.get("query_text"),
                    model_a=data.get("model_a"),
                    model_b=data.get("model_b"),
                    verdict=data.get("verdict"),
                )
                self.send_response(204)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        elif url_path == "/api/compatibilidad/ejecutar":
            try:
                import hmac
                auth_header = self.headers.get("Authorization", "")
                token = auth_header.replace("Bearer ", "").strip() if "Bearer " in auth_header else ""
                expected_token = os.environ.get("COMPATIBILITY_MAINTENANCE_TOKEN") or os.environ.get("CRON_SECRET")
                if not (expected_token and token and hmac.compare_digest(token, expected_token)):
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b'{"error": "No autorizado"}')
                    return
                dry_run = data.get("dry_run", True)
                if not isinstance(dry_run, bool):
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"error":"dry_run debe ser booleano"}')
                    return
                pipeline = MaintenancePipeline()
                summary = pipeline.execute_maintenance(dry_run=dry_run)
                self.send_response(200 if summary['status']=='OK' else 503)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(summary, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        self.send_error(404)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        from observatorio.estatico import static_observatory_file
        static_price_file = static_observatory_file(path)
        if static_price_file:
            body = static_price_file.read_bytes()
            is_csv = static_price_file.name in ('descargar-csv', 'historial.csv')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8' if is_csv else 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'public, max-age=300, must-revalidate')
            self.send_header('Content-Length', str(len(body)))
            if is_csv: self.send_header('Content-Disposition', 'attachment; filename="precios-herramientas.csv"')
            self.end_headers()
            self.wfile.write(body)
            return
        if path.startswith(("/api/relevamiento/", "/relevamiento-2027", "/comunidad/")):
            return self._serve_relevamiento()

        if path == "/robots.txt":
            body = render_robots().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/sitemap.xml":
            body = render_sitemap().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/search-cards.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Robots-Tag", "noindex")
            self.end_headers()
            self.wfile.write(render_search_cards().encode("utf-8"))
            return

        if path in ("/equipo-editorial", "/equipo-editorial/"):
            self.send_response(301)
            self.send_header("Location", AUTHOR_PATH + ("?" + parsed.query if parsed.query else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if not path.endswith("/") and path + "/" in INDEXABLE_PATH_SET:
            self.send_response(301)
            self.send_header("Location", path + "/" + ("?" + parsed.query if parsed.query else ""))
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        
        # Favicon
        if path in ("/favicon.ico", "/favicon.svg"):
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.end_headers()
            self.wfile.write((ASSETS_DIR / "favicon.svg").read_bytes())
            return
        
        # 1. Servir archivos estáticos (assets/...)
        if path.startswith("/assets/"):
            file_path = ROOT_DIR / path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if path.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif path.endswith(".jpg") or path.endswith(".jpeg"):
                    self.send_header("Content-Type", "image/jpeg")
                elif path.endswith(".webp"):
                    self.send_header("Content-Type", "image/webp")
                elif path.endswith(".svg"):
                    self.send_header("Content-Type", "image/svg+xml")
                elif path.endswith(".css"):
                    self.send_header("Content-Type", "text/css; charset=utf-8")
                elif path.endswith(".js"):
                    self.send_header("Content-Type", "text/javascript; charset=utf-8")
                self.send_header("Cache-Control", "no-store" if path.endswith(".css") else "public, max-age=3600")
                self.end_headers()
                self.wfile.write(file_path.read_bytes())
                return

        # 2. Portada (Inicio)
        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_home_page().encode("utf-8"))
            return
        if path in ("/como-trabajamos/", "/autor/joaquin-vallasciani/", "/contacto/", "/privacidad/"):
            kind = {"/como-trabajamos/": "metodologia", AUTHOR_PATH: "equipo", "/contacto/": "contacto", "/privacidad/": "privacidad"}[path]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_editorial_page(kind).encode("utf-8"))
            return

        # Observatorio de precios: descarga de CSV
        if path.startswith("/datos/precios/") and path.endswith("/descargar-csv"):
            parts = path.strip("/").split("/")
            cat = parts[2] if len(parts) >= 3 else None
            csv_data = export_observations_to_csv(category=cat if cat in ("compresores", "hidrolavadoras", "generadores") else None)
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="tallerlab-precios-{cat or "catalogo"}.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
            return

        # Observatorio de precios: páginas HTML
        if path in OBSERVATORY_PATHS:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_observatory_page(path).encode("utf-8"))
            return

        # Documentación y alertas de herramientas
        if path in ALERTAS_PATHS:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_alertas_page(path).encode("utf-8"))
            return

        if path == '/api/compatibilidad/estado':
            from compatibilidad.operations import capture_health
            health = capture_health()
            self.send_response(200 if health['status']=='ok' else 503)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(json.dumps(health, ensure_ascii=False).encode('utf-8'))
            return

        # Base de compatibilidad: descarga de CSV y JSON
        if path == "/datos/compatibilidad/baterias.csv":
            csv_data = export_compatibility_to_csv()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="tallerlab-compatibilidad-baterias.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
            return

        if path == "/datos/compatibilidad/baterias.json":
            json_data = export_compatibility_to_json()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="tallerlab-compatibilidad-baterias.json"')
            self.end_headers()
            self.wfile.write(json_data.encode("utf-8"))
            return

        # Base de compatibilidad: buscador y comprobador de par
        if path == COMPATIBILITY_SEARCH_PATH:
            query_params = dict(urllib.parse.parse_qsl(parsed.query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Robots-Tag", "noindex, follow")
            self.end_headers()
            self.wfile.write(render_compatibility_page(path, query_params).encode("utf-8"))
            return

        # Base de compatibilidad: páginas HTML indexables
        from compatibilidad.presentation import resolve_relationship
        if path in COMPATIBILITY_PATHS or resolve_relationship(path) is not None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_compatibility_page(path).encode("utf-8"))
            return

        # TallerLab Data: descarga de CSV de investigación
        if path == "/herramientas/investigacion/descargar-datos.csv":
            csv_data = generate_study_csv()
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="tallerlab-datos-investigacion-herramientas.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
            return

        if path in TALLERLAB_DATA_DOWNLOAD_PATHS and path.endswith('.json'):
            from tallerlab_data.documentary import export_snapshot, sources
            if path.endswith('fuentes.json'):
                fields = {'url', 'checked_at', 'http_status', 'final_url', 'status', 'sha256', 'text_sha256', 'title', 'format', 'pages', 'reason', 'publisher_url'}
                payload = {'scope': 'Recuperación documental; no acredita ensayo ni validación automática de todas las especificaciones', 'sources': [{k: v for k, v in r.items() if k in fields} for r in sources().values()]}
            else:
                payload = export_snapshot()
                payload.pop('candidates', None)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="tallerlab-data.json"')
            self.end_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            return

        # TallerLab Data: páginas HTML indexables
        if path in TALLERLAB_DATA_PATHS:
            query_params = dict(urllib.parse.parse_qsl(parsed.query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_tallerlab_data_page(path, query_params).encode("utf-8"))
            return

        # Los ocho hubs tienen prioridad; sus guías troncales conservan Article.
        if path[1:-1] in PUBLIC_SECTIONS and path.endswith("/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_category_page(path[1:-1]).encode("utf-8"))
            return

        # 3. Artículos específicos
        for a in ALL_ARTICLES:
            if path == a["url"]:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_article_page(a).encode("utf-8"))
                return

        # 4. Categorías restantes (/hidrolavadoras/, /compresores/, etc.)
        for sec_id in PUBLIC_SECTIONS:
            if path == f"/{sec_id}/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_category_page(sec_id).encode("utf-8"))
                return
                
        # 5. Error 404
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(render_not_found(path).encode("utf-8"))

def run():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), TallerLabHandler)
    print(f"Servidor TallerLab activo en http://localhost:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
