"""Adaptadores específicos para tiendas especializadas independientes."""

import json
import re
from decimal import Decimal
from typing import Optional
from bs4 import BeautifulSoup

from observatorio.extractors.base import BaseExtractor, ExtractionResult
from observatorio.extractors.structured_data import StructuredDataExtractor
from observatorio.extractors.identity import identity_error


class EasyStoreAdapter(BaseExtractor):
    """Adaptador específico para páginas de Easy Argentina."""

    VERSION = "1.0.0"

    def extract(self, content: str, url: str, target_product) -> ExtractionResult:
        evidence_hash = self.compute_evidence_hash(content)
        soup = BeautifulSoup(content, "html.parser")

        # Intentar primero mediante datos estructurados JSON-LD estándar
        structured = StructuredDataExtractor().extract(content, url, target_product)
        if structured.success:
            # Contrastar con clases visibles de Easy si existen
            self._enrich_with_visible_html(soup, structured)
            return structured

        # Fallback a parseo selectivo de elementos HTML propios de la tienda
        # 1. Título e identidad
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else ""
        if not title:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message="No se encontró el título del producto en la página.",
                extractor_version=self.VERSION,
            )

        # Validar coincidencia de modelo: debe coincidir marca Y (nombre de modelo O MPN exacto)
        brand_ok = target_product.brand.lower() in title.lower()
        model_ok = (
            target_product.model_name.lower() in title.lower()
            or target_product.mpn.lower() in title.lower()
        )
        if identity_error(target_product, title=title):
            model_ok = False
        if not (brand_ok and model_ok):
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                extracted_title=title,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message=f"El producto de la página ('{title}') no coincide con '{target_product.brand} {target_product.model_name}'.",
                extractor_version=self.VERSION,
            )

        # 2. Precio de pago único (NO cuota)
        # Buscar contenedor de precio principal
        price_elem = (
            soup.find(class_=re.compile(r"(product-price|price-selling|best-price|val-price)"))
            or soup.find(id=re.compile(r"price"))
        )

        raw_price_str = ""
        if price_elem:
            # Descartar elementos internos de cuotas si existiesen
            for sub in price_elem.find_all(class_=re.compile(r"(installments|cuota|cuotas)")):
                sub.decompose()
            raw_price_str = price_elem.get_text()
        else:
            # Sin selector estructurado confiable: no usar primer $ como fallback (puede ser una cuota)
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                extracted_title=title,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message="No se encontró contenedor de precio principal identificable en la página.",
                extractor_version=self.VERSION,
            )

        price = self.parse_money(raw_price_str)
        if price is None:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                extracted_title=title,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message="No fue posible extraer un precio de pago único válido.",
                extractor_version=self.VERSION,
            )

        # 3. Disponibilidad: prioridad a señales de no disponibilidad
        # No derivar stock de botones genéricos fuera del contenedor del producto
        stock_text = content.lower()
        if "sin stock" in stock_text or "agotado" in stock_text or "no disponible" in stock_text:
            availability = "agotado"
        else:
            # Buscar botón de compra dentro del contenedor del precio o del producto
            product_section = price_elem.parent if price_elem else None
            if product_section:
                section_text = product_section.get_text(" ", strip=True).lower()
                if "agregar al carrito" in section_text or "comprar ahora" in section_text:
                    availability = "disponible"
                else:
                    availability = "desconocido"
            else:
                availability = "desconocido"

        return ExtractionResult(
            success=True,
            price_single_payment=price,
            currency="ARS",
            availability=availability,
            shipping_note="Envío a calcular por zona",
            extracted_title=title,
            raw_evidence_hash=evidence_hash,
            raw_evidence_snippet=self.extract_snippet(content),
            extractor_version=self.VERSION,
        )

    def _enrich_with_visible_html(self, soup: BeautifulSoup, result: ExtractionResult):
        """Enriquece el resultado con detalles visibles como precio tachado o cuotas."""
        del_tag = soup.find(["del", "s"]) or soup.find(class_=re.compile(r"(list-price|tachado|old-price)"))
        if del_tag:
            p_ref = self.parse_money(del_tag.get_text())
            if p_ref and result.price_single_payment and p_ref > result.price_single_payment:
                result.price_reference_shown = p_ref


class VtexStoreAdapter(BaseExtractor):
    """Adaptador para comercios ferreteros independientes basados en plataforma VTEX."""

    VERSION = "1.0.0"

    def extract(self, content: str, url: str, target_product) -> ExtractionResult:
        # La mayoría de tiendas VTEX inyectan un script vtex.events o skuJson y JSON-LD
        structured = StructuredDataExtractor().extract(content, url, target_product)
        if structured.success:
            return structured

        evidence_hash = self.compute_evidence_hash(content)
        # Buscar script vtex con datos de precio
        sku_match = re.search(r"skuJson_0\s*=\s*(\{.*?\});", content, re.DOTALL)
        if sku_match:
            try:
                sku_data = json.loads(sku_match.group(1))
                skus = sku_data.get("skus", [])
                if len(skus)==1 and not identity_error(target_product, title=sku_data.get('name','')):
                    best_sku = skus[0]
                    best_price_int = best_sku.get("bestPrice")
                    if best_price_int:
                        # En VTEX suele venir en centavos enteros: 12500000 -> 125000.00
                        p = self.parse_money(Decimal(best_price_int) / Decimal(100))
                        available = "disponible" if best_sku.get("available") else "agotado"
                        return ExtractionResult(
                            success=True,
                            price_single_payment=p,
                            currency="ARS",
                            availability=available,
                            extracted_title=sku_data.get("name"),
                            extracted_mpn=str(best_sku.get("id")),
                            raw_evidence_hash=evidence_hash,
                            raw_evidence_snippet=self.extract_snippet(sku_match.group(1)),
                            extractor_version=self.VERSION,
                        )
            except Exception:
                pass

        return ExtractionResult(
            success=False,
            price_single_payment=None,
            raw_evidence_hash=evidence_hash,
            raw_evidence_snippet=self.extract_snippet(content),
            error_message="No fue posible extraer datos estructurados ni SKU de la plataforma VTEX.",
            extractor_version=self.VERSION,
        )
