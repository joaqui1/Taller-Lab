"""Regression checks for internal navigation into the compatibility catalog."""

import copy
import unittest
from html.parser import HTMLParser
from unittest.mock import patch

from compatibilidad import catalog
from compatibilidad.presentation import guide_compatibility_block, product_path
from compatibilidad.views import (
    COMPATIBILITY_STATIC_PATHS,
    render_compatibility_hub_html,
    get_compatibility_meta,
    render_platform_page_html,
)


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.hrefs.append(attributes["href"])
        if tag == "meta" and attributes.get("name", "").lower() == "robots":
            self.noindex = self.noindex or "noindex" in attributes.get("content", "").lower()


class CompatibilityInternalLinksTests(unittest.TestCase):
    def setUp(self):
        catalog.apply_state(catalog.baseline_state())

    def tearDown(self):
        catalog.apply_state(catalog.baseline_state())

    def test_target_guides_link_to_product_fiches_not_pair_queries(self):
        expected = {
            "/amoladoras/inalambricas/": {"BAT-BOSCH-PROCORE-4AH"},
            "/taladros/atornilladores-de-impacto/": {"TOOL-BOSCH-GDX-18V-200"},
            "/taladros/bosch-inalambrico/": {
                "BAT-BOSCH-GBA-2AH",
                "BAT-BOSCH-PROCORE-8AH",
                "BAT-BOSCH-GBA-4AH",
                "BAT-BOSCH-GBA-5AH",
                "CHG-BOSCH-GAL-18V40-1600A028U0",
                "CHG-BOSCH-GAL-1880CV-1600A015TL",
            },
        }
        for guide_url, product_ids in expected.items():
            with self.subTest(guide_url=guide_url):
                html = guide_compatibility_block(guide_url)
                self.assertIn('class="compat-guide-block"', html)
                links = LinkCollector()
                links.feed(html)
                hrefs = set(links.hrefs)
                self.assertFalse(any(href.startswith("/compatibilidad/") and "-con-" in href for href in hrefs))
                for product_id in product_ids:
                    product = catalog.PRODUCTS_BY_ID[product_id]
                    self.assertEqual(product.guide_url, guide_url)
                    self.assertEqual(product.status, "publicado")
                    self.assertIn(product_path(product), hrefs)

    def test_blocks_render_on_the_three_indexable_guide_pages(self):
        import servidor_local

        target_urls = (
            "/amoladoras/inalambricas/",
            "/taladros/atornilladores-de-impacto/",
            "/taladros/bosch-inalambrico/",
        )
        articles = {article["url"]: article for article in servidor_local.ALL_ARTICLES}
        for guide_url in target_urls:
            with self.subTest(guide_url=guide_url):
                self.assertIn(guide_url, servidor_local.INDEXABLE_PATHS)
                rendered = servidor_local.render_article_page(articles[guide_url])
                links = LinkCollector()
                links.feed(rendered)
                self.assertIn('class="compat-guide-block"', rendered)
                self.assertFalse(any(href.startswith("/compatibilidad/") and "-con-" in href for href in links.hrefs))

    def test_indexable_hub_links_every_published_product_and_active_platforms(self):
        import servidor_local

        self.assertIn("/compatibilidad/", COMPATIBILITY_STATIC_PATHS)
        self.assertIn("/compatibilidad/", servidor_local.INDEXABLE_PATHS)
        with patch("compatibilidad.views.track_event"):
            hub = LinkCollector()
            hub.feed(render_compatibility_hub_html())
            self.assertFalse(hub.noindex)
            for product in catalog.CATALOG_PRODUCTS:
                path = product_path(product)
                if product.status == "publicado" and path in servidor_local.INDEXABLE_PATHS:
                    self.assertIn(path, hub.hrefs, product.id)
                    _, _, head_metadata = get_compatibility_meta(path)
                    self.assertNotIn('name="robots" content="noindex', head_metadata, product.id)
            self.assertIn("/plataformas/bosch-professional-18v/", hub.hrefs)
            self.assertIn("/plataformas/gamma-multi-energy/", hub.hrefs)

            bosch_page = render_platform_page_html("bosch-professional-18v")
        platform_links = LinkCollector()
        platform_links.feed(bosch_page)
        self.assertIn("/plataformas/gamma-multi-energy/", platform_links.hrefs)
        self.assertIn("no implica que sus baterías sean intercambiables", bosch_page)

    def test_static_guide_urls_survive_older_persisted_product_metadata(self):
        state = copy.deepcopy(catalog.baseline_state())
        product = next(item for item in state["products"] if item["id"] == "BAT-BOSCH-PROCORE-8AH")
        product["guide_url"] = None
        catalog.apply_state(state)
        self.assertEqual(
            catalog.PRODUCTS_BY_ID["BAT-BOSCH-PROCORE-8AH"].guide_url,
            "/taladros/bosch-inalambrico/",
        )


if __name__ == "__main__":
    unittest.main()
