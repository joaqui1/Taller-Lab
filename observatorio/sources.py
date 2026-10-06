"""Registro formal de fuentes, marco de permisos y mapeo de ofertas."""

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SourceRegistry:
    id: str
    name: str
    domain: str
    access_method: str
    terms_reference: str
    status: str  # 'habilitada', 'pendiente_evaluacion', 'descartada'
    conservation_restrictions: str
    max_requests_per_minute: int
    terms_verified_date: Optional[str] = None
    redistribution_allowed: bool = False
    capture_allowed: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass(frozen=True)
class ConfiguredOffer:
    id: str
    product_id: str
    source_id: str
    seller_name: str
    direct_url: str
    affiliate_url: Optional[str]
    external_sku: Optional[str]
    extraction_method: str
    enabled: bool

    def to_dict(self) -> Dict:
        return asdict(self)


# Registro de fuentes con evidencia y estado legal/operativo
SOURCES_REGISTRY: List[SourceRegistry] = [
    SourceRegistry(
        id="feed_distribuidor_directo",
        name="Feed Oficial Mayorista y Distribuidor Ferretero",
        domain="catalogo.distribuidor-herramientas.com.ar",
        access_method="feed_import",
        terms_reference="Sin documento verificable — pendiente de acreditación formal.",
        status="pendiente_evaluacion",
        conservation_restrictions="Pendiente de acreditación formal. No habilitado para captura ni publicación.",
        max_requests_per_minute=30,
        terms_verified_date=None,
        redistribution_allowed=False,
    ),
    SourceRegistry(
        id="tienda_bulonera_vtex",
        name="Bulonera y Ferretería Industrial",
        domain="www.buloneragrupo.com.ar",
        access_method="structured_data_jsonld",
        terms_reference="Acceso a datos estructurados públicos Schema.org/Product. Pendiente de evaluación de redistribución.",
        status="pendiente_evaluacion",
        conservation_restrictions="Pendiente de evaluación de derechos de conservación y redistribución.",
        max_requests_per_minute=20,
        terms_verified_date=None,
        redistribution_allowed=False,
    ),
    SourceRegistry(
        id="tienda_easy_argentina",
        name="Easy Argentina (Cencosud)",
        domain="www.easy.com.ar",
        access_method="store_adapter",
        terms_reference="Páginas públicas de catálogo minorista. Pendiente de evaluación de términos de uso.",
        status="pendiente_evaluacion",
        conservation_restrictions="Pendiente de evaluación de conservación de datos para publicación y descarga.",
        max_requests_per_minute=15,
        terms_verified_date=None,
        redistribution_allowed=False,
    ),
    SourceRegistry(
        id="tienda_directa_lusqtoff",
        name="Tienda Oficial Lüsqtoff Argentina",
        domain="tienda.lusqtoff.com.ar",
        access_method="structured_data_jsonld",
        terms_reference="Datos estructurados públicos de la tienda directa de marca.",
        status="pendiente_evaluacion",
        conservation_restrictions="Conservación de datos públicos del catálogo oficial.",
        max_requests_per_minute=20,
        terms_verified_date=None,
        redistribution_allowed=False,
    ),
    SourceRegistry(
        id="mercadolibre_argentina",
        name="Mercado Libre Argentina",
        domain="www.mercadolibre.com.ar",
        access_method="api_o_scraping",
        terms_reference="Términos y Condiciones del Programa de Desarrolladores (https://developers.mercadolibre.com.ar/es_ar/es-ar-terminos-y-condiciones). Cláusula restrictiva de scraping y estadísticas derivadas sin autorización expresa por escrito.",
        status="descartada",
        conservation_restrictions="Captura automatizada descartada en v1. No se ejecutan consultas activas sin autorización expresa.",
        max_requests_per_minute=0,
        terms_verified_date=None,
        redistribution_allowed=False,
    ),
]

SOURCES_BY_ID = {s.id: s for s in SOURCES_REGISTRY}

# Configuración de ofertas concretas para cada modelo
# Mapeo a URLs directas (hasta 3 ofertas por modelo en tiendas independientes)
CONFIGURED_OFFERS: List[ConfiguredOffer] = [
    # COMP-LUSQ-LC2550B
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC2550B-FEED",
        product_id="COMP-LUSQ-LC2550B",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lc2550b-8",
        affiliate_url=None,
        external_sku="LUS-LC2550B8",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC2550B-BULO",
        product_id="COMP-LUSQ-LC2550B",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/compresor-de-aire-lusqtoff-50-litros-lc2550b-8/p",
        affiliate_url=None,
        external_sku="BULO-94821",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC2550B-EASY",
        product_id="COMP-LUSQ-LC2550B",
        source_id="tienda_easy_argentina",
        seller_name="Easy Argentina",
        direct_url="https://www.easy.com.ar/compresor-de-aire-50l-2-5hp-lusqtoff-lc-2550b-8/p",
        affiliate_url=None,
        external_sku="1249912",
        extraction_method="easy_store_adapter",
        enabled=True,
    ),

    # COMP-GAMMA-G2802
    ConfiguredOffer(
        id="OFF-COMP-GAMMA-G2802-FEED",
        product_id="COMP-GAMMA-G2802",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/gamma-g2802ar",
        affiliate_url=None,
        external_sku="GAM-G2802AR",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-COMP-GAMMA-G2802-BULO",
        product_id="COMP-GAMMA-G2802",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/compresor-monofasico-50l-gamma-g2802ar/p",
        affiliate_url=None,
        external_sku="BULO-11048",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # COMP-EINHELL-TEAC270
    ConfiguredOffer(
        id="OFF-COMP-EINHELL-TEAC270-FEED",
        product_id="COMP-EINHELL-TEAC270",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/einhell-4020610",
        affiliate_url=None,
        external_sku="EIN-4020610",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-COMP-EINHELL-TEAC270-EASY",
        product_id="COMP-EINHELL-TEAC270",
        source_id="tienda_easy_argentina",
        seller_name="Easy Argentina",
        direct_url="https://www.easy.com.ar/compresor-silencioso-50-litros-einhell-te-ac-270-50/p",
        affiliate_url=None,
        external_sku="1389401",
        extraction_method="easy_store_adapter",
        enabled=True,
    ),

    # COMP-LUSQ-LC0122
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC0122-FEED",
        product_id="COMP-LUSQ-LC0122",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lc-0122",
        affiliate_url=None,
        external_sku="LUS-LC0122",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC0122-BULO",
        product_id="COMP-LUSQ-LC0122",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/compresor-silencioso-24l-lusqtoff-lc-0122/p",
        affiliate_url=None,
        external_sku="BULO-38912",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # COMP-LUSQ-MCL150
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-MCL150-FEED",
        product_id="COMP-LUSQ-MCL150",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-mcl150-8",
        affiliate_url=None,
        external_sku="LUS-MCL1508",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-MCL150-LUSQ",
        product_id="COMP-LUSQ-MCL150",
        source_id="tienda_directa_lusqtoff",
        seller_name="Lüsqtoff Tienda Oficial",
        direct_url="https://tienda.lusqtoff.com.ar/productos/mini-compresor-portatil-12v-mcl150-8",
        affiliate_url=None,
        external_sku="MCL150-8",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # HIDRO-KARCH-K2
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K2-FEED",
        product_id="HIDRO-KARCH-K2",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/karcher-k2-16732200",
        affiliate_url=None,
        external_sku="KAR-16732200",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K2-BULO",
        product_id="HIDRO-KARCH-K2",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/hidrolavadora-karcher-k2-110-bar-1400w/p",
        affiliate_url=None,
        external_sku="BULO-55910",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K2-EASY",
        product_id="HIDRO-KARCH-K2",
        source_id="tienda_easy_argentina",
        seller_name="Easy Argentina",
        direct_url="https://www.easy.com.ar/hidrolavadora-karcher-k2-compact-110-bar/p",
        affiliate_url=None,
        external_sku="1120034",
        extraction_method="easy_store_adapter",
        enabled=True,
    ),

    # HIDRO-KARCH-K4PC
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K4PC-FEED",
        product_id="HIDRO-KARCH-K4PC",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/karcher-k4-power-control",
        affiliate_url=None,
        external_sku="KAR-13240300",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K4PC-BULO",
        product_id="HIDRO-KARCH-K4PC",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/hidrolavadora-karcher-k4-power-control-130-bar/p",
        affiliate_url=None,
        external_sku="BULO-55940",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # HIDRO-LUSQ-HL100
    ConfiguredOffer(
        id="OFF-HIDRO-LUSQ-HL100-FEED",
        product_id="HIDRO-LUSQ-HL100",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-hl100-7",
        affiliate_url=None,
        external_sku="LUS-HL1007",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-HIDRO-LUSQ-HL100-BULO",
        product_id="HIDRO-LUSQ-HL100",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/hidrolavadora-lusqtoff-hl100-7-100-bar/p",
        affiliate_url=None,
        external_sku="BULO-42001",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # HIDRO-LUSQ-HL120
    ConfiguredOffer(
        id="OFF-HIDRO-LUSQ-HL120-FEED",
        product_id="HIDRO-LUSQ-HL120",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-hl-120",
        affiliate_url=None,
        external_sku="LUS-HL120",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-HIDRO-LUSQ-HL120-LUSQ",
        product_id="HIDRO-LUSQ-HL120",
        source_id="tienda_directa_lusqtoff",
        seller_name="Lüsqtoff Tienda Oficial",
        direct_url="https://tienda.lusqtoff.com.ar/productos/hidrolavadora-120-bar-1400w-hl-120",
        affiliate_url=None,
        external_sku="HL-120",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # HIDRO-GAMMA-G130
    ConfiguredOffer(
        id="OFF-HIDRO-GAMMA-G130-FEED",
        product_id="HIDRO-GAMMA-G130",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/gamma-g1902ar-g130",
        affiliate_url=None,
        external_sku="GAM-G1902AR",
        extraction_method="feed_import",
        enabled=True,
    ),
    ConfiguredOffer(
        id="OFF-HIDRO-GAMMA-G130-BULO",
        product_id="HIDRO-GAMMA-G130",
        source_id="tienda_bulonera_vtex",
        seller_name="Bulonera Central",
        direct_url="https://www.buloneragrupo.com.ar/hidrolavadora-gamma-g130-130-bar-1600w/p",
        affiliate_url=None,
        external_sku="BULO-19020",
        extraction_method="structured_data_jsonld",
        enabled=True,
    ),

    # COMP-LUSQ-LC2550VS
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC2550VS-FEED",
        product_id="COMP-LUSQ-LC2550VS",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lc-2550vs",
        affiliate_url=None,
        external_sku="LUS-LC2550VS",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-LUSQ-LCS50
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LCS50-FEED",
        product_id="COMP-LUSQ-LCS50",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lcs50-8",
        affiliate_url=None,
        external_sku="LUS-LCS508",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-LUSQ-LC3550BK
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC3550BK-FEED",
        product_id="COMP-LUSQ-LC3550BK",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lc-3550bk",
        affiliate_url=None,
        external_sku="LUS-LC3550BK",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-LUSQ-LC30100
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC30100-FEED",
        product_id="COMP-LUSQ-LC30100",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lc-30100",
        affiliate_url=None,
        external_sku="LUS-LC30100",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-LUSQ-LC40100
    ConfiguredOffer(
        id="OFF-COMP-LUSQ-LC40100-FEED",
        product_id="COMP-LUSQ-LC40100",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-lc-40100",
        affiliate_url=None,
        external_sku="LUS-LC40100",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-GAMMA-G2801
    ConfiguredOffer(
        id="OFF-COMP-GAMMA-G2801-FEED",
        product_id="COMP-GAMMA-G2801",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/gamma-g2801ar",
        affiliate_url=None,
        external_sku="GAM-G2801AR",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-GAMMA-G2803
    ConfiguredOffer(
        id="OFF-COMP-GAMMA-G2803-FEED",
        product_id="COMP-GAMMA-G2803",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/gamma-g2803ar",
        affiliate_url=None,
        external_sku="GAM-G2803AR",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-EINHELL-TCAC190
    ConfiguredOffer(
        id="OFF-COMP-EINHELL-TCAC190-FEED",
        product_id="COMP-EINHELL-TCAC190",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/einhell-4007325",
        affiliate_url=None,
        external_sku="EIN-4007325",
        extraction_method="feed_import",
        enabled=True,
    ),

    # COMP-NICTOM-IE01
    ConfiguredOffer(
        id="OFF-COMP-NICTOM-IE01-FEED",
        product_id="COMP-NICTOM-IE01",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/nictom-ie01",
        affiliate_url=None,
        external_sku="NIC-IE01",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-KARCH-K3
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K3-FEED",
        product_id="HIDRO-KARCH-K3",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/karcher-k3-16018120",
        affiliate_url=None,
        external_sku="KAR-16018120",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-KARCH-K5PC
    ConfiguredOffer(
        id="OFF-HIDRO-KARCH-K5PC-FEED",
        product_id="HIDRO-KARCH-K5PC",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/karcher-k5-power-control",
        affiliate_url=None,
        external_sku="KAR-13245500",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-LUSQ-HL145
    ConfiguredOffer(
        id="OFF-HIDRO-LUSQ-HL145-FEED",
        product_id="HIDRO-LUSQ-HL145",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/lusqtoff-hl-145",
        affiliate_url=None,
        external_sku="LUS-HL145",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-GAMMA-G150
    ConfiguredOffer(
        id="OFF-HIDRO-GAMMA-G150-FEED",
        product_id="HIDRO-GAMMA-G150",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/gamma-g1903ar-g150",
        affiliate_url=None,
        external_sku="GAM-G1903AR",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-BOSCH-EA100
    ConfiguredOffer(
        id="OFF-HIDRO-BOSCH-EA100-FEED",
        product_id="HIDRO-BOSCH-EA100",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/bosch-easyaquatak-100",
        affiliate_url=None,
        external_sku="BOS-06008A7E00",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-BOSCH-EA120
    ConfiguredOffer(
        id="OFF-HIDRO-BOSCH-EA120-FEED",
        product_id="HIDRO-BOSCH-EA120",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/bosch-easyaquatak-120",
        affiliate_url=None,
        external_sku="BOS-06008A7900",
        extraction_method="feed_import",
        enabled=True,
    ),

    # HIDRO-BD-BEPW1600
    ConfiguredOffer(
        id="OFF-HIDRO-BD-BEPW1600-FEED",
        product_id="HIDRO-BD-BEPW1600",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/black-decker-bepw1600",
        affiliate_url=None,
        external_sku="BD-BEPW1600",
        extraction_method="feed_import",
        enabled=True,
    ),

    # GEN-HONDA-EU22I
    ConfiguredOffer(
        id="OFF-GEN-HONDA-EU22I-FEED",
        product_id="GEN-HONDA-EU22I",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/honda-eu22i",
        affiliate_url=None,
        external_sku="HON-EU22I",
        extraction_method="feed_import",
        enabled=True,
    ),

    # GEN-GAMMA-GE3480
    ConfiguredOffer(
        id="OFF-GEN-GAMMA-GE3480-FEED",
        product_id="GEN-GAMMA-GE3480",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/gamma-ge3480ar",
        affiliate_url=None,
        external_sku="GAM-GE3480AR",
        extraction_method="feed_import",
        enabled=True,
    ),

    # GEN-PHILCO-GEPH25
    ConfiguredOffer(
        id="OFF-GEN-PHILCO-GEPH25-FEED",
        product_id="GEN-PHILCO-GEPH25",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/philco-geph2500alp",
        affiliate_url=None,
        external_sku="PHI-GEPH2500ALP",
        extraction_method="feed_import",
        enabled=True,
    ),

    # GEN-PEKTRA-GPK980
    ConfiguredOffer(
        id="OFF-GEN-PEKTRA-GPK980-FEED",
        product_id="GEN-PEKTRA-GPK980",
        source_id="feed_distribuidor_directo",
        seller_name="Distribuidor Ferretero",
        direct_url="https://catalogo.distribuidor-herramientas.com.ar/productos/pektra-gpk980",
        affiliate_url=None,
        external_sku="PEK-GPK980",
        extraction_method="feed_import",
        enabled=True,
    ),
]

OFFERS_BY_ID = {o.id: o for o in CONFIGURED_OFFERS}
