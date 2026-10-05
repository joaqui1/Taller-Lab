"""Regresiones SEO de Documentación y alertas: indexación, metadatos, sitemap y avisos en guías."""
import json
import re
import unittest

import app as app_module
from alertas_datos import cargar_expedientes
from alertas_seo import dossier_meta, expediente_indexable, render_aviso_guia


def _ld(html, tipo):
    for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        data = json.loads(bloque)
        if data.get("@type") == tipo:
            return data
    return None


class AlertasSEOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app_module.app.test_client()
        cls.expedientes = cargar_expedientes()

    def test_titulos_y_descripciones_dentro_de_limites(self):
        for exp in self.expedientes:
            titulo, desc = dossier_meta(exp)
            self.assertLessEqual(len(titulo), 60, titulo)
            self.assertLessEqual(len(desc), 160, desc)
            self.assertIn(exp["modelo_base"], titulo)

    def test_fichas_no_revisadas_noindex_y_fuera_del_sitemap(self):
        sitemap = self.client.get("/sitemap.xml").get_data(as_text=True)
        for exp in self.expedientes:
            path = f"/alertas/{exp['slug']}/"
            html = self.client.get(path).get_data(as_text=True)
            noindex = 'name="robots" content="noindex, follow"' in html
            if expediente_indexable(exp):
                self.assertFalse(noindex, path)
                self.assertRegex(sitemap, re.escape(path) + r"</loc><lastmod>\d{4}-\d{2}-\d{2}</lastmod>")
            else:
                self.assertTrue(noindex, path)
                self.assertNotIn(path + "<", sitemap)

    def test_techarticle_con_autor_persona_y_fuentes(self):
        exp = next(e for e in self.expedientes if e.get("alertas"))
        html = self.client.get(f"/alertas/{exp['slug']}/").get_data(as_text=True)
        data = _ld(html, "TechArticle")
        self.assertEqual(data["author"]["@type"], "Person")
        self.assertEqual(data["author"]["name"], "Joaquín Vallasciani")
        self.assertTrue(data["author"]["url"].endswith("/autor/joaquin-vallasciani/"))
        self.assertTrue(data["isBasedOn"])
        self.assertIn('id="resumen"', html)
        miga = _ld(html, "BreadcrumbList")["itemListElement"]
        self.assertEqual(miga[1]["name"], "Documentación y alertas")

    def test_hub_lista_solo_expedientes_indexables(self):
        html = self.client.get("/alertas/").get_data(as_text=True)
        data = _ld(html, "CollectionPage")
        urls = [i["url"] for i in data["mainEntity"]["itemListElement"]]
        for exp in self.expedientes:
            self.assertEqual(any(u.endswith(f"/alertas/{exp['slug']}/") for u in urls), expediente_indexable(exp))
        self.assertIn("Registro de alertas y recalls de herramientas", html)

    def test_aviso_en_guia_solo_si_menciona_modelo_con_alerta(self):
        con_alerta = next(e for e in self.expedientes if e.get("guia_url") and e.get("alertas"))
        self.assertIn(f"/alertas/{con_alerta['slug']}/", render_aviso_guia(con_alerta["guia_url"], ""))
        self.assertEqual(render_aviso_guia("/guia-inexistente/", "Texto sin modelos."), "")


if __name__ == "__main__":
    unittest.main()
