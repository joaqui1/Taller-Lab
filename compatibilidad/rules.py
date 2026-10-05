"""Motor de reglas de compatibilidad y verificación de evidencias."""

from dataclasses import dataclass, field
from compatibilidad.catalog import catalog_read_locked
from typing import Any, Dict, List, Optional, Tuple

from compatibilidad.catalog import (
    EVIDENCES_BY_ID,
    PLATFORMS_BY_ID,
    PRODUCTS_BY_ID,
)
from compatibilidad.models import (
    Evidence,
    Platform,
    Product,
    ProductType,
    RelationType,
    Verdict,
)


@dataclass
class CompatibilityEvaluation:
    """Resultado detallado de la evaluación de compatibilidad entre dos productos."""
    source_product: Optional[Product]
    target_product: Optional[Product]
    relation_type: str
    verdict: str
    is_compatible: bool
    requires_conditions: bool
    conditions: List[str]
    exclusions: List[str]
    required_packs_count: int
    derivation_method: str
    evidence_chain: List[Evidence]
    summary_text: str
    notes: str
    recommendations: List[str] = field(default_factory=list)
    is_ambiguous: bool = False
    ambiguous_candidates: List[str] = field(default_factory=list)
    candidates_by_side: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_product": self.source_product.to_dict() if self.source_product else None,
            "target_product": self.target_product.to_dict() if self.target_product else None,
            "relation_type": self.relation_type,
            "verdict": self.verdict,
            "is_compatible": self.is_compatible,
            "requires_conditions": self.requires_conditions,
            "conditions": self.conditions,
            "exclusions": self.exclusions,
            "required_packs_count": self.required_packs_count,
            "derivation_method": self.derivation_method,
            "evidence_chain": [e.to_dict() for e in self.evidence_chain],
            "summary_text": self.summary_text,
            "notes": self.notes,
            "recommendations": self.recommendations,
            "is_ambiguous": self.is_ambiguous,
            "ambiguous_candidates": self.ambiguous_candidates,
            "candidates_by_side": self.candidates_by_side,
        }


@catalog_read_locked
def evaluate_compatibility(source_prod: Product, target_prod: Product) -> CompatibilityEvaluation:
    """Only published relations with a complete documentary chain yield a verdict."""
    from compatibilidad.catalog import RELATIONS
    from compatibilidad.sources import proof_valid
    if source_prod.product_type == 'herramienta' and target_prod.product_type == 'bateria':
        source_prod, target_prod = target_prod, source_prod
    if source_prod.product_type == 'bateria' and target_prod.product_type in ('cargador', 'adaptador'):
        source_prod, target_prod = target_prod, source_prod
    def unknown(message, conflict=False):
        return CompatibilityEvaluation(source_prod, target_prod, 'sin_documentacion',
            Verdict.CONFLICTO_EN_REVISION.value if conflict else Verdict.SIN_EVIDENCIA_SUFICIENTE.value,
            False, False, [], [], 1, 'abstencion_documental', [], message, '')
    if source_prod.status != 'publicado' or target_prod.status != 'publicado':
        return unknown('Uno de los registros está pendiente o suspendido. No se confirma compatibilidad.',
                       'conflicto' in (source_prod.status, target_prod.status))
    chain = {}
    for product in (source_prod, target_prod):
        for field, claim in ((product.evidence_identity_id, 'identidad'), (product.evidence_platform_id, 'pertenencia')):
            evidence = EVIDENCES_BY_ID.get(field)
            if not evidence or not proof_valid(evidence, product.id) or claim not in evidence.claim_types:
                return unknown('Falta evidencia verificada de identidad o pertenencia de uno de los modelos.')
            chain[evidence.id] = evidence
    relation = next((r for r in RELATIONS if r['source_product_id'] == source_prod.id and r['target_product_id'] == target_prod.id), None)
    if not relation:
        return unknown('No hay una regla documental verificada para esta combinación. La ausencia de evidencia no demuestra incompatibilidad.')
    for eid in relation['evidence_ids']:
        evidence = EVIDENCES_BY_ID.get(eid)
        if not evidence or not proof_valid(evidence):
            return unknown('La evidencia de la relación requiere revisión.')
        chain[eid] = evidence
    if not any('compatibilidad' in e.claim_types for e in chain.values()):
        return unknown('Falta una declaración oficial de compatibilidad.')
    verdict = relation['verdict']
    compatible = verdict in (Verdict.COMPATIBLE_DOCUMENTADO.value, Verdict.COMPATIBLE_BAJO_CONDICIONES.value)
    return CompatibilityEvaluation(source_prod, target_prod, relation['relation_type'], verdict,
        compatible, bool(relation['conditions']), relation['conditions'], relation['exclusions'],
        relation['required_packs_count'], relation['derivation_method'], list(chain.values()),
        'Compatible según documentación del fabricante.' if compatible else 'Incompatible según documentación del fabricante.',
        relation.get('notes', ''), relation.get('recommendations', []))
