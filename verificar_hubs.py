"""Comprueba rutas, enlaces y metadatos tras cambios globales del sitio."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

if (Path(__file__).parent / ".qa-deps").exists():
    sys.path.insert(0, str(Path(__file__).parent / ".qa-deps"))
import servidor_local as site
from app import app


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links, self.ids, self.canonicals = [], [], []
        self.headings = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "h1":
            self.headings += 1
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs["href"])


def main():
    client = app.test_client()
    for path in site.INDEXABLE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path
        html = response.get_data(as_text=True)
        page = Page(html)
        assert page.canonicals == [site.absolute_url(path)], path
        assert page.headings == 1, path
        assert len(page.ids) == len(set(page.ids)), path
        for phrase in ("revisión editorial pendiente", "afirmaciones sin revisar", "presión real", "caudal real", "presiones reales"):
            assert phrase not in html.lower(), (path, phrase)
        if path != "/":
            redirect = client.get(path[:-1] + "?origen=qa")
            assert redirect.status_code == 301, path
            assert redirect.headers["Location"] == path + "?origen=qa", path
        for href in page.links:
            if href.startswith("/") and not href.startswith("/assets/"):
                assert href.split("#")[0] in site.INDEXABLE_PATH_SET, (path, href)
            if href.startswith("#"):
                assert href[1:] in page.ids, (path, href)
    for article in site.ALL_ARTICLES:
        assert article["author"] == "Equipo editorial TallerLab", article["url"]
        html = client.get(article["url"]).get_data(as_text=True)
        schemas = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]
        schemas = [schema for schema in schemas if schema.get("@type") == "Article"]
        assert len(schemas) == 1, article["url"]
        assert schemas[0]["mainEntityOfPage"] == site.absolute_url(article["url"]), article["url"]
        assert schemas[0]["headline"] == article["h1"], article["url"]
    for section in site.CATEGORY_META:
        page = Page(client.get(f"/{section}/").get_data(as_text=True))
        anchors = [anchor for _, anchor, _, _ in site.HUB_STEPS]
        assert [identifier for identifier in page.ids if identifier in anchors] == anchors, section
        for article in site.ALL_ARTICLES:
            if article["section"] == section:
                assert article["url"] == f"/{section}/" or article["url"] in page.links, article["url"]
    assert client.get("/no-existe/").status_code == 404
    assert client.head("/sierras/").status_code == 200
    print(f"OK: {len(site.INDEXABLE_PATHS)} rutas y canonical; redirects con query; {len(site.ALL_ARTICLES)} autores y Article; 8 hubs completos; enlaces, anclas, H1, 404 y HEAD.")
    if "--seo-snapshot" in sys.argv:
        print(json.dumps({"paths": site.INDEXABLE_PATHS, "sitemap": site.render_sitemap(), "robots": site.render_robots()}))


if __name__ == "__main__":
    main()
