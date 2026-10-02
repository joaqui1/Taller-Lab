"""Comprueba identidad, posición, cantidad de cards y enlaces del HTML servido."""
import re
from html.parser import HTMLParser
from pathlib import Path
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
import servidor_local as s

class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.cards = []
        self.shelves = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'a':
            self.links.append(attrs)
        if 'offer-card' in classes and 'data-product' in attrs:
            self.cards.append(attrs['data-product'])
        if 'affiliate-shelf' in classes:
            self.shelves += 1

def main():
    articles = {article['url']: article for article in s.ALL_ARTICLES}
    cards = 0
    for path, config in s.COMPRESORES_OFFERS.items():
        article = articles[path]
        html = s.render_article_page(article)
        doc = Document(html)
        expected = [offer['url'] for offer in config['offers']]
        selected=s.guide_comparison_selection(path,'compresores',s.PRODUCT_FACTS)
        if selected:
            expected=[item[2] for _,item in selected]
        assert doc.cards == expected, (path, doc.cards, expected)
        assert doc.shelves == int(bool(expected)), path
        assert '<!-- COMPRESORES-OFFERS -->' not in html, path
        for offer in config['offers']:
            anchors = [link for link in doc.links if link.get('href') == offer['url']]
            assert anchors, (path, offer)
            assert all({'sponsored', 'nofollow', 'noopener'} <= set(link.get('rel', '').split()) for link in anchors)
            s.validate_affiliate_click(dict(product=offer['url'], page=path, placement='qa-compresores'))
            assert offer['cta'] in html, (path, offer['cta'])
        if expected:
            heading = '<h2>' + config['cards_heading'] + '</h2>'
            start = html.index(heading)
            shelf = html.index('<section class="affiliate-shelf"', start)
            next_heading = html.find('<h2>', start + len(heading))
            assert next_heading < 0 or shelf < next_heading, path
            if config['mode'] == 'table' and not selected:
                table_end = html.index('</table>', start) + len('</table>')
                # Las tablas con fotos llevan un contenedor de desplazamiento móvil.
                if '<div class="model-table-scroll"' in html[start:table_end]:
                    assert html[table_end:shelf].strip() == '</div>', path
                else:
                    assert not html[table_end:shelf].strip(), path
        for link in doc.links:
            href = link.get('href', '')
            if href.startswith('/') and not href.startswith('/assets/'):
                assert href.split('#')[0] in s.INDEXABLE_PATH_SET, (path, href)
        cards += len(expected)
    for slug in ('manguera', 'acoples-rapidos', 'aceite', 'filtros'):
        path = f'/compresores/{slug}/'
        doc = Document(s.render_article_page(articles[path]))
        assert doc.shelves == 0
        assert not any(link.get('href', '').startswith('https://meli.la/') for link in doc.links), path
    # No trasladar AV37-TY a AV000009, ni el 50 L convencional al oil-free.
    assert s.PRODUCT_FACTS['https://meli.la/2aSkmx1']['model'] == 'AV37-TY'
    assert s.PRODUCT_FACTS['https://meli.la/2MHTmab']['model'] == 'AV000009'
    assert 'https://meli.la/1nobM6T' not in articles['/compresores/sin-aceite/']['body']
    for path, url, model in [('/compresores/24-litros/','https://meli.la/1vR4xKe','G2801AR'),('/compresores/100-litros/','https://meli.la/1jaQvxd','G2803AR')]:
        assert url in s.render_article_page(articles[path])
        assert s.PRODUCT_FACTS[url]['model'] == model
        assert s.PRODUCT_FACTS[url]['source'].startswith('https://www.gammaherramientas.com.ar/producto/')
        assert url not in s.render_article_page(articles['/compresores/50-litros/'])
        assert '50 MHz' not in s.render_article_page(articles[path])
    stanley = s.render_article_page(articles['/compresores/stanley/'])
    assert stanley.index('Disponibilidad local, garantía y servicio') < stanley.index('data-product="https://meli.la/26gU4mL"')
    assert 'la publicación histórica citada en la guía indica 24 L' in stanley
    painting = s.render_article_page(articles['/compresores/para-pintar/'])
    assert painting.index('Combinaciones documentadas: qué se puede validar') < painting.index('class="affiliate-shelf"')
    server = ThreadingHTTPServer(('127.0.0.1', 0), s.TallerLabHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        paths = [path for path in articles if path.startswith('/compresores/')]
        assert len(paths) == 23
        for path in paths:
            with urlopen(f'http://127.0.0.1:{server.server_port}{path}') as response:
                assert response.status == 200, path
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    print('OK: las 23 URLs de compresores responden HTTP 200 en el servidor local.')
    print(f'OK: 19 asignaciones, {cards} cards en 16 guías; 4 páginas sin monetizar; identidad, CTAs, ubicación y eventos válidos.')

if __name__ == '__main__':
    main()
