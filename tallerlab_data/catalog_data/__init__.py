"""Agregador de los 100 modelos documentados de TallerLab Data."""

from typing import List
from tallerlab_data.models import TechnicalTool
from tallerlab_data.catalog_data.compresores import COMPRESORES_TOOLS
from tallerlab_data.catalog_data.hidrolavadoras import HIDROLAVADORAS_TOOLS
from tallerlab_data.catalog_data.taladros import TALADROS_TOOLS
from tallerlab_data.catalog_data.amoladoras import AMOLADORAS_TOOLS
from tallerlab_data.catalog_data.soldadoras_generadores import SOLDADORAS_GENERADORES_TOOLS

ALL_TOOLS: List[TechnicalTool] = (
    COMPRESORES_TOOLS +
    HIDROLAVADORAS_TOOLS +
    TALADROS_TOOLS +
    AMOLADORAS_TOOLS +
    SOLDADORAS_GENERADORES_TOOLS
)

assert len(ALL_TOOLS) == 100, f"Se esperaban 100 modelos exactos, se encontraron {len(ALL_TOOLS)}"
