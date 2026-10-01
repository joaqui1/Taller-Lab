"""Contrasta cada URL pública y sus assets con el estado local aprobado."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
os.environ['SITE_URL'] = 'https://www.tallerlab.com.ar'
from app import app
import servidor_local as site
from auditoria_seo_consultor import Doc, inspect


def fetch(path):
    with urlopen(Request(site.SITE_URL + path, headers={'User-Agent': 'TallerLab-publication-QA/1.0'}), timeout=40) as response:
        return path, response.status, response.read(), dict(response.headers)


def main():
    client = app.test_client()
    pages, assets, failures = [], set(), []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch, site.INDEXABLE_PATHS))
    for path, status, body, headers in results:
        html = body.decode('utf-8')
        page = inspect(path, html, status, headers)
        local = client.get(path).data
        identical = hashlib.sha256(body).digest() == hashlib.sha256(local).digest()
        issues = list(page['issues'])
        if not identical:
            issues.append('HTML público distinto del aprobado localmente')
        doc = Doc(html)
        if doc.meta.get('og:image'):
            assets.add(urlsplit(doc.meta['og:image']).path)
        if not doc.meta.get('og:title') or doc.meta.get('twitter:card') != 'summary_large_image':
            issues.append('Metadatos sociales incompletos')
        for img in doc.images:
            if img['src'].startswith('/assets/'):
                assets.add(img['src'])
        if issues:
            failures.append(dict(path=path, issues=issues))
        pages.append(dict(path=path, status=status, identical=identical, issues=issues, title=doc.titles))
    assets.update('/assets/' + p.relative_to(site.ASSETS_DIR).as_posix() for p in (site.ASSETS_DIR / 'fonts').glob('*'))
    from fotos_productos import PHOTOS
    assets.update(photo['image'] for photo in PHOTOS.values())
    assets.update(['/assets/site.css?v=11', '/assets/home.js', '/assets/commerce.js', '/assets/decision-tools.js'])
    asset_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        public_assets = list(pool.map(fetch, sorted(assets)))
    for path, status, body, headers in public_assets:
        source = site.ASSETS_DIR / path.split('?', 1)[0].removeprefix('/assets/')
        expected = source.read_bytes()
        # Git normaliza los archivos de texto a LF en el checkout de Linux.
        # No se normalizan fuentes, imágenes ni otros binarios.
        if source.suffix in ('.css', '.js', '.txt'):
            identical = body.replace(b'\r\n', b'\n') == expected.replace(b'\r\n', b'\n')
        else:
            identical = body == expected
        if not identical:
            failures.append(dict(path=path, issues=['Asset público distinto']))
        asset_results.append(dict(path=path, status=status, identical=identical, cache=headers.get('Cache-Control'), vercel_cache=headers.get('X-Vercel-Cache')))
    _, _, body, _ = fetch('/sitemap.xml')
    sitemap = {n.text for n in ET.fromstring(body).findall('{*}url/{*}loc')}
    assert sitemap == {site.absolute_url(p) for p in site.INDEXABLE_PATHS}, 'Sitemap público distinto'
    report = dict(routes=len(pages), sitemap=len(sitemap), failures=failures, pages=pages, assets=asset_results)
    Path('despliegue-verificado-2026-10-01.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not failures, failures
    print(f'OK: {len(pages)} rutas y {len(asset_results)} assets públicos coinciden con el estado aprobado; sitemap completo. Sólo se normaliza CRLF/LF en archivos de texto.')


if __name__ == '__main__':
    main()
