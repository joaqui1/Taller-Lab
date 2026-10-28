"""Rendering and validation checks for owner-approved compatibility ficha data."""

import copy
from datetime import date
import json
import re
import unittest
from unittest.mock import patch

from compatibilidad import catalog
from compatibilidad.editorial import EDITORIAL_FICHAS, render_editorial_blocks, validate_fichas_editorial
from compatibilidad.views import get_product_schema_json, render_tool_detail


def fact(value, unit, source, consulted, section="Fixture de prueba", note=None, value_format=None):
    excerpt = value if isinstance(value, str) else "Dato de prueba con valor numérico documentado"
    result = {
        "value": value,
        "unit": unit,
        "source": source,
        "section": section,
        "date_consulted": consulted,
        "excerpt": excerpt,
    }
    if note:
        result["note"] = note
    if value_format:
        result["value_format"] = value_format
    return result


def complete_fixture(product):
    evidence = catalog.EVIDENCES_BY_ID[product.evidence_identity_id]
    source = evidence.official_url
    consulted = date.fromisoformat(evidence.date_reviewed[:10]).strftime("%d/%m/%Y")
    battery = catalog.PRODUCTS_BY_ID["BAT-BOSCH-PROCORE-4AH"]
    charger = catalog.PRODUCTS_BY_ID["CHG-BOSCH-GAL-18V40-1600A028U0"]
    return {
        "publicado": True,
        "last_approved_modified_at": "2026-10-26",
        "compatibility": [{
            "counterpart_id": battery.id,
            "type": fact("Batería para herramienta", "tipo de relación", source, consulted),
            "conditions": fact("Usar el código exacto indicado", "condición", source, consulted),
        }],
        "specifications": {
            "voltage": fact(18, "V", source, consulted),
            "capacity_ah": fact(4, "Ah", source, consulted),
            "energy_wh": fact(72, "Wh", source, consulted, "Cálculo TallerLab: 18 V × 4 Ah"),
            "weight": fact(1.2, "kg", source, consulted, note="Sin batería."),
            "dimensions": fact([118, 75, 65], "mm", source, consulted, value_format="dimensions"),
            "cell_technology": fact("Ion-litio", "texto", source, consulted),
        },
        "charge_times": [{
            "counterpart_id": charger.id,
            "time": fact(35, "min", source, consulted),
            "label": fact("Carga al 80 %", "texto", source, consulted),
        }],
        "tool": {"packages": [{
            "code": fact(product.mpn, "texto", source, consulted),
            "package_type": fact("Solo cuerpo", "presentación", source, consulted),
            "box_contents": [fact("Herramienta, empuñadura y guarda", "elemento", source, consulted)],
        }]},
        "identification": {
            "text": fact("Buscá el código de pedido en la etiqueta de características.", "texto", source, consulted),
            "image": {
                "file": fact("/assets/compatibility-fixture.svg", "archivo", source, consulted),
                "alt": fact("Ilustración de prueba de una etiqueta", "texto alternativo", source, consulted),
                "author_or_license": fact("Fixture de prueba", "autor o licencia", source, consulted),
                "credit": fact("Imagen sintética de QA", "crédito visible", source, consulted),
            },
        },
        "common_errors": [fact("Confundir la familia con el código exacto.", "texto", source, consulted)],
        "faqs": [{
            "question": fact("¿Alcanza con comparar el voltaje?", "pregunta", source, consulted),
            "answer": fact("No; verificá el código y la documentación del fabricante.", "respuesta", source, consulted),
        }],
        "image": {
            "file": fact("/assets/compatibility-fixture.svg", "archivo", source, consulted),
            "alt": fact("Imagen de producto de prueba", "texto alternativo", source, consulted),
            "author_or_license": fact("Fixture de prueba", "autor o licencia", source, consulted),
            "credit": fact("Imagen sintética de QA", "crédito visible", source, consulted),
        },
    }


class CompatibilityEditorialTests(unittest.TestCase):
    def setUp(self):
        self.product = catalog.PRODUCTS_BY_ID["TOOL-BOSCH-GWS-18V-10"]
        self.fixture = complete_fixture(self.product)

    def test_default_editorial_file_has_all_ids_unpublished_and_valid(self):
        self.assertEqual(validate_fichas_editorial(), [])
        self.assertTrue(set(catalog.PRODUCTS_BY_ID) <= set(EDITORIAL_FICHAS))
        self.assertTrue(all(EDITORIAL_FICHAS[product_id].get("publicado") is False for product_id in catalog.PRODUCTS_BY_ID))

    def test_unpublished_fixture_does_not_add_empty_enrichment(self):
        hidden = copy.deepcopy(self.fixture)
        hidden["publicado"] = False
        with patch.dict(EDITORIAL_FICHAS, {self.product.id: hidden}):
            html = render_tool_detail(self.product)
        self.assertIn("<h1>Baterías compatibles con", html)
        self.assertIn('class="compat-direct-answer"', html)
        self.assertNotIn("compat-editorial-block", html)
        self.assertNotIn("Preguntas frecuentes</h2>", html)

    def test_complete_fixture_renders_all_blocks_in_order_and_image_schema(self):
        with patch.dict(EDITORIAL_FICHAS, {self.product.id: self.fixture}):
            html = render_tool_detail(self.product)
            schema_html = get_product_schema_json(self.product, "https://www.tallerlab.com.ar")

        markers = (
            'class="compat-direct-answer"',
            "Tabla de compatibilidad",
            "Especificaciones con fuente",
            "Tiempos de carga",
            "Presentación y contenido documentado",
            "Cómo identificar el código en la etiqueta",
            "Errores comunes",
            "Preguntas frecuentes",
            "Imagen del producto",
            "Fuente y comprobación documental",
            "Consultar precio y contenido del kit Bosch 1600A015TD",
        )
        positions = [html.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("72 Wh", html)
        self.assertIn("cálculo de TallerLab", html)
        self.assertIn("Nota: Sin batería.", html)
        self.assertIn("Carga al 80 %", html)
        self.assertIn("118 × 75 × 65 mm", html)
        self.assertIn('href="/baterias/bosch-procore18v-4-0ah-1600a016gb/"', html)
        self.assertIn("Imagen sintética de QA", html)
        self.assertNotIn('"@type": "FAQPage"', html)

        schema_json = re.search(r'<script type="application/ld\+json">(.*?)</script>', schema_html).group(1)
        schema = json.loads(schema_json)
        self.assertEqual(schema["primaryImageOfPage"]["contentUrl"], "https://www.tallerlab.com.ar/assets/compatibility-fixture.svg")
        self.assertEqual(schema["about"]["image"], "https://www.tallerlab.com.ar/assets/compatibility-fixture.svg")
        self.assertNotEqual(schema["@type"], "Product")

    def test_only_populated_blocks_render(self):
        self.assertEqual(render_editorial_blocks(self.product, {"publicado": True}), "")

    def test_validation_rejects_unofficial_url_bad_date_and_unknown_unit(self):
        valid_record = copy.deepcopy(self.fixture)
        invalid_fact = valid_record["specifications"]["voltage"]
        invalid_fact.update(source="https://bosch-professional.com.attacker.example/spec", date_consulted="2026-10-26", unit="volts")
        errors = validate_fichas_editorial({self.product.id: valid_record}, product_ids={self.product.id})
        joined = "\n".join(errors)
        self.assertIn("URL oficial HTTPS", joined)
        self.assertIn("dd/mm/aaaa", joined)
        self.assertIn("unidad desconocida", joined)

    def test_validation_rejects_legacy_products_list(self):
        data = {self.product.id: self.fixture, "productos": []}
        errors = validate_fichas_editorial(data, product_ids={self.product.id})
        self.assertTrue(any("no se admite la lista heredada" in error for error in errors))

    def test_validation_requires_numeric_values_for_numeric_units_and_short_excerpt(self):
        invalid = copy.deepcopy(self.fixture)
        invalid["specifications"]["weight"]["value"] = "1,9"
        invalid["specifications"]["weight"]["excerpt"] = " ".join(["palabra"] * 26)
        errors = validate_fichas_editorial({self.product.id: invalid}, product_ids={self.product.id})
        joined = "\n".join(errors)
        self.assertIn("debe ser numérico para la unidad kg", joined)
        self.assertIn("no puede superar 25 palabras", joined)

    def test_related_kit_cta_requires_published_bare_body_tool(self):
        from compatibilidad.commercial import render_pair_commercial, render_product_commercial

        battery = catalog.PRODUCTS_BY_ID["BAT-BOSCH-GBA-4AH"]
        no_record = copy.deepcopy(self.fixture)
        no_record["publicado"] = False
        with patch.dict(EDITORIAL_FICHAS, {self.product.id: no_record}):
            self.assertEqual(render_pair_commercial(battery, self.product), "")

        with patch.dict(EDITORIAL_FICHAS, {self.product.id: self.fixture}):
            self.assertIn("Consultar precio y contenido del kit Bosch 1600A015TD", render_pair_commercial(battery, self.product))
            self.assertIn('rel="sponsored nofollow noopener noreferrer"', render_product_commercial(self.product))

        full_kit = copy.deepcopy(self.fixture)
        full_kit["tool"]["packages"][0]["package_type"]["value"] = "Kit"
        with patch.dict(EDITORIAL_FICHAS, {self.product.id: full_kit}):
            self.assertEqual(render_product_commercial(self.product), "")
        self.assertEqual(render_product_commercial(battery), "")


if __name__ == "__main__":
    unittest.main()
