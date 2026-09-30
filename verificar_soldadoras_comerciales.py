"""Comprueba integridad editorial, ubicación, enlaces únicos y publicación HTTP."""
import hashlib
import re
import subprocess
import sys
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
import servidor_local as s
from integrar_soldadoras_comerciales import ANALYSIS, MARKER, insertion, normalize_main_links
from soldadoras_comerciales import OFFERS, PENDING, url


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs))


def main():
    articles = {a['url']: a for a in s.ALL_ARTICLES}
    total = 0
    for path, config in s.SOLDADORAS_OFFERS.items():
        file = Path('paginas/soldadoras') / config['file']
        text = file.read_text(encoding='utf-8')
        original = subprocess.check_output(['git', 'show', 'HEAD:paginas/soldadoras/' + config['file']]).decode('utf-8')
        if path == '/soldadoras/':
            original = normalize_main_links(original)
        # Solo bloques de ofertas y espacio separador pueden cambiar.
        assert re.sub(r'\s+', ' ', MARKER.sub('\n\n', text).replace(ANALYSIS, '')).strip() == re.sub(r'\s+', ' ', original).strip(), ('Contenido alterado', path)
        blocks = list(re.finditer(r'<!-- SOLDADORAS-OFERTAS -->.*?<!-- /SOLDADORAS-OFERTAS -->', text, re.S))
        assert len(blocks) == len(config['placements']), path
        for placement in config['placements']:
            matching = [b for b in blocks if all(url(key) in b[0] for key in placement['models'])]
            assert len(matching) == 1, path
            block = matching[0]
            without = text[:block.start()].rstrip() + '\n\n' + text[block.end():].lstrip('\n')
            position = insertion(without, placement['anchor'], placement['position'])
            assert without[:position].rstrip() == text[:block.start()].rstrip(), ('Ubicación', path, placement['anchor'])
        if not config['offers'] and path not in articles:
            continue
        assert path in articles, ('Ruta sin publicar', path)
        html = s.render_category_page('soldadoras') if path == '/soldadoras/' else s.render_article_page(articles[path])
        assert html.count('<h1>') == 1, ('H1', path)
        ids = re.findall(r'\bid="([^"]+)"', html)
        assert len(ids) == len(set(ids)), ('IDs duplicados', path)
        links = Links(html).links
        actual = [link for link in links if link.get('href', '').startswith('https://meli.la/')]
        assert {link['href'] for link in actual} == {offer['url'] for offer in config['offers']}, ('Ofertas inesperadas', path)
        assert len(actual) == len(config['offers']), ('CTA duplicados', path)
        for link in actual:
            assert link['target'] == '_blank' and set(link['rel'].split()) == {'nofollow', 'sponsored', 'noopener', 'noreferrer'}, path
            assert link['data-affiliate-placement'] == 'soldadoras-contextual', path
            s.validate_affiliate_click(dict(product=link['href'], page=path, placement='soldadoras-contextual'))
        total += len(actual)
    assert len(OFFERS) == len({url(key) for key in OFFERS}) == 28
    assert set(OFFERS) == {key for config in s.SOLDADORAS_OFFERS.values() for key in config['models']}
    assert set(PENDING) == {offer['model'] for config in s.SOLDADORAS_OFFERS.values() for offer in config['pending']}
    paths = list(Path('paginas/soldadoras').glob('*.md')) + [Path('soldadoras-ofertas.json')]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    subprocess.run([sys.executable, 'integrar_soldadoras_comerciales.py'], check=True)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'Integración no idempotente'

    class QuietHandler(s.TallerLabHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        for path, config in s.SOLDADORAS_OFFERS.items():
            if path not in articles:
                continue
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}', timeout=10) as response:
                assert response.status == 200, path
                actual = [a for a in Links(response.read().decode('utf-8')).links if a.get('href', '').startswith('https://meli.la/')]
                assert len(actual) == len(config['offers']), path
    finally:
        server.shutdown()
        server.server_close()
    print(f'OK: 28 productos, {total} CTA en 26 guías; {sum(path in articles for path in s.SOLDADORAS_OFFERS)} rutas HTTP 200, fichas originales, ubicaciones, atributos, clics e idempotencia.')


if __name__ == '__main__':
    main()
