"""Funciones utilitarias para generación de especificaciones técnicas."""

from typing import Optional
from tallerlab_data.models import Specification


def make_spec(
    key: str,
    name: str,
    raw_val: str,
    raw_unit: str,
    norm_val: Optional[float],
    norm_unit: str,
    condition: str,
    variant: str,
    source_name: str,
    source_url: str,
    page: Optional[str] = None,
    status: str = "declarado",
    notes: Optional[str] = None,
    market: str = "Argentina · 220 V 50 Hz",
    source_type: Optional[str] = None,
    date: str = "2026-10-01"
) -> Specification:
    from tallerlab_data.quality import source_type_for
    resolved_source_type = source_type_for(source_url, source_name, source_type)
    # Unknown pagination must remain unknown, including PDFs.
    resolved_page = None if page == "pág. 1" else page

    return Specification(
        spec_key=key,
        name=name,
        raw_value=raw_val,
        raw_unit=raw_unit,
        normalized_value=norm_val,
        normalized_unit=norm_unit,
        condition=condition,
        applicable_variant=variant,
        applicable_market=market,
        source_type=resolved_source_type,
        source_name=source_name,
        source_url=source_url,
        document_page=resolved_page,
        consultation_date=date,
        status=status,
        notes=notes
    )

