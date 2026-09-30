"""Control de publicación: enlaces fuente y HTML, HTTP, canonical y regresiones."""
import copy
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import servidor_local as s
from validacion_enlaces import EnlacesHTML, validar_html


def check_rejected(html, path="/soldadoras/tig/"):
    try:
        validar_html(html, path, s.INDEXABLE_PATH_SET, s.SITE_URL)
    except ValueError:
        return
    raise AssertionError("El validador aceptó un enlace inválido: " + html)


def main():
    s.validate_published_links()
    for html in (
        '<a href="/tig/">TIG</a>',
        '<a href="../no-existe/">Relativo</a>',
        f'<a href="{s.SITE_URL}/no-existe/">Absoluto interno</a>',
        '<a href="/no-existe/?a=1#detalle">Query y fragmento</a>',
        s.MARKDOWN.render('[TIG][ref]\n\n[ref]: /tig/'),
    ):
        check_rejected(html)
    validar_html('<a href="/soldadoras/tig/?a=1#detalle">TIG</a>'
                 '<a href="#detalle">Sección</a><a href="https://externo.example/tig/">Fuente</a>',
                 '/soldadoras/tig/', s.INDEXABLE_PATH_SET, s.SITE_URL)

    article = copy.deepcopy(next(a for a in s.ALL_ARTICLES if a['url'] == '/soldadoras/tig/'))
    article['body'] += '\n[TIG](/tig/)'
    try:
        s.render_article_page(article)
    except ValueError:
        pass
    else:
        raise AssertionError('El renderer debe rechazar el enlace, sin quitarlo silenciosamente')
    original = s.ALL_ARTICLES
    try:
        s.ALL_ARTICLES = original + [article]
        try:
            s.validate_published_links()
        except ValueError:
            pass
        else:
            raise AssertionError('La validación de inicio no bloqueó el artículo inválido')
    finally:
        s.ALL_ARTICLES = original

    from app import app
    client = app.test_client()
    link_count = 0
    for path in s.INDEXABLE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)
        html = response.get_data(as_text=True)
        validar_html(html, path, s.INDEXABLE_PATH_SET, s.SITE_URL)
        assert f'<link rel="canonical" href="{s.SITE_URL}{path}">' in html, path
        link_count += len(EnlacesHTML(html).enlaces)
    articles = {a['url']: a for a in s.ALL_ARTICLES}
    for a in s.ALL_ARTICLES:
        if a['section'] != 'soldadoras':
            continue
        source = EnlacesHTML(s.MARKDOWN.render(a['body'])).enlaces
        html = s.render_article_page(a)  # Incluye el cuerpo del hub como artículo embebido.
        rendered = EnlacesHTML(html).enlaces
        for href in source:
            if href.startswith('/soldadoras/'):
                assert href in rendered, (a['url'], href)
    assert '/soldadoras/tig/' in articles
    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    locations = ET.fromstring(sitemap.data).findall('{*}url/{*}loc')
    assert {x.text for x in locations} == {s.SITE_URL + p for p in s.INDEXABLE_PATHS}
    assert s.SITE_URL + '/sitemap.xml' in client.get('/robots.txt').get_data(as_text=True)

    config = json.loads(Path('vercel.json').read_text(encoding='utf-8'))
    canonical = config['env']['SITE_URL']
    assert canonical == 'https://www.tallerlab.com.ar'
    env = dict(os.environ, VERCEL_ENV='production', VERCEL_PROJECT_PRODUCTION_URL='otro.vercel.app')
    env.pop('SITE_URL', None)
    failed = subprocess.run([sys.executable, '-c', 'import servidor_local'], env=env, capture_output=True, text=True)
    assert failed.returncode != 0 and 'requiere SITE_URL' in failed.stderr
    for invalid in ('http://www.tallerlab.com.ar', 'https://otro.vercel.app', 'https://www.tallerlab.com.ar/subcarpeta/'):
        env['SITE_URL'] = invalid
        failed = subprocess.run([sys.executable, '-c', 'import servidor_local'], env=env, capture_output=True, text=True)
        assert failed.returncode != 0, invalid
    env['SITE_URL'] = canonical + '/'
    code = ('import servidor_local as s; '
            'assert s.SITE_URL == "https://www.tallerlab.com.ar"; '
            'assert s.SITE_URL in s.render_sitemap(); '
            'assert s.organization_schema()["url"] == s.SITE_URL + "/"; '
            'assert s.SITE_URL in s.canonical_tag("/soldadoras/tig/")')
    subprocess.run([sys.executable, '-c', code], env=env, check=True)
    print(f'OK: {len(s.ALL_ARTICLES)} guías, {len(s.INDEXABLE_PATHS)} rutas HTTP 200, {link_count} enlaces HTML; '
          'fuentes, renderer, canonical, sitemap, robots, dominio de producción y rechazo de regresiones.')


if __name__ == '__main__':
    main()
