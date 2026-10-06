"""TallerLab Data: Base técnica de herramientas para Argentina."""

from tallerlab_data.models import (
    CommercialOffer,
    ContradictionRecord,
    KitOption,
    RegionalVariant,
    SourceType,
    SpecStatus,
    Specification,
    TechnicalTool,
)
from tallerlab_data.storage import (
    get_tool as get_tool_by_slug,
    list_tools as get_all_tools,
    save_tool,
    init_db,
)
from tallerlab_data.editorial_comparisons import (
    get_editorial_comparison,
    list_editorial_comparisons as get_all_editorial_comparisons,
)

__all__ = [
    "TechnicalTool",
    "Specification",
    "RegionalVariant",
    "KitOption",
    "CommercialOffer",
    "ContradictionRecord",
    "SpecStatus",
    "SourceType",
    "get_all_tools",
    "get_tool_by_slug",
    "get_editorial_comparison",
    "get_all_editorial_comparisons",
]
