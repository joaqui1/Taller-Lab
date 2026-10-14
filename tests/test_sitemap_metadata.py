"""Fechas y coherencia de indexación del sitemap principal."""
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit
import unittest
import xml.etree.ElementTree as ET

import app as app_module
import servidor_local


class _RobotsMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.directives = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "meta":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("name", "").lower() == "robots":
            self.directives.append(values.get("content", "").lower())


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


if __name__ == "__main__":
    unittest.main()
