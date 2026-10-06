"""Importador de feeds de catálogo en formato JSON o CSV autorizados."""

import csv
import json
import io
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional

from observatorio.extractors.base import BaseExtractor, ExtractionResult
from observatorio.extractors.identity import identity_error


class FeedImporter(BaseExtractor):
    """Extractor/Importador para feeds de datos directos suministrados por comercios."""

    VERSION = "1.0.0"

    def extract(self, content: str, url: str, target_product) -> ExtractionResult:
        evidence_hash = self.compute_evidence_hash(content)
        content_clean = content.strip()

        # Detectar si el feed es JSON o CSV
        if content_clean.startswith("{") or content_clean.startswith("["):
            return self._extract_json(content_clean, target_product, evidence_hash)
        else:
            return self._extract_csv(content_clean, target_product, evidence_hash)

    def _extract_json(self, content: str, target_product, evidence_hash: str) -> ExtractionResult:
        try:
            data = json.loads(content, parse_float=Decimal)
        except Exception as e:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message=f"Error al decodificar feed JSON: {e}",
                extractor_version=self.VERSION,
            )

        items: List[Dict[str, Any]] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # Podría ser {"productos": [...]} o un producto individual
            if "productos" in data and isinstance(data["productos"], list):
                items = data["productos"]
            elif "items" in data and isinstance(data["items"], list):
                items = data["items"]
            else:
                items = [data]

        target_mpn = re.sub(r"[^A-Za-z0-9]", "", target_product.mpn).upper()

        matched_item = None
        for it in items:
            it_mpn = re.sub(r"[^A-Za-z0-9]", "", str(it.get("mpn") or it.get("sku") or "")).upper()
            it_title = str(it.get("titulo") or it.get("title") or it.get("nombre") or "").lower()
            
            if target_mpn and target_mpn == it_mpn:
                matched_item = it
                break
            if not it_mpn and target_product.brand.lower() in it_title and target_product.model_name.lower() in it_title:
                matched_item = it
                break

        if not matched_item:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message=f"El modelo '{target_product.brand} {target_product.model_name}' (MPN: {target_product.mpn}) no figura en el feed provisto.",
                extractor_version=self.VERSION,
            )

        if isinstance(data, dict):
            # La moneda explícita del catálogo puede aplicarse a sus productos.
            root_currency = data.get('moneda') or data.get('currency')
            if root_currency and not (matched_item.get('moneda') or matched_item.get('currency')):
                matched_item = dict(matched_item, moneda=root_currency)
        return self._build_result_from_dict(matched_item, evidence_hash, target_product)

    def _extract_csv(self, content: str, target_product, evidence_hash: str) -> ExtractionResult:
        reader = csv.DictReader(io.StringIO(content))
        target_mpn = re.sub(r"[^A-Za-z0-9]", "", target_product.mpn).upper()

        matched_row = None
        for row in reader:
            row_mpn = re.sub(r"[^A-Za-z0-9]", "", str(row.get("mpn") or row.get("sku") or "")).upper()
            row_title = str(row.get("titulo") or row.get("title") or row.get("nombre") or "").lower()
            
            if target_mpn and target_mpn == row_mpn:
                matched_row = row
                break
            if not row_mpn and target_product.brand.lower() in row_title and target_product.model_name.lower() in row_title:
                matched_row = row
                break

        if not matched_row:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(content),
                error_message=f"El modelo '{target_product.brand} {target_product.model_name}' no figura en el feed CSV.",
                extractor_version=self.VERSION,
            )

        return self._build_result_from_dict(matched_row, evidence_hash, target_product)

    def _build_result_from_dict(self, item: Dict[str, Any], evidence_hash: str, target_product) -> ExtractionResult:
        mismatch = identity_error(target_product, item.get('mpn') or '', item.get('titulo') or item.get('title') or item.get('nombre') or '',
                                  item.get('voltage') or item.get('voltaje') or '', item.get('condition') or '', item.get('kit') or '')
        if mismatch:
            return ExtractionResult(False,None,error_message=mismatch,raw_evidence_hash=evidence_hash)
        currency = str(item.get("moneda") or item.get("currency") or "").strip().upper()
        if currency != "ARS":
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                currency=currency,
                availability="desconocido",
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(str(item)),
                error_message=f"Moneda en feed no admitida: {currency}.",
                extractor_version=self.VERSION,
            )

        price = self.parse_money(item.get("precio_final") or item.get("precio_contado") or item.get("price"))
        if price is None:
            return ExtractionResult(
                success=False,
                price_single_payment=None,
                availability="desconocido",
                raw_evidence_hash=evidence_hash,
                raw_evidence_snippet=self.extract_snippet(str(item)),
                error_message="Precio final ausente o nulo en el feed.",
                extractor_version=self.VERSION,
            )

        price_transfer = self.parse_money(item.get("precio_transferencia") or item.get("transfer_price"))
        price_ref = self.parse_money(item.get("precio_referencia") or item.get("precio_lista"))

        # Disponibilidad
        stock_value = next((item[key] for key in ('disponibilidad','stock','disponible') if key in item and item[key] is not None), '')
        raw_stock = str(stock_value).lower()
        if raw_stock in ("disponible", "instock", "true", "1", "si", "sí") or (raw_stock.isdigit() and int(raw_stock) > 0):
            availability = "disponible"
        elif raw_stock in ("agotado", "outofstock", "false", "0", "no"):
            availability = "agotado"
        else:
            availability = "desconocido"

        mpn = str(item.get("mpn") or item.get("sku") or "")
        title = str(item.get("titulo") or item.get("title") or item.get("nombre") or "")

        return ExtractionResult(
            success=True,
            price_single_payment=price,
            currency="ARS",
            price_transfer=price_transfer,
            price_reference_shown=price_ref,
            availability=availability,
            shipping_cost=None,
            shipping_note="Consultar según código postal",
            extracted_mpn=mpn,
            extracted_title=title,
            raw_evidence_hash=evidence_hash,
            raw_evidence_snippet=self.extract_snippet(json.dumps(item, ensure_ascii=False, default=str) if isinstance(item, dict) else str(item)),
            extractor_version=self.VERSION,
        )
