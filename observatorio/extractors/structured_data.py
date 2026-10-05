"""Extractor de datos estructurados Schema.org (JSON-LD y Microdata)."""

import json
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

from observatorio.extractors.base import BaseExtractor, ExtractionResult
from observatorio.extractors.identity import identity_error


class StructuredDataExtractor(BaseExtractor):
    """Extractor para sitios con marcado JSON-LD schema.org/Product y Offer."""

    VERSION = "1.0.0"

    def extract(self, content: str, url: str, target_product) -> ExtractionResult:
        evidence_hash = self.compute_evidence_hash(content)
        soup = BeautifulSoup(content, "html.parser")
        
        # 1. Buscar bloques JSON-LD
        json_ld_blocks = soup.find_all("script", type="application/ld+json")
        product_obj: Optional[Dict[str, Any]] = None

        for script in json_ld_blocks:
            try:
                raw_json = script.string
                if not raw_json:
                    continue
                data = json.loads(raw_json)
                
                # Manejar dict individual, lista de objetos o @graph
                candidates = []
                if isinstance(data, list):
                    candidates = data
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        candidates = data["@graph"]
                    else:
                        candidates = [data]

                for item in candidates:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("@type", "")
                    if item_type == "Product" or (isinstance(item_type, list) and "Product" in item_type):
                        product_obj = item
                        break
                
                if product_obj:
                    break
            except Exception:
                continue

        if not product_obj:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message="No se encontró estructura schema.org/Product en el contenido.",
                extractor_version=self.VERSION,
            )

        # 2. Validación de identidad y variante
        name = str(product_obj.get("name", "")).strip()
        mpn = str(product_obj.get("mpn", "")).strip()
        sku = str(product_obj.get("sku", "")).strip()

        # Comprobar que no sea repuesto o accesorio aislado
        lower_name = name.lower()
        spare_terms = ("repuesto para", "accesorio para", "solo manguera", "soporte para", "batería de repuesto")
        if any(term in lower_name for term in spare_terms) and not any(term in target_product.model_name.lower() for term in spare_terms):
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                error_message=f"La página ofrece un repuesto/accesorio ('{name}') y no el producto completo.",
                extractor_version=self.VERSION,
            )

        # Validar coincidencia con el modelo buscado
        target_mpn_clean = re.sub(r"[^A-Za-z0-9]", "", target_product.mpn).upper()
        extracted_mpn_clean = re.sub(r"[^A-Za-z0-9]", "", mpn or sku).upper()
        
        mpn_matched = bool(target_mpn_clean and target_mpn_clean == extracted_mpn_clean)
        name_matched = target_product.brand.lower() in lower_name and (
            target_product.model_name.lower() in lower_name or 
            target_product.mpn.lower() in lower_name
        )

        # Si el MPN extraído existe pero contradice explícitamente al MPN del producto buscado
        if extracted_mpn_clean and target_mpn_clean and not mpn_matched:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                error_message=f"MPN contradictorio: se esperaba '{target_product.mpn}' pero se encontró '{mpn or sku}'.",
                extractor_version=self.VERSION,
            )

        if not (mpn_matched or name_matched):
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                error_message=f"Discrepancia de producto: se esperaba '{target_product.brand} {target_product.model_name}' pero se encontró '{name}' (MPN: {mpn or sku}).",
                extractor_version=self.VERSION,
            )

        # Validar tensión / voltaje
        target_voltage = str(getattr(target_product, "voltage", "")).lower()
        extracted_voltage = ""
        add_props = product_obj.get("additionalProperty", [])
        if isinstance(add_props, list):
            for prop in add_props:
                if isinstance(prop, dict) and prop.get("name", "").lower() in ("voltaje", "voltage", "tension", "tensión"):
                    extracted_voltage = str(prop.get("value", "")).lower()
        if not extracted_voltage:
            extracted_voltage = str(product_obj.get("voltage", "")).lower()

        mismatch = identity_error(target_product, mpn=mpn, title=name, voltage=extracted_voltage,
                                  condition=product_obj.get('itemCondition',''), kit=product_obj.get('description',''))
        if mismatch:
            return ExtractionResult(False,None,error_message=mismatch,raw_evidence_hash=evidence_hash)

        is_target_220 = "220" in target_voltage or "monofas" in target_voltage
        is_extracted_380 = "380" in extracted_voltage or "380" in lower_name or "trifas" in lower_name or "trifas" in extracted_voltage
        if is_target_220 and is_extracted_380:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                error_message=f"Incompatibilidad de tensión: el producto buscado es {target_product.voltage} pero la oferta indica 380 V / trifásica.",
                extractor_version=self.VERSION,
            )

        # Rechazar ítems usados o reacondicionados para productos declarados como nuevos
        item_condition = str(product_obj.get("itemCondition", "")).lower()
        if target_product.item_condition == "nuevo" and any(
            cond in item_condition for cond in ("used", "refurbished", "usedcondition", "refurbishedcondition")
        ):
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                error_message=f"Condición del ítem incompatible: '{item_condition}'. Se requiere producto nuevo.",
                extractor_version=self.VERSION,
            )

        # 3. Parsear oferta
        offers_data = product_obj.get("offers")
        if not offers_data:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                error_message="El producto no contiene campo 'offers'.",
                extractor_version=self.VERSION,
            )

        # Tratar AggregateOffer
        offer = None
        if isinstance(offers_data, dict):
            if offers_data.get("@type") == "AggregateOffer":
                # Si contiene lista interna de offers, buscar la primera oferta concreta
                sub_offers = offers_data.get("offers", [])
                if isinstance(sub_offers, list) and sub_offers:
                    offer = sub_offers[0]
                elif "lowPrice" in offers_data:
                    # Regla obligatoria: No tomar AggregateOffer.lowPrice si agrupa vendedores/variantes desconocidos
                    # Solo aceptable si highPrice == lowPrice o la oferta concreta está identificada
                    low_p = offers_data.get("lowPrice")
                    high_p = offers_data.get("highPrice")
                    seller = offers_data.get("seller") or offers_data.get("offeredBy")
                    offer_count = offers_data.get("offerCount")
                    single_seller = seller and (offer_count is None or int(offer_count) <= 1)
                    if low_p == high_p and low_p is not None and single_seller:
                        offer = offers_data
                        offer["price"] = low_p
                    else:
                        return ExtractionResult(
                            success=False,
                            price_single_payment=None,
                            availability="desconocido",
                            extracted_title=name,
                            raw_evidence_hash=evidence_hash,
                            raw_evidence_snippet=self.extract_snippet(json.dumps(offers_data, ensure_ascii=False)),
                            error_message="AggregateOffer agrupa un rango de precios sin oferta concreta identificable.",
                            extractor_version=self.VERSION,
                        )
            else:
                offer = offers_data
        elif isinstance(offers_data, list) and offers_data:
            offer = offers_data[0]

        if not offer or not isinstance(offer, dict):
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(str(offers_data)),
                error_message="Estructura de oferta no reconocida.",
                extractor_version=self.VERSION,
            )

        # Rechazar ítems usados o reacondicionados en la oferta
        offer_condition = str(offer.get("itemCondition", "")).lower()
        if target_product.item_condition == "nuevo" and any(
            cond in offer_condition for cond in ("used", "refurbished", "usedcondition", "refurbishedcondition")
        ):
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                extracted_mpn=mpn or sku,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(offer, ensure_ascii=False)),
                error_message=f"Condición de la oferta incompatible: '{offer_condition}'. Se requiere producto nuevo.",
                extractor_version=self.VERSION,
            )

        # Moneda: ausente o vacía es un error, no asumir ARS
        raw_currency = offer.get("priceCurrency")
        if raw_currency is None or str(raw_currency).strip() == "":
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(offer, ensure_ascii=False)),
                error_message="Moneda no declarada en la oferta. No se asume ARS.",
                extractor_version=self.VERSION,
            )
        currency = str(raw_currency).strip().upper()
        if currency != "ARS":
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                currency=currency,
                availability="desconocido",
                extracted_title=name,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(offer, ensure_ascii=False)),
                error_message=f"Moneda no admitida: {currency}. Solo se aceptan ofertas en ARS.",
                extractor_version=self.VERSION,
            )

        # Precio de pago único
        raw_price = offer.get("price")
        price = self.parse_money(raw_price)
        if price is None:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                extracted_title=name,
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(json.dumps(offer, ensure_ascii=False)),
                error_message="Precio ausente o no parseable en la oferta estructurada.",
                extractor_version=self.VERSION,
            )

        # Disponibilidad
        raw_avail = str(offer.get("availability", "")).lower()
        if "instock" in raw_avail:
            availability = "disponible"
        elif "outofstock" in raw_avail or "discontinued" in raw_avail:
            availability = "agotado"
        else:
            availability = "desconocido"

        # Detección complementaria de precio por transferencia y precio tachado en visible
        price_transfer = None
        price_ref = None

        # Si en el HTML figura explícitamente descuento por transferencia
        price_container = soup.select_one('.precio-box, .product-price, .product-info, [itemtype="https://schema.org/Product"]')
        price_content = str(price_container) if price_container else ''
        if "transferencia" in price_content.lower():
            # Buscar mención de importe en pesos vinculado a transferencia
            m_transfer_val = re.search(r"\$\s*([\d\.\,]+)\s*(?:con|por)?\s*transferencia", price_content, re.IGNORECASE)
            if not m_transfer_val:
                m_transfer_val = re.search(r"transferencia[^\$]{0,40}\$\s*([\d\.\,]+)", price_content, re.IGNORECASE)
            if m_transfer_val:
                p_trans = self.parse_money(m_transfer_val.group(1))
                if p_trans and p_trans < price:
                    price_transfer = p_trans

        # Precio tachado / precio de lista de referencia mostrado
        ref_match = price_container.find(class_=re.compile(r"(precio-lista|tachado|strikethrough|price-reference|old-price)")) if price_container else None
        if ref_match:
            p_ref = self.parse_money(ref_match.get_text())
            if p_ref and p_ref > price:
                price_ref = p_ref

        # Contraste precio estructurado vs primer importe visible de magnitud similar
        # Si divergen más del 15%, retener para revisión
        if price is not None:
            visible_nodes = soup.select('.product-price, .price-selling, .best-price, [itemprop="price"]')
            visible_amounts = [node.get('content') or node.get_text(' ', strip=True) for node in visible_nodes
                               if not re.search(r'cuota|installment|transferencia|tachado|old-price', ' '.join(node.get('class', []))+' '+node.get_text(), re.I)]
            comparable_visible = []
            for va in visible_amounts:
                vp = self.parse_money(va)
                if vp and vp > 0:
                    comparable_visible.append(vp)
            if comparable_visible:
                # Buscar el importe visible más próximo al precio estructurado
                closest = max(comparable_visible, key=lambda x: abs(x - price))
                if closest > 0 and abs(price - closest) / closest > Decimal("0.01"):
                    # Divergencia significativa entre JSON-LD y precio visible
                    return ExtractionResult(
                        success=False,
                        price_single_payment=None,
                        availability="desconocido",
                        extracted_title=name,
                        extracted_mpn=mpn or sku,
                        raw_evidence_hash=evidence_hash,
                        raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
                        error_message=(
                            f"Divergencia de precio: JSON-LD ${price:,.2f} vs "
                            f"precio visible más cercano ${closest:,.2f} "
                            f"(diferencia {abs(price-closest)/closest*100:.1f}%). Retenido para revisión."
                        ),
                        extractor_version=self.VERSION,
                    )

        return ExtractionResult(
            success=True,
            price_single_payment=price,
            currency="ARS",
            price_transfer=price_transfer,
            price_reference_shown=price_ref,
            availability=availability,
            shipping_cost=None,
            shipping_note="No especificado",
            extracted_mpn=mpn or sku,
            extracted_title=name,
            raw_evidence_hash=evidence_hash,
            raw_evidence_snippet=self.extract_snippet(json.dumps(product_obj, ensure_ascii=False)),
            extractor_version=self.VERSION,
        )
