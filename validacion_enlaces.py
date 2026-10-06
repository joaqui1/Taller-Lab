"""Valida enlaces rastreables de Markdown y HTML antes de servir páginas."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote


class EnlacesHTML(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.enlaces = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href is not None:
                self.enlaces.append(href)


def enlaces_invalidos(html, page_path, indexable_paths, site_url):
    """Incluye enlaces relativos, referencias Markdown y HTML, query y fragmento."""
    origin = urlsplit(site_url).netloc.lower()
    invalid = []
    for href in EnlacesHTML(html).enlaces:
        target = urlsplit(urljoin(site_url + page_path, href))
        if target.scheme not in ("http", "https") or target.netloc.lower() != origin:
            continue
        path = unquote(target.path or "/")
        # Permitir endpoints de descarga de datos verificados (CSV, JSON o rutas /descargar-csv)
        if path.endswith((".csv", ".json")) or path.endswith("/descargar-csv"):
            continue
        # Interfaces operativas accesibles, excluidas deliberadamente del índice.
        if path not in indexable_paths and path not in ('/comunidad/', '/alertas/estado/', '/alertas/editorial/'):
            invalid.append(href)
    return invalid


def validar_html(html, page_path, indexable_paths, site_url):
    invalid = enlaces_invalidos(html, page_path, indexable_paths, site_url)
    if invalid:
        raise ValueError(f"Enlaces internos no indexables en {page_path}: " + ", ".join(invalid))
