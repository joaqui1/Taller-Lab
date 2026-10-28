import json
import unittest

from tallerlab_data.guide_links import render_guide_technical_tools_block
from tallerlab_data.model_equivalences import (
    REVIEW_PATH,
    TABLE_PATH,
    build_equivalences,
    guides_for_tool_slug,
    related_paths,
    tool_slug_for_related_path,
)


class ModelInternalLinksTests(unittest.TestCase):
    def test_equivalence_files_are_reproducible_and_ambiguous_candidates_are_not_linked(self):
        table, review = build_equivalences()
        saved = json.loads(TABLE_PATH.read_text(encoding="utf-8"))["equivalences"]
        review_saved = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))["candidates"]
        self.assertEqual(saved, table)
        self.assertEqual(review_saved, review)
        self.assertTrue(all(
            entry["price_path"] is None or entry["price_path"].startswith("/datos/precios/")
            for entry in saved.values()
        ))
        uncertain = next(item for item in review if item["tool_slug"] == "lusqtoff-lc3550bk")
        self.assertNotEqual(saved["lusqtoff-lc3550bk"]["price_path"], uncertain["candidato"])

    def test_existing_guide_model_block_contains_exact_related_price_link(self):
        html = render_guide_technical_tools_block("/compresores/50-litros/")
        self.assertIn("Modelos de esta guía en nuestra Base Técnica", html)
        self.assertIn('href="/datos/precios/compresores/lusqtoff-lc2550b-8/"', html)

    def test_inverse_guides_resolve_from_model_and_price_identifier(self):
        expected = "/compresores/50-litros/"
        guides = {url for _, url in guides_for_tool_slug("lusqtoff-lc2550b-8")}
        self.assertIn(expected, guides)
        price_path = related_paths("lusqtoff-lc2550b-8")["price_path"]
        self.assertEqual(tool_slug_for_related_path("price_path", price_path), "lusqtoff-lc2550b-8")
        self.assertIn(expected, {url for _, url in guides_for_tool_slug(price_path.rstrip("/").split("/")[-1])})

    def test_product_fiche_renders_inverse_guide_section(self):
        import servidor_local

        page = servidor_local.render_tallerlab_data_page("/herramientas/lusqtoff-lc2550b-8/")
        self.assertIn("Guías que analizan este modelo", page)
        self.assertIn('href="/compresores/50-litros/"', page)

    def test_price_detail_builds_inverse_links_from_the_equivalence_table(self):
        from observatorio.estatico import model_body

        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "observatorio/piloto_gratuito.json").read_text(encoding="utf-8"))
        guides = json.loads((root / "observatorio/guias_por_modelo.json").read_text(encoding="utf-8"))
        model = next(row for row in manifest["models"] if row["id"] == "lusqtoff-lc2550b8")
        html = model_body({"model": model, "observation": None, "state": "pendiente", "series": [], "attempt": {}},
                          [], manifest["sources"], guides, lambda path: path,
                          "https://www.tallerlab.com.ar/datos/precios/compresores/lusqtoff-lc2550b-8/", "")
        self.assertIn("Guías que analizan este modelo", html)
        self.assertIn('href="https://www.tallerlab.com.ar/compresores/50-litros/"', html)

    def test_calculator_and_guide_link_to_each_other(self):
        import servidor_local

        generator = next(a for a in servidor_local.ALL_ARTICLES if a["url"] == "/generadores/para-casa/")
        calculator_link = servidor_local.render_article_calculator_link(generator)
        self.assertIn('href="/calculadoras/generador-para-casa/"', calculator_link)
        calculator = servidor_local.render_calculator_page("/calculadoras/generador-para-casa/")
        self.assertIn('href="/generadores/para-casa/"', calculator)

    def test_model_with_no_unambiguous_equivalence_does_not_get_extra_links(self):
        self.assertEqual(related_paths("modelo-sin-equivalencia")["price_path"], None)
        self.assertEqual(tool_slug_for_related_path("alert_path", "/alertas/modelo-dudoso/"), None)


if __name__ == "__main__":
    unittest.main()
