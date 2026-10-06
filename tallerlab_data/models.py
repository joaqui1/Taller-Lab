"""TallerLab Data: Modelos de dominio para la base técnica de herramientas."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SpecStatus(str, Enum):
    DECLARADO = "declarado"
    MEDIDO = "medido"
    CALCULADO = "calculado"
    CONTRADICTORIO = "contradictorio"
    NO_ENCONTRADO = "no_encontrado"


class SourceType(str, Enum):
    MANUAL_OFICIAL = "manual_oficial"
    FICHA_FABRICANTE = "ficha_fabricante"
    CATALOGO_OFICIAL = "catalogo_oficial"
    DESPIECE_OFICIAL = "despiece_oficial"
    DECLARACION_MARCA = "declaracion_marca"
    COMERCIO = "comercio"


@dataclass
class Specification:
    spec_key: str
    name: str
    raw_value: str
    raw_unit: str
    normalized_value: Optional[float]
    normalized_unit: str
    condition: str
    applicable_variant: str
    applicable_market: str
    source_type: str
    source_name: str
    source_url: str
    document_page: Optional[str]
    consultation_date: str
    status: str = SpecStatus.DECLARADO.value
    notes: Optional[str] = None
    documentary_status: str = ""
    evidence_reference: str = ""
    evidence_excerpt: str = ""
    condition_status: str = ""

    @property
    def original_value(self) -> str:
        return self.raw_value

    @property
    def original_unit(self) -> str:
        return self.raw_unit

    @property
    def measurement_condition(self) -> str:
        return self.condition

    @property
    def source_page(self) -> Optional[str]:
        return self.document_page

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RegionalVariant:
    code: str
    market: str
    voltage_frequency: str
    plug_type: Optional[str] = None
    notes: str = ""

    @property
    def variant_code(self) -> str:
        return self.code

    @property
    def is_cordless(self) -> bool:
        v_low = (self.voltage_frequency or "").lower()
        return any(term in v_low for term in ("cc", "dc", "v max", "batería", "bateria"))

    @property
    def is_combustion(self) -> bool:
        v_low = (self.voltage_frequency or "").lower()
        return any(term in v_low for term in ("nafta", "diesel", "gasolina", "4 tiempos", "2 tiempos"))

    @property
    def voltage(self) -> str:
        if not self.voltage_frequency:
            return "No informada"
        if self.is_cordless:
            return self.voltage_frequency
        if "/" in self.voltage_frequency:
            return self.voltage_frequency.split("/")[0].strip()
        if "~" in self.voltage_frequency:
            return self.voltage_frequency.split("~")[0].strip()
        return self.voltage_frequency.split()[0] + " V" if " " in self.voltage_frequency else self.voltage_frequency

    @property
    def frequency(self) -> str:
        if self.is_cordless or self.is_combustion:
            return ""
        if "/" in self.voltage_frequency:
            return self.voltage_frequency.split("/")[-1].strip()
        elif "~" in self.voltage_frequency:
            return self.voltage_frequency.split("~")[-1].strip()
        parts = self.voltage_frequency.split()
        return parts[-1] if len(parts) > 1 and "hz" in parts[-1].lower() else ""

    @property
    def motor_type(self) -> str:
        n_low = (self.notes or "").lower()
        if "brushless" in n_low or "sin carbones" in n_low:
            return "Brushless (sin carbones)"
        elif "inducción" in n_low or "induccion" in n_low:
            return "Inducción"
        elif "carbones" in n_low or "escobillas" in n_low:
            return "Universal con carbones"

        return ""

    @property
    def certification(self) -> str:
        n_low = (self.notes or "").lower()
        if any(term in n_low for term in ("iram", "seguridad eléctrica", "resolución", "certificado", "tüv", "iqc", "lenor", "dnct", "dc-e-", "bva/e/")):
            return self.notes
        return ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KitOption:
    kit_code: str
    description: str
    battery_included: str = "No aplica"
    charger_included: str = "No aplica"
    accessories: List[str] = field(default_factory=list)

    @property
    def kit_sku(self) -> str:
        return self.kit_code

    @property
    def kit_name(self) -> str:
        return self.description

    @property
    def includes_battery(self) -> bool:
        return self.battery_included.lower() not in ("no aplica", "no", "false", "")

    @property
    def battery_capacity(self) -> str:
        return self.battery_included

    @property
    def includes_charger(self) -> bool:
        return self.charger_included.lower() not in ("no aplica", "no", "false", "")

    @property
    def charger_model(self) -> str:
        return self.charger_included

    @property
    def accessories_str(self) -> str:
        return ", ".join(self.accessories) if isinstance(self.accessories, list) else str(self.accessories)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommercialOffer:
    seller: str
    platform: str
    url: str
    observed_price_ars: Optional[float]
    observation_date: str
    item_condition: str = "nuevo"
    verification_status: str = "pendiente_relevamiento"
    evidence_reference: str = ""
    observed_availability: str = "desconocida"
    variant_code: str = ""
    kit_code: str = ""
    valid_until: str = ""

    @property
    def seller_name(self) -> str:
        return self.seller

    @property
    def channel(self) -> str:
        return self.platform

    @property
    def currency(self) -> str:
        return "ARS"

    @property
    def kit_quoted(self) -> str:
        return self.kit_code or "No documentado"

    @property
    def availability(self) -> str:
        return self.observed_availability

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContradictionRecord:
    spec_key: str
    field_name: str
    source_a_name: str
    source_a_value: str
    source_a_url: str
    source_b_name: str
    source_b_value: str
    source_b_url: str
    editorial_note: str

    @property
    def spec_name(self) -> str:
        return self.field_name

    @property
    def source_a_date(self) -> str:
        return ""

    @property
    def source_b_date(self) -> str:
        return ""

    @property
    def analysis_notes(self) -> str:
        return self.editorial_note

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TechnicalTool:
    slug: str
    brand: str
    commercial_name: str
    mpn: str
    category: str
    summary: str
    primary_use: str
    power_source: str
    specs: Dict[str, Specification] = field(default_factory=dict)
    variants: List[RegionalVariant] = field(default_factory=list)
    kits: List[KitOption] = field(default_factory=list)
    commercial_offers: List[CommercialOffer] = field(default_factory=list)
    contradictions: List[ContradictionRecord] = field(default_factory=list)
    limits_and_warnings: List[str] = field(default_factory=list)
    primary_sources: List[Dict[str, str]] = field(default_factory=list)
    last_reviewed: str = "2026-10-01"
    status: str = "aceptado"

    @property
    def model_name(self) -> str:
        prefix = self.brand + ' '
        return self.commercial_name[len(prefix):] if self.commercial_name.lower().startswith(prefix.lower()) else self.commercial_name

    @property
    def specifications(self) -> List[Specification]:
        return list(self.specs.values())

    @property
    def regional_variants(self) -> List[RegionalVariant]:
        return self.variants

    @property
    def offers(self) -> List[CommercialOffer]:
        return self.commercial_offers

    @property
    def operational_limits(self) -> str:
        return "\n".join(self.limits_and_warnings)

    @property
    def cautions(self) -> str:
        return ""

    @property
    def is_cordless(self) -> bool:
        return any(v.is_cordless for v in self.variants) or "batería" in self.power_source.lower() or "bateria" in self.power_source.lower()

    @property
    def is_combustion(self) -> bool:
        return any(v.is_combustion for v in self.variants) or "nafta" in self.power_source.lower() or "combustión" in self.power_source.lower() or "combustion" in self.power_source.lower()

    @property
    def power_badge_text(self) -> str:
        if self.is_cordless:
            return f"Batería {self.variants[0].voltage}" if self.variants else "Batería CC"
        if self.is_combustion:
            return self.power_source or "Combustión interna"
        if any("380" in v.voltage_frequency for v in self.variants):
            return "380 V ~ 50 Hz AR (Trifásico)"
        return self.variants[0].voltage_frequency if self.variants else "Alimentación no documentada"

    @property
    def power_badge_css(self) -> str:
        if self.is_cordless:
            return "tl-badge-battery"
        if self.is_combustion:
            return "tl-badge-combustion"
        return "tl-badge-corded"

    @property
    def manual_sources(self) -> List[Dict[str, str]]:
        """Fuentes que corresponden a manuales de fábrica o despieces técnicos en PDF."""
        from tallerlab_data.quality import source_type_for
        return [source for source in self.primary_sources if isinstance(source, dict)
                and source_type_for(source.get("url", ""), source.get("label", ""), source.get("type"))
                in {"manual_oficial", "despiece_oficial"}]

    @property
    def web_sheet_sources(self) -> List[Dict[str, str]]:
        """Fuentes correspondientes a páginas web o fichas de ingeniería del fabricante."""
        return [
            s for s in self.primary_sources
            if isinstance(s, dict) and s not in self.manual_sources and s.get("url")
        ]

    @property
    def manual_urls(self) -> List[str]:
        return [s.get("url", "") for s in self.manual_sources if s.get("url")]

    @property
    def exploded_diagram_urls(self) -> List[str]:
        return [s.get("url", "") for s in self.primary_sources if isinstance(s, dict) and "despiece" in s.get("label", "").lower() and s.get("url")]

    @property
    def last_documented_date(self) -> str:
        return self.last_reviewed

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["specs"] = {k: v.to_dict() for k, v in self.specs.items()}
        d["variants"] = [v.to_dict() for v in self.variants]
        d["kits"] = [k.to_dict() for k in self.kits]
        d["commercial_offers"] = [o.to_dict() for o in self.commercial_offers]
        d["contradictions"] = [c.to_dict() for c in self.contradictions]
        return d
