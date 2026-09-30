"""Audita todas las guías actuales y la separación entre hub y comparativa."""
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import servidor_local as site
from app import app
from validacion_enlaces import EnlacesHTML, validar_html

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / 'paginas' / 'hidrolavadoras'


def schemas(html):
    return [json.loads(raw) for raw in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)]


def main():
    files = sorted(PAGES_DIR.glob('*.md'))
    articles = {a['filename']: a for a in site.ALL_ARTICLES if a['section'] == 'hidrolavadoras'}
    client = app.test_client()
    errors, urls = [], set()
    verified = 0
    sitemap = {node.text for node in ET.fromstring(site.render_sitemap()).findall(
        './/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    for path in files:
        try:
            content = path.read_text(encoding='utf-8')
            assert re.match(r'^---\n.*?\n---\n', content, re.DOTALL), 'Frontmatter mal formado'
            fm, body = site.extract_frontmatter(content)
            for key in ('title', 'h1', 'url', 'description', 'author', 'category', 'keywords'):
                assert fm.get(key), f'Falta {key}'
            assert re.findall(r'^# (.+)$', body, re.MULTILINE) == [fm['h1']], 'H1 del cuerpo y metadatos inconsistentes'
            url = fm['url']
            assert url.startswith('/hidrolavadoras/') and url.endswith('/'), 'URL fuera de categoría o sin barra final'
            assert url not in urls, 'URL duplicada'
            urls.add(url)
            assert len(body.split()) >= 400, 'Contenido menor a 400 palabras'
            assert path.name in articles, 'Guía excluida por el filtro editorial'
            response = client.get(url)
            assert response.status_code == 200, f'HTTP {response.status_code}'
            html = response.get_data(as_text=True)
            assert len(re.findall(r'<h1\b', html)) == 1, 'El HTML debe tener un H1'
            canonical = site.absolute_url(url)
            assert f'<link rel="canonical" href="{canonical}">' in html, 'Canonical incorrecto'
            assert canonical in sitemap, 'URL ausente del sitemap'
            article_schemas = [s for s in schemas(html) if s.get('@type') == 'Article']
            assert len(article_schemas) == 1, 'Debe haber un Article'
            assert article_schemas[0]['mainEntityOfPage'] == canonical, 'Article apunta a otra página'
            assert article_schemas[0]['headline'] == fm['h1'], 'Headline inconsistente'
            validar_html(html, url, site.INDEXABLE_PATH_SET, site.SITE_URL)
            for attrs in re.findall(r'<a\b([^>]+)>', html):
                if re.search(r'href="https://(?:meli\.la|www\.mercadolibre\.com/sec)/', attrs):
                    rel = re.search(r'rel="([^"]*)"', attrs)
                    assert rel and 'sponsored' in rel[1].split(), 'Enlace afiliado sin sponsored'
            verified += 1
        except (AssertionError, ValueError, KeyError) as error:
            errors.append(f'{path.name}: {error}')
    try:
        response = client.get('/hidrolavadoras/')
        assert response.status_code == 200, 'Hub sin HTTP 200'
        html = response.get_data(as_text=True)
        assert '<h1>Hidrolavadoras</h1>' in html, 'H1 del hub incorrecto'
        assert '<title>Hidrolavadoras: guías, marcas y comparativas</title>' in html, 'Title del hub incorrecto'
        assert not any(s.get('@type') == 'Article' for s in schemas(html)), 'El hub carga Article'
        assert 'class="hub-documental"' not in html, 'Guía incrustada en el hub'
        assert 'Comparar hidrolavadoras' in html, 'Falta enlace destacado'
        assert f'<link rel="canonical" href="{site.absolute_url("/hidrolavadoras/")}">' in html, 'Canonical del hub incorrecto'
        assert urls.issubset(EnlacesHTML(html).enlaces), 'El hub no enlaza todas las guías'
        main_article = articles['01-hidrolavadoras.md']
        assert main_article['body'] not in html, 'Comparativa incrustada'
        assert 'class="article-body"' not in html, 'Cuerpo de artículo incrustado'
    except (AssertionError, ValueError, KeyError) as error:
        errors.append(f'Hub: {error}')
    print(f'Guías detectadas: {len(files)}; verificadas sin errores: {verified}; hub auditado: 1')
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print(f'OK: {verified} guías y hub; publicación, enlaces, canonical, sitemap y Article.')


if __name__ == '__main__':
    main()
