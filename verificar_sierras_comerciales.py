"""Comprueba referidos, publicación, ubicación editorial y repetibilidad."""
import hashlib
import re
import subprocess
from pathlib import Path
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
from sierras_comerciales import OFFERS, PENDING, url
import servidor_local as s

class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.active_link = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.active_link = dict(attrs, text='')
            self.links.append(self.active_link)

    def handle_data(self, data):
        if self.active_link is not None:
            self.active_link['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a':
            self.active_link = None

def main():
    articles = {article['url']: article for article in s.ALL_ARTICLES}
    total = 0
    routes = []
    for path, config in s.SIERRAS_OFFERS.items():
        file = Path('paginas/sierras') / config['file']
        text = file.read_text(encoding='utf-8')
        original = subprocess.check_output(['git', 'show', 'HEAD:paginas/sierras/' + config['file']]).decode('utf-8')
        assert all(heading in text for heading in re.findall(r'(?m)^#{1,3} .+$', original)), path
        # Los enlaces comerciales pueden cambiar; las tablas documentales se conservan.
        marker = r'<!-- SIERRAS-OFERTAS -->.*?<!-- /SIERRAS-OFERTAS -->'
        original_tables = re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', re.sub(marker, '', original, flags=re.S))
        current_tables = re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', re.sub(marker, '', text, flags=re.S))
        assert original_tables == current_tables, ('Tabla documental modificada', path)
        if not config['offers']:
            assert '<!-- SIERRAS-OFERTAS -->' not in text, path
            continue
        assert path in articles, ('No publicada', path)
        block = re.search(r'<!-- SIERRAS-OFERTAS -->.*?<!-- /SIERRAS-OFERTAS -->', text, re.S)
        assert block and text.count('<!-- SIERRAS-OFERTAS -->') == 1, path
        prefix = text[:block.start()].rstrip()
        assert config['anchor'] in prefix, path
        if config['position'] == 'table':
            assert prefix.endswith('|'), ('No sigue a tabla', path)
        elif config['position'] == 'heading':
            assert prefix.endswith(config['anchor']), path
        else:
            anchor = re.search(r'(?m)^(#{2,3}) ' + re.escape(config['anchor']) + r'$', prefix)
            level = len(anchor[1])
            assert not re.search(r'(?m)^#{1,' + str(level) + r'} ', prefix[anchor.end():]), path
        for table in re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', text):
            assert len({len(row.split('|')) for row in table.splitlines()}) == 1, path
        html = s.render_article_page(articles[path])
        doc = Links(html)
        for offer in config['offers']:
            matches = [link for link in doc.links if link.get('href') == offer['url']]
            assert len(matches) == 1, (path, offer['model'], len(matches))
            assert matches[0]['text'].strip() == offer['cta'], (path, offer['model'], 'Texto CTA')
            assert matches[0].get('target') == '_blank', path
            assert set(matches[0]['rel'].split()) == {'nofollow', 'sponsored', 'noopener', 'noreferrer'}, path
            s.validate_affiliate_click(dict(product=offer['url'], page=path, placement='qa-sierras'))
            total += 1
        assert not any(url(key) in html for key in PENDING), path
        assert not any(old in html for old in ['https://meli.la/1ntghna', 'https://meli.la/2WFpTNp', 'https://meli.la/1mLrBwo']), path
        routes.append(path)
    paths = list(Path('paginas/sierras').glob('*.md')) + [Path('sierras-ofertas.json')]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    subprocess.run(['python', 'integrar_sierras_comerciales.py'], check=True)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'No idempotente'
    class QuietHandler(s.TallerLabHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        for path in routes:
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}', timeout=10) as response:
                assert response.status == 200, path
                html = response.read().decode('utf-8')
                assert all(offer['url'] in html for offer in s.SIERRAS_OFFERS[path]['offers']), path
    finally:
        server.shutdown()
        server.server_close()
    print(f'OK: {total} CTA, {len(OFFERS)-len(PENDING)} productos y {len(routes)} rutas HTTP 200; ubicaciones, atributos, registro de clics e idempotencia.')

if __name__ == '__main__':
    main()
