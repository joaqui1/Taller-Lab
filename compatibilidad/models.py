"""Modelos de datos y estructuras para la base argentina de compatibilidad."""

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Verdict(str, Enum):
    """Veredictos formales admitidos por la metodología editorial de TallerLab."""
    COMPATIBLE_DOCUMENTADO = "Compatible documentado"
    COMPATIBLE_BAJO_CONDICIONES = "Compatible bajo condiciones"
    INCOMPATIBLE_DOCUMENTADO = "Incompatible documentado"
    SIN_EVIDENCIA_SUFICIENTE = "Sin evidencia suficiente"
    CONFLICTO_EN_REVISION = "Conflicto en revisión"


class ProductType(str, Enum):
    BATERIA = "bateria"
    CARGADOR = "cargador"
    HERRAMIENTA = "herramienta"
    ADAPTADOR = "adaptador"


class RelationType(str, Enum):
    BATERIA_A_HERRAMIENTA = "bateria_hacia_herramienta"
    CARGADOR_A_BATERIA = "cargador_hacia_bateria"
    REGLA_PLATAFORMA = "regla_plataforma"


class VerificationMethod(str, Enum):
    INSPECCION_DOCUMENTAL_PRIMARIA = "inspeccion_documental_primaria"
    COTEJO_FICHA_MANUAL_AR = "cotejo_ficha_manual_ar"
    DECLARACION_SISTEMA_OFICIAL = "declaracion_sistema_oficial"


@dataclass(frozen=True)
class Platform:
    """Plataforma tecnológica de batería y herramientas."""
    id: str
    name: str
    brand: str
    system_name: str
    voltage_nominal: str
    voltage_max: str
    description: str
    compatibility_rule: str
    conditions_summary: str
    exceptions: List[str]
    official_url: str
    badge_color: str = "#ff5500"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Evidence:
    """Registro granular de respaldo documental para una afirmación o regla."""
    id: str
    source_id: str
    manufacturer: str
    official_url: str
    document_title: str
    section_or_page: str
    excerpt: str
    date_consulted: str
    date_reviewed: str
    verification_method: str = VerificationMethod.COTEJO_FICHA_MANUAL_AR.value
    reviewer: str = "Verificación documental automática"
    evidence_hash: str = ""
    status: str = "pendiente"
    product_ids: List[str] = field(default_factory=list)
    claim_types: List[str] = field(default_factory=list)
    text_assertions: List[str] = field(default_factory=list)
    content_text: str = ""
    product_facts: Dict[str, Any] = field(default_factory=dict)
    supporting_urls: List[str] = field(default_factory=list)
    primary_text: str = ""
    supporting_documents: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Product:
    """Ficha técnica normalizada de batería, cargador o herramienta."""
    id: str
    slug: str
    product_type: str  # bateria, cargador, herramienta, adaptador
    brand: str
    model_name: str
    mpn: str  # Código exacto de pedido o modelo de fabricante
    gtin_ean: Optional[str]
    platform_id: str
    aliases: List[str]
    voltage_nominal: Optional[str]
    voltage_max: Optional[str]
    capacity_ah: Optional[float]
    specs: Dict[str, str]
    is_argentina_catalog: bool
    market_availability_notes: str
    guide_url: Optional[str]
    official_url: str
    required_packs: int = 1  # 2 para herramientas Twin-Pack / 36V
    status: str = "publicado"
    evidence_identity_id: Optional[str] = None
    evidence_platform_id: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompatibilityRelation:
    """Relación verificada entre dos productos o entre producto y regla."""
    id: str
    source_product_id: str
    target_product_id: str
    relation_type: str
    verdict: str
    conditions: List[str]
    exclusions: List[str]
    required_packs_count: int
    evidence_ids: List[str]
    derivation_method: str  # directa_documentada o derivada_por_plataforma
    notes: str
    date_reviewed: str
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChangeLogEntry:
    """Historial auditable de revisiones y cambios en la evidencia."""
    version: str
    date: str
    author: str
    description: str
    affected_records: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
