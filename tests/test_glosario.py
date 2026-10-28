import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from markdown_it import MarkdownIt

import app
import glosario_publicacion as glossary
import servidor_local as site


class GlossaryTests(unittest.TestCase):
    def setUp(self):
        temp_parent = Path.cwd() / "tmp"
        temp_parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_parent, prefix="tallerlab-glosario-")
        self.data_dir = Path(self.temp.name)
        self.directory_patch = patch.object(glossary, "GLOSSARY_DIR", self.data_dir)
        self.directory_patch.start()
        self.client = app.app.test_client()

    def tearDown(self):
        self.directory_patch.stop()
        self.temp.cleanup()

    def write_term(self, slug, title, state="borrador", definition="Definición de prueba.", variants=None):
        data = {
            "termino": title,
            "slug": slug,
            "definicion_corta": definition,
            "unidades": [],
            "terminos_relacionados": [],
            "guias": [],
            "fuentes": [],
            "reviewed": "",
            "estado": state,
            "variantes": variants or [],
        }
        lines = ["---"] + [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in data.items()] + ["---", ""]
        (self.data_dir / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")

    def test_drafts_do_not_enter_sitemap_and_empty_hub_is_noindex(self):
        self.write_term("termino-prueba", "Término de prueba")
        self.assertEqual(glossary.published_glossary_paths(), ())
        self.assertNotIn(glossary.GLOSSARY_HUB_PATH, site.build_indexable_paths())
        self.assertNotIn(glossary.GLOSSARY_HUB_PATH, site.render_sitemap())
        response = self.client.get(glossary.GLOSSARY_HUB_PATH)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="robots" content="noindex, follow"', response.text)

    def test_published_term_has_routes_breadcrumbs_and_schema(self):
        self.write_term("caudal", "Caudal", state="publicado", definition="Volumen que circula por unidad de tiempo.")
        hub = self.client.get(glossary.GLOSSARY_HUB_PATH)
        detail = self.client.get("/glosario/caudal/")
        self.assertEqual(hub.status_code, 200)
        self.assertEqual(detail.status_code, 200)
        self.assertIn('"@type": "DefinedTermSet"', hub.text)
        self.assertIn('"@type": "DefinedTerm"', detail.text)
        self.assertIn('aria-label="Ubicación"', detail.text)
        self.assertIn("Glosario", detail.text)
        self.assertIn(glossary.GLOSSARY_HUB_PATH, site.build_indexable_paths())
        self.assertIn("/glosario/caudal/", site.build_indexable_paths())
        self.assertIn("/glosario/caudal/", site.render_sitemap())
        self.assertEqual(self.client.get("/glosario/termino-prueba/").status_code, 404)

    def test_autolinks_first_occurrence_only_outside_titles_links_and_code(self):
        self.write_term("brushless", "motor brushless", state="publicado", variants=["brushless"])
        markdown = MarkdownIt("commonmark", {"html": True}).enable("table")
        source = "# motor brushless\n\n[brushless](https://example.com) `brushless` y motor brushless. Después, brushless."
        html = glossary.render_markdown_with_glossary(markdown, source)
        self.assertEqual(html.count('href="/glosario/brushless/"'), 1)
        self.assertIn("<h1>motor brushless</h1>", html)
        self.assertIn("<code>brushless</code>", html)
        self.assertIn('<a href="https://example.com">brushless</a>', html)

    def test_autolinks_are_limited_to_five_terms_per_guide(self):
        for index in range(6):
            self.write_term(f"termino-{index}", f"Término {index}", state="publicado")
        markdown = MarkdownIt("commonmark")
        source = " ".join(f"Término {index}." for index in range(6))
        html = glossary.render_markdown_with_glossary(markdown, source)
        self.assertEqual(html.count('class="glossary-term-link"'), 5)


if __name__ == "__main__":
    unittest.main()
