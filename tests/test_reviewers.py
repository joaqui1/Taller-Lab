import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as app_module
import servidor_local as site


class ReviewerPagesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.reviewers_file = Path(self.temp.name) / "revisores.json"
        self.write_reviewers([])
        self.file_patch = patch.object(site, "REVIEWERS_FILE", self.reviewers_file)
        self.file_patch.start()
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.file_patch.stop()
        self.temp.cleanup()

    def write_reviewers(self, reviewers):
        self.reviewers_file.write_text(
            json.dumps({"_instrucciones": "datos de prueba", "revisores": reviewers}, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def reviewer(**overrides):
        record = {
            "slug": "persona-ficticia-de-prueba",
            "nombre": "Persona ficticia de prueba",
            "oficio": "Electricista matriculada",
            "anios_oficio": 8,
            "localidad": "Localidad de prueba",
            "foto": "/assets/revisores/persona-ficticia.jpg",
            "bio_corta": "Perfil inventado usado únicamente para verificar el render.",
            "perfiles": ["https://example.org/perfil"],
            "categorias": ["generadores"],
            "activo": True,
            "consentimiento_publicacion": True,
        }
        return {**record, **overrides}

    def test_sin_personas_no_publica_indice_ni_enlaces(self):
        self.assertEqual(site.indexable_reviewer_paths(), ())
        self.assertNotIn(site.REVIEWERS_PATH, site.build_indexable_paths())
        self.assertEqual(self.client.get(site.REVIEWERS_PATH).status_code, 404)
        self.assertEqual(self.client.get(site.REVIEWERS_PATH + "persona-ficticia-de-prueba/").status_code, 404)
        self.assertNotIn(site.REVIEWERS_PATH, site.render_sitemap())
        for path in ("/", site.AUTHOR_PATH):
            html = self.client.get(path).get_data(as_text=True)
            self.assertNotIn(site.REVIEWERS_PATH, html)

    def test_publica_solo_con_actividad_y_consentimiento_y_renderiza_perfil_y_guias(self):
        person = self.reviewer()
        inactive = self.reviewer(slug="inactiva", nombre="Persona inactiva", activo=False)
        no_consent = self.reviewer(slug="sin-consentimiento", nombre="Persona sin consentimiento", consentimiento_publicacion=False)
        self.write_reviewers([person, inactive, no_consent])

        article = copy.deepcopy(next(a for a in site.ALL_ARTICLES if a["url"] == "/generadores/para-casa/"))
        article["revisor"] = person["slug"]
        article["revision_tecnica"] = "12/10/2026"
        with patch.object(site, "ALL_ARTICLES", [article]):
            self.assertEqual([r["slug"] for r in site.public_reviewers()], [person["slug"]])
            self.assertEqual(
                site.indexable_reviewer_paths(),
                (site.REVIEWERS_PATH, site.REVIEWERS_PATH + person["slug"] + "/"),
            )
            self.assertTrue(set(site.indexable_reviewer_paths()).issubset(site.build_indexable_paths()))
            self.assertIn(site.REVIEWERS_PATH, site.render_sitemap())
            self.assertIn(site.REVIEWERS_PATH + person["slug"] + "/", site.render_sitemap())

            listing = self.client.get(site.REVIEWERS_PATH)
            profile = self.client.get(site.REVIEWERS_PATH + person["slug"] + "/")
            self.assertEqual(listing.status_code, 200)
            self.assertEqual(profile.status_code, 200)
            listing_html = listing.get_data(as_text=True)
            profile_html = profile.get_data(as_text=True)
            self.assertIn("Equipo de revisión técnica", listing_html)
            self.assertIn("Persona ficticia de prueba", profile_html)
            self.assertIn("Electricista matriculada", profile_html)
            self.assertIn("Perfil inventado usado únicamente", profile_html)
            self.assertIn("https://example.org/perfil", profile_html)
            self.assertIn("revisada el 12/10/2026", profile_html)
            self.assertNotIn("Persona inactiva", listing_html)
            self.assertNotIn("Persona sin consentimiento", listing_html)
            self.assertIn('href="/revisores/"', self.client.get(site.AUTHOR_PATH).get_data(as_text=True))
            self.assertIn('href="/revisores/"', self.client.get("/").get_data(as_text=True))

            person_json = json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>', profile_html, re.S)[-1])
            self.assertEqual(person_json["@type"], "Person")
            self.assertEqual(person_json["@id"], site.absolute_url(site.REVIEWERS_PATH + person["slug"] + "/") + "#person")
            self.assertEqual(person_json["sameAs"], person["perfiles"])

            article_schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', site.article_schema_tag(article), re.S).group(1))
            self.assertEqual(article_schema["reviewedBy"]["@id"], person_json["@id"])

    def test_slug_no_existente_no_se_publica(self):
        self.write_reviewers([self.reviewer()])
        self.assertEqual(self.client.get(site.REVIEWERS_PATH + "otro/" ).status_code, 404)


if __name__ == "__main__":
    unittest.main()
