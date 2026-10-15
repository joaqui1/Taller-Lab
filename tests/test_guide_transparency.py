import copy
import re
import unittest
from unittest.mock import patch

import servidor_local as site


class TransparenciaDeGuiasTests(unittest.TestCase):
    def test_cada_guia_publicada_explica_una_vez_que_no_hubo_prueba_fisica(self):
        for article in site.ALL_ARTICLES:
            with self.subTest(url=article["url"]):
                html = site.render_article_page(article)
                self.assertEqual(html.count('<h2>Cómo investigamos esta guía</h2>'), 1)
                self.assertEqual(html.count("Prueba física: no realizada"), 1)
                self.assertEqual(len(re.findall(r"(?i)(?:sin prueba física|no realizó una prueba física|no se realizaron pruebas físicas|no incluye prueba física|no representa una prueba física)", html)), 0)
                method = html.split('aria-label="Cómo investigamos esta guía"', 1)[1].split("</section>", 1)[0]
                self.assertIn("Prueba física: no realizada", method)

    def test_limpiar_metodo_repetido_conserva_el_contenido_especifico_y_el_embed(self):
        article = copy.deepcopy(next(a for a in site.ALL_ARTICLES if a["url"] not in site.RESOURCES))
        article["reviewed"] = "15/10/2026"
        article["body"] = """# Guía de ejemplo

## Cómo investigamos esta guía

- Tipo de análisis: documental
- Prueba física de TallerLab: no
- Especificaciones contrastadas: sí
- Opiniones de compradores: no
- Fuentes primarias: sí
- Última revisión: 28/09/2026

Detalle documental específico que acompaña al método.

## Alcance del análisis

Conclusión editorial propia de esta guía.
"""
        rendered = site.render_article_page(article)
        embedded = site.render_article_page(article, embedded=True)
        for html in (rendered, embedded):
            self.assertEqual(html.count('<h2>Cómo investigamos esta guía</h2>'), 1)
            self.assertIn("Detalle documental específico que acompaña al método.", html)
            self.assertIn("Conclusión editorial propia de esta guía.", html)
        self.assertNotIn("Última revisión: 28/09/2026", rendered)
        self.assertIn("Última revisión: 15/10/2026", rendered)
        self.assertIn("Última revisión: 28/09/2026", embedded)
        article["body"] = article["body"].split("\n\nDetalle documental específico", 1)[0].rstrip()
        rendered = site.render_article_page(article)
        self.assertEqual(rendered.count('<h2>Cómo investigamos esta guía</h2>'), 1)
        self.assertNotIn("Última revisión: 28/09/2026", rendered)

    def test_veredictos_vacios_no_agregan_bloque_y_con_revisor_se_validan(self):
        article = copy.deepcopy(next(a for a in site.ALL_ARTICLES if a["url"] == "/generadores/para-casa/"))
        baseline = site.render_article_page(article)
        article["veredictos"] = [{"uso": "Cargas esenciales", "recomendacion": "Sumá la marcha", "condicion": "revisá el pico de arranque en el manual"}]
        article["revisor"] = "revisora-de-prueba"
        article["revision_tecnica"] = "12/10/2026"
        article["alcance_revision"] = "cálculo de cargas y lectura de placas"
        reviewer = {"slug": "revisora-de-prueba", "publicado": True, "nombre": "Revisora de prueba", "oficio": "Electricista matriculada", "foto": "/media/revisora-prueba.jpg"}
        with patch.object(site, "public_reviewer", return_value=reviewer):
            rendered = site.render_article_page(article)
        self.assertIn('class="reviewer-attribution"', rendered)
        self.assertIn('href="/revisores/revisora-de-prueba/"', rendered)
        self.assertIn('src="/media/revisora-prueba.jpg"', rendered)
        self.assertIn("12/10/2026", rendered)
        self.assertIn("cálculo de cargas y lectura de placas", rendered)
        self.assertIn("Respuesta por tarea", rendered)
        self.assertIn("Validado por Revisora de prueba", rendered)
        self.assertLess(rendered.index('class="task-verdicts"'), rendered.index("Cómo calcular la potencia"))
        article["veredictos"] = []
        self.assertEqual(site.render_article_page(article), baseline)

    def test_revisor_no_publicado_no_se_muestra_ni_valida_veredictos(self):
        article = copy.deepcopy(next(a for a in site.ALL_ARTICLES if a["url"] == "/generadores/para-casa/"))
        article["revisor"] = "revisora-oculta"
        article["veredictos"] = [{"uso": "Cargas esenciales", "recomendacion": "Sumá la marcha", "condicion": "revisá el pico"}]
        with patch.object(site, "public_reviewer", return_value=None):
            html = site.render_article_page(article)
        self.assertNotIn('class="reviewer-attribution"', html)
        self.assertNotIn("Validado por", html)

    def test_registros_opcionales_aparecen_en_metodo_solo_cuando_corresponden(self):
        article = copy.deepcopy(next(a for a in site.ALL_ARTICLES if a["url"] == "/compresores/50-litros/"))
        article["revisor"] = "revisor-prueba"
        article["revision_tecnica"] = "12/10/2026"
        article["alcance_revision"] = "caudal de salida"
        article["respuestas_usuarios"] = {"cantidad": 4}
        reviewer = {"slug": "revisor-prueba", "publicado": True, "nombre": "Revisor de prueba", "oficio": "Técnico mecánico"}
        with patch.object(site, "public_reviewer", return_value=reviewer), patch.object(
            site, "_manufacturer_responses_for_article",
            return_value=[{"id": "consulta-demo", "marca": "Marca de prueba", "fecha_respuesta": "11/10/2026"}],
        ):
            html = site.render_article_page(article)
        self.assertIn("Revisión técnica: Revisor de prueba", html)
        self.assertIn('href="/fabricantes/respuestas/#consulta-demo"', html)
        self.assertIn("Experiencia de usuarios: 4 respuestas registradas", html)

    def test_comision_aparece_junto_al_primer_enlace_de_compra(self):
        for url in ("/compresores/50-litros/", "/generadores/para-casa/", "/taladros/inalambricos/"):
            article = next(a for a in site.ALL_ARTICLES if a["url"] == url)
            html = site.render_article_page(article)
            self.assertEqual(html.count("Podemos recibir una comisión si comprás desde estos enlaces."), 1, url)
            note = html.index("Podemos recibir una comisión si comprás desde estos enlaces.")
            buy = html.find('rel="nofollow sponsored', note)
            self.assertGreater(buy, note, url)

    def test_veredictos_se_parsean_desde_frontmatter_yaml(self):
        frontmatter = '''---
veredictos:
  - uso: "Cargas esenciales"
    recomendacion: "Sumá la marcha"
    condicion: "Revisá el pico"
respuestas_usuarios:
  cantidad: 3
---
Texto de guía.
'''
        metadata, _ = site.extract_frontmatter(frontmatter)
        self.assertEqual(metadata["veredictos"], [{"uso": "Cargas esenciales", "recomendacion": "Sumá la marcha", "condicion": "Revisá el pico"}])
        self.assertEqual(metadata["respuestas_usuarios"], {"cantidad": "3"})


if __name__ == "__main__":
    unittest.main()
