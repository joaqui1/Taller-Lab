"""Correspondencia de ofertas, variantes y materiales de las guías integradas."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
import servidor_local as s

EXPECTED = {
    '/hidrolavadoras/comparativa-general/': {'https://meli.la/2izv76H','https://meli.la/2SuGMdL','https://meli.la/2dFtHcP','https://meli.la/149NjG2'},
    '/hidrolavadoras/lusqtoff/': {'https://meli.la/1qPbvWX','https://meli.la/1X9cSf1','https://meli.la/1uvMFdz'},
    '/taladros/inalambricos/': {'https://meli.la/2xvJRJp'},
    '/taladros/percutores/': {'https://meli.la/18iubWD'},
    '/taladros/taladro-de-banco/': {'https://meli.la/2Znq55m'},
    '/amoladoras/bosch/': {'https://meli.la/1GRCAjZ'},
    '/compresores/para-auto/': {'https://meli.la/2Xv53zX','https://meli.la/274KM8a','https://meli.la/2r8uZXD','https://meli.la/2MHTmab'},
    '/sierras/caladoras/': {'https://meli.la/2azLzTF','https://meli.la/1PmtLAQ','https://meli.la/2N5KYMc'},
    '/generadores/comparativa-general/': {'https://meli.la/2jcLSy1','https://meli.la/2bL6gVj','https://meli.la/1nUAUuv'},
    '/generadores/precios/': {'https://meli.la/2r7eRux','https://meli.la/2dryX8a','https://meli.la/221u1rq'},
}

class Document(HTMLParser):
    def __init__(self,html):
        super().__init__()
        self.links=[]
        self.ids=[]
        self.headings=0
        self.shelves=0
        self.feed(html)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a':self.links.append(attrs)
        if tag=='h1':self.headings+=1
        if 'id' in attrs:self.ids.append(attrs['id'])
        if 'affiliate-shelf' in attrs.get('class','').split():self.shelves+=1

def main():
    articles={a['url']:a for a in s.ALL_ARTICLES}
    assert EXPECTED.keys()<=articles.keys()
    for path,expected in EXPECTED.items():
        article=articles[path]
        html=s.render_article_page(article)
        doc=Document(html)
        affiliates=[a for a in doc.links if a.get('href','').startswith('https://meli.la/')]
        assert expected <= {a['href'] for a in affiliates}, (path, expected - {a['href'] for a in affiliates})
        assert doc.headings==1 and len(doc.ids)==len(set(doc.ids)),path
        assert 'fuentes-consultadas' in doc.ids,path
        for a in affiliates:
            assert {'sponsored','nofollow','noopener'}<=set(a['rel'].split()),(path,a)
            s.validate_affiliate_click(dict(product=a['href'],page=path,placement='qa-integration'))
        for a in doc.links:
            href=a.get('href','')
            if href.startswith('/') and not href.startswith('/assets/'):
                assert href.split('#')[0] in s.INDEXABLE_PATH_SET,(path,href)
    # A general filename must not inject its category offers into another URL.
    clone=dict(articles['/generadores/comparativa-general/'],url='/generadores/qa-sin-asignacion/',body='')
    assert not any(a.get('href','').startswith('https://meli.la/') for a in Document(s.render_article_page(clone)).links)
    hyd=s.RESOURCES['/hidrolavadoras/comparativa-general/']
    assert any('HL100-7' in row[0] and '70 nominales' in row[1] for row in hyd['rows'])
    assert all('GHL150' not in row[0] for row in hyd['rows'])
    assert s.PRODUCT_FACTS['https://meli.la/1cZXqxL']['source_type']=='fabricante'
    assert s.PRODUCT_FACTS['https://meli.la/2m7TJWQ']['source_type']=='marca'
    for url in ['https://meli.la/2xvJRJp','https://meli.la/2Znq55m','https://meli.la/274KM8a']:
        assert s.PRODUCT_FACTS[url]['source_type']=='publicación comercial'
    assert 'Metal: 6 mm; acero no especificado' in articles['/sierras/caladoras/']['body']
    prices=articles['/generadores/precios/']['body']
    assert all(amount in prices for amount in ['$875.199','$1.049.699','$1.339.499','$1.968.699'])
    assert 'captura del **27/09/2026**' in prices and 'PVP publicado el 27/09/2026' in prices
    # La auditoría actual abarca toda la colección; el hash de una fase anterior
    # no distingue una corrección editorial autorizada de una regresión.
    forbidden = {'https://meli.la/1KHbTXG', 'https://meli.la/1fzxaCM', 'https://meli.la/2q7fy7p', 'https://meli.la/2BE54o4'}
    validated = 0
    for path, article in articles.items():
        for link in Document(s.render_article_page(article)).links:
            href = link.get('href', '')
            assert href not in forbidden, (path, href, 'Variante incorrecta o destino retirado')
            if href in s.AFFILIATE_URLS:
                assert {'sponsored', 'noopener'} <= set(link.get('rel', '').split()), (path, href)
                s.validate_affiliate_click(dict(product=href, page=path, placement='qa-integration'))
                validated += 1
    print(f'OK: ofertas prioritarias conservadas, {len(articles)} guías y {validated} CTA registrados; atribución, variantes retiradas y PVP históricos.')

if __name__=='__main__':main()
