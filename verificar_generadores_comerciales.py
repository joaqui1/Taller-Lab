"""Verifica las ubicaciones, identidad de las filas y atributos en HTML real."""
import hashlib
import subprocess
import re
from pathlib import Path
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
from generadores_comerciales import OFFERS, PENDING, url
import servidor_local as s

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
    for path, config in s.GENERADORES_OFFERS.items():
        if not config['models']:
            continue
        assert path in articles, ('No publicada', path)
        article = articles[path]
        text = article['body']
        original = subprocess.check_output(['git', 'show', 'HEAD:paginas/generadores/' + config['file']]).decode('utf-8')
        editorial = re.sub(r'<!-- GENERADORES-EXTRAS -->.*?<!-- /GENERADORES-EXTRAS -->', '', original, flags=re.S)
        for heading in re.findall(r'(?m)^#{1,3} .+$', editorial):
            if heading=='## El LG3000: dato a verificar':
                heading='## LG3000 y LG3000E: cotejá el código y la potencia'
            assert heading in text, (path, heading)
        html = s.render_article_page(article)
        doc = Document(html)
        for offer in config['offers']:
            links = [a for a in doc.links if a.get('href') == offer['url']]
            assert len(links) == 1, (path, offer['model'], len(links))
            assert links[0].get('target') == '_blank'
            assert set(links[0]['rel'].split()) == {'nofollow', 'sponsored', 'noopener', 'noreferrer'}
            s.validate_affiliate_click(dict(product=offer['url'], page=path, placement='qa-generadores'))
            total += 1
        for key in PENDING:
            assert url(key) not in html
        for key in {'LGIS3.8-8', 'GNW-55-E', 'DELTA 2 Max', 'AC70P'}:
            assert not any(url(key) in row for row in text.splitlines() if row.startswith('|'))
        for row in text.splitlines():
            if row.startswith('|') and any(offer['url'] in row for offer in config['offers']):
                assert '[Ver precio →]' in row
        for table in re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', text):
            widths = {len(row.split('|')) for row in table.splitlines()}
            assert len(widths) == 1, (path, widths)
    paths = list(Path('paginas/generadores').glob('*.md')) + [Path('generadores-ofertas.json')]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    subprocess.run(['python', 'integrar_generadores_comerciales.py'], check=True)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'Integración no idempotente'
    assert len({url(k) for k in OFFERS if k not in PENDING}) == 26
    class QuietHandler(s.TallerLabHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        for path, config in s.GENERADORES_OFFERS.items():
            if not config['models']:
                continue
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}', timeout=10) as response:
                assert response.status == 200, path
                html = response.read().decode('utf-8')
                assert all(offer['url'] in html for offer in config['offers']), path
    finally:
        server.shutdown()
        server.server_close()
    print(f'OK: {total} CTA en 20 guías HTTP 200; {len(OFFERS)-len(PENDING)} productos, atributos, tablas e idempotencia verificados.')

if __name__ == '__main__':
    main()
