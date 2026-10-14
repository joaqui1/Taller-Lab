import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import servidor_local as site
from tallerlab_data import storage


class AuthorProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.profile_file = Path(self.temp.name) / "perfil_autor.json"
        self.profile_patch = patch.object(site, "AUTHOR_PROFILE_FILE", self.profile_file)
        self.profile_patch.start()
        self.write_profile({"email_publico": ""})

    def tearDown(self):
        self.profile_patch.stop()
        self.temp.cleanup()

    def write_profile(self, values):
        self.profile_file.write_text(json.dumps(values, ensure_ascii=False), encoding="utf-8")

    def test_campos_vacios_no_agregan_secciones_opcionales(self):
        self.write_profile({
            "foto": "", "experiencia": "", "formacion": "", "que_hace": [],
            "que_no_hace": [], "perfiles": [], "email_publico": "",
        })
        with patch.object(site, "author_metrics", return_value={
            "guias_publicadas": 0, "fichas": 0,
            "documentos_fabricante": 0, "correcciones_publicadas": 0,
        }):
            html = site.render_editorial_page("equipo")
        for marker in ('class="author-photo"', "<h2>Qué hago</h2>", "<h2>Qué no hago</h2>", "<h2>Experiencia</h2>", "<h2>Formación</h2>"):
            self.assertNotIn(marker, html)

    def test_muestra_datos_reales_configurados_y_person_incluye_foto(self):
        self.write_profile({
            "foto": "assets/logo_cropped.webp",
            "experiencia": "Edición documental.",
            "formacion": "Formación declarada.",
            "que_hace": ["Contrasta fuentes oficiales.", "Explica cálculos."],
            "que_no_hace": ["No realiza pruebas físicas."],
            "perfiles": ["https://example.org/joaquin"],
            "email_publico": "",
        })
        with patch.object(site, "author_metrics", return_value={
            "guias_publicadas": 10, "fichas": 3,
            "documentos_fabricante": 2, "correcciones_publicadas": 4,
        }):
            html = site.render_editorial_page("equipo")
        self.assertIn('src="/assets/logo_cropped.webp"', html)
        self.assertIn("<h2>Qué hago</h2>", html)
        self.assertIn("<h2>Qué no hago</h2>", html)
        self.assertIn("Contrasta fuentes oficiales.", html)
        self.assertIn("No realiza pruebas físicas.", html)
        self.assertIn("Documentos de fabricante citados", html)
        self.assertIn("<dd>10</dd>", html)
        self.assertEqual(site.author_schema()["image"], site.absolute_url("/assets/logo_cropped.webp"))
        profile = site.author_profile_page_schema()
        self.assertEqual(profile["mainEntity"]["image"], site.absolute_url("/assets/logo_cropped.webp"))

    def test_metricas_se_calculan_desde_fuentes_publicas(self):
        article = copy.deepcopy(next(a for a in site.ALL_ARTICLES if a["url"] == "/generadores/para-casa/"))
        article["body"] = (
            "[Manual oficial](https://www.bosch-professional.com/manual.pdf)\n"
            "[El mismo manual](https://www.bosch-professional.com/manual.pdf)\n"
            "## Historial de correcciones\n\n"
            "- **12/10/2026 — Dato corregido:** cambio publicado.\n"
        )
        tool = SimpleNamespace(
            primary_sources=[{"url": "https://www.bosch-professional.com/ficha", "label": "Ficha oficial"}],
            specifications=[SimpleNamespace(source_url="https://www.bosch-professional.com/manual.pdf", source_name="Manual oficial")],
        )
        with patch.object(site, "ALL_ARTICLES", [article]), \
                patch.object(site, "TALLERLAB_DATA_TOOL_PATHS", ("/herramientas/uno/", "/herramientas/dos/", "/herramientas/tres/")), \
                patch.object(site, "get_all_tools", return_value=[tool]), \
                patch.object(storage, "list_corrections", return_value=[{}, {}]):
            self.assertEqual(site.author_metrics(), {
                "guias_publicadas": 1,
                "fichas": 3,
                "documentos_fabricante": 2,
                "correcciones_publicadas": 3,
            })


if __name__ == "__main__":
    unittest.main()
