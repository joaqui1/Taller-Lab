"""Puerta de publicación: verifica cada ruta y sus recursos en el HTML servido."""
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET
from auditoria_seo_consultor import Doc, inspect
import servidor_local as site
from app import app

def main():
    client = app.test_client()
    pages, assets, external_images, titles, descriptions = [], set(), set(), {}, {}
    forbidden = {'https://meli.la/1KHbTXG', 'https://meli.la/1fzxaCM', 'https://meli.la/2q7fy7p', 'https://meli.la/2BE54o4'}
    for path in site.INDEXABLE_PATHS:
        response = client.get(path)
        html = response.get_data(as_text=True)
        page = inspect(path, html, response.status_code, dict(response.headers))
        doc = Doc(html)
        assert not page['issues'], (path, page['issues'])
        assert client.head(path).status_code == 200, path
        assert len(doc.ids) == len(set(doc.ids)), ('IDs', path)
        assert doc.meta['og:url'] == site.absolute_url(path), path
        assert doc.meta['og:title'] and doc.meta['og:description'], path
        assert doc.meta['twitter:card'] == 'summary_large_image', path
        assert 'contenido-principal' in doc.ids, path
        for value, seen in [(doc.titles[0], titles), (doc.meta['description'], descriptions)]:
            assert value not in seen, ('Metadatos repetidos', path, seen.get(value))
            seen[value] = path
        breadcrumbs = [s for s in doc.schemas if s.get('@type') == 'BreadcrumbList']
        assert len(breadcrumbs) == int(path != '/'), path
        if breadcrumbs:
            items = breadcrumbs[0]['itemListElement']
            assert items[-1]['item'] == site.absolute_url(path), path
            assert [item['position'] for item in items] == list(range(1, len(items) + 1)), path
        for image in doc.images:
            assert image.get('alt') is not None and image.get('width') and image.get('height'), (path, image)
            (external_images if image['src'].startswith(('https://', 'http://')) else assets).add(image['src'])
        assets.add(urlsplit(doc.meta['og:image']).path)
        for link in doc.links:
            href = link.get('href', '')
            assert href not in forbidden, ('Destino incorrecto', path, href)
            parsed = urlsplit(urljoin(site.SITE_URL + path, href))
            if parsed.netloc == urlsplit(site.SITE_URL).netloc:
                if parsed.path.startswith('/assets/'):
                    assets.add(parsed.path)
                else:
                    assert parsed.path in site.INDEXABLE_PATH_SET, (path, href)
                    if parsed.fragment:
                        destination = doc if parsed.path == path else Doc(client.get(parsed.path).get_data(as_text=True))
                        assert parsed.fragment in destination.ids, ('Ancla', path, href)
            if parsed.netloc == 'meli.la':
                assert {'sponsored', 'noopener'} <= set(link.get('rel', '').split()), (path, href)
                assert href in site.AFFILIATE_URLS, (path, href)
        pages.append(dict(path=path, status=200, title=doc.titles[0], description=doc.meta['description'], schemas=[s.get('@type') for s in doc.schemas]))
    for asset in assets | {'/favicon.svg', '/assets/site.css', '/assets/home.js', '/assets/commerce.js', '/assets/decision-tools.js'}:
        assert client.get(asset).status_code == 200, asset
    for font in (site.ASSETS_DIR / 'fonts').glob('*.woff2'):
        response = client.get('/assets/fonts/' + font.name)
        assert response.status_code == 200 and response.data[:4] == b'wOF2', font.name
        assert 'immutable' in response.headers['Cache-Control'], font.name
    assert client.get('/assets/fonts/fonts.css').status_code == 200
    sitemap = ET.fromstring(client.get('/sitemap.xml').data)
    assert {node.text for node in sitemap.findall('{*}url/{*}loc')} == {site.absolute_url(path) for path in site.INDEXABLE_PATHS}
    assert client.get('/no-existe-qa/').status_code == 404
    assert client.get('/search-cards.html').headers['X-Robots-Tag'] == 'noindex'
    assert client.post('/api/affiliate-click', data='malformed').status_code == 400
    result = dict(routes=len(pages), articles=len(site.ALL_ARTICLES), assets=len(assets), external_images=sorted(external_images), pages=pages)
    Path('produccion-rutas-verificadas-2026-09-30.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"OK: {len(pages)} rutas, {len(site.ALL_ARTICLES)} guías, {len(assets)} imágenes/recursos; canonical, metadatos únicos, JSON-LD, migas, anclas, afiliación, sitemap, 404 y eventos inválidos.")

if __name__ == '__main__':
    main()
