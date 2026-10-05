"""Buscador determinista normalizado por modelo, MPN, marca y alias."""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

from compatibilidad.catalog import (
    CATALOG_PRODUCTS,
    PLATFORMS_BY_ID,
    PRODUCTS_BY_ID,
    PRODUCTS_BY_MPN,
    PRODUCTS_BY_SLUG,
)
from compatibilidad.models import Product, ProductType, Verdict
from compatibilidad.catalog import catalog_read_locked
from compatibilidad.rules import CompatibilityEvaluation, evaluate_compatibility


def normalize_text(text: str) -> str:
    """Normaliza texto eliminando acentos, caracteres especiales y mayúsculas."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return " ".join(text.split())


def normalize_code(code: str) -> str:
    """Elimina guiones, barras y espacios para emparejar códigos alfanuméricos."""
    if not code:
        return ""
    return re.sub(r"[^a-zA-Z0-9]", "", code.upper())


class ProductSearchIndex:
    """Índice en memoria para búsquedas instantáneas y precisas."""

    def __init__(self, products: Optional[List[Product]] = None):
        self.products = CATALOG_PRODUCTS if products is None else products
        self._build_index()

    def _build_index(self):
        self.by_id: Dict[str, Product] = {p.id: p for p in self.products}
        self.by_slug: Dict[str, Product] = {p.slug: p for p in self.products}
        self.by_mpn_clean = {}
        self.exact_terms = {}
        for p in self.products:
            self.by_mpn_clean.setdefault(normalize_code(p.mpn), []).append(p)
            for term in [p.mpn, p.model_name] + p.aliases:
                bucket = self.exact_terms.setdefault(normalize_code(term), [])
                if p not in bucket:
                    bucket.append(p)
        
        # Mapeo de términos normalizados a listas de productos
        self.term_map: Dict[str, List[Product]] = {}
        for p in self.products:
            searchable_strings = [
                p.model_name,
                p.mpn,
                p.brand,
                p.platform_id,
                p.product_type,
                PLATFORMS_BY_ID.get(p.platform_id, None).name if p.platform_id in PLATFORMS_BY_ID else "",
            ] + p.aliases

            tokens = set()
            for s in searchable_strings:
                if not s:
                    continue
                # Token por palabras
                for word in normalize_text(s).split():
                    if len(word) >= 2:
                        tokens.add(word)
                # Token compacto alfanumérico
                clean = normalize_code(s).lower()
                if len(clean) >= 3:
                    tokens.add(clean)

            for token in tokens:
                self.term_map.setdefault(token, []).append(p)

    def search(
        self,
        query: str,
        platform_id: Optional[str] = None,
        product_type: Optional[str] = None,
        brand: Optional[str] = None,
        limit: int = 20,
    ) -> List[Tuple[Product, int]]:
        """
        Búsqueda por coincidencia exacta y difusa con puntuación de relevancia.
        Retorna tuplas (producto, score_relevancia).
        """
        query_raw = query.strip()
        if not query_raw:
            # Si no hay query, filtrar solo por plataforma / tipo
            results = self.products
            if platform_id:
                results = [p for p in results if p.platform_id == platform_id]
            if product_type:
                results = [p for p in results if p.product_type == product_type]
            if brand:
                results = [p for p in results if p.brand.lower() == brand.lower()]
            return [(p, 10) for p in results[:limit]]

        clean_code = normalize_code(query_raw)
        norm_text = normalize_text(query_raw)
        tokens = [token for token in norm_text.split() if len(token) >= 2]

        scores: Dict[str, int] = {}

        # 1. Coincidencia exacta de MPN / código limpio (máxima puntuación: 100)
        if clean_code in self.by_mpn_clean:
            for prod in self.by_mpn_clean[clean_code]:
                scores[prod.id] = scores.get(prod.id, 0) + 100

        # 2. Puntuación por cada token del query
        for token in tokens:
            # Búsqueda directa en term_map
            matches = self.term_map.get(token, [])
            for p in matches:
                scores[p.id] = scores.get(p.id, 0) + 25

            # Búsqueda por subcadena en código MPN o modelo
            for p in self.products:
                p_code = normalize_code(p.mpn).lower()
                if token in p_code:
                    scores[p.id] = scores.get(p.id, 0) + 30
                if token in normalize_text(p.model_name):
                    scores[p.id] = scores.get(p.id, 0) + 15
                if token in normalize_text(p.brand):
                    scores[p.id] = scores.get(p.id, 0) + 10

        # 3. Filtrar y ordenar
        scored_products: List[Tuple[Product, int]] = []
        for p_id, score in scores.items():
            prod = self.by_id[p_id]
            if platform_id and prod.platform_id != platform_id:
                continue
            if product_type and prod.product_type != product_type:
                continue
            if brand and prod.brand.lower() != brand.lower():
                continue
            scored_products.append((prod, score))

        scored_products.sort(key=lambda x: x[1], reverse=True)
        return scored_products[:limit]

    def resolve_product(
        self,
        identifier_or_query: str,
    ) -> Tuple[Optional[Product], bool, List[Product]]:
        """
        Resuelve un producto unívocamente o detecta ambigüedad.
        Retorna (producto_resuelto, es_ambiguo, lista_de_candidatos_alternativos).
        """
        identifier = identifier_or_query.strip()
        if not identifier:
            return None, False, []

        # 1. Búsqueda exacta por ID o slug
        if identifier in self.by_id:
            return self.by_id[identifier], False, []
        if identifier in self.by_slug:
            return self.by_slug[identifier], False, []

        # 2. Búsqueda exacta por MPN limpio
        clean = normalize_code(identifier)
        if clean in self.exact_terms:
            options = self.exact_terms[clean]
            if len(options) == 1:
                return options[0], False, []
            return None, True, options

        # 3. Detección de marcas puras o términos genéricos (ambigüedad directa)
        known_brands = {"bosch", "dewalt", "makita", "einhell", "gamma", "black & decker", "stanley"}
        if identifier.lower() in known_brands or clean.lower() in known_brands:
            matches = self.search(identifier, limit=10)
            return None, True, [p for p, _ in matches]

        # 4. Búsqueda con evaluación de colisiones y margen de confianza
        matches = self.search(identifier, limit=10)
        if not matches:
            return None, False, []

        return None, True, [p for p, _ in matches[:10]]

    def find_one(self, identifier_or_query: str) -> Optional[Product]:
        """Localiza un producto único por ID, slug, MPN exacto o coincidencia unívoca."""
        prod, is_ambiguous, _ = self.resolve_product(identifier_or_query)
        if is_ambiguous:
            return None
        return prod

    @catalog_read_locked
    def check_pair(
        self,
        query_a: str,
        query_b: str,
    ) -> Tuple[Optional[Product], Optional[Product], Optional[CompatibilityEvaluation]]:
        """
        Busca dos productos y evalúa su compatibilidad exacta.
        Si alguna consulta es ambigua, no decide a ciegas y retorna evaluación de ambigüedad.
        """
        prod_a, amb_a, alts_a = self.resolve_product(query_a)
        prod_b, amb_b, alts_b = self.resolve_product(query_b)

        if amb_a or amb_b:
            eval_amb = CompatibilityEvaluation(
                source_product=prod_a,
                target_product=prod_b,
                relation_type="ambigua",
                verdict=Verdict.SIN_EVIDENCIA_SUFICIENTE.value,
                is_compatible=False,
                requires_conditions=False,
                conditions=[],
                exclusions=[
                    "La consulta ingresada no especifica un modelo exacto y coincide con múltiples productos posibles.",
                    "Seleccione uno de los modelos sugeridos para obtener un dictamen preciso.",
                ],
                required_packs_count=1,
                derivation_method="desambiguacion_requerida",
                evidence_chain=[],
                summary_text="Búsqueda ambigua: se requiere especificar el modelo exacto de la herramienta o batería.",
                notes="Evita asignar modelos arbitrarios por simple coincidencia de marca.",
                is_ambiguous=True,
                ambiguous_candidates=[p.id for p in (alts_a + alts_b)[:5]],
                candidates_by_side={'a': [p.id for p in alts_a], 'b': [p.id for p in alts_b]},
            )
            return prod_a, prod_b, eval_amb

        if not prod_a or not prod_b:
            return prod_a, prod_b, None

        evaluation = evaluate_compatibility(prod_a, prod_b)
        return prod_a, prod_b, evaluation


# Instancia única del índice
GLOBAL_SEARCH_INDEX = ProductSearchIndex()
