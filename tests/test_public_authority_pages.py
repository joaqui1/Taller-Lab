import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as app_module
import publicaciones_autoridad as authority
import servidor_local as site
from servidor_local import ALL_ARTICLES, render_article_page, render_sitemap


class PublicAuthorityPagesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd() / "tmp", prefix="test-public-authority-")
        self.data_dir = Path(self.temp.name)
        self.data_patch = patch.object(authority, "DATA_DIR", self.data_dir)
        self.data_patch.start()
        self.write("quienes_somos.json", {"publicado": False})
        self.write("consultas_fabricantes.json", {"consultas": []})
        self.write("prensa.json", {"menciones": []})
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.data_patch.stop()
        self.temp.cleanup()

    def write(self, filename, data):
        (self.data_dir / filename).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def response(index):
        answered = index == 1
        return {
            "id": f"consulta-{index}", "marca": "Marca de prueba", "modelo": f"Modelo {index}",
            "codigo": f"COD-{index}", "pregunta": f"¿Cuál es el dato documentado {index}?",
            "fecha_envio": "01/10/2026", "estado": "respondida" if answered else "enviada",
            "respuesta_textual": "Respuesta textual de prueba." if answered else "",
            "fecha_respuesta": "03/10/2026" if answered else "", "guias": ["/generadores/para-casa/"],
        }

    def publish_fixtures(self):
        self.write("quienes_somos.json", {
            "publicado": True, "quienes_somos": "Texto institucional de prueba.",
            "como_se_financia": "Financiamiento de prueba.", "que_no_aceptamos": "Límite de prueba.",
            "politica_independencia": "Independencia de prueba.", "contacto": "Contacto de prueba.",
        })
        self.write("consultas_fabricantes.json", {"consultas": [self.response(i) for i in range(1, 6)]})
        self.write("prensa.json", {"menciones": [{
            "medio": "Medio de prueba", "titulo": "Nota de prueba", "url": "https://ejemplo.com/nota",
            "fecha": "04/10/2026", "tipo": "cita", "dato_usado": "Dato de prueba usado.",
        }]})

    def test_empty_json_does_not_publish_pages_or_footer_links(self):
        routes = (authority.WHO_PATH, authority.MANUFACTURER_PATH, authority.PRESS_PATH)
        self.assertEqual(authority.indexable_authority_paths(), ())
        self.assertTrue(set(routes).isdisjoint(site.build_indexable_paths()))
        sitemap = render_sitemap()
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 404)
                self.assertIn("noindex", response.get_data(as_text=True))
                self.assertNotIn(route, sitemap)
        self.assertEqual(self.client.get(authority.MANUFACTURER_CSV_PATH).status_code, 404)
        home = self.client.get("/").get_data(as_text=True)
        for label in ("Quiénes somos", "Respuestas de fabricantes", "En los medios"):
            self.assertNotIn(label, home)

    def test_content_thresholds_publish_pages_sitemap_footer_csv_and_dataset(self):
        self.publish_fixtures()
        routes = (authority.WHO_PATH, authority.MANUFACTURER_PATH, authority.PRESS_PATH)
        self.assertEqual(set(authority.indexable_authority_paths()), set(routes))
        self.assertTrue(set(routes).issubset(site.build_indexable_paths()))
        sitemap = render_sitemap()
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(route, sitemap)
        home = self.client.get("/").get_data(as_text=True)
        for label in ("Quiénes somos", "Respuestas de fabricantes", "En los medios"):
            self.assertIn(label, home)

        page = self.client.get(authority.MANUFACTURER_PATH).get_data(as_text=True)
        self.assertIn("respondió 1 de 5", page)
        self.assertIn('id="consulta-1"', page)
        schemas = [json.loads(value) for value in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)]
        dataset = next(schema for schema in schemas if schema.get("@type") == "Dataset")
        self.assertEqual(dataset["@type"], "Dataset")
        self.assertEqual(dataset["publisher"]["@type"], "Organization")

        csv_response = self.client.get(authority.MANUFACTURER_CSV_PATH)
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response.headers.get("X-Robots-Tag"), "noindex, nofollow")
        self.assertIn("pregunta", csv_response.get_data(as_text=True))

    def test_four_valid_manufacturer_queries_stay_unpublished(self):
        self.publish_fixtures()
        self.write("consultas_fabricantes.json", {"consultas": [self.response(i) for i in range(1, 5)]})
        self.assertEqual(self.client.get(authority.MANUFACTURER_PATH).status_code, 404)
        self.assertNotIn(authority.MANUFACTURER_PATH, render_sitemap())
        self.assertEqual(self.client.get(authority.MANUFACTURER_CSV_PATH).status_code, 404)

    def test_markdown_marker_renders_only_associated_literal_answer(self):
        self.publish_fixtures()
        guide = copy.deepcopy(next(article for article in ALL_ARTICLES if article["url"] == "/generadores/para-casa/"))
        guide["body"] = "# Guía de prueba\n\n{{respuesta_fabricante:consulta-1}}\n"
        html = render_article_page(guide)
        self.assertIn("Respuesta oficial del fabricante", html)
        self.assertIn("Respuesta textual de prueba.", html)
        self.assertIn("/fabricantes/respuestas/#consulta-1", html)
        self.assertNotIn("consulta-2", html)


if __name__ == "__main__":
    unittest.main()
