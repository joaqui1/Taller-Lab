"""Correspondencia de ofertas, variantes y materiales de las guías integradas."""
import hashlib
import json
import re
from pathlib import Path
from html.parser import HTMLParser
import servidor_local as s

EXPECTED = {
    '/hidrolavadoras/comparativa-general/': {'https://meli.la/1cZXqxL','https://meli.la/2Rcddpg','https://meli.la/1KQjHgT'},
    '/hidrolavadoras/lusqtoff/': {'https://meli.la/1cZXqxL'},
    '/taladros/inalambricos/': {'https://meli.la/2xvJRJp'},
    '/taladros/percutores/': {'https://meli.la/2xvJRJp'},
    '/taladros/taladro-de-banco/': {'https://meli.la/2Znq55m'},
    '/amoladoras/bosch/': {'https://meli.la/1GRCAjZ'},
    '/compresores/para-auto/': {'https://meli.la/2m7TJWQ','https://meli.la/274KM8a'},
    '/sierras/caladoras/': {'https://meli.la/1ntghna'},
    '/generadores/comparativa-general/': {'https://meli.la/2jcLSy1','https://meli.la/2bL6gVj','https://meli.la/1nUAUuv'},
    '/generadores/precios/': {'https://meli.la/2jcLSy1','https://meli.la/2bL6gVj','https://meli.la/1nUAUuv'},
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
        assert {a['href'] for a in affiliates}==expected,path
        assert doc.shelves==0,path
        assert doc.headings==1 and len(doc.ids)==len(set(doc.ids)),path
        assert article['reviewed']=='28/09/2026',path
        assert 'buying-title' in doc.ids and 'fuentes-consultadas' in doc.ids,path
        for a in affiliates:
            assert {'sponsored','nofollow','noopener'}<=set(a['rel'].split()),(path,a)
            s.validate_affiliate_click(dict(product=a['href'],page=path,placement='qa-integration'))
        for a in doc.links:
            href=a.get('href','')
            if href.startswith('/') and not href.startswith('/assets/'):
                assert href.split('#')[0] in s.INDEXABLE_PATH_SET,(path,href)
        assert 'data-buying-status="choice"' not in html,path
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
    assert 'No recotizado' in prices and '27/09/2026' in prices
    baseline=json.loads(Path('baseline-integracion-comercial.json').read_text(encoding='utf-8'))
    targeted={str(a['path'].relative_to(Path(__file__).parent)).replace('\\','/') for p,a in articles.items() if p in EXPECTED}
    untouched=0
    for filename,oldhash in baseline.items():
        if filename.replace('\\','/').startswith('paginas/') and filename.replace('\\','/') not in targeted:
            assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==oldhash,filename
            untouched+=1
    print(f'OK: 10 guías con ofertas exactas, atribución y variantes; {untouched} páginas restantes sin cambios; PVP históricos conservados.')

if __name__=='__main__':main()
