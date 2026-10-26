"""Fechas y coherencia de indexación del sitemap principal."""
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit
import unittest
import xml.etree.ElementTree as ET

import app as app_module
import servidor_local
from compatibilidad.presentation import relationship_paths


class _RobotsMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.directives = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta" and values.get("name", "").lower() == "robots":
            self.directives.append(values.get("content", "").lower())
        elif tag.lower() == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))


class SitemapMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app_module.app.test_client()

    def _sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        return ET.fromstring(response.get_data(as_text=True))

    def test_todas_las_guias_publicadas_tienen_lastmod_igual_a_reviewed(self):
        root = self._sitemap()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        lastmods = {}
        for url in root.findall("sm:url", ns):
            loc = url.findtext("sm:loc", namespaces=ns)
            lastmod = url.findtext("sm:lastmod", namespaces=ns)
            if loc:
                lastmods[urlsplit(loc).path] = lastmod

        for article in servidor_local.ALL_ARTICLES:
            expected = datetime.strptime(article["reviewed"], "%d/%m/%Y").date().isoformat()
            self.assertEqual(lastmods.get(article["url"]), expected, article["url"])

    def test_ninguna_url_del_sitemap_devuelve_noindex(self):
        root = self._sitemap()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        paths = [
            urlsplit(url.findtext("sm:loc", namespaces=ns)).path
            for url in root.findall("sm:url", ns)
        ]
        for path in paths:
            response = self.client.get(path)
            header = response.headers.get("X-Robots-Tag", "").lower()
            parser = _RobotsMetaParser()
            parser.feed(response.get_data(as_text=True))
            response.close()
            directives = " ".join(parser.directives)
            self.assertNotIn("noindex", header, path)
            self.assertNotIn("noindex", directives, path)

    def test_sitemap_excluye_relaciones_y_historial_de_cambios(self):
        root = self._sitemap()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        paths = {
            urlsplit(url.findtext("sm:loc", namespaces=ns)).path
            for url in root.findall("sm:url", ns)
        }
        self.assertTrue(set(relationship_paths()).isdisjoint(paths))
        self.assertFalse(any(path.startswith("/compatibilidad/") and "-con-" in path for path in paths))
        self.assertNotIn("/compatibilidad/cambios/", paths)

    def test_relaciones_responden_noindex_una_vez_con_canonical_propio(self):
        for path in relationship_paths():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                parser = _RobotsMetaParser()
                parser.feed(html)
                self.assertEqual(parser.directives, ["noindex, follow"])
                self.assertEqual(parser.canonicals, [servidor_local.absolute_url(path)])
                self.assertNotIn('"@type": "WebPage"', html)

    def test_historial_de_cambios_es_noindex_con_canonical_propio(self):
        path = "/compatibilidad/cambios/"
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        parser = _RobotsMetaParser()
        parser.feed(response.get_data(as_text=True))
        self.assertEqual(parser.directives, ["noindex, follow"])
        self.assertEqual(parser.canonicals, [servidor_local.absolute_url(path)])


if __name__ == "__main__":
    unittest.main()
