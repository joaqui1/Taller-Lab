"""Comprueba referidos, publicación, ubicación editorial y repetibilidad."""
import hashlib
import re
import argparse
import subprocess
from pathlib import Path
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
from sierras_comerciales import OFFERS, PENDING, UNMONETIZED, url
import servidor_local as s
from integrar_sierras_comerciales import DOCUMENTED_ROWS

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

def main(pages=None):
    articles = {article['url']: article for article in s.ALL_ARTICLES}
    total = 0
    routes = []
    assert not any(pending['model'] in UNMONETIZED for config in s.SIERRAS_OFFERS.values() for pending in config['pending']), 'Modelo sin afiliado volvió a pendientes'
    for path, config in s.SIERRAS_OFFERS.items():
        if pages and int(config['file'][:2]) not in pages:
            continue
        file = Path('paginas/sierras') / config['file']
        text = file.read_text(encoding='utf-8')
        original = subprocess.check_output(['git', 'show', 'HEAD:paginas/sierras/' + config['file']]).decode('utf-8')
        headings = re.findall(r'(?m)^#{1,3} .+$', original)
        headings = [h for h in headings if h != '### Consultá estas opciones en Mercado Libre']
        if config['file'] == '25-caladoras-black-decker.md' and 'BES602' in re.sub(r'https://[^)\s]+', '', original):
            headings = [heading.replace('Sierra caladora Black+Decker: cómo elegir entre modelos', 'Sierra caladora Black+Decker BES603: capacidad y usos').replace('BES603 y BES602: velocidad variable y variante', 'BES603: capacidad, velocidad y variante').replace('BES602 o BES603: cuándo aporta la velocidad variable', 'BES603: cuándo aporta la velocidad variable') for heading in headings]
        assert all(heading in text for heading in headings), path
        # Los enlaces comerciales pueden cambiar; las tablas documentales se conservan.
        marker = r'<!-- SIERRAS-OFERTAS -->.*?<!-- /SIERRAS-OFERTAS -->'
        original_tables = re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', re.sub(marker, '', original, flags=re.S))
        current_tables = re.findall(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', re.sub(marker, '', text, flags=re.S))
        if config['file'] == '25-caladoras-black-decker.md' and any('BES602' in table for table in original_tables):
            # La sustitución solicitada conserva todos los datos de la columna BES603.
            original_tables = ['\n'.join('| ' + ' | '.join(cell.strip() for cell in row.split('|')[1:3]) + ' |' for row in table.splitlines()) + '\n' for table in original_tables]
            assert 'BES602' not in re.sub(r'https://[^)\s]+', '', text), path
        assert original_tables == current_tables, ('Tabla documental modificada', path)
        if not config['offers']:
            assert '<!-- SIERRAS-OFERTAS -->' not in text, path
            continue
        assert path in articles, ('No publicada', path)
        if config['position'] == 'inline':
            assert '<!-- SIERRAS-OFERTAS -->' not in text, path
            for offer in config['offers']:
                section = text.split('### ' + offer['section'], 1)[1].split('\n### ', 1)[0]
                assert offer['url'] in section, (path, offer['model'], 'CTA fuera del H3')
            for saw, kit in zip(config['offers'][::2], config['offers'][1::2]):
                assert text.index(saw['url']) < text.index(kit['url']), (path, 'Kit antes de la sierra')
            assert 'enlace de compra pendiente' not in text, path
        else:
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
        number = int(config['file'][:2])
        if number in DOCUMENTED_ROWS:
            documented_url = re.search(r'\]\((https://[^)]+)\)', DOCUMENTED_ROWS[number])[1]
            documented = [link for link in doc.links if link.get('href') == documented_url]
            assert documented and all('sponsored' not in link.get('rel', '').split() for link in documented), (path, 'Enlace documental tratado como afiliado')
            assert DOCUMENTED_ROWS[number] in text, (path, 'Alternativa documental ausente')
        if config['position'] != 'inline':
            block = re.search(r'<!-- SIERRAS-OFERTAS -->(.*?)<!-- /SIERRAS-OFERTAS -->', text, re.S)[1]
            assert ('Compará los modelos' in block) == (len(config['offers']) + (number in DOCUMENTED_ROWS) >= 2), (path, 'Comparación plural sin alternativas')
        for offer in config['offers']:
            matches = [link for link in doc.links if link.get('href') == offer['url']]
            assert len(matches) == 1, (path, offer['model'], len(matches))
            assert matches[0]['text'].strip() == offer['cta'], (path, offer['model'], 'Texto CTA')
            assert matches[0].get('target') == '_blank', path
            assert set(matches[0]['rel'].split()) == {'nofollow', 'sponsored', 'noopener', 'noreferrer'}, path
            s.validate_affiliate_click(dict(product=offer['url'], page=path, placement='qa-sierras'))
            total += 1
        assert not any(url(key) in html for key in PENDING), path
        assert not any(old in html for old in ['https://meli.la/1ntghna', 'https://meli.la/2WFpTNp', 'https://meli.la/1mLrBwo', 'https://meli.la/1aq4mGc']), path
        routes.append(path)
    paths = list(Path('paginas/sierras').glob('*.md')) + [Path('sierras-ofertas.json')]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    command = ['python', 'integrar_sierras_comerciales.py']
    if pages:
        command += ['--pages', *map(str, pages)]
    subprocess.run(command, check=True)
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', nargs='+', type=int)
    main(parser.parse_args().pages)
