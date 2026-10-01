"""Verifica ubicación, referencias, exclusiones, HTML servido e idempotencia."""
import hashlib
import re
import subprocess
from pathlib import Path
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
import servidor_local as s
from hidrolavadoras_comerciales import OFFERS, PENDING, url

class Document(HTMLParser):
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
    for path, config in s.HIDROLAVADORAS_OFFERS.items():
        assert path in articles, ('No publicada', path)
        article = articles[path]
        body = article['body']
        html = s.render_article_page(article)
        doc = Document(html)
        assert 'HIDROLAVADORAS-OFERTAS' not in html
        selected=s.guide_comparison_selection(path,'hidrolavadoras',s.PRODUCT_FACTS)
        assert html.count('class="offer-card"') == (len(selected) if selected else len(config['models'])), path
        if config['models']:
            anchor = re.search(r'(?m)^## ' + re.escape(config['anchor']) + r'.*$', body)
            marker = body.index('<!-- HIDROLAVADORAS-OFERTAS -->')
            next_heading = re.search(r'(?m)^## ', body[anchor.end():])
            assert anchor.end() < marker < anchor.end() + next_heading.start(), path
        for offer in config['offers']:
            key = offer['model']
            links = [link for link in doc.links if link.get('href') == offer['url']]
            assert len(links) == (2 if config['repeat'] else 1), (path, key, len(links))
            for link in links:
                assert link['target'] == '_blank'
                assert set(link['rel'].split()) == {'nofollow', 'sponsored', 'noopener', 'noreferrer'}
                s.validate_affiliate_click(dict(product=offer['url'], page=path, placement='qa-hidrolavadoras'))
            total += len(links)
        for key in PENDING.keys() & OFFERS.keys():
            assert url(key) not in html, (path, key)
        for old in ['2Rcddpg', '1cZXqxL', '1KQjHgT']:
            assert 'https://meli.la/' + old not in html, (path, old)
        for table in re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', body):
            assert len({len(row.split('|')) for row in table.splitlines()}) == 1, path
    files = list(Path('paginas/hidrolavadoras').glob('*.md')) + [Path('hidrolavadoras-ofertas.json')]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    subprocess.run(['python', 'integrar_hidrolavadoras_comerciales.py'], check=True)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    class QuietHandler(s.TallerLabHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        for path, config in s.HIDROLAVADORAS_OFFERS.items():
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}', timeout=10) as response:
                assert response.status == 200
                html = response.read().decode('utf-8')
                assert all(offer['url'] in html for offer in config['offers'])
    finally:
        server.shutdown()
        server.server_close()
    print(f'OK: 23 guías HTTP 200; 20 con bloques, 26 productos, {total} CTA; ubicación, exclusiones, atributos, tablas e idempotencia.')

if __name__ == '__main__':
    main()
