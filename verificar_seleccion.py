"""Integración de recursos y selección comercial sin registrar clics ni salir a ML."""
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlsplit

import servidor_local as site
from recursos_compra import EXTRA_RESOURCES, BUYING_NOTES
from recursos_uso import USE_RESOURCES


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links, self.resources, self.notes, self.source_ids = [], [], [], 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.links.append(attrs)
        if "editorial-resource" in attrs.get("class", "").split():
            self.resources.append(attrs)
        if "buying-note" in attrs.get("class", "").split():
            self.notes.append(attrs)
        if attrs.get("id") == "fuentes-consultadas":
            self.source_ids += 1


def main():
    article_map = {article["url"]: article for article in site.ALL_ARTICLES}
    assert len(EXTRA_RESOURCES) == 16 and len(USE_RESOURCES) == 20 and len(site.RESOURCES) == 72
    assert set(USE_RESOURCES).isdisjoint(EXTRA_RESOURCES)
    assert len({resource["title"] for resource in site.RESOURCES.values()}) == len(site.RESOURCES)
    assert set(BUYING_NOTES) == set(EXTRA_RESOURCES)
    assert set(site.RESOURCES) <= article_map.keys()
    commercial = Counter()
    for article in site.ALL_ARTICLES:
        document = Document(site.render_article_page(article))
        selected = article["url"] in site.RESOURCES
        assert len(document.resources) == int(selected), article["url"]
        if selected:
            assert document.source_ids == 1, article["url"]
        assert len(document.notes) == int(article["url"] in BUYING_NOTES), article["url"]
        for link in document.links:
            href = link.get("href", "")
            host = urlsplit(href).hostname or ""
            if host == "meli.la":
                assert href in site.AFFILIATE_URLS, (article["url"], href)
                assert "sponsored" in link.get("rel", "").split(), href
                commercial["affiliate"] += 1
            elif host == "mercadolibre.com.ar" or host.endswith(".mercadolibre.com.ar"):
                assert "sponsored" not in link.get("rel", "").split(), href
                commercial["general"] += 1
        if article["url"] in BUYING_NOTES:
            expected = BUYING_NOTES[article["url"]]
            actions = [link for link in document.links if link.get("data-affiliate-placement") == "editorial-choice"]
            assert [link["href"] for link in actions] == [url for url, _ in expected["urls"]]
            for link in actions:
                assert site.validate_affiliate_click(dict(product=link["href"], page=article["url"], placement="editorial-choice")), link
            assert expected["alternative"][0] in site.INDEXABLE_PATH_SET
            assert document.notes[0]["data-buying-status"] == ("choice" if expected["recommend"] else "check")
    # Estas dudas cambian la elegibilidad; una refactorización no debe darles sello de elección.
    for path in ("/sierras/de-banco-lusqtoff/", "/sierras/sensitivas-total/", "/soldadoras/mig-lusqtoff/", "/generadores/chicos/"):
        assert BUYING_NOTES[path]["recommend"] is False, path
    assert "3.800 rpm" not in site.PRODUCT_FACTS["https://meli.la/1mLrBwo"]["specs"]
    assert all("rpm" not in field for field in site.PRODUCT_FACTS["https://meli.la/1ntghna"]["specs"])
    print(f"OK: {len(site.RESOURCES)} recursos; {len(BUYING_NOTES)} bloques de compra; variante dudosa sin recomendación; {commercial['affiliate']} enlaces afiliados y {commercial['general']} generales con rel correcto.")


if __name__ == "__main__":
    main()
