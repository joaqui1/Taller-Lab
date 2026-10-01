"""Valida rutas, integridad documental, ubicación, CTA, clics e idempotencia."""
import hashlib
import io
from contextlib import redirect_stdout
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
if (Path(__file__).parent / '.taladros-qa-deps').exists():
    sys.path.insert(0, str(Path(__file__).parent / '.taladros-qa-deps'))
import servidor_local as s
from app import app
from integrar_taladros_comerciales import ANALYSIS, DOCUMENTED, MARKER, insertion
from taladros_comerciales import OFFERS
from normalizar_citas_qa import normalized_citations


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links, self.ids, self.h1, self.ctas = [], [], 0, []
        self.current_cta = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.links.append(attrs)
            if attrs.get('data-affiliate-placement') == 'taladros-contextual':
                self.current_cta = [attrs, '']
                self.ctas.append(self.current_cta)
        if tag == 'h1':
            self.h1 += 1
        if 'id' in attrs:
            self.ids.append(attrs['id'])

    def handle_data(self, data):
        if self.current_cta is not None:
            self.current_cta[1] += data

    def handle_endtag(self, tag):
        if tag == 'a':
            self.current_cta = None


def main():
    client = app.test_client()
    articles = {a['url']: a for a in s.ALL_ARTICLES if a['section'] == 'taladros'}
    assert len(articles) == 23
    assert len(OFFERS) == len({o[1] for o in OFFERS.values()}) == 32
    assert len(s.TALADROS_OFFERS) == 17
    expected_urls = {o[1] for o in OFFERS.values()}
    seen, count = set(), 0
    for path, article in articles.items():
        file = article['path']
        text = file.read_text(encoding='utf-8')
        original = subprocess.check_output(['git', 'show', 'HEAD:paginas/taladros/' + file.name]).decode('utf-8')
        original = MARKER.sub('\n\n', original).replace(DOCUMENTED, '').replace(ANALYSIS, '')
        original = original.replace('### Percutor vs SDS DeWalt', '## Percutor vs SDS DeWalt')
        original = normalized_citations(original)
        clean = MARKER.sub('\n\n', text).replace(DOCUMENTED, '').replace(ANALYSIS, '')
        assert re.sub(r'\s+', ' ', clean).strip() == re.sub(r'\s+', ' ', original).strip(), ('Documento alterado', path)
        response = client.get(path)
        assert response.status_code == client.head(path).status_code == 200, path
        redirect = client.get(path[:-1] + '?origen=qa')
        assert redirect.status_code == 301 and redirect.headers['Location'] == path + '?origen=qa', path
        html = response.get_data(as_text=True)
        page = Page(html)
        assert page.h1 == 1 and len(page.ids) == len(set(page.ids)), path
        for link in page.links:
            href = link.get('href', '')
            if href.startswith('/taladros/'):
                assert href.split('#')[0] in s.INDEXABLE_PATH_SET, (path, href)
        config = s.TALADROS_OFFERS.get(path)
        if not config:
            assert not page.ctas, path
            continue
        block = re.search(r'<!-- TALADROS-OFERTAS -->.*?<!-- /TALADROS-OFERTAS -->', text, re.S)
        assert block and text.count('<!-- TALADROS-OFERTAS -->') == 1, path
        without = text[:block.start()].rstrip() + '\n\n' + text[block.end():].lstrip('\n')
        position = insertion(without, config['anchor'], config['position'])
        assert without[:position].rstrip() == text[:block.start()].rstrip(), ('Ubicación', path)
        assert len(page.ctas) == len(config['offers']), path
        actual = {link['href']: label.strip() for link, label in page.ctas}
        assert actual == {o['url']: o['cta'] + ' ↗' for o in config['offers']}, ('CTA o destino', path)
        for link, _ in page.ctas:
            assert link['target'] == '_blank'
            assert set(link['rel'].split()) == {'nofollow', 'sponsored', 'noopener', 'noreferrer'}
            event = dict(product=link['href'], page=path, placement='taladros-contextual')
            s.validate_affiliate_click(event)
            with redirect_stdout(io.StringIO()):
                assert client.post('/api/affiliate-click', json=event).status_code == 204
            assert sum(a.get('href') == link['href'] for a in page.links) == 1, ('Duplicado', path)
        # Conservar los referidos anteriores presentes en el cuerpo, como Omaha.
        legacy = set(re.findall(r'https://meli\.la/[A-Za-z0-9]+', original))
        actual_short = {a['href'] for a in page.links if a.get('href', '').startswith('https://meli.la/')}
        assert actual_short == legacy | {u for u in actual if u.startswith('https://meli.la/')}, path
        seen.update(actual)
        count += len(actual)
    assert seen == expected_urls and count == 32
    assert client.post('/api/affiliate-click', json=dict(product='https://example.org/', page='/taladros/', placement='taladros-contextual')).status_code == 400
    hub = Page(client.get('/taladros/').get_data(as_text=True))
    assert set(articles) <= {a.get('href') for a in hub.links}
    assert all(s.absolute_url(path) in s.render_sitemap() for path in articles)
    files = list(Path('paginas/taladros').glob('*.md')) + [Path('taladros-ofertas.json')]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    subprocess.run([sys.executable, 'integrar_taladros_comerciales.py'], check=True)
    assert before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, 'No idempotente'
    print('OK: 32 productos/CTA en 17 guías; 23 rutas HTTP 200, integridad documental, ubicaciones, clics, sitemap e idempotencia.')


if __name__ == '__main__':
    main()
